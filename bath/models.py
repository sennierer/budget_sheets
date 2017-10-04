from __future__ import unicode_literals

from django.db import models

class ExtractAooRef(models.Model):
    aootype = models.CharField(max_length=10, blank=True)
    aookey = models.IntegerField(blank=True, null=True)
    aooname = models.CharField(primary_key=True,max_length=255, blank=True)
    aoosort = models.CharField(max_length=100, blank=True)
    welsh = models.CharField(max_length=1, blank=True)
    master = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'extract_aoo_ref'

class ExtractCharity(models.Model):
    regno = models.IntegerField(primary_key=True,blank=True, null=True)
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
    class Meta:
        managed = False
        db_table = 'extract_charity'

class ExtractFinancial(models.Model):
    regno = models.IntegerField(primary_key=True,blank=True, null=True)
    fystart = models.DateTimeField(blank=True, null=True)
    fyend = models.DateTimeField(blank=True, null=True)
    income = models.IntegerField(blank=True, null=True)
    expend = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'extract_financial'

class ExtractTrustee(models.Model):
    regno = models.IntegerField(primary_key=True,blank=True, null=True)
    trustee = models.CharField(max_length=255, blank=True)
    class Meta:
        managed = False
        db_table = 'extract_trustee'

class PdfsBudget(models.Model):
    id = models.IntegerField(primary_key=True)
    regno = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True)
    date = models.IntegerField(blank=True, null=True)
    include = models.BooleanField(blank=True,null=True,default=False)
    class Meta:
        managed = False
        db_table = 'pdfs_budget'

class budget_flow(models.Model):
    regno = models.IntegerField()
    id_budget_file = models.IntegerField()
    type_flow_coices = (('in','Income'),('out','Spending'))
    type_of_flow = models.CharField(max_length=3, choices=type_flow_coices,default='in')
    amount = models.IntegerField()
    currency = models.CharField(max_length=255, blank=True)