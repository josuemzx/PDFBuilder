from flask import Flask, request, send_file, render_template
import os, tempfile, shutil, subprocess
from PyPDF2 import PdfMerger

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    # 1) Carpeta temporal
    workdir = tempfile.mkdtemp()
    try:
        # 2) Guardar uploads
        files = request.files.getlist('file')
        pdfs = []
        for f in files:
            filename = f.filename
            path = os.path.join(workdir, filename)
            f.save(path)
            # 3) Si es .doc/.docx => LibreOffice headless
            if path.lower().endswith(('.doc','.docx')):
                subprocess.run([
                    'soffice', '--headless',
                    '--convert-to', 'pdf',
                    path,
                    '--outdir', workdir
                ], check=True)
                pdfs.append(path.rsplit('.',1)[0] + '.pdf')
            elif path.lower().endswith('.pdf'):
                pdfs.append(path)

        # 4) Fusionar
        merger = PdfMerger()
        for pdf in pdfs:
            merger.append(pdf)
        out_path = os.path.join(workdir, 'expediente_unificado.pdf')
        merger.write(out_path)
        merger.close()

        # 5) Devolver
        return send_file(out_path, as_attachment=True)
    finally:
        # 6) Limpiar
        shutil.rmtree(workdir, ignore_errors=True)

if __name__=='__main__':
    app.run()
