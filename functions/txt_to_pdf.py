import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image as ReportLabImage,
    Table,
    PageBreak,
    Spacer,
)
from reportlab.lib.units import mm
from reportlab.lib import colors
from modules.Summary import TOCEntry
from modules.markdown_parser import MarkdownParser
from PIL import Image
from pypdf import PdfReader, PdfWriter
import markdown

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

from configs.page_configs import carregar_config, salvar_config

from modules.latex import replace_latex_with_placeholders, render_latex_to_image

from modules.validations import (
    validar_cor,
    validar_fonte,
    registrar_fontes,
    validar_tabela_markdown,
)

from modules.shares import enviar_telegram

from modules.page_manager import adicionar_pagina, reordenar_arquivos

from modules.content_manager import editar_texto, formatar_palavras, visualizar_previa

from functions.html_to_pdf import exportar_para_html

from weasyprint import HTML


# Conversão de TXT para PDF
def txt_para_pdf(multiplos=False, process_latex=False):
    global config, custom_styles, tabela_estilos, toc
    try:
        # Inicializar variáveis
        story = []
        toc = []

        registrar_fontes()
        config = carregar_config()
        caminhos = []
        if multiplos:
            pasta = input("📂 Caminho da pasta com arquivos .txt: ")
            if not os.path.isdir(pasta):
                print(f"❌ Pasta '{pasta}' não encontrada. Tente novamente.")
                return
            caminhos = [
                os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith(".txt")
            ]
            if not caminhos:
                print("❌ Nenhum arquivo .txt encontrado na pasta. Tente outra pasta.")
                return
            caminhos = reordenar_arquivos(caminhos)
        else:
            caminho = input("📝 Caminho do arquivo .txt: ")
            if not os.path.exists(caminho) or not caminho.endswith(".txt"):
                print(
                    f"❌ Arquivo '{caminho}' inválido ou não encontrado. Use um arquivo .txt."
                )
                return
            caminhos = [caminho]

        saida = input("📄 Nome do PDF de saída (ex.: output.pdf): ")
        if not saida.endswith(".pdf"):
            saida += ".pdf"
        if not os.access(os.path.dirname(saida) or ".", os.W_OK):
            print(f"❌ Sem permissão para escrever em '{saida}'. Escolha outro local.")
            return
        # Verificar conteúdo do TXT
        has_tables = False
        has_images = False
        textos = []
        for caminho in caminhos:
            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read()
                if "|" in texto and not validar_tabela_markdown(texto):
                    print(
                        f"❌ Tabela inválida em {caminho}. Corrija e tente novamente."
                    )
                    return
                if "|" in texto:
                    has_tables = True
                if "![" in texto:
                    has_images = True
                latex_images = {}
                if process_latex:
                    texto, latex_placeholders = replace_latex_with_placeholders(texto)
                    for placeholder, latex in latex_placeholders.items():
                        try:
                            latex_images[placeholder] = render_latex_to_image(latex)
                        except Exception as e:
                            print(f"⚠️ Erro ao renderizar LaTeX '{latex}': {str(e)}")
                texto = formatar_palavras(texto)
                if (
                    input(
                        "🔎 Deseja visualizar o conteúdo antes da conversão? (s/n): "
                    ).lower()
                    == "s"
                ):
                    if not visualizar_previa(
                        texto,
                        caminhos=[caminho],
                        incluir_capa=incluir_capa,
                        incluir_sumario=incluir_sumario,
                        config=config,
                        toc=toc,
                    ):
                        return
                if (
                    input(
                        "📝 Deseja editar o texto antes da conversão? (s/n): "
                    ).lower()
                    == "s"
                ):
                    texto = editar_texto(caminho)
                    if texto is None:
                        return
                textos.append((texto, latex_images))

        # Configuração de capa e sumário
        incluir_capa = (
            input("📖 Incluir página de capa? (s/n, padrão s): ").lower() or "s"
        )
        incluir_sumario = (
            input("📑 Incluir sumário clicável? (s/n, padrão s): ").lower() or "s"
        )

        # Configurações personalizáveis
        usar_config = (
            input("⚙️ Usar configurações salvas? (s/n, padrão s): ").lower() or "s"
        )
        if usar_config != "s":
            config["margem_esq"] = float(
                input(f"📏 Margem esquerda (mm, padrão {config['margem_esq']}): ")
                or config["margem_esq"]
            )
            config["margem_dir"] = float(
                input(f"📏 Margem direita (mm, padrão {config['margem_dir']}): ")
                or config["margem_dir"]
            )
            config["margem_sup"] = float(
                input(f"📏 Margem superior (mm, padrão {config['margem_sup']}): ")
                or config["margem_sup"]
            )
            config["margem_inf"] = float(
                input(f"📏 Margem inferior (mm, padrão {config['margem_inf']}): ")
                or config["margem_inf"]
            )
            config["fonte"] = (
                input(
                    f"🖋️ Fonte (Helvetica/Times-Roman/Courier, padrão {config['fonte']}): "
                )
                or config["fonte"]
            )
            config["fonte"] = validar_fonte(config["fonte"])
            config["tamanho_fonte"] = float(
                input(f"📏 Tamanho da fonte (padrão {config['tamanho_fonte']}): ")
                or config["tamanho_fonte"]
            )
            config["alinhamento"] = (
                input(
                    f"📍 Alinhamento (esquerda/centro/justificado, padrão {config['alinhamento']}): "
                ).lower()
                or config["alinhamento"]
            )
            config["espacamento_linha"] = float(
                input(
                    f"📏 Espaçamento entre linhas (padrão {config['espacamento_linha']}): "
                )
                or config["espacamento_linha"]
            )
            config["tema"] = (
                input("🎨 Tema (moderno/classico/minimalista, padrão moderno): ")
                or "moderno"
            )
            config["modelo_pagina"] = (
                input(
                    "📄 Modelo de página (padrao/colorido/profissional, padrão padrao): "
                )
                or "padrao"
            )
            config["imagem_fundo"] = (
                input("🖼️ Caminho da imagem de fundo (opcional, Enter para nenhum): ")
                or ""
            )
            if config["modelo_pagina"] not in modelos_pagina:
                print(f"❌ Modelo de página inválido. Usando 'padrao'.")
                config["modelo_pagina"] = "padrao"
            if config["modelo_pagina"] == "colorido":
                config["cor_fundo_pagina"] = (
                    input("🎨 Cor de fundo da página (ex.: #E6F3FA): ") or "#E6F3FA"
                )
                modelos_pagina["colorido"]["cor_fundo"] = validar_cor(
                    config["cor_fundo_pagina"]
                )
            config["verificar_titulos"] = (
                input(
                    "📑 Verificar títulos no final da página? (s/n, padrão s): "
                ).lower()
                == "s"
            )
            if has_tables:
                config["tabela_estilo"] = (
                    input(
                        "📊 Estilo da tabela (simples/grade/listrado/personalizado, padrão simples): "
                    )
                    or "simples"
                )
                if config["tabela_estilo"] == "personalizado":
                    config["tabela_cor_fundo"] = (
                        input(
                            "🎨 Cor de fundo da tabela (ex.: white, lightgrey, #FF0000): "
                        )
                        or "white"
                    )
                    config["tabela_cor_borda"] = (
                        input("🎨 Cor da borda da tabela (ex.: black, #000000): ")
                        or "black"
                    )
            config["capa_titulo"] = (
                input(f"📖 Título da capa (padrão {config['capa_titulo']}): ")
                or config["capa_titulo"]
            )
            config["capa_autor"] = (
                input(f"✍️ Autor da capa (padrão {config['capa_autor']}): ")
                or config["capa_autor"]
            )
            config["capa_data"] = (
                input(f"📅 Data da capa (padrão {config['capa_data']}): ")
                or config["capa_data"]
            )
            salvar_config(config)

        # Configuração de paginação
        paginacao = {"tipo": "todas", "inicio": 1}
        paginacao_op = (
            input(
                "📄 Paginação (todas/impares/pares/a_partir_de/nenhuma, padrão todas): "
            )
            or "todas"
        )
        paginacao["tipo"] = paginacao_op
        if paginacao_op == "a_partir_de":
            paginacao["inicio"] = int(
                input("📄 A partir de qual página? (ex.: 1): ") or 1
            )

        # Mapear alinhamento
        alinhamento_map = {"esquerda": 0, "centro": 1, "justificado": 4}
        alinhamento = alinhamento_map.get(config["alinhamento"], 4)

        # Estilos de tabela
        tabela_estilos = {
            "simples": [
                ("GRID", (0, 0), (-1, -1), 1, validar_cor(config["tabela_cor_borda"])),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("FONTNAME", (0, 0), (-1, -1), validar_fonte(config["fonte"])),
                ("FONTSIZE", (0, 0), (-1, -1), config["tamanho_fonte"]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ],
            "grade": [
                ("GRID", (0, 0), (-1, -1), 1, validar_cor(config["tabela_cor_borda"])),
                ("FONTNAME", (0, 0), (-1, -1), validar_fonte(config["fonte"])),
                ("FONTSIZE", (0, 0), (-1, -1), config["tamanho_fonte"]),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
            "listrado": [
                ("GRID", (0, 0), (-1, -1), 1, validar_cor(config["tabela_cor_borda"])),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F0F0")),
                ("FONTNAME", (0, 0), (-1, -1), validar_fonte(config["fonte"])),
                ("FONTSIZE", (0, 0), (-1, -1), config["tamanho_fonte"]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ],
            "personalizado": [
                ("GRID", (0, 0), (-1, -1), 1, validar_cor(config["tabela_cor_borda"])),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    validar_cor(config["tabela_cor_fundo"]),
                ),
                ("FONTNAME", (0, 0), (-1, -1), validar_fonte(config["fonte"])),
                ("FONTSIZE", (0, 0), (-1, -1), config["tamanho_fonte"]),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ],
        }

        # Estilos personalizados
        custom_styles = {
            "CustomBody": ParagraphStyle(
                name="CustomBody",
                fontSize=config["tamanho_fonte"],
                fontName=validar_fonte(config["fonte"]),
                textColor=temas[config["tema"]]["cor_texto"],
                spaceAfter=6,
                leading=config["tamanho_fonte"] * config["espacamento_linha"],
                alignment=alinhamento,
            ),
            "CustomHeading1": ParagraphStyle(
                name="CustomHeading1",
                fontSize=config["tamanho_fonte"] + 4,
                fontName=validar_fonte(config["fonte"], bold=True),
                textColor=temas[config["tema"]]["cor_titulo"],
                spaceAfter=10,
            ),
            "CustomHeading2": ParagraphStyle(
                name="CustomHeading2",
                fontSize=config["tamanho_fonte"] + 2,
                fontName=validar_fonte(config["fonte"], bold=True),
                textColor=temas[config["tema"]]["cor_titulo"],
                spaceAfter=8,
            ),
            "CustomListItem": ParagraphStyle(
                name="CustomListItem",
                fontSize=config["tamanho_fonte"],
                fontName=validar_fonte(config["fonte"]),
                textColor=temas[config["tema"]]["cor_texto"],
                leftIndent=20,
                spaceAfter=4,
            ),
            "CustomFootnote": ParagraphStyle(
                name="CustomFootnote",
                fontSize=config["tamanho_fonte"] - 2,
                fontName=validar_fonte(config["fonte"]),
                textColor=temas[config["tema"]]["cor_texto"],
                spaceAfter=4,
            ),
        }

        # Processar cada arquivo TXT
        textos = []
        for caminho in caminhos:
            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read()
            # Processar LaTeX se solicitado
            latex_images = {}
            if process_latex:
                texto, latex_placeholders = replace_latex_with_placeholders(texto)
                for placeholder, latex in latex_placeholders.items():
                    try:
                        latex_images[placeholder] = render_latex_to_image(latex)
                    except Exception as e:
                        print(f"⚠️ Erro ao renderizar LaTeX '{latex}': {str(e)}")
            texto = formatar_palavras(texto)
            if (
                input(
                    "🔎 Deseja visualizar o conteúdo antes da conversão? (s/n): "
                ).lower()
                == "s"
            ):
                if not visualizar_previa(
                    texto,
                    caminhos=[caminho],
                    incluir_capa=incluir_capa,
                    incluir_sumario=incluir_sumario,
                    config=config,
                    toc=toc,
                ):
                    return
            if (
                input("📝 Deseja editar o texto antes da conversão? (s/n): ").lower()
                == "s"
            ):
                texto = editar_texto(caminho)
                if texto is None:
                    return
            textos.append((texto, latex_images))

        # Pré-visualização de tabelas
        if (
            has_tables
            and input("📊 Visualizar tabelas antes da conversão? (s/n): ").lower()
            == "s"
        ):
            for texto, _ in textos:
                html = markdown.markdown(texto, extensions=["tables"])
                parser = MarkdownParser(A4[1])
                parser.feed(html)
                for row in parser.table_raw_data:
                    print("| " + " | ".join(str(cell) for cell in row) + " |")

        # Exportar para HTML
        if input("📂 Exportar para HTML? (s/n): ").lower() == "s":
            exportar_para_html(
                [texto for texto, _ in textos],
                config,
                saida_html,
                incluir_sumario == "s",
                [(os.path.basename(caminho), 1) for caminho in caminhos],
            )

        # Exportar para DOCX
        # if saida_docx:
        #  exportar_para_docx(textos, config, saida_docx, toc)

        # Primeira passagem: Criar PDF temporário para contar páginas
        temp_pdf = "temp_output.pdf"
        if not os.access(os.path.dirname(temp_pdf) or ".", os.W_OK):
            print(
                f"❌ Sem permissão para escrever em '{temp_pdf}'. Escolha outro local."
            )
            return
        doc = SimpleDocTemplate(
            temp_pdf,
            pagesize=A4,
            leftMargin=config["margem_esq"],
            rightMargin=config["margem_dir"],
            topMargin=config["margem_sup"],
            bottomMargin=config["margem_inf"],
            title=config["capa_titulo"],
            author=config["capa_autor"],
            creator="BorgePDF",
        )
        story = []

        # Adicionar capa somente se solicitado
        if incluir_capa == "s":
            if input("🖼️ Adicionar imagem à capa? (s/n): ").lower() == "s":
                img_path = input("📂 Caminho da imagem: ")
                if os.path.exists(img_path):
                    img = Image.open(img_path).convert("RGB")
                    img_width, img_height = img.size
                    scale = min(doc.width / img_width, doc.height / 4 / img_height)
                    story.append(
                        ReportLabImage(
                            img_path, width=img_width * scale, height=img_height * scale
                        )
                    )
                    story.append(Spacer(1, 12))
                else:
                    print(
                        f"⚠️ Imagem '{img_path}' não encontrada. Prosseguindo sem imagem."
                    )
            story.append(
                Paragraph(
                    config["capa_titulo"],
                    ParagraphStyle(
                        name="CapaTitulo",
                        fontSize=24,
                        fontName=validar_fonte(config["fonte"], bold=True),
                        alignment=1,
                        spaceAfter=20,
                    ),
                )
            )
            story.append(
                Paragraph(
                    config["capa_autor"],
                    ParagraphStyle(
                        name="CapaAutor",
                        fontSize=16,
                        fontName=validar_fonte(config["fonte"]),
                        alignment=1,
                        spaceAfter=20,
                    ),
                )
            )
            story.append(
                Paragraph(
                    config["capa_data"],
                    ParagraphStyle(
                        name="CapaData",
                        fontSize=12,
                        fontName=validar_fonte(config["fonte"]),
                        alignment=1,
                    ),
                )
            )
            story.append(PageBreak())

        # Converter Markdown para PDF (primeira passagem)
        page_counter = 1 if incluir_capa == "s" else 0
        for texto, latex_images in textos:
            html = markdown.markdown(
                texto, extensions=["extra", "fenced_code", "tables", "footnotes"]
            )
            parser = MarkdownParser(doc.height, latex_images)
            parser.page_counter = page_counter
            parser.feed(html)
            story.extend(parser.story)
            page_counter = parser.page_counter

        # Definir destinos na primeira passagem
        def on_page_temp(canvas, doc):
            canvas.saveState()
            canvas.bookmarkPage(f"page{doc.page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=on_page_temp, onLaterPages=on_page_temp)

        # Contar páginas geradas
        reader = PdfReader(temp_pdf)
        total_pages = len(reader.pages)
        print(f"📄 Total de páginas geradas na primeira passagem: {total_pages}")

        # Validar entradas do sumário
        toc = [
            (texto, nivel, min(page, total_pages))
            for texto, nivel, page in toc
            if page <= total_pages and page > 0
        ]
        if incluir_sumario == "s" and not toc:
            print("⚠️ Nenhum título encontrado para o sumário.")

        # Segunda passagem: Criar PDF final com sumário
        story = []
        if incluir_capa == "s":
            if input("🖼️ Adicionar imagem à capa? (s/n): ").lower() == "s":
                img_path = input("📂 Caminho da imagem: ")
                if os.path.exists(img_path):
                    img = Image.open(img_path).convert("RGB")
                    img_width, img_height = img.size
                    scale = min(doc.width / img_width, doc.height / 4 / img_height)
                    story.append(
                        ReportLabImage(
                            img_path, width=img_width * scale, height=img_height * scale
                        )
                    )
                    story.append(Spacer(1, 12))
                else:
                    print(
                        f"⚠️ Imagem '{img_path}' não encontrada. Prosseguindo sem imagem."
                    )
            story.append(
                Paragraph(
                    config["capa_titulo"],
                    ParagraphStyle(
                        name="CapaTitulo",
                        fontSize=24,
                        fontName=validar_fonte(config["fonte"], bold=True),
                        alignment=1,
                        spaceAfter=20,
                    ),
                )
            )
            story.append(
                Paragraph(
                    config["capa_autor"],
                    ParagraphStyle(
                        name="CapaAutor",
                        fontSize=16,
                        fontName=validar_fonte(config["fonte"]),
                        alignment=1,
                        spaceAfter=20,
                    ),
                )
            )
            story.append(
                Paragraph(
                    config["capa_data"],
                    ParagraphStyle(
                        name="CapaData",
                        fontSize=12,
                        fontName=validar_fonte(config["fonte"]),
                        alignment=1,
                    ),
                )
            )
            story.append(PageBreak())

        if incluir_sumario == "s":
            story.append(Paragraph("Sumário", custom_styles["CustomHeading1"]))
            story.append(Spacer(1, 12))
            y_position = doc.height - 50
            for texto, nivel, page in toc:
                story.append(TOCEntry(texto, nivel, page, y_position))
                y_position -= 15
                print(f"Adicionando entrada ao sumário: {texto}, página {page}")
            story.append(PageBreak())

        # Reprocessar conteúdo
        page_counter = 1 if incluir_capa == "s" else 0
        if incluir_sumario == "s":
            page_counter += 1
        for texto, latex_images in textos:
            html = markdown.markdown(
                texto, extensions=["extra", "fenced_code", "tables", "footnotes"]
            )
            parser = MarkdownParser(doc.height, latex_images)
            parser.page_counter = page_counter
            parser.feed(html)
            story.extend(parser.story)
            page_counter = parser.page_counter

        # Adicionar numeração, marca d'água e destinos
        def on_page(canvas, doc):
            adicionar_pagina(
                canvas,
                doc,
                config["margem_esq"],
                config["margem_dir"],
                config["margem_sup"],
                config["margem_inf"],
                paginacao,
                doc.page,
                config["modelo_pagina"],
            )
            canvas.bookmarkPage(f"page{doc.page}")

        doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
        print(f"✅ PDF temporário salvo como: {temp_pdf}")

        # Edição e reordenação de páginas
        reader = PdfReader(temp_pdf)
        paginas = [page.extract_text() or "" for page in reader.pages]
        if (
            input("📝 Deseja editar, remover ou reordenar páginas? (s/n): ").lower()
            == "s"
        ):
            while True:
                print(f"📄 Total de páginas: {len(paginas)}")
                modo = input(
                    "📄 Visualizar [t]odas, [u]ma página, [e]ditar página, [r]emover página, [o]rdenar páginas, [s]air: "
                ).lower()
                if modo == "t":
                    visualizar_previa(
                        "",
                        paginas,
                        caminhos,
                        incluir_capa,
                        incluir_sumario,
                        config,
                        toc,
                    )
                elif modo == "u":
                    idx = int(input(f"📄 Número da página (1 a {len(paginas)}): ")) - 1
                    if 0 <= idx < len(paginas):
                        visualizar_previa(
                            paginas[idx],
                            caminhos=[caminhos[idx] if idx < len(caminhos) else None],
                            incluir_capa=incluir_capa,
                            incluir_sumario=incluir_sumario,
                            config=config,
                            toc=toc,
                        )
                    else:
                        print(f"❌ Página inválida. Escolha entre 1 e {len(paginas)}.")
                elif modo == "e":
                    idx = (
                        int(
                            input(
                                f"📄 Número da página para editar (1 a {len(paginas)}): "
                            )
                        )
                        - 1
                    )
                    if 0 <= idx < len(paginas):
                        paginas = editar_texto(temp_pdf, paginas, idx)
                        if paginas is None:
                            return
                    else:
                        print(f"❌ Página inválida. Escolha entre 1 e {len(paginas)}.")
                elif modo == "r":
                    idx = (
                        int(
                            input(
                                f"📄 Número da página para remover (1 a {len(paginas)}): "
                            )
                        )
                        - 1
                    )
                    if 0 <= idx < len(paginas):
                        paginas.pop(idx)
                        writer = PdfWriter()
                        reader = PdfReader(temp_pdf)
                        for i, page in enumerate(reader.pages):
                            if i != idx:
                                writer.add_page(page)
                        with open(temp_pdf, "wb") as f:
                            writer.write(f)
                        print(f"✅ Página {idx + 1} removida.")
                    else:
                        print(f"❌ Página inválida. Escolha entre 1 e {len(paginas)}.")
                elif modo == "o":
                    print("\n📑 Páginas atuais:")
                    for i, pagina in enumerate(paginas, 1):
                        print(f"[{i}] Página {i}: {pagina[:50]}...")
                    ordem = input("📑 Nova ordem das páginas (ex.: 2,1,3): ")
                    if ordem.strip():
                        try:
                            indices = [int(i) - 1 for i in ordem.split(",")]
                            if sorted(indices) == list(range(len(paginas))):
                                paginas = [paginas[i] for i in indices]
                                writer = PdfWriter()
                                reader = PdfReader(temp_pdf)
                                for i in indices:
                                    writer.add_page(reader.pages[i])
                                with open(temp_pdf, "wb") as f:
                                    writer.write(f)
                                print("✅ Páginas reordenadas com sucesso.")
                            else:
                                print(
                                    f"❌ Ordem inválida. Deve conter todos os números de 1 a {len(paginas)}."
                                )
                        except:
                            print(
                                "❌ Ordem inválida. Use números separados por vírgula."
                            )
                    else:
                        print("❌ Ordem não especificada. Mantendo ordem atual.")
                elif modo == "s":
                    break
                else:
                    print("❌ Opção inválida. Escolha t, u, e, r, o ou s.")

            # Reconstruir PDF após edição ou reordenação
            story = []
            toc = []
            if incluir_capa == "s":
                if input("🖼️ Adicionar imagem à capa? (s/n): ").lower() == "s":
                    img_path = input("📂 Caminho da imagem: ")
                    if os.path.exists(img_path):
                        img = Image.open(img_path).convert("RGB")
                        img_width, img_height = img.size
                        scale = min(doc.width / img_width, doc.height / 4 / img_height)
                        story.append(
                            ReportLabImage(
                                img_path,
                                width=img_width * scale,
                                height=img_height * scale,
                            )
                        )
                        story.append(Spacer(1, 12))
                    else:
                        print(
                            f"⚠️ Imagem '{img_path}' não encontrada. Prosseguindo sem imagem."
                        )
                story.append(
                    Paragraph(
                        config["capa_titulo"],
                        ParagraphStyle(
                            name="CapaTitulo",
                            fontSize=24,
                            fontName=validar_fonte(config["fonte"], bold=True),
                            alignment=1,
                            spaceAfter=20,
                        ),
                    )
                )
                story.append(
                    Paragraph(
                        config["capa_autor"],
                        ParagraphStyle(
                            name="CapaAutor",
                            fontSize=16,
                            fontName=validar_fonte(config["fonte"]),
                            alignment=1,
                            spaceAfter=20,
                        ),
                    )
                )
                story.append(
                    Paragraph(
                        config["capa_data"],
                        ParagraphStyle(
                            name="CapaData",
                            fontSize=12,
                            fontName=validar_fonte(config["fonte"]),
                            alignment=1,
                        ),
                    )
                )
                story.append(PageBreak())
            if incluir_sumario == "s":
                story.append(Paragraph("Sumário", custom_styles["CustomHeading1"]))
                story.append(Spacer(1, 12))
                y_position = doc.height - 50
                for texto, nivel, page in toc:
                    story.append(TOCEntry(texto, nivel, page, y_position))
                    y_position -= 15
                story.append(PageBreak())
            page_counter = 1 if incluir_capa == "s" else 0
            if incluir_sumario == "s":
                page_counter += 1
            for texto in paginas:
                html = markdown.markdown(
                    texto, extensions=["extra", "fenced_code", "tables", "footnotes"]
                )
                parser = MarkdownParser(doc.height)
                parser.page_counter = page_counter
                parser.feed(html)
                story.extend(parser.story)
                page_counter = parser.page_counter
            doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

        # Salvar PDF final
        os.rename(temp_pdf, saida)
        print(f"✅ PDF final salvo como: {saida}")

        if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
            enviar_telegram(saida)

    except Exception as e:
        print(
            f"❌ Erro na conversão: {str(e)}. Verifique os arquivos, configurações e tente novamente."
        )
