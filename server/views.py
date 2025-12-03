from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncDate, ExtractHour, ExtractWeekDay
from django.utils.dateformat import DateFormat
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth import logout
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
from django.utils import timezone
import csv
from django.views.decorators.http import require_http_methods
import json


# ==========================
# 🌍 VISTAS PÚBLICAS
# ==========================
def index(request):
    """Página principal: muestra reportes verificados y estadísticas."""
    # === MENSAJE DE BIENVENIDA SEGÚN ROL ( SOLO UNA VEZ ) ===
    if request.user.is_authenticated and not request.session.get("bienvenida_mostrada"):

        # Administrador
        if request.user.is_superuser:
            messages.success(request, "Bienvenido Administrador 👑")

        # Moderador
        elif request.user.groups.filter(name="Moderador").exists():
            messages.success(request, "Bienvenido Moderador 🛡️")

        # Usuario normal
        else:
            messages.success(request, "Bienvenido Usuario 👤")

        # Para que el mensaje no se repita cada vez que entra
        request.session["bienvenida_mostrada"] = True

    # === Reportes verificados ===
    reportes = NuevoReporte.objects.filter(estado='aprobado').order_by('-fecha_creacion')

    # === Estadísticas ===
    total_reportes = NuevoReporte.objects.count()
    total_verificados = NuevoReporte.objects.filter(estado='aprobado').count()
    total_pendientes = NuevoReporte.objects.filter(estado='pendiente').count()

    hoy = timezone.now().date()
    total_mes = NuevoReporte.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).count()

    contexto = {
        'reportes': reportes,
        'total_reportes': total_reportes,
        'total_verificados': total_verificados,
        'total_pendientes': total_pendientes,
        'total_mes': total_mes,
    }

    return render(request, 'index.html', contexto)

def detalle(request, id):
    """Vista detallada de un reporte individual."""
    reporte = get_object_or_404(NuevoReporte, id=id)
    fotos = reporte.fotos.all()
    return render(request, 'detalle.html', {'reporte': reporte, 'fotos': fotos})

def contacto(request):
    """Página de contacto."""
    return render(request, 'nosotros/contacto.html')



def ayuda(request):
    """Página de ayuda."""
    return render(request, 'nosotros/ayuda.html')


def acerca(request):
    """Página acerca de."""
    return render(request, 'nosotros/acerca_de.html')

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        user_input = request.POST.get("username")
        password = request.POST.get("password")

        # 📌 Si NO existe como email NI como username
        if not User.objects.filter(email=user_input).exists() and not User.objects.filter(username=user_input).exists():
            messages.error(request, "Este correo o usuario no existe.", extra_tags="username")
            return render(request, "auth/login.html")

        # 📌 Si existe como email → convertirlo a username real
        if User.objects.filter(email=user_input).exists():
            user_input = User.objects.get(email=user_input).username

        # 🔐 Autenticar
        user = authenticate(request, username=user_input, password=password)

        if user:
            login(request, user)
            return redirect("index")

        # 📌 Contraseña incorrecta
        messages.error(request, "La contraseña es incorrecta.", extra_tags="password")
        return render(request, "auth/login.html")

    return render(request, "auth/login.html")

def cerrar_sesion(request):
    """Permite cerrar sesión con método GET (seguro para tu navbar)."""
    logout(request)
    return redirect('login')

# ==========================
# 📝 NUEVO REPORTE
# ==========================
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NuevoReporte, Foto
from .forms import NuevoReporteForm

def nuevo_reporte(request):
    """Vista para crear un nuevo reporte con soporte de anonimato y máximo 5 imágenes."""
    
    if request.method == 'POST':
        form = NuevoReporteForm(request.POST, request.FILES)
        
        # Validar imágenes ANTES de validar el form
        fotografias = request.FILES.getlist('fotografias')
        
        # Validaciones de imágenes
        imagen_errors = []
        if len(fotografias) > 5:
            imagen_errors.append('Máximo 5 fotografías permitidas.')
        
        for foto in fotografias:
            if foto.size > 5 * 1024 * 1024:
                imagen_errors.append(f'{foto.name} excede los 5MB permitidos.')
            if not foto.content_type.startswith('image/'):
                imagen_errors.append(f'{foto.name} no es una imagen válida.')
        
        # Si hay errores de imágenes, mostrarlos
        if imagen_errors:
            for error in imagen_errors:
                messages.error(request, f'⚠️ {error}')
            return render(request, 'nuevo_reporte.html', {
                'form': form,
                'title': 'Nuevo Reporte'
            })
        
        if form.is_valid():
            # Crear el reporte sin guardar todavía
            reporte = form.save(commit=False)
            
            # Si el usuario está autenticado, asociarlo
            if request.user.is_authenticated:
                reporte.usuario = request.user
            
            # Si es anónimo, limpiar datos de contacto
            if reporte.anonimo:
                reporte.nombre_reportante = None
                reporte.email_reportante = None
                reporte.telefono_reportante = None
            
            # Guardar el reporte
            reporte.save()
            
            # Guardar las imágenes (máximo 5)
            for idx, foto in enumerate(fotografias[:5], start=1):
                Foto.objects.create(
                    reporte=reporte,
                    archivo=foto,
                    orden=idx
                )
            
            # Mensaje de éxito
            if reporte.anonimo:
                messages.success(
                    request,
                    f'✅ ¡Reporte enviado como anónimo! Gracias por tu aporte a la comunidad 🐾.'
                )
            else:
                messages.success(
                    request,
                    f'✅ ¡Reporte enviado exitosamente! ID: REP-{reporte.id}. '
                    'Te notificaremos cuando sea revisado.'
                )
            
            return redirect('index')  # Cambia por tu URL de destino
        
        else:
            # Mostrar errores específicos
            error_msg = '⚠️ Por favor corrige los siguientes errores:<br><ul>'
            for field, errors in form.errors.items():
                if field == '__all__':
                    for error in errors:
                        error_msg += f'<li>{error}</li>'
                else:
                    field_label = form.fields[field].label if field in form.fields else field
                    error_msg += f'<li><strong>{field_label}:</strong> {errors[0]}</li>'
            error_msg += '</ul>'
            messages.error(request, error_msg)
    
    else:
        # Prellenar datos si el usuario está autenticado
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'nombre_reportante': request.user.get_full_name() or request.user.username,
                'email_reportante': request.user.email,
            }
        form = NuevoReporteForm(initial=initial_data)
    
    return render(request, 'nuevo_reporte.html', {
        'form': form,
        'title': 'Nuevo Reporte'
    })
# ==========================
# 🗺️ Resgistro  Y Inisiar sesion
# ==========================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import PerfilUsuario


def registro(request):
    """Vista para registro de nuevos usuarios."""
    
    if request.method == 'POST':
        # Datos del formulario
        usuario = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        terms = request.POST.get('terms')

        # ========== VALIDACIONES ==========
        if not all([usuario, email, password, confirm_password]):
            messages.error(request, 'Por favor completa todos los campos obligatorios.')
            return render(request, 'auth/registro.html')

        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'auth/registro.html')

        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'auth/registro.html')

        if not terms:
            messages.error(request, 'Debes aceptar los términos y condiciones.')
            return render(request, 'auth/registro.html')

        # Usuario ya existe
        if User.objects.filter(username=usuario).exists():
            messages.error(request, 'Este nombre de usuario ya está en uso.')
            return render(request, 'auth/registro.html')

        # Correo ya existe
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo electrónico ya está registrado.')
            return render(request, 'auth/registro.html')

        # ========== CREAR USUARIO Y PERFIL ==========
        try:
            nuevo_usuario = User.objects.create_user(
                username=usuario,
                email=email,
                password=password
            )

            # Crear perfil con rol default = "usuario"
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=nuevo_usuario,
                defaults={'rol': 'usuario'}
            )

            # ========== LOGIN AUTOMÁTICO ==========
            login(request, nuevo_usuario)

            # Mensaje de éxito
            messages.success(request, f'¡Bienvenido/a {nuevo_usuario.username}! Tu cuenta ha sido creada exitosamente.')

            # Redirigir al inicio
            return redirect('index')

        except Exception as e:
            messages.error(request, f'Error al crear la cuenta: {str(e)}')
            return render(request, 'auth/registro.html')

    # GET → mostrar formulario
    return render(request, 'auth/registro.html')


from django.http import JsonResponse
from django.contrib.auth.models import User

def check_email(request):
    email = request.GET.get("email")
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({"exists": exists})

# ==========================
# 🗺️ MAPA Y ESTADÍSTICAS
# =========================
def mapa(request):
    """Muestra los reportes aprobados en un mapa interactivo."""

    reportes = NuevoReporte.objects.filter(
        estado='aprobado',
        latitud__isnull=False,
        longitud__isnull=False
    )

    # Si es AJAX, devolver JSON válido
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for r in reportes:
            try:
                data.append({
                    'id': r.id,
                    'titulo': r.titulo,
                    'descripcion': r.descripcion,
                    
                    # Datos principales
                    'tipo_animal': r.tipo_animal,
                    'cantidad_perros': r.cantidad_perros,
                    'gravedad': r.gravedad,
                    'hora': r.hora.strftime('%H:%M') if r.hora else '',
                    
                    'gravedad': r.gravedad,
                    'sector': r.get_sector_display() if r.sector else 'Sin sector',
                    'comuna': r.get_sector_display() if r.sector else 'Sin sector',  # 👈 Agregado
                    'fecha': r.fecha.strftime('%d/%m/%Y'),  # 👈 Formato más legible
                    'lat': float(r.latitud),
                    'lon': float(r.longitud),
                    'direccion': r.direccion,  # 👈 Agregado
                    'foto': r.fotos.first().archivo.url if r.fotos.exists() else '',
                })
            except Exception as e:
                print(f"Error en reporte {r.id}: {e}")
                continue  # 👈 Continuar con el siguiente si hay error

        print(f"✅ Enviando {len(data)} reportes al frontend")  # 👈 Debug
        return JsonResponse(data, safe=False)

    # Si es carga normal de página
    total_reportes = reportes.count()
    return render(request, 'mapa.html', {'total_reportes': total_reportes})


def estadisticas(request):
    """Genera estadísticas completas de reportes."""
    
    # ============================================
    # ESTADÍSTICAS GENERALES (HERO)
    # ============================================
    total_reportes = NuevoReporte.objects.count()
    verificados = NuevoReporte.objects.filter(estado='aprobado').count()
    ataques_graves = NuevoReporte.objects.filter(gravedad='grave').count()
    sectores_afectados = NuevoReporte.objects.values('sector').distinct().count()

    # ============================================
    # REPORTES POR MES (Gráfico de Barras)
    # ============================================
    mes_data = (
        NuevoReporte.objects.filter(estado='aprobado')
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    
    meses = [DateFormat(m['mes']).format('M') for m in mes_data] if mes_data else []
    totales_mes = [m['total'] for m in mes_data] if mes_data else []

    # ============================================
    # DISTRIBUCIÓN POR GRAVEDAD (Gráfico de Dona)
    # ============================================
    gravedad_data = (
        NuevoReporte.objects.filter(estado='aprobado')
        .values('gravedad')
        .annotate(total=Count('id'))
    )
    
    graves = next((g['total'] for g in gravedad_data if g['gravedad'] == 'grave'), 0)
    moderados = next((g['total'] for g in gravedad_data if g['gravedad'] == 'moderado'), 0)
    leves = next((g['total'] for g in gravedad_data if g['gravedad'] == 'leve'), 0)

    # ============================================
    # TOP 10 SECTORES MÁS AFECTADOS (Ranking)
    # ============================================
    top_sectores = (
        NuevoReporte.objects.filter(estado='aprobado')
        .exclude(sector__isnull=True)
        .values('sector')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )
    
    # Obtener nombres legibles de sectores
    SECTOR_NOMBRES = dict(NuevoReporte.SECTOR_CHOICES)
    sectores_ranking = []
    for s in top_sectores:
        sectores_ranking.append({
            'sector': SECTOR_NOMBRES.get(s['sector'], s['sector']),
            'total': s['total']
        })
    
    # Calcular el máximo para porcentajes
    max_sector = sectores_ranking[0]['total'] if sectores_ranking else 1

    # ============================================
    # TENDENCIA TEMPORAL (Gráfico de Línea)
    # ============================================
    # Últimos 12 meses
    hace_12_meses = datetime.now() - timedelta(days=365)
    
    tendencia_2024 = (
        NuevoReporte.objects.filter(
            estado='aprobado',
            fecha__gte=hace_12_meses
        )
        .annotate(mes=TruncMonth('fecha'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    
    meses_tendencia = [DateFormat(m['mes']).format('M') for m in tendencia_2024]
    totales_tendencia = [m['total'] for m in tendencia_2024]

    # ============================================
    # INCIDENTES POR HORA DEL DÍA
    # ============================================
    horas_data = (
        NuevoReporte.objects.filter(estado='aprobado')
        .exclude(hora__isnull=True)
        .annotate(hora_del_dia=ExtractHour('hora'))
        .values('hora_del_dia')
        .annotate(total=Count('id'))
        .order_by('hora_del_dia')
    )
    
    # Agrupar por rangos horarios
    rangos_horas = {
        '0-6h': 0, '6-9h': 0, '9-12h': 0, '12-15h': 0,
        '15-18h': 0, '18-21h': 0, '21-24h': 0
    }
    
    for h in horas_data:
        hora = h['hora_del_dia']
        if 0 <= hora < 6:
            rangos_horas['0-6h'] += h['total']
        elif 6 <= hora < 9:
            rangos_horas['6-9h'] += h['total']
        elif 9 <= hora < 12:
            rangos_horas['9-12h'] += h['total']
        elif 12 <= hora < 15:
            rangos_horas['12-15h'] += h['total']
        elif 15 <= hora < 18:
            rangos_horas['15-18h'] += h['total']
        elif 18 <= hora < 21:
            rangos_horas['18-21h'] += h['total']
        else:
            rangos_horas['21-24h'] += h['total']
    
    etiquetas_horas = list(rangos_horas.keys())
    totales_horas = list(rangos_horas.values())

    # ============================================
    # INCIDENTES POR DÍA DE LA SEMANA
    # ============================================
    dias_data = (
        NuevoReporte.objects.filter(estado='aprobado')
        .annotate(dia_semana=ExtractWeekDay('fecha'))
        .values('dia_semana')
        .annotate(total=Count('id'))
        .order_by('dia_semana')
    )
    
    dias_nombres = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
    totales_dias = [0] * 7
    
    for d in dias_data:
        totales_dias[d['dia_semana'] - 1] = d['total']
    
    # Reorganizar para que empiece en Lunes
    totales_dias_ordenados = totales_dias[1:] + [totales_dias[0]]
    dias_ordenados = dias_nombres[1:] + [dias_nombres[0]]

    # ============================================
    # MÉTRICAS DE CALIDAD
    # ============================================
    if total_reportes > 0:
        tasa_aprobacion = round((verificados / total_reportes) * 100)
    else:
        tasa_aprobacion = 0
    
    reportes_con_foto = NuevoReporte.objects.filter(
        estado='aprobado',
        fotos__isnull=False
    ).distinct().count()
    
    if verificados > 0:
        porcentaje_con_foto = round((reportes_con_foto / verificados) * 100)
    else:
        porcentaje_con_foto = 0

    # ============================================
    # CONTEXT PARA EL TEMPLATE
    # ============================================
    context = {
        # Hero Stats
        'total_reportes': total_reportes,
        'verificados': verificados,
        'ataques_graves': ataques_graves,
        'sectores_afectados': sectores_afectados,
        
        # Gráfico de Barras (Mes)
        'meses': meses,
        'totales_mes': totales_mes,
        
        # Gráfico de Dona (Gravedad)
        'graves': graves,
        'moderados': moderados,
        'leves': leves,
        
        # Ranking de Sectores
        'sectores_ranking': sectores_ranking,
        'max_sector': max_sector,
        
        # Tendencia Temporal
        'meses_tendencia': meses_tendencia,
        'totales_tendencia': totales_tendencia,
        
        # Por Hora
        'etiquetas_horas': etiquetas_horas,
        'totales_horas': totales_horas,
        
        # Por Día
        'dias_ordenados': dias_ordenados,
        'totales_dias': totales_dias_ordenados,
        
        # Métricas
        'tasa_aprobacion': tasa_aprobacion,
        'porcentaje_con_foto': porcentaje_con_foto,
    }
    
    return render(request, 'estadisticas.html', context)
# ==========================
# 🧩 PANEL MODERADOR
# ==========================

def es_moderador(user):
    return user.is_authenticated and (
        user.perfil.rol == 'moderador' or user.perfil.rol == 'admin'
    )


# ============================================
# 📋 Panel de Moderación (con filtros de estado, gravedad y animal)
# ============================================
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ============================================
# 📋 Panel de Moderación (con filtros completos)
# ============================================
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
@user_passes_test(es_moderador)
def panel_moderador(request):
    # Obtener parámetros de filtros
    estado_filtro = request.GET.get('estado', None)
    gravedad_filtro = request.GET.get('gravedad', None)
    animal_filtro = request.GET.get('animal', None)
    anonimo_filtro = request.GET.get('anonimo', None)  # NUEVO

    # Query base ordenado por más reciente
    reportes = NuevoReporte.objects.all().order_by('-fecha', '-id')

    # Aplicar filtro de ESTADO
    if estado_filtro and estado_filtro != 'todos':
        reportes = reportes.filter(estado=estado_filtro)

    # Aplicar filtro de GRAVEDAD
    if gravedad_filtro and gravedad_filtro != 'all':
        reportes = reportes.filter(gravedad=gravedad_filtro)

    # Aplicar filtro de ANIMAL
    if animal_filtro and animal_filtro != 'all':
        reportes = reportes.filter(tipo_animal=animal_filtro)

    # Aplicar filtro de ANÓNIMO
    if anonimo_filtro and anonimo_filtro != 'all':
        if anonimo_filtro == 'true':
            reportes = reportes.filter(anonimo=True)
        elif anonimo_filtro == 'false':
            reportes = reportes.filter(anonimo=False)

    # Configurar paginación
    reportes_por_pagina = 5
    paginator = Paginator(reportes, reportes_por_pagina)
    
    page = request.GET.get('page', 1)
    
    try:
        reportes_paginados = paginator.page(page)
    except PageNotAnInteger:
        reportes_paginados = paginator.page(1)
    except EmptyPage:
        reportes_paginados = paginator.page(paginator.num_pages)

    context = {
        'reportes': reportes_paginados,
        'pendientes': NuevoReporte.objects.filter(estado='pendiente').count(),
        'aprobados': NuevoReporte.objects.filter(estado='aprobado').count(),
        'rechazados': NuevoReporte.objects.filter(estado='rechazado').count(),
        'todos': NuevoReporte.objects.count(),
        'total_filtrados': paginator.count,  # Total con filtros aplicados
    }
    return render(request, 'moderador/panel_moderador.html', context)

# ============================================
# ✅ Aprobar Reporte
# ============================================
@login_required
@user_passes_test(es_moderador)
def aprobar_reporte(request, id):
    reporte = get_object_or_404(NuevoReporte, id=id)
    reporte.estado = 'aprobado'
    reporte.moderador = request.user
    reporte.fecha_moderacion = timezone.now()
    reporte.comentario_moderacion = 'Reporte aprobado y publicado.'
    reporte.save()

    ModeracionLog.objects.create(
        reporte=reporte,
        moderador=request.user,
        accion='verificado',
        motivo='Aprobado por moderador'
    )

    return JsonResponse({'status': 'ok', 'mensaje': 'Reporte aprobado correctamente.'})

# ============================================
# ❌ Rechazar Reporte
# ============================================
@login_required
@user_passes_test(es_moderador)
def rechazar_reporte(request, id):
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '').strip()
        if not motivo:
            return JsonResponse({'status': 'error', 'mensaje': 'Debes escribir un motivo de rechazo.'})
        
        reporte = get_object_or_404(NuevoReporte, id=id)
        reporte.estado = 'rechazado'
        reporte.moderador = request.user
        reporte.fecha_moderacion = timezone.now()
        reporte.comentario_moderacion = motivo
        reporte.save()

        ModeracionLog.objects.create(
            reporte=reporte,
            moderador=request.user,
            accion='rechazado',
            motivo=motivo
        )

        return JsonResponse({'status': 'ok', 'mensaje': 'Reporte rechazado correctamente.'})
    
    return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'})

# ============================================
# 🔍 Ver Detalles
# ============================================
@login_required
@user_passes_test(es_moderador)
def detalles_reporte(request, id):
    reporte = get_object_or_404(NuevoReporte, id=id)

    data = {
        # TITULO Y FECHA
        'titulo': reporte.titulo,
        'fecha': reporte.fecha.strftime("%d/%m/%Y"),
        'hora': reporte.hora.strftime("%H:%M") if reporte.hora else '',

        # INCIDENTE
        'tipo_animal': reporte.get_tipo_animal_display(),
        'cantidad_perros': reporte.cantidad_perros or 'Sin dato',
        'gravedad': reporte.get_gravedad_display(),
        'direccion': reporte.direccion or 'No indicada',

        # DATOS DEL REPORTANTE
        'nombre_reportante': reporte.nombre_visible() or '',
        'email_reportante': reporte.email_reportante or '',
        'telefono_reportante': reporte.telefono_reportante or '',
        'anonimo': reporte.anonimo,
        'usuario': reporte.usuario.username if reporte.usuario else '',

        # UBICACIÓN
        'sector': reporte.get_sector_display(),
        'latitud': float(reporte.latitud) if reporte.latitud else None,
        'longitud': float(reporte.longitud) if reporte.longitud else None,

        # DESCRIPCIÓN
        'descripcion': reporte.descripcion or '',
    }

    return JsonResponse(data)


# ============================================
# 📤 Exportar CSV
# ============================================
@login_required
@user_passes_test(es_moderador)
def exportar_csv(request):
    reportes = NuevoReporte.objects.all().select_related('usuario', 'moderador')

    fecha_actual = timezone.now().strftime("%Y-%m-%d_%H-%M")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="reportes_{fecha_actual}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Título', 'Descripción', 'Estado', 'Gravedad', 'Tipo Animal',
        'Cantidad Perros', 'Dirección', 'Latitud', 'Longitud',
        'Fecha', 'Hora', 'Usuario', 'Email', 'Teléfono',
        'Moderador', 'Comentario Moderación'
    ])

    for r in reportes:
        writer.writerow([
            r.id, r.titulo, r.descripcion, r.estado, r.gravedad,
            r.tipo_animal, r.cantidad_perros, r.direccion, r.latitud, r.longitud,
            r.fecha.strftime("%d-%m-%Y") if r.fecha else '',
            r.hora.strftime("%H:%M") if r.hora else '',
            r.usuario.username if r.usuario else 'Anónimo',
            r.email_reportante, r.telefono_reportante,
            r.moderador.username if r.moderador else '',
            r.comentario_moderacion or ''
        ])

    return response

# ============================================
# views.py - Vistas de Gestión de Usuarios
# ============================================
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json

from .models import PerfilUsuario
# ============================================================
# 🔐 HELPER PARA ROLES
# ============================================================

def es_admin(user):
    if user.is_superuser or user.is_staff:
        return True
    return hasattr(user, "perfil") and user.perfil.rol == "admin"


def es_mod_o_admin(user):
    if user.is_superuser or user.is_staff:
        return True
    return hasattr(user, "perfil") and user.perfil.rol in ["moderador", "admin"]



# ============================================================
# 👥 LISTA DE USUARIOS
# ============================================================

@login_required
def usuarios_list(request):
    if not es_mod_o_admin(request.user):
        return redirect("index")

    usuarios = User.objects.select_related("perfil").all()

    admins_count = usuarios.filter(perfil__rol="admin").count()
    moderadores_count = usuarios.filter(perfil__rol="moderador").count()
    usuarios_count = usuarios.filter(perfil__rol="usuario").count()

    return render(request, "admin/usuarios.html", {
        "usuarios": usuarios,
        "admins_count": admins_count,
        "moderadores_count": moderadores_count,
        "usuarios_count": usuarios_count,
    })


# ============================================================
# ➕ CREAR USUARIO
# ============================================================

@login_required
@require_http_methods(["POST"])
def crear_usuario(request):
    if not es_admin(request.user):
        return JsonResponse({"success": False, "message": "No autorizado"})

    try:
        data = json.loads(request.body)

        name = data.get("name", "").strip()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        role = data.get("role", "").strip()

        # Validar campos vacíos
        if "" in [name, username, email, password, role]:
            return JsonResponse({"success": False, "message": "Todos los campos son obligatorios"})

        # Validar rol
        if role not in ["usuario", "moderador", "admin"]:
            return JsonResponse({"success": False, "message": "Rol inválido"})

        # Validar username único (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            return JsonResponse({
                "success": False, 
                "message": "El nombre de usuario ya está en uso"
            })

        # Validar email único (case-insensitive)
        if User.objects.filter(email__iexact=email).exists():
            return JsonResponse({
                "success": False, 
                "message": "El email ya está registrado"
            })

        # Crear usuario
        user = User.objects.create_user(username=username, email=email, password=password)

        # Guardar nombre
        partes = name.split(" ", 1)
        user.first_name = partes[0]
        user.last_name = partes[1] if len(partes) > 1 else ""
        user.save()

        # Crear o actualizar perfil
        perfil = user.perfil
        perfil.rol = role
        perfil.save()

        return JsonResponse({
            "success": True, 
            "message": f"Usuario {username} creado correctamente"
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"})


# ============================================================
# 📄 OBTENER DATA DE USUARIO PARA MODAL EDITAR
# ============================================================

@login_required
def usuario_data(request, user_id):
    if not es_mod_o_admin(request.user):
        return JsonResponse({"success": False, "message": "No autorizado"})

    usuario = get_object_or_404(User.objects.select_related("perfil"), id=user_id)

    return JsonResponse({
        "id": usuario.id,
        "name": usuario.get_full_name() or usuario.username,
        "email": usuario.email,
        "role": usuario.perfil.rol,
        "date_joined": usuario.date_joined.strftime("%d/%m/%Y"),
        "reportes_count": usuario.reportes.count(),
        "reportes_moderados_count": usuario.reportes_moderados.count(),
    })


# ============================================================
# ✏ EDITAR USUARIO
# ============================================================

@login_required
@require_http_methods(["GET", "POST"])
def editar_usuario(request, user_id):

    if not es_admin(request.user):
        return JsonResponse({"success": False, "message": "No autorizado"})

    usuario = get_object_or_404(User.objects.select_related("perfil"), id=user_id)

    # Si es GET → enviar datos al modal
    if request.method == "GET":
        return JsonResponse({
            "id": usuario.id,
            "name": usuario.get_full_name() or usuario.username,
            "email": usuario.email,
            "role": usuario.perfil.rol,
        })

    # Si es POST → actualizar
    try:
        data = json.loads(request.body)

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        role = data.get("role", "").strip()

        # Validar rol
        if role not in ["usuario", "moderador", "admin"]:
            return JsonResponse({"success": False, "message": "Rol inválido"})

        # Validar email único (excluyendo el usuario actual, case-insensitive)
        if User.objects.filter(email__iexact=email).exclude(id=usuario.id).exists():
            return JsonResponse({
                "success": False, 
                "message": "El email ya está en uso por otro usuario"
            })

        # Actualizar nombre
        partes = name.split(" ", 1)
        usuario.first_name = partes[0]
        usuario.last_name = partes[1] if len(partes) > 1 else ""

        usuario.email = email
        usuario.save()

        # Actualizar rol
        usuario.perfil.rol = role
        usuario.perfil.save()

        return JsonResponse({
            "success": True, 
            "message": "Usuario actualizado correctamente"
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error: {str(e)}"})


# ============================================================
# 🗑 ELIMINAR USUARIO
# ============================================================

@login_required
@require_http_methods(["DELETE"])
def eliminar_usuario(request, user_id):

    if not es_admin(request.user):
        return JsonResponse({"success": False, "message": "No autorizado"})

    usuario = get_object_or_404(User.objects.select_related("perfil"), id=user_id)

    # No eliminarse a sí mismo
    if usuario == request.user:
        return JsonResponse({
            "success": False, 
            "message": "No puedes eliminarte a ti mismo"
        })

    # No eliminar último administrador
    if usuario.perfil.rol == "admin":
        if User.objects.filter(perfil__rol="admin").count() <= 1:
            return JsonResponse({
                "success": False, 
                "message": "No puedes eliminar al último administrador"
            })

    username = usuario.username
    usuario.delete()

    return JsonResponse({
        "success": True, 
        "message": f"Usuario {username} eliminado correctamente"
    })