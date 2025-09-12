import os
import re
from prompt_toolkit import PromptSession

def editar_texto(text_content, is_file_path=False):
    """
    Opens an interactive multiline prompt to edit text.
    Can operate on a string or read/write from a file path.
    """
    try:
        if is_file_path:
            # Editing a file on disk
            if not os.path.exists(text_content):
                print(f"❌ Arquivo '{text_content}' não encontrado.")
                return None
            with open(text_content, "r", encoding="utf-8") as f:
                default_text = f.read()
        else:
            # Editing a string in memory
            default_text = text_content

        print("📝 Editando texto. Use Ctrl+D (Linux/Mac) ou Ctrl+Z+Enter (Windows) para salvar.")
        session = PromptSession(multiline=True, default=default_text or "")
        novo_texto = session.prompt("Edite o texto (Markdown):\n")

        if is_file_path:
            with open(text_content, "w", encoding="utf-8") as f:
                f.write(novo_texto)
            print(f"✅ Texto salvo em {text_content}.")

        return novo_texto

    except Exception as e:
        print(f"❌ Erro ao editar texto: {e}.")
        return None if is_file_path else text_content # Return original content on error if in memory

def formatar_palavras(texto):
    """
    Interactively prompts the user to find and format specific words
    in the text with Markdown or HTML font tags.
    """
    if input("🔍 Deseja formatar palavras específicas? (s/n): ").lower() != "s":
        return texto

    while True:
        palavra = input("🔍 Palavra-chave a formatar (ou Enter para parar): ")
        if not palavra:
            break

        formato = input("🎨 Formato (negrito/sublinhado/cor): ").lower()

        if formato == "negrito":
            texto = re.sub(rf"(\b)({re.escape(palavra)})(\b)", r"\1**\2**\3", texto, flags=re.IGNORECASE)
        elif formato == "sublinhado":
            texto = re.sub(rf"(\b)({re.escape(palavra)})(\b)", r"\1<u>\2</u>\3", texto, flags=re.IGNORECASE)
        elif formato == "cor":
            cor = input("🎨 Cor (ex: red, #FF0000): ")
            if cor:
                texto = re.sub(rf"(\b)({re.escape(palavra)})(\b)", f'\\1<font color="{cor}">\\2</font>\\3', texto, flags=re.IGNORECASE)
        else:
            print("❌ Formato inválido. Use negrito, sublinhado ou cor.")

    print("✅ Formatação de palavras concluída.")
    return texto
