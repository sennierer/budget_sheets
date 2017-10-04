from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from budget_sheets.forms import form_user_login
from budget_sheets.forms import query_name
from budget_sheets.forms import select_inst
from budget_sheets.forms import form_update_pdfs
from budget_sheets.forms import form_update_pdfs_2, form_search_results, search_form_pdfs
from django.core.management import call_command
from .models import ExtractCharity
from .models import PdfsBudget
from .models import ExtractTrustee
from .models import budget_flow
from .models import ConCharityBudgetflow, CmdSearchPDFs, CmdSearchPDFsTerm
from .forms import FormSet1Helper
from operator import itemgetter
from .py_find_pdfs import downl_pdfs
import re
import logging
import requests, json
import math


def user_login(request):
    errors = []
    if request.method == 'POST':
        form = form_user_login(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # return HttpResponse('logged in %s'%user)
                    return HttpResponseRedirect(request.GET.get('next', '/login/'))
                else:
                    return HttpResponse('not active.')
            else:
                return HttpResponse('user does not exist')
    else:
        form = form_user_login()
        return render(request, 'user_login.html', {'form': form})


# @login_required(login_url='/login/')
# def select_pdfs(request):


@login_required(login_url='/login/')
def search(request):
    errors = []
    formset_1 = formset_factory(select_inst, extra=0)
    if request.method == 'POST':
        form2 = query_name(request.POST)
        if form2.is_valid():
            cd = form2.cleaned_data
            results = []
            if cd['kind'] == '1':
                results = ExtractCharity.objects.filter(name__contains=cd['name'].upper(), subno=0)
            elif cd['kind'] == '2':
                trustees = ExtractTrustee.objects.filter(trustee__contains=cd['name'].upper())
                regnos = []

                for zz in trustees:
                    # return HttpResponse('Funkt: %s'%zz.trustee)
                    if zz.regno not in regnos:
                        # return HttpResponse('Funkt: %s'%zz.regno)
                        try:
                            results.append(ExtractCharity.objects.get(regno=int(zz.regno), subno=0))
                            regnos.append(zz.regno)
                        except:
                            pass
            elif cd['kind'] == '3':
                results = ExtractCharity.objects.filter(aob__contains=cd['name'].upper(), subno=0)
            elif cd['kind'] == '4':
                results = ExtractCharity.objects.filter(regno__contains=cd['name'], subno=0)
            results_2 = []

            for x in results:
                #	if PdfsBudget.objects.filter(regno=x.regno).exists():
                results_2.append({'regno': x.regno, 'name': x.name, 'aob': x.aob, 'include': x.include})

            if len(results) == 0:
                return render(request, 'message.html',
                              {'message': 'No Results!', 'redirect': '/bath/budget_sheets/search'})

            form = query_name()
            formset = formset_1(initial=results_2)
            helper = FormSet1Helper()
            return render(request, 'search.html', {'form': form, 'formset': formset, 'helper': helper})
        else:
            return render(request, 'search.html', {'form': form2})

    else:
        form = query_name()

        return render(request, 'search.html', {'form': form, 'results': False, 'formset': False})


@login_required(login_url='/login/')
def update_data(request):
    errors = []
    formset_1 = formset_factory(select_inst)
    if request.method == 'POST':
        formset = formset_1(request.POST, request.FILES)
        if formset.is_valid():
            cd = formset.cleaned_data
            loaded_pdfs = ''
            # return HttpResponse('Funkt: %s'%cd)
            for x in cd:
                charity = ExtractCharity.objects.get(regno=int(x['regno']), subno=0)
                charity.include = x['include']
                charity.save()
                if x['include'] == True:
                    if charity.pdfs != True and PdfsBudget.objects.filter(regno=int(x['regno'])).count() == 0:
                        loaded_pdfs = downl_pdfs(charity.regno)
                        PdfsBudget.objects.filter(regno=int(x['regno'])).update(downloaded=True)
                    pdfs = PdfsBudget.objects.filter(regno=int(x['regno'])).update(include=True)


                # pdfs.include = True
                # pdfs.save()
                # return HttpResponse('Funkt: %s'%x['regno'])
                else:
                    pdfs = PdfsBudget.objects.filter(regno=int(x['regno'])).update(include=False)
            return render(request, 'message.html', {'message': 'Saved!', 'redirect': '/budget_sheets/search'})

        else:
            return HttpResponse('Mistake! %s' % formset)


@login_required(login_url='/login/')
def list_pdfs(request):
    pdfs = PdfsBudget.objects.filter(include=True, file_name__contains='_ac_').exclude(finalized=True).exclude(
        no_data=True)
    regnos2 = []
    chs = []
    for x in pdfs:
        results2 = []
        if x.regno not in regnos2 and ExtractCharity.objects.get(regno=int(x.regno), subno=0):
            chs.append(ExtractCharity.objects.get(regno=int(x.regno), subno=0))
            regnos2.append(x.regno)

    # chs = sorted(chs,key=itemgetter('name'))
    # return HttpResponse('Funkt: %s'%results)
    return render(request, 'list_pdfs.html', {'chs': chs, 'pdfs': pdfs, 'type': 'todo'})


@login_required(login_url='/login/')
def update_pdfs(request, file_name):
    logging.basicConfig(format='%(asctime)s %(message)s', filename='/opt/bath/submits.log', level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s %(message)s',filename='submits.log',level=logging.DEBUG)
    formset_1 = formset_factory(form_update_pdfs)
    formset_2 = formset_factory(form_update_pdfs, extra=0)
    if request.method == 'POST':
        formset = formset_1(request.POST, request.FILES)
        form = form_update_pdfs_2(request.POST)
        if formset.is_valid() and form.is_valid():
            cd_2 = formset.cleaned_data
            cd_3 = form.cleaned_data
            logging.info('Submitted the following dataset: %s' % cd_2)
            logging.info('Submitted the following form: %s' % cd_3)
            filen = PdfsBudget.objects.get(file_name=file_name)
            char_3 = ExtractCharity.objects.get(regno=filen.regno, subno=0)
            id_file = filen.id
            regno = filen.regno
            if cd_3['no_data'] == True:
                filen.no_data = True
                filen.save()
                char_3.not_interested = cd_3['not_interested']
                char_3.not_interested_text = cd_3['not_interested_text']
                char_3.save()
                return render(request, 'message.html', {'message': 'Saved!', 'redirect': request.get_full_path()})
            if cd_3['not_interested'] == True:
                char_3.not_interested = True
                char_3.not_interested_text = cd_3['not_interested_text']
                char_3.save()
                return render(request, 'message.html', {'message': 'Saved!', 'redirect': request.get_full_path()})

            filen.finalized = cd_3['finalized']
            filen.notes = cd_3['notes_pdf']
            filen.no_data = cd_3['no_data']
            char_3.not_interested = cd_3['not_interested']
            char_3.not_interested_text = cd_3['not_interested_text']
            char_3.save()
            filen.save()
            username = request.user.username
            if cd_3['cp_field']:
                if cd_3['cp_delete']:
                    cd_2 = []
                cp_fields = re.split(r'\s+', cd_3['cp_descr'])
                reg = ''
                y_list = []
                for ind, p in enumerate(cp_fields):
                    if p.lower().strip() == 'name':
                        reg = reg + r'([a-zA-Z\._\- ]+)'
                        y_list.append('name')
                    elif p.lower().strip() == 'amount':
                        reg = reg + r'([\d\.,\-]+)'
                        y_list.append(p.strip())

                    elif p.lower().strip() == 'disc':
                        reg = reg + '[^\s]+?'
                        y_list.append('disc')
                    if ind < len(cp_fields) - 1:
                        reg = reg + '\s+'
                cp_lines = cd_3['cp_field'].split('\r\n')
                if re.search(r'\d+', cp_lines[0]) and re.search(r'\d+', cp_lines[-1]):
                    for p in cp_lines:
                        cp_match = re.search(r'^' + reg + r'\s*$', p, flags=re.U)
                        # cp_match = re.match(r'([a-zA-Z\._\- ]+)\s+([\d\.,\-]+)\s*[\d\.,\-]+?([\d\.,\-]+)\s*',p,flags=re.U)
                        count = 0
                        name = ''
                        y2_years = []
                        if cp_match:
                            nmb = cp_match.group(2).replace(',', '')
                            try:
                                nmb = nmb.split('.')[0]
                            except:
                                pass
                            if cd_3['cp_multi']:
                                nmb = int(nmb) * cd_3['cp_multi']
                            if re.match(r'^\d+$', str(nmb)):
                                cd_2.append({'regno': regno, 'id_budget_file': id_file, 'type_of_flow': cd_3['cp_kind'],
                                             'username': username, 'amount': nmb, 'recip_don': cp_match.group(1),
                                             'currency': cd_3['currency'], 'nmb_of_grants': None, 'notes_grants': None})
                else:
                    nmb_lines = len(cp_lines) / len(y_list)
                    cnt_1 = 0
                    cnt_2 = 0
                    cnt_3 = 0
                    zwi = []
                    while cnt_1 < len(y_list):
                        zwi_2 = []
                        cnt_2 = 0
                        while cnt_2 < nmb_lines:
                            if re.match(r'[0-9,]+\.', cp_lines[cnt_3]):
                                nmb = re.search(r'([0-9, ]+)', cp_lines[cnt_3].strip()).group(1).replace(',',
                                                                                                         '').replace(
                                    ' ', '')
                                if cd_3['cp_multi']:
                                    nmb = int(nmb) * int(cd_3['cp_multi'])
                                zwi_2.append(nmb)
                            elif re.match(r'[0-9, ]+', cp_lines[cnt_3]):
                                nmb = cp_lines[cnt_3].strip().replace(',', '').replace(' ', '')
                                if cd_3['cp_multi']:
                                    nmb = int(nmb) * cd_3['cp_multi']
                                zwi_2.append(nmb)
                            else:
                                zwi_2.append(cp_lines[cnt_3].strip())
                            cnt_2 += 1
                            cnt_3 += 1
                        zwi.append(zwi_2)
                        cnt_1 += 1

                    cnt_3 = 0
                    res_3 = dict()
                    for xx in y_list:
                        if xx == 'name':
                            res_3['name'] = cnt_3
                        # elif re.match(r'\d+',xx) and :
                        elif str(xx) == 'amount':
                            res_3['amount'] = cnt_3
                        cnt_3 += 1
                    cnt_3 = 0
                    for xxx in zwi[res_3['name']]:
                        if re.match(r'^\d+$', str(zwi[res_3['amount']][cnt_3])) and len(xxx) > 0:
                            cd_2.append({'regno': regno, 'id_budget_file': id_file, 'type_of_flow': cd_3['cp_kind'],
                                         'username': username, 'amount': zwi[res_3['amount']][cnt_3], 'recip_don': xxx,
                                         'currency': cd_3['currency'], 'nmb_of_grants': None, 'notes_grants': None})
                        cnt_3 += 1
            budget_flow.objects.filter(id_budget_file=int(id_file)).delete()
            for cd in cd_2:

                # if cd['id']:
                # return HttpResponse('Id found: %s'%cd['id'])
                #	budget_flow.objects.filter(id=int(cd['id'])).update(regno=regno,recip_don=cd['recip_don'],recip_don_regno=regno_recip,id_budget_file=id_file,type_of_flow=cd['type_of_flow'],amount=cd['amount'],currency=cd['currency'],user_name=username,nmb_of_grants=cd['nmb_of_grants'],notes_grants=cd['notes_grants'])

                # else:
                # aa = budget_flow(regno=regno,recip_don=cd['recip_don'],recip_don_regno=regno_recip,id_budget_file=id_file,type_of_flow=cd['type_of_flow'],amount=cd['amount'],currency=cd['currency'],user_name=username,nmb_of_grants=cd['nmb_of_grants'],notes_grants=cd['notes_grants'])
                regno_recip = None
                try:
                    kind_recip_don_1 = cd['kind_recip_don']
                except:
                    kind_recip_don_1 = 'charity'
                aa = budget_flow(regno=regno, recip_don=cd['recip_don'], id_budget_file=id_file,
                                 type_of_flow=cd['type_of_flow'], amount=cd['amount'], currency=cd['currency'],
                                 user_name=username, nmb_of_grants=cd['nmb_of_grants'], notes_grants=cd['notes_grants'],
                                 kind_recip_don=kind_recip_don_1)

                aa.save()

                if ExtractCharity.objects.filter(name=cd['recip_don']).exists():
                    regno_recip = ExtractCharity.objects.filter(name=cd['recip_don']).values('regno')
                    for zzz in regno_recip:
                        char_2 = ExtractCharity.objects.get(regno=zzz['regno'], subno=0)
                        ddd = ConCharityBudgetflow(id_charity=char_2, id_budgetflow=aa)
                        ddd.save()

            return render(request, 'message.html', {'message': 'Saved!', 'redirect': request.get_full_path()})
        else:
            # formset_3 = formset_1()
            return render_to_response('update_pdfs.html',
                                      {'filename': file_name, 'formset': formset, 'helper': FormSet1Helper,
                                       'errors': formset.errors, 'form': form},
                                      context_instance=RequestContext(request))
    else:
        file_name2 = 'https://powerstructure.bath.ac.uk/pdfs/' + file_name
        pdf2 = PdfsBudget.objects.get(file_name=file_name)
        char_3 = ExtractCharity.objects.get(regno=pdf2.regno, subno=0)
        if pdf2.downloaded == True:
            file_name2 = 'https://powerstructure.bath.ac.uk/pdfs_download/' + file_name
        form = form_update_pdfs_2(
            initial={'notes_pdf': pdf2.notes, 'no_data': pdf2.no_data, 'not_interested': char_3.not_interested,
                     'not_interested_text': char_3.not_interested_text, 'finalized': pdf2.finalized})
        if budget_flow.objects.filter(id_budget_file=pdf2.id).exists():
            formset = formset_2(initial=budget_flow.objects.filter(id_budget_file=pdf2.id).values())
        else:
            # form = form_update_pdfs_2()
            formset = formset_1()
        return render(request, 'update_pdfs.html',
                      {'filename': file_name2, 'formset': formset, 'helper': FormSet1Helper, 'form': form})


# @login_required(login_url='/bath/login/')
# def update_pdfs_data(request):
@login_required(login_url='/login/')
def finalized(request):
    pdfs = PdfsBudget.objects.filter(finalized=True)
    regnos2 = []
    chs = []
    for x in pdfs:
        results2 = []
        if x.regno not in regnos2:
            chs.append(ExtractCharity.objects.get(regno=int(x.regno), subno=0))
            regnos2.append(x.regno)

    # return HttpResponse('Funkt: %s'%results)
    return render(request, 'list_pdfs.html', {'chs': chs, 'pdfs': pdfs, 'type': 'finalized'})


@login_required(login_url='/login/')
def index(request):
    pdfs = PdfsBudget.objects.filter(finalized=True).count()
    datasets = budget_flow.objects.all().count()
    return render(request, 'index.html', {'pdfs': pdfs, 'datasets': datasets})


@login_required(login_url='/login/')
def list_results(request):
    if request.method == "POST":
        form = form_search_results(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            page = 1
            # flows = budget_flow.objects.filter(recip_don__icontains=cd['search'])
            search_term = cd['search']
    else:
        page = request.GET.get('page')

    if 'q' in request.GET:
        search_term = request.GET.get('q')

    try:
        # l_1 = ((int(page)*25)-25,int(page)*25)
        page = int(page)
        l_1_low = (int(page) * 25) - 25
        l_1_high = int(page) * 25
    except:
        page = 1
        # l_1 = ((int(page)*25)-25,int(page)*25)
        l_1_low = (int(page) * 25) - 25
        l_1_high = int(page) * 25
    try:
        nmb_res = budget_flow.objects.filter(recip_don__icontains=search_term).count()
        flows = budget_flow.objects.filter(recip_don__icontains=search_term)[l_1_low:l_1_high]
    except:
        nmb_res = budget_flow.objects.all().count()
        flows = budget_flow.objects.all()[l_1_low:l_1_high]

    for x in flows:
        y = x.id_budget_file
        x.file_name = PdfsBudget.objects.get(id=y).file_name
        flows_2 = ConCharityBudgetflow.objects.filter(id_budgetflow=x)
        x.regno_inst_rec = False
        # if len(flows_2)>0:
        # x.regno_inst_rec=flows_2.id_charity.regno
        count = 0
        for uu in flows_2:
            if count == 0:
                x.regno_inst_rec = uu.id_charity.regno
            count += 1
    pagin = dict()
    pagin['page'] = page
    if page > 1:
        pagin['prev'] = page - 1
    if float(page) < (float(nmb_res) / 25):
        pagin['nxt'] = page + 1
    # paginator = Paginator (flows,25)
    # test2
    # page = request.GET.get('page')
    # try:
    #	flows2 = paginator.page(page)
    # except PageNotAnInteger:
    # If page is not an integer, deliver first page.
    #	flows2 = paginator.page(1)
    # except EmptyPage:
    # If page is out of range (e.g. 9999), deliver last page of results.
    #	flows2 = paginator.page(paginator.num_pages)
    tot_pages = int(math.ceil(float(nmb_res) / 25))
    pagin['tot_pages'] = tot_pages
    form = form_search_results()
    try:
        return render(request, 'list_results.html',
                      {'flows2': flows, 'form': form, 'nmb_res': nmb_res, 'search_term': search_term, 'pagin': pagin, })
    except:
        return render(request, 'list_results.html', {'flows2': flows, 'form': form, 'nmb_res': nmb_res, 'pagin': pagin})


@login_required(login_url='/login/')
def details_charity(request, regno_charity):
    url_search = "http://127.0.0.1:9200/charity_index_5/pdfs/_search"
    charity = ExtractCharity.objects.get(regno=regno_charity, subno=0)
    bud_flows = budget_flow.objects.filter(regno=regno_charity)
    bud_flows_2 = ConCharityBudgetflow.objects.filter(id_charity=charity.id)
    st_wrds = ['limited', 'ltd.', 'the']
    ch_n_1 = charity.name.split(' ')
    pdfs = []
    ff = ''
    page = request.GET.get('page')
    try:
        from_p = (10 * int(page)) - 10
    except:
        from_p = 0
    for x in ch_n_1:
        if x.lower().strip() not in st_wrds:
            ff = ff + x.lower().strip() + ' '
    ff = ff.strip()
    for x in PdfsBudget.objects.filter(regno=regno_charity):
        pdfs.append(x.pk)
    data = {"from": from_p, "size": 10, "fields": ["institution", "id_data"], "query": {
        "filtered": {"query": {"match_phrase": {"pdf_a": {"query": ff, "slop": 1}}},
                     "filter": {"bool": {"must_not": {"terms": {"id_data": pdfs}}}}}},
            "highlight": {"fields": {"pdf_a": {}}}}
    s_resp = requests.post(url_search, data=json.dumps(data)).json()
    for ind, x in enumerate(s_resp['hits']['hits']):
        t = PdfsBudget.objects.get(pk=x['fields']['id_data'][0])
        s_resp['hits']['hits'][ind]["fields"]["regno"] = t.regno
        s_resp['hits']['hits'][ind]["fields"]["year"] = t.year
        s_resp['hits']['hits'][ind]["fields"]["file_name"] = t.file_name
        try:
            for ind2, ll in enumerate(s_resp['hits']['hits'][ind]['highlight']['pdf_a']):
                # s_resp['hits']['hits'][ind]["highlight"]["pdf_a"][ind2]=s_resp['hits']['hits'][ind]["highlight"]["pdf_a"][ind2].replace("\n","<br />")
                s_resp['hits']['hits'][ind]['highlight']["pdf_a"][ind2], c = re.subn(r'\n+', '<br />',
                                                                                     s_resp['hits']['hits'][ind][
                                                                                         "highlight"]["pdf_a"][ind2])
        except:
            pass
    for x in bud_flows:
        y = x.id_budget_file
        x.file_name = PdfsBudget.objects.get(id=y).file_name
        flows_2 = ConCharityBudgetflow.objects.filter(id_budgetflow=x)
        x.regno_inst_rec = False
        # if len(flows_2)>0:
        # x.regno_inst_rec=flows_2.id_charity.regno
        count = 0
        for uu in flows_2:
            if count == 0:
                x.regno_inst_rec = uu.id_charity.regno
            count += 1
    flows_3 = []
    for x in bud_flows_2:
        y = x.id_budgetflow
        y.file_name = PdfsBudget.objects.get(id=y.id_budget_file).file_name
        flows_3.append(y)

    if s_resp['hits']['total'] > from_p + 10 and from_p == 0:
        return render(request, 'charity_details.html',
                      {'charity': charity, 'bud_flows': bud_flows, 'flows_3': flows_3, 's_resp': s_resp,
                       'page_next': 2})
    elif s_resp['hits']['total'] > from_p + 10 and from_p > 0:
        return render(request, 'charity_details.html',
                      {'charity': charity, 'bud_flows': bud_flows, 'flows_3': flows_3, 's_resp': s_resp,
                       'page_next': int(page) + 1, 'page_previous': int(page) - 1})
    elif s_resp['hits']['total'] < from_p + 10 and from_p > 0:
        return render(request, 'charity_details.html',
                      {'charity': charity, 'bud_flows': bud_flows, 'flows_3': flows_3, 's_resp': s_resp,
                       'page_previous': int(page) - 1})
    else:
        return render(request, 'charity_details.html',
                      {'charity': charity, 'bud_flows': bud_flows, 'flows_3': flows_3, 's_resp': s_resp})


@login_required(login_url='/login/')
def search_pdfs(request):
    url_search = "http://127.0.0.1:9200/charity_index_5/pdfs/_search"
    if request.method == 'POST':
        form2 = search_form_pdfs(request.POST)
        if form2.is_valid():
            cd = form2.cleaned_data
            data = {"from": 0, "size": 10, "fields": ["institution", "id_data"],
                    "query": {"match_phrase": {"pdf_a": {"query": cd['search'], "slop": 1}}},
                    "highlight": {"fields": {"pdf_a": {}}}}
            s_resp = requests.post(url_search, data=json.dumps(data)).json()
            for ind, x in enumerate(s_resp['hits']['hits']):
                t = PdfsBudget.objects.get(pk=x['fields']['id_data'][0])
                s_resp['hits']['hits'][ind]["fields"]["regno"] = t.regno
                s_resp['hits']['hits'][ind]["fields"]["year"] = t.year
                s_resp['hits']['hits'][ind]["fields"]["file_name"] = t.file_name
                try:
                    for ind2, ll in enumerate(s_resp['hits']['hits'][ind]['highlight']['pdf_a']):
                        # s_resp['hits']['hits'][ind]["highlight"]["pdf_a"][ind2]=s_resp['hits']['hits'][ind]["highlight"]["pdf_a"][ind2].replace("\n","<br />")test
                        s_resp['hits']['hits'][ind]['highlight']["pdf_a"][ind2], c = re.subn(r'\n+', '<br />',
                                                                                             s_resp['hits']['hits'][
                                                                                                 ind]["highlight"][
                                                                                                 "pdf_a"][ind2])
                except:
                    pass
            form = search_form_pdfs()
            if s_resp['hits']['total'] > 10:
                return render(request, 'search_pdfs.html',
                              {'form': form, 'searchterm': cd['search'], 's_resp': s_resp, 'page_next': 2})
            else:
                return render(request, 'search_pdfs.html', {'form': form, 'searchterm': cd['search'], 's_resp': s_resp})

    elif request.GET.get('page'):
        page = request.GET.get('page')
        searchterm = request.GET.get('search')
        try:
            from_p = (10 * int(page)) - 10
        except:
            from_p = 0
        data = {"from": from_p, "size": 10, "fields": ["institution", "id_data"],
                "query": {"filtered": {"query": {"match_phrase": {"pdf_a": {"query": searchterm, "slop": 1}}}}},
                "highlight": {"fields": {"pdf_a": {}}}}
        s_resp = requests.post(url_search, data=json.dumps(data)).json()
        for ind, x in enumerate(s_resp['hits']['hits']):
            t = PdfsBudget.objects.get(pk=x['fields']['id_data'][0])
            s_resp['hits']['hits'][ind]["fields"]["regno"] = t.regno
            s_resp['hits']['hits'][ind]["fields"]["year"] = t.year
            s_resp['hits']['hits'][ind]["fields"]["file_name"] = t.file_name
            try:
                for ind2, ll in enumerate(s_resp['hits']['hits'][ind]['highlight']['pdf_a']):
                    # s_resp['hits']['hits'][ind]["highlight"]["pdf_a"][ind2]=s_resp['hits']['hits'][ind]["highlight"]["pdf_a"][ind2].replace("\n","<br />")
                    s_resp['hits']['hits'][ind]['highlight']["pdf_a"][ind2], c = re.subn(r'\n+', '<br />',
                                                                                         s_resp['hits']['hits'][ind][
                                                                                             "highlight"]["pdf_a"][
                                                                                             ind2])
            except:
                pass
        form = search_form_pdfs()
        if s_resp['hits']['total'] > from_p + 10 and from_p > 0:
            return render(request, 'search_pdfs.html',
                          {'form': form, 'searchterm': searchterm, 's_resp': s_resp, 'page_next': int(page) + 1,
                           'page_previous': int(page) - 1})
        elif s_resp['hits']['total'] < from_p + 10 and from_p > 0:
            return render(request, 'search_pdfs.html',
                          {'form': form, 'searchterm': searchterm, 's_resp': s_resp, 'page_previous': int(page) - 1})
        elif s_resp['hits']['total'] > 10 and from_p == 0:
            return render(request, 'search_pdfs.html',
                          {'form': form, 'searchterm': searchterm, 's_resp': s_resp, 'page_next': 2})
        else:
            return render(request, 'search_pdfs.html', {'form': form, 'searchterm': searchterm, 's_resp': s_resp})
    else:
        form = search_form_pdfs()
        return render(request, 'search_pdfs.html', {'form': form})


@login_required(login_url='/login/')
def search_all_pdfs(request):
    if request.method == 'POST':
        if request.POST['Sdelete'] == 'true':
            CmdSearchPDFs.objects.get(pk=request.POST['Sid']).delete()
            res = json.dumps({'worked': True, 'id': request.POST['Sid']})
            return HttpResponse(res, content_type='application/javascript')
        else:
            name = request.POST['Sname']
            years = request.POST['Syears']
            terms = request.POST['Sterms']
            if len(years) > 0:
                if '-' in years:
                    yy = years.split('-')
                    SYear = yy[0]
                    EYear = yy[1]
                    if (len(SYear) > 0) and (len(EYear) > 0):
                        search = CmdSearchPDFs(name=name, Y_start=int(SYear), Y_end=int(EYear))
                    elif len(EYear) > 0:
                        search = CmdSearchPDFs(name=name, Y_end=int(EYear))
                    elif len(SYear) > 0:
                        search = CmdSearchPDFs(name=name, Y_start=int(SYear))
                else:
                    search = CmdSearchPDFs(name=name, Y_start=int(years), Y_end=int(years))
            else:
                search = CmdSearchPDFs(name=name)
            if request.POST['Semail'] == 'true':
                search.user = request.user
            search.save()
            terms2 = []
            for xx in terms.split(';'):
                zz, created = CmdSearchPDFsTerm.objects.get_or_create(term=xx.lower().strip())
                search.search_terms.add(zz)
                search.save()
                terms2.append(xx.strip())
            terms3 = ', '.join(terms2)
            if search.Y_start and search.Y_end:
                nmb = PdfsBudget.objects.filter(year__lte=search.Y_end).filter(year__gte=search.Y_start).count()
            elif d.Y_start:
                nmb = PdfsBudget.objects.filter(year__gte=search.Y_start).count()
            elif d.Y_end:
                nmb = PdfsBudget.objects.filter(year__lte=search.Y_end).count()
            else:
                nmb = PdfsBudget.objects.all().count()
            if nmb > 0:
                minutes = round(nmb / 8.5, 2)
            else:
                minutes = 0

            res = json.dumps(
                {'worked': True, 'id': search.pk, 'terms': terms3, 'years': years, 'name2': name, 'minutes': minutes})
            if request.POST['Snow'] == 'true':
                params = {'job': 'searchPDFs', 'token': 'dsdsfjjffgrggasdjjaslklakfadfhjhgdfkjdsfh'}
                requests.get('http://powerstructure.bath.ac.uk:8080/buildByToken/build', params=params)
            return HttpResponse(res, content_type='application/javascript')

    else:
        searchFin = CmdSearchPDFs.objects.filter(progress=1)
        searchRun = CmdSearchPDFs.objects.filter(progress__gt=0).filter(progress__lt=1)
        searchPlan2 = CmdSearchPDFs.objects.filter(progress=0)
        searchPlan = []
        for d in searchPlan2:
            if d.Y_start and d.Y_end:
                nmb = PdfsBudget.objects.filter(year__lte=d.Y_end).filter(year__gte=d.Y_start).count()
            elif d.Y_start:
                nmb = PdfsBudget.objects.filter(year__gte=d.Y_start).count()
            elif d.Y_end:
                nmb = PdfsBudget.objects.filter(year__lte=d.Y_end).count()
            else:
                nmb = PdfsBudget.objects.all().count()
            if nmb > 0:
                minutes = round(nmb / 8.5, 2)
            else:
                minutes = 0
            searchPlan.append({'minutes': minutes, 'pk': d.pk, 'name': d.name, 'Y_end': d.Y_end, 'Y_start': d.Y_start,
                               'search_terms': d.search_terms})
        return render(request, 'searchPDFscomp.html',
                      {'searchFin': searchFin, 'searchRun': searchRun, 'searchPlan': searchPlan})


@login_required(login_url='/login/')
def show_search_all_pdfs(request, id_search):
    search = CmdSearchPDFs.objects.get(pk=int(id_search))
    res = search.hits.all()

    paginator = Paginator(res, 25)  # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        res = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        res = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        res = paginator.page(paginator.num_pages)
    res2 = []
    for x in res:
        res2.append((x, PdfsBudget.objects.get(pk=int(x.pdf))))
    return render(request, 'searchPDFsdetail.html', {'search': search, 'res': res, 'res2': res2})
