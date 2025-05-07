import os
import uuid
import shutil
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
import subprocess

UPLOAD_DIR = '/tmp/pdfbuilder'

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('file')
    if not files:
        return jsonify(error='No files uploaded'), 400

    session_id = str(uuid.uuid4())
    sess_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(sess_dir, exist_ok=True)

    pdf_names = []
    for f in files:
        filename = secure_filename(f.filename)
        src_path = os.path.join(sess_dir, filename)
        f.save(src_path)

        # Convertir DOC/DOCX a PDF con LibreOffice
        if filename.lower().endswith(('.doc', '.docx')):
            dest_path = os.path.splitext(src_path)[0] + '.pdf'
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', sess_dir,
                src_path
            ]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                shutil.rmtree(sess_dir)
                return jsonify(error=f'Error converting {filename}'), 500
            pdf_names.append(os.path.basename(dest_path))
        elif filename.lower().endswith('.pdf'):
            pdf_names.append(filename)
        else:
            continue

    return jsonify(session_id=session_id, files=pdf_names)

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    data = request.get_json()
    session_id = data.get('session_id')
    order = data.get('order', [])
    if not session_id or not order:
        return jsonify(error='Invalid merge parameters'), 400

    sess_dir = os.path.join(UPLOAD_DIR, session_id)
    if not os.path.isdir(sess_dir):
        return abort(404)

    merger = PdfMerger()
    for name in order:
        path = os.path.join(sess_dir, secure_filename(name))
        if os.path.isfile(path):
            merger.append(path)
    output_path = os.path.join(sess_dir, 'expediente_unificado.pdf')
    merger.write(output_path)
    merger.close()

    # Enviar y limpiar
    response = send_file(output_path, as_attachment=True, download_name='expediente_unificado.pdf')
    # Limpiar sesión
    shutil.rmtree(sess_dir)
    return response

@app.errorhandler(500)
def server_error(e):
    return jsonify(error=str(e)), 500

if __name__ == '__main__':
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)