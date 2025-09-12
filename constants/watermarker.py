# Marca d'água e numeração
def marca_dagua(canvas, largura, texto="📌 Borge Dev – Feito com Python"):
    canvas.saveState()
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColorRGB(0.5, 0.5, 0.5, alpha=0.3)  # Adiciona transparência
    canvas.drawCentredString(largura / 2, 30, texto)  # Ajusta y para 30
    canvas.restoreState()