#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from budget_sheets.models import PdfsBudget,CmdSearchPDFs,CmdSearchPDFsHits
from django.contrib.auth.models import User
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
from bath.settings import BASE_DIR


class Command(BaseCommand):
    args = '<SearchTerm>'
    help = 'You can additionally define a start and a end year.'

    option_list = BaseCommand.option_list + (
    	make_option(
    	'--startYear',
    	type='int',
    	dest='startYear'
    	),make_option(
    	'--endYear',
    	type='int',
    	dest='endYear'),make_option(
    	'--user',
    	type='string',
    	dest='user'))

    
    #b_dir = '~/CloudStation/ba'


    def handle(self, *args, **options):

    	b_dir = os.path.join(BASE_DIR,'search_tmp')
    	st = args[0]
    	a = CmdSearchPDFs(name=st,progress=0)
    	logging.basicConfig(format='%(asctime)s %(message)s',filename=os.path.join(b_dir,'logs')+str(a.pk)+'.log',level=logging.DEBUG)
    	if options['user']:
    		x = User.objects.get(username=options['user'])
    		a.user=x
    	if  options["startYear"]:
    		sY=options['startYear']
    		if options["endYear"]:
    			eY = options['endYear']
    			pdf_files = PdfsBudget.objects.filter(year__gte=sY,year__lte=eY)
    			a.Y_start = sY
    			a.Y_end = eY
    			
    		else:
    			pdf_files = PdfsBudget.objects.filter(year__gte=sY)
    			a.Y_start = sY
    			
    	elif options["endYear"]:
    		eY = options['endYear']
    		pdf_files = PdfsBudget.objects.filter(year__lte=eY)
    		a.Y_end = eY
    		
    	else:
    		pdf_files = PdfsBudget.objects.all()
    	a.save()
    	nmb = pdf_files.count()
    	for ind,pdf in enumerate(pdf_files):
	    	path = hashlib.md5(to_bytes(pdf.file_name)).hexdigest()
	    	if pdf.downloaded:
	    		print 'process file '+str(ind)
	    		try:
	    			subprocess.call(['pdf2txt.py','-o',b_dir+'/txt/'+path,'-t','text',os.path.join(BASE_DIR,'pdfs_download/')+pdf.file_name])
	    		except:
	    			logging.warning('Something went wrong: %s',(pdf.file_name,))
	    			continue
	    	else:
	    		print 'process file '+str(ind)
	    		try:
	    			subprocess.call(['pdf2txt.py','-o',b_dir+'/txt/'+path,'-t','text','/opt/charity_pdfs/'+pdf.file_name])
	    		except:
	    			logging.warning('Something went wrong: %s',(pdf.file_name,))
	    			continue
	    	txt = to_unicode(open(b_dir+'/txt/'+path).read())
	    	print 'search for string'
	    	st =st.replace(' ','\s')
	    	st = st.replace('*','\w*')
            search_s = re.compile(r'^.*?\s'+st+r'\s.*?$',flags=re.M|re.U|re.I)
	    	l_search = search_s.findall(txt)
	    	print 'found '+str(len(l_search))
	    	for z in l_search:
	    		snp =  CmdSearchPDFsHits(snippet=z,pdf=pdf.pk)
	    		snp.save()
	    		a.hits.add(snp)
	    	os.remove(b_dir+'/txt/'+path)
	    	a.progress=(float(ind+1))/float(nmb)
	    	a.save()
