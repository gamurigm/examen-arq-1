"""Comprueba cobertura de archivos, fragmentación y contenido de los dos borradores."""
import hashlib, importlib.util, json, pathlib, re, sys, zipfile
from lxml import etree
from pptx import Presentation
ROOT = pathlib.Path(__file__).resolve().parents[1]
draft_directory = sys.argv[1] if len(sys.argv) > 1 else "05. DOCUMENTACION/.trabajo/borradores"
sys.argv = [sys.argv[0]]
spec = importlib.util.spec_from_file_location('generador', ROOT / 'scripts/GenerarDocumentacion.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
source = ROOT / '05. DOCUMENTACION/fuentes/manual_verificado.md'
_, sections = g.parse_source(source)
inv = json.loads((ROOT / '05. DOCUMENTACION/INVENTARIO_MANUAL_PRACTICO.json').read_text())
blocks = [b for s in sections for b in s['blocks']]
for record in inv['archivos']:
    path = ROOT / record['archivo']
    assert hashlib.sha256(path.read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest() == record['sha256Contenido'], path
    text = path.read_text(encoding='utf-8-sig').rstrip()
    assert any(b['kind'] == 'code' and b['text'].strip('\n') == text.strip('\n') and b.get('file_label') == record['archivo'] for b in blocks), path
for b in blocks:
    if b['kind'] == 'code':
        parts = g.split_block_for_presentation(b)
        assert ''.join(p['text'] for p in parts) == b['text']
        assert all(g.presentation_line_count(p['text']) <= 10 for p in parts), b.get('file_label')
        if b.get('file_label'): assert all(p.get('file_label') == b['file_label'] for p in parts)
groups = g.group_presentation_sections(sections)
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
expected_code = ''.join(b['text'] for b in blocks if b['kind']=='code')
compact = lambda x: re.sub(r'\s+', '', x)
results=[]
for kind,ext in [('MANUAL_TECNICO','docx'),('PRESENTACION','pptx')]:
    path = ROOT / draft_directory / f'{kind}_CELULAR_BDDLOCAL_RESTFUL_DOTNET_GR09.{ext}'
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        if ext=='docx':
            xml=etree.fromstring(z.read('word/document.xml'))
            runs=xml.xpath('//w:r[w:rPr/w:rFonts[@w:ascii="Consolas"] and w:rPr/w:sz[@w:val="18"]]',namespaces=ns)
            actual=''.join(''.join(r.xpath('.//w:t/text()',namespaces=ns)) for r in runs)
            assert '1-2' in ''.join(xml.xpath('//w:instrText/text()',namespaces=ns))
        else:
            slides = Presentation(path).slides
            actual = ''.join(''.join(slide._element.xpath('//a:r[a:rPr/a:latin[@typeface="Consolas"]]/a:t/text()')) for slide in slides)
        assert compact(actual)==compact(expected_code), (ext,'El código del artefacto no coincide con la fuente')
        media={hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if '/media/' in n}
        for b in blocks:
            if b['kind']=='image':assert hashlib.sha256(b['path'].read_bytes()).hexdigest() in media,b['path']
        results.append({'archivo':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
print(json.dumps({'archivosDocumentados':len(inv['archivos']),'capitulos':len(sections),'diapositivasEsperadas':len(groups)+2,'codigoCompletoCoincidente':True,'artefactos':results},ensure_ascii=False,indent=2))
