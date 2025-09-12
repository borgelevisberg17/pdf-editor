import os
from constants.watermarker import marca_dagua
from PIL import Image
from reportlab.lib import colors

def aplicar_modelo_pagina(canvas, doc, config, modelo_config):
    """Aplica o estilo de fundo e borda da página."""
    canvas.saveState()

    # Cor de fundo
    if modelo_config.get("cor_fundo"):
        canvas.setFillColor(modelo_config["cor_fundo"])
        canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1)

    # Imagem de fundo
    img_fundo_path = config.get("imagem_fundo")
    if img_fundo_path and os.path.exists(img_fundo_path):
        try:
            img = Image.open(img_fundo_path).convert("RGB")
            # Lógica para escalar e desenhar a imagem de fundo
            canvas.drawImage(img_fundo_path, 0, 0, width=doc.pagesize[0], height=doc.pagesize[1], preserveAspectRatio=True)
        except Exception as e:
            # Log error instead of printing
            pass

    # Borda
    if modelo_config.get("borda"):
        canvas.setStrokeColor(modelo_config["borda"])
        canvas.setLineWidth(2)
        canvas.rect(config.get("margem_esq"), config.get("margem_inf"), doc.width, doc.height, stroke=1, fill=0)

    canvas.restoreState()


def adicionar_pagina(canvas, doc, config, pagina_atual):
    """
    Desenha os elementos fixos em cada página, como numeração e marca d'água.
    Controlado por um dicionário de configuração.
    """
    canvas.saveState()

    # Modelos de página
    modelos_pagina = {
        "padrao": {"cor_fundo": colors.white, "borda": None},
        "colorido": {"cor_fundo": colors.HexColor("#E6F3FA"), "borda": colors.HexColor("#000080")},
        "profissional": {"cor_fundo": colors.white, "borda": colors.HexColor("#4A4A4A")}
    }
    modelo_selecionado = config.get("modelo_pagina", "padrao")
    modelo_config = modelos_pagina.get(modelo_selecionado, modelos_pagina["padrao"])

    # Aplicar cor de fundo e bordas
    aplicar_modelo_pagina(canvas, doc, config, modelo_config)

    # Paginação
    paginacao = config.get("paginacao", {"tipo": "nenhuma"})
    if paginacao.get("tipo") != "nenhuma":
        inicio = paginacao.get("inicio", 1)
        if pagina_atual >= inicio:
            tipo = paginacao.get("tipo")
            if (tipo == "todas" or
                (tipo == "impares" and pagina_atual % 2 != 0) or
                (tipo == "pares" and pagina_atual % 2 == 0)):

                canvas.setFont("Helvetica", 10)
                canvas.setFillColor(colors.black)
                page_num_text = f"Página {pagina_atual}"
                canvas.drawCentredString(doc.pagesize[0] / 2, config.get("margem_inf", 20) * 0.5, page_num_text)

    # Marca d'água
    if config.get("incluir_marca_dagua", False):
        marca_dagua(canvas, doc.width + config.get("margem_esq", 40) + config.get("margem_dir", 40))

    canvas.restoreState()


def reordenar_arquivos(caminhos):
    """
    Esta função é interativa e deve ser movida para o módulo de UI.
    Deixada aqui temporariamente para não quebrar as importações existentes.
    """
    print("\n📑 Arquivos encontrados:")
    for i, caminho in enumerate(caminhos, 1):
        print(f"[{i}] {os.path.basename(caminho)}")
    print("\n📑 Digite a ordem dos arquivos (ex.: 2,1,3 para reordenar). Pressione Enter para manter a ordem atual.")
    ordem = input("Ordem (números separados por vírgula): ")
    if ordem.strip():
        try:
            indices = [int(i) - 1 for i in ordem.split(",")]
            if sorted(indices) == list(range(len(caminhos))):
                return [caminhos[i] for i in indices]
            else:
                print("❌ Ordem inválida. Usando ordem original.")
                return caminhos
        except Exception:
            print("❌ Ordem inválida. Usando ordem original.")
            return caminhos
    return caminhos
