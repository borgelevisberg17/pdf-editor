# BorgePDF

O **BorgePDF** é uma aplicação web para organizar, converter e manipular arquivos PDF com uma experiência simples, visual e rápida. A nova interface transforma os fluxos que antes estavam espalhados entre CLI e formulários básicos em um workspace único, responsivo e orientado a tarefas.

## O que já está disponível

A página inicial apresenta as ferramentas em cards e abre um fluxo de upload com drag-and-drop, validação de formato, lista de arquivos selecionados, campos contextuais e download automático do resultado. Os fluxos implementados são:

| Ferramenta | Endpoint | Resultado |
| --- | --- | --- |
| Mesclar PDF | `POST /merge-pdfs` | Combina dois ou mais PDFs na ordem selecionada. |
| Comprimir PDF | `POST /compress-pdf` | Reescreve e compacta streams de conteúdo sem alterar as páginas. |
| Dividir PDF | `POST /split-pdf` | Extrai páginas com especificações como `1,3-5`, `odd` ou `even`. |
| Girar PDF | `POST /rotate-pdf` | Gira todas ou páginas específicas em 90, 180 ou 270 graus. |
| Remover páginas | `POST /delete-pages` | Remove páginas selecionadas sem permitir um PDF vazio. |
| Organizar páginas | `POST /reorder-pages` | Reordena todas as páginas exatamente uma vez. |
| Imagem para PDF | `POST /image-to-pdf` | Converte imagens PNG, JPG, JPEG ou WEBP em PDF. |
| Texto para PDF | `POST /txt-to-pdf` | Converte TXT e Markdown para PDF com o motor existente. |
| HTML para PDF | `POST /html-to-pdf` | Renderiza arquivos HTML usando WeasyPrint. |
| Informações do PDF | `POST /pdf-info` | Exibe quantidade de páginas e tamanho do arquivo. |

A autenticação, os planos e o painel administrativo existentes foram preservados, mas as páginas de login e cadastro receberam a mesma linguagem visual da home. O plano gratuito continua disponível para uso básico e a conversão com LaTeX permanece protegida pelo plano premium.

## Instalação e execução

O projeto usa Python 3.10+ e Flask. Para executar localmente:

```bash
git clone https://github.com/borgelevisberg17/pdf-editor.git
cd pdf-editor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Depois, acesse `http://127.0.0.1:5000`. O limite padrão de upload é de 50 MB por request e pode ser ajustado em `app.py` por meio de `MAX_CONTENT_LENGTH`.

## Arquitetura

A camada Flask em `app.py` concentra autenticação, rotas, limites e entrega de arquivos. As operações estruturais de PDF foram isoladas em `modules/pdf_operations.py`, com validação explícita de páginas e erros amigáveis. Os conversores legados em `functions/` continuam sendo utilizados para TXT, imagens e HTML, enquanto `modules/pdf_generator.py` permanece responsável pela geração formatada de documentos de texto.

Uploads são gravados com nomes aleatórios em `uploads/` e removidos após o request. Resultados são criados em `generated/` e removidos depois do download. Esses diretórios, assim como o banco SQLite local, estão protegidos no `.gitignore`.

## Validação

O repositório inclui um smoke test local em `tests/smoke_app.py`, ignorado por padrão pelo projeto original, que verifica importação do app, renderização da home, parsing de páginas, mesclagem, divisão, rotação, remoção, reordenação, compressão e conversão TXT para PDF.

```bash
python3 -m py_compile app.py modules/pdf_operations.py configs/config_manager.py
python3 tests/smoke_app.py
```

## Próximas evoluções sugeridas

As próximas etapas naturais são adicionar compressão por perfil de qualidade com ferramentas nativas do sistema, preview de miniaturas no navegador, edição visual de texto sobre a página, assinatura digital, OCR e uma fila assíncrona para arquivos maiores. A estrutura atual deixa esses recursos isolados dos fluxos já entregues.

## Licença

MIT License. Desenvolvido por Borge Dev.
