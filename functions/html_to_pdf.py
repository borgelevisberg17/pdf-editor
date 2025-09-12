import os
import webbrowser
import markdown
from weasyprint import HTML, CSS

from configs.config_manager import carregar_config, obter_configuracao_usuario
from modules.shares import enviar_telegram

def exportar_para_html():
    """
    Handles user interaction to convert one or more TXT files into a single,
    styled HTML file.
    """
    try:
        # 1. Get file paths
        caminho_str = input("📂 Caminho do arquivo ou pasta com .txt: ")
        if os.path.isdir(caminho_str):
            caminhos = [os.path.join(caminho_str, f) for f in sorted(os.listdir(caminho_str)) if f.endswith(".txt")]
            if not caminhos:
                print(f"❌ Nenhum arquivo .txt encontrado em '{caminho_str}'.")
                return
        elif os.path.isfile(caminho_str) and caminho_str.endswith(".txt"):
            caminhos = [caminho_str]
        else:
            print(f"❌ Caminho '{caminho_str}' não é um arquivo .txt ou pasta válida.")
            return

        saida_html = input("📄 Nome do arquivo HTML de saída (ex.: output.html): ")
        if not saida_html.endswith(".html"):
            saida_html += ".html"

        # 2. Get configuration
        config = carregar_config()
        config = obter_configuracao_usuario(config, has_tables=True) # Assume tables may exist

        # 3. Generate HTML content
        # Basic CSS generation from config
        temas = {
            "moderno": {"cor_titulo": "#000080"},
            "classico": {"cor_titulo": "#320000"},
            "minimalista": {"cor_titulo": "#333333"}
        }
        tema_selecionado = temas.get(config.get("tema", "moderno"), temas["moderno"])

        css_style = f"""
        @page {{
            margin-left: {config.get('margem_esq', 10)}mm;
            margin-right: {config.get('margem_dir', 10)}mm;
            margin-top: {config.get('margem_sup', 10)}mm;
            margin-bottom: {config.get('margem_inf', 10)}mm;
        }}
        body {{
            font-family: "{config.get('fonte', 'Helvetica')}";
            font-size: {config.get('tamanho_fonte', 12)}pt;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {tema_selecionado['cor_titulo']};
            font-family: "{config.get('fonte', 'Helvetica')}-Bold";
        }}
        p {{ line-height: {config.get('espacamento_linha', 1.15)}; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 1em; margin-bottom: 1em;}}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        """

        full_html_content = ""
        for caminho in caminhos:
            with open(caminho, 'r', encoding='utf-8') as f:
                text = f.read()
            full_html_content += markdown.markdown(text, extensions=["extra", "fenced_code", "tables", "footnotes"])

        final_html = f"<html><head><meta charset='UTF-8'><style>{css_style}</style></head><body>{full_html_content}</body></html>"

        with open(saida_html, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"✅ HTML salvo como: {saida_html}")
        if input("🔎 Visualizar HTML no navegador? (s/n): ").lower() == "s":
            webbrowser.open(f"file://{os.path.abspath(saida_html)}")

    except Exception as e:
        print(f"❌ Erro ao exportar para HTML: {e}")


def html_para_pdf():
    """
    Converts a local HTML file to PDF using WeasyPrint.
    This function is self-contained.
    """
    try:
        caminho = input("🌐 Caminho do arquivo .html: ")
        if not os.path.exists(caminho) or not caminho.endswith(".html"):
            print(f"❌ Arquivo '{caminho}' inválido ou não encontrado.")
            return

        saida = input("📄 Nome do PDF de saída (ex.: output.pdf): ")
        if not saida.endswith(".pdf"):
            saida += ".pdf"

        print("🚀 Convertendo HTML para PDF... Por favor, aguarde.")
        html = HTML(caminho)
        html.write_pdf(saida)

        print(f"✅ PDF salvo como: {saida}")
        if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
            enviar_telegram(saida)

    except Exception as e:
        print(f"❌ Erro na conversão de HTML para PDF: {e}")
        print("ℹ️  Esta função requer a instalação do WeasyPrint e suas dependências (Pango, Cairo).")
        print("ℹ️  Consulte a documentação: https://weasyprint.readthedocs.io/en/stable/install.html")
