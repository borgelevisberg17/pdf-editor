from reportlab.platypus.flowables import Flowable

# Sumário clicável
class TOCEntry(Flowable):
    def __init__(self, texto, nivel, page_num, y_position=0):
        Flowable.__init__(self)
        self.texto = texto
        self.nivel = nivel
        self.page_num = page_num
        self.y_position = y_position

    def draw(self):
        self.canv.setFont("Helvetica", 10)
        indent = self.nivel * 10
        texto = self.texto[:50] + "..." if len(self.texto) > 50 else self.texto  # Truncar
        if self.page_num > 0:
            try:
                # Criar um link clicável para o destino nomeado
                self.canv.linkAbsolute(
                    "", f"page{self.page_num}",
                    (indent, self.y_position, indent + 200, self.y_position + 10),
                    relative=1
                )
                self.canv.drawString(indent, self.y_position, f"{self.texto} ... {self.page_num}")
            except Exception as e:
                print(f"⚠️ Erro ao criar link para '{self.texto}': {str(e)}")
                self.canv.drawString(indent, self.y_position, f"{self.texto} ... (página não encontrada)")
        else:
            self.canv.drawString(indent, self.y_position, f"{self.texto} ... (página inválida)")
