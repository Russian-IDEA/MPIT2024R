from django.db import models


class Category(models.Model):
   id_category = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=50)
   mat_exp = models.FloatField()
   sigm = models.FloatField()
   count = models.IntegerField()

   class Meta:
      db_table = "CategoryMetric"


class Reason(models.Model):
   index = models.IntegerField(primary_key=True)
   column = models.CharField(max_length=50)
   type = models.CharField(max_length=50)
   reason = models.CharField(max_length=50)

   class Meta:
      db_table = "report"