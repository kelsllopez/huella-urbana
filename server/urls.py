from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    # ============================
    # Público / Principal
    # ============================
    path('', views.index, name='index'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('detalle_reporte_mapa/<int:id>/', views.detalle, name='detalle_reporte_mapa'),
    path('nuevo/', views.nuevo_reporte, name='nuevo_reporte'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('mapa/', views.mapa, name='mapa'),
    path('contacto/', views.contacto, name='contacto'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('acerca/', views.acerca, name='acerca'),

    # ============================
    # Autenticación
    # ============================
    path('registro/', views.registro, name='registro'),
    path('logout/', views.cerrar_sesion, name='logout'),

    path("login/", views.login_view, name="login"),

    # ============================
    # Reset Password (flujo completo)
    # ============================
    path("reset/", auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset_form.html",
            email_template_name="registration/password_reset_email.txt",  # texto
            html_email_template_name="registration/password_reset_email.html",  # HTML bonito
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset"
    ),
    path('reset/enviado/',auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html',success_url='/reset/completo/'),name='password_reset_confirm'),
    path('reset/completo/',auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'),name='password_reset_complete'),
    path("api/check-email/", views.check_email, name="check_email"),

    # ============================
    # Moderador
    # ============================
    path('moderador/', views.panel_moderador, name='panel_moderador'),
    path('detalles/<int:id>/', views.detalles_reporte, name='detalles_reporte'),
    path('aprobar/<int:id>/', views.aprobar_reporte, name='aprobar_reporte'),
    path('rechazar/<int:id>/', views.rechazar_reporte, name='rechazar_reporte'),
    path('exportar_csv/', views.exportar_csv, name='exportar_csv'),

    # ============================
    # Administrador de Usuarios (CRUD)
    # ============================
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/<int:user_id>/data/', views.usuario_data, name='usuario_data'),
    path('usuarios/<int:user_id>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:user_id>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),

]
