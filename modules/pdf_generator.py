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
from reportlab.platypus.tableofcontents import TableOfContents
from .page_manager import adicionar_pagina
from .validations import validar_fonte
from .latex import replace_latex_with_placeholders, render_latex_to_image

class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        self.toc = TableOfContents()

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if hasattr(flowable, 'bookmark') and flowable.bookmark:
            self.notify('TOCEntry', (flowable.level, flowable.getPlainText(), self.page, flowable.bookmark))

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

    def _parse_content(self, text_blocks, process_latex=False):
        story = []
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

        return story

    def _on_page_draw(self, canvas, doc):
        adicionar_pagina(canvas, doc, self.config, doc.page)
        canvas.bookmarkPage(f"page_{doc.page}")

    def build(self, text_blocks, output_filename, process_latex=False):
        """
        Builds the final PDF. Handles the two-pass generation for TOC if needed.
        """
        doc = MyDocTemplate(
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

        story = []
        self._add_cover_page(story)

        if self.config.get("incluir_sumario", False):
            story.append(Paragraph("Sumário", self.styles["Heading1"]))
            story.append(doc.toc)
            story.append(PageBreak())

        main_content_story = self._parse_content(text_blocks, process_latex)
        story.extend(main_content_story)

        doc.multiBuild(story, onFirstPage=self._on_page_draw, onLaterPages=self._on_page_draw)
