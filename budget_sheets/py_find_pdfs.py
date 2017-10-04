#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml
import lxml.html
from urllib.request import urlopen
import MySQLdb as mdb
import codecs
import re
import time
import random
import datetime
import logging
import os
import sys
from django.conf import settings


def downl_pdfs(regno_2):
    con = mdb.connect('localhost', settings.DATABASES['default']['USER'],
                      settings.DATABASES['default']['PASSWORD'],
                      settings.DATABASES['default']['NAME'])
    # con = mdb.connect('localhost','dj_bath','','django_charity_2')
    cur = con.cursor()

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    logging.basicConfig(format='%(asctime)s %(message)s',
                        filename=os.path.join(settings.BASE_DIR, 'warnings_downl_pdfs.log'), level=logging.DEBUG)

    direct = os.path.join(settings.BASE_DIR, 'pdfs_download/')

    # log = codecs.open('log.txt','w',encoding='utf-8')

    count = 0

    zufall = random.randint(2, 5)
    try:
        url = "http://apps.charitycommission.gov.uk/Showcharity/RegisterOfCharities/DocumentList.aspx?RegisteredCharityNumber=" + str(
            regno_2) + "&SubsidiaryNumber=0&DocType=AccountList"
        web = urlopen(url).read()
    except:
        cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('" + str(
            regno_2) + "',Null,Null,'summary page not accesible')")
        con.commit()
        # print("Summary page not accesible: "+str(regno_2))
        logging.warning("Summary page not accesible: %s" % str(regno_2))
        print("Summary page not accesible: %s" % str(regno_2))
    mytree = lxml.html.fromstring(web)
    pdfs = mytree.xpath('//table[@id="ctl00_MainContent_dgrDocumentList"]//a/@href')
    # print("Downloading %s" % str(regno_2))
    logging.info("Downloading %s" % str(regno_2))
    print("Downloading %s" % str(regno_2))
    sys.stdout.flush()
    if len(pdfs) > 0:
        for s in pdfs:
            zufall2 = random.randint(1, 7)
            regno = re.search(r'0{3,}([0-9]+)', s, flags=re.IGNORECASE).group(1)
            date1 = re.search(r'ac_([0-9]+)', s, flags=re.IGNORECASE).group(1)
            if int(regno) != int(regno_2):
                # print("Regnos are not the same: "+str(regno)+" / "+str(regno_2))
                logging.warning("Regnos not the same: %s - %s" % (str(regno), str(regno_2)))
                print("Regnos not the same: %s - %s" % (str(regno), str(regno_2)))
            filename = direct + regno + '_ac_' + str(date1[:4]) + '.pdf'
            filename2 = regno + '_ac_' + str(date1[:4]) + '.pdf'

            try:
                pdf_1 = urlopen("http://apps.charitycommission.gov.uk" + s).read()
                # print("Downloading "+str(filename2))
                logging.info("Downloading %s" % str(filename2))
                print("Downloading %s" % str(filename2))
                file_1 = open(filename, 'wb')
                file_1.write(pdf_1)
                file_1.close()
                cur.execute(
                    "INSERT INTO pdfs_budget(regno,year,date,file_name,downloaded) VALUES('" + regno + "','" + date1[
                                                                                                               :4] + "','" + date1[
                                                                                                                             4:] + "','" + filename2 + "',1)")
                con.commit()
                count += 1
            except:
                cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('" + regno + "','" + date1[
                                                                                                            :4] + "','" + date1[
                                                                                                                          4:] + "','could not load')")
                con.commit()
            # print("Sleeping for "+str(10*zufall2)+' seconds.')
            # logging.info("Sleeping for %s seconds." % str(10*zufall2))
            # time.sleep(8*zufall2)

        last_pdf = pdfs.pop()
        date1 = re.search(r'ac_([0-9]+)', last_pdf, flags=re.IGNORECASE).group(1)
        date2 = date1[:4]

        for x in range(2005, int(date2)):
            zufall3 = random.randint(1, 7)
            filen = re.sub(r'_[0-9]{4}', '_' + str(x), last_pdf, flags=re.IGNORECASE)
            regno = re.search(r'0{3,}([0-9]+)', s, flags=re.IGNORECASE).group(1)
            filename = direct + regno + '_ac_' + str(x) + '.pdf'
            filename2 = regno + '_ac_' + str(x) + '.pdf'

            # print("Downloading "+str(filename2))
            logging.info("Downloading %s" % str(filename2))
            print("Downloading %s" % str(filename2))
            sys.stdout.flush()
            try:
                pdf_1 = urlopen("http://apps.charitycommission.gov.uk" + filen).read()
                file_1 = open(filename, 'wb')
                file_1.write(pdf_1)
                file_1.close()
                cur.execute(
                    "INSERT INTO pdfs_budget(regno,year,date,file_name,downloaded) VALUES('" + regno + "','" + str(
                        x) + "','" + date1[4:] + "','" + filename2 + "',1)")
                con.commit()
                count += 1
            except:
                cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('" + regno + "','" + str(
                    x) + "','" + date1[4:] + "','not available')")
                con.commit()
                logging.warning("%s / %s not available for download" % (str(regno), str(x)))
                print("%s / %s not available for download" % (str(regno), str(x)))
                sys.stdout.flush()
            # print("Sleeping for "+str(10*zufall2)+' seconds.')
            # logging.info("Sleeping for %s seconds." % str(10*zufall2))
            # time.sleep(8*zufall2)

            # print("Sleeping for "+str(60*zufall)+' seconds.')
            # logging.info("Sleeping for %s seconds." % str(60*zufall))
            # time.sleep(30*zufall)
    else:
        cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('" + str(
            regno_2) + "',Null,Null,'no pdfs found')")
        con.commit()
        # print("No pdfs found: "+str(row[0]))
        logging.warning("No pdfs found: %s" % str(regno_2))
        print("No pdfs found: %s" % str(regno_2))
        sys.stdout.flush()

    con.close()
    return count


def downl_pdfs2(regno_2):
    # used to download pdfs without writing anything to the database.
    # con = mdb.connect('localhost','dj_bath','dx74$uvz','django_charity_2')
    # con = mdb.connect('localhost','dj_bath','','django_charity_2')
    # cur = con.cursor()


    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    # logging.basicConfig(format='%(asctime)s %(message)s',filename=os.path.join(settings.BASE_DIR,'warnings_downl_pdfs.log'),level=logging.DEBUG)

    direct = os.path.join(settings.BASE_DIR, 'pdfs_download/')

    # log = codecs.open('log.txt','w',encoding='utf-8')

    count = 0

    zufall = random.randint(2, 5)
    try:
        url = "http://apps.charitycommission.gov.uk/Showcharity/RegisterOfCharities/DocumentList.aspx?RegisteredCharityNumber=" + str(
            regno_2) + "&SubsidiaryNumber=0&DocType=AccountList"
        web = urlopen(url).read()
    except:
        # cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('"+str(regno_2)+"',Null,Null,'summary page not accesible')")
        # con.commit()
        # print("Summary page not accesible: "+str(regno_2))
        # logging.warning("Summary page not accesible: %s" % str(regno_2))
        print("Summary page not accesible: %s" % str(regno_2))
    mytree = lxml.html.fromstring(web)
    pdfs = mytree.xpath('//table[@id="ctl00_MainContent_dgrDocumentList"]//a/@href')
    # print("Downloading %s" % str(regno_2))
    # logging.info("Downloading %s" % str(regno_2))
    print("Downloading %s" % str(regno_2))
    sys.stdout.flush()
    if len(pdfs) > 0:
        for s in pdfs:
            zufall2 = random.randint(1, 7)
            regno = re.search(r'0{3,}([0-9]+)', s, flags=re.IGNORECASE).group(1)
            date1 = re.search(r'ac_([0-9]+)', s, flags=re.IGNORECASE).group(1)
            if int(regno) != int(regno_2):
                # print("Regnos are not the same: "+str(regno)+" / "+str(regno_2))
                # logging.warning("Regnos not the same: %s - %s"%(str(regno),str(regno_2)))
                print("Regnos not the same: %s - %s" % (str(regno), str(regno_2)))
            filename = direct + regno + '_ac_' + str(date1[:4]) + '.pdf'
            filename2 = regno + '_ac_' + str(date1[:4]) + '.pdf'

            try:
                pdf_1 = urlopen("http://apps.charitycommission.gov.uk" + s).read()
                # print("Downloading "+str(filename2))
                # logging.info("Downloading %s" % str(filename2))
                print("Downloading %s" % str(filename2))
                file_1 = open(filename, 'wb')
                file_1.write(pdf_1)
                file_1.close()
                # cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name,downloaded) VALUES('"+regno+"','"+date1[:4]+"','"+date1[4:]+"','"+filename2+"',1)")
                # con.commit()
                count += 1
            except:
                # cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('"+regno+"','"+date1[:4]+"','"+date1[4:]+"','could not load')")
                # con.commit()
                print('could not load')
            # print("Sleeping for "+str(10*zufall2)+' seconds.')
            # logging.info("Sleeping for %s seconds." % str(10*zufall2))
            # time.sleep(8*zufall2)

        last_pdf = pdfs.pop()
        date1 = re.search(r'ac_([0-9]+)', last_pdf, flags=re.IGNORECASE).group(1)
        date2 = date1[:4]

        for x in range(2005, int(date2)):
            zufall3 = random.randint(1, 7)
            filen = re.sub(r'_[0-9]{4}', '_' + str(x), last_pdf, flags=re.IGNORECASE)
            regno = re.search(r'0{3,}([0-9]+)', s, flags=re.IGNORECASE).group(1)
            filename = direct + regno + '_ac_' + str(x) + '.pdf'
            filename2 = regno + '_ac_' + str(x) + '.pdf'

            # print("Downloading "+str(filename2))
            # logging.info("Downloading %s" % str(filename2))
            print("Downloading %s" % str(filename2))
            sys.stdout.flush()
            try:
                pdf_1 = urlopen("http://apps.charitycommission.gov.uk" + filen).read()
                file_1 = open(filename, 'wb')
                file_1.write(pdf_1)
                file_1.close()
                # cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name,downloaded) VALUES('"+regno+"','"+str(x)+"','"+date1[4:]+"','"+filename2+"',1)")
                # con.commit()
                count += 1
            except:
                # cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('"+regno+"','"+str(x)+"','"+date1[4:]+"','not available')")
                # con.commit()
                # logging.warning("%s / %s not available for download"%(str(regno),str(x)))
                print("%s / %s not available for download" % (str(regno), str(x)))
                sys.stdout.flush()
            # print("Sleeping for "+str(10*zufall2)+' seconds.')
            # logging.info("Sleeping for %s seconds." % str(10*zufall2))
            # time.sleep(8*zufall2)

            # print("Sleeping for "+str(60*zufall)+' seconds.')
            # logging.info("Sleeping for %s seconds." % str(60*zufall))
            # time.sleep(30*zufall)
    else:
        # cur.execute("INSERT INTO pdfs_budget(regno,year,date,file_name) VALUES('"+str(regno_2)+"',Null,Null,'no pdfs found')")
        # con.commit()
        # print("No pdfs found: "+str(row[0]))
        # logging.warning("No pdfs found: %s" % str(regno_2))
        print("No pdfs found: %s" % str(regno_2))
        sys.stdout.flush()

    return count
