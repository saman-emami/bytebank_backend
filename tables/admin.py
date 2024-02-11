from django.contrib import admin
from .models import TableBluePrint, TableFieldBluePrint, TableInstance,TableInstanceField, Dummy, Database
admin.site.register(TableBluePrint)
admin.site.register(TableFieldBluePrint)
admin.site.register(TableInstance)
admin.site.register(TableInstanceField)
admin.site.register(Dummy)
admin.site.register(Database)

