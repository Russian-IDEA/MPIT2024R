from django.db import models


class Category(models.Model):
   id_category = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=50)
   mat_exp = models.FloatField()
   sigm = models.FloatField()
   count = models.IntegerField()

   class Meta:
      db_table = "CategoryMetric"


class Report(models.Model):
   index = models.IntegerField(primary_key=True)
   column = models.CharField(max_length=50)
   type = models.CharField(max_length=50)
   reason = models.CharField(max_length=50)

   class Meta:
      db_table = "report"


class YandexOffer(models.Model):
   index = models.IntegerField(primary_key=True)
   available = models.BooleanField(null=True)
   price = models.FloatField(null=True)
   currencyId = models.CharField(max_length=50, null=True)
   categoryId = models.IntegerField(null=True)
   picture = models.CharField(max_length=50, null=True)
   name = models.CharField(max_length=50, null=True)
   vendor = models.CharField(max_length=50, null=True)
   description = models.CharField(max_length=50, null=True)
   barcode = models.IntegerField(null=True)
   article = models.IntegerField(null=True)
   rating = models.FloatField(null=True)
   review_amount = models.IntegerField(null=True)
   sale = models.FloatField(null=True)
   newby = models.BooleanField(null=True)