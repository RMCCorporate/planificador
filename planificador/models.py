from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Producto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    nombre = models.CharField(max_length=128)
    lista_precios = ArrayField(models.IntegerField(null=True), default=list)
    fecha_actualizacion = models.DateField(null=True)
    fechas_actualizaciones_historicas = ArrayField(models.CharField(max_length=128, null=True), default=list)
    clase = models.CharField(max_length=128)
    subclase = models.CharField(max_length=128)
    unidad = models.CharField(max_length=128, null=True)
    ultimo_proveedor = models.CharField(max_length=128, null=True)
    lista_proveedores = ArrayField(models.CharField(max_length=128, null=True), default=list)
    lista_tipo_cambio = ArrayField(models.CharField(max_length=128, null=True), default=list)

    def __str__(self):
        return self.nombre

class Proyecto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    productos = models.ManyToManyField(Producto, through='Producto_proyecto')
    nombre = models.CharField(max_length=128)
    precio_final = models.FloatField(null=True)
    centro_costos = models.CharField(max_length=128, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False, null=True)
    fecha_final = models.DateField(auto_now=False, auto_now_add=False, null=True)
    administrador_contrato = models.CharField(max_length=128, null=True)
    creador = models.CharField(max_length=128)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    rut = models.CharField(primary_key=True, max_length=128)
    nombre = models.CharField(max_length=128)
    razon_social = models.CharField(max_length=128, null=True)
    clases = ArrayField(models.CharField(null=True, max_length=128))
    subclases = ArrayField(models.CharField(null=True, max_length=128))
    lista_nombre_calificaciones = ArrayField(models.CharField(max_length=128, null=True), default=list)
    lista_calificaciones = ArrayField(models.FloatField(null=True), default=list)
    lista_contactos = ArrayField(models.CharField(max_length=128, null=True), default=list)
    
    def __str__(self):
        return self.nombre

class Producto_proyecto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    URGENTE = 'UR'
    TRANSPORTE = 'TR'
    BODEGA = 'BO'
    FUTURO = 'FU'
    ESTADO_COMPRAS_CHOICES = [
        (URGENTE,'Urgente'),
        (TRANSPORTE, 'Transporte'),
        (BODEGA, 'Bodega'),
        (FUTURO, 'Futuro'),
    ]
    status = models.CharField(
        max_length=2,
        choices = ESTADO_COMPRAS_CHOICES,
        default=FUTURO,
    )
    fecha_uso = models.DateField(null=True)
    usuario_modificacion = models.CharField(max_length=128, null=True)