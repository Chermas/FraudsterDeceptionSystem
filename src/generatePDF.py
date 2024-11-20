import string
import random
import io
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize
from reportlab.lib.utils import simpleSplit
import datetime
from pikepdf import Pdf, Page, Encryption
import uuid
import honeytoken_service as honeytoken
import openai_service as openai

address = os.environ.get('API_URL')

def update_url(token, name):
    path='templates/template.pdf'
    pdf = Pdf.open(path)
    Page(pdf.pages[0]).obj['/AA']['/O']['/URI'] = address + '/' + token
    pdf.save('/tmp/' + name + '.pdf')
    

def insert_text(name,context,title,subTitle, section):
   
    response = openai.fill_pdf(context)
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet)
    PAGE_WIDTH  = defaultPageSize[0]
    PAGE_HEIGHT = defaultPageSize[1]
    text_width = stringWidth(title,"Helvetica-Bold",28)
    
    can.setFillColorRGB(255,255,255)
    can.setFont("Helvetica-Bold",28)
    can.drawString((PAGE_WIDTH - text_width) / 2.0, 745, title)
    can.setFont("Helvetica-Oblique",22)
    text_width = stringWidth(subTitle,"Helvetica-Oblique",22)
    can.drawString((PAGE_WIDTH - text_width) / 2.0, 690, subTitle)

    can.setFillColorRGB(0,0,0)
    can.setFont("Helvetica-Bold",18)
    can.drawString(40, 615, section)

    can.line(40,605,PAGE_WIDTH-40,605)

    can.setFont("Helvetica",12)

    L = simpleSplit(response,can._fontname,can._fontsize,PAGE_WIDTH-80)
    x= 40
    y=580
    for t in L:
        can.drawString(x,y,t)
        y -= can._leading

    can.save()
    packet.seek(0)

    token_pdf = Pdf.open('/tmp/'+name+'.pdf',allow_overwriting_input=True)
    text_pdf = Pdf.open(packet)
    token_pdf_page = Page(token_pdf.pages[0])
    text_pdf_page = Page(text_pdf.pages[0])

    token_pdf_page.add_overlay(text_pdf_page)

    token_pdf.save()

def update_metadata(name):
   pdf = Pdf.open('/tmp/'+name+'.pdf',allow_overwriting_input=True)

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

def generate_pdf(context,title,subtitle,section):
    name = openai.generate_pdf_name(context)
    if name == None:
        name = 'info'
    token = honeytoken.generate_token()
    update_url(token, name)
    insert_text(name,context,title,subtitle,section)
    update_metadata(name)
    return '/tmp/'+ name +'.pdf'
