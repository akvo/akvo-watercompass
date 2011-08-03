# -*- coding: utf-8 -*-

import subprocess
import os

def create_PDF_selected_techs(URL):


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
    
    return {p}