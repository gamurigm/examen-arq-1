"""Genera borradores desde plantillas Office; no sustituye entregables finales."""
import copy, hashlib, json, pathlib, re, subprocess
from docx import Document
from docx.shared import Inches, Pt, RGBColor as DColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from pptx import Presentation
from pptx.util import Inches as PInches, Pt as PPt
from pptx.dml.color import RGBColor
ROOT=pathlib.Path(__file__).resolve().parents[1]
profile=json.loads((ROOT/'documentation-profile.json').read_text(encoding='utf-8'))
dest=pathlib.Path(profile['documentation']['draft_directory']);dest.mkdir(parents=True,exist_ok=True)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def cells(line):return [x.strip() for x in line.strip().strip('|').split('|')]
def generate_word(template,source,target):
    doc=Document(template)
    from docx.enum.style import WD_STYLE_TYPE
    for name,size in [('Title',24),('Heading 1',16),('Heading 2',13)]:
        if name not in doc.styles:
            style=doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
            style.base_style=doc.styles['Normal'];style.font.size=Pt(size);style.font.bold=True
    table_props=copy.deepcopy(doc.tables[0]._tbl.tblPr) if doc.tables else None
    for child in list(doc._element.body):
        if child.tag.endswith('}sectPr'):continue
        doc._element.body.remove(child)
    for section in doc.sections:
        section.top_margin=Inches(.8);section.bottom_margin=Inches(.8)
        section.left_margin=Inches(.85);section.right_margin=Inches(.85)
        for part in [section.header,section.footer]:
            for child in list(part._element):part._element.remove(child)
        section.header.add_paragraph('GR09 · CELULARES / BANQUITO · REST .NET')
        section.footer.add_paragraph('NRC 36884 · Borrador para revisión · Noviembre de 2026')
    normal=doc.styles['Normal'];normal.font.size=Pt(11);normal.font.bold=False;normal.font.color.rgb=DColor(30,40,50)
    normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.LEFT
    normal.paragraph_format.line_spacing=1.1
    normal.paragraph_format.space_after=Pt(6)
    lines=source.read_text(encoding='utf-8').splitlines();i=0
    while i<len(lines):
        line=lines[i].strip();i+=1
        if not line:continue
        if line.startswith('|'):
            rows=[cells(line)]
            while i<len(lines) and lines[i].strip().startswith('|'):
                row=cells(lines[i]);i+=1
                if all(re.fullmatch(r'[: -]+',c) for c in row):continue
                rows.append(row)
            cols=max(map(len,rows));t=doc.add_table(rows=0,cols=cols)
            if table_props is not None:
                t._tbl.remove(t._tbl.tblPr);t._tbl.insert(0,copy.deepcopy(table_props))
            for row in rows:
                cells_=t.add_row().cells
                for j,content in enumerate(row):cells_[j].text=content
            t.autofit=False
            for ri,row in enumerate(t.rows):
                for ci,cell in enumerate(row.cells):
                    cell.width=Inches(1.25 if ci==0 and cols==2 else (5.2 if cols==2 else 2.15))
                    for para in cell.paragraphs:
                        para.alignment=WD_ALIGN_PARAGRAPH.LEFT
                        para.paragraph_format.space_after=Pt(3)
                        for run in para.runs:
                            run.font.bold=(ri==0);run.font.size=Pt(10);run.font.color.rgb=DColor(20,30,40)
            for cell in t.rows[0].cells:
                for run in cell.paragraphs[0].runs:run.bold=True
            # Repetir encabezado y evitar dividir una fila entre páginas.
            header=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(header)
            for row in t.rows:
                row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            doc.add_paragraph()
        elif line.startswith('# '):
            doc.add_heading(line[2:],0)
            doc.add_paragraph('Gabriel Omar Murillo Medina · Julio Enrique Viche Casrillo\nGrupo 09 · NRC 36884\nTutor: Ing. Eduardo Mauricio Campaña Ortega\n4 de noviembre de 2026')
        elif line.startswith('## '):
            if source.name.startswith('ecud') and line.startswith('## CU') and not line.startswith('## CU01'):doc.add_page_break()
            doc.add_heading(line[3:],1)
        elif line.startswith('### '):doc.add_heading(line[4:],2)
        else:doc.add_paragraph(line)
    doc.save(target)
def generate_slides(template,source,target):
    prs=Presentation(template)
    chunks=re.split(r'^## ',source.read_text(encoding='utf-8'),flags=re.M)
    # Reutilizar tema, fondos y gráficos pequeños de las diapositivas de plantilla.
    while len(prs.slides)>len(chunks):
        sid=prs.slides._sldIdLst[-1];prs.part.drop_rel(sid.rId);prs.slides._sldIdLst.remove(sid)
    for idx,chunk in enumerate(chunks):
        slide=prs.slides[idx]
        for shape in list(slide.shapes):
            # Evitar capturas y texto del ejemplo; mantener solo marcas gráficas pequeñas.
            if shape.shape_type==13 and shape.width<PInches(1.5) and shape.height<PInches(1.5):continue
            shape._element.getparent().remove(shape._element)
        lines=[l.strip() for l in chunk.splitlines() if l.strip()]
        title=lines[0].lstrip('# ')
        x=PInches(.65);width=prs.slide_width-PInches(1.3)
        box=slide.shapes.add_textbox(x,PInches(.65),width,PInches(1.1))
        p=box.text_frame.paragraphs[0];p.text=title;p.font.size=PPt(30);p.font.bold=True;p.font.color.rgb=RGBColor(8,90,90) if idx==0 else RGBColor(255,255,255)
        box=slide.shapes.add_textbox(x,PInches(2),width,prs.slide_height-PInches(2.6))
        box.text_frame.word_wrap=True
        for j,line in enumerate(lines[1:]):
            p=box.text_frame.paragraphs[0] if j==0 else box.text_frame.add_paragraph()
            p.text=line;p.font.size=PPt(25);p.font.color.rgb=RGBColor(30,45,60);p.space_after=PPt(18)
    prs.save(target)
manifest={'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'estado':'BORRADOR; requiere revisión visual','artifacts':[]}
for key,item in profile['documentation']['artifacts'].items():
    template=ROOT/item['template'];source=ROOT/item['source'];target=dest/pathlib.Path(item['output']).name
    (generate_slides if key=='presentacion' else generate_word)(template,source,target)
    manifest['artifacts'].append({'id':key,'template':item['template'],'templateSha256':sha(template),'source':item['source'],'sourceSha256':sha(source),'draft':str(target),'draftSha256':sha(target),'output':item['output']})
(dest/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Cuatro borradores generados en',dest)
