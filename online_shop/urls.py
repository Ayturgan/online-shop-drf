from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.views.generic import TemplateView
from online_shop import settings

schema_view = get_schema_view(  # new
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),

    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path(
      'swagger-ui/',
      TemplateView.as_view(
          template_name='swaggerui/swaggerui.html',
          extra_context={'schema_url': 'openapi-schema'}
      ),
      name='swagger-ui'),
    re_path(
      r'^swagger(?P<format>\.json|\.yaml)$',
      schema_view.without_ui(cache_timeout=0),
      name='schema-json'),
    path('admin/', admin.site.urls),
    path('swagger/',schema_view.as_view()),
    path("api/", include("rest_framework.urls")),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.product.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

