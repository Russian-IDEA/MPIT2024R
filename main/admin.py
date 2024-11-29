from django.contrib import admin
from .models import Category, Report, YandexOffer, Current

# Register your models here.
admin.site.register(Category)
admin.site.register(Report)
admin.site.register(YandexOffer)
admin.site.register(Current)