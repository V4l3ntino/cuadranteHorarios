import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
import pytz
from .models import User, Eventos, Permutado, Incidencia, Parte, Faltas
from django.db.models import Q
from datetime import datetime, timedelta, timezone
from django.http import HttpResponse
import locale
import json
from .forms import Taskform
from .forms import Taskform_eventos
from .models import Tarea
from django.contrib.auth.models import User as creator
from django.conf import settings

# Create your views here.
class TurnosRotativos:
    #El constructor de la clase
    def __init__(self):
        #JORNADA COMPLETA
        self.rotacionMañana = self.generar_turnos_rotativos('M')
        self.rotacionTarde = self.generar_turnos_rotativos('T')
        self.rotacionNoche = self.generar_turnos_rotativos('N')
        # RESPONSABLE
        self.rotacionMañanaR = self.generar_turnos_rotativos('M', responsable = True)
        self.rotacionTardeR = self.generar_turnos_rotativos('T', responsable = True)
        self.rotacionNocheR = self.generar_turnos_rotativos('N', responsable = True)
        
        #PARCIAL SIN MAÑANA
        self.rotacionSinMañana_Tarde = self.generar_turnos_rotativos("T", sinMañana=True)
        self.rotacionSinMañana_Noche = self.generar_turnos_rotativos("N", sinMañana=True)
        #PARCIAL SIN TARDE
        self.rotacionSinTarde_Mañana = self.generar_turnos_rotativos("M", sinTarde=True)
        self.rotacionSinTarde_Noche = self.generar_turnos_rotativos("N", sinTarde=True)
        #PARCIAL SIN NOCHE
        self.rotacionSinNoche_Mañana = self.generar_turnos_rotativos("M", sinNoche=True)
        self.rotacionSinNoche_Tarde = self.generar_turnos_rotativos("T", sinNoche=True)


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

        # !! No tocar, esto saca el turno de años futuros
        for _ in range(500000):
            # Esto lo que hace es hacer la rotación según el diccionario sin que sobrepase la posición
            turno_actual_posicion = (rotacion_operario[turno_actual] + 1) % len(rotacion_operario)
            # Esto saca la clave si coincide con el valor de la posición en cualquier item del diccionario de rotacion_operario
            turno_actual = next(nombre for nombre, posicion in rotacion_operario.items() if posicion == turno_actual_posicion)
            # De cada semana guardo el turno en la lista
            for _ in range(7):
                turnos_rotativos.append(turno_actual)

        # Devuelvo la lista acortada ya que tengo la primera semana y un año entero juntos
        return turnos_rotativos
#Creamos una clase para usar datos repetitivos   
class necesarios():
    #Creamos los operarios que se necesitan en cada tecnica
    autos = 23
    laser = 7
    tampo = 27
    pulpos = 14
    digital = 6
    bordado = 2
    termo = 1
    planchas = 32
    sublimacion = 30
    envasado = 20
    cosido = 0
    horno = 0
    # total = autos + laser + tampo + pulpos + digital + bordado + termo + planchas + sublimacion + envasado + cosido + horno
    #Creamos una lista con todas las tecnicas
    lista_maquina = ["autos","laser","tampo","pulpos","digital","bordado","termo","planchas","sublimacion","otros","cosido","horno","No tiene","INACTIVO"]
    #Creamos una lista con todos los turnos y operarios para hacer las redirecciones
    redirectsTurnos = ['turnoautos','turnolaser','turnotampo','turnopulpos','turnodigital','turnobordado','turnotermo','turnoplanchas','turnosublimacion','turnoenvasado','urlCosido','turnohorno','turnotodo','turnotodo']
    redirectsOperarios = ['operarios_autos','operarios_laser','operarios_tampo','operarios_pulpos','operarios_digital','operarios_bordado','operarios_termo','operarios_planchas','operarios_sublimacion','operarios_envasado','urlCosido','urlHorno','dashboard','dashboard']
    #Volvemos a poner los necesarios pero ahora solo con los nombres
    necesario = [autos,laser,tampo,pulpos,digital,bordado,termo,planchas,sublimacion,envasado,cosido,horno]
    user_request = []
    #Asignamos que el turno sea la función generar turnos rotativos
    turno = TurnosRotativos()
    #Establecemos que la zona horaria sea Madrid
    zona_horaria_espana = pytz.timezone('Europe/Madrid')
    #Establecemos que el minimo valor que pueden elegir sea la fecha de hoy
    minValueDate = datetime.now(zona_horaria_espana).date().strftime('%Y-%m-%d')
    #Establecemos la fecha de hoy
    hoy = datetime.now(zona_horaria_espana).date().strftime('%Y-%m-%d')


class colores():
    def __init__(self) -> None:
        self.green = 0
        self.red = -5
    
class colores_maquina():
    def __init__(self) -> None:
        self.autos = colores()
        self.laser = colores()
        self.tampo = colores()
        self.pulpos = colores()
        self.digital = colores()
        self.bordado = colores()
        self.termo = colores()
        self.planchas = colores()
        self.sublimacion = colores()
        self.envasado = colores()
        self.cosido = colores()
        self.horno = colores()    
    def update(self, maquina, color, valor):
        if maquina == "autos":
            if color == "green":
                self.autos.green = valor
            elif color == "red":
                self.autos.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "laser":
            if color == "green":
                self.laser.green = valor
            elif color == "red":
                self.laser.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "tampo":
            if color == "green":
                self.tampo.green = valor
            elif color == "red":
                self.tampo.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "pulpos":
            if color == "green":
                self.pulpos.green = valor
            elif color == "red":
                self.pulpos.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "digital":
            if color == "green":
                self.digital.green = valor
            elif color == "red":
                self.digital.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "bordado":
            if color == "green":
                self.bordado.green = valor
            elif color == "red":
                self.bordado.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "termo":
            if color == "green":
                self.termo.green = valor
            elif color == "red":
                self.termo.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "planchas":
            if color == "green":
                self.planchas.green = valor
            elif color == "red":
                self.planchas.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "sublimacion":
            if color == "green":
                self.sublimacion.green = valor
            elif color == "red":
                self.sublimacion.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "envasado":
            if color == "green":
                self.envasado.green = valor
            elif color == "red":
                self.envasado.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "cosido":
            if color == "green":
                self.cosido.green = valor
            elif color == "red":
                self.cosido.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

        if maquina == "horno":
            if color == "green":
                self.horno.green = valor
            elif color == "red":
                self.horno.red = valor
            else:
                raise ValueError(f"Color {color} no es válida")

class necesarios2():
    def __init__(self) -> None:
        self.autos = 23
        self.laser = 7
        self.tampo = 27
        self.pulpos = 14
        self.digital = 6
        self.bordado = 2
        self.termo = 1
        self.planchas = 32
        self.sublimacion = 30
        self.envasado = 20
        self.cosido = 0
        self.horno = 0
        self.necesario = [self.autos,self.laser,self.tampo,self.pulpos,self.digital,self.bordado,self.termo,self.planchas,self.sublimacion,self.envasado,self.cosido,self.horno]
        
    def update(self, maquina, valor):
        if maquina == "autos":
            self.autos = valor
            
        if maquina == "laser":
            self.laser = valor
            
        if maquina == "tampo":
            self.tampo = valor
            
        if maquina == "pulpos":
            self.pulpos = valor
            
        if maquina == "digital":
            self.digital = valor
            
        if maquina == "bordado":
            self.bordado = valor
            
        if maquina == "termo":
            self.termo = valor
            
        if maquina == "planchas":
            self.planchas = valor
            
        if maquina == "sublimacion":
            self.sublimacion = valor
            
        if maquina == "envasado":
            self.envasado = valor
            
        if maquina == "cosido":
            self.cosido = valor
            
        if maquina == "horno":
            self.horno = valor
            
        self.necesario = [self.autos,self.laser,self.tampo,self.pulpos,self.digital,self.bordado,self.termo,self.planchas,self.sublimacion,self.envasado,self.cosido,self.horno]
            
#Creamos una función por defecto que muestre la dashboard
@login_required
def index(request):
    #Llamamos a la función dashboard que esta donde se llama a la función generica de operarios
    return dashboard(request)

@login_required
def dashboard(request):
    return funcion_generica_operarios(request)


@login_required
def profile(request):
    if request.method == 'GET':
        if request.user.is_superuser and request.user.is_staff:
            users = creator.objects.all()
            return render(request, 'blogapp/adminDashboard/usuarios.html', {"users":users})
        else:
            return render(request, 'blogapp/user_profile.html', {"nombre":request.user.username})
    if request.method == "POST":
        if request.user.is_superuser and request.user.is_staff:
            search = request.POST.get("search")
            users = creator.objects.all()
            users = users.filter(username__icontains=search)
            return render(request, 'blogapp/adminDashboard/usuarios.html', {"users":users})
        else:
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            if password1 != password2:
                return render(request, 'blogapp/user_profile.html', {"nombre":request.user.username,"error":"Las contraseñas no coinciden"})        
            elif len(password2) < 5:
                return render(request, 'blogapp/user_profile.html', {"nombre":request.user.username,"error":"Mínimo 5 caracteres"})
            else:
                user = get_object_or_404(creator, pk=request.user.id)
                user.set_password(password2)
                user.save()
                return redirect('/dashboard')

@login_required
def appdetalle(request, user_id):
    user = get_object_or_404(creator, pk=user_id)
    if request.method == "GET":
        if request.user.is_superuser and request.user.is_staff:
            return render(request, 'blogapp/adminDashboard/user_detail.html', {"user":user})
    if request.method == "POST":
        if request.user.is_superuser and request.user.is_staff:
            nombre = request.POST.get("username")
            password = request.POST.get("password")
            estado = request.POST.get("estado").lower()
            
            if nombre != "":
                if creator.objects.filter(username__iexact=nombre).exclude(pk=user_id).exists():
                    return render(request, 'blogapp/adminDashboard/user_detail.html', {"user":user,"error":"El nombre ya está siendo usado"})
                else:
                    user.username = nombre
            if password != "":
                user.set_password(password)
            
            if estado == "admin":
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
            elif estado == "user":
                user.is_superuser = True
                user.is_staff = False
                user.is_active = True
            elif estado == "userinf":
                user.is_superuser = False
                user.is_staff = False
                user.is_active = True
            elif estado == "inactivo":
                user.is_active = False
            user.save()
            return redirect('profile')
@login_required
def appdelete(request, user_id):
    if request.method == "POST":
        if request.user.is_superuser and request.user.is_staff:
            user = get_object_or_404(creator, pk=user_id)
            user.delete()
            return redirect('profile')

@login_required
def appcreate(request):
    if request.method == "GET":
        if request.user.is_superuser and request.user.is_staff:
            return render(request, 'blogapp/adminDashboard/user_profile_add.html')
        else:
            return HttpResponse("USTED NO TIENE PRIVILEGIOS SUFIENTES PARA HACER ESTA ACCIÓN")
    if request.method == "POST":
        if request.user.is_superuser and request.user.is_staff:
            nombre = request.POST.get("username")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            estado = request.POST.get("estado")
            if password1 != password2:
                return render(request, 'blogapp/adminDashboard/user_profile_add.html', {"error":"Las contraseñas no coinciden"})
            elif len(password2) < 4:
                return render(request, 'blogapp/adminDashboard/user_profile_add.html', {"error":"Mínimo 5 caracteres"})
            else:
                if creator.objects.filter(username__iexact=nombre).exists():
                    return render(request, 'blogapp/adminDashboard/user_profile_add.html', {"error":"El nombre ya está siendo usado"})
                else:
                    if estado == "admin":
                        creator.objects.create_superuser(username=nombre, password=password2)
                    elif estado == "user":
                        user = creator.objects.create_user(username=nombre, password=password2)
                        user.is_superuser = True
                        user.save()
                    elif estado == "userinf":
                        creator.objects.create_user(username=nombre, password=password2)
                    return redirect('profile')
        
#Creamos una función para iniciar sesión
def login_view(request):
    permutas()
    #Si el metodo es GET:
    if request.method == 'GET':
        return render(request, "blogapp/login.html")
    #De lo contrario en el caso de que sea POST:
    else:
        #Se hace una comprobación con la función authenticate establecida por django para validar que las credenciales son correctas
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password']
        )
        #Si la autentificación falla da error y tiene que introducir los datos de nuevo
        if user is None:
            return render(request, 'blogapp/login.html', {"nombre":request.POST['username'],'error': 'Nombre o contraseña incorrectos'})
        #Si la autentificación esta bien le redirecciona a dashboard (Es la función en la que se muestran todos los operarios)
        login(request, user)
        return redirect('/dashboard')

def register(request):
    if request.method == "GET":
        return render(request, "blogapp/register.html")
    if request.method == "POST":
        nombre = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password1 != password2:
            return render(request, 'blogapp/register.html', {"nombre":nombre,"error":"Las contraseñas no coinciden"})  
        elif len(password2) < 5:
            return render(request, 'blogapp/register.html', {"nombre":nombre,"error":"Mínimo 5 caracteres"})      
        elif creator.objects.filter(username__iexact=nombre).exists():
            return render(request, 'blogapp/register.html', {"error":"Ese nombre ya está en uso"})
        else:
            creator.objects.create_user(username=nombre, password=password2)
            return redirect('/dashboard')

#Creamos una función para cerrar sesión
@login_required
def signout(request):
    #llamamos a la función logout del init.py
    logout(request)
    return redirect('/dashboard')
    
#Creamos una función para obtener todos los operarios
@login_required
def operarios(request):
    users = User.objects.all()

    return render(request, 'blogapp/usuarios.html', {'userList':users})
#Creamos una función para poder ver y editar los detalles de los operarios pasandole el id del operario que clickea el usuario
@login_required
def user_detail(request, user_id):
    #Obtenemos el operario que su id coincida con el id del operario que ha clickeado el usuario
    user = get_object_or_404(User, pk=user_id)
    #Esto es una variable auxiliar que almacena la máquina del usuario que ha sido seleccionado para luego redireccionar a la url correcta.
    aux = user.maquina
    #Si el metodo es GET:
    if request.method == 'GET':
        #Devolvemos los detalles del usuario 
       return render(request, 'blogapp/user_detail.html', {'user': user})
    #De lo contrario en el caso que sea POST
    else:
        #Esta condición valida si el usuario de la request tiene como true los permismos de superususario o de admin, en caso contrario devolverá un html indicando que el usuario no tiene permisos suficientes
        if request.user.is_superuser or request.user.is_staff:
            #Obtenemos lo que selecciona en maquina
            new_maquina = request.POST.get('maquina')
             #Obtenemos lo que selecciona en el turno
            new_turno = request.POST.get('turno')
             #Obtenemos lo que selecciona en conocimientos
            new_conocimiento = request.POST.get('conocimientos')
             #Igualamos los atributos que tiene el usuario con los nuevos
            auxiliar_maquina = user.maquina
            auxiliar_turno = user.turno
            auxiliar_conocimientos = user.conocimientos

            user.maquina = new_maquina
            user.turno = new_turno
            user.conocimientos = new_conocimiento
            user.nombre = user.apellido + ',' + user.nombre
             #Guardamos los nuevos datos en la base de datos
            user.save()

            logs = []
            logs.append({"Maquina":(auxiliar_maquina, user.maquina)})
            logs.append({"Turno":(auxiliar_turno, user.turno)})
            logs.append({"Conocimiento":(auxiliar_conocimientos, user.conocimientos)})


            ruta_file = "json\\tracking.json"

            if os.path.exists(ruta_file):
                with open(ruta_file, 'r') as f:
                    try:
                        lista = json.load(f)
                    except json.JSONDecodeError:
                        lista = []
            else:
                lista = []

            contador = 0
            if len(lista) > 0:
                contador = lista[-1]["id"]
                contador = int(contador)
                contador += 1
            data = {
                    "id": contador,
                    "id_request": request.user.id,
                    "nombre": request.user.username,
                    "fecha": necesarios.hoy,
                    "log": "{} ha actualizado los datos del usuario {} con id {}".format(request.user, user.nombre, user.id),
                    "movimientos": logs
                }

            lista.append(data)

            with open(ruta_file, 'w') as f:
                json.dump(lista, f, indent=4)

            #Para que redireccione a la misma url:
            count = 0
            #Iteramos por todas las maquinas existentes
            for machine in necesarios.lista_maquina:
                #Aux es la variable que almacena la máquina del usuario que se está editando,
                # Si la máquina del usuario coincide con la máquina de la lista, la url tendrá el valor haga referencia a esa máquina
                if aux.lower() == machine.lower():
                    #RedirectsOperarios es una lista con todas las url de cada maquina ordenada en el mismo orden que la lista de máquinas, por tanto con el count podemos acceder a 
                    #la url correcta cuando la maquina del usuario coincida con la máquina de la lista
                    url=necesarios.redirectsOperarios[count]
                else:
                    #en caso de no encontrar coincidencia va sumandole uno al contador
                    count = count + 1

            return redirect(url)
        else:
            #Devuelve un html indicando que el usuario no tiene persmisos suficientes
            return render(request,'components/permisionError.html')
 
@login_required
def todo(request):
    return redirect ("dashboard")


def permutas():
    usersFilter = User.objects.filter(permutado__exact=True)
    permutas = Permutado.objects.all()
    for usuario in usersFilter:
        for perm in permutas:
            if perm.usuario.id == usuario.id and perm.maquina:
                fecha_inicio = datetime.strptime(perm.fecha_inicio, "%Y-%m-%d").date()
                fecha_fin = datetime.strptime(perm.fecha_fin, "%Y-%m-%d").date()
                fecha_hoy = datetime.strptime(necesarios.hoy, "%Y-%m-%d").date()

                if fecha_fin < fecha_hoy:
                    cantidad_eventos_usuario = 0
                    for p in permutas:
                        if p.usuario.id == usuario.id and p.maquina:
                            cantidad_eventos_usuario += 1
                    if cantidad_eventos_usuario == 1:
                        usuario.permutado = False
                    usuario.maquina = perm.auxiliar
                    perm.delete()
                    usuario.nombre = usuario.apellido + ',' + usuario.nombre
                    usuario.save()

                    lista = usuario.nombre.split(',')
                    usuario.nombre = lista[1]
                    usuario.apellido = lista[0]

                elif fecha_inicio <= fecha_hoy:
                    usuario.maquina = perm.tipo
                    usuario.nombre = usuario.apellido + ',' + usuario.nombre
                    usuario.save()

                    lista = usuario.nombre.split(',')
                    usuario.nombre = lista[1]
                    usuario.apellido = lista[0]

            elif perm.usuario.id == usuario.id and perm.maquina == False:
                fecha_inicio = datetime.strptime(perm.fecha_inicio, "%Y-%m-%d").date()
                fecha_fin = datetime.strptime(perm.fecha_fin, "%Y-%m-%d").date()
                fecha_hoy = datetime.strptime(necesarios.hoy, "%Y-%m-%d").date()

                if fecha_fin < fecha_hoy:
                    cantidad_eventos_usuario = 0
                    for p in permutas:
                        if p.usuario.id == usuario.id and p.maquina == False:
                            cantidad_eventos_usuario += 1
                    if cantidad_eventos_usuario == 1:
                        usuario.permutado = False
                    usuario.turno = perm.auxiliar
                    perm.delete()
                    usuario.nombre = usuario.apellido + ',' + usuario.nombre
                    usuario.save()

                    lista = usuario.nombre.split(',')
                    usuario.nombre = lista[1]
                    usuario.apellido = lista[0]

                elif fecha_inicio <= fecha_hoy:
                    usuario.turno = perm.tipo
                    usuario.nombre = usuario.apellido + ',' + usuario.nombre
                    usuario.save()

                    lista = usuario.nombre.split(',')
                    usuario.nombre = lista[1]
                    usuario.apellido = lista[0]

#Creamos una fucnión generica para crear las vistas de los operarios, la funcion necesita para funcionar 1 variable (La maquina por la cual se va a filtrar)
#(Aqui no se necesita la maquina para hacer el operarios todos)
def funcion_generica_operarios(request, maquina=None):
    permutas()
    #Creamos la posibilidad de que cuando se llame a la función generica se pueda usar sin pasarle una maquina para poder hacer una pagina en la que no se filtre por maquina (Para hacer Operarios todos)
    if maquina is None:
        #Si la petición es un GET hacemos los siguiente:
        if request.method == 'GET':
            #Aqui recogemos todos los usuarios porque en el filtro no le ponemos nada por lo tanto todos los usuarios pasan el filtrado
            usersFilter = User.objects.filter()
            #Le pasamos al html los operarios necesarios y los operarios que cumplen los filtros (osea todos)
            diccionario = {"userList":usersFilter}
            return render(request, 'blogapp/usuarios.html', {'diccionario':diccionario})
        #De lo contrario si es POST hacemos lo siguiente:
        else:
            #Igualamos una variable llamada search_term a la petición que haga el usuario en el input llamado search que es el buscar que hay en la navbar
            search_term = request.POST.get("search")
            #Igualamos la variable turno a la petición que haga el usuario en el select llamado "turno" que es el select que hay a la derecha del buscar
            turno = request.POST.get("turno")

            #Si en el select dejan marcado el turno en "Todo" hacemos otra vez lo de hacer un filtrado sin filtros por lo tanto no filtra mediante el turno
            if turno == "Todo":
                userp = User.objects.filter()
                #De lo contrario osea que el usuario seleccione algun turno, se filtra mediante el turno que se ha seleccionado osea que solo apareceran los operarios que esta semana tienen ese turno
            else:
                userp = User.objects.filter(
                Q(turno__iexact=turno)
                )   
            #Aqui lo que hacemos es que si el usuario introduce algo en el buscar solo aparecen los usuarios que contengan los datos introducidos en el buscar 
            #(Hacemos un filtrado que no tiene que ser exacto y pueden buscar mediante el id y el nombre)
            userFilter = userp.filter(
                Q(id__icontains=search_term) |
                Q(nombre__icontains=search_term) 
            )
            #Si la lista de usuarios es mayor a 0 se renderiza la pagina de operarios con sus respectivos operarios filtrados
            if len(userFilter) > 0:
                diccionario = {"userList":userFilter}
                return render(request, 'blogapp/usuarios.html', {"diccionario":diccionario})
            #De lo contrario (si la lista esta vacia) se renderiza una ventana personalizada de error diciendoles que no hay usuarios con los criterios de busqueda
            else:
                return render(request, 'components/error_dashboard.html')
    #De lo contrario (Si introducimos la maquina) hacemos un filtrado mediante la maquina que le pasamos cuando llamamos a la función
    else:    
        #Si la petición es un GET hacemos los siguiente:
        if request.method == 'GET':
            #Aqui recogemos los operarios que tengan como maquina la que se le ha pasado a la función a la hora de llamarla (lo hacemos de forma exacta para que la maquina coincida si o si)
            usersFilter = User.objects.filter(maquina__iexact=maquina)
            #Le pasamos al html los operarios filtrados
            diccionario = {"userList":usersFilter}
            return render(request, 'blogapp/usuarios.html', {'diccionario':diccionario})
        #De lo contrario osea en el caso de que la petición sea POST hacemos lo siguiente:
        else:
            #Igualamos una variable llamada search_term a la petición que haga el usuario en el input llamado search que es el buscar que hay en la navbar
            search_term = request.POST.get("search")
            #Igualamos la variable turno a la petición que haga el usuario en el select llamado "turno" que es el select que hay a la derecha del buscar
            turno = request.POST.get("turno")
            #Si en el select dejan marcado el turno en "Todo" hacemos otra vez lo de hacer un filtrado sin filtros por lo tanto no filtra mediante el turno
            if turno == "Todo":
                userp = User.objects.filter(maquina__iexact=maquina)
            #De lo contrario osea que el usuario seleccione algun turno, se filtra mediante el turno que se ha seleccionado osea que solo apareceran los operarios que esta semana tienen ese turno,
            #además de filtrar por la maquina 
            else:
                userp = User.objects.filter(
                Q(maquina__iexact=maquina)&
                Q(turno__iexact=turno)
                )   
            #Aqui lo que hacemos es que si el usuario introduce algo en el buscar solo aparecen los usuarios que contengan los datos introducidos en el buscar 
            #(Hacemos un filtrado que no tiene que ser exacto y pueden buscar mediante el id y el nombre)
            userFilter = userp.filter(
                Q(id__icontains=search_term) |
                Q(nombre__icontains=search_term) 
            )
            #Si la lista de usuarios es mayor a 0 se renderiza la pagina de operarios con sus respectivos operarios filtrados
            if len(userFilter) > 0:
                diccionario = {"userList":userFilter}
                return render(request, 'blogapp/usuarios.html', {"diccionario":diccionario})
            #De lo contrario (si la lista esta vacia) se renderiza una ventana personalizada de error diciendoles que no hay usuarios con los criterios de busqueda
            else:
                return render(request, 'components/error_dashboard.html')


#Aqui es donde llamamos a la función generica de operarios 
#Hacemos que se necesite estar logeado para entrar en estas funciones además le pasamos a cada una el request y el nombre de la maquina de cada función (Por la cuál se va a filtrar luego)
@login_required
def autos(request):
    return funcion_generica_operarios(request, "autos")
    

 
@login_required
def laser(request):
    return funcion_generica_operarios(request, "laser")

        
@login_required
def tampo(request):
    return funcion_generica_operarios(request, "tampo")

        
@login_required
def pulpos(request):
    return funcion_generica_operarios(request, "pulpos")

        
@login_required
def digital(request):
    return funcion_generica_operarios(request, "digital")
        
@login_required
def bordado(request):
    return funcion_generica_operarios(request, "bordado")
        
@login_required
def termo(request):
    return funcion_generica_operarios(request, "termo")
        
@login_required
def planchas(request):
    return funcion_generica_operarios(request, "planchas")
    
@login_required
def sublimacion(request):
    return funcion_generica_operarios(request, "sublimacion")
        
@login_required
def envasado(request):
    return funcion_generica_operarios(request, "otros")

@login_required
def cosido(request):
    return funcion_generica_operarios(request, "cosido")

@login_required
def horno(request):
    return funcion_generica_operarios(request, "horno")




#Creamos una función para mostrar los dias, meses y años en las vistas de los turnos
def fechaCompleto(fecha=None):
    fechas=[]
    if fecha is None:
        # Establecer la configuración regional en español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

        # Obtener la fecha de hoy
        hoy = datetime.now()

        # Lista para almacenar los títulos de las columnas, comenzando con el día de hoy
        dia = []
        mes = []
        año = []

        # Agregar el día de hoy a la lista de columnas
        dia.append(f"{hoy.strftime('%a %d')}")
        mes.append(hoy.strftime('%B'))
        año.append(hoy.strftime('%Y'))
        

        # Calcular los días de los próximos 12 meses, comenzando desde el próximo día después de hoy
        fecha_actualizada = hoy + timedelta(days=1)
        for _ in range(365):  # Iterar durante un año (365 días)

            # Agregar el día actual a la lista de columnas
            dia.append(f"{fecha_actualizada.strftime('%a %d')}")
            mes.append(fecha_actualizada.strftime('%B'))
            año.append(fecha_actualizada.strftime('%Y'))
            # Actualizar a la próxima fecha
            fecha_actualizada += timedelta(days=1)
        #Añadimos a fechas los dias, meses y años con un limite de 182 para mejorar el rendimiento
        fechas.append(dia[:62])
        fechas.append(mes[:62])
        fechas.append(año[:62])
        return fechas
    else:
        # Obtener la fecha de hoy
        hoy = datetime.now()

        # Establecer la configuración regional en español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        
        # Convertir la cadena a un objeto datetime
        fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
        
        
        # Lista para almacenar los títulos de las columnas, comenzando con el día de hoy
        dia = []
        mes = []
        año = []

        # Agregar el día de hoy a la lista de columnas
        dia.append(f"{fecha_datetime.strftime('%a %d')}")
        mes.append(fecha_datetime.strftime('%B'))
        año.append(fecha_datetime.strftime('%Y'))
        

        # Calcular los días de los próximos 12 meses, comenzando desde el próximo día después de hoy
        fecha_actualizada = fecha_datetime + timedelta(days=1)
        for _ in range(365):  # Iterar durante un año (365 días)

            # Agregar el día actual a la lista de columnas
            dia.append(f"{fecha_actualizada.strftime('%a %d')}")
            mes.append(fecha_actualizada.strftime('%B'))
            año.append(fecha_actualizada.strftime('%Y'))
            # Actualizar a la próxima fecha
            fecha_actualizada += timedelta(days=1)

        #Añadimos a fechas los dias, meses y años con un limite de 182 para mejorar el rendimiento
        fechas.append(dia[:62])
        fechas.append(mes[:62])
        fechas.append(año[:62])
        return fechas
        

def turnodefecto(request, necesidad=None, maquina=None, green=None, red=None):
    #Cuando maquina=None significa que renderiza todos los usuarios sin importar la máquina en la que esté
    if maquina is None:
        # Cuando la petición del usuario le llega por Get
        if request.method == 'GET':
            permutas()
            fecha_modificada = necesarios.hoy


            # Sacamos todos los usuarios de la base de datos
            userp = User.objects.all()
            # Esto es saca una lista que alberga tres listas: Día, Mes, Año
            dateall = fechaCompleto()
            #Esto saca las fechas correspondientes de un mes completo partiendo del día de hoy
            dia = dateall[0][:31]
            mes = dateall[1][:31]
            año = dateall[2][:31]
            # Esta lista guarda los usuarios que tengan eventos asociados
            users_event = userp.filter(evento__exact=True)
            
            # Igualamos el atributo a true para cada usuario, esto permite renderizar en el html los turnos de un mes 
            for user in userp:
                user.limiteRotacion = True
            # La lista colores alberga la posición inicial y final de cada evento asociada a cada usuario, por defecto se inicializa a una lista vacía
            colores = []
            #Cuando existen usuarios con eventos añadiremos en la lista colores las posiciones correspondientes de cada evento con su usuario relacionado
            #colores es una lista que almacena un conjunto de listas con esta estructura:
            #[PoscionInical,PosicionFinal,Id_Usuario]
            #Si la longitud de la lista es superior a 0 significa que existen usuarios con eventos
            if len(users_event) > 0:
                #Sacamos todo los eventos existentes
                eventos = Eventos.objects.all()
                #Iteramos por cada usuario y por cada evento para encontrar los eventos relacionados con un ususario
                for user in users_event:
                    for event in eventos:
                        # Esta condición saca el evento que está asociado con ese usuario
                        if user.id == event.usuario.id:
                            # Crear la zona horaria para España
                            zona_horaria_espana = pytz.timezone('Europe/Madrid')
                            # Obtener la fechas sin la hora, para eso se pone el .date() al final
                            fecha_inicio = datetime.strptime(event.fecha_inicio, "%Y-%m-%d").date()
                            fecha_fin = datetime.strptime(event.fecha_fin, "%Y-%m-%d").date()
                            fecha_hoy = datetime.now(zona_horaria_espana).date()
                            # Cuando la fecha_inicio es inferior a la fecha de hoy la fecha de inicio pasaría a ser la fecha actual
                            if fecha_inicio < fecha_hoy:
                                fecha_inicio = fecha_hoy
                            # Si la fecha final es inferior a la actual continuamos con el siguiente evento, esto permite descartar los eventos pasados y no se pintaría en el la tabla
                            if fecha_fin < fecha_hoy:
                                continue
                            
                            #Sacamos los días previos que hay antes de empezar el evento, esto permite sacar la posición inicial
                            dias_previos = (fecha_inicio - fecha_hoy).days
                            # Con la diferencia de días podemos sacar la posición final si sumamos los días previos y los días que dura el evento
                            diferencia_dias = (fecha_fin - fecha_inicio).days 
                            posicion_listap2_inicio = dias_previos
                            # Con la suma de los días previos y los días que dura el evento sacaremos la posición final
                            posicion_listap2_fin = (diferencia_dias+dias_previos)
                            # Creamos una lista con los datos correspondientes del evento
                            if len(user.rotacionMes) <= posicion_listap2_fin:
                                posicion_listap2_fin = len(user.rotacionMes)-1
                                
                            color = [posicion_listap2_inicio, posicion_listap2_fin, user.id]
                            try:
                                user.rotacionMes[dias_previos]
                            except:
                                continue
                            #Añadimos esa lista con el resto de listas.
                            colores.append(color)
            
            # Esto es un diccionario que alberga todas las propiedades que hemos ido sacando en la función
            diccionario = {"operarios":userp, "fechas":dia,"fecha_modificada":fecha_modificada ,"año":año, "mes":mes,"necesarios":necesidad, "colores":colores, "minValue":necesarios.minValueDate}
            return render(request, "blogapp/index.html", {"diccionario":diccionario})
        #Cuando la petición del usuario llega por POST
        else:
            #Esto guarda la fecha que el usuario quiere filtrar
            fecha_modificada = request.POST.get("fecha")

            # data = {
            #         "id_request": request.user.id,
            #         "fecha": fecha_modificada
            #     }

            # ruta_file = "json\\fechas.json"

            # if os.path.exists(ruta_file):
            #     with open(ruta_file, 'r') as f:
            #         try:
            #             lista = json.load(f)
            #         except json.JSONDecodeError:
            #             lista = []
            # else:
            #     lista = []

            # updated = False

            # for item in lista:
            #         if item["id_request"] == request.user.id:
            #             item["fecha"] = fecha_modificada
            #             updated = True
            #             break
            
            # if not updated:
            #     lista.append(data)


            # with open(ruta_file, 'w') as f:
            #     json.dump(lista, f, indent=4)
            

            #Esto guarda la palabra o el número que ha introducido el usuario en el buscador
            search_term = request.POST.get("search")
            turno = request.POST.get("turno")
            
            #Hacemos una petición a la base de datos filtrando los usuarios que tengan la misma id o que tengan un nombre parecido al input de filtrado
            usersFilter = User.objects.filter(
                Q(id__iexact=search_term) |
                Q(nombre__icontains=search_term) 
            )

            # Devuelve una lista con tres listas: Dia, Mes, Año
            dateall = fechaCompleto(fecha_modificada)
            dia = dateall[0][:31] # limitamos la lista a un mes a partir del día de hoy
            mes = dateall[1][:31] # limitamos la lista a un mes a partir del día de hoy
            año = dateall[2][:31] # limitamos la lista a un mes a partir del día de hoy
            
            
            #Procedemos ha sacar las dias previos calulandolo a partir de la fecha de filtrado(fecha_input) y la fehca actual
            # Crear la zona horaria para España
            zona_horaria_espana = pytz.timezone('Europe/Madrid')
            #Esto devuelve la fecha_modificada pero en formato fecha "AAAA-MM-DD"
            fecha_input = datetime.strptime(fecha_modificada, '%Y-%m-%d').date()
            fecha_hoy = datetime.now(zona_horaria_espana).date()
            dias_previos = (fecha_input - fecha_hoy).days
            
            #Con los días previos sacamos el turno en el que se encuentra ese día y generamos tres nuevas listas (Mañana,Tarde,Noche) a partir de ese turno
            rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos],fecha_modificada)
            rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos],fecha_modificada)
            rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos],fecha_modificada)

            #JORNADA PARCIAL
            rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_modificada, sinMañana=True)
            rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_modificada, sinMañana=True)

            rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_modificada, sinTarde=True )    
            rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_modificada, sinTarde=True)

            rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_modificada, sinNoche=True)    
            rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_modificada, sinNoche=True)  
            
            #JORNADA ESTÁTICA
            rotacion_estatica_M = generar_turnos_rotativos("M", fecha_modificada, noRota=True)
            rotacion_estatica_T = generar_turnos_rotativos("T", fecha_modificada, noRota=True)
            rotacion_estatica_N = generar_turnos_rotativos("N", fecha_modificada, noRota=True)

            # Turno fecha equivale al turno que el usuario desea filtrar por el día concreto
            turno_fecha=request.POST.get("turnoFecha")
            # Iteramos por cada usuario que hemos sacado del filtrado
            for objeto in usersFilter:
                #Limitamos la rotacion a 1 mes para mejorar el rendimiento
                objeto.limiteRotacion = True
                #Si el usuario tiene el evento a True se generará una nueva lista de eventos a partir de la fecha en la que se desea filtrar para ese usuario
                if objeto.evento:
                    #Asignamos la nueva lista generada a partir de la fecha filtrada a cada usuario correspondiente y luego generamos el evento
                    if objeto.turno == "Mañana":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_mañana.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "Tarde":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_tarde.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "Noche":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_noche.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    #JORNADA PARCIALES
                    if objeto.turno == "sinMañana-T":
                        objeto.rotacion = rotacion_sinMañana_T.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinMañana-N":
                        objeto.rotacion = rotacion_sinMañana_N.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinTarde-M":
                        objeto.rotacion = rotacion_sinTarde_M.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinTarde-N":
                        objeto.rotacion = rotacion_sinTarde_N.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinNoche-M":
                        objeto.rotacion = rotacion_sinNoche_M.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinNoche-T":
                        objeto.rotacion = rotacion_sinNoche_T.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto,fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]
                    
                    #JORNADAS ESTÁTICAS          
                    if objeto.turno == "estatica-M":
                        objeto.rotacion = rotacion_estatica_M.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto, fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "estatica-T":
                        objeto.rotacion = rotacion_estatica_T.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto, fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "estatica-N":
                        objeto.rotacion = rotacion_estatica_N.copy()
                        objeto.rotacionMes = objeto.rotacion[:31]
                        funcion_eventos(objeto, fecha_input)
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                else:
                    #Asignamos la nueva lista generada a partir de la fecha filtrada a cada usuario correspondiente
                    if objeto.turno == "Mañana":
                        objeto.rotacionMes = rotacion_mañana[:31]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacionMes[0]
                    if objeto.turno == "Tarde":
                        objeto.rotacionMes = rotacion_tarde[:31]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacionMes[0]
                    if objeto.turno == "Noche":
                        objeto.rotacionMes = rotacion_noche[:31]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacionMes[0]
                    
                    #JORNADA PARCIALES
                    if objeto.turno == "sinMañana-T":
                        objeto.rotacionMes = rotacion_sinMañana_T[:31]
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinMañana-N":
                        objeto.rotacionMes = rotacion_sinMañana_N[:31]
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinTarde-M":
                        objeto.rotacionMes = rotacion_sinTarde_M[:31]
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinTarde-N":
                        objeto.rotacionMes = rotacion_sinTarde_N[:31]
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinNoche-M":
                        objeto.rotacionMes = rotacion_sinNoche_M[:31]
                        objeto.rotacion_fecha = objeto.rotacionMes[0]

                    if objeto.turno == "sinNoche-T":
                        objeto.rotacionMes = rotacion_sinNoche_T[:31]
                        objeto.rotacion_fecha = objeto.rotacionMes[0]
                              
                    if objeto.turno == "estatica-M" or objeto.turno == "estatica-T" or objeto.turno == "estatica-N":
                        objeto.rotacion_fecha = objeto.rotacionMes[0]
                    
                

            #Esta lista alberga los usuarios que coincidan con el turno que el usuario desea filtrar por un día concreto
            usersFilterTurno = []
            for objeto in usersFilter:
                if objeto.rotacion_fecha == turno_fecha:
                    usersFilterTurno.append(objeto)
            #Si se desea filtrar por todos los turnos entonces asignamos la misma lista de los usuarios filtrados
            if turno_fecha.lower() == "todo":
                usersFilterTurno = usersFilter
            
            #Filtramos a partir de la primera consulta aquellos usuario que tienen algún evento
            users_event = usersFilter.filter(evento__exact=True)
            # La lista colores alberga la posición inicial y final de cada evento asociada a cada usuario, por defecto se inicializa a una lista vacía
            colores = []
            #Cuando existen usuarios con eventos añadiremos en la lista colores las posiciones correspondientes de cada evento con su usuario relacionado
            #colores es una lista que almacena un conjunto de listas con esta estructura:
            #[PoscionInical,PosicionFinal,Id_Usuario]
            #Si la longitud de la lista es superior a 0 significa que existen usuarios con eventos
            if len(users_event) > 0:
                #Sacamos todo los eventos existentes
                eventos = Eventos.objects.all()
                #Iteramos por cada usuario y por cada evento para encontrar los eventos relacionados con un ususario
                for user in users_event:
                    for event in eventos:
                        # Esta condición saca el evento que está asociado con ese usuario
                        if user.id == event.usuario.id:
                            # Obtener la fechas sin la hora, para eso se pone el .date() al final
                            fecha_inicio = datetime.strptime(event.fecha_inicio, "%Y-%m-%d").date()
                            fecha_fin = datetime.strptime(event.fecha_fin, "%Y-%m-%d").date()
                            # En esto caso modificamos la fecha de hoy por la nueva fecha que el usuario desea filtrar
                            fecha_hoy = fecha_input
                            dias_previos = (fecha_inicio - fecha_hoy).days
                            diferencia_dias = (fecha_fin - fecha_inicio).days
                            # Cuando la fecha_inicio es inferior a la fecha de hoy la fecha de inicio pasaría a ser la fecha actual
                            if fecha_inicio < fecha_hoy:
                                dias_previos = 0
                                # Con la diferencia de días podemos sacar la posición final si sumamos los días previos y los días que dura el evento
                                diferencia_dias = (fecha_fin - fecha_hoy).days
                            if fecha_fin < fecha_hoy:
                                continue
                            # Con los días previos sacamos la posición de inicio del evento
                            posicion_listap2_inicio = dias_previos
                            # Con la suma de los días previos y los días que dura el evento sacaremos la posición final
                            posicion_listap2_fin = (diferencia_dias+dias_previos)
                            # El color equivale a la posición inicio y la fin con el id del usuario relacionado
                            if len(user.rotacionMes) <= posicion_listap2_fin:
                                posicion_listap2_fin = len(user.rotacionMes)-1
                                
                            color = [posicion_listap2_inicio, posicion_listap2_fin, user.id]
                            try:
                                user.rotacionMes[dias_previos]
                            except:
                                continue
                            colores.append(color)
                
            
            
    
            #Cuando existen usuarios filtrados se devuelve el html con esos usuarios
            if len(usersFilter) > 0:
                filter = {"operarios":usersFilterTurno, "fechas":dia,"año":año, "fecha_modificada":fecha_modificada ,"necesarios":necesidad,  "turno":turno,  "mes":mes, "colores":colores, "minValue":necesarios.minValueDate}
                return render(request, "blogapp/index.html", {"diccionario":filter})
            # En caso contrario se devuelve un HTML con mensaje de error.
            else:
                filter = {"fecha_modificada":fecha_modificada ,"turno":turno}
                return render(request, "components/error.html",{"diccionario":filter})
            
    else:
        # Cuando la petición le llega por get
        if request.method == 'GET':
            permutas()
            zona_horaria_espana = pytz.timezone('Europe/Madrid')
            fecha_modificada = necesarios.hoy
            # ruta_file = "json\\fechas.json"

            # if os.path.exists(ruta_file):
            #     with open(ruta_file, 'r') as f:
            #         try:
            #             lista = json.load(f)
            #         except json.JSONDecodeError:
            #             lista = []
            # else:
            #     lista = []
            
            # if len(lista) > 0:
            #     for item in lista:
            #         if item["id_request"] == request.user.id:
            #             fecha_modificada = item["fecha"]
            
            fecha_input = datetime.strptime(fecha_modificada, '%Y-%m-%d').date()
            fecha_hoy = datetime.now(zona_horaria_espana).date()

            # if fecha_input < fecha_hoy:
            #     fecha_modificada = necesarios.hoy
            
            # fecha_modificada = necesarios.hoy
            
            # Filtramos por los usuarios que tengan la máquina correspondiente por la que se quiere filtrar
            userp = User.objects.filter(Q(maquina__iexact=maquina) & ~Q(categoria__iexact="RESPONSABLE"))
            #Esto es una lista que guarda tres listas más: Dia, Mes, Año
            dateall = fechaCompleto(fecha_modificada)
            dia = dateall[0]
            mes = dateall[1]
            año = dateall[2]

            #Esto devuelve la fecha_modificada pero en formato fecha "AAAA-MM-DD"
            fecha_input = datetime.strptime(fecha_modificada, '%Y-%m-%d').date()
            fecha_hoy = datetime.now(zona_horaria_espana).date()
            dias_previos = (fecha_input - fecha_hoy).days
            
            #Con los días previos sacamos el turno en el que se encuentra ese día y generamos tres nuevas listas (Mañana,Tarde,Noche) a partir de ese turno
            #JORNADA COMPLETA
            rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos],fecha_modificada)
            rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos],fecha_modificada)
            rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos],fecha_modificada)

            #JORNADA PARCIAL
            rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_modificada, sinMañana=True)
            rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_modificada, sinMañana=True)

            rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_modificada, sinTarde=True )    
            rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_modificada, sinTarde=True)

            rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_modificada, sinNoche=True)    
            rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_modificada, sinNoche=True)  
            
            #JORNADA ESTÁTICA
            rotacion_estatica_M = generar_turnos_rotativos("M", fecha_modificada, noRota=True)
            rotacion_estatica_T = generar_turnos_rotativos("T", fecha_modificada, noRota=True)
            rotacion_estatica_N = generar_turnos_rotativos("N", fecha_modificada, noRota=True)              



            # Iteramos por cada usuario que hemos sacado del filtrado
            for objeto in userp:
                #Si el usuario tiene el evento a True se generará una nueva lista de eventos a partir de la fecha en la que se desea filtrar para ese usuario
                if objeto.evento:
                    #Asignamos la nueva lista generada a partir de la fecha filtrada a cada usuario correspondiente y luego generamos el evento
                    if objeto.turno == "Mañana":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_mañana.copy()
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]
                    if objeto.turno == "Tarde":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_tarde.copy()
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]
                    if objeto.turno == "Noche":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_noche.copy()
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]
                    
                    #JORNADA PARCIALES
                    if objeto.turno == "sinMañana-T":
                        objeto.rotacion = rotacion_sinMañana_T.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinMañana-N":
                        objeto.rotacion = rotacion_sinMañana_N.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinTarde-M":
                        objeto.rotacion = rotacion_sinTarde_M.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinTarde-N":
                        objeto.rotacion = rotacion_sinTarde_N.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinNoche-M":
                        objeto.rotacion = rotacion_sinNoche_M.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinNoche-T":
                        objeto.rotacion = rotacion_sinNoche_T.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]    
                              
                    if objeto.turno == "estatica-M":
                        objeto.rotacion = rotacion_estatica_M.copy()
                        funcion_eventos(objeto, fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "estatica-T":
                        objeto.rotacion = rotacion_estatica_T.copy()
                        funcion_eventos(objeto, fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "estatica-N":
                        objeto.rotacion = rotacion_estatica_N.copy()
                        funcion_eventos(objeto, fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                else:
                    #Asignamos la nueva lista generada a partir de la fecha filtrada a cada usuario correspondiente
                    if objeto.turno == "Mañana":
                        objeto.rotacion = rotacion_mañana[:62]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    if objeto.turno == "Tarde":
                        objeto.rotacion = rotacion_tarde[:62]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    if objeto.turno == "Noche":
                        objeto.rotacion = rotacion_noche[:62]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    
                    #JORNADA PARCIALES
                    if objeto.turno == "sinMañana-T":
                        objeto.rotacion = rotacion_sinMañana_T[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinMañana-N":
                        objeto.rotacion = rotacion_sinMañana_N[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinTarde-M":
                        objeto.rotacion = rotacion_sinTarde_M[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinTarde-N":
                        objeto.rotacion = rotacion_sinTarde_N[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinNoche-M":
                        objeto.rotacion = rotacion_sinNoche_M[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinNoche-T":
                        objeto.rotacion = rotacion_sinNoche_T[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]
                              
                    if objeto.turno == "estatica-M" or objeto.turno == "estatica-T" or objeto.turno == "estatica-N":
                        objeto.rotacion_fecha = objeto.rotacion[0]
            

            #Filtramos los usuarios de la máquina que tengan eventos
            users_event = userp.filter(evento__exact=True)
            #Colores es una lista vacía
            colores = []
            #Cuando existen usuarios con eventos añadiremos en la lista colores las posiciones correspondientes de cada evento con su usuario relacionado
            #colores es una lista que almacena un conjunto de listas con esta estructura:
            #[PoscionInical,PosicionFinal,Id_Usuario]
            #Si la longitud de la lista es superior a 0 significa que existen usuarios con eventos
            if len(users_event) > 0:
                #Sacamos todo los eventos existentes
                eventos = Eventos.objects.all()
                #Iteramos por cada usuario y por cada evento para encontrar los eventos relacionados con un ususario
                for user in users_event:
                    for event in eventos:
                        # Esta condición saca el evento que está asociado con ese usuario
                        if user.id == event.usuario.id:
                            # Crear la zona horaria para España
                            zona_horaria_espana = pytz.timezone('Europe/Madrid')
                            # Obtener la fechas sin la hora, para eso se pone el .date() al final
                            fecha_inicio = datetime.strptime(event.fecha_inicio, "%Y-%m-%d").date()
                            fecha_fin = datetime.strptime(event.fecha_fin, "%Y-%m-%d").date()
                            fecha_hoy = fecha_input
                            # Cuando la fecha_inicio es inferior a la fecha de hoy la fecha de inicio pasaría a ser la fecha actual                            
                            if fecha_inicio < fecha_hoy:
                                fecha_inicio = fecha_hoy
                            # Cuando la fecha final es inferior a la actual se descarta el evento y pasa a evaluar el siguiente evento
                            if fecha_fin < fecha_hoy:
                                continue
                            
                            #Sacamos los días previos que hay antes de empezar el evento, esto permite sacar la posición inicial                           
                            dias_previos = (fecha_inicio - fecha_hoy).days
                            # Con la diferencia de días podemos sacar la posición final si sumamos los días previos y los días que dura el evento                           
                            diferencia_dias = (fecha_fin - fecha_inicio).days + 1
                            posicion_listap2_inicio = dias_previos
                            posicion_listap2_fin = (diferencia_dias+dias_previos) - 1
                            # Creamos una lista con los datos correspondientes del evento
                            if len(user.rotacion) <= posicion_listap2_fin:
                                posicion_listap2_fin = len(user.rotacion)-1
                                
                            color = [posicion_listap2_inicio, posicion_listap2_fin, user.id]
                            try:
                                user.rotacion[dias_previos]
                            except:
                                continue
                            #Añadimos esa lista con el resto de listas.
                            colores.append(color)
            
           # Esto es un diccionario que alberga todas las propiedades que hemos ido sacando en la función
            diccionario = {"operarios":userp, "fechas":dia,"fecha_modificada":fecha_modificada ,"año":año, "mes":mes,"necesarios":necesidad, "colores":colores, "minValue":necesarios.minValueDate, "maquina":maquina}
            return render(request, "blogapp/index.html", {"diccionario":diccionario, "green":green, "red":red})
        #Cuando la petición del usuario llega por POST
        else:
            #Esto guarda la fecha que el usuario quiere filtrar
            fecha_modificada = request.POST.get("fecha")

            # data = {
            #     "id_request": request.user.id,
            #     "fecha": fecha_modificada
            # }

            # ruta_file = "json\\fechas.json"

            # if os.path.exists(ruta_file):
            #     with open(ruta_file, 'r') as f:
            #         try:
            #             lista = json.load(f)
            #         except json.JSONDecodeError:
            #             lista = []
            # else:
            #     lista = []

            # updated = False

            # for item in lista:
            #         if item["id_request"] == request.user.id:
            #             item["fecha"] = fecha_modificada
            #             updated = True
            #             break
            
            # if not updated:
            #     lista.append(data)


            # with open(ruta_file, 'w') as f:
            #     json.dump(lista, f, indent=4)


            #Esto guarda la palabra o el número que ha introducido el usuario en el buscador
            search_term = request.POST.get("search")
            turno = request.POST.get("turno")
            userp = User.objects.filter(Q(maquina__iexact=maquina) & ~Q(categoria__iexact="RESPONSABLE"))
            
            #Hacemos una petición a la base de datos filtrando los usuarios que tengan la misma id o que tengan un nombre parecido al input de filtrado
            usersFilter = userp.filter(
                Q(id__iexact=search_term) |
                Q(nombre__icontains=search_term) 
            )

            # Devuelve una lista con tres listas: Dia, Mes, Año
            dateall = fechaCompleto(fecha_modificada)
            dia = dateall[0] # limitamos la lista a un mes a partir del día de hoy
            mes = dateall[1] # limitamos la lista a un mes a partir del día de hoy
            año = dateall[2] # limitamos la lista a un mes a partir del día de hoy
            
            #Procedemos ha sacar las dias previos calulandolo a partir de la fecha de filtrado(fecha_input) y la fehca actual
            # Crear la zona horaria para España
            zona_horaria_espana = pytz.timezone('Europe/Madrid')
            #Esto devuelve la fecha_modificada pero en formato fecha "AAAA-MM-DD"
            fecha_input = datetime.strptime(fecha_modificada, '%Y-%m-%d').date()
            fecha_hoy = datetime.now(zona_horaria_espana).date()
            dias_previos = (fecha_input - fecha_hoy).days
            
            #Con los días previos sacamos el turno en el que se encuentra ese día y generamos tres nuevas listas (Mañana,Tarde,Noche) a partir de ese turno
            #JORNADA COMPLETA
            rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos],fecha_modificada)
            rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos],fecha_modificada)
            rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos],fecha_modificada)

            #JORNADA PARCIAL
            rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_modificada, sinMañana=True)
            rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_modificada, sinMañana=True)

            rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_modificada, sinTarde=True )    
            rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_modificada, sinTarde=True)

            rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_modificada, sinNoche=True)    
            rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_modificada, sinNoche=True)  
            
            #JORNADA ESTÁTICA
            rotacion_estatica_M = generar_turnos_rotativos("M", fecha_modificada, noRota=True)
            rotacion_estatica_T = generar_turnos_rotativos("T", fecha_modificada, noRota=True)
            rotacion_estatica_N = generar_turnos_rotativos("N", fecha_modificada, noRota=True)              



            # Turno fecha equivale al turno que el usuario desea filtrar por el día concreto
            turno_fecha=request.POST.get("turnoFecha")
            # Iteramos por cada usuario que hemos sacado del filtrado
            for objeto in usersFilter:
                #Si el usuario tiene el evento a True se generará una nueva lista de eventos a partir de la fecha en la que se desea filtrar para ese usuario
                if objeto.evento:
                    #Asignamos la nueva lista generada a partir de la fecha filtrada a cada usuario correspondiente y luego generamos el evento
                    if objeto.turno == "Mañana":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_mañana.copy()
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]
                    if objeto.turno == "Tarde":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_tarde.copy()
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]
                    if objeto.turno == "Noche":
                        # !! Importante no quitar la extensión .copy(), esto permite que la lista del usuario no apunte directamente a la variable de la lista, así cuando cambiemos la lista con los eventos no habrá problemas de persistencia.
                        objeto.rotacion = rotacion_noche.copy()
                        funcion_eventos(objeto,fecha_input)
                        #Esto alberga el primer turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]
                    
                    #JORNADA PARCIALES
                    if objeto.turno == "sinMañana-T":
                        objeto.rotacion = rotacion_sinMañana_T.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinMañana-N":
                        objeto.rotacion = rotacion_sinMañana_N.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinTarde-M":
                        objeto.rotacion = rotacion_sinTarde_M.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinTarde-N":
                        objeto.rotacion = rotacion_sinTarde_N.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinNoche-M":
                        objeto.rotacion = rotacion_sinNoche_M.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "sinNoche-T":
                        objeto.rotacion = rotacion_sinNoche_T.copy()
                        funcion_eventos(objeto,fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]    
                              
                    if objeto.turno == "estatica-M":
                        objeto.rotacion = rotacion_estatica_M.copy()
                        funcion_eventos(objeto, fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "estatica-T":
                        objeto.rotacion = rotacion_estatica_T.copy()
                        funcion_eventos(objeto, fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                    if objeto.turno == "estatica-N":
                        objeto.rotacion = rotacion_estatica_N.copy()
                        funcion_eventos(objeto, fecha_input)

                        objeto.rotacion_fecha = objeto.rotacion[0]
                        objeto.rotacion = objeto.rotacion[:62]

                else:
                    #Asignamos la nueva lista generada a partir de la fecha filtrada a cada usuario correspondiente
                    if objeto.turno == "Mañana":
                        objeto.rotacion = rotacion_mañana[:62]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    if objeto.turno == "Tarde":
                        objeto.rotacion = rotacion_tarde[:62]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    if objeto.turno == "Noche":
                        objeto.rotacion = rotacion_noche[:62]
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    
                    #JORNADA PARCIALES
                    if objeto.turno == "sinMañana-T":
                        objeto.rotacion = rotacion_sinMañana_T[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinMañana-N":
                        objeto.rotacion = rotacion_sinMañana_N[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinTarde-M":
                        objeto.rotacion = rotacion_sinTarde_M[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinTarde-N":
                        objeto.rotacion = rotacion_sinTarde_N[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinNoche-M":
                        objeto.rotacion = rotacion_sinNoche_M[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]

                    if objeto.turno == "sinNoche-T":
                        objeto.rotacion = rotacion_sinNoche_T[:62]
                        objeto.rotacion_fecha = objeto.rotacion[0]
                              
                    if objeto.turno == "estatica-M" or objeto.turno == "estatica-T" or objeto.turno == "estatica-N":
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    
                

            #Esta lista alberga los usuarios que coincidan con el turno que el usuario desea filtrar por un día concreto
            usersFilterTurno = []
            if turno_fecha == "M" or turno_fecha == "T" or turno_fecha == "N":
                for objeto in usersFilter:
                    if objeto.turno == "Mañana":
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = rotacion_mañana[0]
                    if objeto.turno == "Tarde":
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = rotacion_tarde[0]
                    if objeto.turno == "Noche":
                        #Esto alberga el primero turno de la lista generada a partir del la fecha filtrada, es decir que guarda el turno correspondiente de ese usuario según la fecha filtrada
                        objeto.rotacion_fecha = rotacion_noche[0]
                    
                    #JORNADA PARCIALES
                    if objeto.turno == "sinMañana-T":
                        objeto.rotacion_fecha = rotacion_sinMañana_T[0]

                    if objeto.turno == "sinMañana-N":
                        objeto.rotacion_fecha = rotacion_sinMañana_N[0]

                    if objeto.turno == "sinTarde-M":
                        objeto.rotacion_fecha = rotacion_sinTarde_M[0]

                    if objeto.turno == "sinTarde-N":
                        objeto.rotacion_fecha = rotacion_sinTarde_N[0]

                    if objeto.turno == "sinNoche-M":
                        objeto.rotacion_fecha = rotacion_sinNoche_M[0]

                    if objeto.turno == "sinNoche-T":
                        objeto.rotacion_fecha = rotacion_sinNoche_T[0]
                              
                    if objeto.turno == "estatica-M" or objeto.turno == "estatica-T" or objeto.turno == "estatica-N":
                        objeto.rotacion_fecha = objeto.rotacion[0]
                    
                    
                    if objeto.rotacion_fecha == turno_fecha:
                        usersFilterTurno.append(objeto)
            
            else:
                for objeto in usersFilter:
                    if objeto.rotacion_fecha == turno_fecha:
                        usersFilterTurno.append(objeto)
            #Si se desea filtrar por todos los turnos entonces asignamos la misma lista de los usuarios filtrados
            if turno_fecha.lower() == "todo":
                usersFilterTurno = usersFilter
            #Filtramos a partir de la primera consulta aquellos usuario que tienen algún evento
            users_event = usersFilter.filter(evento__exact=True)
            # La lista colores alberga la posición inicial y final de cada evento asociada a cada usuario, por defecto se inicializa a una lista vacía
            colores = []
            #Cuando existen usuarios con eventos añadiremos en la lista colores las posiciones correspondientes de cada evento con su usuario relacionado
            #colores es una lista que almacena un conjunto de listas con esta estructura:
            #[PoscionInical,PosicionFinal,Id_Usuario]
            #Si la longitud de la lista es superior a 0 significa que existen usuarios con eventos
            if len(users_event) > 0:
                #Sacamos todo los eventos existentes
                eventos = Eventos.objects.all()
                #Iteramos por cada usuario y por cada evento para encontrar los eventos relacionados con un ususario
                for user in users_event:
                    for event in eventos:
                        # Esta condición saca el evento que está asociado con ese usuario
                        if user.id == event.usuario.id:
                            # Obtener la fechas sin la hora, para eso se pone el .date() al final
                            fecha_inicio = datetime.strptime(event.fecha_inicio, "%Y-%m-%d").date()
                            fecha_fin = datetime.strptime(event.fecha_fin, "%Y-%m-%d").date()
                            # En esto caso modificamos la fecha de hoy por la nueva fecha que el usuario desea filtrar
                            fecha_hoy = fecha_input
                            dias_previos = (fecha_inicio - fecha_hoy).days
                            diferencia_dias = (fecha_fin - fecha_inicio).days
                            # Cuando la fecha_inicio es inferior a la fecha de hoy la fecha de inicio pasaría a ser la fecha actual
                            if fecha_inicio < fecha_hoy:
                                dias_previos = 0
                                # Con la diferencia de días podemos sacar la posición final si sumamos los días previos y los días que dura el evento
                                diferencia_dias = (fecha_fin - fecha_hoy).days
                            if fecha_fin < fecha_hoy:
                                continue
                            # Con los días previos sacamos la posición de inicio del evento
                            posicion_listap2_inicio = dias_previos
                            # Con la suma de los días previos y los días que dura el evento sacaremos la posición final
                            posicion_listap2_fin = (diferencia_dias+dias_previos)
                            # El color equivale a la posición inicio y la fin con el id del usuario relacionado
                            if len(user.rotacion) <= posicion_listap2_fin:
                                posicion_listap2_fin = len(user.rotacion)-1
                                
                            color = [posicion_listap2_inicio, posicion_listap2_fin, user.id]
                            try:
                                user.rotacion[dias_previos]
                            except:
                                continue
                            colores.append(color)
                
                
            #Cuando existen usuarios filtrados se devuelve el html con esos usuarios
            if len(usersFilter) > 0:
                filter = {"operarios":usersFilterTurno, "fechas":dia,"año":año, "fecha_modificada":fecha_modificada ,"necesarios":necesidad,  "turno":turno,  "mes":mes, "colores":colores, "minValue":necesarios.minValueDate, "maquina":maquina}
                return render(request, "blogapp/index.html", {"diccionario":filter, "green":green, "red":red})
            # En caso contrario se devuelve un HTML con mensaje de error.
            else:
                filter = {"fecha_modificada":fecha_modificada ,"turno":turno}
                return render(request, "components/error.html",{"diccionario":filter})


def funcion_eventos(user, fecha_input, faltas=None):
        # Busca todo los eventos existentes
        if not faltas:
            eventos = Eventos.objects.all()
        else:
            eventos = Faltas.objects.all()
        for event in eventos:
            #Esta condición saca el usuario que tiene relación con ese evento
            if event.usuario_id == user.id:
                    
                    # Crear la zona horaria para España
                    zona_horaria_espana = pytz.timezone('Europe/Madrid')
                    # Obtener la fechas sin la hora, para eso se pone el .date() al final
                    fecha_inicio = datetime.strptime(event.fecha_inicio, "%Y-%m-%d").date()
                    fecha_fin = datetime.strptime(event.fecha_fin, "%Y-%m-%d").date()
                    fecha_hoy = fecha_input
                    dias_previos = (fecha_inicio - fecha_hoy).days
                    diferencia_dias = (fecha_fin - fecha_inicio).days + 1

                    #SI LA FECHA DE INICIO ES MENOR QUE LA FECHA ACTUAL EL VALOR DE LOS DÍAS PREVIOS CORRESPONDERÍA A LOS DÍAS PASADOS A PARTIR DEL DÍA DE HOY
                    if (fecha_inicio < fecha_hoy):
                        dias_previos = (fecha_hoy - fecha_inicio).days
                        diferencia_dias = (fecha_fin - fecha_hoy).days + 1
                    #SI EL EVENTO ESTA FUERA DE FECHA CONTINÚA CON EL SIGUIENTE EVENTO
                    if (fecha_fin < fecha_hoy):
                        continue
                    try:
                        user.rotacion[dias_previos]
                    except:
                        continue
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
                        if evento_actual == "F.I":
                            rotacion_operario = {"F.I":0}
                        # Esto lo que hace es hacer la rotación según el diccionario sin que sobrepase la posicion, explicado en el siguiente enlace -> https://chat.openai.com/share/c1651f02-571c-4bd6-b64d-1af898133ea0
                        turno_actual_posicion = (rotacion_operario[evento_actual] + 1) % len(rotacion_operario)
                        # Esto saca la clave si coincide con el valor de la posición en cualquier item del diccionario de rotacion_operario
                        evento_actual = next(nombre for nombre, posicion in rotacion_operario.items() if posicion == turno_actual_posicion)
                        # de cada semana guardo el turno en la lista
                        for _ in range(7):
                            turnos_rotativos.append(evento_actual)

                    # # reemplaza la lista_turnos del usuario con el nuevo contenido
                    if fecha_inicio < fecha_hoy:
                        i = 0
                        count = 0
                        
                        # Si la fecha de inicio es inferior a la actual se tiene que partir por la posición 0, por eso i vale 0 (representa el día de hoy) para que funcione bien el evento
                        #Cuando la fecha de inicio es inferior a la actual los días previos pasarían a significar los días pasados, por tanto descartamos de la lista los días pasados
                        turnos_eventos = turnos_rotativos[dias_previos:]
                        # Luego iteramos por cada item de la lista desde el inicio del evento hasta los días que dura el evento
                        for _ in range(len(turnos_eventos[:diferencia_dias])):
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
                        




#Aqui es donde llamamos a la función generica de turnos
#Hacemos que se necesite estar logeado para entrar en estas funciones además le pasamos a cada una la request, 
#los operarios necesarios por maquina y turno además del nombre de la maquina de cada función (Por la cuál se va a filtrar luego)

obj = necesarios2()
obj_color = colores_maquina()

def actualizar_colores():
    valor = {}
    file = "json\\colores.json"
    if os.path.exists(file):
        with open(file, 'r') as f:
            try:
                valor = json.load(f)
            except json.JSONDecodeError as e:
                print(e)
        
        if not valor == {}:
            if "autos" in valor:
                obj_color.update("autos", "green", valor["autos"]["green"])
                obj_color.update("autos", "red", valor["autos"]["red"])
                
            if "laser" in valor:
                obj_color.update("laser", "green", valor["laser"]["green"])
                obj_color.update("laser", "red", valor["laser"]["red"])
                
            if "tampo" in valor:
                obj_color.update("tampo", "green", valor["tampo"]["green"])
                obj_color.update("tampo", "red", valor["tampo"]["red"])
                
            if "pulpos" in valor:
                obj_color.update("pulpos", "green", valor["pulpos"]["green"])
                obj_color.update("pulpos", "red", valor["pulpos"]["red"])
                
            if "digital" in valor:
                obj_color.update("digital", "green", valor["digital"]["green"])
                obj_color.update("digital", "red", valor["digital"]["red"])
                
            if "bordado" in valor:
                obj_color.update("bordado", "green", valor["bordado"]["green"])
                obj_color.update("bordado", "red", valor["bordado"]["red"])
                
            if "termo" in valor:
                obj_color.update("termo", "green", valor["termo"]["green"])
                obj_color.update("termo", "red", valor["termo"]["red"])
                
            if "planchas" in valor:
                obj_color.update("planchas", "green", valor["planchas"]["green"])
                obj_color.update("planchas", "red", valor["planchas"]["red"])
                
            if "sublimacion" in valor:
                obj_color.update("sublimacion", "green", valor["sublimacion"]["green"])
                obj_color.update("sublimacion", "red", valor["sublimacion"]["red"])
                
            if "envasado" in valor:
                obj_color.update("envasado", "green", valor["envasado"]["green"])
                obj_color.update("envasado", "red", valor["envasado"]["red"])
                
            if "cosido" in valor:
                obj_color.update("cosido", "green", valor["cosido"]["green"])
                obj_color.update("cosido", "red", valor["cosido"]["red"])
                
            if "horno" in valor:
                obj_color.update("horno", "green", valor["horno"]["green"])
                obj_color.update("horno", "red", valor["horno"]["red"])
    else:
        with open(file, 'w') as f:
            json.dump({}, f)


                
def actualizar_valores():
    valor = {}
    file = "json\\semaforo.json"
    if os.path.exists(file):
        with open(file, 'r') as f:
            try:
                valor = json.load(f)
            except json.JSONDecodeError as e:
                print(e)
        if not valor == {}:
            
            if "autos" in valor:
                if not valor["autos"] <= 0:
                    obj.update("autos", valor["autos"])
                else:
                    obj.update("autos", necesarios.autos)
                    
            if "laser" in valor:
                if not valor["laser"] <= 0:
                    obj.update("laser", valor["laser"])
                else:
                    obj.update("laser", necesarios.laser)
                    
            if "tampo" in valor:
                if not valor["tampo"] <= 0:
                    obj.update("tampo", valor["tampo"])
                else:
                    obj.update("tampo", necesarios.tampo)
                    
            if "pulpos" in valor:
                if not valor["pulpos"] <= 0:
                    obj.update("pulpos", valor["pulpos"])
                else:
                    obj.update("pulpos", necesarios.pulpos)
                    
            if "digital" in valor:
                if not valor["digital"] <= 0:
                    obj.update("digital", valor["digital"])
                else:
                    obj.update("digital", necesarios.digital)
                    
            if "bordado" in valor:
                if not valor["bordado"] <= 0:
                    obj.update("bordado", valor["bordado"])
                else:
                    obj.update("bordado", necesarios.bordado)
                    
            if "termo" in valor:
                if not valor["termo"] <= 0:
                    obj.update("termo", valor["termo"])
                else:
                    obj.update("termo", necesarios.termo)
                    
            if "planchas" in valor:
                if not valor["planchas"] <= 0:
                    obj.update("planchas", valor["planchas"])
                else:
                    obj.update("planchas", necesarios.planchas)
                    
            if "sublimacion" in valor:
                if not valor["sublimacion"] <= 0:
                    obj.update("sublimacion", valor["sublimacion"])
                else:
                    obj.update("sublimacion", necesarios.sublimacion)
                    
            if "envasado" in valor:
                if not valor["envasado"] <= 0:
                    obj.update("envasado", valor["envasado"])
                else:
                    obj.update("envasado", necesarios.envasado)
                    
            if "cosido" in valor:
                if not valor["cosido"] <= 0:
                    obj.update("cosido", valor["cosido"])
                else:
                    obj.update("cosido", necesarios.cosido)
                    
            if "horno" in valor:
                if not valor["horno"] <= 0:
                    obj.update("horno", valor["horno"])
                else:
                    obj.update("horno", necesarios.horno)
    else:
        with open(file, 'w') as f:
            json.dump({}, f)

def colores_update(request):
    if request.method == "POST":
        valor = {}
        file = "json\\colores.json"
        if os.path.exists(file):
            with open(file, 'r') as f:
                try:
                    valor = json.load(f)
                except json.JSONDecodeError as e:
                    print(e)
            
            if not request.POST.get("maquina") == "otros":
                valor[request.POST.get("maquina")]={}
                valor[request.POST.get("maquina")]["green"]=int(request.POST.get("green"))
                valor[request.POST.get("maquina")]["red"]=int(request.POST.get("red"))
            else:
                valor["envasado"]={}
                valor["envasado"]["green"]=int(request.POST.get("green"))
                valor["envasado"]["red"]=int(request.POST.get("red"))
            
            with open(file, 'w') as f:
                json.dump(valor, f, indent=4)
        contador = 0
        for maquina in necesarios.lista_maquina:
            if maquina == request.POST.get("maquina"):
                url = necesarios.redirectsTurnos[contador]
            else:
                contador +=1
        
        return redirect(url)

def valores_update(request):
    if request.method == "POST":
        file = "json\\semaforo.json"
        if os.path.exists(file):
            with open(file, 'r') as f:
                try:
                    valor = json.load(f)
                except json.JSONDecodeError as e:
                    print(e)
            if not request.POST.get("maquina") == "otros":
                valor[request.POST.get("maquina")]=int(request.POST.get("valor"))
            else:
                valor["envasado"]=int(request.POST.get("valor"))
            with open(file, 'w') as f:
                json.dump(valor, f, indent=4)
        
        contador = 0
        for maquina in necesarios.lista_maquina:
            if maquina == request.POST.get("maquina"):
                url = necesarios.redirectsTurnos[contador]
            else:
                contador +=1
        
        return redirect(url)
    else:
        return redirect('/dashboard')

def valores_reset(request):
    if request.method == "POST":
        file = "json\\semaforo.json"
        if os.path.exists(file):
            with open(file, 'r') as f:
                try:
                    valor = json.load(f)
                except json.JSONDecodeError as e:
                    print(e)
            cantidad = 0
            contador_valor = 0
            for machine in necesarios.lista_maquina:
                if machine == request.POST.get("maquina"):
                    cantidad = necesarios.necesario[contador_valor]
                else:
                    contador_valor += 1
            if not request.POST.get("maquina") == "otros":
                valor[request.POST.get("maquina")]=cantidad
            else:
                valor["envasado"]=cantidad
            with open(file, 'w') as f:
                json.dump(valor, f, indent=4)
        
        contador = 0
        for maquina in necesarios.lista_maquina:
            if maquina == request.POST.get("maquina"):
                url = necesarios.redirectsTurnos[contador]
            else:
                contador +=1
        
        return redirect(url)
    else:
        return redirect('/dashboard')
    
@login_required
def turnotodo(request):
    return turnodefecto(request)

@login_required
def turnoautos(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.autos, "autos", green=obj_color.autos.green, red=obj_color.autos.red)
    
@login_required
def turnolaser(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.laser, "laser" , green=obj_color.laser.green, red=obj_color.laser.red)
    
@login_required
def turnotampo(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.tampo, "tampo" , green=obj_color.tampo.green, red=obj_color.tampo.red)
    
@login_required
def turnopulpos(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.pulpos,"pulpos" , green=obj_color.pulpos.green, red=obj_color.pulpos.red)
    
@login_required
def turnodigital(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.digital,"digital" , green=obj_color.digital.green, red=obj_color.digital.red)
    
@login_required
def turnobordado(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.bordado,"bordado" , green=obj_color.bordado.green, red=obj_color.bordado.red)
    
@login_required
def turnotermo(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.termo, "termo" , green=obj_color.termo.green, red=obj_color.termo.red)
    
@login_required
def turnoplanchas(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.planchas,"planchas" , green=obj_color.planchas.green, red=obj_color.planchas.red)
    
@login_required
def turnosublimacion(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.sublimacion, "sublimacion" , green=obj_color.sublimacion.green, red=obj_color.sublimacion.red)
    
@login_required
def turnoenvasado(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.envasado,"otros" , green=obj_color.envasado.green, red=obj_color.envasado.red)

@login_required
def cosido(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.cosido,"cosido", green=obj_color.cosido.green, red=obj_color.cosido.red)

@login_required
def turnohorno(request):
    actualizar_valores()
    actualizar_colores()
    return turnodefecto(request, obj.horno,"horno", green=obj_color.horno.green, red=obj_color.horno.red)
#Creamos una función para hacer permutados de usuarios(Intercambiar el turno de un usuairo por el de otro)
@login_required
def permutado(request):
    #Si el usuario tiene como True los permisos de superuser o admin tiene privilegios para acceder a esta view:
    if request.user.is_superuser or request.user.is_staff:
        #Si el metodo es GET:
        if request.method == 'GET':
            zona_horaria_espana = pytz.timezone('Europe/Madrid')
            fecha_modificada_str = necesarios.hoy
            fecha = datetime.strptime(fecha_modificada_str, '%Y-%m-%d').date()
            hoy = datetime.now(zona_horaria_espana).date()

            dias_previos = (fecha - hoy).days

            rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos],fecha_modificada_str)
            rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos],fecha_modificada_str)
            rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos],fecha_modificada_str)

            #JORNADA PARCIAL
            rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_modificada_str, sinMañana=True)
            rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_modificada_str, sinMañana=True)

            rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_modificada_str, sinTarde=True )    
            rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_modificada_str, sinTarde=True)

            rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_modificada_str, sinNoche=True)    
            rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_modificada_str, sinNoche=True)  
            
            #JORNADA ESTÁTICA
            rotacion_estatica_M = generar_turnos_rotativos("M", fecha_modificada_str, noRota=True)
            rotacion_estatica_T = generar_turnos_rotativos("T", fecha_modificada_str, noRota=True)
            rotacion_estatica_N = generar_turnos_rotativos("N", fecha_modificada_str, noRota=True)
            userMaquina = User.objects.all()
            users_disponibles=[]
            for user in userMaquina:

                if user.turno == 'Mañana':
                    user.rotacion = rotacion_mañana.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]
                                            
                elif user.turno == 'Tarde':
                    user.rotacion = rotacion_tarde.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "Noche":
                    user.rotacion = rotacion_noche.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "sinMañana-T":
                    user.rotacion = rotacion_sinMañana_T.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "sinMañana-N":
                    user.rotacion = rotacion_sinMañana_N.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "sinTarde-M":
                    user.rotacion = rotacion_sinTarde_M.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "sinTarde-N":
                    user.rotacion = rotacion_sinTarde_N.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "sinNoche-M":
                    user.rotacion = rotacion_sinNoche_M.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "sinNoche-T":
                    user.rotacion = rotacion_sinNoche_T.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "estatica-M":
                    user.rotacion = rotacion_estatica_M.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "estatica-T":
                    user.rotacion = rotacion_estatica_T.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]

                elif user.turno == "estatica-N":
                    user.rotacion = rotacion_estatica_N.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    user.rotacion = user.rotacion[:1]
                    user.rotacion_fecha = user.rotacion[0]
                
                users_disponibles = userMaquina
                
            users_disponibles = [user for user in users_disponibles if user.rotacion_fecha != "V" and user.rotacion_fecha != "L"]

            return render(request, 'blogapp/permutar.html', {"usuarios":users_disponibles, "fecha_modificada":fecha_modificada_str, "minValue":necesarios.minValueDate})
        #De lo contrario si el metodo es POST:
        else:
            #De lo contrario si el metodo es POST:
            if request.content_type == "application/json":
                datos_json = json.loads(request.body)
                lista = datos_json["lista"]
                # ids = [id[2] for id in lista]
                fechaini = datos_json["fecha_inicio"]
                fechafin = datos_json["fecha_fin"]
                turno_1 = lista[0][1]
                turno_2 = lista[1][1]

                if turno_1 == "M":
                    turno_1 = "Mañana"
                elif turno_1 == "T":
                    turno_1 = "Tarde"
                elif turno_1 == "N":
                    turno_1 = "Noche"

                if turno_2 == "M":
                    turno_2 = "Mañana"
                elif turno_2 == "T":
                    turno_2 = "Tarde"
                elif turno_2 == "N":
                    turno_2 = "Noche"

                user1 = get_object_or_404(User, pk=lista[0][2])
                user2 = get_object_or_404(User, pk=lista[1][2])
                
                user1.permutado = True
                user2.permutado = True

                user1.nombre = user1.apellido + ',' + user1.nombre
                user2.nombre = user2.apellido + ',' + user2.nombre

                creador = get_object_or_404(creator, pk=request.user.id)

                Permutado.objects.create(usuario=user1, fecha_inicio=fechaini, fecha_fin=fechafin, tipo=turno_2, auxiliar=user1.turno, creador=creador, maquina=False)
                Permutado.objects.create(usuario=user2, fecha_inicio=fechaini, fecha_fin=fechafin, tipo=turno_1, auxiliar=user2.turno, creador=creador, maquina=False)

                user1.save()
                user2.save()

                    
                return HttpResponse()
            #De lo contrario en el caso que el metodo sea POST
            else:
                zona_horaria_espana = pytz.timezone('Europe/Madrid')
                fecha_modificada_str = request.POST.get("fecha")
                #Obtenemos lo que el usuario introduce en el input de buscar
                search = request.POST.get('search')
                #Obtenemos lo que selecciona el usuario en el select de turno
                turno = request.POST.get('turno')
                #Obtenemos lo que selecciona le usuario en el select de maquina
                maquina = request.POST.get('maquina')
                 #Obtenemos los operarios que tengan como maquina la que haya seleccionado el usuario antes
                userMaquina = User.objects.filter(maquina__iexact=maquina)
                #Si el usuario tiene seleccionada maquina como todo obtiene todos los operarios sin filtrar por maquina (Comvertimos el input a minúscula para evitar problemas)
                if maquina.lower() == 'todo':
                    userMaquina = User.objects.all()
                
                fecha = datetime.strptime(fecha_modificada_str, '%Y-%m-%d').date()
                hoy = datetime.now(zona_horaria_espana).date()

                dias_previos = (fecha - hoy).days

                rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos],fecha_modificada_str)
                rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos],fecha_modificada_str)
                rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos],fecha_modificada_str)

                #JORNADA PARCIAL
                rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_modificada_str, sinMañana=True)
                rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_modificada_str, sinMañana=True)

                rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_modificada_str, sinTarde=True )    
                rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_modificada_str, sinTarde=True)

                rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_modificada_str, sinNoche=True)    
                rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_modificada_str, sinNoche=True)  
                
                #JORNADA ESTÁTICA
                rotacion_estatica_M = generar_turnos_rotativos("M", fecha_modificada_str, noRota=True)
                rotacion_estatica_T = generar_turnos_rotativos("T", fecha_modificada_str, noRota=True)
                rotacion_estatica_N = generar_turnos_rotativos("N", fecha_modificada_str, noRota=True)
                
                users_disponibles=[]
                for user in userMaquina:

                    if user.turno == 'Mañana':
                        user.rotacion = rotacion_mañana.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]
                                                
                    elif user.turno == 'Tarde':
                        user.rotacion = rotacion_tarde.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "Noche":
                        user.rotacion = rotacion_noche.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinMañana-T":
                        user.rotacion = rotacion_sinMañana_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinMañana-N":
                        user.rotacion = rotacion_sinMañana_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinTarde-M":
                        user.rotacion = rotacion_sinTarde_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinTarde-N":
                        user.rotacion = rotacion_sinTarde_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinNoche-M":
                        user.rotacion = rotacion_sinNoche_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinNoche-T":
                        user.rotacion = rotacion_sinNoche_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-M":
                        user.rotacion = rotacion_estatica_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-T":
                        user.rotacion = rotacion_estatica_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-N":
                        user.rotacion = rotacion_estatica_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]
                    
                    if turno.lower() == "todo":
                        users_disponibles = userMaquina
                    if user.rotacion[0] == "M" and turno.lower() == "mañana":
                        users_disponibles.append(user)
                    if user.rotacion[0] == "T" and turno.lower() == "tarde":
                        users_disponibles.append(user)
                    if user.rotacion[0] == "N" and turno.lower() == "noche":
                        users_disponibles.append(user)


                ids = [user.id for user in users_disponibles]
                users_disponibles_queryset = User.objects.filter(pk__in=ids)
                #Hacemos una petición a la base de datos filtrando los usuarios que tengan la misma id o que tengan un nombre parecido al input de filtrado
                userFilter = users_disponibles_queryset.filter(
                    Q(nombre__icontains=search)|
                    Q(id__iexact=search)
                )
                for user in userFilter:

                    if user.turno == 'Mañana':
                        user.rotacion = rotacion_mañana.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]
                                                
                    elif user.turno == 'Tarde':
                        user.rotacion = rotacion_tarde.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "Noche":
                        user.rotacion = rotacion_noche.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinMañana-T":
                        user.rotacion = rotacion_sinMañana_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinMañana-N":
                        user.rotacion = rotacion_sinMañana_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinTarde-M":
                        user.rotacion = rotacion_sinTarde_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinTarde-N":
                        user.rotacion = rotacion_sinTarde_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinNoche-M":
                        user.rotacion = rotacion_sinNoche_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinNoche-T":
                        user.rotacion = rotacion_sinNoche_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-M":
                        user.rotacion = rotacion_estatica_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-T":
                        user.rotacion = rotacion_estatica_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-N":
                        user.rotacion = rotacion_estatica_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]
                
                userFilter = [user for user in userFilter if user.rotacion_fecha != "V" and user.rotacion_fecha != "L"]

                return render(request, 'blogapp/permutar.html', {"usuarios":userFilter, "fecha_modificada":fecha_modificada_str, "minValue":necesarios.minValueDate})
    else:
        #De lo contrario en el caso de que no tenga permisos se muestra una vista de error diciendole que no tiene permisos suficientes para hacer eso
        return render(request, 'components/permisionError.html')


#Creamos una vista para poder modificar los turnos de los operarios en dias específicos
@login_required
def update(request):
    #Si el metodo es GET:
    if request.method == 'GET':
        #Iniciamos las variables para que al empezar estén vacías
        usuario = ""
        fecha = ""
        anio = ""
        turno_user = ""
        #user_request es un array que almacena varias listas, y cada lista tiene almacenada el id del usuario con sus respectivas fechas seleccionadas, 
        #Este método permite que dos o más usuarios puedan recargar la página y no se les pierda los datos seleccionados
        #Primero iteramos por cada lista obeniendo el id del usuario
        for user_id, data in necesarios.user_request:
            #comparamos si el id del usuario coincide con el id del usuario que hace la petición
            if user_id == request.user.id:
                #Si coincide sacamos todos los de datos a partir de la lista relacionada con ese usuario:
                usuario = get_object_or_404(User,pk=data[2])
                fecha = procesar_fecha(data[0])[0]
                anio = procesar_fecha(data[0])[1]
                turno_user = data[1]
                
        return render(request, 'blogapp/update.html', {"user":usuario, "fecha":fecha, "anio":anio, "turno":turno_user, "minValueDate":necesarios.hoy})
    else:
        #Si la cabezera tiene como titulo "application/json"
        if request.content_type == "application/json":
            #Parsea los datos de un json para poder acceder a sus atributos
            datos_json = json.loads(request.body)
            #Obtenemos la fila que ha sido clickeada
            fila = datos_json.get("fila")
            #Obtenemos la columna que ha sido clickeada
            columna = datos_json.get("columna")
            #Obtiene la lista de los datos antes parseados
            lista = datos_json.get("lista")
            
             #Se le resta -3 porque la lista fechas tiene las primeras cuantro posiciones [ID, NOMBRE, APELLIDO, MAQUINA,2ºCONOCIMIENTO], que se descartan y la primera fecha comienza en la posición 5, mientras que la lista meses solo tiene que dar tres saltos para coger el primer mes 
            # y como la columna tiene la posición que proviene de las fechas es necesario restarle 3 para que muestre bien el mes
            mes = columna - 3
            #La fecha almacena el número del día y su mes correspondiente, lista[-1] hace referencia a la última posición que es donde se encuentra la lista de los meses
            fecha = lista[5][columna], lista[-2][mes], lista[-1][mes]
            
            #Guardamos los datos en variables , luego se lo pasamos a la lista user_request que almacena el id del usuario que ha hecho la petición con sus datos correspondientes
            fecha_user = fecha
            turno_user = lista[fila][columna]
            id_user = lista[fila][0]
            necesarios.user_request.append((request.user.id, (fecha_user, turno_user, id_user)))
        else:
            #Si el usuario tiene como True los permisos de superuser y admin:
            if request.user.is_superuser or request.user.is_staff:
                #Obtenemos la fecha de inicio que introduce el usuario
                fechaini = request.POST.get("fechainicio")
                #Obtenemos la fecha de fin que introduce el usuario
                fechafin = request.POST.get("fechafin")
                #Obtenemos el turno vinculado con la fecha
                turnofecha = request.POST.get("turno-fecha")
                #Obtenemos el operario al que se le modifica el turno
                id_user = request.POST.get("user")
                #Obtenemos la maquina en la que esta el usuario al que le vamos a modificar el turno
                maquina = request.POST.get("maquina")
                observacion = request.POST.get("observacion")

                #BUSCO AL USUARIO
                user = get_object_or_404(User, pk=id_user)
                user.evento = True
                user.nombre = user.apellido + ',' + user.nombre
                user.save()
                #CREO EL NUEVO EVENTO VINCULADO AL USUARIO
                #fecha_inicio = datetime.strptime(fechaini, "%Y-%m-%d")
                #fecha_fin = datetime.strptime(fechafin, "%Y-%m-%d")
                creador = get_object_or_404(creator, pk=request.user.id)
                lista_eventos = Eventos.objects.all()
                lista_eventos = [evento for evento in lista_eventos]
                if len(lista_eventos) > 0:
                    lista_eventos = lista_eventos[-1].orden + 1
                else:
                    lista_eventos = 0
                evento = Eventos.objects.create(usuario=user, fecha_inicio=fechaini, fecha_fin=fechafin, turno_actualizado=turnofecha, creador=creador, observaciones=observacion, orden=lista_eventos)
                #Inicializamos count a 0
                count = 0
                #Para redireccionar al usuario a la misma url se itera primero por cada máquina existente
                for machine in necesarios.lista_maquina:
                    #Si la maquina en la que se encuentra el usuario coincide con la máquina de la lista, la url valdrá el valor correspondiente para
                    #redireccionar al usuario a la misma url, redirectTurnos es una lista con todas las posibles urls y están en el mismo orden que la lista_maquina
                    #(Lo pasamos por .lower para evitar problemas de mayúsculas)
                    if maquina.lower() == machine.lower():
                        url=necesarios.redirectsTurnos[count]
                    else:
                        #En caso de no encontrar coincidencia se continúa el for pero sumandole uno al contador
                        count = count + 1
                
                data = {
                    "id_request": request.user.id,
                    "fecha": fechaini
                }

                ruta_file = "json\\fechas.json"

                if os.path.exists(ruta_file):
                    with open(ruta_file, 'r') as f:
                        try:
                            lista = json.load(f)
                        except json.JSONDecodeError:
                            lista = []
                else:
                    lista = []

                updated = False

                for item in lista:
                        if item["id_request"] == request.user.id:
                            item["fecha"] = fechaini
                            updated = True
                            break
                
                if not updated:
                    lista.append(data)


                with open(ruta_file, 'w') as f:
                    json.dump(lista, f, indent=4)

                    
                return redirect(url)
            else:
                return render(request,'components/permisionError.html')
        
        return HttpResponse()

def procesar_fecha(fecha_str):
    # Dividir la cadena en día y mes
    _, dia = fecha_str[0].split(' ')
    #Obtenemos el mes
    mes = fecha_str[1]
    #Creamos un diccionario con todos los meses con sus numeros vinculados
    meses = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
    #Formateamos el mes
    mes_formated = meses[mes]
    #Obtenemos el año actual
    anio_actual = int(fecha_str[2])

    if anio_actual > int(datetime.now().year)+1:
        anio_actual = int(datetime.now().year)+1
    # Convertir a formato datetime
    fecha = datetime(year=anio_actual, month=int(mes_formated), day=int(dia))
    
    # # Formatear la fecha como AAAA/MM/DD
    fecha_formateada = fecha.strftime('%Y-%m-%d')
    
    return [fecha_formateada, anio_actual]

def generar_turnos_rotativos(turno_actual, fecha_input, sinMañana=None, sinTarde=None, sinNoche=None, noRota=None, activo=None):
    turnos_rotativos=[]

    if activo is None:
        turnos_rotativos.append(turno_actual)


    rotacion_operario = {"N":0,"T":1,"M":2}
    
    if sinMañana:
        rotacion_operario = {"N":0,"T":1}

    if sinTarde:
        rotacion_operario = {"N":0,"M":1}

    if sinNoche:
        rotacion_operario = {"T":0,"M":1}

    if noRota:
        rotacion_operario = {turno_actual:0}
        
    # Obtener la fecha total (dia, mes, año, hora) del día de hoy
    
    hoy_fecha_total = datetime.strptime(fecha_input, '%Y-%m-%d').date()
        
    # Obtener el día de la semana actual, le sumo uno porque el lunes empieza por 0
    dia_semana = hoy_fecha_total.weekday() + 1


    #calcula cuantos dias quedan para terminar la semana a partir del dia de hoy
    primera_semana = 7 - dia_semana

    if activo:
        primera_semana = 7

    # con datetime puedo sacar el año actual y sumarle uno para representar el año que viene y escoger el mes y el día, 
    # en este caso saco el primer día del primer mes del año que viene
    # primer_dia_proximo_anio = datetime(datetime.now().year + 1, 1, 1)
    

    # # Calcular la diferencia en días entre hoy y el primer día del próximo año contando a partir del día de hoy
    # dias_restantes = (primer_dia_proximo_anio - hoy_fecha_total).days + 1
    # semanas = dias_restantes // 7
    
    #Saco el turno de la primera semana
    for i in range (primera_semana) :
        turnos_rotativos.append(turno_actual)


    #Un año tiene 52 semanas saco el turno de todo el año
    for a in range(5000):
        # Esto lo que hace es hacer la rotación según el diccionario sin que sobrepase la posicion, explicado en el siguiente enlace -> https://chat.openai.com/share/c1651f02-571c-4bd6-b64d-1af898133ea0
        turno_actual_posicion = (rotacion_operario[turno_actual] + 1) % len(rotacion_operario)
        # Esto saca la clave si coincide con el valor de la posición en cualquier item del diccionario de rotacion_operario
        turno_actual = next(nombre for nombre, posicion in rotacion_operario.items() if posicion == turno_actual_posicion)
        # de cada semana guardo el turno en la lista
        for a in range(7):
            turnos_rotativos.append(turno_actual)
    



    # De vuelvo la lista acortada ya que tengo la primera semana y un año entero juntos
    return turnos_rotativos[:len(turnos_rotativos)-primera_semana]


#Creamos una función para mostrar las tareas (Comentarios)
@login_required
def tareas(request):
    fecha_actual = datetime.now()
    
    fecha_formateada = fecha_actual.strftime('%b %d, %Y')
    #Si el metodo de la request es GET hacemos lo siguiente:
    if request.method == "GET":
        
        #Obtenemos todas las tareas que no estan completadas
        Tareas_filtro = Tarea.objects.filter(fechacompleto__isnull=True).order_by('fecha_limite')
    #De lo contrario en el caso de que el metodo sea POST:
    else:
        #Obtenemos los datos que introducen en el input buscar
        search_term = request.POST.get("search")
        #Obtenemos las tareas que no estan completadas
        Tareas = Tarea.objects.filter(fechacompleto__isnull=True).order_by('fecha_limite')
        #Filtramos las tareas en las que lo introducido en el input tenga conincidencias con el titulo (No tienen que ser exactas) 
        
        Tareas_filtro = Tareas.filter(
            Q(titulo__icontains=search_term)|
            Q(creado__icontains=search_term)
        ).order_by('fecha_limite')
    #Si la lista de Tareas filtradas es mayor a 0 renderizamos una lista con todas las tareas que coincidan con los filtros
    if len(Tareas_filtro) > 0:
        return render(request, "components/tasks.html", {"tareas" : Tareas_filtro, "fecha_actual" : fecha_formateada})
    #De lo contrario mostramos la vista de error
    else:
        return render(request, "components/error_tareas.html", {"tareas" : Tareas_filtro})
#Creamos una función en la que mostraremos las tareas completadas
@login_required
def tareas_completadas(request):
    #Si el metodo es GET hacemos esto:
    if request.method == "GET":
        #Obtenemos todas las tareas que estén completadas, ordenadas de forma que se muestran arriba las ultimas completadas
        Tareas_filtro = Tarea.objects.filter(fechacompleto__isnull=False).order_by('-fechacompleto')
    #De lo contrario en el caso de que el metodo sea POST hacemos lo siguiente:
    else:
        #Obtenemos los datos que introducen en el input buscar
        search_term = request.POST.get("search")
        #Obtenemos las tareas que estan completadas
        Tareas = Tarea.objects.filter(fechacompleto__isnull=False)
        #Filtramos las tareas en las que lo introducido en el input tenga conincidencias con el titulo (No tienen que ser exactas) otra vez ordenadas
        Tareas_filtro = Tareas.filter(
            Q(titulo__icontains=search_term)|
            Q(creado__icontains=search_term)
        ).order_by('-fechacompleto')
    #Si la lista de Tareas filtradas es mayor a 0 renderizamos una lista con todas las tareas que coincidan con los filtros
    if len(Tareas_filtro) > 0:
        return render(request, "components/tasks.html", {"tareas" : Tareas_filtro})
    #De lo contrario mostramos la vista de error
    else:
        return render(request, "components/error_tareas.html", {"tareas" : Tareas_filtro})
#Creamos una fucnión para poder editar y ver los detalles de cada tarea además de poder completarla y eliminarla pasandole el id de la tarea que seleccione el usuario
@login_required
def detalle_tarea(request, tarea_id):
    #Si el metodo es GET hacemos lo siguiente:
    if request.method == "GET":
        #Obtenemos la tarea que su id coincide con el id de la tarea que ha clickeado el usuario
        tarea = get_object_or_404(Tarea, pk=tarea_id)
        #Creamos el form con python
        form = Taskform(objeto=tarea)
        #Le pasamos al html la tarea seleccionada y el formulario que será con lo que se editará la tarea
        return render (request, "components/task_detail.html", {"tarea": tarea, "form": form}) 
    else:
         #Obtenemos la tarea que su id coincide con el id de la tarea que ha clickeado el usuario
        tarea = get_object_or_404(Tarea, pk=tarea_id)
        #Creamos el form con python pasandole los introducido en el POST
        form = Taskform(request.POST, objeto=tarea)
        #Guardamos el formulario para actulaizar los datos 
        form.save()
        #Redireccionamos a la vista de tareas sin completar
        return redirect("tareas")
#Creamos la función para completar las tareas pasandole el id de la tarea que seleccione el usuario    
@login_required
def completar_tarea(request, tarea_id):
    #Obtenemos la tarea que su id coincide con el id de la tarea que ha clickeado el usuario
    tarea = get_object_or_404(Tarea, pk= tarea_id)
     #Si el metodo es POST:
    if request.method == "POST":
        #Rellenamos el campo de fecha completo con la fecha del momento en el que se clickea en completar
        tarea.fechacompleto = datetime.now()
        #Guardamos la tarea con el nuevo dato
        tarea.save()
        #Redireccionamos a tareas sin completar
        return redirect("tareas")
#Creamos una función para eliminar las tareas pasandole el id de la tarea que seleccione el usuario
@login_required    
def eliminar_tarea(request, tarea_id):
    #Obtenemos la tarea que su id coincide con el id de la tarea que ha clickeado el usuario
    tarea = get_object_or_404(Tarea, pk= tarea_id)
    #Si el metodo es POST:
    if request.method == "POST":
        #Eliminamos la tarea
        tarea.delete()
        #Redireccionamos a las tareas sin completar
        return redirect("tareas")

#Creamos una función para crear tareas nuevas (Comentarios)
@login_required
def crear_tareas(request):
    #Si el metodo es GET:
    if request.method == "GET":
        #Devolvemos al html el html de crear tarea y el form que hemos creado en python
        return render(request, "components/crear_tarea.html", {
            "form": Taskform
        })
    #De lo contrario en el caso de que el metodo sea POST:
    else:
        try:
            #Crea una instancia del formulario Taskform con los datos enviados en la solicitud POST
            form = Taskform(request.POST)
            #Guarda los datos del formulario en una nueva instancia del modelo asociado, pero no los guarda en la base de datos aún.
            new_task = form.save(commit=False)
            #Asigna el usuario actual (quien está haciendo la solicitud) como el usuario asociado a la nueva tarea.
            new_task.user = request.user
            #Guarda la nueva tarea en la base de datos.
            new_task.save()
            #Redirecciona a las tareas sin completar
            return redirect("tareas")
        except ValueError:
            return render(request, "components/crear_tarea.html", {
            "form": Taskform,
            "error" : "Por favor introduce datos validos"
        })
@login_required
#Creamos una función para que nos sugiran operacios de tecnicas en las que sobren cuando nos faltan en algun turno            
def sugerencias(request):
    actualizar_valores()
    zona_horaria_espana = pytz.timezone('Europe/Madrid')
    #Si el metodo es GET:
    if request.method == 'GET':
        ruta_file = "json\\sugerencias.json"

        if os.path.exists(ruta_file):
            with open(ruta_file, 'r') as f:
                try:
                    lista = json.load(f)
                except json.JSONDecodeError:
                    lista = []
        else:
            lista = []
        
        if len(lista) > 0:
            for item in lista:
                if item["id_request"] == request.user.id:
                    fecha_modificada_str = item["fecha"]
                    maquina = item["maquina"]
                    turno = item["turno"]

        fecha = datetime.strptime(fecha_modificada_str, '%Y-%m-%d').date()
        hoy = datetime.now(zona_horaria_espana).date()

        dias_previos = (fecha - hoy).days

        rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos],fecha_modificada_str)
        rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos],fecha_modificada_str)
        rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos],fecha_modificada_str)

        #JORNADA PARCIAL
        rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_modificada_str, sinMañana=True)
        rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_modificada_str, sinMañana=True)

        rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_modificada_str, sinTarde=True )    
        rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_modificada_str, sinTarde=True)

        rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_modificada_str, sinNoche=True)    
        rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_modificada_str, sinNoche=True)  
        
        #JORNADA ESTÁTICA
        rotacion_estatica_M = generar_turnos_rotativos("M", fecha_modificada_str, noRota=True)
        rotacion_estatica_T = generar_turnos_rotativos("T", fecha_modificada_str, noRota=True)
        rotacion_estatica_N = generar_turnos_rotativos("N", fecha_modificada_str, noRota=True)

        #Inicializamos count a 0
        count = 0
        #Creamos una lista vacia para luego meter los usuarios disponible ahí
        users_disponibles_global = []
        #Hacemos un bucle que encuentre los usuarios de cada maquina
        for user_maquina in necesarios.lista_maquina[:len(necesarios.lista_maquina)-2]:
            users_disponibles = []
            #SACO USUARIOS DE CADA MAQUINA
            user = User.objects.filter(
                Q(maquina__iexact=user_maquina)
                )
            #Si hay mas operarios de los que necesitamos hace lo siguiente:
            if len(user) > obj.necesario[count]:
               #Filtra los usuarios para que solo se muestren los que su conocimiento es igual que la maquina en la que faltan operarios(Es la maquina en la que esta el usuario antes de darle a las sugerencias),
               #que el turno en el que estan los operarios conincida con el turno que selecciona el usuario y por ultimo que la maquina principal del operario sea diferente a la que necesita mas operarios.
               usersFilter = user.filter(~Q(maquina__iexact=maquina))
               
               for user in usersFilter:

                    if user.turno == 'Mañana':
                        user.rotacion = rotacion_mañana.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]
                                                
                    elif user.turno == 'Tarde':
                        user.rotacion = rotacion_tarde.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "Noche":
                        user.rotacion = rotacion_noche.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinMañana-T":
                        user.rotacion = rotacion_sinMañana_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinMañana-N":
                        user.rotacion = rotacion_sinMañana_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinTarde-M":
                        user.rotacion = rotacion_sinTarde_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinTarde-N":
                        user.rotacion = rotacion_sinTarde_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinNoche-M":
                        user.rotacion = rotacion_sinNoche_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "sinNoche-T":
                        user.rotacion = rotacion_sinNoche_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-M":
                        user.rotacion = rotacion_estatica_M.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-T":
                        user.rotacion = rotacion_estatica_T.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]

                    elif user.turno == "estatica-N":
                        user.rotacion = rotacion_estatica_N.copy()
                        if user.evento:
                            funcion_eventos(user, fecha)
                        user.rotacion = user.rotacion[:1]
                        user.rotacion_fecha = user.rotacion[0]
                    
                    if user.rotacion[0] == "M" and turno.lower() == "mañana":
                        users_disponibles.append(user)
                    if user.rotacion[0] == "T" and turno.lower() == "tarde":
                        users_disponibles.append(user)
                    if user.rotacion[0] == "N" and turno.lower() == "noche":
                        users_disponibles.append(user)
                        
               if len(users_disponibles) > obj.necesario[count]:
                   diferencia = len(users_disponibles) - obj.necesario[count]
                   users_disponibles = [user for user in users_disponibles if user.conocimientos == maquina]
                   users_disponibles = users_disponibles[:diferencia]
               else:
                   users_disponibles = []      

            if len(users_disponibles) > 0:
                for itemUser in users_disponibles:
                    users_disponibles_global.append(itemUser)
                   
            count+=1
        diccionario = {"fecha_modificada":necesarios.hoy, "fecha_modificada2":fecha_modificada_str, "turno":turno, "usuarios":users_disponibles_global, "maquina":maquina, "minValue":necesarios.hoy}
        return render(request, 'blogapp/sugerencias.html', {"diccionario":diccionario})
    else:
         #Si la petición que le llega tiene en la cabecera el titulo "aplication/json" obtiene los siguientes datos:
        if request.content_type == "application/json":
            #esta variable parsea los datos que le llega del cuerpo de la petición para poder acceder a sus atributos
            datos_json = json.loads(request.body)
            #Obtiene la fila que le llega de la petición por javascirpt en html
            fila = datos_json.get("fila")
            #Obtiene la columna que le llega de la petición por javascirpt en html
            columna = datos_json.get("columna")
            #Obtiene la lista que le llega de la petición por javascirpt en html
            lista = datos_json.get("lista")
            mes = columna
            fecha = lista[5][columna + 3], lista[-2][mes], lista[-1][mes]
            maquina = datos_json.get("maquina")
            fecha = procesar_fecha(fecha)[0]
            turno = lista[fila][1]
            data = {
                    "id_request": request.user.id,
                    "fecha": fecha,
                    "maquina": maquina,
                    "turno": turno
                }

            ruta_file = "json\\sugerencias.json"

            if os.path.exists(ruta_file):
                with open(ruta_file, 'r') as f:
                    try:
                        lista = json.load(f)
                    except json.JSONDecodeError:
                        lista = []
            else:
                lista = []

            updated = False

            for item in lista:
                    if item["id_request"] == request.user.id:
                        item["fecha"] = fecha
                        item["maquina"] = maquina
                        item["turno"] = turno
                        updated = True
                        break
            
            if not updated:
                lista.append(data)


            with open(ruta_file, 'w') as f:
                json.dump(lista, f, indent=4)
            

            return HttpResponse()
        
        ############################################# METODO POR POST
        else:
            ruta_file = "json\\sugerencias.json"
            fecha_modificada_str = request.POST.get("fecha")
            turno = request.POST.get("turnoFecha")
            search_term = request.POST.get("search")

            if os.path.exists(ruta_file):
                with open(ruta_file, 'r') as f:
                    try:
                        lista = json.load(f)
                    except json.JSONDecodeError:
                        lista = []
            else:
                lista = []
            
            if len(lista) > 0:
                for item in lista:
                    if item["id_request"] == request.user.id:
                        maquina = item["maquina"]
            
            fecha = datetime.strptime(fecha_modificada_str, '%Y-%m-%d').date()
            hoy = datetime.now(zona_horaria_espana).date()

            dias_previos = (fecha - hoy).days

            rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos],fecha_modificada_str)
            rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos],fecha_modificada_str)
            rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos],fecha_modificada_str)

            #JORNADA PARCIAL
            rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_modificada_str, sinMañana=True)
            rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_modificada_str, sinMañana=True)

            rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_modificada_str, sinTarde=True )    
            rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_modificada_str, sinTarde=True)

            rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_modificada_str, sinNoche=True)    
            rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_modificada_str, sinNoche=True)  
            
            #JORNADA ESTÁTICA
            rotacion_estatica_M = generar_turnos_rotativos("M", fecha_modificada_str, noRota=True)
            rotacion_estatica_T = generar_turnos_rotativos("T", fecha_modificada_str, noRota=True)
            rotacion_estatica_N = generar_turnos_rotativos("N", fecha_modificada_str, noRota=True)

            #Inicializamos count a 0
            count = 0
            #Creamos una lista vacia para luego meter los usuarios disponible ahí
            users_disponibles_global = []
            #Hacemos un bucle que encuentre los usuarios de cada maquina
            for user_maquina in necesarios.lista_maquina[:len(necesarios.lista_maquina)-2]:
                users_disponibles = []
                #SACO USUARIOS DE CADA MAQUINA
                user = User.objects.filter(
                    Q(maquina__iexact=user_maquina)
                    )
                #Si hay mas operarios de los que necesitamos hace lo siguiente:
                if len(user) > obj.necesario[count]:
                    #Filtra los usuarios para que solo se muestren los que su conocimiento es igual que la maquina en la que faltan operarios(Es la maquina en la que esta el usuario antes de darle a las sugerencias),
                    #que el turno en el que estan los operarios conincida con el turno que selecciona el usuario y por ultimo que la maquina principal del operario sea diferente a la que necesita mas operarios.
                    usersFilter = user.filter(~Q(maquina__iexact=maquina))

                    for user in usersFilter:
                        if user.turno == 'Mañana':
                            user.rotacion = rotacion_mañana.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]
                                                    
                        elif user.turno == 'Tarde':
                            user.rotacion = rotacion_tarde.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "Noche":
                            user.rotacion = rotacion_noche.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinMañana-T":
                            user.rotacion = rotacion_sinMañana_T.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinMañana-N":
                            user.rotacion = rotacion_sinMañana_N.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinTarde-M":
                            user.rotacion = rotacion_sinTarde_M.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinTarde-N":
                            user.rotacion = rotacion_sinTarde_N.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinNoche-M":
                            user.rotacion = rotacion_sinNoche_M.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinNoche-T":
                            user.rotacion = rotacion_sinNoche_T.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "estatica-M":
                            user.rotacion = rotacion_estatica_M.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "estatica-T":
                            user.rotacion = rotacion_estatica_T.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "estatica-N":
                            user.rotacion = rotacion_estatica_N.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]
                        
                        if turno.lower() == "todo":
                            users_disponibles = User.objects.filter(Q(conocimientos__iexact=maquina) & ~Q(maquina__iexact=maquina)) 
                        if user.rotacion[0] == "M" and turno.lower() == "mañana":
                            users_disponibles.append(user)
                        if user.rotacion[0] == "T" and turno.lower() == "tarde":
                            users_disponibles.append(user)
                        if user.rotacion[0] == "N" and turno.lower() == "noche":
                            users_disponibles.append(user)
                            
                    if len(users_disponibles) > obj.necesario[count]:
                        diferencia = len(users_disponibles) - obj.necesario[count]
                        users_disponibles = [user for user in users_disponibles if user.conocimientos == maquina]
                        users_disponibles = users_disponibles[:diferencia]
                    else:
                        users_disponibles = []     
                        
                if len(users_disponibles) > 0:
                    for itemUser in users_disponibles:
                        users_disponibles_global.append(itemUser)
                        
                count+=1
            ids = [user.id for user in users_disponibles_global]
            users_disponibles_queryset = User.objects.filter(pk__in=ids)

            users_disponibles_queryset = users_disponibles_queryset.filter(
                Q(id__iexact=search_term) |
                Q(nombre__icontains=search_term)
            )
            for user in users_disponibles_queryset:
                        if user.turno == 'Mañana':
                            user.rotacion = rotacion_mañana.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]
                                                    
                        elif user.turno == 'Tarde':
                            user.rotacion = rotacion_tarde.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "Noche":
                            user.rotacion = rotacion_noche.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinMañana-T":
                            user.rotacion = rotacion_sinMañana_T.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinMañana-N":
                            user.rotacion = rotacion_sinMañana_N.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinTarde-M":
                            user.rotacion = rotacion_sinTarde_M.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinTarde-N":
                            user.rotacion = rotacion_sinTarde_N.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinNoche-M":
                            user.rotacion = rotacion_sinNoche_M.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "sinNoche-T":
                            user.rotacion = rotacion_sinNoche_T.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "estatica-M":
                            user.rotacion = rotacion_estatica_M.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "estatica-T":
                            user.rotacion = rotacion_estatica_T.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]

                        elif user.turno == "estatica-N":
                            user.rotacion = rotacion_estatica_N.copy()
                            if user.evento:
                                funcion_eventos(user, fecha)
                            user.rotacion = user.rotacion[:1]
                            user.rotacion_fecha = user.rotacion[0]
                        

            diccionario = {"fecha_modificada":necesarios.hoy, "fecha_modificada2":fecha_modificada_str, "turno":turno, "usuarios":users_disponibles_queryset, "maquina":maquina, "minValue":necesarios.hoy}
            return render(request, 'blogapp/sugerencias.html', {"diccionario":diccionario})

#Creamos una función para enviar el usuario que nos sugiere a la nueva maquina  
@login_required   
def añadir_sugerencia(request):
     if request.content_type == "application/json":
        #esta variable parsea los datos que le llega del cuerpo de la petición para poder acceder a sus atributos
        datos_json = json.loads(request.body)
        lista = datos_json["lista"]
        ids = [id[2] for id in lista]
        fechaini = datos_json["fecha_inicio"]
        fechafin = datos_json["fecha_fin"]
        maquina = datos_json["maquina"]
        users = User.objects.filter(pk__in=ids)
        
        for obj in users:
            obj.permutado = True
            obj.nombre = obj.apellido + ',' + obj.nombre
            creador = get_object_or_404(creator, pk=request.user.id)
            Permutado.objects.create(usuario=obj, fecha_inicio=fechaini, fecha_fin=fechafin, tipo=maquina, auxiliar=obj.maquina, creador=creador, maquina=True)
            obj.save()
            

        return HttpResponse()
        
        
@login_required
def evento_view(request):
    if request.method == "GET":
        eventos_filtro = Eventos.objects.all()
        return render(request, "components/eventos.html", {"Eventos" : eventos_filtro})
    else:
        search_term = request.POST.get("search")
        turno = request.POST.get("turno")
        maquina = request.POST.get("maquina")
        eventos = Eventos.objects.all()
        usuarios_filtro = User.objects.filter(evento__exact=True)
        eventos_filtro = eventos
        
        if search_term != "" and maquina.lower() == "todo":
            eventos_filtro = [] 
            usuarios_filtro = usuarios_filtro.filter(Q(nombre__icontains=search_term) | Q(id__iexact=search_term))
            for user in usuarios_filtro:
                for evento in eventos:
                    if user.id == evento.usuario.id:
                        eventos_filtro.append(evento)
        
        elif search_term != "" and maquina.lower() != "todo":
            eventos_filtro = []
            usuarios_filtro = usuarios_filtro.filter(Q(nombre__icontains=search_term) | Q(id__iexact=search_term) & Q(maquina__iexact=maquina))
            for user in usuarios_filtro:
                for evento in eventos:
                    if user.id == evento.usuario.id:
                        eventos_filtro.append(evento)
        
        elif search_term == "" and maquina.lower() != "todo":
            eventos_filtro = []
            usuarios_filtro = usuarios_filtro.filter(Q(maquina__iexact=maquina))
            for user in usuarios_filtro:
                for evento in eventos:
                    if user.id == evento.usuario.id:
                        eventos_filtro.append(evento)
        
        if turno.lower() != "todo":
            eventos_filtro = [evento for evento in eventos_filtro if evento.turno_actualizado == turno]
        
        eventos_filtro = sorted(eventos_filtro, key=lambda evento: evento.orden)

    if len(eventos_filtro) > 0:
        return render(request, "components/eventos.html", {"Eventos" : eventos_filtro})
    else:
        return render(request, "components/eventos.html", {"Eventos" : eventos, "error" : "No se ha encontrado a ningún usuario relacionado"})

@login_required
def evento_detail(request, evento_id):
    if request.method == "GET":
        evento = get_object_or_404(Eventos, pk=evento_id)
        form = Taskform_eventos(instance=evento)
        return render (request, "components/detalle_evento.html", {"Eventos": evento, "form": form}) 
    else:
        evento = get_object_or_404(Eventos, pk=evento_id)
        user = get_object_or_404(User, pk=evento.usuario.id)
        user.nombre = user.apellido + ',' + user.nombre
        user.evento = True
        user.save()
        form = Taskform_eventos(request.POST, instance=evento)
        form.save()
        return redirect("mostrar_eventos")
#Creamos una fucnión para eliminar los eventos pasandole el id del evento que ha clickeado el usuario    
@login_required
def evento_delete(request, evento_id):
    # Obtenemos el evento en el que su id coincida con el id del evento que haya clickeado el usuario 
    evento = get_object_or_404(Eventos, pk= evento_id)
    #Obtiene la instancia del usuario asociada al evento
    user = get_object_or_404(User, pk= evento.usuario.id)
    #Inicializa la cantidad de eventos del usuario a 0 para hacer comprobaciones
    cantidad_eventos_usuario = 0
    #Obtiene todos los eventos
    all_events = Eventos.objects.all()
    #Comprueba cuantos eventos tiene el usuario y cada vez que encuentra alguno suma +1 a la cuenta que hemos inicializado a 0 antes
    for event in all_events:
        if event.usuario.id == user.id:
            cantidad_eventos_usuario += 1
    #Despues de comprobar los eventos que tiene el usuario, si el usuario tiene menos que 1 osea no tiene eventos se le cambia el user.evento a False porque no tiene ninguno
    if cantidad_eventos_usuario == 1:
        user.evento = False
    #Guardamos los nuevos daltos para el usuario
    user.nombre = user.apellido + ',' + user.nombre
    user.save()
    #Si el metodo es POST:
    if request.method == "POST":
        #Eliminarmos el evento 
        evento.delete()
        #Redireccionamos a mostrar eventos
        return redirect("mostrar_eventos")
    
def estadisticas(request, maquina, tipo, fecha_input=None, user_id=None):
    permutas()
    zona_horaria_espana = pytz.timezone('Europe/Madrid')
    
    UsersFiltered = User.objects.filter(Q(maquina__iexact=maquina) & ~Q(categoria__iexact="RESPONSABLE"))
    usuario = None
    if user_id:
        UsersFiltered = User.objects.filter(id__exact=user_id)
        usuario = get_object_or_404(User, pk=user_id)
    if tipo == "d":
        hoy = datetime.now(zona_horaria_espana).date()
        fecha_actual = hoy.strftime('%Y-%m-%d')
        dia_semana = hoy.weekday()

        dia_lunes = hoy.day - dia_semana

        fecha_string = fecha_actual
        fecha = hoy

        if fecha_input is not None:
            fecha_string = fecha_input
            fecha = datetime.strptime(fecha_input, '%Y-%m-%d').date()
            fecha_actual = fecha_input
            dias_previos = (fecha - hoy).days
        else:
            dias_previos = 0
        
        rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos], fecha_string)
        
        rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos], fecha_string)
        rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos], fecha_string)

        rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_string, sinMañana=True)
        rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_string, sinMañana=True)

        rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_string, sinTarde=True )    
        rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_string, sinTarde=True)

        rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_string, sinNoche=True)    
        rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_string, sinNoche=True)  

        rotacion_estatica_M = generar_turnos_rotativos("M", fecha_string, noRota=True)
        rotacion_estatica_T = generar_turnos_rotativos("T", fecha_string, noRota=True)
        rotacion_estatica_N = generar_turnos_rotativos("N", fecha_string, noRota=True)


        Mañana = []
        Tarde = []
        Noche = []
        Licencia = []
        Vacaciones = []


        for user in UsersFiltered:

            if user.turno == 'Mañana':
                user.rotacion = rotacion_mañana.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == 'Tarde':
                user.rotacion = rotacion_tarde.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)


            elif user.turno == "Noche":
                user.rotacion = rotacion_noche.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "sinMañana-T":
                user.rotacion = rotacion_sinMañana_T.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "sinMañana-N":
                user.rotacion = rotacion_sinMañana_N.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "sinTarde-M":
                user.rotacion = rotacion_sinTarde_M.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "sinTarde-N":
                user.rotacion = rotacion_sinTarde_N.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "sinNoche-M":
                user.rotacion = rotacion_sinNoche_M.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "sinNoche-T":
                user.rotacion = rotacion_sinNoche_T.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "estatica-M":
                user.rotacion = rotacion_estatica_M.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "estatica-T":
                user.rotacion = rotacion_estatica_T.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

            elif user.turno == "estatica-N":
                user.rotacion = rotacion_estatica_N.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:1]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        Mañana.append(user)
                    if turno == 'T':
                        Tarde.append(user)
                    if turno == 'N':
                        Noche.append(user)
                    if turno == 'L' or turno == 'B':
                        Licencia.append(user)
                    if turno == 'V':
                        Vacaciones.append(user)

        return render(request, 'blogapp/estadisticas/estadisticas_dia.html', {"Mañana":len(Mañana), 
                                                                 "Tarde":len(Tarde), 
                                                                 "Noche":len(Noche), 
                                                                 "Licencia":len(Licencia), 
                                                                 "Vacaciones":len(Vacaciones),
                                                                 "fecha_modificada":fecha_actual,
                                                                 "tipo": tipo,
                                                                 "user":usuario,
                                                                 "minValue":necesarios.hoy})


    if tipo == "s":
        hoy = datetime.now(zona_horaria_espana).date()

        if fecha_input is not None:
            fecha_input = datetime.strptime(fecha_input, '%Y-%m-%d').date()
        else:
            fecha_input = datetime.now().date()
                        
        fecha_actual = fecha_input.strftime("%Y-%m-%d")            
        dia_semana = fecha_input.weekday()
        
        fecha_rango_retroceder = [fecha_input - timedelta(days=i) for i in range(dia_semana+1)]
        fecha_rango_avanzar = [fecha_rango_retroceder[-1] + timedelta(days=i) for i in range(7)]
        fecha_string = fecha_rango_retroceder[-1].strftime('%Y-%m-%d')
        fecha = fecha_rango_retroceder[-1]
   
        
        if fecha < hoy:
            dias_previos = 0
        else:
            dias_previos = (fecha - hoy).days

        meses = {'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12}
        meses_inverso = {valor:clave for clave, valor in meses.items()}


        lunes = "Lunes - " + str(fecha_rango_avanzar[0].day) + " de " + str(meses_inverso[fecha_rango_avanzar[0].month])
        martes = "Martes - " + str(fecha_rango_avanzar[1].day) + " de " + str(meses_inverso[fecha_rango_avanzar[1].month])
        miercoles = "Miércoles - " + str(fecha_rango_avanzar[2].day) + " de " + str(meses_inverso[fecha_rango_avanzar[2].month])
        jueves = "Jueves - " + str(fecha_rango_avanzar[3].day) + " de " + str(meses_inverso[fecha_rango_avanzar[3].month])
        viernes = "Viernes - " + str(fecha_rango_avanzar[4].day) + " de " + str(meses_inverso[fecha_rango_avanzar[4].month])
        sabado = "Sábado - " + str(fecha_rango_avanzar[5].day) + " de " + str(meses_inverso[fecha_rango_avanzar[5].month])
        domingo = "Domingo - " + str(fecha_rango_avanzar[6].day) + " de " + str(meses_inverso[fecha_rango_avanzar[6].month])

    
        rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos], fecha_string, activo=True)
        rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos], fecha_string, activo=True)
        rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos], fecha_string, activo=True)
        
        

        rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_string, sinMañana=True, activo=True)
        rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_string, sinMañana=True, activo=True)

        rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_string, sinTarde=True, activo=True)    
        rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_string, sinTarde=True, activo=True)

        rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_string, sinNoche=True, activo=True)    
        rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_string, sinNoche=True, activo=True)          

        rotacion_estatica_M = generar_turnos_rotativos("M", fecha_string, noRota=True, activo=True)
        rotacion_estatica_T = generar_turnos_rotativos("T", fecha_string, noRota=True, activo=True)
        rotacion_estatica_N = generar_turnos_rotativos("N", fecha_string, noRota=True, activo=True)

        semana = {
        "Lunes": {"Mañana": [], "Tarde": [], "Noche": [], "Licencia": [], "Vacaciones": []},
        "Martes": {"Mañana": [], "Tarde": [], "Noche": [], "Licencia": [], "Vacaciones": []},
        "Miercoles": {"Mañana": [], "Tarde": [], "Noche": [], "Licencia": [], "Vacaciones": []},
        "Jueves": {"Mañana": [], "Tarde": [], "Noche": [], "Licencia": [], "Vacaciones": []},
        "Viernes": {"Mañana": [], "Tarde": [], "Noche": [], "Licencia": [], "Vacaciones": []},
        "Sabado": {"Mañana": [], "Tarde": [], "Noche": [], "Licencia": [], "Vacaciones": []},
        "Domingo": {"Mañana": [], "Tarde": [], "Noche": [], "Licencia": [], "Vacaciones": []}
        }

        dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]


        for user in UsersFiltered:

            if user.turno == 'Mañana':
                user.rotacion = rotacion_mañana.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]
                
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                
                                        
            elif user.turno == 'Tarde':
                user.rotacion = rotacion_tarde.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]
                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                


            elif user.turno == "Noche":
                user.rotacion = rotacion_noche.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "sinMañana-T":
                user.rotacion = rotacion_sinMañana_T.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "sinMañana-N":
                user.rotacion = rotacion_sinMañana_N.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "sinTarde-M":
                user.rotacion = rotacion_sinTarde_M.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "sinTarde-N":
                user.rotacion = rotacion_sinTarde_N.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "sinNoche-M":
                user.rotacion = rotacion_sinNoche_M.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "sinNoche-T":
                user.rotacion = rotacion_sinNoche_T.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "estatica-M":
                user.rotacion = rotacion_estatica_M.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "estatica-T":
                user.rotacion = rotacion_estatica_T.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)                

            elif user.turno == "estatica-N":
                user.rotacion = rotacion_estatica_N.copy()
                if user.evento:
                    funcion_eventos(user, fecha)
                user.rotacion = user.rotacion[:7]

                for dia_semana, turno in enumerate(user.rotacion):
                    if turno == 'M':
                        semana[dias[dia_semana]]["Mañana"].append(user)                
                    if turno == 'T':
                        semana[dias[dia_semana]]["Tarde"].append(user)                
                    if turno == 'N':
                        semana[dias[dia_semana]]["Noche"].append(user)                
                    if turno == 'L' or turno == 'B':
                        semana[dias[dia_semana]]["Licencia"].append(user)                
                    if turno == 'V':
                        semana[dias[dia_semana]]["Vacaciones"].append(user)  
        count = 0
        necesidad_maquina = 0

        for item_maquina in necesarios.lista_maquina:
            if item_maquina == maquina:
                    actualizar_valores()
                    necesidad_maquina = obj.necesario[count]
            else:
                count += 1
            
        return render(request, 'blogapp/estadisticas/estadisticas_semana.html', {
                                                            # Lunes
                                                            "L_Mañana": len(semana["Lunes"]["Mañana"]),
                                                            "L_Tarde": len(semana["Lunes"]["Tarde"]),
                                                            "L_Noche": len(semana["Lunes"]["Noche"]),
                                                            "L_Licencia": len(semana["Lunes"]["Licencia"]),
                                                            "L_Vacaciones": len(semana["Lunes"]["Vacaciones"]),

                                                            # Martes
                                                            "Ma_Mañana": len(semana["Martes"]["Mañana"]),
                                                            "Ma_Tarde": len(semana["Martes"]["Tarde"]),
                                                            "Ma_Noche": len(semana["Martes"]["Noche"]),
                                                            "Ma_Licencia": len(semana["Martes"]["Licencia"]),
                                                            "Ma_Vacaciones": len(semana["Martes"]["Vacaciones"]),

                                                            # Miércoles (sin tilde)
                                                            "Mi_Mañana": len(semana["Miercoles"]["Mañana"]),
                                                            "Mi_Tarde": len(semana["Miercoles"]["Tarde"]),
                                                            "Mi_Noche": len(semana["Miercoles"]["Noche"]),
                                                            "Mi_Licencia": len(semana["Miercoles"]["Licencia"]),
                                                            "Mi_Vacaciones": len(semana["Miercoles"]["Vacaciones"]),

                                                            # Jueves
                                                            "J_Mañana": len(semana["Jueves"]["Mañana"]),
                                                            "J_Tarde": len(semana["Jueves"]["Tarde"]),
                                                            "J_Noche": len(semana["Jueves"]["Noche"]),
                                                            "J_Licencia": len(semana["Jueves"]["Licencia"]),
                                                            "J_Vacaciones": len(semana["Jueves"]["Vacaciones"]),

                                                            # Viernes
                                                            "V_Mañana": len(semana["Viernes"]["Mañana"]),
                                                            "V_Tarde": len(semana["Viernes"]["Tarde"]),
                                                            "V_Noche": len(semana["Viernes"]["Noche"]),
                                                            "V_Licencia": len(semana["Viernes"]["Licencia"]),
                                                            "V_Vacaciones": len(semana["Viernes"]["Vacaciones"]),

                                                            # Sábado (sin tilde)
                                                            "Sa_Mañana": len(semana["Sabado"]["Mañana"]),
                                                            "Sa_Tarde": len(semana["Sabado"]["Tarde"]),
                                                            "Sa_Noche": len(semana["Sabado"]["Noche"]),
                                                            "Sa_Licencia": len(semana["Sabado"]["Licencia"]),
                                                            "Sa_Vacaciones": len(semana["Sabado"]["Vacaciones"]),

                                                            # Domingo
                                                            "D_Mañana": len(semana["Domingo"]["Mañana"]),
                                                            "D_Tarde": len(semana["Domingo"]["Tarde"]),
                                                            "D_Noche": len(semana["Domingo"]["Noche"]),
                                                            "D_Licencia": len(semana["Domingo"]["Licencia"]),
                                                            "D_Vacaciones": len(semana["Domingo"]["Vacaciones"]),

                                                            "Lunes": lunes,
                                                            "Martes": martes,
                                                            "Miercoles": miercoles,
                                                            "Jueves": jueves,
                                                            "Viernes": viernes,
                                                            "Sabado": sabado,
                                                            "Domingo": domingo,

                                                            "fecha_modificada":fecha_actual,
                                                            "minValue":necesarios.hoy,
                                                            "necesarios": necesidad_maquina,
                                                            "user":usuario,
                                                            "tipo": tipo
                                                            })
    if tipo == "a":
            hoy = datetime.now(zona_horaria_espana).date()

            if fecha_input is not None:
                fecha_input = datetime.strptime(fecha_input, '%Y-%m-%d').date()
            else:
                fecha_input = datetime.now().date()
            
            fecha_actual = fecha_input.strftime("%Y-%m-%d") 

            fecha_string = datetime(year=fecha_input.year, month=1, day=int(1)).strftime('%Y-%m-%d')
            fecha = datetime(year=fecha_input.year, month=1, day=int(1)).date()
            fecha_hoy = datetime(year=hoy.year, month=1, day=int(1)).date()
            retroceder = False
            if fecha.year == hoy.year:
                dias_previos = (datetime.now().date() - fecha).days
                retroceder = True
            else:
                dias_previos = (fecha - datetime.now().date()).days

            dias_meses = { 'Enero': 31, 'Febrero': 31+28, 'Marzo': 31+28+31, 'Abril': 31+28+31+30, 'Mayo': 31+28+31+30+31, 'Junio': 31+28+31+30+31+30, 'Julio': 31+28+31+30+31+30+31, 'Agosto': 31+28+31+30+31+30+31+31, 'Septiembre': 31+28+31+30+31+30+31+31+30, 'Octubre': 31+28+31+30+31+30+31+31+30+31, 'Noviembre': 31+28+31+30+31+30+31+31+30+31+30, 'Diciembre': 31+28+31+30+31+30+31+31+30+31+30+31 }
            days_of_year = 365
            #COMPRUEBA SI LA FECHA ES DE UN AÑO BISIESTO O NO
            if (fecha.year % 4 == 0) and (fecha.year % 100 != 0) or (fecha.year % 400 == 0):
                dias_meses = { 'Enero': 31, 'Febrero': 31+29, 'Marzo': 31+29+31, 'Abril': 31+29+31+30, 'Mayo': 31+29+31+30+31, 'Junio': 31+29+31+30+31+30, 'Julio': 31+29+31+30+31+30+31, 'Agosto': 31+29+31+30+31+30+31+31, 'Septiembre': 31+29+31+30+31+30+31+31+30, 'Octubre': 31+29+31+30+31+30+31+31+30+31, 'Noviembre': 31+29+31+30+31+30+31+31+30+31+30, 'Diciembre': 31+29+31+30+31+30+31+31+30+31+30+31 }
                days_of_year = 366

            

            rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañana[dias_previos], fecha_string, activo=True)
            rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTarde[dias_previos], fecha_string, activo=True)
            rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNoche[dias_previos], fecha_string, activo=True) 
            
            if retroceder:
                rotacion_mañana = generar_turnos_rotativos(necesarios.turno.rotacionMañanaR[dias_previos], fecha_string, activo=True)
                rotacion_tarde = generar_turnos_rotativos(necesarios.turno.rotacionTardeR[dias_previos], fecha_string, activo=True)
                rotacion_noche = generar_turnos_rotativos(necesarios.turno.rotacionNocheR[dias_previos], fecha_string, activo=True) 

            rotacion_sinMañana_T = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Tarde[dias_previos], fecha_string, sinMañana=True, activo=True)
            rotacion_sinMañana_N = generar_turnos_rotativos(necesarios.turno.rotacionSinMañana_Noche[dias_previos], fecha_string, sinMañana=True, activo=True)

            rotacion_sinTarde_M = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Mañana[dias_previos], fecha_string, sinTarde=True, activo=True)    
            rotacion_sinTarde_N = generar_turnos_rotativos(necesarios.turno.rotacionSinTarde_Noche[dias_previos], fecha_string, sinTarde=True, activo=True)

            rotacion_sinNoche_M = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Mañana[dias_previos], fecha_string, sinNoche=True, activo=True)    
            rotacion_sinNoche_T = generar_turnos_rotativos(necesarios.turno.rotacionSinNoche_Tarde[dias_previos], fecha_string, sinNoche=True, activo=True)          

            rotacion_estatica_M = generar_turnos_rotativos("M", fecha_string, noRota=True, activo=True)
            rotacion_estatica_T = generar_turnos_rotativos("T", fecha_string, noRota=True, activo=True)
            rotacion_estatica_N = generar_turnos_rotativos("N", fecha_string, noRota=True, activo=True)

            meses = {
                "Enero": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0}, 
                "Febrero": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Marzo": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Abril": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Mayo": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Junio": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Julio": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Agosto": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Septiembre": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Octubre": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Noviembre": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0},
                "Diciembre": {"Mañana": 0, "Tarde": 0, "Noche": 0, "Licencia": 0, "Vacaciones": 0, "Faltas":0}
            }

            total_mañana = 0
            total_tarde = 0
            total_noche = 0
            total_licencia = 0
            total_vacaciones = 0
            total_faltas = 0

            for user in UsersFiltered:

                if user.turno == 'Mañana':
                    user.rotacion = rotacion_mañana.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == 'Tarde':
                    user.rotacion = rotacion_tarde.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0


                elif user.turno == "Noche":
                    user.rotacion = rotacion_noche.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "sinMañana-T":
                    user.rotacion = rotacion_sinMañana_T.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "sinMañana-N":
                    user.rotacion = rotacion_sinMañana_N.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "sinTarde-M":
                    user.rotacion = rotacion_sinTarde_M.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "sinTarde-N":
                    user.rotacion = rotacion_sinTarde_N.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "sinNoche-M":
                    user.rotacion = rotacion_sinNoche_M.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "sinNoche-T":
                    user.rotacion = rotacion_sinNoche_T.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "estatica-M":
                    user.rotacion = rotacion_estatica_M.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "estatica-T":
                    user.rotacion = rotacion_estatica_T.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0

                elif user.turno == "estatica-N":
                    user.rotacion = rotacion_estatica_N.copy()
                    if user.evento:
                        funcion_eventos(user, fecha)
                    if user.faltas > 0:
                        funcion_eventos(user, fecha, faltas=True)
                    user.rotacion = user.rotacion[:days_of_year]
                    
                    for dia_semana, turno in enumerate(user.rotacion):
                        if turno == 'M':
                            total_mañana += 1             
                        if turno == 'T':
                            total_tarde += 1
                        if turno == 'N':
                            total_noche += 1
                        if turno == 'L' or turno == 'B':
                            total_licencia += 1
                        if turno == 'V':
                            total_vacaciones += 1
                        if turno == 'F.I':
                            total_faltas += 1
                        
                        if dia_semana + 1 == dias_meses["Enero"]:
                            meses["Enero"]["Mañana"] += total_mañana
                            meses["Enero"]["Tarde"] += total_tarde
                            meses["Enero"]["Noche"] += total_noche
                            meses["Enero"]["Licencia"] += total_licencia
                            meses["Enero"]["Vacaciones"] += total_vacaciones
                            meses["Enero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Febrero"]:
                            meses["Febrero"]["Mañana"] += total_mañana
                            meses["Febrero"]["Tarde"] += total_tarde
                            meses["Febrero"]["Noche"] += total_noche
                            meses["Febrero"]["Licencia"] += total_licencia
                            meses["Febrero"]["Vacaciones"] += total_vacaciones
                            meses["Febrero"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Marzo"]:
                            meses["Marzo"]["Mañana"] += total_mañana
                            meses["Marzo"]["Tarde"] += total_tarde
                            meses["Marzo"]["Noche"] += total_noche
                            meses["Marzo"]["Licencia"] += total_licencia
                            meses["Marzo"]["Vacaciones"] += total_vacaciones
                            meses["Marzo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Abril"]:
                            meses["Abril"]["Mañana"] += total_mañana
                            meses["Abril"]["Tarde"] += total_tarde
                            meses["Abril"]["Noche"] += total_noche
                            meses["Abril"]["Licencia"] += total_licencia
                            meses["Abril"]["Vacaciones"] += total_vacaciones
                            meses["Abril"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Mayo"]:
                            meses["Mayo"]["Mañana"] += total_mañana
                            meses["Mayo"]["Tarde"] += total_tarde
                            meses["Mayo"]["Noche"] += total_noche
                            meses["Mayo"]["Licencia"] += total_licencia
                            meses["Mayo"]["Vacaciones"] += total_vacaciones
                            meses["Mayo"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Junio"]:
                            meses["Junio"]["Mañana"] += total_mañana
                            meses["Junio"]["Tarde"] += total_tarde
                            meses["Junio"]["Noche"] += total_noche
                            meses["Junio"]["Licencia"] += total_licencia
                            meses["Junio"]["Vacaciones"] += total_vacaciones
                            meses["Junio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Julio"]:
                            meses["Julio"]["Mañana"] += total_mañana
                            meses["Julio"]["Tarde"] += total_tarde
                            meses["Julio"]["Noche"] += total_noche
                            meses["Julio"]["Licencia"] += total_licencia
                            meses["Julio"]["Vacaciones"] += total_vacaciones
                            meses["Julio"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Agosto"]:
                            meses["Agosto"]["Mañana"] += total_mañana
                            meses["Agosto"]["Tarde"] += total_tarde
                            meses["Agosto"]["Noche"] += total_noche
                            meses["Agosto"]["Licencia"] += total_licencia
                            meses["Agosto"]["Vacaciones"] += total_vacaciones
                            meses["Agosto"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Septiembre"]:
                            meses["Septiembre"]["Mañana"] += total_mañana
                            meses["Septiembre"]["Tarde"] += total_tarde
                            meses["Septiembre"]["Noche"] += total_noche
                            meses["Septiembre"]["Licencia"] += total_licencia
                            meses["Septiembre"]["Vacaciones"] += total_vacaciones
                            meses["Septiembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Octubre"]:
                            meses["Octubre"]["Mañana"] += total_mañana
                            meses["Octubre"]["Tarde"] += total_tarde
                            meses["Octubre"]["Noche"] += total_noche
                            meses["Octubre"]["Licencia"] += total_licencia
                            meses["Octubre"]["Vacaciones"] += total_vacaciones
                            meses["Octubre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Noviembre"]:
                            meses["Noviembre"]["Mañana"] += total_mañana
                            meses["Noviembre"]["Tarde"] += total_tarde
                            meses["Noviembre"]["Noche"] += total_noche
                            meses["Noviembre"]["Licencia"] += total_licencia
                            meses["Noviembre"]["Vacaciones"] += total_vacaciones
                            meses["Noviembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                        elif dia_semana + 1 == dias_meses["Diciembre"]:
                            meses["Diciembre"]["Mañana"] += total_mañana
                            meses["Diciembre"]["Tarde"] += total_tarde
                            meses["Diciembre"]["Noche"] += total_noche
                            meses["Diciembre"]["Licencia"] += total_licencia
                            meses["Diciembre"]["Vacaciones"] += total_vacaciones
                            meses["Diciembre"]["Faltas"] += total_faltas
                            total_faltas = 0
                            total_mañana = 0
                            total_tarde = 0
                            total_noche = 0
                            total_licencia = 0
                            total_vacaciones = 0
                
            return render(request, 'blogapp/estadisticas/estadisticas_año.html', {
                                                                #Enero
                                                                "Enero_Mañana":meses["Enero"]["Mañana"],
                                                                "Enero_Tarde":meses["Enero"]["Tarde"],
                                                                "Enero_Noche":meses["Enero"]["Noche"],
                                                                "Enero_Licencia":meses["Enero"]["Licencia"],
                                                                "Enero_Vacaciones":meses["Enero"]["Vacaciones"],
                                                                "Enero_Faltas":meses["Enero"]["Faltas"],

                                                                # Febrero
                                                                "Febrero_Mañana": meses["Febrero"]["Mañana"],
                                                                "Febrero_Tarde": meses["Febrero"]["Tarde"],
                                                                "Febrero_Noche": meses["Febrero"]["Noche"],
                                                                "Febrero_Licencia": meses["Febrero"]["Licencia"],
                                                                "Febrero_Vacaciones": meses["Febrero"]["Vacaciones"],
                                                                "Febrero_Faltas": meses["Febrero"]["Faltas"],

                                                                # Marzo
                                                                "Marzo_Mañana": meses["Marzo"]["Mañana"],
                                                                "Marzo_Tarde": meses["Marzo"]["Tarde"],
                                                                "Marzo_Noche": meses["Marzo"]["Noche"],
                                                                "Marzo_Licencia": meses["Marzo"]["Licencia"],
                                                                "Marzo_Vacaciones": meses["Marzo"]["Vacaciones"],
                                                                "Marzo_Faltas": meses["Marzo"]["Faltas"],

                                                                # Abril
                                                                "Abril_Mañana": meses["Abril"]["Mañana"],
                                                                "Abril_Tarde": meses["Abril"]["Tarde"],
                                                                "Abril_Noche": meses["Abril"]["Noche"],
                                                                "Abril_Licencia": meses["Abril"]["Licencia"],
                                                                "Abril_Vacaciones": meses["Abril"]["Vacaciones"],
                                                                "Abril_Faltas": meses["Abril"]["Faltas"],

                                                                # Mayo
                                                                "Mayo_Mañana": meses["Mayo"]["Mañana"],
                                                                "Mayo_Tarde": meses["Mayo"]["Tarde"],
                                                                "Mayo_Noche": meses["Mayo"]["Noche"],
                                                                "Mayo_Licencia": meses["Mayo"]["Licencia"],
                                                                "Mayo_Vacaciones": meses["Mayo"]["Vacaciones"],
                                                                "Mayo_Faltas": meses["Mayo"]["Faltas"],

                                                                # Junio
                                                                "Junio_Mañana": meses["Junio"]["Mañana"],
                                                                "Junio_Tarde": meses["Junio"]["Tarde"],
                                                                "Junio_Noche": meses["Junio"]["Noche"],
                                                                "Junio_Licencia": meses["Junio"]["Licencia"],
                                                                "Junio_Vacaciones": meses["Junio"]["Vacaciones"],
                                                                "Junio_Faltas": meses["Junio"]["Faltas"],

                                                                # Julio
                                                                "Julio_Mañana": meses["Julio"]["Mañana"],
                                                                "Julio_Tarde": meses["Julio"]["Tarde"],
                                                                "Julio_Noche": meses["Julio"]["Noche"],
                                                                "Julio_Licencia": meses["Julio"]["Licencia"],
                                                                "Julio_Vacaciones": meses["Julio"]["Vacaciones"],
                                                                "Julio_Faltas": meses["Julio"]["Faltas"],

                                                                # Agosto
                                                                "Agosto_Mañana": meses["Agosto"]["Mañana"],
                                                                "Agosto_Tarde": meses["Agosto"]["Tarde"],
                                                                "Agosto_Noche": meses["Agosto"]["Noche"],
                                                                "Agosto_Licencia": meses["Agosto"]["Licencia"],
                                                                "Agosto_Vacaciones": meses["Agosto"]["Vacaciones"],
                                                                "Agosto_Faltas": meses["Agosto"]["Faltas"],

                                                                # Septiembre
                                                                "Septiembre_Mañana": meses["Septiembre"]["Mañana"],
                                                                "Septiembre_Tarde": meses["Septiembre"]["Tarde"],
                                                                "Septiembre_Noche": meses["Septiembre"]["Noche"],
                                                                "Septiembre_Licencia": meses["Septiembre"]["Licencia"],
                                                                "Septiembre_Vacaciones": meses["Septiembre"]["Vacaciones"],
                                                                "Septiembre_Faltas": meses["Septiembre"]["Faltas"],

                                                                # Octubre
                                                                "Octubre_Mañana": meses["Octubre"]["Mañana"],
                                                                "Octubre_Tarde": meses["Octubre"]["Tarde"],
                                                                "Octubre_Noche": meses["Octubre"]["Noche"],
                                                                "Octubre_Licencia": meses["Octubre"]["Licencia"],
                                                                "Octubre_Vacaciones": meses["Octubre"]["Vacaciones"],
                                                                "Octubre_Faltas": meses["Octubre"]["Faltas"],

                                                                # Noviembre
                                                                "Noviembre_Mañana": meses["Noviembre"]["Mañana"],
                                                                "Noviembre_Tarde": meses["Noviembre"]["Tarde"],
                                                                "Noviembre_Noche": meses["Noviembre"]["Noche"],
                                                                "Noviembre_Licencia": meses["Noviembre"]["Licencia"],
                                                                "Noviembre_Vacaciones": meses["Noviembre"]["Vacaciones"],
                                                                "Noviembre_Faltas": meses["Noviembre"]["Faltas"],

                                                                # Diciembre
                                                                "Diciembre_Mañana": meses["Diciembre"]["Mañana"],
                                                                "Diciembre_Tarde": meses["Diciembre"]["Tarde"],
                                                                "Diciembre_Noche": meses["Diciembre"]["Noche"],
                                                                "Diciembre_Licencia": meses["Diciembre"]["Licencia"],
                                                                "Diciembre_Vacaciones": meses["Diciembre"]["Vacaciones"],
                                                                "Diciembre_Faltas": meses["Diciembre"]["Faltas"],

                                                                "fecha_modificada":fecha_actual,
                                                                "minValue":necesarios.hoy,
                                                                "user":usuario,
                                                                "tipo": tipo
                                                                })

@login_required
def estadisticas_auto(request):
    if request.method == "GET":
        return estadisticas(request, "autos", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "autos", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))

 
@login_required
def estadisticas_laser(request):
    if request.method == "GET":
            return estadisticas(request, "laser", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "laser", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
        
@login_required
def estadisticas_tampo(request):
    if request.method == "GET":
            return estadisticas(request, "tampo", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "tampo", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
        
@login_required
def estadisticas_pulpos(request):
    if request.method == "GET":
            return estadisticas(request, "pulpos", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "pulpos", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
        
@login_required
def estadisticas_digital(request):
    if request.method == "GET":
            return estadisticas(request, "digital", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "digital", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
@login_required
def estadisticas_bordado(request):
    if request.method == "GET":
            return estadisticas(request, "bordado", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "bordado", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
@login_required
def estadisticas_termo(request):
    if request.method == "GET":
            return estadisticas(request, "termo", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "termo", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
@login_required
def estadisticas_planchas(request):
    if request.method == "GET":
            return estadisticas(request, "planchas", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "planchas", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
@login_required
def estadisticas_sublimacion(request):
    if request.method == "GET":
            return estadisticas(request, "sublimacion", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "sublimacion", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
@login_required
def estadisticas_envasado(request):
    if request.method == "GET":
            return estadisticas(request, "otros", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "otros", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
@login_required
def estadisticas_cosido(request):
    if request.method == "GET":
            return estadisticas(request, "cosido", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "cosido", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
@login_required
def estadisticas_horno(request):
    if request.method == "GET":
            return estadisticas(request, "horno", tipo="d")
    if request.method == "POST":
        return estadisticas(request, "horno", tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"))
    
    
@login_required
def estadisticas_user(request, user_id):
    user = get_object_or_404(User,pk=user_id)
    if request.method == "GET":
        return estadisticas(request=request,maquina=user.maquina,tipo="a",user_id=user_id)
    if request.method == "POST":
        return estadisticas(request, maquina=user.maquina, tipo=request.POST.get("tipo"), fecha_input=request.POST.get("fecha"), user_id=user_id)

@login_required
def tracking(request):

    ruta_file = "json\\tracking.json"

    if os.path.exists(ruta_file):
        with open(ruta_file, 'r') as f:
            try:
                lista = json.load(f)
            except json.JSONDecodeError:
                lista = []
    else:
        lista = []
    
        
    return render(request, 'blogapp/registros/updates_operarios.html', {"lista":lista})

@login_required
def operarios_borrados(request):
    if request.method == "GET":
        ruta_file = "json\\operarios_borrados.json"

        if os.path.exists(ruta_file):
            with open(ruta_file, 'r') as f:
                try:
                    lista = json.load(f)
                except json.JSONDecodeError:
                    lista = []
        else:
            lista = []
        
            
        return render(request, 'blogapp/registros/operarios_borrados.html', {"lista":lista})
    if request.method == "POST":
        ruta_file = "json\\operarios_borrados.json"

        if os.path.exists(ruta_file):
            with open(ruta_file, 'r') as f:
                try:
                    lista = json.load(f)
                except json.JSONDecodeError:
                    lista = []
        else:
            lista = []
        
        maquina = request.POST.get("maquina")
        turno = request.POST.get("turno")
        search = request.POST.get("search")
        if maquina.lower() != "todo":
            lista = [user for user in lista if user["maquina"].lower() == maquina.lower()]
        
        if turno.lower() != "todo":
            lista = [user for user in lista if user["turno"].lower() == turno.lower()]

        if search != "":
            lista = [user for user in lista if str(user["id"]) == search or search.lower() in user["nombre"].lower()]
            
        return render(request, 'blogapp/registros/operarios_borrados.html', {"lista":lista})
@login_required
def block_view_logged(request):
    if request.method == "GET" and request.user.is_superuser:
        users = User.objects.all()
        return render(request, 'blogapp/incidencias/exp_usuarios.html', {"users":users})
    elif request.method == "GET" and not request.user.is_superuser:
        return render(request, 'components/error_generico.html')
        
    if request.method == "POST":
        maquina = request.POST.get("maquina").lower()
        turno = request.POST.get("turno").lower()
        search = request.POST.get("search")
        if turno != "todo" and maquina != "todo":
            users = User.objects.filter(Q(maquina__iexact=maquina) & Q(turno__iexact=turno))
        elif turno == "todo" and maquina != "todo":
            users = User.objects.filter(maquina__iexact=maquina)
        elif turno != "todo" and maquina == "todo":
            users = User.objects.filter(turno__iexact=turno)
        else:
            users = User.objects.all()
            
        if search != "":
            users = users.filter(Q(nombre__icontains=search) | Q(id__iexact=search))
            
        return render(request, 'blogapp/incidencias/exp_usuarios.html', {"users":users})
@login_required
def block_view(request):
    if request.method == "GET":
        return render(request, 'blogapp/incidencias/block_view.html')
    if request.method == "POST":
        user = authenticate( request ,username=request.user.username, password=request.POST.get("password") )
        if user:
            return redirect('historial')
        else:
            return render(request, 'blogapp/incidencias/block_view.html', {"error":"Contraseña incorrecta"})

@login_required
def expediente(request):
    if request.method == "GET" and not request.user.is_superuser:
        users = User.objects.all()
        return render(request, 'blogapp/incidencias/exp_usuarios.html', {"users":users})
    elif request.method == "GET" and request.user.is_superuser:
        return redirect ('blockview')
        
    if request.method == "POST":
        maquina = request.POST.get("maquina").lower()
        turno = request.POST.get("turno").lower()
        search = request.POST.get("search")
        if turno != "todo" and maquina != "todo":
            users = User.objects.filter(Q(maquina__iexact=maquina) & Q(turno__iexact=turno))
        elif turno == "todo" and maquina != "todo":
            users = User.objects.filter(maquina__iexact=maquina)
        elif turno != "todo" and maquina == "todo":
            users = User.objects.filter(turno__iexact=turno)
        else:
            users = User.objects.all()
            
        if search != "":
            users = users.filter(Q(nombre__icontains=search) | Q(id__iexact=search))
            
        return render(request, 'blogapp/incidencias/exp_usuarios.html', {"users":users})
    
@login_required
def mis_expedientes(request):
    if request.method == "GET":
        partes = Parte.objects.filter(creador__exact=request.user.id)
        incidencias = Incidencia.objects.filter(creador__exact=request.user.id)
        users = set()
        for parte in partes:
            user = get_object_or_404(User,pk=parte.operario.id)
            users.add(user)
        
        for incidencia in incidencias:
            user = get_object_or_404(User,pk=incidencia.operario.id)
            users.add(user)
        
        return render(request, 'blogapp/incidencias/misIncidencias/mis_exp_usuarios.html', {"users":users})
        
    if request.method == "POST":
        maquina = request.POST.get("maquina").lower()
        turno = request.POST.get("turno").lower()
        search = request.POST.get("search")
        
        partes = Parte.objects.filter(creador__exact=request.user.id)
        incidencias = Incidencia.objects.filter(creador__exact=request.user.id)
        users = set()
        for parte in partes:
            user = get_object_or_404(User,pk=parte.operario.id)
            users.add(user)
        
        for incidencia in incidencias:
            user = get_object_or_404(User,pk=incidencia.operario.id)
            users.add(user)
        users = list(users)
        users = [user.id for user in users]
        
        users_queryset = User.objects.filter(pk__in=users)
        
        if turno != "todo" and maquina != "todo":
            users = users_queryset.filter(Q(maquina__iexact=maquina) & Q(turno__iexact=turno))
        elif turno == "todo" and maquina != "todo":
            users = users_queryset.filter(maquina__iexact=maquina)
        elif turno != "todo" and maquina == "todo":
            users = users_queryset.filter(turno__iexact=turno)
        else:
            users = users_queryset.all()
            
        if search != "":
            users = users_queryset.filter(Q(nombre__icontains=search) | Q(id__iexact=search))
            
        return render(request, 'blogapp/incidencias/misIncidencias/mis_exp_usuarios.html', {"users":users})

@login_required
def expediente_detail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.user.is_superuser:
       incidencias_user = Incidencia.objects.filter(operario__exact=user.id)
       partes_user = Parte.objects.filter(operario__exact=user.id)
    else:
        incidencias_user = Incidencia.objects.filter(Q(operario__exact=user.id) & Q(creador__exact=request.user.id))
        partes_user = Parte.objects.filter(Q(operario__exact=user.id) & Q(creador__exact=request.user.id))  

    if request.method == "GET":
        return render (request, 'blogapp/incidencias/exp_user_detail.html', {"user":user, "partes":partes_user, "incidencias":incidencias_user})

@login_required
def crearparte(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "GET":
        zona_horaria_espana = pytz.timezone('Europe/Madrid')
        fecha_actual = datetime.now(zona_horaria_espana).strftime('%Y-%m-%d %H:%M')
        return render (request, 'blogapp/incidencias/crearparte.html', {"user":user,"fecha_modificada":fecha_actual})
    if request.method == "POST":
        maquina = request.POST.get("maquina")
        numeroPedido = request.POST.get("numeroPedido")
        numeroFabricacion = request.POST.get("numeroFabricacion")
        unidades = request.POST.get("unidades")
        fecha = request.POST.get("fecha")
        motivo = request.POST.get("motivo")
        observacion = request.POST.get("observacion")
        observacionResponsable = request.POST.get("observacionResponsable")
        observacionOperario = request.POST.get("observacionOperario")
        accion = request.POST.get("accion")
        cantidadPartes = Parte.objects.filter(operario__exact=user.id)
        cantidadIncidencias = Incidencia.objects.filter(operario__exact=user.id)
        user.expediente = len(cantidadPartes) + len(cantidadIncidencias) + 1
        user.nombre = user.apellido + ',' + user.nombre
        user.save()
        Parte.objects.create(
                            operario=user,  # user es un objeto de User
                            numero_pedido=numeroPedido,
                            numero_fabricacion=numeroFabricacion,
                            unidades=unidades,
                            fecha_reporte=fecha,
                            observacion=observacion,
                            observacion_responsable=observacionResponsable,
                            observacion_operario=observacionOperario,
                            maquina=maquina,
                            motivo=motivo,
                            accion=accion,
                            creador=request.user  # request.user es un objeto de Usuario
                        )
        if request.user.is_superuser:
            return redirect('user_detail_expediente', user_id=user.id)
        else :
            return redirect('expedientes')
@login_required
def deleteparte(request, parte_id):
    parte = get_object_or_404(Parte, pk=parte_id)
    user = get_object_or_404(User, pk=parte.operario.id)
    parte.delete()

    if user.expediente <= 0:
        user.expediente = 0
    else:
        cantidadPartes = Parte.objects.filter(operario__exact=user.id)
        cantidadIncidencias = Incidencia.objects.filter(operario__exact=user.id)
        user.expediente = len(cantidadPartes) + len(cantidadIncidencias)
    user.nombre = user.apellido + ',' + user.nombre
    user.save()
    if request.user.is_superuser:
            return redirect('user_detail_expediente', user_id=user.id)
    else:
        return redirect('expedientes')
@login_required
def deleteincidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    user = get_object_or_404(User, pk=incidencia.operario.id)
    foto = incidencia.imagen
    archivo_eliminar = os.path.join(settings.BASE_DIR, 'media', str(foto))
    # os.remove(archivo_eliminar)
    incidencia.delete()
    if user.expediente <= 0:
        user.expediente = 0
    else:
        cantidadPartes = Parte.objects.filter(operario__exact=user.id)
        cantidadIncidencias = Incidencia.objects.filter(operario__exact=user.id)
        user.expediente = len(cantidadPartes) + len(cantidadIncidencias)
    user.nombre = user.apellido + ',' + user.nombre
    user.save()
    if request.user.is_superuser:
            return redirect('user_detail_expediente', user_id=user.id)
    else:
        return redirect('expedientes')

@login_required
def updateparte(request, parte_id):
    parte = get_object_or_404(Parte, pk=parte_id)
    user = get_object_or_404(User, pk=parte.operario.id)
    if request.method == "GET":
        return render (request, 'blogapp/incidencias/updateparte.html', {"user":user,"fecha_modificada":parte.fecha_reporte, "parte":parte})
    if request.method == "POST":
        maquina = request.POST.get("maquina")
        numeroPedido = request.POST.get("numeroPedido")
        numeroFabricacion = request.POST.get("numeroFabricacion")
        unidades = request.POST.get("unidades")
        fecha = request.POST.get("fecha")
        motivo = request.POST.get("motivo")
        observacion = request.POST.get("observacion")
        observacionResponsable = request.POST.get("observacionResponsable")
        observacionOperario = request.POST.get("observacionOperario")
        accion = request.POST.get("accion")
        
        parte.maquina = maquina
        parte.numero_pedido = numeroPedido
        parte.numero_fabricacion = numeroFabricacion
        parte.unidades = unidades
        parte.fecha_reporte = fecha
        parte.motivo = motivo
        parte.observacion = observacion
        parte.observacion_responsable = observacionResponsable
        parte.observacion_operario = observacionOperario
        parte.accion = accion
        parte.save()
        
        return redirect('user_detail_expediente', user_id=user.id)
    
    
@login_required
def crearincidencia(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "GET":
        zona_horaria_espana = pytz.timezone('Europe/Madrid')
        fecha_actual = datetime.now(zona_horaria_espana).strftime('%Y-%m-%d %H:%M')
        return render (request, 'blogapp/incidencias/crearincidencia.html', {"user":user,"fecha_modificada":fecha_actual})
    if request.method == "POST":
        fechaIncidencia = request.POST.get("fechaIncidencia")
        fechaReporte = request.POST.get("fechaReporte")
        referenciaArticulo = request.POST.get("referenciaArticulo")
        nombreArticulo = request.POST.get("nombreArticulo")
        numeroPedido = request.POST.get("numeroPedido")
        unidadesTotales = request.POST.get("unidadesTotales")
        unidadesMalMarcadas = request.POST.get("unidadesMalMarcadas")
        costeIncidencia = request.POST.get("costeIncidencia")
        responsableTurno = request.POST.get("responsableTurno")
        maquina = request.POST.get("maquina")
        personasImplicadas = request.POST.get("personasImplicadas")
        personaDetectaError = request.POST.get("personaDetectaError")
        testigos = request.POST.get("testigos")
        observaciones = request.POST.get("observaciones")
        imagen = request.FILES.get("imagen")
        
        cantidadPartes = Parte.objects.filter(operario__exact=user.id)
        cantidadIncidencias = Incidencia.objects.filter(operario__exact=user.id)
        user.expediente = len(cantidadPartes) + len(cantidadIncidencias) + 1

        user.nombre = user.apellido + ',' + user.nombre
        user.save()
        Incidencia.objects.create(
                            operario=user,  # user es un objeto de User
                            fecha_incidencia=fechaIncidencia,
                            fecha_reporte=fechaReporte,
                            referencia_articulo=referenciaArticulo,
                            nombre_articulo=nombreArticulo,
                            numero_pedido=numeroPedido,
                            unidades_totales_pedido=unidadesTotales,
                            unidades_mal_marcadas_revisadas=unidadesMalMarcadas,
                            coste_incidencia=costeIncidencia,
                            tecnica_marcado=maquina,
                            responsable_turno=responsableTurno,
                            personas_implicadas=personasImplicadas,
                            persona_quien_detecta_error=personaDetectaError,
                            testigos=testigos,
                            observaciones=observaciones,
                            creador=request.user,
                            imagen=imagen
                        )
        if request.user.is_superuser:
            return redirect('user_detail_expediente', user_id=user.id)
        else :
            return redirect('expedientes')
    
@login_required
def updateincidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    user = get_object_or_404(User, pk=incidencia.operario.id)
    if request.method == "GET":
        return render (request, 'blogapp/incidencias/updateincidencia.html', {"user":user, "incidencia":incidencia})
    if request.method == "POST":
        fechaIncidencia = request.POST.get("fechaIncidencia")
        fechaReporte = request.POST.get("fechaReporte")
        referenciaArticulo = request.POST.get("referenciaArticulo")
        nombreArticulo = request.POST.get("nombreArticulo")
        numeroPedido = request.POST.get("numeroPedido")
        unidadesTotales = request.POST.get("unidadesTotales")
        unidadesMalMarcadas = request.POST.get("unidadesMalMarcadas")
        costeIncidencia = request.POST.get("costeIncidencia")
        responsableTurno = request.POST.get("responsableTurno")
        maquina = request.POST.get("maquina")
        personasImplicadas = request.POST.get("personasImplicadas")
        personaDetectaError = request.POST.get("personaDetectaError")
        testigos = request.POST.get("testigos")
        observaciones = request.POST.get("observaciones")
        imagen = request.FILES.get("imagen")
        
        incidencia.fecha_incidencia = fechaIncidencia
        incidencia.fecha_reporte = fechaReporte
        incidencia.referencia_articulo = referenciaArticulo
        incidencia.nombre_articulo = nombreArticulo
        incidencia.numero_pedido = numeroPedido
        incidencia.unidades_totales_pedido = unidadesTotales
        incidencia.unidades_mal_marcadas_revisadas = unidadesMalMarcadas
        incidencia.coste_incidencia = costeIncidencia
        incidencia.responsable_turno = responsableTurno
        incidencia.tecnica_marcado = maquina
        incidencia.personas_implicadas = personasImplicadas
        incidencia.persona_quien_detecta_error = personaDetectaError
        incidencia.testigos = testigos
        incidencia.observaciones = observaciones
        if imagen:
            incidencia.imagen = imagen
        
        incidencia.save()
        
        
        return redirect('user_detail_expediente', user_id=user.id)
    
    
@login_required
def view_parte(request, parte_id):
    parte = get_object_or_404(Parte, pk=parte_id)
    user = get_object_or_404(User, pk=parte.operario.id)
    return render(request, 'blogapp/incidencias/viewParte.html',{"parte":parte, "user":user})

@login_required
def view_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id)
    user = get_object_or_404(User, pk=incidencia.operario.id)
    return render(request, 'blogapp/incidencias/viewIncidencia.html',{"incidencia":incidencia, "user":user})
        

@login_required
def mis_eventos(request):
    if request.method == "GET":
        eventos_filtro = Eventos.objects.filter(creador__exact=request.user.id)
        if len(eventos_filtro) > 0:
            return render(request, "blogapp/misEventos/misEventos.html", {"Eventos" : eventos_filtro})
        else :
            return render(request, "blogapp/misEventos/misEventos.html", {"error" : "No tienes creado ningún evento"})
    else:
        search_term = request.POST.get("search")
        turno = request.POST.get("turno")
        maquina = request.POST.get("maquina")
        eventos = Eventos.objects.filter(creador__exact=request.user.id)
        usuarios_filtro = User.objects.filter(evento__exact=True)
        eventos_filtro = eventos
        
        if search_term != "" and maquina.lower() == "todo":
            eventos_filtro = [] 
            usuarios_filtro = usuarios_filtro.filter(Q(nombre__icontains=search_term) | Q(id__iexact=search_term))
            for user in usuarios_filtro:
                for evento in eventos:
                    if user.id == evento.usuario.id:
                        eventos_filtro.append(evento)
        
        elif search_term != "" and maquina.lower() != "todo":
            eventos_filtro = []
            usuarios_filtro = usuarios_filtro.filter(Q(nombre__icontains=search_term) | Q(id__iexact=search_term) & Q(maquina__iexact=maquina))
            for user in usuarios_filtro:
                for evento in eventos:
                    if user.id == evento.usuario.id:
                        eventos_filtro.append(evento)
        
        elif search_term == "" and maquina.lower() != "todo":
            eventos_filtro = []
            usuarios_filtro = usuarios_filtro.filter(Q(maquina__iexact=maquina))
            for user in usuarios_filtro:
                for evento in eventos:
                    if user.id == evento.usuario.id:
                        eventos_filtro.append(evento)
        
        if turno.lower() != "todo":
            eventos_filtro = [evento for evento in eventos_filtro if evento.turno_actualizado == turno]

    if len(eventos_filtro) > 0:
        return render(request, "blogapp/misEventos/misEventos.html", {"Eventos" : eventos_filtro})
    else:
        return render(request, "blogapp/misEventos/misEventos.html", {"Eventos" : eventos, "error" : "No se ha encontrado a ningún usuario relacionado"})

    
@login_required
def mi_evento_detail(request, evento_id):
    if request.method == "GET":
        evento = get_object_or_404(Eventos, pk=evento_id)
        form = Taskform_eventos(instance=evento)
        user = get_object_or_404(User, pk=evento.usuario.id)
        user.nombre = user.apellido + ',' + user.nombre
        user.evento = True
        user.save()
        return render (request, "blogapp/misEventos/miDetalle_evento.html", {"Eventos": evento, "form": form}) 
    else:
        evento = get_object_or_404(Eventos, pk=evento_id)
        form = Taskform_eventos(request.POST, instance=evento)
        form.save()
        return redirect("mostrar_mis_eventos")
    
@login_required
def mi_evento_delete(request, evento_id):
    # Obtenemos el evento en el que su id coincida con el id del evento que haya clickeado el usuario 
    evento = get_object_or_404(Eventos, pk= evento_id)
    #Obtiene la instancia del usuario asociada al evento
    user = get_object_or_404(User, pk= evento.usuario.id)
    #Inicializa la cantidad de eventos del usuario a 0 para hacer comprobaciones
    cantidad_eventos_usuario = 0
    #Obtiene todos los eventos
    all_events = Eventos.objects.all()
    #Comprueba cuantos eventos tiene el usuario y cada vez que encuentra alguno suma +1 a la cuenta que hemos inicializado a 0 antes
    for event in all_events:
        if event.usuario.id == user.id:
            cantidad_eventos_usuario += 1
    #Despues de comprobar los eventos que tiene el usuario, si el usuario tiene menos que 1 osea no tiene eventos se le cambia el user.evento a False porque no tiene ninguno
    if cantidad_eventos_usuario == 1:
        user.evento = False
    #Guardamos los nuevos daltos para el usuario
    user.nombre = user.apellido + ',' + user.nombre
    user.save()
    #Si el metodo es POST:
    if request.method == "POST":
        #Eliminarmos el evento 
        evento.delete()
        #Redireccionamos a mostrar eventos
        return redirect("mostrar_mis_eventos")
    
@login_required
def permutas_view_maquina(request):
    if request.method == "GET":
        maquinas = Permutado.objects.filter(maquina__exact=True)
        return render(request, 'blogapp/permutas/maquina/permutas_maquina.html', {"maquinas":maquinas})
    if request.method == "POST":
        search_term = request.POST.get("search")
        maquina = request.POST.get("maquina")
        users = User.objects.filter(permutado__exact=True)
        maquinas = Permutado.objects.filter(maquina__exact=True)
        lista_maquinas = [machine for machine in maquinas]
        if search_term != "" and maquina.lower() == "todo":
            lista_maquinas = []
            users = users.filter(nombre__icontains=search_term)
            for user in users:
                for machine in maquinas:
                    if user.id == machine.usuario.id:
                        lista_maquinas.append(machine)
        
        elif search_term != "" and maquina.lower() != "todo":
            lista_maquinas = []
            users = users.filter(Q(nombre__icontains=search_term) & Q(maquina__iexact=maquina))
            for user in users:
                for machine in maquinas:
                    if user.id == machine.usuario.id:
                        lista_maquinas.append(machine)        

        elif search_term == "" and maquina.lower() != "todo":
            lista_maquinas = []
            users = users.filter(maquina__iexact=maquina)
            for user in users:
                for machine in maquinas:
                    if user.id == machine.usuario.id:
                        lista_maquinas.append(machine)
                                
        if len(lista_maquinas) > 0:
            return render(request, 'blogapp/permutas/maquina/permutas_maquina.html', {"maquinas":lista_maquinas})
        else:
            return render(request, 'blogapp/permutas/maquina/permutas_maquina.html', {"maquinas":maquinas, "error":"No se ha encontrado ningún registro"})

@login_required
def permutas_delete_maquina(request, permuta_id):
    permuta = get_object_or_404(Permutado, pk=permuta_id)
    user = get_object_or_404(User, pk=permuta.usuario.id)
    user.nombre = user.apellido + ',' + user.nombre
    user.maquina = permuta.auxiliar
    user.permutado = False
    user.save()
    permuta.delete()
    return redirect('permutasmaquina')
@login_required
def permutas_delete_turno(request, permuta_id):
    permuta = get_object_or_404(Permutado, pk=permuta_id)
    user = get_object_or_404(User, pk=permuta.usuario.id)
    user.nombre = user.apellido + ',' + user.nombre
    user.turno = permuta.auxiliar
    user.permutado = False
    user.save()
    permuta.delete()
    return redirect('permutasturno')
@login_required
def permutas_view_turno(request):
    if request.method == "GET":
        turnos = Permutado.objects.filter(maquina__exact=False)
        return render(request, 'blogapp/permutas/turno/permutas_turno.html', {"maquinas":turnos})
    if request.method == "POST":
        search_term = request.POST.get("search")
        turno = request.POST.get("turno")
        users = User.objects.filter(permutado__exact=True)
        maquinas = Permutado.objects.filter(maquina__exact=False)
        lista_maquinas = [machine for machine in maquinas]
        if search_term != "" and turno.lower() == "todo":
            lista_maquinas = []
            users = users.filter(nombre__icontains=search_term)
            for user in users:
                for machine in maquinas:
                    if user.id == machine.usuario.id:
                        lista_maquinas.append(machine)
        
        elif search_term != "" and turno.lower() != "todo":
            lista_maquinas = []
            users = users.filter(Q(nombre__icontains=search_term) & Q(turno__iexact=turno))
            for user in users:
                for machine in maquinas:
                    if user.id == machine.usuario.id:
                        lista_maquinas.append(machine)        

        elif search_term == "" and turno.lower() != "todo":
            lista_maquinas = []
            users = users.filter(turno__iexact=turno)
            for user in users:
                for machine in maquinas:
                    if user.id == machine.usuario.id:
                        lista_maquinas.append(machine)
                                
        if len(lista_maquinas) > 0:
            return render(request, 'blogapp/permutas/turno/permutas_turno.html', {"maquinas":lista_maquinas})
        else:
            return render(request, 'blogapp/permutas/turno/permutas_turno.html', {"maquinas":maquinas, "error":"No se ha encontrado ningún registro"})


@login_required
def ayuda(request):
    return render(request, 'blogapp/ayuda/ayudaIndex.html')
@login_required
def ayudaTurnos(request):
    return render(request, 'blogapp/ayuda/ayudaTurnos.html')
@login_required
def ayudaEstadisticas(request):
    return render(request, 'blogapp/ayuda/ayudaEstadisticas.html')
@login_required
def ayudaOperarios(request):
    return render(request, 'blogapp/ayuda/ayudaOperarios.html')
@login_required
def ayudaBajas(request): 
    return render(request, 'blogapp/ayuda/ayudaBajas.html')
@login_required
def ayudaExpedientes(request): 
    return render(request, 'blogapp/ayuda/ayudaExpedientes.html')
@login_required
def ayudaCambios(request): 
    return render(request, 'blogapp/ayuda/ayudaCambios.html')
@login_required
def ayudaPermutar(request): 
    return render(request, 'blogapp/ayuda/ayudaPermutar.html')
@login_required
def faltas(request):
    if request.method == "GET":
        operarios = User.objects.all()
        return render(request, 'blogapp/faltas/faltas.html', {"users": operarios} )
    if request.method == "POST":
        search_term = request.POST.get("search")
        turno = request.POST.get("turno")
        maquina = request.POST.get("maquina")
        
        if search_term != "" and maquina.lower() == "todo":
            operarios = User.objects.filter(Q(id__iexact=search_term) | Q(nombre__icontains=search_term))
        
        elif search_term == "" and maquina.lower() == "todo":
            operarios = User.objects.all()
        
        elif search_term != "" and maquina.lower() != "todo":
            operarios = User.objects.filter(Q(id__iexact=search_term) | Q(nombre__icontains=search_term) & Q(maquina__iexact=maquina))
        
        elif search_term == "" and maquina.lower() != "todo":
            operarios = User.objects.filter(maquina__iexact=maquina)
            
        
        if turno.lower() != "todo":
            operarios = [ope for ope in operarios if ope.turno == turno]
        
        return render(request, 'blogapp/faltas/faltas.html', {"users": operarios})