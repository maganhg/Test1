import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['pdf', 'xml'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                    pdf_files[base_filename] = file  # Guarda el archivo en lugar del nombre de archivo
                elif extension == '.xml':
                    xml_files[base_filename] = file  # Guarda el archivo en lugar del nombre de archivo

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

        # Check for filename length (if needed)
        # ...

        # Send files by email
        send_files_by_email(pdf_files, xml_files)

        flash('File(s) successfully sent via email')
        return redirect('/')

def send_files_by_email(pdf_files, xml_files):
    # Email configuration
    EMAIL_ADDRESS = "---"  
    EMAIL_PASSWORD = "---"  
    EMAIL_TO = "---"  

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_TO
    msg['Subject'] = 'Archivos Adjuntos'

    # Cuerpo del correo
    body = 'Archivos adjuntos desde la aplicación Flask:'
    msg.attach(MIMEText(body, 'plain'))

    # Adjunta los archivos a enviar
    for pdf_base, pdf_file in pdf_files.items():
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_file.read())  # Lee el contenido del archivo
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {pdf_base}.pdf")  # Cambia el nombre del archivo si es necesario
        msg.attach(part)

    for xml_base, xml_file in xml_files.items():
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(xml_file.read())  # Lee el contenido del archivo
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {xml_base}.xml")  # Cambia el nombre del archivo si es necesario
        msg.attach(part)

    # Establece la conexión al servidor SMTP y envía el correo
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, EMAIL_TO, text)
        server.quit()
    except Exception as e:
        flash(f'Error sending email: {str(e)}')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
