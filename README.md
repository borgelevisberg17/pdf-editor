# BorgePDF Toolbox

**BorgePDF Toolbox** é uma ferramenta em Python para manipulação de arquivos, com foco na conversão de arquivos TXT (com formatação Markdown e LaTeX), imagens e HTML para PDF, além de mesclagem e edição de PDFs no terminal.

Esta versão do projeto foi extensivamente refatorada para melhorar a arquitetura do software, eliminando código duplicado e variáveis globais. A lógica de negócio foi separada da interface de usuário, resultando em um código mais limpo, manutenível e testável.

## Funcionalidades
- **Conversão de TXT para PDF**: Transforma arquivos TXT com formatação Markdown em PDFs, com suporte a títulos, listas, tabelas, notas de rodapé e imagens.
- **Suporte a LaTeX**: Renderiza fórmulas LaTeX (`$e=mc^2$`) em imagens e as insere no PDF.
- **Conversão de Múltiplos Arquivos**: Combina vários arquivos TXT em um único PDF.
- **Conversão de Imagens para PDF**: Converte uma ou várias imagens (.png, .jpg, .jpeg) em PDF.
- **Conversão de HTML para PDF**: Converte arquivos HTML em PDFs usando WeasyPrint.
- **Exportação para HTML**: Converte arquivos TXT (Markdown) para HTML estilizado.
- **Mesclagem de PDFs**: Combina múltiplos PDFs em um único arquivo.
- **Edição de PDF (baseada em texto)**: Extrai o texto de um PDF, permite editar, remover ou reordenar as páginas, e gera um *novo* PDF.
- **Informações de PDF**: Exibe detalhes como número de páginas e dimensões.
- **Personalização Avançada**:
  - Margens, fontes, tamanho de fonte, alinhamento, espaçamento entre linhas.
  - Temas (moderno, clássico, minimalista).
  - Estilos de tabelas e paginação configurável.
  - Capa personalizável com título, autor e data.
  - Sumário clicável.
- **Gerenciamento de Configurações**: Salva e carrega perfis de configuração para reutilização.
- **Envio via Telegram**: Envia PDFs gerados diretamente para um chat do Telegram.

## Pré-requisitos
- Python 3.10+
- **WeasyPrint**: Para a conversão de HTML para PDF, pode ser necessário instalar dependências adicionais (ex: GTK no Windows, `libpango` no Linux/Mac). Veja a [documentação do WeasyPrint](https://weasyprint.readthedocs.io/).
- **LaTeX**: Para renderizar fórmulas LaTeX, é preciso ter uma distribuição LaTeX instalada (ex: MiKTeX, TeX Live, MacTeX).
- **Telegram (Opcional)**: Para enviar arquivos, crie um arquivo `configs/config.py` com seu `CHAT_ID` e `TELEGRAM_TOKEN`.

## Instalação
1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd <pasta-do-repositorio>
   ```
2. Instale as dependências usando o arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) Configure as credenciais do Telegram em `configs/config.py`.

## Uso
Execute o script principal `full.py` a partir da raiz do projeto:
```bash
python full.py
```
Siga as opções do menu interativo:
```
🧰 BorgePDF Toolbox – Dev Tools no Terminal 💼

[1] Converter TXT para PDF com formatação Markdown
[2] Converter TXT para PDF com Markdown e fórmulas LaTeX
[3] Converter Múltiplos TXTs para um PDF
[4] Converter Imagens para PDF
[5] Mesclar vários PDFs
[6] Ver informações de um PDF
[7] Editar texto no terminal
[8] Converter HTML para PDF
[9] Editar PDF existente
[10] Exportar TXT para HTML
[11] Gerenciar configurações (Exportar/Importar)
[0] Sair
```

## Estrutura do Projeto
A arquitetura do projeto foi refatorada para uma melhor separação de responsabilidades:
- `full.py`: O ponto de entrada principal da aplicação, responsável pelo menu e pela orquestração das chamadas.
- `requirements.txt`: Lista de todas as dependências do projeto.
- `configs/`: Módulos para gerenciamento de configurações da aplicação (perfis, prompts, etc.).
- `constants/`: Arquivos com constantes da aplicação, como estilos.
- `functions/`: Módulos que contêm a lógica de interação com o usuário para cada funcionalidade do menu (ex: `txt_to_pdf.py`).
- `modules/`: Módulos de baixo nível que encapsulam a lógica de negócio principal.
  - `pdf_generator.py`: O novo motor de geração de PDF, reutilizável e independente da UI.
  - `content_manager.py`: Funções para manipulação de conteúdo de texto.
  - `pdf_manager.py`: Funções para manipulação de arquivos PDF existentes (mesclar, editar, etc.).
- `fonts/`: Diretório para fontes personalizadas.

## Limitações
- **Edição de Páginas**: A edição de páginas do PDF usa o texto extraído do arquivo original. Isso significa que formatações complexas, fontes específicas ou elementos vetoriais do PDF original serão perdidos. A função gera um *novo* PDF a partir do conteúdo de texto.
- **WeasyPrint**: A conversão de HTML para PDF pode não renderizar CSS externo ou JavaScript. Para melhores resultados, use HTML autocontido.

## Contribuições
Sinta-se à vontade para abrir issues ou pull requests. Sugestões de melhorias:
- Suporte a diagramas Markdown (ex.: Mermaid).
- Exportação para outros formatos como DOCX ou ODT.
- Uma interface gráfica (GUI) com `tkinter` ou `PyQt`.

## Licença
MIT License. Desenvolvido por Borge Dev, 2025.
