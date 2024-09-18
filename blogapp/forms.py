from django import forms
from .models import Tarea
from .models import Eventos
 
 #Creamos el form para las tareas(Comentarios)
class Taskform(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ["titulo", "descripcion", "fecha_limite"]
        widgets = {
            "titulo": forms.TextInput(attrs={"class":"form-control", "placeholder": "Escribe un titulo"}),
            "descripcion": forms.Textarea(attrs={"class":"form-control mb-3", "placeholder": "Escribe una descripcion "}),
            "fecha_limite": forms.DateInput(attrs={"class":"form-control mb-3",'type': 'date'}),
        }
       
#Creamos el form para los eventos(Cambios de turno)       
class Taskform_eventos(forms.ModelForm):
    # Definir las opciones para el campo de selección 'turno_actualizado'
    TURNOS_CHOICES = [
        ('M', 'M'),
        ('T', 'T'),
        ('N', 'N'),
        ('L', 'L'),
        ('V', 'V'),
        ('B', 'B'),
    ]
   
    # Definir el campo de selección 'turno_actualizado' utilizando forms.ChoiceField
    turno_actualizado = forms.ChoiceField(choices=TURNOS_CHOICES, widget=forms.Select(attrs={"class": "form-control"}))
   #Usamos el Meta para definir la estructura del formulario
    class Meta:
         #Definimos que este modelo es para Eventos
        model = Eventos
        #Creamos los campos del formulario
        fields = ["id_evento", "usuario","turno_actualizado", "fecha_inicio", "fecha_fin", "observaciones"]
        #Personalizamos los campos del fomulario diciendo que tipo de campo es y definiendo la clase para el css 
        widgets = {
            "usuario":forms.TextInput(attrs={"class":"form-control ",'type': 'text',"readonly": "readonly"}),
            "fecha_inicio": forms.DateInput(attrs={"class":"form-control ",'type': 'date'}),  # Utilizando forms.DateInput con type='date'
            "fecha_fin": forms.DateInput(attrs={"class":"form-control mb-3",'type': 'date'}),  # Utilizando forms.DateInput con type='date'
            "observaciones": forms.TextInput(attrs={"class":"form-control ",'type': 'text'})
        }
   