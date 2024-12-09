import random
import io
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize
from reportlab.lib.utils import simpleSplit
from reportlab.lib.colors import blue
import datetime
from pikepdf import Pdf, Page, Encryption
import uuid
import honeytoken_service as honeytoken
import openai_service as openai
import dotenv

dotenv.load_dotenv()

address = os.getenv('API_URL')

client = openai.OpenAIClient()


def update_url(token, name):
    path='templates/template.pdf'
    pdf = Pdf.open(path)
    Page(pdf.pages[0]).obj['/AA']['/O']['/URI'] = address + '/' + token

    # Save the modified PDF
    pdf.save('../pdf_files/' + name + '.pdf')

def insert_text(name, body, title, subTitle, section, token):
    response = client.fill_pdf(body)
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    PAGE_WIDTH = defaultPageSize[0]
    PAGE_HEIGHT = defaultPageSize[1]

    # Title
    text_width = stringWidth(title, "Helvetica-Bold", 28)
    can.setFillColorRGB(255, 255, 255)
    can.setFont("Helvetica-Bold", 28)
    can.drawString((PAGE_WIDTH - text_width) / 2.0, 745, title)

    # Subtitle
    can.setFont("Helvetica-Oblique", 22)
    text_width = stringWidth(subTitle, "Helvetica-Oblique", 22)
    can.drawString((PAGE_WIDTH - text_width) / 2.0, 690, subTitle)

    # Section Header
    can.setFillColorRGB(0, 0, 0)
    can.setFont("Helvetica-Bold", 18)
    can.drawString(40, 615, section)

    # Section Divider Line
    can.line(40, 605, PAGE_WIDTH - 40, 605)

    # Body Text
    can.setFont("Helvetica", 12)
    L = simpleSplit(response, can._fontname, can._fontsize, PAGE_WIDTH - 80)
    x = 40
    y = 580
    for t in L:
        can.drawString(x, y, t)
        y -= can._leading

    # Finalize the canvas
    can.save()
    packet.seek(0)

    # Overlay the new content onto the PDF
    token_pdf = Pdf.open('../pdf_files/' + name + '.pdf', allow_overwriting_input=True)
    text_pdf = Pdf.open(packet)
    token_pdf_page = Page(token_pdf.pages[0])
    text_pdf_page = Page(text_pdf.pages[0])

    token_pdf_page.add_overlay(text_pdf_page)
    token_pdf.save()

def update_metadata(name):
   pdf = Pdf.open('../pdf_files/'+name+'.pdf',allow_overwriting_input=True)

   with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
    meta['pdf:Producer'] ='Adobe PDF Library 23.1.96'
    meta['xmp:CreatorTool'] = 'Acrobat PDFMaker 23 for Word'  
    meta['xmp:ModifyDate'] = get_mod_date()
    meta['xmp:CreateDate'] = get_creation_date()
    meta['xmp:MetadataDate'] = get_mod_date()
    meta['xmpMM:DocumentID'] = str(uuid.uuid4())
    meta['xmpMM:InstanceID'] = str(uuid.uuid4())
    
    pdf.save(encryption=Encryption(''))

def get_creation_date():
    time = datetime.datetime.now()
    rand_region =str(random.randint(1, 3))
    stamp = time.strftime('%Y-%m-%d')+'T'+time.strftime('%H:%M:%S')+ '+0'+ rand_region + ':00'
    return stamp

def get_mod_date():
    time = datetime.datetime.now()
    stamp = time.strftime('%Y-%m-%d')+'T'+time.strftime('%H:%M:%S')
    return stamp

def generate_pdf(token, body, title, subtitle, section):
    name = client.generate_pdf_name(body)
    if name == None:
        name = 'info'
    update_url(token, name)
    insert_text(name,body,title,subtitle,section,token)
    update_metadata(name)
    return '../pdf_files/'+ name +'.pdf'
