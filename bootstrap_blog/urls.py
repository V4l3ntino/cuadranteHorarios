"""
URL configuration for bootstrap_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

from blogapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signin/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.signout, name='logout'),
    path('eventos/', views.evento_view, name='mostrar_eventos'),
    path('mis/eventos/', views.mis_eventos, name='mostrar_mis_eventos'),
    path('evento<int:evento_id>/', views.evento_detail, name='detalle_evento'),
    path('mi/evento<int:evento_id>/', views.mi_evento_detail, name='midetalle_evento'),
    path('evento<int:evento_id>/eliminar', views.evento_delete, name='eliminar_evento'),
    path('mi/evento<int:evento_id>/eliminar', views.mi_evento_delete, name='mi_eliminar_evento'),
    path('tareas/', views.tareas, name='tareas'),
    path('tareas_completadas/', views.tareas_completadas, name='tareas_completadas'),
    path('tareas/crear/', views.crear_tareas, name='crear_tareas'),
    path('tareas/<int:tarea_id>/', views.detalle_tarea, name='detalle_tarea'),
    path('tareas/<int:tarea_id>/completada', views.completar_tarea, name='completar_tarea'),
    path('tareas/<int:tarea_id>/eliminar', views.eliminar_tarea, name='eliminar_tarea'),
    
    path('faltasInjustificadas/', views.faltas, name='faltas'),

    path('operarios/<int:user_id>/', views.user_detail, name='user_detail'),
    path('userapp/<int:user_id>/', views.appdetalle, name='appdetalle'),
    path('appdelete/<int:user_id>/', views.appdelete, name='appdelete'),
    path('appcreate/', views.appcreate, name='appcreate'),
    path('operarios/update/', views.update, name='update'),
    path('operarios/sugerencia/', views.sugerencias, name='sugerencia'),
    path('operarios/sugerenciapost/', views.añadir_sugerencia, name='añadir_sugerencia'),
    path('operarios/todo/', views.todo, name='operarios_todo'),
    path('operarios/autos/', views.autos, name='operarios_autos'),
    path('operarios/laser/', views.laser, name='operarios_laser'),
    path('operarios/tampo/', views.tampo, name='operarios_tampo'),
    path('operarios/pulpos/', views.pulpos, name='operarios_pulpos'),
    path('operarios/digital/', views.digital, name='operarios_digital'),
    path('operarios/bordado/', views.bordado, name='operarios_bordado'),
    path('operarios/termo/', views.termo, name='operarios_termo'),
    path('operarios/planchas/', views.planchas, name='operarios_planchas'),
    path('operarios/hornos/', views.horno, name='operarios_hornos'),
    path('operarios/sublimacion/', views.sublimacion, name='operarios_sublimacion'),
    path('operarios/envasado/', views.envasado, name='operarios_envasado'),
    
    path('turnos/turnotodo/', views.turnotodo, name='turnotodo'),
    path('turnos/turnoautos/', views.turnoautos, name='turnoautos'),
    path('turnos/turnolaser/', views.turnolaser, name='turnolaser'),
    path('turnos/turnotampo/', views.turnotampo, name='turnotampo'),
    path('turnos/turnopulpos/', views.turnopulpos, name='turnopulpos'),
    path('turnos/turnodigital/', views.turnodigital, name='turnodigital'),
    path('turnos/turnobordado/', views.turnobordado, name='turnobordado'),
    path('turnos/turnotermo/', views.turnotermo, name='turnotermo'),
    path('turnos/turnoplanchas/', views.turnoplanchas, name='turnoplanchas'),
    path('turnos/turnosublimacion/', views.turnosublimacion, name='turnosublimacion'),
    path('turnos/turnoenvasado/', views.turnoenvasado, name='turnoenvasado'),
    path('turnos/turnohorno/', views.turnohorno, name='turnohorno'),
    path('permutar/', views.permutado, name='permutar'),
    
    path('estadisticas/auto/', views.estadisticas_auto, name='estadisticas_auto'),
    path('estadisticas/laser/', views.estadisticas_laser, name='estadisticas_laser'),
    path('estadisticas/tampo/', views.estadisticas_tampo, name='estadisticas_tampo'),
    path('estadisticas/pulpos/', views.estadisticas_pulpos, name='estadisticas_pulpos'),
    path('estadisticas/digital/', views.estadisticas_digital, name='estadisticas_digital'),
    path('estadisticas/bordado/', views.estadisticas_bordado, name='estadisticas_bordado'),
    path('estadisticas/termo/', views.estadisticas_termo, name='estadisticas_termo'),
    path('estadisticas/planchas/', views.estadisticas_planchas, name='estadisticas_planchas'),
    path('estadisticas/hornos/', views.estadisticas_horno, name='estadisticas_hornos'),
    path('estadisticas/sublimacion/', views.estadisticas_sublimacion, name='estadisticas_sublimacion'),
    path('estadisticas/envasado/', views.estadisticas_envasado, name='estadisticas_envasado'),
    path('estadistica/operario/<int:user_id>', views.estadisticas_user, name='estadisticas_user'),

    path('registros/', views.tracking, name='registros'),
    path('operarios/borrados', views.operarios_borrados, name='operariosborrados'),
    path('expediente/', views.expediente, name='expedientes'),
    path('expediente/<int:user_id>', views.expediente_detail, name='user_detail_expediente'),
    path('expediente/<int:user_id>/crearparte', views.crearparte, name='crearparte'),
    path('expediente/<int:user_id>/crearincidencia', views.crearincidencia, name='crearincidencia'),
    path('expediente/<int:parte_id>/borrarparte', views.deleteparte, name='deleteparte'),
    path('expediente/<int:incidencia_id>/deleteincidencia', views.deleteincidencia, name='deleteincidencia'),
    path('expediente/<int:incidencia_id>/updateincidencia', views.updateincidencia, name='updateincidencia'),
    path('expediente/<int:parte_id>/updateparte', views.updateparte, name='updateparte'),
    path('expediente/<int:parte_id>/visualizarParte', views.view_parte, name='viewParte'),
    path('expediente/<int:incidencia_id>/visualizarIncidencia', views.view_incidencia, name='viewIncidencia'),
    path('expediente/historial', views.mis_expedientes, name='misExpedientes'),
    
    path('expediente/block_view', views.block_view, name='blockview'),
    path('expediente/historial_expedientes', views.block_view_logged, name='historial'),
    path('actualizar', views.valores_update, name='actualizar'),
    path('resetear', views.valores_reset, name='resetear'),
    path('actualizar_colores', views.colores_update, name='coloresupdate'),
    path('permutas_maquina', views.permutas_view_maquina, name='permutasmaquina'),
    path('permutas_turno', views.permutas_view_turno, name='permutasturno'),
    path('pemutas_delete_maquina/<int:permuta_id>', views.permutas_delete_maquina, name='permutamaquinadelete'),
    path('pemutas_delete_turno/<int:permuta_id>', views.permutas_delete_turno, name='permutaturnodelete'),
    
    path('ayuda/', views.ayuda, name='ayuda'),
    path('ayuda/Turnos', views.ayudaTurnos, name='ayudaTurnos'),
    path('ayuda/Estadisticas', views.ayudaEstadisticas, name='ayudaEstadisticas'),
    path('ayuda/Operarios', views.ayudaOperarios, name='ayudaOperarios'),
    path('ayuda/Bajas', views.ayudaBajas, name='ayudaBajas'),
    path('ayuda/Expedientes', views.ayudaExpedientes, name='ayudaExpedientes'),
    path('ayuda/Cambios', views.ayudaCambios, name='ayudaCambios'),
    path('ayuda/Permutar', views.ayudaPermutar, name='ayudaPermutar')
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    