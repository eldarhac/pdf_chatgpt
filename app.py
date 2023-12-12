from flask import Flask, render_template, request, send_file
from pdf_ama import translate_pdf
import os
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', message='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', message='No selected file')
        if file:
                        # Save the uploaded file to a temporary file
            temp_dir = tempfile.TemporaryDirectory()
            temp_path = os.path.join(temp_dir.name, file.filename)
            file.save(temp_path)

            translated_file_path = translate_pdf(temp_path)

            # Send the translated file to the user
            return_data = send_file(translated_file_path, as_attachment=True)

            # Clean up the temporary directory
            temp_dir.cleanup()

            return return_data
    return render_template('upload.html', message=None)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
