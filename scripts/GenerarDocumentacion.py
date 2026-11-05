"""Genera borradores Office desde las plantillas GR09 y sus fuentes canónicas."""
import argparse
import copy
import hashlib
import json
import pathlib
import re
import subprocess
import zipfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches as PInches, Pt as PPt
from PIL import Image


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "documentation-profile.json"
PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8-sig"))
DOCS = PROFILE["documentation"]
PROJECT = PROFILE["project"]
AUTHOR_LINE = "; ".join(PROJECT["authors"])
DATE = "04/11/2026"

parser = argparse.ArgumentParser()
parser.add_argument("--artifacts", nargs="+", choices=["ers", "ecud", "manual", "presentacion"])
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
            blocks.append({"kind": "code", "text": "\n".join(code)})
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
    """Keep template paragraph styles and apply only inline-code treatment."""
    cursor = 0
    for match in re.finditer(r"`([^`]+)`", text):
        if match.start() > cursor:
            paragraph.add_run(text[cursor:match.start()])
        run = paragraph.add_run(match.group(1))
        run.font.name = "Consolas"
        run.font.size = Pt(9)
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
    instruction.text = ' TOC \\o "1-1" \\h \\z \\u '
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


def render_word_block(doc, block, section):
    kind = block["kind"]
    if kind == "paragraph":
        p = doc.add_paragraph()
        add_inline_markdown(p, block["text"])
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
        caption.add_run(". Servicios REST confirmados")
        table = doc.add_table(rows=0, cols=columns)
        table.style = "Table Grid" if "Table Grid" in [style.name for style in doc.styles] else doc.tables[0].style
        table.autofit = True
        for row_index, values in enumerate(rows):
            cells = table.add_row().cells
            for column, value in enumerate(values):
                cells[column].text = value
                for paragraph in cells[column].paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        if row_index == 0:
                            run.bold = True
            tr_pr = table.rows[-1]._tr.get_or_add_trPr()
            tr_pr.append(OxmlElement("w:cantSplit"))
        if rows:
            table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
        doc.add_paragraph()
    elif kind == "code":
        table = doc.add_table(rows=1, cols=1)
        table.style = "Table Grid" if "Table Grid" in [style.name for style in doc.styles] else doc.tables[0].style
        cell = table.cell(0, 0)
        cell.text = block["text"]
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.name = "Consolas"
                run.font.size = Pt(8)
        table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
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

    for index, section in enumerate(sections):
        if section["title"].casefold().startswith("prueba:"):
            add_test_result_label(doc, section["title"])
        else:
            heading = doc.add_heading(section["title"], level=1)
            if section["title"].casefold().startswith("diagrama:"):
                heading.paragraph_format.page_break_before = True
        image_blocks = [block for block in section["blocks"] if block["kind"] == "image"]
        emitted_images = False
        for block in section["blocks"]:
            if block["kind"] == "image":
                if emitted_images:
                    continue
                add_word_image_group(doc, image_blocks, section)
                emitted_images = True
            else:
                render_word_block(doc, block, section)
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


def fit_picture(slide, path, bounds):
    left, top, width, height = bounds
    with Image.open(path) as bitmap:
        scale = min(width / bitmap.width, height / bitmap.height)
        fitted_width = int(bitmap.width * scale)
        fitted_height = int(bitmap.height * scale)
    return slide.shapes.add_picture(
        str(path),
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
        ))


def slide_body(sections):
    result = []
    for section in sections:
        parts = [section["title"]]
        for block in section["blocks"]:
            if block["kind"] == "image":
                continue
            text = block_text(block)
            if text:
                parts.append(text)
        result.append("\n".join(parts))
    return "\n".join(result).replace("`", "").replace("**", "")


def group_presentation_sections(sections):
    groups = []
    pending = []
    expanded = []

    for source_index, section in enumerate(sections):
        images = [block for block in section["blocks"] if block["kind"] == "image"]
        text = [block for block in section["blocks"] if block["kind"] != "image"]
        if images and text:
            expanded.append({**section, "blocks": text, "_source_index": source_index})
            image_section = {**section, "blocks": images, "_source_index": source_index}
            if len(images) > 2:
                for start in range(0, len(images), 2):
                    end = min(start + 2, len(images))
                    expanded.append({
                        **image_section,
                        "blocks": images[start:end],
                        "_gallery_title": f"{section['title']} · tramos {start + 1}–{end} de {len(images)}",
                        "_gallery_start": start + 1,
                        "_gallery_end": end,
                        "_gallery_total": len(images),
                    })
            else:
                expanded.append(image_section)
        else:
            image_section = {**section, "_source_index": source_index}
            if images and len(images) > 2:
                for start in range(0, len(images), 2):
                    end = min(start + 2, len(images))
                    expanded.append({
                        **image_section,
                        "blocks": images[start:end],
                        "_gallery_title": f"{section['title']} · tramos {start + 1}–{end} de {len(images)}",
                        "_gallery_start": start + 1,
                        "_gallery_end": end,
                        "_gallery_total": len(images),
                    })
            else:
                expanded.append(image_section)

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
        lines = sum(max(1, (len(line) + 74) // 75) for line in candidate_text.splitlines())
        if pending and (lines > 10 or len(candidate) > 3):
            flush()
        pending.append(section)
    flush()
    grouped_sections = [section for group in groups for section in group]
    if sorted(id(block) for section in grouped_sections for block in section["blocks"]) != sorted(id(block) for section in sections for block in section["blocks"]):
        raise ValueError("La distribución PPTX omitió o duplicó contenido canónico.")
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
    top = max(content.top, PInches(1.92))
    bottom = PInches(6.88)
    if not images:
        content.left = left
        content.width = width
        content.top = top
        content.height = bottom - top
        content.text_frame.auto_size = MSO_AUTO_SIZE.NONE
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


def presentation_image_title(section):
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


def generate_presentation(template, source, target, sections):
    prs = Presentation(template)
    groups = group_presentation_sections(sections)
    if len(groups) + 2 > len(prs.slides):
        raise ValueError("La plantilla no tiene suficientes diapositivas para la distribución canónica.")
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
    if cover_pictures:
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
            chapter_title = group[0]["title"]
            if chapter_title.casefold().startswith("diagrama:"):
                slide_title = re.sub(r"^Diagrama:\s*", "", chapter_title, flags=re.IGNORECASE).upper()
            elif len(chapter_title) > 36:
                slide_title = "RESULTADO DE PRUEBAS"
            else:
                slide_title = chapter_title.upper()
            replace_frame_text(title, slide_title)
            replace_slide_images(slide, image_blocks)
            update_sidebar(slide, nav, "ARQUITECTURA")
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
        if len(group) == 1 and (group[0]["title"].casefold() in ("conclusiones", "recomendaciones") or group[0]["title"].casefold().startswith("bibliografía")):
            replace_frame_text(title, group[0]["title"].upper())
        elif image_only:
            slide_title = presentation_image_title(group[0]).upper()
            replace_frame_text(title, slide_title)
        else:
            replace_frame_text(title, "DESARROLLO")
        replace_frame_text(content, "" if image_only else slide_body(group))
        old_pictures = [shape for shape in slide.shapes if shape.shape_type == 13]
        for shape in old_pictures:
            shape._element.getparent().remove(shape._element)
        if image_only:
            content.text_frame.auto_size = MSO_AUTO_SIZE.NONE
            content.text_frame.word_wrap = True
            picture_bounds = (PInches(0.82), PInches(1.92), PInches(8.85), PInches(4.78))
        else:
            picture_bounds = fit_slide_body(slide, content, group)
        if picture_bounds:
            images = image_blocks
            left, top, width, height = picture_bounds
            gap = PInches(0.16)
            columns = min(2, len(images))
            column_width = int((width - gap * (columns - 1)) / columns)
            for image_index, block in enumerate(images):
                fit_picture(slide, block["path"], (
                    left + image_index * (column_width + gap), top, column_width, height
                ))
        if label.startswith("conclus"):
            active = "CONCLUSIONES"
        elif label.startswith("recomend"):
            active = "RECOMENDACIONES"
        elif label.startswith("bibliograf"):
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
        update_sidebar(slide, nav, active)
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
    prs.core_properties.subject = "Misma fuente canónica del manual DOCX"
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
    if artifacts["manual"]["source"] != artifacts["presentacion"]["source"]:
        raise ValueError("Manual DOCX y PPTX deben compartir exactamente la misma fuente canónica.")
    canonical_path = ROOT / artifacts["manual"]["source"]
    title, sections = parse_source(canonical_path)
    content_hash = canonical_content_hash(sections)
    draft_dir = pathlib.Path(DOCS["draft_directory"])
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
            generate_presentation(template, source, target, sections)
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
            "canonicalContentSha256": content_hash if key in ("manual", "presentacion") else None,
            "chapters": len(sections) if key in ("manual", "presentacion") else None,
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
        "expectedPresentationSlides": len(group_presentation_sections(sections)) + 2,
        "artifacts": records,
    }
    (draft_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(records)} borradores generados desde {len(sections)} capítulos canónicos en {draft_dir}")


if __name__ == "__main__":
    main()
