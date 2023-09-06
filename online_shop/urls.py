from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from online_shop import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path("api/", include("rest_framework.urls")),
    path('api/', include('users.urls')),
    path('api/', include('product.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

