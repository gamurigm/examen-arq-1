"""Renderiza SVG generados por VBS y compara atributos del MER con SQL Docker."""
from pathlib import Path
import hashlib,json,subprocess,xml.etree.ElementTree as E
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parents[1]
figures=[root/'01. UML/03. DIAGRAMAS UML/01_CASOS_DE_USO/GR09_BanQuito_CasosUso.svg',root/'01. UML/03. DIAGRAMAS UML/05_ARQUITECTURA/GR09_Arquitectura_Docker.svg',root/'02. MER/03. FISICO/GR09_Celulares_SQL_Actual.svg']
def query(sql):
 p=subprocess.run(['docker','compose','exec','-T','sqlserver','bash','-c','/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -b -h-1 -W -Q "$1"','qa',sql],cwd=root,text=True,capture_output=True,check=True)
 return [s.strip() for s in p.stdout.splitlines() if s.strip() and not s.startswith('Changed database context')]
columns=query("SET NOCOUNT ON; USE ComercializadoraCelulares; SELECT c.name FROM sys.columns c JOIN sys.tables t ON c.object_id=t.object_id WHERE t.name IN ('CELULAR','FACTURA') ORDER BY t.name,c.column_id;")
mer=figures[-1].read_text(encoding='utf-8-sig')
assert len(columns)==21,columns
assert all(name in mer for name in columns), [name for name in columns if name not in mer]
fks=query("SET NOCOUNT ON; USE ComercializadoraCelulares; SELECT OBJECT_NAME(parent_object_id)+'->'+OBJECT_NAME(referenced_object_id) FROM sys.foreign_keys;")
assert fks==['FACTURA->CELULAR'],fks
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
 for svg in figures:
  el=E.parse(svg).getroot();page=browser.new_page(viewport={'width':int(el.attrib['width']),'height':int(el.attrib['height'])},device_scale_factor=1.5)
  page.goto(svg.as_uri());page.locator('svg').screenshot(path=str(svg.with_suffix('.png')));page.close()
 browser.close()
powerdesigner_diagrams = [
    ('casos_uso', root/'01. UML/03. DIAGRAMAS UML/01_CASOS_DE_USO/GR09_CasosUso_Sistema de ventas de celulares.png'),
    ('actividad', root/'01. UML/03. DIAGRAMAS UML/02_ACTIVIDAD/GR09_Actividad_Venta a crédito.png'),
    ('secuencia', root/'01. UML/03. DIAGRAMAS UML/03_SECUENCIA/GR09_Secuencia_Venta a crédito.png'),
    ('clases', root/'01. UML/03. DIAGRAMAS UML/04_CLASES/GR09_Clases_Clases del servicio y cliente.png'),
    ('arquitectura', root/'01. UML/03. DIAGRAMAS UML/05_ARQUITECTURA/GR09_Arquitectura_Arquitectura cliente-servidor.png'),
    ('mer_fisico', root/'02. MER/03. FISICO/GR09_Celulares_Physical_DotNet_SQLServer.png'),
]
missing = [str(path.relative_to(root)) for _, path in powerdesigner_diagrams if not path.is_file()]
assert not missing, f'Faltan exportaciones PowerDesigner requeridas: {missing}'
manifest={
    'generador':'01. UML/GenerarFigurasEntrega.vbs',
    'formatoEditable':'SVG auxiliar; no se afirma regeneración PowerDesigner',
    'columnasSQLVerificadas':columns,
    'foreignKeys':fks,
    'figuras':[{'svg':str(f.relative_to(root)).replace('\\','/'),'svgSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'png':str(f.with_suffix('.png').relative_to(root)).replace('\\','/'),'pngSha256':hashlib.sha256(f.with_suffix('.png').read_bytes()).hexdigest()} for f in figures],
    'usoFigurasAuxiliares':'Los SVG/PNG generados por este verificador sirven para comprobaciones auxiliares y no se insertan en el manual DOCX ni en el PPTX.',
    'figurasManualPowerDesigner':[{
        'tipo':kind,
        'png':str(path.relative_to(root)).replace('\\','/'),
        'origen':'Exportación PNG PowerDesigner existente',
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
    } for kind, path in powerdesigner_diagrams],
    'modelosNativosRegeneradosEnEstaRevision':False,
    'motivoNoRegeneracion':'Licencia de evaluación de PowerDesigner vencida; se reutilizan exportaciones existentes.',
}
(root/'05. DOCUMENTACION/EVIDENCIA_DIAGRAMAS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Tres figuras renderizadas; 21 atributos y relación FACTURA->CELULAR contrastados con SQL.')
