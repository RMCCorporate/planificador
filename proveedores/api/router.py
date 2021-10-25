from rest_framework.routers import DefaultRouter
from proveedores.api.views import ProveedorApiViewSet, RMCApiViewSet, ContactoApiViewSet, CalificacionApiViewSet

router_proveedores = DefaultRouter()

router_proveedores.register(prefix='calificacion', basename='calificacion', viewset=CalificacionApiViewSet)
router_proveedores.register(prefix='contacto', basename='contacto', viewset=ContactoApiViewSet)
router_proveedores.register(prefix='proveedores', basename='proveedores', viewset=ProveedorApiViewSet)
router_proveedores.register(prefix='RMC', basename='RMC', viewset=RMCApiViewSet)
