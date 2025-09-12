import os
from constants.watermarker import marca_dagua
from constants.globals import config, modelos_pagina
from PIL import Image


def aplicar_modelo_pagina(
    canvas, doc, modelo, margem_esq, margem_dir, margem_sup, margem_inf
):
    canvas.saveState()
    if modelo["cor_fundo"]:
        canvas.setFillColor(modelo["cor_fundo"])
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1)
    if config.get("imagem_fundo") and os.path.exists(config["imagem_fundo"]):
        try:
            img = Image.open(config["imagem_fundo"]).convert("RGB")
            img_width, img_height = img.size
            scale = min(doc.pagesize[0] / img_width, doc.pagesize[1] / img_height)
            canvas.drawImage(
                config["imagem_fundo"],
                0,
                0,
                width=img_width * scale,
                height=img_height * scale,
            )
        except Exception as e:
            print(f"⚠️ Erro ao adicionar imagem de fundo: {str(e)}")
    if modelo["borda"]:
        canvas.setStrokeColor(modelo["borda"])
        canvas.setLineWidth(2)
        canvas.rect(margem_esq, margem_inf, doc.width, doc.height, stroke=1, fill=0)
    canvas.restoreState()


def adicionar_pagina(
    canvas,
    doc,
    margem_esq,
    margem_dir,
    margem_sup,
    margem_inf,
    paginacao,
    pagina_atual,
    modelo,
):
    canvas.saveState()
    aplicar_modelo_pagina(
        canvas,
        doc,
        modelos_pagina[modelo],
        margem_esq,
        margem_dir,
        margem_sup,
        margem_inf,
    )
    if paginacao["tipo"] != "nenhuma" and (
        paginacao["tipo"] != "a_partir_de" or pagina_atual >= paginacao["inicio"]
    ):
        if (
            paginacao["tipo"] == "todas"
            or (paginacao["tipo"] == "impares" and pagina_atual % 2 == 1)
            or (paginacao["tipo"] == "pares" and pagina_atual % 2 == 0)
        ):
            canvas.setFont("Helvetica", 10)
            canvas.setFillColor(colors.black)
            canvas.drawString(margem_esq, margem_inf - 10, f"Página {pagina_atual}")
    marca_dagua(canvas, doc.width + margem_esq + margem_dir)
    canvas.restoreState()


# Reordenar arquivos
def reordenar_arquivos(caminhos):
    print("\n📑 Arquivos encontrados:")
    for i, caminho in enumerate(caminhos, 1):
        print(f"[{i}] {os.path.basename(caminho)}")
    print(
        "\n📑 Digite a ordem dos arquivos (ex.: 2,1,3 para reordenar). Pressione Enter para manter a ordem atual."
    )
    ordem = input("Ordem (números separados por vírgula): ")
    if ordem.strip():
        try:
            indices = [int(i) - 1 for i in ordem.split(",")]
            if sorted(indices) == list(range(len(caminhos))):
                return [caminhos[i] for i in indices]
            else:
                print("❌ Ordem inválida. Usando ordem original.")
                return caminhos
        except:
            print("❌ Ordem inválida. Usando ordem original.")
            return caminhos
    return caminhos
