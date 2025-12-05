from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import PerfilUsuario, NuevoReporte, Foto, ModeracionLog


class FotoInline(admin.TabularInline):
    model = Foto
    extra = 1
    max_num = 5
    fields = ('miniatura', 'archivo', 'orden', 'contiene_contenido_grafico', 'es_censurada', 'estado_moderacion')
    readonly_fields = ('miniatura', 'subida_en')
    
    def miniatura(self, obj):
        if obj.archivo:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 120px; border-radius: 4px;" />',
                obj.archivo.url
            )
        return "Sin imagen"
    miniatura.short_description = "Vista previa"


class ModeracionLogInline(admin.TabularInline):
    model = ModeracionLog
    extra = 0
    can_delete = False
    fields = ('fecha', 'moderador', 'accion', 'motivo')
    readonly_fields = ('fecha', 'moderador', 'accion', 'motivo')
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'email_usuario', 'fecha_registro', 'reportes_totales')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('fecha_registro', 'reportes_totales')
    
    fieldsets = (
        ('Información de Usuario', {
            'fields': ('user', 'rol')
        }),
        ('Estadísticas', {
            'fields': ('fecha_registro', 'reportes_totales'),
            'classes': ('collapse',)
        }),
    )
    
    def email_usuario(self, obj):
        return obj.user.email
    email_usuario.short_description = "Email"
    
    def fecha_registro(self, obj):
        return obj.user.date_joined.strftime('%d/%m/%Y %H:%M')
    fecha_registro.short_description = "Fecha de registro"
    
    def reportes_totales(self, obj):
        count = obj.user.reportes.count()
        return format_html(
            '<strong style="color: #417690;">{}</strong> reportes',
            count
        )
    reportes_totales.short_description = "Reportes realizados"



@admin.register(NuevoReporte)
class NuevoReporteAdmin(admin.ModelAdmin):
    list_display = (
        'titulo_corto',
        'estado_badge',
        'gravedad_badge',
        'sector',
        'fecha',
        'nombre_reportante_display',
        'fotos_count',
        'fecha_creacion_corta'
    )
    
    list_filter = (
        'estado',
        'gravedad',
        'sector',
        'tipo_animal',
        'anonimo',
        'fecha_creacion',
        'fecha'
    )
    
    search_fields = (
        'titulo',
        'descripcion',
        'direccion',
        'nombre_reportante',
        'email_reportante'
    )
    
    readonly_fields = (
        'fecha_creacion',
        'fecha_actualizacion',
        'usuario',
        'mapa_ubicacion',
        'info_reportante_completa'
    )
    
    date_hierarchy = 'fecha_creacion'
    
    ordering = ('-fecha_creacion',)
    
    inlines = [FotoInline, ModeracionLogInline]
    
    fieldsets = (
        ('📋 Información del Reporte', {
            'fields': ('titulo', 'fecha', 'hora', 'estado')
        }),
        ('🐕 Detalles del Incidente', {
            'fields': ('tipo_animal', 'cantidad_perros', 'gravedad', 'descripcion')
        }),
        ('📍 Ubicación', {
            'fields': ('direccion', 'sector', 'latitud', 'longitud', 'mapa_ubicacion'),
            'classes': ('wide',)
        }),
        ('👤 Información del Reportante', {
            'fields': ('anonimo', 'usuario', 'info_reportante_completa'),
            'classes': ('collapse',)
        }),
        ('✅ Moderación', {
            'fields': ('moderador', 'fecha_moderacion', 'comentario_moderacion'),
            'classes': ('wide',)
        }),
        ('🕐 Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['aprobar_reportes', 'rechazar_reportes', 'marcar_pendientes']
    
    def titulo_corto(self, obj):
        return obj.titulo[:50] + '...' if len(obj.titulo) > 50 else obj.titulo
    titulo_corto.short_description = "Título"
    
    def estado_badge(self, obj):
        colores = {
            'pendiente': '#ffc107',
            'aprobado': '#28a745',
            'rechazado': '#dc3545'
        }
        iconos = {
            'pendiente': '⏳',
            'aprobado': '✅',
            'rechazado': '❌'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            colores.get(obj.estado, '#6c757d'),
            iconos.get(obj.estado, ''),
            obj.get_estado_display()
        )
    estado_badge.short_description = "Estado"
    
    def gravedad_badge(self, obj):
        colores = {
            'leve': '#17a2b8',
            'moderado': '#fd7e14',
            'grave': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 8px; font-size: 10px;">{}</span>',
            colores.get(obj.gravedad, '#6c757d'),
            obj.get_gravedad_display()
        )
    gravedad_badge.short_description = "Gravedad"
    
    def nombre_reportante_display(self, obj):
        if obj.anonimo:
            return format_html('<em style="color: #999;">Anónimo</em>')
        return obj.nombre_reportante or format_html('<em style="color: #999;">No especificado</em>')
    nombre_reportante_display.short_description = "Reportante"
    
    def fotos_count(self, obj):
        count = obj.fotos.count()
        if count > 0:
            return format_html(
                '<span style="color: #28a745;">📷 {}</span>',
                count
            )
        return format_html('<span style="color: #999;">Sin fotos</span>')
    fotos_count.short_description = "Fotos"
    
    def fecha_creacion_corta(self, obj):
        return obj.fecha_creacion.strftime('%d/%m/%Y %H:%M')
    fecha_creacion_corta.short_description = "Creado"
    
    def mapa_ubicacion(self, obj):
        if obj.latitud and obj.longitud:
            return format_html(
                '<div style="margin: 10px 0;">'
                '<p><strong>Coordenadas:</strong> {}, {}</p>'
                '<a href="https://www.google.com/maps?q={},{}" target="_blank" '
                'style="display: inline-block; padding: 8px 16px; background-color: #4285f4; '
                'color: white; text-decoration: none; border-radius: 4px; margin-top: 8px;">'
                '🗺️ Ver en Google Maps</a>'
                '</div>',
                obj.latitud,
                obj.longitud,
                obj.latitud,
                obj.longitud
            )
        return "No disponible"
    mapa_ubicacion.short_description = "Mapa"
    
    def info_reportante_completa(self, obj):
        if obj.anonimo:
            return format_html('<p style="color: #999; font-style: italic;">Reporte anónimo - información no disponible</p>')
        
        html = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">'
        if obj.nombre_reportante:
            html += f'<p><strong>Nombre:</strong> {obj.nombre_reportante}</p>'
        if obj.email_reportante:
            html += f'<p><strong>Email:</strong> <a href="mailto:{obj.email_reportante}">{obj.email_reportante}</a></p>'
        if obj.telefono_reportante:
            html += f'<p><strong>Teléfono:</strong> {obj.telefono_reportante}</p>'
        if obj.usuario:
            url = reverse('admin:auth_user_change', args=[obj.usuario.id])
            html += f'<p><strong>Usuario registrado:</strong> <a href="{url}">{obj.usuario.username}</a></p>'
        html += '</div>'
        return mark_safe(html)
    info_reportante_completa.short_description = "Datos del reportante"
    
    def aprobar_reportes(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            estado='aprobado',
            moderador=request.user,
            fecha_moderacion=timezone.now()
        )
        self.message_user(request, f'{updated} reporte(s) aprobado(s) exitosamente.')
    aprobar_reportes.short_description = "✅ Aprobar reportes seleccionados"
    
    def rechazar_reportes(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            estado='rechazado',
            moderador=request.user,
            fecha_moderacion=timezone.now()
        )
        self.message_user(request, f'{updated} reporte(s) rechazado(s).')
    rechazar_reportes.short_description = "❌ Rechazar reportes seleccionados"
    
    def marcar_pendientes(self, request, queryset):
        updated = queryset.update(estado='pendiente')
        self.message_user(request, f'{updated} reporte(s) marcado(s) como pendiente(s).')
    marcar_pendientes.short_description = "⏳ Marcar como pendientes"


@admin.register(Foto)
class FotoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'imagen_preview',
        'reporte_link',
        'estado_badge',
        'contenido_grafico_badge',
        'censurada_badge',
        'orden',
        'subida_en_corta'
    )
    
    list_filter = (
        'estado_moderacion',
        'es_censurada',
        'contiene_contenido_grafico',
        'subida_en'
    )
    
    search_fields = ('reporte__titulo', 'id')
    
    readonly_fields = ('subida_en', 'imagen_completa')
    
    ordering = ('-subida_en',)
    
    fieldsets = (
        ('📷 Imagen', {
            'fields': ('reporte', 'archivo', 'imagen_completa', 'orden')
        }),
        ('⚠️ Moderación de Contenido', {
            'fields': ('estado_moderacion', 'contiene_contenido_grafico', 'es_censurada')
        }),
        ('🕐 Información', {
            'fields': ('subida_en',)
        }),
    )
    
    def imagen_preview(self, obj):
        if obj.archivo:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 80px; '
                'border-radius: 4px; border: 1px solid #ddd;" />',
                obj.archivo.url
            )
        return "Sin imagen"
    imagen_preview.short_description = "Preview"
    
    def imagen_completa(self, obj):
        if obj.archivo:
            return format_html(
                '<img src="{}" style="max-width: 100%; max-height: 500px; '
                'border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.archivo.url
            )
        return "Sin imagen"
    imagen_completa.short_description = "Imagen completa"
    
    def reporte_link(self, obj):
        url = reverse('admin:server_nuevoreporte_change', args=[obj.reporte.id])
        return format_html('<a href="{}">{}</a>', url, obj.reporte.titulo[:40])
    reporte_link.short_description = "Reporte"
    
    def estado_badge(self, obj):
        colores = {
            'pendiente': '#ffc107',
            'aprobada': '#28a745',
            'rechazada': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 10px;">{}</span>',
            colores.get(obj.estado_moderacion, '#6c757d'),
            obj.get_estado_moderacion_display()
        )
    estado_badge.short_description = "Estado"
    
    def contenido_grafico_badge(self, obj):
        if obj.contiene_contenido_grafico:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ Sí</span>'
            )
        return format_html('<span style="color: #6c757d;">No</span>')
    contenido_grafico_badge.short_description = "Contenido gráfico"
    
    def censurada_badge(self, obj):
        if obj.es_censurada:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">🚫 Sí</span>'
            )
        return format_html('<span style="color: #28a745;">No</span>')
    censurada_badge.short_description = "Censurada"
    
    def subida_en_corta(self, obj):
        return obj.subida_en.strftime('%d/%m/%Y %H:%M')
    subida_en_corta.short_description = "Subida"


@admin.register(ModeracionLog)
class ModeracionLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'fecha_corta',
        'moderador',
        'accion_badge',
        'reporte_link',
        'motivo_corto'
    )
    
    list_filter = ('accion', 'fecha', 'moderador')
    
    search_fields = ('reporte__titulo', 'moderador__username', 'motivo')
    
    readonly_fields = ('fecha', 'moderador', 'reporte', 'accion', 'motivo')
    
    date_hierarchy = 'fecha'
    
    ordering = ('-fecha',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    
    def fecha_corta(self, obj):
        return obj.fecha.strftime('%d/%m/%Y %H:%M')
    fecha_corta.short_description = "Fecha"
    
    def accion_badge(self, obj):
        colores = {
            'verificado': '#28a745',
            'rechazado': '#dc3545',
            'comentario': '#17a2b8'
        }
        iconos = {
            'verificado': '✅',
            'rechazado': '❌',
            'comentario': '💬'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px;">{} {}</span>',
            colores.get(obj.accion, '#6c757d'),
            iconos.get(obj.accion, ''),
            obj.get_accion_display()
        )
    accion_badge.short_description = "Acción"
    
    def reporte_link(self, obj):
        url = reverse('admin:server_nuevoreporte_change', args=[obj.reporte.id])
        return format_html('<a href="{}">{}</a>', url, obj.reporte.titulo[:50])
    reporte_link.short_description = "Reporte"
    
    def motivo_corto(self, obj):
        if obj.motivo:
            return obj.motivo[:60] + '...' if len(obj.motivo) > 60 else obj.motivo
        return format_html('<em style="color: #999;">Sin motivo</em>')
    motivo_corto.short_description = "Motivo"



admin.site.site_header = "🐕 Sistema de Reportes de Ataques"
admin.site.site_title = "Admin - Reportes"
admin.site.index_title = "Panel de Administración"