import json
import os
from datetime import datetime
from .config import CONFIG_FILE
from modules.validations import validar_fonte # Import needed for the moved function

def carregar_config(profile_name="default"):
    """Carrega um perfil de forma determinística, sem prompts interativos."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                configs = json.load(file)
            if isinstance(configs, dict):
                config = configs.get(profile_name) or configs.get("default")
                if isinstance(config, dict):
                    merged = get_default_config()
                    merged.update(config)
                    return merged
    except (json.JSONDecodeError, OSError):
        pass
    return get_default_config()

def get_default_config():
    """Retorna um dicionário com as configurações padrão."""
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
        "incluir_marca_dagua": False,
    }

def salvar_config(config_to_save, profile_name="default"):
    """Salva um dicionário de configuração em um perfil nomeado pelo usuário."""
    try:
        configs = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    configs = json.load(f)
                if not isinstance(configs, dict):
                    configs = {}
            except (json.JSONDecodeError, IOError):
                configs = {} # Overwrite if malformed or unreadable

        nome_perfil = profile_name or "default"
        configs[nome_perfil] = config_to_save

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(configs, f, indent=4, ensure_ascii=False)
        print(f"✅ Perfil '{nome_perfil}' salvo com sucesso em '{CONFIG_FILE}'!")

    except IOError as e:
        print(f"❌ Erro ao salvar configurações: {e}.")

def obter_configuracao_usuario(config, has_tables=False):
    """
    Prompts the user for configuration settings and updates the config dictionary.
    This is a UI-focused function.
    """
    if input("⚙️ Deseja personalizar as configurações? (s/n, padrão n): ").lower() == "s":
        # Page margins
        config["margem_esq"] = float(input(f"📏 Margem esquerda (mm, padrão {config.get('margem_esq', 40)}): ") or config.get('margem_esq', 40))
        config["margem_dir"] = float(input(f"📏 Margem direita (mm, padrão {config.get('margem_dir', 40)}): ") or config.get('margem_dir', 40))
        config["margem_sup"] = float(input(f"📏 Margem superior (mm, padrão {config.get('margem_sup', 50)}): ") or config.get('margem_sup', 50))
        config["margem_inf"] = float(input(f"📏 Margem inferior (mm, padrão {config.get('margem_inf', 50)}): ") or config.get('margem_inf', 50))

        # Font settings
        config["fonte"] = validar_fonte(input(f"🖋️ Fonte (Helvetica/Times-Roman/Courier, padrão {config.get('fonte', 'Helvetica')}): ") or config.get('fonte', 'Helvetica'))
        config["tamanho_fonte"] = float(input(f"📏 Tamanho da fonte (padrão {config.get('tamanho_fonte', 12)}): ") or config.get('tamanho_fonte', 12))

        # Text alignment and spacing
        config["alinhamento"] = input(f"📍 Alinhamento (esquerda/centro/justificado, padrão {config.get('alinhamento', 'justificado')}): ").lower() or config.get('alinhamento', 'justificado')
        config["espacamento_linha"] = float(input(f"📏 Espaçamento entre linhas (padrão {config.get('espacamento_linha', 1.15)}): ") or config.get('espacamento_linha', 1.15))

        # Theme and style
        config["tema"] = input("🎨 Tema (moderno/classico/minimalista, padrão moderno): ") or "moderno"
        config["modelo_pagina"] = input("📄 Modelo de página (padrao/colorido/profissional, padrão padrao): ") or "padrao"
        config["imagem_fundo"] = input("🖼️ Caminho da imagem de fundo (opcional, Enter para nenhum): ") or ""

        # Table styles
        if has_tables:
            config["tabela_estilo"] = input("📊 Estilo da tabela (simples/grade/listrado/personalizado, padrão simples): ") or "simples"
            if config["tabela_estilo"] == "personalizado":
                config["tabela_cor_fundo"] = input("🎨 Cor de fundo da tabela (ex.: white, lightgrey, #FF0000): ") or "white"
                config["tabela_cor_borda"] = input("🎨 Cor da borda da tabela (ex.: black, #000000): ") or "black"

        # Cover page settings
        if config.get("incluir_capa"):
            config["capa_titulo"] = input(f"📖 Título da capa (padrão {config.get('capa_titulo', 'Documento')}): ") or config.get('capa_titulo', 'Documento')
            config["capa_autor"] = input(f"✍️ Autor da capa (padrão {config.get('capa_autor', 'Autor')}): ") or config.get('capa_autor', 'Autor')
            config["capa_data"] = input(f"📅 Data da capa (padrão {config.get('capa_data', 'Hoje')}): ") or config.get('capa_data', 'Hoje')
            if input("🖼️ Adicionar imagem à capa? (s/n): ").lower() == "s":
                config["capa_imagem_path"] = input("📂 Caminho da imagem da capa: ")

        if input("💾 Salvar estas configurações como um novo perfil? (s/n): ").lower() == 's':
            salvar_config(config)

    return config
