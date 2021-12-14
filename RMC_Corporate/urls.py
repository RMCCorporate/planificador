"""RMC_Corporate URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from planificador import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls import url

schema_view = get_schema_view(
    openapi.Info(
        title="Documentación API Planificador",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="home"),
    path("planificador/crear_usuario/", views.crear_usuario, name="crear_usuario"),
    path("planificador/crear_grupo/", views.crear_grupo, name="crear_grupo"),
    path("planificador/crear_permisos/", views.crear_permisos, name="crear_permisos"),
    path("planificador/usuario/", views.usuario, name="usuario"),
    path(
        "planificador/nueva_subclase/",
        views.agregar_subclases,
        name="agregar_subclases",
    ),
    path(
        "planificador/actualizar_planilla/",
        views.actualizar_planilla,
        name="actualizar_planilla",
    ),
    path(
        "planificador/permisos_notificacion/",
        views.permisos_notificacion,
        name="permisos_notificacion",
    ),
    path(
        "planificador/editar_usuario/<str:correo>",
        views.editar_usuario,
        name="editar_usuario",
    ),
    path("notificaciones/", views.notificaciones, name="notificaciones"),
    path("", include("users.urls")),
    path("", include("productos.urls")),
    path("", include("proveedores.urls")),
    path("", include("proyectos.urls")),
    path("", include("calculo.urls")),
    path("", include("importaciones.urls")),
    path("token/", include("users.api.router")),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redocs/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
