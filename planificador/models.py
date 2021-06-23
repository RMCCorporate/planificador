from django.db import models
from django.contrib.postgres.fields import ArrayField

class Precio(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    valor = models.FloatField()
    valor_importación = models.FloatField(null=True)
    tipo_cambio = models.CharField(max_length=128, default="CLP")
    valor_cambio = models.FloatField(null=True)
    fecha = models.DateTimeField(null=True)
    nombre_proveedor = models.CharField(max_length=128, null=True)
    nombre_cotizacion = models.CharField(max_length=128, null=True)
    comentarios = models.TextField(null=True)
    usuario_modificacion = models.CharField(max_length=128, null=True)

class Producto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    nombre = models.CharField(max_length=512)
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
    centro_costos = models.CharField(max_length=128, null=True)
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
    ESPANOL = 'ES'
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
    id = models.CharField(max_length=128, primary_key=True)
    producto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedores = models.ManyToManyField(Proveedor)
    URGENTE = 'Urgente'
    FUTURO = 'Futuro'
    ESTADO_COMPRAS_CHOICES = [
        (URGENTE,'Urgente'),
        (FUTURO, 'Futuro'),
    ]
    status = models.CharField(
        max_length=128,
        choices = ESTADO_COMPRAS_CHOICES,
        default=FUTURO,
    )
    estado_cotizacion = models.CharField(max_length=128, null=True)
    estado_tiempo = models.CharField(max_length=128, null=True)
    fecha_uso = models.DateField(null=True)
    cantidades = models.FloatField(null=True)
    usuario_modificacion = models.CharField(max_length=128, null=True)

class Producto_proveedor(models.Model):
    producto = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    nombre_RMC = models.CharField(max_length=128)
    nombre_proveedor = models.CharField(max_length=128)

class Filtro_producto(models.Model):
    nombre_producto = models.CharField(max_length=128, primary_key=True)
    nombre_clase = models.CharField(max_length=128)
    id_producto = models.CharField(max_length=128, null=True)
    nombre_subclase = models.CharField(max_length=128)

class Cotizacion(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    nombre = models.CharField(max_length=128, null=True)
    proyecto_asociado = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='proyecto_asociado')
    productos_asociados = models.ManyToManyField(Producto, related_name='productos_asociados')
    proveedor_asociado = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='proveedor_asociado', null=True)
    contacto_asociado = models.ManyToManyField(Contacto, related_name='contacto_asociado')
    fecha_salida = models.DateField(auto_now=False, auto_now_add=False, null=True)
    fecha_respuesta = models.DateField(auto_now=False, auto_now_add=False, null=True)
    fecha_actualizacion_precio = models.DateField(auto_now=False, auto_now_add=False, null=True)
    usuario_modificacion = models.CharField(max_length=128, null=True)

class Usuario(models.Model):
    correo = models.CharField(max_length=128, primary_key=True)
    nickname = models.CharField(max_length=128, null=True)
    nombre = models.CharField(max_length=128, null=True)
    apellido = models.CharField(max_length=128, null=True)
    segundo_apellido = models.CharField(max_length=128, null=True)
    celular = models.CharField(max_length=128, null=True)
    cargo = models.CharField(max_length=128, null=True)
    telefono = models.CharField(max_length=128, null=True)
    precios = models.ManyToManyField(Precio)
    productos_proyecto = models.ManyToManyField(Producto_proyecto)
    proyectos = models.ManyToManyField(Proyecto)
    cotizaciones = models.ManyToManyField(Cotizacion)
    notificaciones = models.IntegerField(null=True)
    session_key = models.CharField(max_length=100, null=True)

class Correlativo_cotizacion(models.Model):
    año = models.IntegerField(primary_key=True)
    numero = models.IntegerField()

class Correlativo_producto(models.Model):
    producto = models.IntegerField(primary_key=True)
    numero = models.IntegerField()

class Permisos_notificacion(models.Model):
    nombre = models.CharField(max_length=128, primary_key=True)
    usuarios = models.ManyToManyField(Usuario)

class Notificacion(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    tipo = models.CharField(max_length=128, null=True)
    usuario_modificacion =  models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True)
    accion = models.CharField(max_length=128, null=True)
    modelo_base_datos = models.CharField(max_length=128, null=True)
    numero_modificado = models.IntegerField(null=True)
    id_modelo = models.CharField(max_length=128, null=True)
    nombre = models.CharField(max_length=128, null=True)
    id_proyecto = models.CharField(max_length=128, null=True)
    fecha = models.DateTimeField(auto_now_add=False, null=True)
    
    def __str__(self):
        return self.tipo
    
class Planilla(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    planilla = models.FileField(upload_to="img")