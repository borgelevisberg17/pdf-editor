import requests
from configs.config import CHAT_ID, TELEGRAM_TOKEN

# Configurações do Telegram
def enviar_telegram(caminho_pdf):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        with open(caminho_pdf, "rb") as f:
            files = {"document": f}
            data = {"chat_id": CHAT_ID}
            response = requests.post(url, files=files, data=data)
            if response.ok:
                print("✅ PDF enviado via Telegram com sucesso!")
            else:
                print(f"❌ Erro ao enviar o PDF: {response.text}. Verifique o token ou ID do chat.")
    except ImportError:
        print("❌ Configurações do Telegram não encontradas. Verifique o arquivo config.py.")
    except Exception as e:
        print(f"❌ Erro ao enviar para Telegram: {str(e)}. Certifique-se de que o arquivo existe e a conexão está ativa.")
