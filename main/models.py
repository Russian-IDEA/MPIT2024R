from django.db import models


class Category(models.Model):
   id_category = models.IntegerField(primary_key=True)
   name = models.CharField(max_length=50)
   mat_exp = models.FloatField()
   sigm = models.FloatField()
   count = models.IntegerField()

   class Meta:
      db_table = "CategoryMetric"