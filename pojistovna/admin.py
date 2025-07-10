from django.contrib import admin

# Register your models here.

from .models import InsuredPerson, Insurance, InsuranceType

admin.site.register(InsuranceType)
admin.site.register(InsuredPerson)
admin.site.register(Insurance)


