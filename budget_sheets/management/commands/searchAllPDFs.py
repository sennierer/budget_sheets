#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from budget_sheets.models import PdfsBudget,CmdSearchPDFs,CmdSearchPDFsHits
from django.contrib.auth.models import User
from django.core.mail import send_mail
import logging
import json
#from budget_sheets.py_find_pdfs import downl_pdfs
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import hashlib
import subprocess
from kitchen.text.converters import to_unicode, to_bytes
import re
from django.db.models import Q
from bath.settings import BASE_DIR
import datetime


class Command(BaseCommand):
   

    def handle(self, *args, **options):
        b_dir = os.path.join(BASE_DIR,'search_tmp')
        logging.basicConfig(format='%(asctime)s %(message)s',filename=os.path.join(b_dir,'logs/',datetime.datetime.now().strftime("%H:%M_%d-%m-%Y")+'.log'),level=logging.DEBUG)
        searches = CmdSearchPDFs.objects.filter(progress__lt=1.0)
        if searches.count() == 0:
            sys.exit('No searches to execute')
        try:
            Y_start = min(int(s.Y_start) for s in searches)
        except:
            logging.info('No start year found.')
            Y_start = False
        try:
            Y_end = max(int(s.Y_end) for s in searches)
        except:
            logging.info('No end year found.')
            Y_end = False
    
        #print('use startyear %s and endyear %s'%(Y_start,Y_end))
        
        if Y_end and Y_start:
            if Y_end == Y_start:
                pdf_files = PdfsBudget.objects.filter(year=Y_start)
            else:
                pdf_files = PdfsBudget.objects.filter(year__gte=Y_start).filter(year__lte=Y_end)
        elif Y_end:
            pdf_files = PdfsBudget.objects.filter(year__lte=Y_end)
        elif Y_start:
            pdf_files = PdfsBudget.objects.filter(year__gte=Y_start)
        else:
            pdf_files = PdfsBudget.objects.all()
        nmb = pdf_files.count()
        emailUser = dict()
        for ind,pdf in enumerate(pdf_files):
            path = hashlib.md5(to_bytes(pdf.file_name)).hexdigest()
            if pdf.downloaded:
                try:
                    subprocess.call(['pdf2txt.py','-o',b_dir+'/txt/'+path,'-t','text',os.path.join(BASE_DIR,'pdfs_download/')+pdf.file_name])
                except:
                    logging.warning('Something went wrong: %s'%(pdf.file_name,))
                    continue
            else:
                try:
                    subprocess.call(['pdf2txt.py','-o',b_dir+'/txt/'+path,'-t','text','/opt/charity_pdfs/'+pdf.file_name])
                except:
                    logging.warning('Something went wrong: %s'%(pdf.file_name,))
                    continue
            txt = to_unicode(open(b_dir+'/txt/'+path).read())

            for srch in searches:
                logging.basicConfig(format='%(asctime)s %(message)s',filename=os.path.join(b_dir,'logs/')+str(srch.pk)+'.log',level=logging.DEBUG)
                output = open(os.path.join(b_dir,'logs/')+str(srch.pk)+'.log','w')
                if (srch.Y_start > pdf.year) or (srch.Y_end < pdf.year):
                    output.write('%s not within time boundaries.\n'%(pdf.file_name))
                    continue
                for x in srch.search_terms.all():
                    st = x.term
                    st = st.replace(' ','\s+')
                    st = st.replace('*','[-\w]*')
                    search_s = re.compile(r'^.*?[\s(]+'+st+r'[\s)]+.*?$',flags=re.M|re.U|re.I)
                    l_search = search_s.findall(txt)
                    for z in l_search:
                        snp =  CmdSearchPDFsHits(snippet=z,pdf=pdf.pk,term=x)
                        try:
                            snp.save()
                        except:
                            snp =  CmdSearchPDFsHits(snippet='unicode error',pdf=pdf.pk,term=x)
                            snp.save()
                        srch.hits.add(snp)
                if srch.user:
                    if srch.user.email:
                        if srch.user.username in emailUser.keys():
                            if str(srch.pk) not in emailUser[srch.user.username]['searchesPK']:
                                emailUser[srch.user.username]['searches'].append((srch.name,str(srch.pk)))
                                emailUser[srch.user.username]['searchesPK'].append(str(srch.pk))
                        else:
                            emailUser[srch.user.username] = {'searches':[(srch.name,str(srch.pk))]}
                            emailUser[srch.user.username]['email'] = srch.user.email
                            emailUser[srch.user.username]['searchesPK'] = [str(srch.pk)]
                srch.progress = round((float(ind+1))/float(nmb),4)
                srch.save()
            os.remove(b_dir+'/txt/'+path)
        for zz in emailUser.keys():
            if len(emailUser[zz]['searches']) > 1:
                listsearches=''
                for uu in emailUser[zz]['searches']:
                    listsearches = listsearches+', '+uu[0]
                listsearches = listsearches[2:]
                email_text = '<p>Dear %s,</p><p>Your searches (<b>%s</b>) have been finished.</p><p>You can view the results <a href="http://powerstructure.bath.ac.uk/budget_sheets/search_pdfs_all/">here</a>.</p><p>Please note that you need to be within the Universities network to view the page (either on campus or connected via VPN).</p>'%(zz,listsearches)
                email_text_plain = 'Dear %s,\nYour searches have been finished.\nYou can view the results here: http://powerstructure.bath.ac.uk/budget_sheets/search_pdfs_all/%s.\nPlease note that you need to be within the Universities network to view the page (either on campus or connected via VPN).</p>'%(zz,listsearches)
            else:
                email_text = '<p>Dear %s,</p><p>Your search <b>%s</b> has been finished.</p><p>You can view the results <a href="http://powerstructure.bath.ac.uk/budget_sheets/search_pdfs_all/%s">here</a>.</p><p>Please note that you need to be within the Universities network to view the page (either on campus or connected via VPN).</p>'%(zz,emailUser[zz]['searches'][0][0],str(emailUser[zz]['searches'][0][1]))
                email_text_plain = 'Dear %s,\nYour search %s has been finished.\nYou can view the results here: http://powerstructure.bath.ac.uk/budget_sheets/search_pdfs_all/%s.\nPlease note that you need to be within the Universities network to view the page (either on campus or connected via VPN).</p>'%(zz,emailUser[zz]['searches'][0][0],str(emailUser[zz]['searches'][0][1]))
            send_mail('CharityComm search results - %s'%datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), email_text_plain, 'mss49@bath.ac.uk',[emailUser[zz]['email']], fail_silently=False, html_message=email_text)
            

            

