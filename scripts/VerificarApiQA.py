"""Prueba HTTP aislada. Requiere Docker inicializado y .NET en PATH; no elimina bases."""
import calendar, datetime, json, os, pathlib, socket, subprocess, time, urllib.request, urllib.error, uuid
from decimal import Decimal
ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
run_id = datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:6]
bank_db = 'BanQuitoCore_QA_' + run_id
shop_db = 'ComercializadoraCelulares_QA_' + run_id
results, processes, logs = [], [], []
password = next(x.split('=',1)[1] for x in (ROOT/'.env').read_text(encoding='utf-8-sig').splitlines() if x.startswith('MSSQL_SA_PASSWORD='))

def sql(content):
    p = subprocess.run(['docker','compose','exec','-T','sqlserver','bash','-c','/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -b'],input=content,encoding='utf-8',capture_output=True)
    if p.returncode: raise RuntimeError(p.stdout + p.stderr)
    return p.stdout

def check(label, condition):
    if not condition: raise AssertionError(label)
    results.append({'caso':label,'resultado':'APROBADO'})

def request(port, path, method='GET', body=None, expected=200):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f'http://127.0.0.1:{port}/{path}',data=data,method=method,headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=15) as r: status, raw = r.status, r.read()
    except urllib.error.HTTPError as e: status, raw = e.code, e.read()
    if status != expected: raise AssertionError(f'{method} {path}: esperado {expected}, recibido {status}: {raw.decode()}')
    return json.loads(raw,parse_float=Decimal) if raw else None

def credit(client, amount, months):
    return dict(codigoCliente=client,precioTelefono=amount,numeroCuotas=months,referenciaVenta=str(uuid.uuid4()))

def invoice(cedula, payment, months=None):
    return dict(idOperacion=str(uuid.uuid4()),cedula=cedula,nombreCliente='Prueba QA',idCelular=1,formaPago=payment,numeroCuotas=months,precioEsperado=450)

def table(rows, principal, months):
    check(f'Amortización {months}: filas y saldo final',len(rows)==months+1 and rows[-1]['saldo']==0 and rows[0]['saldo']==principal)
    check(f'Amortización {months}: capital completo',sum(x['capitalPagado'] for x in rows)==principal)
    check(f'Amortización {months}: interés 16,5% anual',rows[1]['interesPagado']==(Decimal(principal)*Decimal('0.165')/12).quantize(Decimal('.01'),rounding='ROUND_HALF_UP'))
    start=datetime.date.fromisoformat(rows[0]['fechaPago'])
    for n,row in enumerate(rows[1:],1):
        month_index=start.year*12+start.month-1+n
        y,m=divmod(month_index,12); m+=1
        due=datetime.date(y,m,min(start.day,calendar.monthrange(y,m)[1]))
        check(f'Cuota {months}/{n}: fecha mensual y balance',row['fechaPago']==due.isoformat() and row['valorCuota']==row['capitalPagado']+row['interesPagado'] and rows[n-1]['saldo']-row['capitalPagado']==row['saldo'])
    check(f'Amortización {months}: cuota fija salvo ajuste final',len({r['valorCuota'] for r in rows[1:-1]})==1)

try:
    for port in [19201,19202]:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',port))
    for file in ['03. BDD/01_CrearBases.sql','03. BDD/03_MigrarImagenes.sql','03. BDD/02_DatosPrueba.sql','03. BDD/BanQuito/BanQuito_01_CrearBase.sql','03. BDD/BanQuito/BanQuito_02_DatosPrueba.sql']:
        sql((ROOT/file).read_text(encoding='utf-8-sig').replace('ComercializadoraCelulares',shop_db).replace('BanQuitoCore',bank_db))
    for name,db,port in [('BanQuito.Api',bank_db,19201),('Comercializadora.Api',shop_db,19202)]:
        env=os.environ.copy()
        env['ConnectionStrings__BaseDatos']=f'Server=127.0.0.1,19433;Database={db};User Id=sa;Password={password};Encrypt=True;TrustServerCertificate=True'
        env['Servicios__BanQuitoUrl']='http://127.0.0.1:19201/'
        project=ROOT/'04. SERVIDOR'/name/(name+'.csproj')
        subprocess.run(['dotnet','build',str(project),'--verbosity','quiet'],check=True,capture_output=True)
        log=open(ROOT/'scripts'/(name+'.log'),'w',encoding='utf-8'); logs.append(log)
        proc=subprocess.Popen(['dotnet','run','--no-build','--no-launch-profile','--project',str(project),'--','--urls',f'http://127.0.0.1:{port}'],env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(proc)
        for attempt in range(60):
            try:
                request(port,'api/salud'); break
            except (OSError,AssertionError):
                if proc.poll() is not None: raise RuntimeError(f'{name} terminó. Revisar log local.')
                time.sleep(1)
        else: raise RuntimeError(f'{name} no disponible')
    initial=request(19202,'api/celulares')
    check('Catálogo inicial: tres celulares',len(initial)==3)
    item=request(19202,'api/celulares','POST',dict(nombre='QA temporal',precio=100,activo=True),201)
    item_id=item['id']
    updated=request(19202,f'api/celulares/{item_id}','PUT',dict(nombre='QA editado',precio=125,activo=True))
    check('Catálogo: alta y edición',updated['nombre']=='QA editado' and updated['precio']==125)
    request(19202,f'api/celulares/{item_id}','DELETE',expected=204)
    check('Catálogo: desactivación',not request(19202,f'api/celulares/{item_id}')['activo'])
    for cedula,eligible,fragment in [('0000000000',False,'cliente'),('0203040506',False,'25'),('0405060708',False,'depósitos'),('0304050607',True,'sujeto')]:
        e=request(19201,'api/credito/elegibilidad?cedula='+cedula)
        check('Elegibilidad '+cedula,e['sujetoCredito']==eligible and fragment in e['motivo'])
    maximum=request(19201,'api/credito/clientes/3/monto-maximo')['montoMaximo']
    check('Máximo 35% de diferencia por seis',maximum==2142)
    for months in [2,19]:
        request(19201,'api/creditos','POST',credit(3,450,months),400)
        check('Rechazo plazo '+str(months),True)
    request(19201,'api/creditos','POST',credit(3,float(maximum+1),3),409)
    check('Rechazo monto superior al máximo',True)
    request(19201,'api/creditos','POST',credit(2,450,3),409)
    check('Otorgamiento rechaza menor masculino',True)
    for months in [2,19]:
        request(19202,'api/facturas','POST',invoice('0304050607','CREDITO_DIRECTO',months),400)
        check('Factura rechaza plazo '+str(months),True)
    cash=invoice('QA-CONTADO','EFECTIVO')
    f=request(19202,'api/facturas','POST',cash,201)
    check('Efectivo: descuento 189 y total 261',f['estado']=='APROBADA' and f['descuento']==189 and f['total']==261)
    retry=request(19202,'api/facturas','POST',cash,201)
    check('Reintento efectivo sin duplicado',retry['id']==f['id'])
    loan=invoice('0304050607','CREDITO_DIRECTO',3)
    f=request(19202,'api/facturas','POST',loan,201)
    check('Crédito 450 aprobado sin descuento',f['estado']=='APROBADA' and f['total']==450 and f['descuento']==0 and f['creditoId'] is not None)
    rows=request(19202,f"api/facturas/{f['id']}/amortizacion")
    table(rows,450,3)
    check('Tabla bancaria coincide con pasarela',request(19201,f"api/creditos/{f['creditoId']}/amortizacion")==rows)
    check('Reintento crédito sin duplicado',request(19202,'api/facturas','POST',loan,201)['id']==f['id'])
    changed=dict(loan,nombreCliente='Otro')
    request(19202,'api/facturas','POST',changed,409)
    check('Reintento con datos diferentes rechazado',True)
    check('Cliente con crédito activo no elegible',not request(19201,'api/credito/elegibilidad?cedula=0304050607')['sujetoCredito'])
    request(19201,'api/creditos','POST',credit(3,450,3),409)
    check('Segundo crédito activo rechazado',True)
    max1=request(19201,'api/credito/clientes/1/monto-maximo')['montoMaximo']
    c=request(19201,'api/creditos','POST',credit(1,float(max1),18))
    check('Monto igual al máximo aprobado',c['monto']==max1)
    table(c['cuotas'],max1,18)
    check('Consulta factura y búsqueda por cédula',request(19202,f"api/facturas/{f['id']}")['id']==f['id'] and len(request(19202,'api/facturas?cedula=0304050607'))==1)
    counts=sql(f'USE [{bank_db}]; SELECT COUNT(*) CREDITOS FROM dbo.CREDITO; USE [{shop_db}]; SELECT COUNT(*) FACTURAS FROM dbo.FACTURA;')
    output={'fecha':datetime.datetime.now().isoformat(),'basesQA':[bank_db,shop_db],'casos':results,'conteosSQL':counts,'alcance':'API HTTP; no acredita interacción con cuatro interfaces.'}
    dest=ROOT/'05. DOCUMENTACION'/'EVIDENCIA_API_QA.json'
    dest.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(results)} comprobaciones aprobadas. Evidencia: {dest.name}. Bases QA conservadas: {bank_db}, {shop_db}')
finally:
    for proc in reversed(processes):
        subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
    for log in logs: log.close()
