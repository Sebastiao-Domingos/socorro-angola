from django.contrib import admin
from .models import ChecklistItem, Incidente, RelatorioIntervencao


admin.site.register(ChecklistItem)
admin.site.register(Incidente)
admin.site.register(RelatorioIntervencao)


# Register your models here.
