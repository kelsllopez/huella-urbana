from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('server.urls')),
    path('accounts/', include('allauth.urls')),
]

# ✅ Solo servir archivos estáticos (CSS, JS) en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ⚠️ NO incluir MEDIA_URL cuando usas Cloudinary