import os
import uuid
import tempfile
import shutil
import subprocess
import json
from flask import Flask, request, jsonify, send_file, render_template
from PyPDF2 import PdfMerger

app = Flask(__name__)

# Carpeta base para temporales
temp_base = tempfile.gettempdir()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Crear carpeta temporal para esta sesión
    session_id = str(uuid.uuid4())
    workdir = os.path.join(temp_base, f"pdfbldr_{session_id}")
    os.makedirs(workdir, exist_ok=True)
    pdfs = []

    for f in request.files.getlist('file'):
        filename = f.filename
        src = os.path.join(workdir, filename)
        f.save(src)
        # Convertir .doc/.docx a PDF
        if src.lower().endswith(('.docx', '.doc')):
            subprocess.run([
                'soffice', '--headless',
                '--convert-to', 'pdf', src,
                '--outdir', workdir
            ], check=True)
            pdf_name = os.path.splitext(filename)[0] + '.pdf'
            pdfs.append(pdf_name)
        # Incluir PDF directamente
        elif src.lower().endswith('.pdf'):
            pdfs.append(filename)

    return jsonify({'session_id': session_id, 'files': pdfs})

@app.route('/merge', methods=['POST'])
def merge():
    data = request.get_json()
    session_id = data.get('session_id')
    order = data.get('order', [])
    workdir = os.path.join(temp_base, f"pdfbldr_{session_id}")

    merger = PdfMerger()
    for name in order:
        path = os.path.join(workdir, name)
        merger.append(path)
    output_path = os.path.join(workdir, 'expediente_unificado.pdf')
    merger.write(output_path)
    merger.close()

    # Enviar y limpiar
    result = send_file(output_path, as_attachment=True, download_name='expediente_unificado.pdf')
    shutil.rmtree(workdir, ignore_errors=True)
    return result

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)