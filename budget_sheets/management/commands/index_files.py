#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from budget_sheets.models import ExtractCharity,PdfsBudget,ExtractFinancial
import logging
import json
from budget_sheets.py_find_pdfs import downl_pdfs
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError



class Command(BaseCommand):
    args = '<minBudget firstYear>'
    help = 'You have to define the minimum Budget (first Argument) and the first year to cover (second argument)'

    def handle(self, *args, **options):

        HOST = 'http://localhost:9200'
        INDEX = 'charity_index_5'
        TYPE = 'pdfs'
        TMP_FILE_NAME = '/opt/bath/pdfs_download/temp_file'
        f_path = '/opt/charity_pdfs'
        f_path_down = '/opt/bath/pdfs_download'

        arg_budget = int(args[0])
        arg_year = int(args[1])

        logging.basicConfig(format='%(asctime)s %(message)s',filename=os.path.join(settings.BASE_DIR,'indexing2.log'),level=logging.DEBUG)

        regnos=[]
        logging.info('Adding charities with more than %s budget in one of the years covered. All pdfs starting with the year %s will be included.'%(str(arg_budget),str(arg_year)))
        print('Adding charities with more than %s budget in one of the years covered. All pdfs starting with the year %s will be included.'%(str(arg_budget),str(arg_year)))
        sys.stdout.flush()
        for x in ExtractFinancial.objects.filter(income__gt=arg_budget):
            if x.regno not in regnos:
                regnos.append(x.regno)

        for t in regnos:
            if PdfsBudget.objects.filter(regno=t).count() == 0:
                logging.info("downloading %s"%t)
                print("downloading %s"%t)
                downl_pdfs(t)
                sys.stdout.flush()

        for z in regnos:
            for x in PdfsBudget.objects.filter(regno=z).exclude(notes_index=True).exclude(year__lt=arg_year):
                if x.downloaded:
                    zz = f_path_down+'/'+x.file_name
                else:
                    zz=f_path+'/'+x.file_name
                try:
                    print(zz)
                    file_r = open(zz,'rb').read()
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
                    sys.stdout.flush()
                    x.notes_index=True
                    x.save()
                except:
                    logging.info("Could not open file: %s"%x.pk)
                    print("Could not open file: %s"%x.pk)
                    sys.stdout.flush()
                    x.notes_index=False
                    x.save()