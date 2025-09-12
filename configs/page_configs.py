import os
import json
from datetime import datetime
from configs.config import CONFIG_FILE
from constants.globals import config

def carregar_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                configs = json.load(f)
                if not isinstance(configs, dict):
                    print(
                        f"❌ Arquivo de configuração '{CONFIG_FILE}' malformado. Usando configurações padrão."
                    )
                    return get_default_config()
                print("\n📋 Perfis disponíveis:")
                for i, perfil in enumerate(configs.keys(), 1):
                    print(f"[{i}] {perfil}")
                escolha = input("📋 Escolha um perfil (ou Enter para padrão): ")
                if (
                    escolha.strip()
                    and escolha.isdigit()
                    and 1 <= int(escolha) <= len(configs)
                ):
                    return configs[list(configs.keys())[int(escolha) - 1]]
                return configs.get("default", get_default_config())
        return get_default_config()
    except json.JSONDecodeError as e:
        print(
            f"❌ Erro ao carregar configurações: JSON inválido em {CONFIG_FILE}. Usando padrões. Detalhes: {str(e)}"
        )
        return get_default_config()
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {str(e)}. Usando padrões.")
        return get_default_config()


def get_default_config():
    return {
        "margem_esq": 40,
        "margem_dir": 40,
        "margem_sup": 50,
        "margem_inf": 50,
        "fonte": "Helvetica",
        "tamanho_fonte": 12,
        "alinhamento": "justificado",
        "espacamento_linha": 1.15,
        "tema": "moderno",
        "modelo_pagina": "padrao",
        "tabela_estilo": "simples",
        "tabela_cor_fundo": "white",
        "tabela_cor_borda": "black",
        "capa_titulo": "Documento",
        "capa_autor": "Autor",
        "capa_data": datetime.now().strftime("%Y-%m-%d"),
        "verificar_titulos": True,
    }


def salvar_config(config):
    try:
        configs = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                configs = json.load(f)
                if not isinstance(configs, dict):
                    configs = {}
        nome_perfil = (
            input("📋 Nome do perfil para salvar (ex.: relatorio, padrão 'default'): ")
            or "default"
        )
        configs[nome_perfil] = config
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(configs, f, indent=4, ensure_ascii=False)
        print(f"✅ Perfil '{nome_perfil}' salvo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar configurações: {str(e)}.")
