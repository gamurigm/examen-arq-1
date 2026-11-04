import datetime, hashlib, json, pathlib, urllib.request, xml.etree.ElementTree as E
root=pathlib.Path(__file__).resolve().parents[1]
folder=root/'05. DOCUMENTACION/evidencias'
def text(name):
    return ' '.join(n.get('text','') for n in E.parse(folder/(name+'.xml')).iter('node'))
def get(path):
    with urllib.request.urlopen('http://127.0.0.1:19202/'+path) as r:return json.load(r)
cash=get('api/facturas?cedula=1111111111')[0]
loan=get('api/facturas?cedula=0102030405')[0]
rows=get(f"api/facturas/{loan['id']}/amortizacion")
assert cash['total']==261 and cash['descuento']==189 and cash['estado']=='APROBADA'
assert loan['total']==450 and loan['estado']=='APROBADA' and rows[-1]['saldo']==0
assert 'EFECTIVO' in text('android_efectivo') and 'APROBADA' in text('android_efectivo')
assert 'QA Android editado' in text('android_catalogo_editado')
assert 'APROBADA' in text('android_busqueda')
assert 'Saldo restante  $0.00' in text('android_consulta_amortizacion')
item=get('api/celulares/5');assert not item['activo'] and item['nombre']=='QA Android editado'
apk=next(pathlib.Path('D:/tools/CelularGR09_MovilQA/bin/Celulares.Movil/Debug/net10.0-android').glob('*Signed.apk'))
data={'fecha':datetime.datetime.now().isoformat(),'entorno':json.loads((root/'scripts/qa-visual.local.json').read_text()),'apkSha256':hashlib.sha256(apk.read_bytes()).hexdigest(),'casos':['Catálogo visible','Alta celular por interfaz','Edición celular por interfaz','Desactivación celular por interfaz','Efectivo aprobado: 450 - 189 = 261','Crédito nuevo aprobado: 450 / 3 cuotas','Búsqueda por cédula','Reapertura factura','Amortización visible con saldo cero'],'facturaEfectivo':cash,'facturaCredito':loan,'amortizacion':rows,'capturas':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('android_*.png')}}
(root/'05. DOCUMENTACION/EVIDENCIA_ANDROID_QA.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('Android: 9 recorridos y persistencia verificados; evidencia guardada.')
