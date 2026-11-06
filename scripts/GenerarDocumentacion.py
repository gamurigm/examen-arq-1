"""Genera borradores Office desde las plantillas GR09 y sus fuentes canónicas."""
import argparse
import copy
import hashlib
import io
import json
import pathlib
import re
import subprocess
import zipfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START, WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as WordRelationship
from docx.shared import Inches, Pt, RGBColor as WordRGBColor
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE, MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement as PptOxmlElement
from pptx.oxml.ns import qn as ppt_qn
from pptx.util import Inches as PInches, Pt as PPt
from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "documentation-profile.json"
PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8-sig"))
DOCS = PROFILE["documentation"]
PROJECT = PROFILE["project"]
AUTHOR_LINE = "; ".join(PROJECT["authors"])
DATE = "05/11/2026"

parser = argparse.ArgumentParser()
parser.add_argument("--artifacts", nargs="+", choices=["ers", "ecud", "manual", "presentacion"])
parser.add_argument("--draft-directory", type=pathlib.Path, help="Directorio alternativo para revisar sin sobrescribir un borrador abierto en Office")
parser.add_argument("--compacto", action="store_true", help="Generar únicamente la presentación resumida desde la selección verificada")
ARGS = parser.parse_args()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value):
    return re.sub(r"\s+", " ", value).strip()


def parse_source(source):
    """Parse the small, explicit Markdown subset used by the canonical sources."""
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), "")
    sections = []
    current = None
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if line.startswith("## "):
            if current:
                current["blocks"] = blocks
                sections.append(current)
            current = {"title": line[3:].strip()}
            blocks = []
            continue
        if current is None or not line:
            continue
        image = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line)
        if image:
            image_path = (source.parent / image.group(2)).resolve()
            if not image_path.is_file():
                raise FileNotFoundError(f"{current['title']}: imagen ausente: {image_path}")
            if not image_path.is_relative_to(ROOT):
                raise ValueError(f"Imagen fuera del repositorio: {image_path}")
            blocks.append({"kind": "image", "caption": image.group(1), "path": image_path})
            continue
        if line.startswith("```"):
            code = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip())
                i += 1
            if i < len(lines):
                i += 1
            label = next((b["text"] for b in reversed(blocks) if b["kind"] == "heading" and b["text"].startswith("04. ")), "")
            blocks.append({"kind": "code", "text": "\n".join(code), "file_label": label})
            continue
        if line.startswith("|"):
            rows = [table_cells(line)]
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = table_cells(lines[i].strip())
                i += 1
                if all(re.fullmatch(r"[:\- ]+", cell or " ") for cell in row):
                    continue
                rows.append(row)
            blocks.append({"kind": "table", "rows": rows})
            continue
        if line.startswith("### "):
            blocks.append({"kind": "heading", "text": line[4:].strip()})
            continue
        if line.startswith("- ") or re.match(r"^\d+[.)]\s", line):
            blocks.append({"kind": "list", "text": line.lstrip("- ").strip()})
            continue
        blocks.append({"kind": "paragraph", "text": line})
    if current:
        current["blocks"] = blocks
        sections.append(current)
    if not title or not sections:
        raise ValueError(f"Fuente sin título o capítulos: {source}")
    return title, sections


def table_cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def block_text(block):
    kind = block["kind"]
    if kind == "image":
        return "Figura: " + block["caption"]
    if kind == "table":
        return "\n".join(" | ".join(row) for row in block["rows"])
    if kind == "code":
        return block["text"]
    return block["text"]


def chapter_text(section):
    return normalize("\n".join(block_text(block) for block in section["blocks"] if block_text(block)))


def canonical_content_hash(sections):
    value = "\n\n".join(section["title"] + "\n" + chapter_text(section) for section in sections)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def add_field(paragraph, instruction, result=""):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " " + instruction + " "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = result
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for element in (begin, instr, separate, text, end):
        run._r.append(element)


def add_inline_markdown(paragraph, text):
    """Preserve template typography, format code and make reference URLs usable."""
    cursor = 0
    for match in re.finditer(r"`([^`]+)`|https?://[^\s]+", text):
        if match.start() > cursor:
            paragraph.add_run(text[cursor:match.start()])
        if match.group(1) is not None:
            run = paragraph.add_run(match.group(1))
            run.font.name = "Consolas"
            run.font.size = Pt(10)
        else:
            url = match.group(0)
            hyperlink = OxmlElement("w:hyperlink")
            hyperlink.set(qn("r:id"), paragraph.part.relate_to(
                url, WordRelationship.HYPERLINK, is_external=True
            ))
            run = OxmlElement("w:r")
            properties = OxmlElement("w:rPr")
            style = OxmlElement("w:rStyle")
            style.set(qn("w:val"), "Hyperlink")
            properties.append(style)
            run.append(properties)
            label = OxmlElement("w:t")
            label.text = url
            run.append(label)
            hyperlink.append(run)
            paragraph._p.append(hyperlink)
        cursor = match.end()
    if cursor < len(text):
        paragraph.add_run(text[cursor:])


def clear_manual_body_preserving_front_matter(doc):
    body = doc._element.body
    controls = [child for child in body if child.tag == qn("w:sdt")]
    if len(controls) < 2:
        raise ValueError("La plantilla manual perdió la portada o el índice dinámico.")
    keep = {id(controls[0]), id(controls[1])}
    for child in body:
        if child.tag in (qn("w:bookmarkStart"), qn("w:bookmarkEnd")):
            keep.add(id(child))
        if child.tag == qn("w:sectPr"):
            keep.add(id(child))
    for child in list(body):
        if id(child) not in keep:
            body.remove(child)
    return controls[0], controls[1]


def update_manual_cover(doc, cover):
    replacements = {
        "Tema": "Manual técnico",
        "EXAMEN PRIMER PARCIAL": "COMERCIALIZADORA DE CELULARES",
        "GRUPO 1": "GRUPO 09 · NRC 36884",
        "EXAMEN PRIMER PARCIAL DOTNET": PROJECT["name"].upper(),
        "Ing. Eduardo Mauricio Campaña Ortega": PROJECT["tutor"],
        "MIS.MDU.CCNA.CCIA.": PROJECT["authors"][0],
        "PhD. (c) Ingeniería de Software": PROJECT["authors"][1],
        "PhD. (c) Seguridad Información": "",
    }
    for node in cover.iter(qn("w:t")):
        value = node.text or ""
        if value in replacements:
            node.text = replacements[value]
        elif re.fullmatch(r"\d{2}/\d{2}/\d{4}", value.strip()):
            node.text = DATE
    doc.core_properties.author = AUTHOR_LINE
    doc.core_properties.title = PROJECT["name"] + " — Manual técnico"
    doc.core_properties.subject = "Manual técnico .NET REST GR09; NRC 36884"
    doc.core_properties.keywords = "GR09, NRC 36884, REST, .NET, celulares, BanQuito"


def rebuild_manual_toc(doc, toc):
    content = toc.find(qn("w:sdtContent"))
    if content is None:
        raise ValueError("La plantilla perdió el contenido del índice dinámico.")
    for child in list(content):
        content.remove(child)

    title = OxmlElement("w:p")
    title_properties = OxmlElement("w:pPr")
    title_style = OxmlElement("w:pStyle")
    title_style.set(qn("w:val"), doc.styles["TOC Heading"].style_id)
    title_properties.append(title_style)
    title.append(title_properties)
    title_run = OxmlElement("w:r")
    title_text = OxmlElement("w:t")
    title_text.text = "ÍNDICE DE CONTENIDOS"
    title_run.append(title_text)
    title.append(title_run)
    content.append(title)

    field_paragraph = OxmlElement("w:p")
    field_properties = OxmlElement("w:pPr")
    field_style = OxmlElement("w:pStyle")
    field_style.set(qn("w:val"), doc.styles["toc 1"].style_id)
    field_properties.append(field_style)
    field_paragraph.append(field_properties)
    field_run = OxmlElement("w:r")
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = ' TOC \\o "1-2" \\h \\z \\u '
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    result = OxmlElement("w:t")
    result.text = ""
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for element in (begin, instruction, separate, result, end):
        field_run.append(element)
    field_paragraph.append(field_run)
    content.append(field_paragraph)


def add_word_image_group(doc, image_blocks, section):
    if len(image_blocks) > 1 and any("respuesta real" in b["caption"].lower() or "rechazo real" in b["caption"].lower() for b in image_blocks):
        for block in image_blocks:
            add_word_image_group(doc, [block], section)
        return
    page = doc.sections[-1]
    max_width = page.page_width - page.left_margin - page.right_margin
    max_height = min(
        page.page_height - page.top_margin - page.bottom_margin - Inches(1.5),
        Inches(5.25),
    )
    columns = min(2, len(image_blocks))
    image_width = int((max_width - Inches(0.18) * (columns - 1)) / columns)
    max_height = int(max_height)

    if len(image_blocks) > 2:
        rows = (len(image_blocks) + 1) // 2
        table = doc.add_table(rows=rows, cols=2)
        table.autofit = False
        column_width = int((max_width - Inches(0.18)) / 2)
        for column in table.columns:
            column.width = column_width
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            border = OxmlElement(f"w:{edge}")
            border.set(qn("w:val"), "nil")
            borders.append(border)
        table._tbl.tblPr.append(borders)
        for index, block in enumerate(image_blocks):
            cell = table.cell(index // 2, index % 2)
            cell.width = column_width
            image_paragraph = cell.paragraphs[0]
            image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            image_paragraph.paragraph_format.keep_with_next = True
            with Image.open(block["path"]) as bitmap:
                scale = min(column_width / bitmap.width, max_height / bitmap.height)
                width = int(bitmap.width * scale)
                height = int(bitmap.height * scale)
            image_paragraph.add_run().add_picture(str(block["path"]), width=width, height=height)
            caption = cell.add_paragraph(style="Caption" if "Caption" in doc.styles else "Normal")
            caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
            caption.paragraph_format.keep_together = True
            caption.add_run("Figura ")
            add_field(caption, "SEQ Figura \\* ARABIC", "1")
            caption.add_run(". " + block["caption"])
        for row in table.rows:
            row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        doc.add_paragraph()
        return

    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.keep_with_next = True
    captions = []
    for index, block in enumerate(image_blocks):
        with Image.open(block["path"]) as bitmap:
            scale = min(image_width / bitmap.width, max_height / bitmap.height)
            width = int(bitmap.width * scale)
            height = int(bitmap.height * scale)
        if index:
            paragraph.add_run("   ")
        paragraph.add_run().add_picture(str(block["path"]), width=width, height=height)
        captions.append(block["caption"])
    caption = doc.add_paragraph(style="Caption" if "Caption" in doc.styles else "Normal")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.keep_together = True
    for index, text in enumerate(captions):
        if index:
            caption.add_run("     ")
        caption.add_run("Figura ")
        add_field(caption, "SEQ Figura \\* ARABIC", "1")
        caption.add_run(". " + text)


def add_test_result_label(doc, title):
    label = re.sub(r"^Prueba:\s*", "", title, flags=re.IGNORECASE)
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(5)
    paragraph.paragraph_format.space_after = Pt(1)
    paragraph.paragraph_format.keep_with_next = True
    paragraph.add_run(label).bold = True


def table_caption_for_section(section):
    title = section["title"].casefold()
    captions = (
        ("contrato rest", "Métodos y recursos REST confirmados"),
        ("configuración de sql server", "Parámetros de SQL Server local"),
        ("configuración de los proyectos en visual studio", "Archivos de configuración revisados"),
        ("secuencia de scripts", "Secuencia de inicialización de las bases"),
        ("verificación y solución de problemas", "Comprobaciones y errores frecuentes"),
        ("modelo de datos", "Tablas, relaciones y reglas de datos"),
        ("estructura del proyecto", "Organización de carpetas y responsabilidades"),
        ("arquitectura y comunicación", "Direcciones y consumidores de los servicios"),
        ("creación y carga", "Orden de ejecución de los scripts SQL"),
        ("contratos rest de la comercializadora", "Recursos HTTP de la comercializadora"),
        ("contratos rest de banquito", "Recursos HTTP de BanQuito"),
        ("cálculo y consulta de amortización", "Ejemplo de amortización de 450,00 a tres meses"),
        ("capa compartida", "Configuración del destino HTTP de los clientes"),
        ("cliente de consola", "Opciones del menú de consola"),
        ("pruebas de los servicios", "Entradas y criterios de comprobación funcional"),
        ("manejo de errores", "Diagnóstico y tratamiento de errores frecuentes"),
    )
    return next((caption for prefix, caption in captions if prefix in title), "Configuración y responsabilidades del componente")


def render_word_block(doc, block, section):
    kind = block["kind"]
    if kind == "paragraph":
        p = doc.add_paragraph()
        add_inline_markdown(p, block["text"])
        if section["title"] == "Referencias bibliográficas":
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.keep_together = True
    elif kind == "heading":
        if block["text"].casefold().startswith("prueba:"):
            add_test_result_label(doc, block["text"])
        else:
            doc.add_heading(block["text"], level=2)
    elif kind == "list":
        style = "List Bullet" if "List Bullet" in doc.styles else "Normal"
        p = doc.add_paragraph(style=style)
        add_inline_markdown(p, block["text"])
    elif kind == "table":
        rows = block["rows"]
        columns = max(len(row) for row in rows)
        caption = doc.add_paragraph(style="Caption" if "Caption" in doc.styles else "Normal")
        caption.add_run("Tabla ")
        add_field(caption, "SEQ Tabla \\* ARABIC", "1")
        caption.add_run(". " + table_caption_for_section(section))
        table = doc.add_table(rows=0, cols=columns)
        table.style = "Table Grid" if "Table Grid" in [style.name for style in doc.styles] else doc.tables[0].style
        table.autofit = True
        for row_index, values in enumerate(rows):
            cells = table.add_row().cells
            for column, value in enumerate(values):
                add_inline_markdown(cells[column].paragraphs[0], value)
                for paragraph in cells[column].paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(10)
                        if row_index == 0:
                            run.bold = True
            tr_pr = table.rows[-1]._tr.get_or_add_trPr()
            tr_pr.append(OxmlElement("w:cantSplit"))
        if rows:
            table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
        doc.add_paragraph()
    elif kind == "code":
        if block.get("file_label"):
            table = doc.add_table(rows=2, cols=1)
            table.style = "Table Grid"
            table.cell(0, 0).text = "Archivo: " + block["file_label"]
            table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
            for run in table.cell(0, 0).paragraphs[0].runs:
                run.font.size = Pt(10)
                run.bold = True
            paragraph = table.cell(1, 0).paragraphs[0]
        else:
            paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.left_indent = Inches(0.12)
        paragraph.paragraph_format.right_indent = Inches(0.12)
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.0
        paragraph.paragraph_format.keep_together = False
        run = paragraph.add_run(block["text"])
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        run.font.color.rgb = WordRGBColor(31, 41, 55)
    elif kind == "image":
        add_word_image_group(doc, [block], section)


def generate_manual_word(template, source, target, sections):
    doc = Document(template)
    cover, toc = clear_manual_body_preserving_front_matter(doc)
    update_manual_cover(doc, cover)
    # Keep the approved master cover image, crop, position, and frame unchanged.
    rebuild_manual_toc(doc, toc)

    for title, instruction in (
        ("ÍNDICE DE ILUSTRACIONES", 'TOC \\h \\z \\c "Figura"'),
        ("ÍNDICE DE TABLAS", 'TOC \\h \\z \\c "Tabla"'),
    ):
        doc.add_heading(title, level=1)
        add_field(doc.add_paragraph(), instruction, "")
    doc.add_page_break()

    normal = doc.styles["Normal"]
    normal.font.size = Pt(11)
    landscape = False
    for index, section in enumerate(sections):
        wide = section["title"].startswith(("Código fuente", "Anexo A.", "Anexo B."))
        if wide != landscape:
            page = doc.add_section(WD_SECTION_START.NEW_PAGE)
            page.orientation = WD_ORIENT.LANDSCAPE if wide else WD_ORIENT.PORTRAIT
            page.page_width = Inches(11.693 if wide else 8.268)
            page.page_height = Inches(8.268 if wide else 11.693)
            page.left_margin = Inches(.886 if wide else 1.18125)
            page.right_margin = Inches(.886 if wide else 1.18125)
            landscape = wide
        if section["title"].casefold().startswith("prueba:"):
            add_test_result_label(doc, section["title"])
        else:
            heading = doc.add_heading(section["title"], level=1)
            if section["title"].casefold().startswith("diagrama:"):
                heading.paragraph_format.page_break_before = True
        # Group only adjacent images: keep each procedure beside its evidence.
        pending_images = []
        for block in section["blocks"]:
            if block["kind"] == "image":
                pending_images.append(block)
                continue
            if pending_images:
                add_word_image_group(doc, pending_images, section)
                pending_images = []
            render_word_block(doc, block, section)
        if pending_images:
            add_word_image_group(doc, pending_images, section)
    doc.save(target)


def replace_frame_text(shape, text):
    frame = shape.text_frame
    lines = text.splitlines() or [""]
    paragraphs = list(frame.paragraphs)
    sample_paragraph = paragraphs[0]
    sample_run = next((run for paragraph in paragraphs for run in paragraph.runs), None)
    while len(paragraphs) < len(lines):
        paragraph = frame.add_paragraph()
        if sample_paragraph._p.pPr is not None:
            if paragraph._p.pPr is not None:
                paragraph._p.remove(paragraph._p.pPr)
            paragraph._p.insert(0, copy.deepcopy(sample_paragraph._p.pPr))
        if sample_run is not None:
            run = paragraph.add_run()
            if sample_run._r.rPr is not None:
                run._r.insert(0, copy.deepcopy(sample_run._r.rPr))
        paragraphs.append(paragraph)
    for index, line in enumerate(lines):
        paragraph = paragraphs[index]
        runs = paragraph.runs
        if runs:
            runs[0].text = line
            for run in runs[1:]:
                run.text = ""
        else:
            run = paragraph.add_run()
            if sample_run is not None and sample_run._r.rPr is not None:
                run._r.insert(0, copy.deepcopy(sample_run._r.rPr))
            run.text = line
    for paragraph in paragraphs[len(lines):]:
        paragraph._p.getparent().remove(paragraph._p)
    frame.word_wrap = True


def replace_frame_text_soft(shape, text):
    """Use DrawingML line breaks in one paragraph, retaining the template run style."""
    frame = shape.text_frame
    paragraphs = list(frame.paragraphs)
    paragraph = paragraphs[0]
    sample_run = next((run for run in paragraph.runs), None)
    sample_rpr = copy.deepcopy(sample_run._r.rPr) if sample_run is not None and sample_run._r.rPr is not None else None
    for extra in paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    for child in list(paragraph._p):
        if child.tag in (qn("a:r"), qn("a:br"), qn("a:fld")):
            paragraph._p.remove(child)
    lines = text.splitlines() or [""]
    for index, line in enumerate(lines):
        if index:
            line_break = OxmlElement("a:br")
            if sample_rpr is not None:
                line_break.append(copy.deepcopy(sample_rpr))
            paragraph._p.append(line_break)
        run = paragraph.add_run()
        if sample_rpr is not None:
            run._r.insert(0, copy.deepcopy(sample_rpr))
        run.text = line
    frame.word_wrap = True


def replace_frame_text_compact(shape, text):
    replace_frame_text(shape, text)
    for paragraph in shape.text_frame.paragraphs:
        paragraph.space_before = 0
        paragraph.space_after = 0
        paragraph.line_spacing = 1.0


def fit_picture(slide, path, bounds, crop=None):
    left, top, width, height = bounds
    with Image.open(path) as bitmap:
        source = str(path)
        if crop is not None:
            x1, y1, x2, y2 = crop
            bitmap = bitmap.crop((int(x1 * bitmap.width), int(y1 * bitmap.height),
                                  int(x2 * bitmap.width), int(y2 * bitmap.height)))
            source = io.BytesIO()
            bitmap.save(source, format="PNG")
            source.seek(0)
        scale = min(width / bitmap.width, height / bitmap.height)
        fitted_width = int(bitmap.width * scale)
        fitted_height = int(bitmap.height * scale)
    return slide.shapes.add_picture(
        source,
        int(left + (width - fitted_width) / 2),
        int(top + (height - fitted_height) / 2),
        width=fitted_width,
        height=fitted_height,
    )


def replace_slide_images(slide, image_blocks):
    old_pictures = [shape for shape in slide.shapes if shape.shape_type == 13]
    if not image_blocks:
        for shape in old_pictures:
            shape._element.getparent().remove(shape._element)
        return
    if old_pictures:
        left = min(shape.left for shape in old_pictures)
        top = min(shape.top for shape in old_pictures)
        right = max(shape.left + shape.width for shape in old_pictures)
        bottom = max(shape.top + shape.height for shape in old_pictures)
        bounds = (left, top, right - left, bottom - top)
    else:
        bounds = (PInches(0.85), PInches(3.0), PInches(8.8), PInches(3.65))
    for shape in old_pictures:
        shape._element.getparent().remove(shape._element)
    count = len(image_blocks)
    gap = PInches(0.12)
    column_width = int((bounds[2] - gap * (count - 1)) / count)
    for index, block in enumerate(image_blocks):
        fit_picture(slide, block["path"], (
            bounds[0] + index * (column_width + gap), bounds[1], column_width, bounds[3]
        ), block.get("crop"))


def slide_body(sections):
    result = []
    for section in sections:
        parts = [] if section.get("_compact") else [section["title"]]
        for block in section["blocks"]:
            if block["kind"] == "image":
                continue
            text = block_text(block)
            if text:
                if block["kind"] != "code":
                    text = text.replace("`", "").replace("**", "")
                if block["kind"] == "code" and block.get("file_label"):
                    parts.append("Archivo: " + block["file_label"])
                parts.append(text)
        result.append("\n".join(parts))
    return "\n".join(result)


def format_slide_code_blocks(shape, sections, compact=False):
    """Use compact monospaced, unbulleted text for SQL/config code on slides."""
    parts = []
    intervals = []
    offset = 0
    def append(text, code=False):
        nonlocal offset
        if parts:
            offset += 1
        if code:
            intervals.append((offset, offset + len(text)))
        parts.append(text)
        offset += len(text)
    for section in sections:
        if not section.get("_compact"):
            append(section["title"])
        for block in section["blocks"]:
            if block["kind"] == "image":
                continue
            text = block_text(block)
            if not text:
                continue
            if block["kind"] == "code":
                if block.get("file_label"):
                    append("Archivo: " + block["file_label"])
                append(text, code=True)
            else:
                append(text.replace("`", "").replace("**", ""))
    code_paragraphs = set()
    offset = 0
    for index, line in enumerate("\n".join(parts).splitlines(keepends=True)):
        if any(start <= offset < end for start, end in intervals):
            code_paragraphs.add(index)
        offset += len(line)

    paragraphs = shape.text_frame.paragraphs
    for index in code_paragraphs:
        if index >= len(paragraphs):
            raise ValueError("No se pudo dar formato a todos los renglones de código de la diapositiva.")
        paragraph = paragraphs[index]
        paragraph.level = 0
        p_pr = paragraph._p.get_or_add_pPr()
        for child in list(p_pr):
            if child.tag in {
                ppt_qn("a:buChar"), ppt_qn("a:buAutoNum"),
                ppt_qn("a:buBlip"), ppt_qn("a:buNone"),
            }:
                p_pr.remove(child)
        p_pr.append(PptOxmlElement("a:buNone"))
        p_pr.set("marL", "0")
        p_pr.set("indent", "0")
        for run in paragraph.runs:
            run.font.name = "Consolas"
            run.font.size = PPt(13 if compact else 11)
            run.font.color.rgb = RGBColor(48, 54, 61)


def presentation_line_count(text):
    return sum(max(1, (len(line) + 74) // 75) for line in text.splitlines() or [text])


def split_text_preserving_content(text, max_chars=1000):
    """Split a long textual block at word boundaries while retaining every character."""
    parts = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end < len(text):
            boundary = text.rfind(" ", start + max_chars // 2, end)
            if boundary > start:
                end = boundary + 1
        parts.append(text[start:end])
        start = end
    return parts


def split_block_for_presentation(block, max_lines=10):
    """Create readable slide fragments for long blocks without changing the Word source."""
    if presentation_line_count(block_text(block)) <= max_lines:
        return [block]

    if block["kind"] == "table":
        rows = block["rows"]
        if len(rows) <= 1:
            return [block]
        header = rows[0]
        header_lines = presentation_line_count(" | ".join(header))
        chunks = []
        current = [header]
        current_lines = header_lines
        for row in rows[1:]:
            row_lines = presentation_line_count(" | ".join(row))
            if len(current) > 1 and current_lines + row_lines > max_lines:
                chunks.append(current)
                current = [header]
                current_lines = header_lines
            current.append(row)
            current_lines += row_lines
        if current:
            chunks.append(current)
        return [
            {"kind": "table", "rows": chunk, "_canonical_block": block}
            for chunk in chunks
        ]

    if block["kind"] == "code":
        lines = [part for line in block["text"].splitlines(keepends=True)
                 for part in split_text_preserving_content(line, max_chars=600)]
        chunks = []
        current = []
        current_lines = 0
        for line in lines:
            line_count = presentation_line_count(line)
            if current and current_lines + line_count > max_lines:
                chunks.append("".join(current))
                current = []
                current_lines = 0
            current.append(line)
            current_lines += line_count
        if current:
            chunks.append("".join(current))
        return [
            {**block, "text": chunk, "_canonical_block": block}
            for chunk in chunks
        ]

    if block["kind"] == "paragraph":
        return [
            {"kind": "paragraph", "text": part, "_canonical_block": block}
            for part in split_text_preserving_content(block["text"])
        ]
    return [block]


def chunk_section_blocks(section, source_index, max_lines=10):
    fragments = []
    for block in section["blocks"]:
        fragments.extend(split_block_for_presentation(block))

    chunks = []
    current = []
    current_lines = 1  # section title
    for block in fragments:
        block_lines = presentation_line_count(block_text(block))
        if current and current_lines + block_lines > max_lines:
            chunks.append(current)
            current = []
            current_lines = 1
        current.append(block)
        current_lines += block_lines
    if current:
        chunks.append(current)

    result = []
    for index, chunk in enumerate(chunks):
        title = section["title"]
        if index:
            title += " (continuación)"
        result.append({
            **section,
            "title": title,
            "blocks": chunk,
            "_source_index": source_index,
        })
    return result


def image_ratio(block):
    with Image.open(block["path"]) as bitmap:
        crop = block.get("crop", [0, 0, 1, 1])
        return bitmap.width * (crop[2] - crop[0]) / (bitmap.height * (crop[3] - crop[1]))


def compact_presentation_groups(sections, source):
    """Select verified canonical blocks without changing the Word generator."""
    selection_path = ROOT / "scripts/presentacion_compacta.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if sha(source) != selection["canonicalSha256"]:
        raise ValueError("La fuente canónica cambió; revisar la selección compacta antes de regenerar.")
    groups = []
    for item in selection["slides"]:
        section = sections[item["section"]]
        blocks = []
        for selector in item["blocks"]:
            selector = {"index": selector} if isinstance(selector, int) else selector
            block = dict(section["blocks"][selector["index"]])
            if "rows" in selector:
                first, last = selector["rows"]
                if block["kind"] != "table" or not 1 <= first < last <= len(block["rows"]):
                    raise ValueError(f"Selección de filas inválida: {item['title']}")
                block["rows"] = block["rows"][:1] + block["rows"][first:last]
            if "lines" in selector:
                first, last = selector["lines"]
                lines = block.get("text", "").splitlines()
                if block["kind"] != "code" or not 0 <= first < last <= len(lines):
                    raise ValueError(f"Selección de código inválida: {item['title']}")
                block["text"] = "\n".join(lines[first:last])
            if "crop" in selector:
                x1, y1, x2, y2 = selector["crop"]
                if block["kind"] != "image" or not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
                    raise ValueError(f"Recorte de imagen inválido: {item['title']}")
                block["crop"] = selector["crop"]
            blocks.append(block)
        if not blocks:
            raise ValueError(f"Diapositiva sin contenido: {item['title']}")
        section_number = item["section"]
        if section_number in (0, 1, 2, 3):
            nav = "OBJETIVO Y ALCANCE"
        elif section_number in (4, 5, 6, 7, 11, 12):
            nav = "ARQUITECTURA"
        elif section_number in (8, 9, 10):
            nav = "MODELO DE DATOS"
        elif section_number in (14, 16):
            nav = "CONTRATO REST"
        elif section_number in (13, 15, 17, 18, 19, 20, 21):
            nav = "VENTAS Y CRÉDITO"
        elif section_number in (38, 39, 40, 41):
            nav = "PRUEBAS Y EVIDENCIAS"
        elif section_number == 43:
            nav = "CONCLUSIONES"
        elif section_number in (42, 44):
            nav = "RECOMENDACIONES"
        elif section_number == 45:
            nav = "BIBLIOGRAFÍA"
        else:
            nav = "CLIENTES"
        groups.append([{ "title": item["title"], "blocks": blocks, "_compact": True,
                        "_gallery_title": item["title"], "_nav": nav }])
    if len(groups) + 2 > 100:
        raise ValueError("La presentación compacta supera las 100 diapositivas.")
    required_images = {
        "PowerDesigner: arquitectura cliente-servidor", "PowerDesigner: modelo físico comercializadora",
        "PowerDesigner: clases del servicio y cliente", "PowerDesigner: secuencia de venta a crédito",
        "PowerDesigner: casos de uso de ventas", "PowerDesigner: actividad de venta a crédito",
        "Consulta real desde consola", "Consulta real desde WPF", "Navegador: catálogo en tema claro",
        "Navegador: detalle de venta en efectivo", "Navegador: detalle y amortización de crédito",
        "Android: catálogo inicial", "Android: detalle de venta en efectivo",
        "Android: detalle de compra a crédito", "Android: amortización a tres cuotas",
        "Android: búsqueda y reapertura de factura",
    }
    selected_images = {block["caption"] for group in groups for section in group
                       for block in section["blocks"] if block["kind"] == "image"}
    if missing := required_images - selected_images:
        raise ValueError("Faltan figuras requeridas de la presentación: " + ", ".join(sorted(missing)))
    return groups, selection_path, selection


def group_presentation_sections(sections):
    groups = []
    pending = []
    expanded = []

    for source_index, section in enumerate(sections):
        blocks = section["blocks"]
        index = 0
        while index < len(blocks):
            images = blocks[index]["kind"] == "image"
            end = index + 1
            while end < len(blocks) and (blocks[end]["kind"] == "image") == images:
                end += 1
            run = blocks[index:end]
            if not images:
                expanded.extend(chunk_section_blocks({**section, "blocks": run}, source_index))
            else:
                offset = 0
                while offset < len(run):
                    count = 1 if image_ratio(run[offset]) >= 1.8 or "respuesta real" in run[offset]["caption"].lower() or "rechazo real" in run[offset]["caption"].lower() else 2
                    gallery = run[offset:offset + count]
                    label = gallery[0]["caption"].removeprefix("PowerDesigner: ")
                    if len(gallery) > 1:
                        label = section["title"].replace("Cliente móvil:", "Android:").replace("Cliente web:", "Web:")
                    expanded.append({**section, "blocks": gallery,
                                     "_source_index": source_index, "_gallery_title": label})
                    offset += count
            index = end

    def flush():
        if pending:
            groups.append(pending.copy())
            pending.clear()

    for section in expanded:
        title = section["title"].casefold()
        groupable = title.startswith("prueba:") or title.startswith(("consola ", "web ")) or title == "catálogo cargado"
        has_images = any(block["kind"] == "image" for block in section["blocks"])
        if not groupable or has_images:
            flush()
            groups.append([section])
            continue
        candidate = pending + [section]
        candidate_text = slide_body(candidate)
        lines = presentation_line_count(candidate_text)
        if pending and (lines > 14 or len(candidate) > 5):
            flush()
        pending.append(section)
    flush()
    grouped_sections = [section for group in groups for section in group]
    expected_blocks = {
        id(block): block for section in sections for block in section["blocks"]
    }
    actual_parts = {}
    for section in grouped_sections:
        for block in section["blocks"]:
            source_block = block.get("_canonical_block", block)
            actual_parts.setdefault(id(source_block), []).append(block)
    if set(actual_parts) != set(expected_blocks):
        raise ValueError("La distribución PPTX omitió o agregó bloques canónicos.")
    for block_id, source_block in expected_blocks.items():
        parts = actual_parts[block_id]
        if source_block["kind"] == "table":
            rows = []
            for part in parts:
                part_rows = part["rows"]
                if rows and part_rows and part_rows[0] == source_block["rows"][0]:
                    part_rows = part_rows[1:]
                rows.extend(part_rows)
            if rows != source_block["rows"]:
                raise ValueError("La distribución PPTX alteró filas de una tabla canónica.")
        elif source_block["kind"] in ("paragraph", "code"):
            if "".join(part["text"] for part in parts) != source_block["text"]:
                raise ValueError("La distribución PPTX alteró un bloque de texto canónico.")
        elif len(parts) != 1 or parts[0] is not source_block:
            raise ValueError("La distribución PPTX duplicó un bloque canónico.")
    source_order = list(dict.fromkeys(section["_source_index"] for section in grouped_sections))
    if source_order != list(range(len(sections))):
        raise ValueError("La distribución PPTX omitió o reordenó capítulos canónicos.")
    return groups


def slide_text_height(text, width, available_height, template_shape):
    """Estimate a readable text box height while retaining the template font."""
    font_pt = 18
    for paragraph in template_shape.text_frame.paragraphs:
        for run in paragraph.runs:
            if run.font.size:
                font_pt = run.font.size.pt
                break
            rpr = run._r.rPr
            if rpr is not None and rpr.get("sz"):
                font_pt = int(rpr.get("sz")) / 100
                break
        else:
            continue
        break
    chars_per_line = max(32, int(width * 8.0))
    lines = 0
    for raw_line in text.splitlines() or [text]:
        line = raw_line.strip()
        if not line:
            lines += 1
        else:
            lines += max(1, (len(line) + chars_per_line - 1) // chars_per_line)
    line_height = max(0.24, font_pt / 72 * 1.28)
    return min(available_height, max(PInches(0.72), int(PInches(0.24) + lines * line_height * 914400)))


def fit_slide_body(slide, content, sections):
    """Use the template content canvas and reserve space below for real figures."""
    images = [block for section in sections for block in section["blocks"] if block["kind"] == "image"]
    nav_left = min(
        (shape.left for shape in slide.shapes
         if shape.has_text_frame and "MARCO TE" in shape.text.upper()),
        default=PInches(10.2),
    )
    left = max(content.left, PInches(0.62))
    right = min(nav_left - PInches(0.22), PInches(10.05))
    width = right - left
    top = max(content.top, PInches(2.12))
    bottom = PInches(6.88)
    if not images:
        content.left = left
        content.width = width
        content.top = top
        content.height = bottom - top
        content.text_frame.auto_size = MSO_AUTO_SIZE.NONE
        content.text_frame.vertical_anchor = MSO_ANCHOR.TOP
        return None

    requested_height = slide_text_height(slide_body(sections), width / 914400, bottom - top - PInches(1.25), content)
    max_height = bottom - top - PInches(1.15)
    content.left = left
    content.width = width
    content.top = top
    content.height = min(max_height, requested_height)
    content.text_frame.auto_size = MSO_AUTO_SIZE.NONE
    image_top = content.top + content.height + PInches(0.15)
    return (PInches(0.82), image_top, PInches(8.85), bottom - image_top)


def first_diagram(sections):
    for section in sections:
        if "arquitectura" in section["title"].casefold():
            for block in section["blocks"]:
                if block["kind"] == "image":
                    return block
    for section in sections:
        for block in section["blocks"]:
            if block["kind"] == "image":
                return block
    return None


def set_slide_number(slide, number):
    for shape in slide.shapes:
        if shape.has_text_frame and shape.text.strip().isdigit() and not shape.is_placeholder:
            replace_frame_text(shape, str(number))


def move_image_only_template_to_matching_chapter(prs, groups):
    """Keep the template's image-only page for a canonical figure chapter."""
    slide_ids = list(prs.slides._sldIdLst)
    special_positions = []
    for position, slide in enumerate(prs.slides):
        if position < 2:
            continue
        placeholders = {shape.placeholder_format.idx for shape in slide.placeholders}
        if 0 in placeholders and 1 not in placeholders:
            special_positions.append(position)
    candidates = []
    for index, group in enumerate(groups):
        images = [block for section in group for block in section["blocks"] if block["kind"] == "image"]
        other = [block for section in group for block in section["blocks"] if block["kind"] != "image"]
        if len(group) == 1 and len(images) == 1 and not other:
            candidates.append(index)
    if len(special_positions) > len(candidates):
        raise ValueError(
            "La estructura de páginas sin cuerpo de la plantilla ya no corresponde "
            "a capítulos de figura de la fuente canónica."
        )
    selected = []
    for special in special_positions:
        special_slide = prs.slides[special]
        picture = next((shape for shape in special_slide.shapes if shape.shape_type == 13), None)
        target_ratio = (picture.width / picture.height) if picture and picture.height else 1.8
        remaining = [index for index in candidates if index not in selected]
        def ratio(index):
            image_path = next(block["path"] for section in groups[index] for block in section["blocks"] if block["kind"] == "image")
            with Image.open(image_path) as bitmap:
                return bitmap.width / bitmap.height
        candidate = min(remaining, key=lambda index: abs(ratio(index) - target_ratio))
        selected.append(candidate)
    for special, candidate in zip(special_positions, selected):
        target_position = candidate + 2
        slide_ids[special], slide_ids[target_position] = slide_ids[target_position], slide_ids[special]
    sld_id_list = prs.slides._sldIdLst
    for child in list(sld_id_list):
        sld_id_list.remove(child)
    for child in slide_ids:
        sld_id_list.append(child)


def extend_presentation_with_template_slides(prs, required_count):
    """Add content slides that retain the approved template layout and navigation."""
    content_template = next((
        slide for slide in prs.slides
        if {0, 1}.issubset({shape.placeholder_format.idx for shape in slide.placeholders})
        and not any(shape.shape_type == 13 for shape in slide.shapes)
        and any(shape.has_text_frame and "MARCO TE" in shape.text.upper() for shape in slide.shapes)
    ), None)
    if content_template is None:
        raise ValueError("No se encontró una diapositiva de contenido de la plantilla para ampliar el manual.")

    excluded_tags = ("}nvGrpSpPr", "}grpSpPr", "}extLst")
    source_tree = content_template.shapes._spTree
    while len(prs.slides) < required_count:
        slide = prs.slides.add_slide(content_template.slide_layout)
        tree = slide.shapes._spTree
        for child in list(tree):
            if not child.tag.endswith(excluded_tags):
                tree.remove(child)
        for child in source_tree:
            if not child.tag.endswith(excluded_tags):
                tree.append(copy.deepcopy(child))


def presentation_image_title(section):
    if "_gallery_title" in section:
        return section["_gallery_title"]
    title = section["title"].strip()
    normalized_title = title.casefold()
    short_titles = {
        "prueba: catálogo, consulta, alta y edición": "PRUEBA: CATÁLOGO Y EDICIÓN",
        "prueba: efectivo: descuento 189 y total 261": "PRUEBA: VENTA EN EFECTIVO",
        "prueba: crédito 450 aprobado sin descuento": "PRUEBA: CRÉDITO APROBADO",
        "prueba: amortización a 3 meses: filas, capital y saldo": "PRUEBA: AMORTIZACIÓN A 3 MESES",
        "prueba: tabla bancaria coincide con pasarela": "PRUEBA: AMORTIZACIÓN Y SALDO",
        "prueba: consulta factura y búsqueda por cédula": "PRUEBA: BÚSQUEDA DE FACTURA",
    }
    if normalized_title in short_titles:
        return short_titles[normalized_title]
    if "_gallery_start" in section and normalized_title.startswith("diseño web adaptable"):
        return (
            f"VISTA WEB 390 PX · TRAMOS {section['_gallery_start']}–"
            f"{section['_gallery_end']}/{section['_gallery_total']}"
        )
    return re.sub(r"^Diagrama:\s*", "", title, flags=re.IGNORECASE)


def update_sidebar(slide, nav_text, active_item):
    nav_levels = [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
    for shape in slide.shapes:
        if not shape.has_text_frame or shape.is_placeholder:
            continue
        if "MARCO TE" not in shape.text.upper() and "DESARROLLO" not in shape.text.upper():
            continue
        replace_frame_text(shape, nav_text)
        for index, paragraph in enumerate(shape.text_frame.paragraphs):
            if index < len(nav_levels):
                paragraph.level = nav_levels[index]
            selected = paragraph.text.strip().casefold() == active_item.casefold()
            selected_parent = active_item not in ("CONCLUSIONES", "RECOMENDACIONES", "BIBLIOGRAFÍA") and paragraph.text.strip() == "DESARROLLO"
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor(255, 255, 255)
                if selected or selected_parent:
                    run.font.color.rgb = RGBColor(255, 220, 0)
                    run.font.bold = True


def generate_presentation(template, source, target, sections, groups=None, compact=False):
    prs = Presentation(template)
    if groups is None:
        groups = group_presentation_sections(sections)
    if len(groups) + 2 > len(prs.slides):
        extend_presentation_with_template_slides(prs, len(groups) + 2)
    move_image_only_template_to_matching_chapter(prs, groups)
    cover = prs.slides[0]
    title_shape = next((shape for shape in cover.placeholders if shape.placeholder_format.idx == 0), None)
    subtitle_shape = next((shape for shape in cover.placeholders if shape.placeholder_format.idx == 1), None)
    if title_shape is None or subtitle_shape is None:
        raise ValueError("La portada de PowerPoint no conserva los marcadores de título e integrantes.")
    replace_frame_text_compact(title_shape, "MANUAL TÉCNICO\nCOMERCIALIZADORA DE CELULARES Y BANQUITO")
    replace_frame_text_compact(
        subtitle_shape,
        "Autores:\n" + PROJECT["authors"][0] + "\n" + PROJECT["authors"][1]
        + "\n" + PROJECT["group"] + " · NRC " + PROJECT["nrc"],
    )
    for shape in cover.shapes:
        if shape.has_text_frame and "FECHA:" in shape.text.upper():
            shape.left = PInches(8.55)
            shape.width = PInches(4.35)
            replace_frame_text_compact(shape, "FECHA: " + DATE + "\nTUTOR: " + PROJECT["tutor"])
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = PPt(12)
    cover_pictures = [shape for shape in cover.shapes if shape.shape_type == 13]
    if cover_pictures and not compact:
        old = cover_pictures[0]
        bounds = (old.left, old.top, old.width, old.height)
        old._element.getparent().remove(old._element)
        fit_picture(cover, ROOT / "assets/celulares/prisma.jpg", bounds)

    outline = [
        "DESARROLLO", "OBJETIVO Y ALCANCE", "ARQUITECTURA Y CONFIGURACIÓN",
        "MODELO DE DATOS Y SQL SERVER", "CONTRATO REST", "VENTA EN EFECTIVO Y CRÉDITO",
        "CLIENTES: CONSOLA, WPF, WEB Y ANDROID", "PRUEBAS Y EVIDENCIAS",
        "DIAGRAMAS", "CONCLUSIONES Y RECOMENDACIONES", "BIBLIOGRAFÍA",
    ]
    toc = prs.slides[1]
    toc_text = next((shape for shape in toc.placeholders if shape.placeholder_format.idx == 1), None)
    if toc_text is None:
        raise ValueError("El índice de la presentación no conserva su marcador de contenido.")
    replace_frame_text(toc_text, "\n".join(outline))
    diagram = first_diagram(sections)
    if diagram:
        replace_slide_images(toc, [diagram])
    for shape in toc.shapes:
        if shape.has_text_frame and "EUREKA" in shape.text.upper():
            replace_frame_text(shape, "")
    set_slide_number(toc, 2)

    nav_items = [
        "MARCO DE REFERENCIA", "DESARROLLO", "OBJETIVO Y ALCANCE", "ARQUITECTURA",
        "MODELO DE DATOS", "CONTRATO REST", "CLIENTES", "VENTAS Y CRÉDITO",
        "PRUEBAS Y EVIDENCIAS", "CONCLUSIONES", "RECOMENDACIONES", "BIBLIOGRAFÍA",
    ]
    nav = "\n".join(nav_items)
    for slide_index, group in enumerate(groups, start=2):
        slide = prs.slides[slide_index]
        title = next((shape for shape in slide.placeholders if shape.placeholder_format.idx == 0), None)
        content = next((shape for shape in slide.placeholders if shape.placeholder_format.idx == 1), None)
        if title is None:
            raise ValueError(f"La diapositiva {slide_index + 1} no conserva el título del master.")
        if content is None:
            image_blocks = [block for section in group for block in section["blocks"] if block["kind"] == "image"]
            non_image_blocks = [block for section in group for block in section["blocks"] if block["kind"] != "image"]
            if len(group) != 1 or len(image_blocks) != 1 or non_image_blocks:
                raise ValueError(f"La diapositiva {slide_index + 1} solo admite un capítulo formado por una figura.")
            slide_title = presentation_image_title(group[0]).upper()
            replace_frame_text(title, slide_title)
            replace_slide_images(slide, image_blocks)
            update_sidebar(slide, nav, group[0].get("_nav", "ARQUITECTURA"))
            set_slide_number(slide, slide_index + 1)
            continue
        label = " ".join(section["title"] for section in group).casefold()
        image_blocks = [block for section in group for block in section["blocks"] if block["kind"] == "image"]
        non_image_blocks = [block for section in group for block in section["blocks"] if block["kind"] != "image"]
        image_only = (
            len(group) == 1
            and len(image_blocks) >= 1
            and not non_image_blocks
        )
        if compact:
            replace_frame_text(title, group[0]["title"].upper())
        elif len(group) == 1 and (group[0]["title"].casefold() in ("conclusiones", "recomendaciones") or group[0]["title"].casefold().startswith(("bibliografía", "referencias bibliográficas"))):
            replace_frame_text(title, group[0]["title"].upper())
        elif image_only:
            slide_title = presentation_image_title(group[0]).upper()
            replace_frame_text(title, slide_title)
        else:
            replace_frame_text(title, "DESARROLLO")
        amortization_table = None
        body_group = group
        if compact and group[0]["title"] == "Amortización: ejemplo de cuotas":
            amortization_table = next(block for block in group[0]["blocks"] if block["kind"] == "table")
            body_group = [{**group[0], "blocks": [block for block in group[0]["blocks"] if block["kind"] != "table"]}]
        replace_frame_text(content, "" if image_only else slide_body(body_group))
        if not image_only:
            format_slide_code_blocks(content, body_group, compact)
        if amortization_table:
            rows = amortization_table["rows"]
            table = slide.shapes.add_table(len(rows), len(rows[0]), PInches(0.8), PInches(3.55),
                                          PInches(8.7), PInches(2.55)).table
            for row_index, row in enumerate(rows):
                for column_index, value in enumerate(row):
                    cell = table.cell(row_index, column_index)
                    cell.text = value
                    cell.margin_left = cell.margin_right = PInches(0.08)
                    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(24, 46, 91) if row_index == 0 else RGBColor(245, 248, 251)
                    for paragraph in cell.text_frame.paragraphs:
                        paragraph.alignment = PP_ALIGN.CENTER
                        for run in paragraph.runs:
                            run.font.name = "Cambria"
                            run.font.size = PPt(16)
                            run.font.bold = row_index == 0
                            run.font.color.rgb = RGBColor(255, 255, 255) if row_index == 0 else RGBColor(48, 54, 61)
        if compact and group[0]["title"] in ("Venta a crédito y estados", "Reintentos y operación única"):
            content.top = PInches(2.12)
        old_pictures = [shape for shape in slide.shapes if shape.shape_type == 13]
        for shape in old_pictures:
            shape._element.getparent().remove(shape._element)
        if image_only:
            content.text_frame.auto_size = MSO_AUTO_SIZE.NONE
            content.text_frame.word_wrap = True
            if "_gallery_title" in group[0] and all(
                image_ratio(block) < 0.65 for block in image_blocks
            ):
                # Portrait phone evidence stays tall enough to read without filling
                # nearly the full slide like a long infographic.
                picture_bounds = (PInches(0.82), PInches(2.42), PInches(8.85), PInches(4.0))
            else:
                picture_bounds = (PInches(0.82), PInches(2.12), PInches(8.85), PInches(4.55))
        else:
            picture_bounds = fit_slide_body(slide, content, group)
        if picture_bounds:
            images = image_blocks
            left, top, width, height = picture_bounds
            gap = PInches(0.16)
            portrait_gallery = (
                image_only
                and "_gallery_title" in group[0]
                and all(image_ratio(block) < 0.65 for block in images)
            )
            if portrait_gallery:
                image_widths = [int(min(width, height * image_ratio(block))) for block in images]
                total_width = sum(image_widths) + gap * (len(images) - 1)
                cursor = left + (width - total_width) // 2
                for block, image_width in zip(images, image_widths):
                    fit_picture(slide, block["path"], (cursor, top, image_width, height), block.get("crop"))
                    cursor += image_width + gap
            else:
                columns = min(2, len(images))
                column_width = int((width - gap * (columns - 1)) / columns)
                for image_index, block in enumerate(images):
                    fit_picture(slide, block["path"], (
                        left + image_index * (column_width + gap), top, column_width, height
                    ), block.get("crop"))
        if label.startswith("conclus"):
            active = "CONCLUSIONES"
        elif label.startswith("recomend"):
            active = "RECOMENDACIONES"
        elif label.startswith(("bibliograf", "referencias bibliograf")):
            active = "BIBLIOGRAFÍA"
        elif any(word in label for word in ("prueba", "evidencia", "comprobación", "catálogo cargado")):
            active = "PRUEBAS Y EVIDENCIAS"
        elif any(word in label for word in ("cliente", "consola", "web", "android", "wpf", "catálogo")):
            active = "CLIENTES"
        elif any(word in label for word in ("efectivo", "crédito", "elegibilidad", "monto", "amortización", "venta")):
            active = "VENTAS Y CRÉDITO"
        elif any(word in label for word in ("modelo", "base", "semilla", "migración", "diagrama físico")):
            active = "MODELO DE DATOS"
        elif any(word in label for word in ("contrato", "rest")):
            active = "CONTRATO REST"
        elif any(word in label for word in ("arquitectura", "entorno", "configuración", "preparación", "figura")):
            active = "ARQUITECTURA"
        else:
            active = "OBJETIVO Y ALCANCE"
        update_sidebar(slide, nav, group[0].get("_nav", active))
        set_slide_number(slide, slide_index + 1)
        for shape in slide.shapes:
            if shape.has_text_frame and "EUREKA" in shape.text.upper():
                replace_frame_text(shape, "")

    slide_ids = prs.slides._sldIdLst
    for slide_id in list(slide_ids)[len(groups) + 2:]:
        prs.part.drop_rel(slide_id.get(qn("r:id")))
        slide_ids.remove(slide_id)

    prs.core_properties.author = AUTHOR_LINE
    prs.core_properties.title = PROJECT["name"] + " — Manual técnico"
    prs.core_properties.subject = ("Presentación resumida basada en la fuente canónica" if compact
                                   else "Misma fuente canónica del manual DOCX")
    prs.core_properties.keywords = "GR09, NRC 36884, REST, .NET, celulares, BanQuito"
    prs.save(target)


def generate_legacy_word(template, source, target):
    """Compatibility path for ERS/ECUD; their source-specific adapters are separate work."""
    doc = Document(template)
    for child in list(doc._element.body):
        if child.tag.endswith("}sectPr"):
            continue
        doc._element.body.remove(child)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
    for line in source.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("# "):
            doc.add_heading(line[2:], 0)
        elif line.startswith("## "):
            doc.add_heading(line[3:], 1)
        elif line:
            doc.add_paragraph(line)
    doc.core_properties.author = AUTHOR_LINE
    doc.core_properties.title = PROJECT["name"]
    doc.save(target)


def main():
    artifacts = DOCS["artifacts"]
    if ARGS.compacto and ARGS.artifacts != ["presentacion"]:
        raise ValueError("--compacto requiere --artifacts presentacion para no modificar otros documentos.")
    if artifacts["manual"]["source"] != artifacts["presentacion"]["source"]:
        raise ValueError("Manual DOCX y PPTX deben compartir exactamente la misma fuente canónica.")
    canonical_path = ROOT / artifacts["manual"]["source"]
    title, sections = parse_source(canonical_path)
    content_hash = canonical_content_hash(sections)
    compact_groups, selection_path, selection = (compact_presentation_groups(sections, canonical_path)
                                                   if ARGS.compacto else (None, None, None))
    draft_dir = ARGS.draft_directory or pathlib.Path(DOCS["draft_directory"])
    draft_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for key, item in artifacts.items():
        if ARGS.artifacts and key not in ARGS.artifacts:
            continue
        template = ROOT / item["template"]
        source = ROOT / item["source"]
        target = draft_dir / pathlib.Path(item["output"]).name
        if not template.is_file() or not source.is_file():
            raise FileNotFoundError(f"{key}: falta fuente o plantilla")
        if key == "manual":
            generate_manual_word(template, source, target, sections)
        elif key == "presentacion":
            generate_presentation(template, source, target, sections, compact_groups, ARGS.compacto)
        elif key in ("ers", "ecud"):
            generate_legacy_word(template, source, target)
        else:
            raise ValueError(key)
        records.append({
            "id": key,
            "template": item["template"],
            "templateSha256": sha(template),
            "source": item["source"],
            "sourceSha256": sha(source),
            "canonicalManualSource": artifacts["manual"]["source"] if key in ("manual", "presentacion") else None,
            "canonicalContentSha256": content_hash if key in ("manual", "presentacion") and not (ARGS.compacto and key == "presentacion") else None,
            "canonicalSourceContentSha256": content_hash if ARGS.compacto and key == "presentacion" else None,
            "chapters": (len({slide["section"] for slide in selection["slides"]}) if ARGS.compacto and key == "presentacion"
                         else len(sections) if key in ("manual", "presentacion") else None),
            "draft": str(target),
            "draftSha256": sha(target),
            "output": item["output"],
        })
    manifest = {
        "revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "estado": "BORRADOR; conservar masters y revisar todos los renderizados",
        "canonicalManualSource": artifacts["manual"]["source"],
        "canonicalContentSha256": content_hash,
        "chapterCount": len(sections),
        "expectedPresentationSlides": len(compact_groups if ARGS.compacto else group_presentation_sections(sections)) + 2,
        "presentationMode": "resumida" if ARGS.compacto else "completa",
        "selection": selection if ARGS.compacto else None,
        "selectionSha256": sha(selection_path) if ARGS.compacto else None,
        "artifacts": records,
    }
    (draft_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(records)} borradores generados desde {len(sections)} capítulos canónicos en {draft_dir}")


if __name__ == "__main__":
    main()
