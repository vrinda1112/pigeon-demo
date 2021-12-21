from django.contrib import admin
from wip.models import *
# Register your models here.
tables = [
    LIMChecklist,
    LIMParameters,
    LIMProductionCounters,
    UserProfile,
    ProductionSheetLIM
]

for table in tables:
    admin.site.register(table)
