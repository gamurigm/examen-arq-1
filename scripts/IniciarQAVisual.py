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
    context={'basesQA':[bank_db,shop_db],'api':'http://127.0.0.1:19202/','banco':'http://127.0.0.1:19201/'}
    (ROOT/'scripts'/'qa-visual.local.json').write_text(json.dumps(context),encoding='utf-8')
    print(json.dumps(context),flush=True)
    print('QA visual activo; Ctrl+C detiene solo estas API. Bases conservadas.',flush=True)
    while True: time.sleep(1)
finally:
    for proc in reversed(processes):
        subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True)
    for log in logs: log.close()
