from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField

class PerfilUsuario(models.Model):
    ROLES = [
        ('usuario', 'Usuario Registrado'),
        ('moderador', 'Moderador'),
        ('admin', 'Administrador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')

    def __str__(self):
        return f"{self.user.username} ({self.rol})"


class NuevoReporte(models.Model):
    TIPO_ANIMAL_CHOICES = [
        ('perro', 'Perro doméstico'),
        ('gato', 'Gato'),
        ('otro', 'Otro animal'),
    ]

    GRAVEDAD_CHOICES = [
        ('leve', 'Leve'),
        ('moderado', 'Moderado'),
        ('grave', 'Grave'),
    ]

    SECTOR_CHOICES = [
        ('centro', 'Centro'),
        ('las_animas', 'Las Ánimas'),
        ('collico', 'Collico'),
        ('parque_saval', 'Parque Saval'),
        ('isla_teja', 'Isla Teja'),
        ('los_pelues', 'Los Pelúes'),
        ('angachilla', 'Angachilla'),
        ('niebla', 'Niebla'),
        ('otro', 'Otro'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    titulo = models.CharField(max_length=200, verbose_name='Título')
    fecha = models.DateField(verbose_name='Fecha del incidente')
    hora = models.TimeField(null=True, blank=True, verbose_name='Hora aproximada')

    tipo_animal = models.CharField(
        max_length=20,
        choices=TIPO_ANIMAL_CHOICES,
        verbose_name='Tipo de animal víctima'
    )

    cantidad_perros = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name='Cantidad de perros agresores'
    )

    gravedad = models.CharField(
        max_length=20,
        choices=GRAVEDAD_CHOICES,
        verbose_name='Gravedad del ataque'
    )

    descripcion = models.TextField(verbose_name='Descripción detallada')

    direccion = models.CharField(max_length=300, verbose_name='Dirección')
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES, null=True, blank=True, verbose_name='Sector')

    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        verbose_name='Latitud'
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        verbose_name='Longitud'
    )

    nombre_reportante = models.CharField(max_length=200, null=True, blank=True, verbose_name='Nombre del reportante')
    email_reportante = models.EmailField(null=True, blank=True, verbose_name='Email del reportante')
    telefono_reportante = models.CharField(max_length=20, null=True, blank=True, verbose_name='Teléfono')
    anonimo = models.BooleanField(default=False, verbose_name='¿Reporte anónimo?')

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes'
    )

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    moderador = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_moderados'
    )
    fecha_moderacion = models.DateTimeField(null=True, blank=True)
    comentario_moderacion = models.TextField(null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} ({self.get_gravedad_display()} - {self.sector})"

    def nombre_visible(self):
        return "Anónimo" if self.anonimo else (self.nombre_reportante or "Anónimo")

    def clean(self):
        if self.anonimo:
            self.nombre_reportante = None
            self.email_reportante = None
            self.telefono_reportante = None

        if self.latitud == 0 and self.longitud == 0:
            raise ValidationError("Debes seleccionar una ubicación válida en el mapa.")


class Foto(models.Model):
    ESTADOS_MODERACION = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    reporte = models.ForeignKey(
        'NuevoReporte',
        related_name='fotos',
        on_delete=models.CASCADE,
        verbose_name='Reporte asociado'
    )

    archivo = CloudinaryField('imagen')


    subida_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de subida')
    orden = models.IntegerField(default=0, verbose_name='Orden de visualización')

    es_censurada = models.BooleanField(default=False, verbose_name='¿Censurada?')
    contiene_contenido_grafico = models.BooleanField(default=False, verbose_name='¿Contiene contenido gráfico?')

    estado_moderacion = models.CharField(
        max_length=20,
        choices=ESTADOS_MODERACION,
        default='pendiente',
        verbose_name='Estado de moderación'
    )

    class Meta:
        verbose_name = 'Fotografía'
        verbose_name_plural = 'Fotografías'
        ordering = ['orden', '-subida_en']

    def __str__(self):
        return f"Foto {self.id} - {self.reporte.titulo}"



class ModeracionLog(models.Model):
    ACCIONES = [
        ('verificado', 'Verificado'),
        ('rechazado', 'Rechazado'),
        ('comentario', 'Comentario interno'),
    ]

    reporte = models.ForeignKey(
        NuevoReporte,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    moderador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=50, choices=ACCIONES)
    motivo = models.TextField(blank=True, null=True, verbose_name="Motivo o Comentario")
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de moderación"
        verbose_name_plural = "Registros de moderación"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.moderador} → {self.accion} ({self.reporte.titulo})"
