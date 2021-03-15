from django.db import models
from django.contrib.postgres.fields import ArrayField

class Precio(models.Model):
    fecha_actualizacion = models.DateField(primary_key=True)
    valor = models.FloatField()
    tipo_cambio = models.CharField(max_length=128, default="CLP")

class Producto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    nombre = models.CharField(max_length=128)
    lista_precios = models.ManyToManyField(Precio)
    fecha_actualizacion = models.DateField(null=True)
    fechas_actualizaciones_historicas = ArrayField(models.CharField(max_length=128, null=True), default=list)
    unidad = models.CharField(max_length=128, null=True)
    ultimo_proveedor = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.nombre

class SubClase(models.Model):
    nombre = models.CharField(primary_key=True, max_length=128)
    productos = models.ManyToManyField(Producto)

    def __str__(self):
        return self.nombre

class Clase(models.Model):
    nombre = models.CharField(primary_key=True, max_length=128)
    subclases = models.ManyToManyField(SubClase)

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    productos = models.ManyToManyField(
        Producto, 
        through='Producto_proyecto',
        through_fields=('producto', 'proyecto'),
        )
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

class Contacto(models.Model):
    correo = models.CharField(primary_key=True, max_length=128)
    telefono = models.CharField(max_length=128, null=True)
    nombre = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.nombre

class Calificacion(models.Model):
    nombre = models.CharField(primary_key=True, max_length=128)
    descripción = models.TextField()

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    rut = models.CharField(primary_key=True, max_length=128)
    nombre = models.CharField(max_length=128)
    razon_social = models.CharField(max_length=128, null=True)
    clases_asociadas = models.ManyToManyField(Clase)
    calificaciones = models.ManyToManyField(
        Calificacion,
        through='Calificacion_Proveedor',
        through_fields=('proveedor', 'calificacion'),
    )
    contactos_asociados = models.ManyToManyField(Contacto)
    
    def __str__(self):
        return self.nombre

class Calificacion_Proveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE)
    nota = models.FloatField()

class Producto_proyecto(models.Model):
    producto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Producto, on_delete=models.CASCADE)
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
    tipo_cambio = models.CharField(max_length=128, null=True)