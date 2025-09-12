from reportlab.lib import colors

# Variáveis globais
story = []
config = {}
custom_styles = {}
tabela_estilos = {}
incluir_sumario = 'n'
toc = []

# Temas globais
temas = {
    "moderno": {"fonte": "Helvetica", "cor_texto": colors.black, "cor_titulo": colors.HexColor("#000080")},
    "classico": {"fonte": "Times", "cor_texto": colors.black, "cor_titulo": colors.HexColor("#320000")},
    "minimalista": {"fonte": "Courier", "cor_texto": colors.HexColor("#333333"), "cor_titulo": colors.HexColor("#333333")}
}

# Modelos de página
modelos_pagina = {
    "padrao": {"cor_fundo": colors.white, "borda": None},
    "colorido": {"cor_fundo": colors.HexColor("#E6F3FA"), "borda": colors.HexColor("#000080")},
    "profissional": {"cor_fundo": colors.white, "borda": colors.HexColor("#4A4A4A")}
}