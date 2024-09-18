import os
from django.db import models
from django.contrib.auth.models import User as Usuario
from django.dispatch import receiver
from django.db.models.signals import post_init
from datetime import datetime, timezone
from django.shortcuts import get_object_or_404
import pytz
import json

# Create your models here.
class User(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    maquina = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100, default='Operario')
    conocimientos = models.CharField(max_length=100, default='null')
    turno = models.CharField(max_length=20)
    evento = models.BooleanField(default=False)
    permutado = models.BooleanField(default=False)
    fechaInicio = models.CharField(max_length=10, blank=True, null=True, db_column="fecha_inicio")
    fechaBaja = models.CharField(max_length=10, blank=True, null=True, db_column="fecha_baja")
    updateTurno = models.BooleanField(default=False, null=True, db_column="update_turno")
    expediente = models.IntegerField(default=0)
    faltas = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Incidencia(models.Model):
    id = models.AutoField(primary_key=True)
    operario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidencias')
    fecha_incidencia = models.CharField(max_length=16, null=True)
    fecha_reporte = models.CharField(max_length=16, null=True)
    referencia_articulo = models.IntegerField(null=True)
    nombre_articulo = models.CharField(max_length=255, null=True)
    numero_pedido = models.IntegerField(null=True)
    unidades_totales_pedido = models.IntegerField(null=True)
    unidades_mal_marcadas_revisadas = models.IntegerField(null=True)
    coste_incidencia = models.IntegerField(null=True)
    tecnica_marcado = models.CharField(max_length=255, null=True)
    responsable_turno = models.TextField(null=True, blank=True)
    personas_implicadas = models.TextField(null=True, blank=True)
    persona_quien_detecta_error = models.TextField(null=True, blank=True)
    testigos = models.TextField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    creador = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    imagen = models.ImageField(upload_to='incidencias/', null=True, blank=True)

    def __str__(self):
        return f"Incidencia {self.id} - Usuario: {self.operario.nombre}"

class Parte(models.Model):
    id = models.AutoField(primary_key=True)
    operario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partes')
    numero_pedido = models.IntegerField(null=True)
    numero_fabricacion = models.IntegerField(null=True)
    unidades = models.IntegerField(null=True)
    fecha_reporte = models.CharField(max_length=16, null=True)
    observacion = models.TextField(null=True, blank=True)
    observacion_responsable = models.TextField(null=True, blank=True)
    observacion_operario = models.TextField(null=True, blank=True)
    maquina = models.CharField(max_length=255, null=True)
    motivo = models.CharField(max_length=255, null=True)
    accion = models.CharField(max_length=255, null=True)
    creador = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"Parte {self.id} - Usuario: {self.operario.nombre}"
    
    
# Un evento puede representar los nuevos turnos o las licencias de cada usuario, ese valor lo representa el atributo turno_actualizado
class Eventos(models.Model):
    id_evento = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos')
    fecha_inicio = models.CharField(max_length=10, null=True)
    fecha_fin = models.CharField(max_length=10, null=True)
    turno_actualizado = models.CharField(max_length=10)
    observaciones = models.CharField(max_length=255)
    # El creador hace referencia al usuario de la aplicación que ha creado el evento
    creador = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    orden = models.IntegerField(null=True)

    def __str__(self):
        return f"Evento {self.id_evento} - Usuario: {self.usuario.nombre}"

class Faltas(models.Model):
    id_evento = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='falta')
    fecha_inicio = models.CharField(max_length=10, null=True)
    fecha_fin = models.CharField(max_length=10, null=True)
    turno_actualizado = models.CharField(max_length=10)
    observaciones = models.CharField(max_length=255)
    # El creador hace referencia al usuario de la aplicación que ha creado el evento
    creador = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    orden = models.IntegerField(null=True)

    def __str__(self):
        return f"Evento {self.id_evento} - Usuario: {self.usuario.nombre}"
    
class Permutado(models.Model):
    id_permutado = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permutados')
    fecha_inicio = models.CharField(max_length=10, null=True)
    fecha_fin = models.CharField(max_length=10, null=True)
    tipo = models.CharField(max_length=250)
    maquina = models.BooleanField(default=False)
    auxiliar = models.CharField(max_length=250)
    # El creador hace referencia al usuario de la aplicación que ha creado el evento
    creador = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Evento {self.id_permutado} - Usuario: {self.usuario.nombre}"
    
class Tarea(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    fechacompleto = models.DateField(null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_actual = models.DateField(default=datetime.now)
    completado = models.BooleanField(default=False)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.titulo  + " Hecha por " + self.user.username
    
# Este metodo se ejecuta por cada usuario, instance hace referencia al usuario
@receiver(post_init, sender=User)
def initialize_rotacion(sender, instance, **kwargs):
    zona_horaria_espana = pytz.timezone('Europe/Madrid')
    # Esto saca la fecha de hoy acorde a la hora de españa
    fecha_hoy = datetime.now(zona_horaria_espana).date()
    dia_semana = fecha_hoy.weekday()
    instance.rotacion = []
    
    # if dia_semana == 1:
    #     instance.updateTurno = True
    #     #JORNADA ESTATICA
    #     if instance.turno == "estatica-M" or instance.turno == "estatica-T" or instance.turno == "estatica-N":
    #         instance.updateTurno = False
            
    #     instance.save()
    
    # if dia_semana == 0:
    #     if instance.updateTurno == True:
    #         #JORNADA COMPLETA
    #         if instance.turno == 'Mañana':
    #             instance.turno = 'Tarde'

    #         elif instance.turno == 'Tarde':
    #             instance.turno = 'Noche'

    #         elif instance.turno == "Noche":
    #             instance.turno = 'Mañana'
            
    #         #JORNADA PARCIAL
    #         elif instance.turno == "sinMañana-T":
    #             instance.turno = "sinMañana-N"

    #         elif instance.turno == "sinMañana-N":
    #             instance.turno = "sinMañana-T"
                
    #         elif instance.turno == "sinTarde-M":
    #             instance.turno = "sinTarde-N"

    #         elif instance.turno == "sinTarde-N":
    #             instance.turno = "sinTarde-M"
            
    #         elif instance.turno == "sinNoche-M":
    #             instance.turno = "sinNoche-T"

    #         elif instance.turno == "sinNoche-T":
    #             instance.turno = "sinNoche-M"

                
    #         instance.updateTurno = False
    #         instance.save()
            
    try:
        #Valida si la el contrato de cada usuario ha terminado
        if instance.fechaBaja is not None and isinstance(instance.fechaBaja, str):
            #Convierte la fecha de formato String a Date
            fecha_de_baja = datetime.strptime(instance.fechaBaja, '%d-%m-%Y').date()
            #Esta condición valida se la fecha de baja es inferior a la fecha actual
            if fecha_de_baja is not None and fecha_de_baja < fecha_hoy:
                print("El usuario",instance.nombre," ha sido borrada de la base de datos por terminar su contrato")

                data = {
                    "id": instance.id,
                    "nombre": instance.nombre,
                    "maquina": instance.maquina,
                    "turno": instance.turno,
                    "conocimientos": instance.conocimientos,
                    "fecha_inicio": instance.fechaInicio,
                    "fecha_fin": instance.fechaBaja
                }

                ruta_file = "json\\operarios_borrados.json"

                if os.path.exists(ruta_file):
                    with open(ruta_file, 'r') as f:
                        try:
                            lista = json.load(f)
                        except json.JSONDecodeError:
                            lista = []
                else:
                    lista = []

                lista.append(data)

                with open(ruta_file, 'w') as f:
                    json.dump(lista, f, indent=4)
                

                instance.delete()
                return
    except ValueError as e:
        fecha_de_baja = None
    
    
    #Inicialiamos el atributo,esto almacenaría el turno del usuario según el día en el que se encuentre el filtro, esto se utiliza en el POST de turnodefecto
    instance.rotacion_fecha = ""
    # Esto sirve para indicar que objetos van a mostrar la rotación 6 meses y los que solo muestra un mes, por defecto intentamos sacar los turnos de 6 meses
    instance.limiteRotacion = False
    # Crea un array de dos items, apellido y nombre
    apellido_nombre = instance.nombre.split(',')
    if len(apellido_nombre) >= 2:
        instance.nombre =  apellido_nombre[1]
        instance.apellido = apellido_nombre[0]
    if len(apellido_nombre) == 1:
        instance.apellido = "‎" 
        
    # Esto almacena las tres posibles listas que pueden existir. Luego según la rotación del operario en la semana actual asigna su lista correspondiente
    #JORNADA COMPLETA
    rotacion_mañana = instanciaTurno.turno.rotacionMañana
    rotacion_tarde = instanciaTurno.turno.rotacionTarde
    rotacion_noche = instanciaTurno.turno.rotacionNoche
    
    rotacion_mañanaR = instanciaTurno.turno.rotacionMañanaR
    rotacion_tardeR = instanciaTurno.turno.rotacionTardeR
    rotacion_nocheR= instanciaTurno.turno.rotacionNocheR

    #JORNADA PARCIAL
    rotacion_sinMañana_T = instanciaTurno.turno.rotacionSinMañana_Tarde
    rotacion_sinMañana_N = instanciaTurno.turno.rotacionSinMañana_Noche

    rotacion_sinTarde_M = instanciaTurno.turno.rotacionSinTarde_Mañana    
    rotacion_sinTarde_N = instanciaTurno.turno.rotacionSinTarde_Noche

    rotacion_sinNoche_M = instanciaTurno.turno.rotacionSinNoche_Mañana    
    rotacion_sinNoche_T = instanciaTurno.turno.rotacionSinNoche_Tarde    

    #JORNADA ESTÁTICA
    rotacion_estatica_M = instanciaTurno.turno.rotacion_estatica_Mañana
    rotacion_estatica_T = instanciaTurno.turno.rotacion_estatica_Tarde
    rotacion_estatica_N = instanciaTurno.turno.rotacion_estatica_Noche

    #IMPORTANTE! dejar el .copy() para no afectar a la lista original cuando se haga un cambio, 
    # esto permite que se puedan editar los eventos correctamente.

    # JORNADA COMPLETA
    if instance.turno == "Mañana" and instance.categoria == "TALLER":
        instance.rotacion = rotacion_mañana.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "Tarde" and instance.categoria == "TALLER":
        instance.rotacion = rotacion_tarde.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "Noche" and instance.categoria == "TALLER":
        instance.rotacion = rotacion_noche.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    # JORNADA COMPLETA RESPONSABLE
    if instance.turno == "Mañana" and instance.categoria == "RESPONSABLE":
        instance.rotacion = rotacion_mañanaR.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "Tarde" and instance.categoria == "RESPONSABLE":
        instance.rotacion = rotacion_tardeR.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "Noche" and instance.categoria == "RESPONSABLE":
        instance.rotacion = rotacion_nocheR.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]

    # JORNADAS PARCIALES
    if instance.turno == "sinMañana-T":
        instance.rotacion = rotacion_sinMañana_T.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "sinMañana-N":
        instance.rotacion = rotacion_sinMañana_N.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "sinTarde-M":
        instance.rotacion = rotacion_sinTarde_M.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "sinTarde-N":
        instance.rotacion = rotacion_sinTarde_N.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "sinNoche-M":
        instance.rotacion = rotacion_sinNoche_M.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "sinNoche-T":
        instance.rotacion = rotacion_sinNoche_T.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]

    # JORNADAS ESTÁTICAS
    if instance.turno == "estatica-M":
        instance.rotacion = rotacion_estatica_M.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "estatica-T":
        instance.rotacion = rotacion_estatica_T.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]
    if instance.turno == "estatica-N":
        instance.rotacion = rotacion_estatica_N.copy()[:62]
        #Lista alternativa para cuando queramos renderizar solo un mes, [:31] esto significa que acortamos la lista 31 posiciones,es decir que saca los primeros 31 elementos de la lista ,[31:] esto haría el proceso inverso, elimina los 31 primeros items de la lista
        instance.rotacionMes = instance.rotacion[:31]

    # Si un usuario tiene uno o varios eventos se modifica su lista correspondiente 
    if instance.evento == True:
        #JORNADAS COMPLETAS
        if instance.turno == "Mañana" and instance.categoria == "TALLER":
            instance.rotacion = rotacion_mañana.copy()
        if instance.turno == "Tarde" and instance.categoria == "TALLER":
            instance.rotacion = rotacion_tarde.copy()
        if instance.turno == "Noche" and instance.categoria == "TALLER":
            instance.rotacion = rotacion_noche.copy()
        #JORNADAS COMPLETAS REPONSABLE
        if instance.turno == "Mañana" and instance.categoria == "RESPONSABLE":
            instance.rotacion = rotacion_mañanaR.copy()
        if instance.turno == "Tarde" and instance.categoria == "RESPONSABLE":
            instance.rotacion = rotacion_tardeR.copy()
        if instance.turno == "Noche" and instance.categoria == "RESPONSABLE":
            instance.rotacion = rotacion_nocheR.copy()
            
        #JORNADAS PARCIALES
        if instance.turno == "sinMañana-T":
            instance.rotacion = rotacion_sinMañana_T.copy()

        if instance.turno == "sinMañana-N":
            instance.rotacion = rotacion_sinMañana_N.copy()

        if instance.turno == "sinTarde-M":
            instance.rotacion = rotacion_sinTarde_M.copy()

        if instance.turno == "sinTarde-N":
            instance.rotacion = rotacion_sinTarde_N.copy()

        if instance.turno == "sinNoche-M":
            instance.rotacion = rotacion_sinNoche_M.copy()

        if instance.turno == "sinNoche-T":
            instance.rotacion = rotacion_sinNoche_T.copy()
        
        # JORNADAS ESTÁTICAS
        if instance.turno == "estatica-M":
            instance.rotacion = rotacion_estatica_M.copy()
        if instance.turno == "estatica-T":
            instance.rotacion = rotacion_estatica_T.copy()
        if instance.turno == "estatica-N":
            instance.rotacion = rotacion_estatica_N.copy()

        instanciaTurno.funcion_eventos(instance)
        instance.rotacion = instance.rotacion[:62]


class TurnosRotativos:
    def __init__(self):
        #COMPLETA
        self.rotacionMañana = self.generar_turnos_rotativos('M')
        self.rotacionTarde = self.generar_turnos_rotativos('T')
        self.rotacionNoche = self.generar_turnos_rotativos('N')
        
        self.rotacionMañanaR = self.generar_turnos_rotativos('M', responsable=True)
        self.rotacionTardeR = self.generar_turnos_rotativos('T', responsable=True)
        self.rotacionNocheR = self.generar_turnos_rotativos('N', responsable=True)
        
        #PARCIAL SIN MAÑANA
        self.rotacionSinMañana_Tarde = self.generar_turnos_rotativos("T", sinMañana=True)
        self.rotacionSinMañana_Noche = self.generar_turnos_rotativos("N", sinMañana=True)
        #PARCIAL SIN TARDE
        self.rotacionSinTarde_Mañana = self.generar_turnos_rotativos("M", sinTarde=True)
        self.rotacionSinTarde_Noche = self.generar_turnos_rotativos("N", sinTarde=True)
        #PARCIAL SIN NOCHE
        self.rotacionSinNoche_Mañana = self.generar_turnos_rotativos("M", sinNoche=True)
        self.rotacionSinNoche_Tarde = self.generar_turnos_rotativos("T", sinNoche=True)

        #ESTATICA
        self.rotacion_estatica_Mañana = self.generar_turnos_rotativos("M", noRota=True)
        self.rotacion_estatica_Tarde = self.generar_turnos_rotativos("T", noRota=True)
        self.rotacion_estatica_Noche = self.generar_turnos_rotativos("N", noRota=True)

        
    def generar_turnos_rotativos(self, turno_actual, sinMañana=None, sinTarde=None, sinNoche=None, noRota=None, responsable=None):
        turnos_rotativos = []
        turnos_rotativos.append(turno_actual)
        
        rotacion_operario = {"N":0,"T":1,"M":2}
        
        if responsable:
            rotacion_operario = {"M":0,"T":1,"N":2}
        
        if sinMañana:
            rotacion_operario = {"N":0,"T":1}

        if sinTarde:
            rotacion_operario = {"N":0,"M":1}

        if sinNoche:
            rotacion_operario = {"T":0,"M":1}
        
        if noRota:
            rotacion_operario = {turno_actual:0}

        # Obtener la fecha total (dia, mes, año, hora) del día de hoy
        hoy_fecha_total = datetime.now()
        # Obtener el día de la semana actual, le sumo uno porque el lunes empieza por 0
        dia_semana = hoy_fecha_total.weekday() + 1

        # Calcula cuántos días quedan para terminar la semana a partir del día de hoy
        primera_semana = 7 - dia_semana

        # Saco el turno de la primera semana
        for _ in range(primera_semana):
            turnos_rotativos.append(turno_actual)

        # Un año tiene 52 semanas saco el turno de todo el año
        for _ in range(104):
            # Esto lo que hace es hacer la rotación según el diccionario sin que sobrepase la posición
            turno_actual_posicion = (rotacion_operario[turno_actual] + 1) % len(rotacion_operario)
            # Esto saca la clave si coincide con el valor de la posición en cualquier item del diccionario de rotacion_operario
            turno_actual = next(nombre for nombre, posicion in rotacion_operario.items() if posicion == turno_actual_posicion)
            # De cada semana guardo el turno en la lista
            for _ in range(7):
                turnos_rotativos.append(turno_actual)

        # Devuelvo la lista acortada ya que tengo la primera semana y un año entero juntos
        return turnos_rotativos[:len(turnos_rotativos)-primera_semana]

class instanciaTurno:
    turno = TurnosRotativos()
    def funcion_eventos(user):
        #Buscamos primero todos los eventos existentes en la base de datos para luego iterar por cada uno de ellos
        eventos = Eventos.objects.all()
        for event in eventos:
            #Si la clave foránea del evento coincide con el usuario asociado se procede a modificar la lista
            if event.usuario_id == user.id:
                    #Para modificar la lista necesitamos sacar las fechas de inicio, fin para luego sacar los dias previos y los dias que dura ese evento
                    # Crear la zona horaria para España
                    zona_horaria_espana = pytz.timezone('Europe/Madrid')
                    # Obtener la fechas sin la hora, para eso se pone el .date() al final
                    #datetime.strptime(fechaini, "%Y-%m-%d")
                    fecha_inicio = datetime.strptime(event.fecha_inicio, "%Y-%m-%d").date()
                    fecha_fin = datetime.strptime(event.fecha_fin, "%Y-%m-%d").date()
                    fecha_hoy = datetime.now(zona_horaria_espana).date()
                    dias_previos = (fecha_inicio - fecha_hoy).days
                    diferencia_dias = (fecha_fin - fecha_inicio).days + 1

                    #SI LA FECHA DE INICIO ES MENOR QUE LA FECHA ACTUAL EL VALOR DE LOS DÍAS PREVIOS CORRESPONDERÍA A LOS DÍAS PASADOS A PARTIR DEL DÍA DE HOY
                    if (fecha_inicio < fecha_hoy):
                        dias_previos = (fecha_hoy - fecha_inicio).days
                        diferencia_dias = (fecha_fin - fecha_hoy).days + 1
                    #SI EL EVENTO ESTA FUERA DE FECHA SE ELIMINA
                    if (fecha_fin < fecha_hoy):
                        evento = get_object_or_404(Eventos, pk=event.id_evento)
                        evento.delete()
                        break
                    #Con las fechas sacadas ya solo nos quedaría sacar la nueva lista del evento y modificar la lista actual del usuario
                    turnos_rotativos=[]
                    evento_actual = event.turno_actualizado
                    #Empezamos la lista agregando el mismo turno del evento para toda una semana
                    for _ in range(7):
                            turnos_rotativos.append(evento_actual)
                    #Luego continuamos con la rotacion con el resto de semanas, como resultado tendríamos la rotación de un año entero + una semana
                    for _ in range(52):
                        rotacion_operario = {"N":0,"T":1,"M":2}
                        if evento_actual == "L":
                            rotacion_operario = {"L":0}
                        if evento_actual == "V":
                            rotacion_operario = {"V":0}
                        if evento_actual == "B":
                            rotacion_operario = {"B":0}                            
                        # Esto lo que hace es hacer la rotación según el diccionario sin que sobrepase la posicion, explicado en el siguiente enlace -> https://chat.openai.com/share/c1651f02-571c-4bd6-b64d-1af898133ea0
                        turno_actual_posicion = (rotacion_operario[evento_actual] + 1) % len(rotacion_operario)
                        # Esto saca la clave si coincide con el valor de la posición en cualquier item del diccionario de rotacion_operario
                        evento_actual = next(nombre for nombre, posicion in rotacion_operario.items() if posicion == turno_actual_posicion)
                        # de cada semana guardo el turno en la lista
                        for _ in range(7):
                            turnos_rotativos.append(evento_actual)

                    # reemplaza la lista_turnos del usuario con el nuevo contenido
                    if fecha_inicio < fecha_hoy:
                        i = 0
                        count = 0
                        # Si la fecha de inicio es inferior a la actual se tiene que partir por la posición 0, por eso i vale 0 (representa el día de hoy) para que funcione bien el evento
                        #Cuando la fecha de inicio es inferior a la actual los días previos pasarían a significar los días pasados, por tanto descartamos de la lista los días pasados
                        turnos_eventos = turnos_rotativos[dias_previos:]
                        # Luego iteramos por cada item de la lista desde el inicio del evento hasta los días que dura el evento
                        for _ in range(len(turnos_eventos[:diferencia_dias])):
                            # Modificamos los items con los nuevos valores del evento en la lista del usuario correspondiente a partir de los dias previos (en este caso a partir del día de hoy)
                            user.rotacion[i] = turnos_eventos[count]
                            count += 1
                            i += 1
                        # También sacamos una lista alternativa de eventos limitada a un mes para cuando se cargen los turnos de todos los operarios de la bd
                        user.rotacionMes = user.rotacion[:31]
                    else:
                        # Si la fecha de inicio es superior a la actual se tiene que partir por la posición correspondiente a los días previos
                        i = dias_previos
                        
                        count = 0
                        # Dado que no hay días pasados no debemos acortar la lista para que la rotación sea correcta
                        turnos_eventos = turnos_rotativos
                        # Iteramos por cada item de la lista rotativa del usuario a partir de los días previos y modificamos su valor por el valor correspondiente al evento
                        for _ in range(len(turnos_eventos[:diferencia_dias])):
                            user.rotacion[i] = turnos_eventos[count]
                            count += 1
                            i += 1
                        # Lista alternativa para cuando se cargen todos los usuarios de la bd con sus turnos correspondientes
                        user.rotacionMes = user.rotacion[:31]
