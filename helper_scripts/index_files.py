#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from budget_sheets.models import ExtractCharity,PdfsBudget,ExtractFinancial
import logging
import json
from budget_sheets.py_find_pdfs import downl_pdfs


HOST = 'http://localhost:9200'
INDEX = 'charity_index_5'
TYPE = 'pdfs'
TMP_FILE_NAME = 'temp_file'
f_path = '/opt/charity_pdfs'
f_path_down = '/opt/bath/pdfs_download'

logging.basicConfig(format='%(asctime)s %(message)s',filename='/opt/bath/indexing2.log',level=logging.DEBUG)

regnos=[]

for x in ExtractFinancial.objects.filter(income__gt=10000000):
    if x.regno not in regnos:
        regnos.append(x.regno)

for t in regnos:
    if PdfsBudget.objects.filter(regno=t).count() == 0:
        print("downloading %s"%t)
        downl_pdfs(t)

for z in regnos:
    for x in PdfsBudget.objects.filter(regno=z).exclude(notes_index=True).exclude(year__lt=2010):
        if x.downloaded:
            zz = f_path_down+'/'+x.file_name
        else:
            zz=f_path+'/'+x.file_name
        try:
            print(zz)
            file64=file_r.encode("base64")
            name = ExtractCharity.objects.get(regno=x.regno,subno='0').name
            data = {'institution':name,'id_data':x.pk,'year':x.year,'pdf_a':{'_content':file64}}
            f = open(TMP_FILE_NAME, 'w')
            json.dump(data, f)
            f.close()
            cmd = 'curl -X POST "{}/{}/{}" -d @'.format(HOST,INDEX,TYPE) + TMP_FILE_NAME
            print cmd
            os.system(cmd)
            logging.info("Indexed %s"%x.pk)
            print("Indexed %s"%x.pk)
            x.notes_index=True
            x.save()
        except:
            logging.info("Could not open file: %s"%x.pk)
            print("Could not open file: %s"%x.pk)
            x.notes_index=False
            x.save()