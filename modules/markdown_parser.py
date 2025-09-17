import os
from reportlab.platypus import (
    Paragraph,
    Image as ReportLabImage,
    Table,
    TableStyle,
    PageBreak,
)
from PIL import Image
from html.parser import HTMLParser

class MarkdownParser(HTMLParser):
    """
    An HTML parser that converts a stream of HTML into ReportLab flowables.
    It is driven by configuration and style dictionaries, with no global state access.
    """
    def __init__(self, doc_height, styles, config, latex_images=None):
        super().__init__()
        self.story = []
        self.headings = []
        self.styles = styles
        self.config = config
        self.latex_images = latex_images or {}

        # Internal state
        self.current_style_name = "Body"
        self.in_table = False
        self.table_raw_data = []
        self.current_raw_row = []
        self.list_level = 0

        # Page position tracking for rudimentary widow/orphan control
        self.y_position = doc_height
        self.doc_height = doc_height
        self.page_counter = 1

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.current_style_name = "Heading1"
        elif tag == "h2":
            self.current_style_name = "Heading2"
        elif tag == "p":
            self.current_style_name = "Body"
        elif tag == "li":
            self.current_style_name = "ListItem"
        elif tag == "img":
            attrs_dict = dict(attrs)
            src = attrs_dict.get("src")
            if src and os.path.exists(src):
                self._add_image(src)
        elif tag == "table":
            self.in_table = True
            self.table_raw_data = []
        elif tag == "tr":
            self.current_raw_row = []

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
            if self.table_raw_data:
                self._add_table()
        elif tag == "tr":
            self.table_raw_data.append(self.current_raw_row)

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        # Handle LaTeX placeholder images
        if data in self.latex_images:
            self._add_image(self.latex_images[data], is_buffer=True)
            return

        if self.in_table:
            self.current_raw_row.append(data)
        else:
            # Basic widow/orphan control for headings
            if "Heading" in self.current_style_name and self.config.get("verificar_titulos", True):
                # If a heading is near the bottom of the page, insert a page break before it.
                if self.y_position < self.config.get("margem_inf", 50) + self.config.get("tamanho_fonte", 12) * 3:
                    self._add_page_break()

            style = self.styles.get(self.current_style_name, self.styles["Body"])

            if self.current_style_name == "ListItem":
                # A real implementation would handle nested lists; this is simplified.
                prefix = "• "
                p = Paragraph(f"{prefix}{data}", style)
            else:
                p = Paragraph(data, style)

            self.story.append(p)
            self._update_y_position(p.wrap(self.doc_height, 0)[1])

            # Add to table of contents if it's a heading
            if self.config.get("incluir_sumario") and "Heading" in self.current_style_name:
                level = 0 if self.current_style_name == "Heading1" else 1
                p = Paragraph(data, style)
                p.bookmark = f"h{level}_{data}"
                p.level = level
                self.story.append(p)
            else:
                p = Paragraph(data, style)
                self.story.append(p)

    def _add_image(self, src, is_buffer=False):
        try:
            img_path_or_buffer = src
            if is_buffer:
                img_path_or_buffer.seek(0)

            img = Image.open(img_path_or_buffer)
            img_width, img_height = img.size

            max_width = self.config.get("doc_width") # Expect this to be pre-calculated in config
            scale = min(1.0, max_width / img_width)

            img_flowable = ReportLabImage(img_path_or_buffer, width=img_width * scale, height=img_height * scale)
            self.story.append(img_flowable)
            self._update_y_position(img_flowable.height)

        except Exception:
            # Fail silently, a real app should log this.
            pass

    def _add_table(self):
        # This logic is complex and has been simplified. A full implementation
        # would need robust column width calculation.
        style_config = self.config.get("tabela_estilos", {}).get(self.config.get("tabela_estilo", "simples"), [])

        table_data = [[Paragraph(cell, self.styles["Body"]) for cell in row] for row in self.table_raw_data]

        table = Table(table_data)
        table.setStyle(TableStyle(style_config))

        self.story.append(table)
        self._update_y_position(table.wrap(0, 0)[1])

    def _update_y_position(self, height):
        self.y_position -= height
        if self.y_position < self.config.get("margem_inf", 50):
            self._add_page_break()

    def _add_page_break(self):
        self.story.append(PageBreak())
        self.y_position = self.doc_height
        self.page_counter += 1
