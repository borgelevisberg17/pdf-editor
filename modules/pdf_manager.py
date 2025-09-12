import os
from pypdf import PdfReader, PdfWriter

from configs.config_manager import carregar_config, obter_configuracao_usuario
from modules.shares import enviar_telegram
from modules.content_manager import editar_texto
from modules.pdf_generator import PdfGenerator

def mesclar_pdfs():
    """
    Merges multiple PDF files into one. The file reordering logic
    should be handled by the caller UI.
    """
    try:
        arquivos_str = input("📄 PDFs para mesclar (separados por vírgula): ")
        arquivos = [arq.strip() for arq in arquivos_str.split(",") if arq.strip().endswith(".pdf")]

        valid_arquivos = [arq for arq in arquivos if os.path.exists(arq)]
        if not valid_arquivos:
            print("❌ Nenhum PDF válido encontrado. Verifique os caminhos.")
            return

        saida = input("📂 Nome do PDF final (ex.: output.pdf): ")
        if not saida.endswith(".pdf"):
            saida += ".pdf"

        writer = PdfWriter()
        for arq in valid_arquivos:
            reader = PdfReader(arq)
            for page in reader.pages:
                writer.add_page(page)

        with open(saida, "wb") as f:
            writer.write(f)
        print(f"✅ PDF mesclado salvo como: {saida}")

        if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
            enviar_telegram(saida)

    except Exception as e:
        print(f"❌ Erro ao mesclar PDFs: {e}")

def infos_pdf():
    """Displays information about a PDF file."""
    try:
        arq = input("🔍 Caminho do PDF: ")
        if not os.path.exists(arq) or not arq.endswith(".pdf"):
            print(f"❌ Arquivo '{arq}' inválido ou não encontrado.")
            return

        reader = PdfReader(arq)
        print(f"\n📄 Arquivo: {os.path.basename(arq)}")
        print(f"📄 Total de páginas: {len(reader.pages)}")
        for i, page in enumerate(reader.pages):
            box = page.mediabox
            print(f"  Página {i + 1}: {box.width}x{box.height} pts")

    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")

def editar_pdf():
    """
    Extracts text from a PDF, allows interactive editing/reordering of pages,
    and then rebuilds a *new* PDF from the modified text content.
    """
    try:
        # 1. Extract text from source PDF
        caminho = input("📄 Caminho do PDF para editar: ")
        if not os.path.exists(caminho) or not caminho.endswith(".pdf"):
            print(f"❌ Arquivo '{caminho}' inválido ou não encontrado.")
            return

        reader = PdfReader(caminho)
        paginas = [page.extract_text() or "" for page in reader.pages]
        if not paginas:
            print("❌ O PDF está vazio ou não contém texto extraível para edição.")
            return

        process_latex = input("📝 Processar fórmulas LaTeX no texto extraído? (s/n): ").lower() == 's'

        # 2. Interactive editing loop
        while True:
            print(f"\n📄 O PDF tem {len(paginas)} página(s).")
            modo = input("Modo: [e]ditar, [r]emover, [o]rdenar, [v]isualizar, [c]ontinuar para salvar: ").lower()

            if modo == 'e':
                idx_str = input(f"📄 Número da página para editar (1 a {len(paginas)}): ")
                if idx_str.isdigit() and 0 < int(idx_str) <= len(paginas):
                    idx = int(idx_str) - 1
                    novo_texto = editar_texto(paginas[idx]) # Pass the text directly
                    paginas[idx] = novo_texto
                    print("✅ Página atualizada.")
                else:
                    print("❌ Página inválida.")

            elif modo == 'r':
                idx_str = input(f"📄 Número da página para remover (1 a {len(paginas)}): ")
                if idx_str.isdigit() and 0 < int(idx_str) <= len(paginas):
                    idx = int(idx_str) - 1
                    paginas.pop(idx)
                    print(f"✅ Página {idx + 1} removida.")
                else:
                    print("❌ Página inválida.")

            elif modo == 'o':
                print("Páginas atuais: " + ", ".join(str(i+1) for i in range(len(paginas))))
                ordem_str = input("📑 Nova ordem (ex.: 2,1,3): ")
                try:
                    indices = [int(i.strip()) - 1 for i in ordem_str.split(",")]
                    if sorted(indices) == list(range(len(paginas))):
                        paginas = [paginas[i] for i in indices]
                        print("✅ Páginas reordenadas.")
                    else:
                        print("❌ Ordem inválida. Deve conter todos os números de página exatamente uma vez.")
                except:
                    print("❌ Entrada inválida.")

            elif modo == 'v':
                 for i, pagina_texto in enumerate(paginas):
                     print(f"\n--- Página {i+1} ---\n{pagina_texto[:200]}...")

            elif modo == 'c':
                break
            else:
                print("❌ Opção inválida.")

        if not paginas:
            print("❌ Nenhuma página restante. Abortando.")
            return

        # 3. Get configuration for the new PDF
        print("\n⚙️ Agora, configure o novo PDF a ser criado com o conteúdo editado.")
        config = carregar_config()
        config["incluir_capa"] = input("📖 Incluir página de capa no novo PDF? (s/n): ").lower() == 's'
        config["incluir_sumario"] = input("📑 Incluir sumário no novo PDF? (s/n): ").lower() == 's'
        config = obter_configuracao_usuario(config, has_tables=True) # Assume tables could be present

        saida_pdf = input("📄 Nome do PDF de saída (ex.: editado.pdf): ")
        if not saida_pdf.endswith(".pdf"):
            saida_pdf += ".pdf"

        # 4. Generate the new PDF
        print("\n🚀 Gerando PDF editado... Por favor, aguarde.")
        generator = PdfGenerator(config)
        generator.build(paginas, saida_pdf, process_latex)

        print(f"✅ PDF editado salvo como: {saida_pdf}")
        if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
            enviar_telegram(saida_pdf)

    except Exception as e:
        print(f"❌ Erro fatal ao editar PDF: {e}")
        import traceback
        traceback.print_exc()
