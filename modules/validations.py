import os
import re
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import getRegisteredFontNames
from reportlab.pdfbase.ttfonts import TTFont

# Validação de cores
def validar_cor(cor):
    try:
        return colors.toColor(cor)
    except:
        print(f"❌ Cor '{cor}' inválida. Usando padrão: white.")
        return colors.white


# Validação de fontes
def validar_fonte(fonte, bold=False, regular=False):
    fontes_disponiveis = getRegisteredFontNames()
    fonte_base = fonte
    fonte_completa = f"{fonte}-Bold" if bold else fonte
    fontes_completa = f"{fonte}-Regular" if regular else fonte
    if fonte_completa in fontes_disponiveis:
        return fonte_completa
    if fonte_base in fontes_disponiveis:
        return fonte_base
    print(f"⚠️ Fonte '{fonte_completa}' não encontrada. Usando 'Helvetica'.")
    return "Helvetica"


# Registrar fontes
def registrar_fontes():
    fontes_padrao = [
        "Helvetica",
        "Times-Roman",
        "Courier",
        "Roboto"
    ]  # Fontes embutidas do ReportLab
    diretorio_fontes = (
        input(
            "📂 Diretório das fontes .ttf (ex.: /sdcard/fonts, ou Enter para usar fontes padrão): "
        )
        or ""
    )

    if not diretorio_fontes:
        print("ℹ️ Usando fontes padrão do ReportLab (Helvetica, Times-Roman, Courier).")
        return

    if not os.path.isdir(diretorio_fontes):
        print(
            f"❌ Diretório '{diretorio_fontes}' não encontrado. Usando fontes padrão."
        )
        return

    for arquivo in os.listdir(diretorio_fontes):
        if arquivo.endswith(".ttf"):
            try:
                caminho = os.path.join(diretorio_fontes, arquivo)
                nome_fonte = os.path.splitext(arquivo)[0]
                pdfmetrics.registerFont(TTFont(nome_fonte, caminho))
                print(f"✅ Fonte '{nome_fonte}' registrada com sucesso.")
            except Exception as e:
                print(
                    f"⚠️ Erro ao registrar fonte '{arquivo}': {str(e)}. Usando fonte padrão."
                )

# Validação de tabelas Markdown
def validar_tabela_markdown(texto):
    try:
        lines = texto.split('\n')
        table_lines = [line.strip() for line in lines if line.strip().startswith('|')]
        if len(table_lines) < 2:
            return False
        col_count = len(table_lines[0].split('|')) - 2
        if not re.match(r'^\|[-:\s]+(?:\|[-:\s]+)*\|$', table_lines[1]):
            print(f"⚠️ Aviso: Linha de separação de cabeçalho inválida na tabela.")
            return False
        for line in table_lines[2:]:
            if len(line.split('|')) - 2 != col_count:
                print(f"⚠️ Aviso: Tabela inconsistente. Linha '{line}' tem número de colunas diferente.")
                return False
        return True
    except Exception as e:
        print(f"❌ Erro ao validar tabela: {str(e)}.")
        return False