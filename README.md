
# BorgePDF Toolbox

**BorgePDF Toolbox** é uma ferramenta em Python para manipulação de arquivos, com foco na conversão de arquivos TXT (com formatação Markdown), imagens e HTML para PDF, além de mesclagem de PDFs e edição de texto no terminal. Desenvolvida para oferecer personalização avançada, a ferramenta suporta Markdown (títulos, listas, tabelas, notas de rodapé, imagens), exportação para HTML, sumário clicável, capas personalizadas, paginação configurável e muito mais. Ideal para desenvolvedores que desejam criar documentos profissionais a partir do terminal.

## Funcionalidades
- **Conversão de TXT para PDF**: Transforma arquivos TXT com formatação Markdown em PDFs, com suporte a títulos, listas, tabelas, notas de rodapé e imagens.
- **Conversão de Múltiplos TXTs**: Combina vários arquivos TXT em um único PDF.
- **Conversão de Imagens para PDF**: Converte uma ou várias imagens (.png, .jpg, .jpeg) em PDF.
- **Conversão de HTML para PDF**: Converte arquivos HTML com CSS inline em PDFs, preservando o design.
- **Mesclagem de PDFs**: Combina múltiplos PDFs em um único arquivo.
- **Informações de PDF**: Exibe detalhes como número de páginas e dimensões.
- **Edição de Texto**: Edita arquivos TXT ou páginas específicas do PDF no terminal.
- **Personalização**:
  - Margens, fontes (Helvetica, Times, Courier), tamanho de fonte, alinhamento, espaçamento entre linhas.
  - Temas (moderno, clássico, minimalista) com cores predefinidas.
  - Estilos de tabelas (simples, grade, listrado, personalizado com cores).
  - Paginação configurável (todas, ímpares, pares, a partir de uma página, nenhuma).
  - Capa personalizável com título, autor e data.
  - Sumário clicável no PDF e HTML.
- **Formatação de Palavras**: Destaca palavras-chave com negrito, sublinhado ou cores específicas.
- **Exportação para HTML**: Gera arquivos HTML com estilos CSS e sumário clicável.
- **Pré-visualização**: Visualiza conteúdo no terminal ou HTML no navegador antes de salvar.
- **Envio via Telegram**: Envia PDFs gerados diretamente para um chat do Telegram.
- **Configurações Salvas**: Armazena preferências em um arquivo JSON (`config_borgepdf.json`).

## Pré-requisitos
Instale as dependências necessárias:
```bash
pip install reportlab markdown prompt_toolkit pypdf pillow requests weasyprint
```

- **WeasyPrint**: Requer bibliotecas adicionais (ex.: GTK no Windows, `libpango` no Linux/Mac). Veja a [documentação do WeasyPrint](https://weasyprint.readthedocs.io/).
- **Configuração do Telegram**: Crie um arquivo `config.py` com:
  ```python
  CHAT_ID = "seu_chat_id"
  TELEGRAM_TOKEN = "seu_bot_token"
  ```
  Obtenha o token criando um bot com o [BotFather](https://t.me/BotFather) e o ID do chat onde deseja enviar os PDFs.

## Instalação
1. Clone o repositório ou baixe o script `borgepdf.py`.
2. Instale as dependências listadas acima.
3. Configure o arquivo `config.py` com as credenciais do Telegram.
4. Execute o script:
   ```bash
   python borgepdf.py
   ```

## Uso
1. Execute o script e escolha uma opção no menu:
   ```
   🧰 BorgePDF Toolbox – Dev Tools no Terminal 💼
   [1] Converter TXT para PDF com formatação Markdown
   [2] Converter Múltiplos TXTs para um PDF
   [3] Converter Imagens para PDF
   [4] Mesclar vários PDFs
   [5] Ver informações de um PDF
   [6] Editar texto no terminal
   [7] Converter HTML para PDF
   [0] Sair
   ```
2. Siga as instruções no terminal, que incluem:
   - Informar caminhos de arquivos ou pastas.
   - Configurar margens, fontes, alinhamento, estilos de tabelas, capa, etc.
   - Formatar palavras específicas (negrito, sublinhado, cor).
   - Visualizar conteúdo no terminal ou navegador.
   - Editar ou remover páginas do PDF.
   - Exportar para HTML ou enviar o PDF via Telegram.

## Formatos de Entrada Suportados
### Arquivos TXT (Markdown)
Os arquivos TXT devem usar a sintaxe Markdown para formatação. Exemplos de conteúdo suportado:
```markdown
# Título Principal
Texto com *itálico*, **negrito** e <font color="red">vermelho</font>[^1].

## Subtítulo
- Item não ordenado
  - Subitem
1. Item ordenado
2. Outro item

| Nome | Idade | Cidade |
|------|-------|--------|
| João | 25    | Lisboa |
| Ana  | 30    | Porto  |

![Imagem](caminho/imagem.png)

[^1]: Esta é uma nota de rodapé.
```

- **Títulos**: `# Título` (h1), `## Subtítulo` (h2).
- **Texto Formatado**: `*itálico*`, `**negrito**`, `<u>sublinhado</u>`, `<font color="red">cor</font>`.
- **Listas**:
  - Não ordenadas: `- Item` ou `* Item`.
  - Ordenadas: `1. Item`.
- **Tabelas**: `| Col1 | Col2 |` com cabeçalhos e linhas.
- **Imagens**: `![Imagem](caminho/imagem.png)` (suporta .png, .jpg, .jpeg).
- **Notas de Rodapé**: `[^1]` no texto e `[^1]: Texto da nota` no final.

### Arquivos de Imagem
- Formatos: `.png`, `.jpg`, `.jpeg`.
- Suporta conversão de uma ou várias imagens em um único PDF.

### Arquivos HTML
- Suporta HTML com CSS inline (ex.: `<p style="color: red;">Texto</p>`).
- Exemplo de arquivo HTML:
  ```html
  <html>
  <head>
      <style>
          body { font-family: Arial; margin: 20px; }
          h1 { color: navy; }
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid black; padding: 8px; }
      </style>
  </head>
  <body>
      <h1>Título Principal</h1>
      <p style="color: red;">Texto em vermelho.</p>
      <table>
          <tr><th>Nome</th><th>Idade</th></tr>
          <tr><td>João</td><td>25</td></tr>
      </table>
      <img src="caminho/imagem.png" alt="Imagem">
  </body>
  </html>
  ```

## Personalização
- **Margens**: Esquerda, direita, superior, inferior (em mm).
- **Fontes**: Helvetica, Times, Courier.
- **Tamanho da Fonte**: Personalizável (ex.: 12pt).
- **Alinhamento**: Esquerda, centro, justificado.
- **Espaçamento entre Linhas**: Ex.: 1.15, 1.5.
- **Temas**:
  - Moderno: Helvetica, cores escuras.
  - Clássico: Times, cores sóbrias.
  - Minimalista: Courier, cores neutras.
- **Tabelas**:
  - Estilos: Simples (cabeçalho cinza), Grade (borda preta), Listrado (linhas alternadas), Personalizado (cores de fundo e borda).
- **Paginação**: Todas, ímpares, pares, a partir de uma página, nenhuma.
- **Capa**: Título, autor, data personalizáveis.
- **Formatação de Palavras**: Negrito, sublinhado ou cor para palavras-chave em todo o documento.

## Exemplo de Interação
1. Escolha a opção 1 (TXT para PDF):
   ```
   📝 Caminho do arquivo .txt: documento.txt
   📄 Nome do PDF de saída: saida.pdf
   ⚙️ Usar configurações salvas? (s/n, padrão s): n
   📏 Margem esquerda (mm, padrão 40): 30
   📏 Margem direita (mm, padrão 40): 30
   📏 Margem superior (mm, padrão 50): 40
   📏 Margem inferior (mm, padrão 50): 40
   🖋️ Fonte (Helvetica/Times/Courier, padrão Helvetica): Times
   📏 Tamanho da fonte (padrão 12): 11
   📍 Alinhamento (esquerda/centro/justificado, padrão justificado): justificado
   📏 Espaçamento entre linhas (padrão 1.15): 1.2
   🎨 Tema (moderno/classico/minimalista, padrão moderno): classico
   📊 Estilo da tabela (simples/grade/listrado/personalizado, padrão simples): listrado
   📖 Título da capa (padrão Documento): Relatório
   ✍️ Autor da capa (padrão Autor): Borge
   📅 Data da capa (padrão 2025-07-13): 2025-07-13
   📄 Paginação (todas/impares/pares/a_partir_de/nenhuma, padrão todas): a_partir_de
   📄 A partir de qual página? (ex.: 1): 2
   📑 Incluir sumário clicável? (s/n, padrão s): s
   🔍 Deseja formatar palavras específicas? (s/n): s
   🔍 Palavra-chave a formatar: importante
   🎨 Formato (negrito/sublinhado/cor): cor
   🎨 Cor (ex.: red, #FF0000): #FF0000
   🔎 Deseja visualizar o conteúdo antes da conversão? (s/n): s
   📄 Visualização Prévia do Conteúdo (primeiros 500 caracteres):
   # Título Principal
   Texto com *itálico* e **negrito**[^1].
   ## Subtítulo
   - Item 1
     - Subitem 1.1
   - Item 2
   1. Item ordenado
   2. Outro item
   | Nome | Idade | Cidade |
   |------|-------|--------|
   | João | 25    | Lisboa |
   | Ana  | 30    | Porto  |
   ![Imagem](caminho/imagem.png)
   Palavra <font color="#FF0000">importante</font> para destacar.
   [^1]: Esta é uma nota de rodapé.
   ✅ Confirmar conversão? (s/n): s
   📝 Deseja editar o texto antes da conversão? (s/n): n
   📂 Exportar para HTML? (s/n): s
   ✅ HTML salvo como: saida.html
   🔎 Visualizar HTML no navegador? (s/n): s
   ✅ PDF temporário salvo como: temp_output.pdf
   📝 Deseja editar ou remover páginas? (s/n): s
   📄 Total de páginas: 3
   📄 Visualizar [t]odas, [u]ma página, [e]ditar página, [r]emover página, [s]air: s
   ✅ PDF final salvo como: saida.pdf
   📤 Enviar para Telegram? (s/n): n
   ```

2. Escolha a opção 7 (HTML para PDF):
   ```
   🌐 Caminho do arquivo .html: documento.html
   📄 Nome do PDF de saída: saida.pdf
   ✅ PDF salvo como: saida.pdf
   📤 Enviar para Telegram? (s/n): n
   ```

## Estrutura do Projeto
- `borgepdf.py`: Script principal com todas as funcionalidades.
- `config.py`: Arquivo de configuração para Telegram (`CHAT_ID` e `TELEGRAM_TOKEN`).
- `config_borgepdf.json`: Arquivo gerado automaticamente para salvar configurações (margens, fontes, etc.).

## Limitações
- **WeasyPrint**: Pode não renderizar CSS externo ou JavaScript dinâmico. Use CSS inline para melhores resultados.
- **Imagens**: Devem estar acessíveis no caminho especificado no Markdown ou HTML.
- **Edição de Páginas**: A edição de páginas do PDF usa texto extraído, que pode perder alguma formatação complexa.

## Contribuições
Sinta-se à vontade para abrir issues ou pull requests no repositório. Sugestões de melhorias:
- Suporte a diagramas Markdown (ex.: Mermaid).
- Exportação para DOCX ou ODT.
- Interface gráfica com `tkinter`.

## Licença
MIT License. Desenvolvido por Borge Dev, 2025.
