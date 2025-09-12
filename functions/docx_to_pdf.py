# from docx import Document
# from docx.shared import Pt, RGBColor
# from docx.enum.text import WD_ALIGN_PARAGRAPH

# from docx import Document
# from docx.shared import Pt, RGBColor, Inches
# from docx.enum.text import WD_ALIGN_PARAGRAPH

# def exportar_para_docx(textos, config, saida_docx, toc=None):
#   try:
#     doc = Document()

# Estilos baseados nas configurações
#      fonte = validar_fonte(config["fonte"])
#    tamanho_fonte = config["tamanho_fonte"]
#    alinhamento_map = {"esquerda": WD_ALIGN_PARAGRAPH.LEFT, "centro": WD_ALIGN_PARAGRAPH.CENTER, "justificado": WD_ALIGN_PARAGRAPH.JUSTIFY}
#    alinhamento = alinhamento_map.get(config["alinhamento"], WD_ALIGN_PARAGRAPH.JUSTIFY)
#    cor_titulo = temas[config["tema"]]["cor_titulo"]
#    cor_texto = temas[config["tema"]]["cor_texto"]

# Adicionar capa (se solicitada)
#  if incluir_capa == "s":
#        p = doc.add_heading(config["capa_titulo"], level=1)
#        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
#       p.runs[0].font.name = fonte
#        p.runs[0].font.size = Pt(24)
#        p.runs[0].font.color.rgb = RGBColor(cor_titulo.red, cor_titulo.green, cor_titulo.blue)

#          p = doc.add_paragraph(config["capa_autor"])
#        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
#         p.runs[0].font.name = fonte
#        p.runs[0].font.size = Pt(16)

#        p = doc.add_paragraph(config["capa_data"])
#         p.alignment = WD_ALIGN_PARAGRAPH.CENTER
#         p.runs[0].font.name = fonte
#         p.runs[0].font.size = Pt(12)

#         doc.add_page_break()

# Adicionar sumário (se solicitado)
#      if incluir_sumario == "s" and toc:
#         doc.add_heading("Sumário", #level=1)
#          for texto, nivel, page in toc:
#           p = doc.add_paragraph(f"{'  ' * nivel}{texto} ... {page}")
#            p.alignment = #WD_ALIGN_PARAGRAPH.LEFT
#  *          p.runs[0].font.name = fonte
#   *           p.runs[0].font.size = Pt(10)
#          doc.add_page_break()

# Processar conteúdo
#      for texto, latex_images in textos:  # Textos agora incluem latex_images
#       html = markdown.markdown(texto, extensions=['extra', 'fenced_code', 'tables', 'footnotes'])
#        parser = MarkdownParser(A4[1], latex_images)
#  parser.feed(html)
#          for item in parser.story:
#             if isinstance(item, Paragraph):
# *               style = item.style.name
#    *               p = doc#.add_paragraph(item.text)
#                  p.style.font.name = fonte
#                   p.style.font.size = Pt(tamanho_fonte if style == 'CustomBody' else tamanho_fonte + 4 if style == 'CustomHeading1' else tamanho_fonte + 2)
#                  p.alignment = alinhamento if style == 'CustomBody' else WD_ALIGN_PARAGRAPH.LEFT
#               p.runs[0].font.color.rgb = RGBColor(cor_texto.red, cor_texto.green, cor_texto.blue) if style == 'CustomBody' else RGBColor(cor_titulo.red, cor_titulo.green, cor_titulo.blue)
#            elif isinstance(item, ReportLabImage):
# Adicionar imagens LaTeX
#                img_stream = item._imgdata
#                img = Image.open(img_stream)
#               img_width, img_height = img.size
#                max_width = Inches(6)  # Limitar largura a 6 polegadas
#               scale = min(1, max_width / img_width)
#                doc.add_picture(img_stream, width=Inches(img_width * scale / 72))
#           elif isinstance(item, Table):
#                table = doc.add_table(rows=len(item.data), cols=len(item.data[0]))
#                for i, row in enumerate(item.data):
#                   for j, cell in enumerate(row):
#                     table.cell(i, j).text = str(cell)
#                       table.cell(i, j).paragraphs[0].style.font.name = fonte
#                       table.cell(i, j).paragraphs[0].style.font.size = Pt(tamanho_fonte)
#                table.style = 'Table Grid'

#    doc.save(saida_docx)
#       print(f"✅ DOCX salvo como: {saida_docx}")
#   except Exception as e:
#       print(f"❌ Erro ao exportar para DOCX: {str(e)}")
# === EXPORTAR/IMPORTAR CONFIGURAÇÕES ===
