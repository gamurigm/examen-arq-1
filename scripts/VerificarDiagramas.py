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
manifest={'generador':'01. UML/GenerarFigurasEntrega.vbs','formatoEditable':'SVG; no se afirma regeneración PowerDesigner','columnasSQLVerificadas':columns,'foreignKeys':fks,'figuras':[{'svg':str(f.relative_to(root)).replace('\\','/'),'svgSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'png':str(f.with_suffix('.png').relative_to(root)).replace('\\','/'),'pngSha256':hashlib.sha256(f.with_suffix('.png').read_bytes()).hexdigest()} for f in figures]}
(root/'05. DOCUMENTACION/EVIDENCIA_DIAGRAMAS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Tres figuras renderizadas; 21 atributos y relación FACTURA->CELULAR contrastados con SQL.')
