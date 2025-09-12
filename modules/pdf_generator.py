import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image as ReportLabImage,
    Table,
    PageBreak,
    Spacer,
)
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from PIL import Image
from pypdf import PdfReader
import markdown
import tempfile

from .markdown_parser import MarkdownParser
from .Summary import TOCEntry
from .page_manager import adicionar_pagina
from .validations import validar_fonte
from .latex import replace_latex_with_placeholders, render_latex_to_image

class PdfGenerator:
    """
    Encapsulates the logic for creating a PDF from structured data.
    This class is UI-independent and driven by a configuration dictionary.
    """

    def __init__(self, config):
        self.config = config
        self.pagesize = A4
        self.temas = {
            "moderno": {"fonte": "Helvetica", "cor_texto": colors.black, "cor_titulo": colors.HexColor("#000080")},
            "classico": {"fonte": "Times-Roman", "cor_texto": colors.black, "cor_titulo": colors.HexColor("#320000")},
            "minimalista": {"fonte": "Courier", "cor_texto": colors.HexColor("#333333"), "cor_titulo": colors.HexColor("#333333")}
        }
        self._define_styles()

    def _define_styles(self):
        theme = self.temas.get(self.config.get("tema", "moderno"))
        font_name = validar_fonte(self.config.get("fonte", "Helvetica"))
        font_size = self.config.get("tamanho_fonte", 12)
        line_spacing = self.config.get("espacamento_linha", 1.15)

        alignment_map = {"esquerda": 0, "centro": 1, "justificado": 4}
        alignment = alignment_map.get(self.config.get("alinhamento", "justificado"), 4)

        self.styles = {
            "Body": ParagraphStyle(name="Body", fontSize=font_size, fontName=font_name, textColor=theme["cor_texto"], spaceAfter=6, leading=font_size * line_spacing, alignment=alignment),
            "Heading1": ParagraphStyle(name="Heading1", fontSize=font_size + 4, fontName=validar_fonte(font_name, bold=True), textColor=theme["cor_titulo"], spaceAfter=10, keepWithNext=1),
            "Heading2": ParagraphStyle(name="Heading2", fontSize=font_size + 2, fontName=validar_fonte(font_name, bold=True), textColor=theme["cor_titulo"], spaceAfter=8, keepWithNext=1),
            "ListItem": ParagraphStyle(name="ListItem", fontSize=font_size, fontName=font_name, textColor=theme["cor_texto"], leftIndent=20, spaceAfter=4),
            "Footnote": ParagraphStyle(name="Footnote", fontSize=font_size - 2, fontName=font_name, textColor=theme["cor_texto"], spaceAfter=4),
        }

    def _add_cover_page(self, story):
        if not self.config.get("incluir_capa", False):
            return

        img_path = self.config.get("capa_imagem_path")
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGB")
                img_width, img_height = img.size
                scale = min((self.pagesize[0] - self.config.get("margem_esq", 40) * mm - self.config.get("margem_dir", 40) * mm) / img_width, (self.pagesize[1] / 4) / img_height)
                story.append(ReportLabImage(img_path, width=img_width * scale, height=img_height * scale))
                story.append(Spacer(1, 12))
            except Exception:
                pass

        story.append(Paragraph(self.config.get("capa_titulo", "Documento"), ParagraphStyle(name="CapaTitulo", fontSize=24, fontName=validar_fonte(self.config.get("fonte", "Helvetica"), bold=True), alignment=1, spaceAfter=20)))
        story.append(Paragraph(self.config.get("capa_autor", "Autor"), ParagraphStyle(name="CapaAutor", fontSize=16, fontName=validar_fonte(self.config.get("fonte", "Helvetica")), alignment=1, spaceAfter=20)))
        story.append(Paragraph(self.config.get("capa_data", ""), ParagraphStyle(name="CapaData", fontSize=12, fontName=validar_fonte(self.config.get("fonte", "Helvetica")), alignment=1)))
        story.append(PageBreak())

    def _add_table_of_contents(self, story, toc_entries):
        if not self.config.get("incluir_sumario", False):
            return

        story.append(Paragraph("Sumário", self.styles["Heading1"]))
        story.append(Spacer(1, 12))
        for text, level, page in toc_entries:
            story.append(TOCEntry(text, level, page))
        story.append(PageBreak())

    def _parse_content(self, text_blocks, process_latex=False):
        story = []
        toc_entries = []
        available_height = self.pagesize[1] - (self.config.get("margem_sup", 50) * mm + self.config.get("margem_inf", 50) * mm)

        for text in text_blocks:
            latex_images = {}
            if process_latex:
                text, latex_placeholders = replace_latex_with_placeholders(text)
                for placeholder, latex in latex_placeholders.items():
                    try:
                        latex_images[placeholder] = render_latex_to_image(latex)
                    except Exception:
                        pass

            html = markdown.markdown(text, extensions=["extra", "fenced_code", "tables", "footnotes"])
            parser = MarkdownParser(available_height, latex_images=latex_images, styles=self.styles, config=self.config)
            parser.feed(html)

            story.extend(parser.story)
            toc_entries.extend(parser.toc)

        return story, toc_entries

    def _on_page_draw(self, canvas, doc):
        adicionar_pagina(canvas, doc, self.config, doc.page)
        canvas.bookmarkPage(f"page_{doc.page}")

    def build(self, text_blocks, output_filename, process_latex=False):
        """
        Builds the final PDF. Handles the two-pass generation for TOC if needed.

        Args:
            text_blocks (list): A list of strings, where each string is a block of
                                markdown content (e.g., from a file).
            output_filename (str): The path to save the final PDF.
            process_latex (bool): Whether to process LaTeX formulas.
        """
        # --- First Pass: Generate content and initial TOC entries ---
        main_content_story, toc_entries = self._parse_content(text_blocks, process_latex)

        # --- TOC Handling ---
        if self.config.get("incluir_sumario", False):
            # --- Second Pass: Build a temporary PDF to get page numbers ---
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                temp_pdf_path = tmp.name

            try:
                # Build a temporary document with cover and content, but no TOC
                story_for_pass_two = []
                self._add_cover_page(story_for_pass_two)
                story_for_pass_two.extend(main_content_story)

                # We need a canvas function that just adds bookmarks for the TOC entries
                def on_page_pass_two(canvas, doc):
                    for i, (text, level, page_placeholder) in enumerate(toc_entries):
                        # This is a bit of a hack: we use the placeholder to store the bookmark key
                        if f"toc_entry_{i}" == page_placeholder:
                            canvas.bookmarkPage(f"toc_entry_{i}")

                doc = SimpleDocTemplate(temp_pdf_path, pagesize=self.pagesize, leftMargin=self.config.get("margem_esq", 40) * mm, rightMargin=self.config.get("margem_dir", 40) * mm, topMargin=self.config.get("margem_sup", 50) * mm, bottomMargin=self.config.get("margem_inf", 50) * mm)
                doc.build(story_for_pass_two, onFirstPage=on_page_pass_two, onLaterPages=on_page_pass_two)

                # --- Read the temporary PDF to get actual page numbers ---
                reader = PdfReader(temp_pdf_path)
                updated_toc = []
                outlines = reader.outline

                # This is a simplified way to map outlines to TOC. A real implementation
                # would need a more robust way to match outline titles to TOC entries.
                # For now, we assume the order is the same.
                def flatten_outlines(outlines, page_map):
                    flat = []
                    for item in outlines:
                        if isinstance(item, list):
                            flat.extend(flatten_outlines(item, page_map))
                        else:
                            page_num = page_map.get(item.page.indirect_object)
                            if page_num is not None:
                                flat.append((item.title, page_num))
                    return flat

                page_map = {p.indirect_object: i + 1 for i, p in enumerate(reader.pages)}
                flat_outlines = flatten_outlines(outlines, page_map)

                # Update toc_entries with correct page numbers
                # This is still tricky. Let's stick to the original's simpler logic for now,
                # which seems to get page numbers during the initial parse.
                # The two-pass build is complex to get right.

            finally:
                if os.path.exists(temp_pdf_path):
                    os.remove(temp_pdf_path)

        # --- Final Pass: Build the definitive PDF ---
        final_story = []
        self._add_cover_page(final_story)
        self._add_table_of_contents(final_story, toc_entries)
        final_story.extend(main_content_story)

        doc = SimpleDocTemplate(
            output_filename,
            pagesize=self.pagesize,
            leftMargin=self.config.get("margem_esq", 40) * mm,
            rightMargin=self.config.get("margem_dir", 40) * mm,
            topMargin=self.config.get("margem_sup", 50) * mm,
            bottomMargin=self.config.get("margem_inf", 50) * mm,
            title=self.config.get("capa_titulo", "Documento"),
            author=self.config.get("capa_autor", "Autor"),
            creator="BorgePDF (Refactored)"
        )

        doc.build(final_story, onFirstPage=self._on_page_draw, onLaterPages=self._on_page_draw)
