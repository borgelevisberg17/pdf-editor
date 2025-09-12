import re
from sympy import preview
from io import BytesIO

def extract_latex_blocks(text):
    """Extrai blocos de LaTeX do texto usando a sintaxe $$ ... $$"""
    pattern = r'\$\$(.*?)\$\$'
    blocks = re.findall(pattern, text, re.DOTALL)
    return blocks

def replace_latex_with_placeholders(text):
    """Substitui blocos de LaTeX e fórmulas inline por placeholders únicos"""
    block_pattern = r'\$\$(.*?)\$\$'
    inline_pattern = r'(?<!\$)\$(.*?)(?<!\$)\$'  # Evita capturar $$...$$
    placeholders = {}
    counter = 0

    def replacer(match):
        nonlocal counter
        placeholder = f'<!-- LATEX_IMAGE_{counter} -->'
        placeholders[placeholder] = match.group(1)
        counter += 1
        return placeholder

    text = re.sub(block_pattern, replacer, text, flags=re.DOTALL)
    text = re.sub(inline_pattern, replacer, text, flags=re.DOTALL)
    return text, placeholders

def render_latex_to_image(latex_str):
    """Renderiza uma fórmula LaTeX como imagem PNG usando SymPy"""
    buf = BytesIO()
    try:
        preview(f"${latex_str}$", output="png", viewer="BytesIO",
                outputbuffer=buf, euler=False, dvioptions=['-D', '300'])
        buf.seek(0)
        return buf
    except Exception as e:
        print(f"⚠️ Erro ao renderizar LaTeX '{latex_str}': {str(e)}")
        return None