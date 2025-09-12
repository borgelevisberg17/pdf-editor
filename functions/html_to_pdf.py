import os
import re
import webbrowser
from constants.globals import story, config, incluir_sumario, temas
from modules.shares import enviar_telegram
from weasyprint import HTML


# Exportação para HTML
def exportar_para_html(textos, config, saida_html, sumario=False, titulos=None):
    try:
        html_content = "<html><head><style>"
        html_content += f"""
        body {{ font-family: {config["fonte"]}; font-size: {config["tamanho_fonte"]}pt; margin: {config["margem_esq"]}mm {config["margem_dir"]}mm; }}
        h1 {{ font-size: {config["tamanho_fonte"] + 4}pt; color: {temas[config["tema"]]["cor_titulo"].hex}; }}
        h2 {{ font-size: {config["tamanho_fonte"] + 2}pt; color: {temas[config["tema"]]["cor_titulo"].hex}; }}
        p {{ line-height: {config["espacamento_linha"]}; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid {config["tabela_cor_borda"]}; padding: 8px; }}
        """
        html_content += "</style></head><body>"

        if sumario and titulos:
            html_content += "<h1>Sumário</h1><ul>"
            for i, (titulo, _) in enumerate(titulos, 1):
                html_content += f"<li><a href='#section{i}'>{titulo}</a></li>"
            html_content += "</ul>"

        for i, texto in enumerate(textos, 1):
            html_content += (
                f"<div id='section{i}'>"
                + markdown.markdown(
                    texto, extensions=["extra", "fenced_code", "tables", "footnotes"]
                )
                + "</div>"
            )

        html_content += "</body></html>"
        with open(saida_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✅ HTML salvo como: {saida_html}")
        if input("🔎 Visualizar HTML no navegador? (s/n): ").lower() == "s":
            webbrowser.open(f"file://{os.path.abspath(saida_html)}")
    except Exception as e:
        print(
            f"❌ Erro ao exportar para HTML: {str(e)}. Verifique o caminho e tente novamente."
        )


# Conversão de HTML para PDF
def html_para_pdf():
    try:
        caminho = input("🌐 Caminho do arquivo .html: ")
        if not os.path.exists(caminho) or not caminho.endswith(".html"):
            print(
                f"❌ Arquivo '{caminho}' inválido ou não encontrado. Use um arquivo .html."
            )
            return
        saida = input("📄 Nome do PDF de saída (ex.: output.pdf): ")
        if not saida.endswith(".pdf"):
            saida += ".pdf"
        HTML(caminho).write_pdf(saida)
        print(f"✅ PDF salvo como: {saida}")
        if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
            enviar_telegram(saida)
    except Exception as e:
        print(
            f"❌ Erro na conversão de HTML para PDF: {str(e)}. Instale libpango, libcairo, gdk-pixbuf ou desative esta função."
        )
