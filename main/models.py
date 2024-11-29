from django.db import models
from viewflow.fields import CompositeKey


class Category(models.Model):
   id_category = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=500)
   mat_exp = models.FloatField()
   sigm = models.FloatField()
   count = models.IntegerField()

   class Meta:
      db_table = "categorymetric"


class Report(models.Model):
   id = CompositeKey(columns=['index', 'column'])
   index = models.BigIntegerField(default=0)
   column = models.BigIntegerField(default=0)
   type = models.CharField(max_length=500)
   reason = models.CharField(max_length=500)
   advice = models.CharField(max_length=200, default="")

   class Meta:
      unique_together = (('index', 'column'))
      db_table = "report"


class YandexOffer(models.Model):
   index = models.BigIntegerField(primary_key=True)
   available = models.BooleanField(null=True)
   price = models.FloatField(null=True)
   currencyId = models.CharField(max_length=500, null=True)
   categoryId = models.BigIntegerField(null=True)
   picture = models.CharField(max_length=500, null=True)
   name = models.CharField(max_length=500, null=True)
   vendor = models.CharField(max_length=500, null=True)
   description = models.CharField(max_length=10000, null=True)
   barcode = models.CharField(max_length=500, null=True)
   article = models.CharField(max_length=1000, null=True)
   rating = models.FloatField(null=True)
   review_amount = models.BigIntegerField(null=True)
   sale = models.FloatField(null=True)
   newby = models.BooleanField(null=True)