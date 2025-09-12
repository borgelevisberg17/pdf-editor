import os
from configs.config_manager import carregar_config, obter_configuracao_usuario
from modules.validations import registrar_fontes
from modules.shares import enviar_telegram
from modules.page_manager import reordenar_arquivos
from modules.content_manager import formatar_palavras
from modules.pdf_generator import PdfGenerator

def txt_para_pdf(multiplos=False, process_latex=False):
    """
    Handles the user interaction for converting TXT files to PDF, then uses
    PdfGenerator to perform the actual conversion.
    """
    try:
        registrar_fontes()
        # 1. Get File Paths
        if multiplos:
            pasta = input("📂 Caminho da pasta com arquivos .txt: ")
            if not os.path.isdir(pasta):
                print(f"❌ Pasta '{pasta}' não encontrada.")
                return
            caminhos = [os.path.join(pasta, f) for f in sorted(os.listdir(pasta)) if f.endswith(".txt")]
            if not caminhos:
                print("❌ Nenhum arquivo .txt encontrado na pasta.")
                return
            caminhos = reordenar_arquivos(caminhos)
        else:
            caminho = input("📝 Caminho do arquivo .txt: ")
            if not os.path.exists(caminho) or not caminho.endswith(".txt"):
                print(f"❌ Arquivo '{caminho}' inválido ou não encontrado.")
                return
            caminhos = [caminho]

        saida_pdf = input("📄 Nome do PDF de saída (ex.: output.pdf): ")
        if not saida_pdf.endswith(".pdf"):
            saida_pdf += ".pdf"

        # 2. Read and Prepare Content
        text_blocks = []
        has_tables = False
        for caminho in caminhos:
            with open(caminho, 'r', encoding='utf-8') as f:
                texto = f.read()
            if "|" in texto: # Simple check for tables
                has_tables = True

            texto = formatar_palavras(texto)
            text_blocks.append(texto)

        # 3. Get Configuration from User
        config = carregar_config()
        config["incluir_capa"] = input("📖 Incluir página de capa? (s/n, padrão s): ").lower() != 'n'
        config["incluir_sumario"] = input("📑 Incluir sumário clicável? (s/n, padrão s): ").lower() != 'n'

        paginacao_op = input("📄 Paginação (todas/impares/pares/a_partir_de/nenhuma, padrão todas): ") or "todas"
        paginacao_inicio = 1
        if paginacao_op == "a_partir_de":
            paginacao_inicio = int(input("📄 A partir de qual página? (ex.: 1): ") or 1)
        config["paginacao"] = {"tipo": paginacao_op, "inicio": paginacao_inicio}

        config = obter_configuracao_usuario(config, has_tables)

        # 4. Generate PDF
        print("\n🚀 Gerando PDF... Por favor, aguarde.")
        generator = PdfGenerator(config)
        generator.build(text_blocks, saida_pdf, process_latex)

        print(f"✅ PDF final salvo como: {saida_pdf}")

        # 5. Post-generation actions
        if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
            enviar_telegram(saida_pdf)

    except Exception as e:
        print(f"❌ Erro fatal na conversão: {e}")
        import traceback
        traceback.print_exc()
