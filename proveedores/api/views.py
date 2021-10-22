from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from planificador.models import Proveedor, RMC
from proveedores.api.serializers import ProveedorSerializer, RMCSerializer
from proveedores.api.permissions import IsAdminOrReadOnly


class ProveedorApiViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ProveedorSerializer
    queryset = Proveedor.objects.all()
    # queryset = Proveedor.objects.filter(published=True)
    lookup_field = 'rut'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nombre']


class RMCApiViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = RMCSerializer
    queryset = RMC.objects.all()
    # queryset = RMC.objects.filter(published=True)
    lookup_field = 'rut'
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nombre']
