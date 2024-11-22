import generatePDF as pdf
import uuid

def generate_token():
    return uuid.uuid4().hex

def generate_pdf_with_url(context, title, subtitle, section):
    pass

def generate_pdf(body, title='Information', subtitle='info', section='info'):
    token = generate_token()
    path = pdf.generate_pdf(token, body, title, subtitle, section)
    return token, path

def generate_url():
    pass