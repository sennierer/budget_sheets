from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class ExtractAooRef(models.Model):
    id = models.AutoField(primary_key=True)
    aootype = models.CharField(max_length=10, blank=True)
    aookey = models.IntegerField(blank=True, null=True)
    aooname = models.CharField(max_length=255)
    aoosort = models.CharField(max_length=100, blank=True)
    welsh = models.CharField(max_length=1, blank=True)
    master = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'extract_aoo_ref'

class ExtractCharity(models.Model):
    id = models.AutoField(primary_key=True)
    regno = models.IntegerField(blank=True)
    subno = models.IntegerField(blank=True, null=True)
    name = models.CharField(max_length=150, blank=True)
    orgtype = models.CharField(max_length=10, blank=True)
    gd = models.TextField(blank=True)
    aob = models.TextField(blank=True)
    aob_defined = models.IntegerField(blank=True, null=True)
    nhs = models.CharField(max_length=1, blank=True)
    ha_no = models.IntegerField(blank=True, null=True)
    corr = models.CharField(max_length=255, blank=True)
    add1 = models.CharField(max_length=35, blank=True)
    add2 = models.CharField(max_length=35, blank=True)
    add3 = models.CharField(max_length=35, blank=True)
    add4 = models.CharField(max_length=35, blank=True)
    add5 = models.CharField(max_length=35, blank=True)
    postcode = models.CharField(max_length=8, blank=True)
    phone = models.CharField(max_length=400, blank=True)
    fax = models.IntegerField(blank=True, null=True)
    pdfs = models.NullBooleanField(blank=True,null=True,default=False)
    include = models.NullBooleanField(blank=True,null=True,default=False)
    not_interested = models.NullBooleanField(blank=True,null=True,default=False)
    not_interested_text = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'extract_charity'

class ExtractFinancial(models.Model):
    id = models.AutoField(primary_key=True)
    regno = models.IntegerField(blank=True)
    fystart = models.DateTimeField(blank=True, null=True)
    fyend = models.DateTimeField(blank=True, null=True)
    income = models.IntegerField(blank=True, null=True)
    expend = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'extract_financial'

class ExtractTrustee(models.Model):
    id = models.AutoField(primary_key=True)
    regno = models.IntegerField(blank=True)
    trustee = models.CharField(max_length=255, blank=True)
    class Meta:
        managed = False
        db_table = 'extract_trustee'

class PdfsBudget(models.Model):
    id = models.AutoField(primary_key=True)
    regno = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True)
    date = models.IntegerField(blank=True, null=True)
    include = models.NullBooleanField(blank=True,null=True,default=False)
    downloaded = models.NullBooleanField(blank=True,null=True,default=False)
    finalized = models.NullBooleanField(blank=True,null=True,default=False)
    notes = models.TextField(blank=True)
    notes_index = models.NullBooleanField(blank=True,null=True,default=False)
    no_data = models.NullBooleanField(blank=True,null=True,default=False)
    class Meta:
        managed = False
        db_table = 'pdfs_budget'

class budget_flow(models.Model):
    id = models.AutoField(primary_key=True)
    regno = models.IntegerField()
    recip_don_regno = models.IntegerField(blank=True)
    recip_don = models.CharField(max_length=255, blank=True)
    id_budget_file = models.IntegerField()
    type_flow_coices = (('in','Income'),('out','Spending'))
    type_of_flow = models.CharField(max_length=3, choices=type_flow_coices,default='in')
    amount = models.IntegerField()
    currency = models.CharField(max_length=255, blank=True)
    nmb_of_grants = models.IntegerField()
    notes_grants = models.TextField(blank=True)
    user_name = models.CharField(max_length=255)
    kind_recip_don_choices = (('Person','Natural Person'),('corp','Corporation'),('charity','Charity'),('tt','Think Tank'),('lawF','Law Firm'),('marketF','Marketing Firm'),('gov','Governmental Body'),('oth','other'))
    kind_recip_don = models.CharField(max_length=8, choices=kind_recip_don_choices,default='charity')
    notes_recip_don = models.TextField(blank=True)
    url_recip_don = models.URLField(blank=True)
    class Meta:
        managed = False
        db_table = 'budget_flow'

class budget_flow_others(models.Model):
    id = models.AutoField(primary_key=True)
    prim_regno = models.IntegerField(blank=True)
    prim_name = models.CharField(max_length=255)
    recip_don_regno = models.IntegerField(blank=True)
    recip_don = models.CharField(max_length=255, blank=True)
    id_budget_file = models.IntegerField()
    type_flow_coices = (('in','Income'),('out','Spending'))
    type_of_flow = models.CharField(max_length=3, choices=type_flow_coices,default='in')
    amount = models.IntegerField()
    currency = models.CharField(max_length=255, blank=True)
    nmb_of_grants = models.IntegerField()
    notes_grants = models.TextField(blank=True)
    user_name = models.CharField(max_length=255)
    kind_recip_don_choices = (('Person','Natural Person'),('corp','Corporation'),('charity','Charity'),('tt','Think Tank'),('lawF','Law Firm'),('marketF','Marketing Firm'),('gov','Governmental Body'),('oth','other'))
    kind_recip_don = models.CharField(max_length=8, choices=kind_recip_don_choices,default='charity')
    notes_recip_don = models.TextField(blank=True)
    url_recip_don = models.URLField(blank=True)
    ressource = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'budget_flow'

class ConCharityBudgetflow(models.Model):
    id_charity = models.ForeignKey(ExtractCharity, db_column='id_charity')
    id_budgetflow = models.ForeignKey(budget_flow, db_column='id_budgetFlow') # Field name made lowercase.
    id = models.AutoField(primary_key=True)
    #other_flow = models.NullBooleanField(blank=True,null=True,default=False) # If the flow was not found in the charity commission database this is true
    class Meta:
        managed = False
        db_table = 'con_charity_budgetFlow'

class CmdSearchPDFsTerm(models.Model):
    term = models.CharField(max_length=255)

class CmdSearchPDFsHits(models.Model):
    snippet = models.TextField(blank=True)
    pdf = models.IntegerField()
    term = models.ForeignKey(CmdSearchPDFsTerm,blank=True,null=True)


class CmdSearchPDFs(models.Model):
    name = models.CharField(max_length=255)
    progress = models.FloatField(default=0)
    user = models.ForeignKey(User,blank=True,null=True)
    started = models.DateTimeField(auto_now_add=True)
    Y_start = models.IntegerField(blank=True,null=True)
    Y_end = models.IntegerField(blank=True,null=True)
    hits = models.ManyToManyField(CmdSearchPDFsHits)
    search_terms = models.ManyToManyField(CmdSearchPDFsTerm)



