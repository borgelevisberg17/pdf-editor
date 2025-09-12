import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image as ReportLabImage,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.platypus.flowables import Flowable
from PIL import Image
from sympy import preview
from io import BytesIO
from html.parser import HTMLParser
from weasyprint import HTML
from constants.globals import (
    story,
    config,
    custom_styles,
    tabela_estilos,
    incluir_sumario,
    toc,
    temas,
    modelos_pagina,
)


# Classe MarkdownParser
class MarkdownParser(HTMLParser):
    def __init__(self, doc_height, latex_images=None):
        super().__init__()
        self.story = []
        self.current_style = "CustomBody"
        self.table_data = []
        self.table_raw_data = []
        self.in_table = False
        self.current_row = []
        self.current_raw_row = []
        self.in_list = False
        self.list_type = None
        self.list_level = 0
        self.footnotes = {}
        self.current_footnote = None
        self.page_counter = 1
        self.y_position = doc_height
        self.doc_height = doc_height
        self.latex_images = (
            latex_images or {}
        )  # Dicionário de placeholders para imagens LaTeX

    def handle_starttag(self, tag, attrs):
        global config, custom_styles, incluir_sumario, toc
        if tag == "h1":
            self.current_style = "CustomHeading1"
        elif tag == "h2":
            self.current_style = "CustomHeading2"
        elif tag == "p":
            self.current_style = "CustomBody"
        elif tag == "img":
            for attr in attrs:
                if attr[0] == "src":
                    try:
                        if os.path.exists(attr[1]):
                            img = Image.open(attr[1]).convert("RGB")
                            img_width, img_height = img.size
                            max_width = (
                                A4[0] - config["margem_esq"] - config["margem_dir"]
                            )
                            max_height = A4[1] / 2
                            scale = min(max_width / img_width, max_height / img_height)
                            img_flowable = ReportLabImage(
                                attr[1],
                                width=img_width * scale,
                                height=img_height * scale,
                            )
                            self.y_position -= img_height * scale
                            self.story.append(img_flowable)
                            if self.y_position < config["margem_inf"]:
                                self.story.append(PageBreak())
                                self.y_position = self.doc_height
                                self.page_counter += 1
                        else:
                            print(f"⚠️ Imagem '{attr[1]}' não encontrada. Ignorando.")
                    except Exception as e:
                        print(f"❌ Erro ao adicionar imagem {attr[1]}: {str(e)}.")
        elif tag == "table":
            self.in_table = True
            self.table_data = []
            self.table_raw_data = []
        elif tag == "tr":
            self.current_row = []
            self.current_raw_row = []
        elif tag == "td" or tag == "th":
            self.current_style = "CustomBody"
        elif tag in ("ul", "ol"):
            self.in_list = True
            self.list_type = tag
            self.list_level += 1
        elif tag == "li":
            self.current_style = "CustomListItem"
        elif tag == "sup" and any(
            attr[0] == "id" and attr[1].startswith("fn") for attr in attrs
        ):
            self.current_footnote = attrs[0][1]

    def handle_endtag(self, tag):
        global config, custom_styles, tabela_estilos
        if tag == "table":
            self.in_table = False
            if self.table_raw_data:
                col_widths = [
                    max(len(str(cell)) for cell in row) * config["tamanho_fonte"] * 0.5
                    for row in zip(*self.table_raw_data)
                ]
                table_data = [
                    [Paragraph(cell or "", custom_styles["CustomBody"]) for cell in row]
                    for row in self.table_raw_data
                ]
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle(tabela_estilos[config["tabela_estilo"]]))
                table_width = sum(col_widths)
                if table_width > (A4[0] - config["margem_esq"] - config["margem_dir"]):
                    scale = (
                        A4[0] - config["margem_esq"] - config["margem_dir"]
                    ) / table_width
                    table._colWidths = [w * scale for w in col_widths]
                self.story.append(table)
                self.y_position -= (
                    len(self.table_raw_data) * config["tamanho_fonte"] * 1.5
                )
                if self.y_position < config["margem_inf"]:
                    self.story.append(PageBreak())
                    self.y_position = self.doc_height
                    self.page_counter += 1
        elif tag == "tr":
            self.table_data.append(self.current_row)
            self.table_raw_data.append(self.current_raw_row)
        elif tag in ("ul", "ol"):
            self.list_level -= 1
            if self.list_level == 0:
                self.in_list = False
                self.list_type = None
        elif tag == "p" and self.current_footnote:
            self.story.append(
                Paragraph(
                    self.footnotes.get(self.current_footnote, ""),
                    custom_styles["CustomFootnote"],
                )
            )
            self.y_position -= config["tamanho_fonte"]
            if self.y_position < config["margem_inf"]:
                self.story.append(PageBreak())
                self.y_position = self.doc_height
                self.page_counter += 1
            self.current_footnote = None

    def handle_data(self, data):
        global config, custom_styles, incluir_sumario, toc
        if data.strip():
            if self.in_table:
                self.current_raw_row.append(data.strip())
            elif self.in_list:
                prefix = f"{len(self.story) + 1}. " if self.list_type == "ol" else "• "
                self.story.append(
                    Paragraph(
                        f"{prefix}{data.strip()}", custom_styles["CustomListItem"]
                    )
                )
                self.y_position -= config["tamanho_fonte"] * config["espacamento_linha"]
                if self.y_position < config["margem_inf"]:
                    self.story.append(PageBreak())
                    self.y_position = self.doc_height
                    self.page_counter += 1
            elif self.current_footnote:
                self.footnotes[self.current_footnote] = data.strip()
            else:
                # Verificar se o dado é um placeholder de LaTeX
                if data.strip() in self.latex_images:
                    try:
                        buf = self.latex_images[data.strip()]
                        if buf:  # Verificar se o buffer não é None
                            img = Image.open(buf)
                            img_width, img_height = img.size
                            max_width = (
                                A4[0] - config["margem_esq"] - config["margem_dir"]
                            )
                            scale = min(1, max_width / img_width)
                            img_flowable = ReportLabImage(
                                buf, width=img_width * scale, height=img_height * scale
                            )
                            self.story.append(img_flowable)
                            self.y_position -= img_height * scale
                            if self.y_position < config["margem_inf"]:
                                self.story.append(PageBreak())
                                self.y_position = self.doc_height
                                self.page_counter += 1
                    except Exception as e:
                        print(f"❌ Erro ao adicionar imagem LaTeX: {str(e)}")
                else:
                    if (
                        self.current_style in ("CustomHeading1", "CustomHeading2")
                        and config["verificar_titulos"]
                    ):
                        if (
                            self.y_position
                            < config["margem_inf"] + config["tamanho_fonte"] * 2
                        ):
                            self.story.append(PageBreak())
                            self.y_position = self.doc_height
                            self.page_counter += 1
                    self.story.append(
                        Paragraph(data.strip(), custom_styles[self.current_style])
                    )
                    self.y_position -= (
                        config["tamanho_fonte"] * config["espacamento_linha"]
                    )
                    if (
                        self.current_style in ("CustomHeading1", "CustomHeading2")
                        and incluir_sumario == "s"
                    ):
                        print(
                            f"📑 Adicionando ao sumário: {data.strip()} (nível {1 if self.current_style == 'CustomHeading1' else 2}, página {self.page_counter})"
                        )
                        toc.append(
                            (
                                data.strip(),
                                1 if self.current_style == "CustomHeading1" else 2,
                                self.page_counter,
                            )
                        )
                    if self.y_position < config["margem_inf"]:
                        self.story.append(PageBreak())
                        self.y_position = self.doc_height
                        self.page_counter += 1
