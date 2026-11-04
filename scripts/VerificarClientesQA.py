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
    for port in [19201,19202,19203]:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1',port))
    for file in ['03. BDD/01_CrearBases.sql','03. BDD/03_MigrarImagenes.sql','03. BDD/02_DatosPrueba.sql','03. BDD/BanQuito/BanQuito_01_CrearBase.sql','03. BDD/BanQuito/BanQuito_02_DatosPrueba.sql']:
        sql((ROOT/file).read_text(encoding='utf-8-sig').replace('ComercializadoraCelulares',shop_db).replace('BanQuitoCore',bank_db))
    for name,db,port in [('BanQuito.Api',bank_db,19201),('Comercializadora.Api',shop_db,19202)]:
        env=os.environ.copy()
        env['ConnectionStrings__BaseDatos']=f'Server=127.0.0.1,19433;Database={db};User Id=sa;Password={password};Encrypt=True;TrustServerCertificate=True'
        env['Servicios__BanQuitoUrl']='http://127.0.0.1:19201/'
        project=ROOT/'04. SERVIDOR'/name/(name+'.csproj')
        subprocess.run(['dotnet','build',str(project),'-p:CelularBuildRoot=D:/tools/CelularGR09_ClientsQA','--verbosity','quiet'],check=True,capture_output=True)
        log=open(ROOT/'scripts'/(name+'.log'),'w',encoding='utf-8'); logs.append(log)
        proc=subprocess.Popen(['dotnet','run','--no-build','--no-launch-profile','--project',str(project),'-p:CelularBuildRoot=D:/tools/CelularGR09_ClientsQA','--','--urls',f'http://127.0.0.1:{port}'],env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
        processes.append(proc)
        for attempt in range(60):
            try:
                request(port,'api/salud'); break
            except (OSError,AssertionError):
                if proc.poll() is not None: raise RuntimeError(f'{name} terminó. Revisar log local.')
                time.sleep(1)
        else: raise RuntimeError(f'{name} no disponible')
    env=os.environ.copy()
    env['CELULARES_API_URL']='http://127.0.0.1:19202/'
    subprocess.run(['dotnet','build','04. CLICON/Celulares.Consola/Celulares.Consola.csproj','-p:CelularBuildRoot=D:/tools/CelularGR09_ClientsQA','--verbosity','quiet'],check=True,capture_output=True)
    inputs='1\n2\n\nQA Consola\n100\n2\n4\nQA Consola editado\n125\n3\n4\ns\n4\n1\nQA-EFECTIVO\nComprador Consola\n1\ns\n4\n1\n0304050607\nAna Consola\n2\n3\ns\n6\n0304050607\n2\n0\n'
    console=subprocess.run(['dotnet','run','--no-build','--project','04. CLICON/Celulares.Consola/Celulares.Consola.csproj','-p:CelularBuildRoot=D:/tools/CelularGR09_ClientsQA'],input=inputs,text=True,encoding='utf-8',capture_output=True,env=env,timeout=60)
    (ROOT/'05. DOCUMENTACION'/'EVIDENCIA_CONSOLA.txt').write_text(console.stdout,encoding='utf-8')
    check('Consola termina correctamente',console.returncode==0)
    check('Consola catálogo alta y edición','Guardado: QA Consola editado' in console.stdout)
    check('Consola efectivo y crédito aprobados',console.stdout.count('Venta APROBADA:')==2)
    check('Consola consulta amortización','Cuota 3' in console.stdout and ('saldo $0.00' in console.stdout or 'saldo $0,00' in console.stdout))
    check('Consola sin errores de operación','No se pudo completar' not in console.stdout)
    (ROOT/'05. DOCUMENTACION'/'EVIDENCIA_CONSOLA.txt').write_text(console.stdout,encoding='utf-8')
    import http.cookiejar, re, urllib.parse, html
    subprocess.run(['dotnet','build','04. CLIWEB/Celulares.Web/Celulares.Web.csproj','-p:CelularBuildRoot=D:/tools/CelularGR09_WebQA','--verbosity','quiet'],check=True,capture_output=True)
    env['CelularesApiUrl']='http://127.0.0.1:19202/'
    log=open(ROOT/'scripts'/'WebQA.log','w',encoding='utf-8'); logs.append(log)
    proc=subprocess.Popen(['dotnet','D:/tools/CelularGR09_WebQA/bin/Celulares.Web/Debug/net10.0/Celulares.Web.dll','--urls','http://127.0.0.1:19203','--contentRoot',str(ROOT/'04. CLIWEB/Celulares.Web')],env=env,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
    processes.append(proc)
    jar=http.cookiejar.CookieJar()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    def web(path='',fields=None):
        data=None if fields is None else urllib.parse.urlencode(fields).encode()
        with opener.open('http://127.0.0.1:19203/'+path,data=data,timeout=15) as response:
            return response.geturl(),response.read().decode()
    for attempt in range(40):
        try: _,page=web(); break
        except OSError: time.sleep(1)
    else: raise RuntimeError('Web QA no disponible')
    def post(path,fields):
        _,page=web()
        token=html.unescape(re.search(r'name="__RequestVerificationToken"[^>]*value="([^"]+)"',page).group(1))
        return web(path,dict(fields,__RequestVerificationToken=token))
    check('Web catálogo renderizado','Aurora' in page)
    post('Tienda/Guardar',dict(nombre='QA Web',precio=100))
    item=next(x for x in request(19202,'api/celulares') if x['nombre']=='QA Web')
    post('Tienda/Guardar',dict(id=item['id'],nombre='QA Web editado',precio=125))
    check('Web alta y edición catálogo',request(19202,f"api/celulares/{item['id']}")['precio']==125)
    post('Tienda/Eliminar',dict(id=item['id']))
    check('Web desactivación',not request(19202,f"api/celulares/{item['id']}")['activo'])
    for payment,cedula in [('EFECTIVO','QA-WEB'),('CREDITO_DIRECTO','0102030405')]:
        fields={'Venta.IdOperacion':str(uuid.uuid4()),'Venta.Cedula':cedula,'Venta.NombreCliente':'Comprador Web','Venta.IdCelular':1,'Venta.FormaPago':payment,'Venta.PrecioEsperado':450}
        if payment=='CREDITO_DIRECTO': fields['Venta.NumeroCuotas']=3
        url,page=post('Tienda/Vender',fields)
        check('Web factura '+payment,'/Tienda/Factura/' in url and 'APROBADA' in page)
        invoice_record=request(19202,'api/facturas?cedula='+cedula)[0]
        check('Web total '+payment,invoice_record['total']==(261 if payment=='EFECTIVO' else 450))
        if payment=='CREDITO_DIRECTO':
            check('Web amortización renderizada','Amortización' in page and '<td>3</td>' in page)
            (ROOT/'05. DOCUMENTACION'/'EVIDENCIA_WEB_FACTURA.html').write_text(page,encoding='utf-8')
    _,page=post('Tienda/BuscarFacturas',dict(cedula='0102030405'))
    check('Web búsqueda por cédula','APROBADA' in page and 'Ver detalle' in page)
    output={'fecha':datetime.datetime.now().isoformat(),'basesQA':[bank_db,shop_db],'casos':results,'alcance':'Consola por entrada estándar; web por formularios MVC reales con cookies y antiforgery. No prueba JavaScript ni inspección visual.'}
    (ROOT/'05. DOCUMENTACION'/'EVIDENCIA_CLIENTES_QA.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(results)} comprobaciones aprobadas de consola/web')
finally:
    for proc in reversed(processes):
        subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
    for log in logs: log.close()
