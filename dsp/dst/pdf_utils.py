# -*- coding: utf-8 -*-

import subprocess
import os
import time
import datetime
import logging

from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import cm, inch
from reportlab.platypus.flowables import Spacer, HRFlowable, PageBreak
from reportlab.lib import colors


def create_PDF_akvopedia(URL):
    
    URL_list=URL.split("/")
    article_name=URL_list[-1]
    tmp_dir=os.path.dirname(__file__)+'/tmp_pdf/'
    
    args=[]
    args.append('mw-render')
    args.append('--config=http://www.akvo.org/wiki/')
    args.append("--username=marktielewestra")
    args.append("--password=Westra123")
    args.append('--output='+tmp_dir+article_name+'.pdf')
    args.append('--writer=rl')
    args.append('--imagesize=300')
    
    args.append(article_name)
    
    p = subprocess.Popen(args)
    return p


def create_PDF_selected_techs(all_chosen_techs,zipped_answerlist,incl_selected,incl_short_expl):
    Intro = """Results of the Sanitation Decision Support Tool. The tool was created by WASTE (www.waste.nl) and the Akvo Foundation (www.akvo.org), in order to assist people in choosing sanitation technologies. We hope this tool proves useful, any comments can be send to m.t.westra@akvo.org."""
    tmp_dir=os.path.dirname(__file__)+'/tmp_pdf/'   
    PAGE_HEIGHT=defaultPageSize[1]
    PAGE_WIDTH=defaultPageSize[0]
    
    today=datetime.datetime.today()
    
    format_date = "%a %b %d, %Y"
    format_time = "%H:%M:%S"
    s_date=today.strftime(format_date)
    s_time=today.strftime(format_time)
    
    Title = "The Sanitation Decision Support tool"
    Author = "Akvo"
    URL = "www.akvopedia.org"

    pageinfo = "%s —- %s -- %s" % (Title, Author, URL )
    
    # definition of first page #############################
    def myFirstPage(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold',18)
        canvas.drawString(2.54*cm, PAGE_HEIGHT-2.5*cm, Title)
        
        THIS_PATH=os.path.dirname(__file__)
        (HOME,HERE)=os.path.split(THIS_PATH)
        MEDIA_PATH=HOME+'/mediaroot/img/logos/'
        pic1=os.path.join(MEDIA_PATH,'akvo_logo_white.png')
        canvas.drawImage(pic1,16*cm, 26*cm)
        
        LEADING=0.5*cm
        canvas.setFont('Helvetica',9)
        canvas.drawString(15*cm, PAGE_HEIGHT-5*cm, "Session information")
        canvas.drawString(15*cm, PAGE_HEIGHT-5*cm-LEADING, "Date:  %s" % (s_date))
        canvas.drawString(15*cm, PAGE_HEIGHT-5*cm-2*LEADING, "Time:  %s" % (s_time))
        
        COLUMN_HEIGHT=7*cm
        BOTTOM_OPTIONS=12*cm
 
        f1=Frame(2*cm,BOTTOM_OPTIONS,5*cm,2*cm+COLUMN_HEIGHT,showBoundary=0)
        f2=Frame(8*cm,BOTTOM_OPTIONS,5*cm,2*cm+COLUMN_HEIGHT,showBoundary=0)
        f3=Frame(14*cm,BOTTOM_OPTIONS,5*cm,2*cm+COLUMN_HEIGHT,showBoundary=0)
        
        canvas.setStrokeColorRGB(0.5,0.5,0.5)
        canvas.rect(2*cm,BOTTOM_OPTIONS,17*cm,2*cm+COLUMN_HEIGHT,stroke=1, fill=0)
        canvas.setStrokeColorRGB(0,0,0)
        
        options1=[]
        options2=[]
        options3=[]
        
        styles=getSampleStyleSheet()
        styleN=styles["Normal"]
        
        column=1
        factor_num=0
        
        for factor, change, criterion, applicable in zipped_answerlist:
            if change:
                factor_num+=1
            
            if factor_num in [1,2,3]:
                column=1
            else:
                if factor_num in [4,5,6]:
                    column=2
                else:
                    column=3            
            
            if column==1:
                if change:
                    options1.append(Spacer(0,0.5*cm))
                    options1.append(Paragraph('<b>'+factor.factor+'</b>',styleN))     
                if applicable:
                    options1.append(Paragraph("&nbsp;&nbsp;&bull; <u><b>"+criterion.criterion+"</b></u>",styleN))
                else:
                    options1.append(Paragraph("&nbsp;&nbsp;&bull; "+criterion.criterion,styleN))
            
            if column==2:
                if change:
                    options2.append(Spacer(0,0.5*cm))
                    options2.append(Paragraph('<b>'+factor.factor+'</b>',styleN))    
                if applicable:
                    options2.append(Paragraph("&nbsp;&nbsp;&bull; <u><b>"+criterion.criterion+"</b></u>",styleN))
                else:
                    options2.append(Paragraph("&nbsp;&nbsp;&bull; "+criterion.criterion,styleN))
            
            if column==3:
                if change:
                    options3.append(Spacer(0,0.5*cm))
                    options3.append(Paragraph('<b>'+factor.factor+'</b>',styleN))    
                if applicable:
                    options3.append(Paragraph("&nbsp;&nbsp;&bull; <u><b>"+criterion.criterion+"</b></u>",styleN))
                else:
                    options3.append(Paragraph("&nbsp;&nbsp;&bull; "+criterion.criterion,styleN))

        f1.addFromList(options1,canvas)
        f2.addFromList(options2,canvas)
        f3.addFromList(options3,canvas)
      
        # draw box selected techologies
        
        canvas.setFillColorRGB(1,1,1)
        
        def draw_arrow(canvas,x,y):
            canvas.saveState()
            canvas.setStrokeColorRGB(0.5,0.5,0.5)
            canvas.setFillColorRGB(0.5,0.5,0.5)
            U=0.2*cm
            p=canvas.beginPath()
            p.moveTo(x,y)
            p.lineTo(x+U,y+2*U)
            p.lineTo(x,y+4*U)
            p.lineTo(x+2*U,y+2*U)
            p.lineTo(x,y)
            canvas.drawPath(p,stroke=0,fill=1)
            canvas.restoreState()
        
        BOX_LOC_X=1.5*cm
        BOX_MARG_BOT=5.0*cm
        BOX_WIDTH=2.5*cm
        BOX_HEIGHT=4.5*cm
        BOX_DELTA=0.7*cm
        num_arrows=0
        
        if incl_selected:
            THIS_PATH=os.path.dirname(__file__)
            (HOME,HERE)=os.path.split(THIS_PATH)
            MEDIA_PATH=HOME+'/mediaroot/techs_white/'
    
            styles.add(ParagraphStyle(name='smallfont', fontName='Helvetica',fontSize=8))
            smallfont=styles["smallfont"]

            for group, tech, relevance in all_chosen_techs:
                canvas.rect(BOX_LOC_X,BOX_MARG_BOT,BOX_WIDTH,BOX_HEIGHT,stroke=1, fill=1)
                if num_arrows<=4:
                    draw_arrow(canvas,BOX_LOC_X+BOX_WIDTH+0.2*cm,BOX_MARG_BOT+0.4*BOX_HEIGHT)
                    num_arrows+=1
            
                if not tech=='':
                    (path,pic)=os.path.split(tech.image)
                    pic1=os.path.join(MEDIA_PATH,pic)
                    canvas.drawImage(pic1,BOX_LOC_X+0.25*cm, BOX_MARG_BOT+2.4*cm,2.0*cm,2.0*cm)
                    f=Frame(BOX_LOC_X,BOX_MARG_BOT,BOX_WIDTH,BOX_HEIGHT-2.3*cm,showBoundary=0)
                    p=[]
                    p.append(Paragraph(tech.name,smallfont))
                    f.addFromList(p,canvas)
                
                BOX_LOC_X+=BOX_WIDTH+BOX_DELTA    
                
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
        canvas.restoreState()
    
    # definition of later pages ######################
    def myLaterPages(canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman',9)
        canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
        canvas.restoreState()
    
    def go():
        Elements.insert(0,Spacer(0,1*cm))
        doc = SimpleDocTemplate(tmp_dir+'page1.pdf')
        doc.build(Elements,onFirstPage=myFirstPage, onLaterPages=myLaterPages)
        
    Elements = []

    styles = getSampleStyleSheet()
    
    HeaderStyle = styles["Heading1"]
    ParaStyle = styles["Normal"]
    
    ParagraphStyle(name="Heading1", spaceAfter=0)
    
    styles.add(ParagraphStyle(name='NarrowPara', rightIndent=5*cm))
    NarrowStyle=styles["NarrowPara"]
    
    def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.3):
        s = Spacer(0.2*inch, sep*inch)
        Elements.append(s)
        para = klass(txt, style)
        Elements.append(para)
    
    def p(txt):
        return header(txt, style=ParaStyle, sep=0.1)
        
    def p_narrow(txt):
        return header(txt, style=NarrowStyle, sep=0.1)

# start of document content
    p_narrow(Intro)
    
    header("Options chosen")
    
    # selected technologies are drawn in first page definition
    if incl_selected:
        header("Selected technologies",sep=4)
    
    Elements.append(PageBreak())
    
    # Link to Akvopedia articles
    header("Links to Akvopedia articles")
    
    for group, tech, relevance in all_chosen_techs:
        if not tech=='':
            t_name=tech.name
            t_link=tech.url
            string="&nbsp;&nbsp;&nbsp;&bull; %s:<br/>&nbsp;&nbsp;&nbsp;&nbsp; %s" % (tech.name, tech.url)
            p(string)
    
    
    if incl_short_expl:
        header("Short descriptions")
    
        styles.add(ParagraphStyle(name='tech_header', fontName='Helvetica',fontSize=14))
        tech_header=styles["tech_header"]
    
        styles.add(ParagraphStyle(name='indent_left', fontName='Helvetica',leftIndent=4*cm))
        indent_left=styles["indent_left"]
    
        THIS_PATH=os.path.dirname(__file__)
        (HOME,HERE)=os.path.split(THIS_PATH)
        MEDIA_PATH=HOME+'/mediaroot/techs_white/'
        
        for group, tech, relevance_objects in all_chosen_techs:
             if not tech=='':
                header("<b>"+tech.name+"</b>",tech_header,sep=0.0 )
            
                header(tech.description,indent_left)
                (path,pic)=os.path.split(tech.image)
                pic1=os.path.join(MEDIA_PATH,pic)
                image_url="""<img src="%s">""" %(pic1)
                p(image_url)
            
                p("<b>Relevant options</b>")
                if len(relevance_objects)!=0:
                    for relevance_object in relevance_objects:
                        p("At option <strong>"+relevance_object.criterion.factor.factor+"</strong> you have selected <strong>"+relevance_object.criterion.criterion+"</strong>. This means that in your situation,"+ tech.name+" might be a suitable technology. This depends on: <strong>"+relevance_object.note.note+"</strong><br/>")       
            
                Elements.append(Spacer(0,0.3*cm))
                Elements.append(HRFlowable(width='100%', hAlign='LEFT', thickness=1, spaceBefore=0, spaceAfter=10, color=colors.grey))
                Elements.append(Spacer(0,0.3*cm))
    go()
    
    return 
