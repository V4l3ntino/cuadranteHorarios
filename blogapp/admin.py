from django.contrib import admin
from .models import User, Eventos, Permutado, Parte, Incidencia, Faltas
# Register your models here.
admin.site.register(User)
admin.site.register(Eventos)
admin.site.register(Permutado)
admin.site.register(Parte)
admin.site.register(Incidencia)
admin.site.register(Faltas)