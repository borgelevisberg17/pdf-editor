import os
import json

from configs.config_manager import carregar_config, salvar_config
from modules.content_manager import editar_texto
from modules.pdf_manager import mesclar_pdfs, infos_pdf, editar_pdf
from functions.html_to_pdf import html_para_pdf, exportar_para_html
from functions.txt_to_pdf import txt_para_pdf
from functions.imagem_to_pdf import imagem_para_pdf

def clear_screen():
    """Clears the terminal screen in a platform-independent way."""
    os.system('cls' if os.name == 'nt' else 'clear')

def gerenciar_configuracoes():
    try:
        modo = input("📋 [e]xportar, [i]mportar ou [l]istar configurações? ").lower()
        if modo == "e":
            config_to_export = carregar_config()
            nome_template = input("📋 Nome do template para exportar: ")
            with open(f"config_{nome_template}.json", "w", encoding="utf-8") as f:
                json.dump(config_to_export, f, indent=4, ensure_ascii=False)
            print(f"✅ Configurações exportadas como config_{nome_template}.json")
        elif modo == "i":
            caminho = input("📋 Caminho do arquivo JSON de configuração para importar: ")
            if os.path.exists(caminho):
                with open(caminho, "r", encoding="utf-8") as f:
                    config_to_import = json.load(f)
                salvar_config(config_to_import)
            else:
                print(f"❌ Arquivo '{caminho}' não encontrado.")
        # 'l' (listar) is handled implicitly by carregar_config now
        else:
            print("❌ Opção inválida. Escolha 'e' para exportar ou 'i' para importar.")
    except Exception as e:
        print(f"❌ Erro ao gerenciar configurações: {e}")

def menu():
    """Displays the main menu."""
    clear_screen()
    print("""
🧰 BorgePDF Toolbox – Dev Tools no Terminal 💼

[1] Converter TXT para PDF com formatação Markdown
[2] Converter TXT para PDF com Markdown e fórmulas LaTeX
[3] Converter Múltiplos TXTs para um PDF
[4] Converter Imagens para PDF
[5] Mesclar vários PDFs
[6] Ver informações de um PDF
[7] Editar texto no terminal
[8] Converter HTML para PDF
[9] Editar PDF existente
[10] Exportar TXT para HTML
[11] Gerenciar configurações (Exportar/Importar)
[0] Sair
""")

def main():
    """Main application loop."""
    while True:
        menu()
        op = input("Digite sua escolha: ")
        match op:
            case "1":
                txt_para_pdf(multiplos=False, process_latex=False)
            case "2":
                txt_para_pdf(multiplos=False, process_latex=True)
            case "3":
                txt_para_pdf(multiplos=True, process_latex=False)
            case "4":
                imagem_para_pdf()
            case "5":
                mesclar_pdfs()
            case "6":
                infos_pdf()
            case "7":
                caminho = input("📝 Caminho do arquivo .txt para editar: ")
                if os.path.exists(caminho) and caminho.endswith(".txt"):
                    editar_texto(caminho, is_file_path=True)
                else:
                    print(f"❌ Arquivo '{caminho}' inválido ou não encontrado.")
            case "8":
                html_para_pdf()
            case "9":
                editar_pdf()
            case "10":
                exportar_para_html()
            case "11":
                gerenciar_configuracoes()
            case "0":
                print("🙏 Até logo, dev! Fica com Deus.")
                break
            case _:
                print("❌ Opção inválida. Escolha entre 0 e 11.")

        input("\n🔁 Pressione Enter para continuar...")

if __name__ == "__main__":
    main()
