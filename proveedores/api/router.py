from rest_framework.routers import DefaultRouter
from proveedores.api.views import ProveedorApiViewSet, RMCApiViewSet

router_proveedores = DefaultRouter()

router_proveedores.register(prefix='proveedores', basename='proveedores', viewset=ProveedorApiViewSet)
router_proveedores.register(prefix='RMC', basename='RMC', viewset=RMCApiViewSet)