from django.db import models
from django.contrib.postgres.fields import ArrayField

class Precio(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    valor = models.FloatField()
    valor_importación = models.FloatField(null=True)
    tipo_cambio = models.CharField(max_length=128, default="CLP")
    valor_cambio = models.FloatField(null=True)
    fecha = models.DateTimeField(auto_now_add=True, null=True)
    nombre_proveedor = models.CharField(max_length=128, null=True)
    comentarios = models.TextField(null=True)

class Producto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    nombre = models.CharField(max_length=128)
    lista_precios = models.ManyToManyField(Precio)
    fecha_actualizacion = models.DateTimeField(auto_now_add=True, null=True)
    unidad = models.CharField(max_length=128, null=True)
    kilos =  models.FloatField(null=True)
    imagen = models.ImageField(upload_to='images', null=True)
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
    fecha_creacion = models.DateField(auto_now_add=True, null=True)
    fecha_inicio = models.DateField(auto_now=False, auto_now_add=False, null=True)
    fecha_final = models.DateField(auto_now=False, auto_now_add=False, null=True)
    creador = models.CharField(max_length=128)
    tipo_cambio = models.CharField(max_length=128, null=True, default="CLP")
    valor_cambio = models.FloatField(null=True, default=1)
    COMPLETO = 'Completo'
    INCOMPLETO = 'Incompleto'
    ESTADO_CHOICES = [
        (COMPLETO, 'Completo'),
        (INCOMPLETO, 'Incompleto'),
    ]
    estado = models.CharField(
        max_length=128,
        choices = ESTADO_CHOICES,
        default = INCOMPLETO,
        null = True
    )
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
    subclases_asociadas = models.ManyToManyField(SubClase)
    calificaciones = models.ManyToManyField(
        Calificacion,
        through='Calificacion_Proveedor',
        through_fields=('proveedor', 'calificacion'),
    )
    contactos_asociados = models.ManyToManyField(Contacto)
    ESPANOL = 'ESP'
    INGLES = 'EN'
    IDIOMA_CHOICES = [
        (ESPANOL, 'Español'),
        (INGLES, 'Inglés'),
    ]
    idioma = models.CharField(
        max_length=128,
        choices = IDIOMA_CHOICES,
        default = ESPANOL,
        null = True
    )
    direccion = models.CharField(max_length=256, null=True)
    def __str__(self):
        return self.nombre

class Calificacion_Proveedor(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    calificacion = models.ForeignKey(Calificacion, on_delete=models.CASCADE)
    nota = models.FloatField()

class Producto_proyecto(models.Model):
    producto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedores = models.ManyToManyField(Proveedor)
    URGENTE = 'Urgente'
    TRANSPORTE = 'Transporte'
    BODEGA = 'Bodega'
    FUTURO = 'Futuro'
    ESTADO_COMPRAS_CHOICES = [
        (URGENTE,'Urgente'),
        (TRANSPORTE, 'Transporte'),
        (BODEGA, 'Bodega'),
        (FUTURO, 'Futuro'),
    ]
    status = models.CharField(
        max_length=128,
        choices = ESTADO_COMPRAS_CHOICES,
        default=FUTURO,
    )
    fecha_uso = models.DateField(null=True)
    cantidades = models.FloatField(null=True)
    usuario_modificacion = models.CharField(max_length=128, null=True)

class Producto_proveedor(models.Model):
    producto = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    nombre_RMC = models.CharField(max_length=128)
    nombre_proveedor = models.CharField(max_length=128)