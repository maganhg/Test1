import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['pdf', 'xml'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def has_matching_xml(pdf_filename):
    xml_filename = pdf_filename.rsplit('.', 1)[0] + '.xml'
    return os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], xml_filename))

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        pdf_files = {}
        xml_files = {}

        for file in request.files.getlist('files[]'):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                base_filename, extension = os.path.splitext(filename)

                if extension == '.pdf':
                    pdf_files[base_filename] = filename
                elif extension == '.xml':
                    xml_files[base_filename] = filename

        # Check if there's a matching XML file for each PDF file
        if len(pdf_files) != len(xml_files):
            flash('Unequal number of PDF and XML files')
            return redirect(request.url)

        # Check for matching PDF and XML files
        for pdf_base in pdf_files:
            if pdf_base not in xml_files:
                flash(f'No matching XML file found for {pdf_base}.pdf')
                return redirect(request.url)

        for xml_base in xml_files:
            if xml_base not in pdf_files:
                flash(f'No matching PDF file found for {xml_base}.xml')
                return redirect(request.url)

        # Check for filename length
        for filename in pdf_files.values():
            if len(filename) > 34:
                flash('Filename too long (max 34 characters)')
                return redirect(request.url)

        for filename in xml_files.values():
            if len(filename) > 34:
                flash('Filename too long (max 34 characters)')
                return redirect(request.url)

        # Files meet all requirements, save them
        for file in request.files.getlist('files[]'):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash('File(s) successfully uploaded')
        return redirect('/')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
