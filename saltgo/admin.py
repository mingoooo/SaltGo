from django.contrib import admin
from saltgo import models

# Register your models here.
admin.site.register(models.Jobs_Result)
admin.site.register(models.Jobs_History)
admin.site.register(models.Minion_Status)
admin.site.register(models.State_File)
admin.site.register(models.Permission)

