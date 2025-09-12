import os

from PIL import Image

from modules.shares import enviar_telegram

# Conversão de imagens para PDF
def imagem_para_pdf():
    try:
        escolha = input("📷 Converter [1] Uma imagem ou [2] Várias imagens? ")
        if escolha == "1":
            img = input("🖼️ Caminho da imagem: ")
            if not os.path.exists(img) or not img.lower().endswith(
                (".png", ".jpg", ".jpeg")
            ):
                print(
                    f"❌ Imagem '{img}' inválida ou não encontrada. Use .png, .jpg ou .jpeg."
                )
                return
            out = input("📄 Nome do PDF de saída (ex.: output.pdf): ")
            if not out.endswith(".pdf"):
                out += ".pdf"
            if not os.access(os.path.dirname(out) or ".", os.W_OK):
                print(
                    f"❌ Sem permissão para escrever em '{out}'. Escolha outro local."
                )
                return
            imagem = Image.open(img).convert("RGB")
            imagem.save(out, "PDF", resolution=100.0)
            print(f"✅ Imagem convertida em PDF: {out}")
            if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
                enviar_telegram(out)
        elif escolha == "2":
            imagens = input("🖼️ Caminhos separados por vírgula: ").split(",")
            imagens = [
                i.strip()
                for i in imagens
                if os.path.exists(i.strip())
                and i.strip().lower().endswith((".png", ".jpg", ".jpeg"))
            ]
            if not imagens:
                print("❌ Nenhuma imagem válida encontrada. Use .png, .jpg ou .jpeg.")
                return
            imagens = reordenar_arquivos(imagens)
            out = input("📄 Nome do PDF de saída (ex.: output.pdf): ")
            if not out.endswith(".pdf"):
                out += ".pdf"
            if not os.access(os.path.dirname(out) or ".", os.W_OK):
                print(
                    f"❌ Sem permissão para escrever em '{out}'. Escolha outro local."
                )
                return
            lista = [Image.open(i).convert("RGB") for i in imagens]
            lista[0].save(out, save_all=True, append_images=lista[1:])
            print(f"✅ PDF com {len(lista)} imagens salvo como: {out}")
            if input("📤 Enviar para Telegram? (s/n): ").lower() == "s":
                enviar_telegram(out)
        else:
            print("❌ Opção inválida. Escolha 1 ou 2.")
    except Exception as e:
        print(
            f"❌ Erro na conversão de imagem: {str(e)}. Verifique os arquivos e tente novamente."
        )
