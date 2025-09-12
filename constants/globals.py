from reportlab.lib import colors

# This file is being refactored. Mutable global variables are being removed.
# The style constants below will be moved to a more appropriate location.

# Temas globais
temas = {
    "moderno": {"fonte": "Helvetica", "cor_texto": colors.black, "cor_titulo": colors.HexColor("#000080")},
    "classico": {"fonte": "Times-Roman", "cor_texto": colors.black, "cor_titulo": colors.HexColor("#320000")},
    "minimalista": {"fonte": "Courier", "cor_texto": colors.HexColor("#333333"), "cor_titulo": colors.HexColor("#333333")}
}

# Modelos de página
modelos_pagina = {
    "padrao": {"cor_fundo": colors.white, "borda": None},
    "colorido": {"cor_fundo": colors.HexColor("#E6F3FA"), "borda": colors.HexColor("#000080")},
    "profissional": {"cor_fundo": colors.white, "borda": colors.HexColor("#4A4A4A")}
}