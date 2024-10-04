from django.contrib import admin
from .models import(
  Housings, HousingPictures
)
# Register your models here.
admin.site.register(
  [Housings, HousingPictures]
)