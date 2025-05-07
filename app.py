import os
import tempfile
import shutil
import subprocess
from flask import Flask, request, send_file, render_template
from PyPDF2 import PdfMerger

app = Flask(__name__)

@app.route('/')
def index():
    # Página principal con formulario de subida
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # Crear carpeta temporal única
    workdir = tempfile.mkdtemp(prefix='pdfbldr_')
    try:
        uploaded = request.files.getlist('file')
        pdfs = []
        for f in uploaded:
            filename = f.filename
            path = os.path.join(workdir, filename)
            f.save(path)
            # Si es Word, convertir a PDF con LibreOffice
            if path.lower().endswith(('.docx', '.doc')):
                subprocess.run([
                    'soffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    path,
                    '--outdir', workdir
                ], check=True)
                pdfs.append(os.path.splitext(path)[0] + '.pdf')
            # Si ya es PDF, añadir directamente
            elif path.lower().endswith('.pdf'):
                pdfs.append(path)

        # Fusionar PDFs con PyPDF2
        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        output_path = os.path.join(workdir, 'expediente_unificado.pdf')
        merger.write(output_path)
        merger.close()

        # Enviar el PDF unificado al cliente
        return send_file(output_path, as_attachment=True)

    finally:
        # Limpiar la carpeta temporal
        shutil.rmtree(workdir, ignore_errors=True)

if __name__ == '__main__':
    # Determinar puerto de escucha desde la variable de entorno
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)