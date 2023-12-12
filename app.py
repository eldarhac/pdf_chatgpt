from flask import Flask, render_template, request, send_file
from pdf_ama import translate_pdf
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', message='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message='No selected file')
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            translated_file = translate_pdf(file_path)

            return send_file(translated_file, as_attachment=True)
    return render_template('upload.html', message=None)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
