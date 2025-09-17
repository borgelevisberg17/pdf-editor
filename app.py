import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from functions.txt_to_pdf import convert_text_to_pdf
from functions.imagem_to_pdf import imagem_para_pdf
from functions.html_to_pdf import html_para_pdf
from modules.pdf_manager import mesclar_pdfs
from modules.pdf_generator import PdfGenerator
from configs.config_manager import carregar_config

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'supersecretkey'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/txt-to-pdf', methods=['POST'])
def txt_to_pdf_route():
    if 'txt_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('txt_files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    config = carregar_config()
    text_blocks = []
    for path in filepaths:
        with open(path, 'r', encoding='utf-8') as f:
            text_blocks.append(f.read())

    if convert_text_to_pdf(text_blocks, output_name, config):
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error converting text to PDF')
        return redirect(url_for('index'))

@app.route('/image-to-pdf', methods=['POST'])
def image_to_pdf_route():
    if 'image_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('image_files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    if imagem_para_pdf(filepaths, output_name):
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error converting images to PDF')
        return redirect(url_for('index'))

@app.route('/html-to-pdf', methods=['POST'])
def html_to_pdf_route():
    if 'html_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['html_file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    if html_para_pdf(filepath, output_name):
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error converting HTML to PDF')
        return redirect(url_for('index'))

@app.route('/merge-pdfs', methods=['POST'])
def merge_pdfs_route():
    if 'pdf_files' not in request.files:
        flash('No file part')
        return redirect(request.url)
    files = request.files.getlist('pdf_files')
    if not files or files[0].filename == '':
        flash('No selected file')
        return redirect(request.url)

    output_name = request.form['output_name']
    if not output_name:
        output_name = "output.pdf"
    if not output_name.endswith('.pdf'):
        output_name += '.pdf'

    filepaths = []
    for file in files:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        filepaths.append(filepath)

    if mesclar_pdfs(filepaths, output_name):
        return send_file(output_name, as_attachment=True)
    else:
        flash('Error merging PDFs')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
