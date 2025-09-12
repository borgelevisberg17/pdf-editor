import os
import re
from constants.globals import story, config, incluir_sumario, toc
from prompt_toolkit import PromptSession

try:
    from rich.console import Console
    from rich.table import Table as RichTable

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Edição de texto
def editar_texto(caminho, paginas=None, pagina_idx=None):
    try:
        if not os.access(os.path.dirname(caminho) or ".", os.W_OK):
            print(f"❌ Sem permissão para escrever em {caminho}.")
            return None
        if paginas and pagina_idx is not None:
            texto = paginas[pagina_idx]
            print(
                f"📝 Editando Página {pagina_idx + 1}. Use Ctrl+D (Linux/Mac) ou Ctrl+Z+Enter (Windows/Termux) para salvar."
            )
            session = PromptSession(multiline=True, default=texto or "")
            novo_texto = session.prompt("📝 Edite o texto (Markdown):\n")
            paginas[pagina_idx] = novo_texto
            print(f"✅ Página {pagina_idx + 1} editada com sucesso.")
            return paginas
        else:
            if not os.path.exists(caminho):
                print(f"❌ Arquivo '{caminho}' não encontrado.")
                return None
            with open(caminho, "r", encoding="utf-8") as f:
                texto = f.read()
            print(
                "📝 Editando texto. Use Ctrl+D (Linux/Mac) ou Ctrl+Z+Enter (Windows/Termux) para salvar."
            )
            session = PromptSession(multiline=True, default=texto or "")
            novo_texto = session.prompt("📝 Edite o texto (Markdown):\n")
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(novo_texto)
            print(f"✅ Texto salvo em {caminho}.")
            return novo_texto
    except Exception as e:
        print(f"❌ Erro ao editar texto: {str(e)}. Verifique o arquivo e permissões.")
        return None


# Formatação de palavras
def formatar_palavras(texto):
    if input("🔍 Deseja formatar palavras específicas? (s/n): ").lower() != "s":
        return texto
    while True:
        palavra = input("🔍 Palavra-chave a formatar (ou Enter para parar): ")
        if not palavra:
            break
        formato = input("🎨 Formato (negrito/sublinhado/cor): ").lower()
        cor = None
        if formato == "cor":
            cor = input("🎨 Cor (ex.: red, #FF0000): ")
        if formato in ("negrito", "sublinhado", "cor"):
            if formato == "negrito":
                texto = re.sub(
                    rf"\b{palavra}\b", f"**{palavra}**", texto, flags=re.IGNORECASE
                )
            elif formato == "sublinhado":
                texto = re.sub(
                    rf"\b{palavra}\b", f"<u>{palavra}</u>", texto, flags=re.IGNORECASE
                )
            elif formato == "cor" and cor:
                texto = re.sub(
                    rf"\b{palavra}\b",
                    f'<font color="{cor}">{palavra}</font>',
                    texto,
                    flags=re.IGNORECASE,
                )
        else:
            print("❌ Formato inválido. Use negrito, sublinhado ou cor.")
    return texto


# Pré-visualização de tabelas com rich
def visualizar_previa(
    texto,
    paginas=None,
    caminhos=None,
    incluir_capa=None,
    incluir_sumario="n",
    config=None,
    toc=None,
):
    if not RICH_AVAILABLE:
        print("⚠️ Biblioteca 'rich' não instalada. Usando visualização padrão.")
        if paginas:
            for i, (pagina, caminho) in enumerate(zip(paginas, caminhos or [None]), 1):
                print(
                    f"\nPágina {i} ({os.path.basename(caminho) if caminho else 'Sem arquivo'}):\n{'-' * 50}"
                )
                print(
                    pagina[:500] + "..."
                    if pagina and len(pagina) > 500
                    else pagina or "Página vazia"
                )
        else:
            print("\n📄 Visualização Prévia do Conteúdo (primeiros 500 caracteres):\n")
            print(
                texto[:500] + "..."
                if texto and len(texto) > 500
                else texto or "Texto vazio"
            )
        return input("✅ Confirmar conversão? (s/n): ").lower() == "s"

    console = Console()
    console.rule(f"[bold]Pré-visualização do PDF[/bold]")
    if incluir_capa == "s" and config:
        console.print(
            f"[bold cyan]{config['capa_titulo']}[/bold cyan]", justify="center"
        )
        console.print(f"[italic]{config['capa_autor']}[/italic]", justify="center")
        console.print(f"{config['capa_data']}", justify="center")
        console.print("")
    if incluir_sumario == "s" and toc:
        table = RichTable(title="Sumário")
        table.add_column("Título")
        table.add_column("Página")
        for texto, nivel, page in toc:
            table.add_row(f"{'  ' * nivel}{texto}", str(page))
        console.print(table)
    if paginas:
        for i, (pagina, caminho) in enumerate(zip(paginas, caminhos or [None]), 1):
            console.print(
                f"\n[bold]Página {i} ({os.path.basename(caminho) if caminho else 'Sem arquivo'})[/bold]:"
            )
            console.print(
                pagina[:200] + "..."
                if pagina and len(pagina) > 200
                else pagina or "Página vazia"
            )
    else:
        console.print(f"\n[bold]Conteúdo[/bold]:")
        console.print(
            texto[:200] + "..."
            if texto and len(texto) > 200
            else texto or "Texto vazio"
        )
    return (
        console.input(
            "[bold green]✅ Confirmar conversão? (s/n): [/bold green]"
        ).lower()
        == "s"
    )
