import os

import json

from constants.globals import config

from configs.page_configs import carregar_config, salvar_config

from modules.content_manager import editar_texto

from modules.pdf_manager import mesclar_pdfs, infos_pdf, editar_pdf

from functions.html_to_pdf import html_para_pdf

from functions.txt_to_pdf import txt_para_pdf

from functions.imagem_to_pdf import imagem_para_pdf


def gerenciar_configuracoes():
    try:
        modo = input("📋 [e]xportar, [i]mportar ou [l]istar configurações? ")
        if modo == "e":
            config = carregar_config()
            nome_template = input("📋 Nome do template para exportar: ")
            with open(f"config_{nome_template}.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"✅ Configurações exportadas como config_{nome_template}.json")
        elif modo == "i":
            caminho = input("📋 Caminho do arquivo JSON: ")
            if os.path.exists(caminho):
                with open(caminho, "r", encoding="utf-8") as f:
                    config = json.load(f)
                salvar_config(config)
            else:
                print(f"❌ Arquivo '{caminho}' não encontrado.")
        elif modo == "l":
            configs = {}
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    configs = json.load(f)
                print("\n📋 Templates disponíveis:")
                for perfil in configs.keys():
                    print(f"- {perfil}")
            else:
                print("❌ Nenhum template encontrado.")
        else:
            print("❌ Opção inválida. Escolha e, i ou l.")
    except Exception as e:
        print(f"❌ Erro ao gerenciar configurações: {str(e)}.")


# === MENU ===
def menu():
    os.system("clear")
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
[10] Exportar/Importar configurações
[0] Sair
""")


def main():
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
                if not os.path.exists(caminho) or not caminho.endswith(".txt"):
                    print(
                        f"❌ Arquivo '{caminho}' inválido ou não encontrado. Use um arquivo .txt."
                    )
                else:
                    editar_texto(caminho)
            case "8":
                html_para_pdf()
            case "9":
                editar_pdf()
            case "10":
                gerenciar_configuracoes()
            case "0":
                print("🙏 Até logo, dev! Fica com Deus.")
                break
            case _:
                print("❌ Opção inválida. Escolha entre 0 e 10.")
        input("\n🔁 Pressione Enter para continuar...")


if __name__ == "__main__":
    main()
