from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),    # 🟣 RESTAURADO: PANEL ADMIN
    path('', include('server.urls')),   # Rutas de tu aplicación principal
    path('accounts/', include('allauth.urls')),

]

# Archivos multimedia
if settings.DEBUG is False:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
