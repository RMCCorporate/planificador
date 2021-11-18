from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not correo:
            raise ValueError("Users must have an email address")
        user = self.model(correo=self.normalize_email(correo), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, correo, password):
        """Creates and saves a new super user"""
        user = self.create_user(correo, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Precio(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    valor = models.FloatField()
    valor_importación = models.FloatField(null=True)
    tipo_cambio = models.CharField(max_length=128, default="CLP")
    valor_cambio = models.FloatField(null=True)
    fecha = models.DateTimeField(null=True)
    nombre_proveedor = models.CharField(max_length=128, null=True)
    nombre_cotizacion = models.CharField(max_length=128, null=True)
    nombre_importacion = models.CharField(max_length=128, null=True)
    comentarios = models.TextField(null=True)
    usuario_modificacion = models.CharField(max_length=128, null=True)


class ImagenProducto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    imagen = models.ImageField(upload_to="images", null=True)


class Producto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    nombre = models.CharField(max_length=512)
    lista_precios = models.ManyToManyField(Precio)
    fecha_actualizacion = models.DateTimeField(auto_now_add=True, null=True)
    unidad = models.CharField(max_length=128, null=True)
    kilos = models.FloatField(null=True)
    imagen = models.ManyToManyField(ImagenProducto)
    proveedor_interno = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.nombre


class SubClase(models.Model):
    nombre = models.CharField(primary_key=True, max_length=128)
    productos = models.ManyToManyField(Producto)
    utilidad = models.FloatField(null=True)

    def __str__(self):
        return self.nombre


class Clase(models.Model):
    nombre = models.CharField(primary_key=True, max_length=128)
    subclases = models.ManyToManyField(SubClase)

    def __str__(self):
        return self.nombre


class Gastos_generales(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    fecha = models.DateTimeField(auto_now_add=False, null=True)
    numero_factura = models.CharField(max_length=128, null=True)
    factura_o_boleta = models.CharField(max_length=128, null=True)
    razon_social = models.CharField(max_length=128, null=True)
    detalle = models.CharField(max_length=128, null=True)
    monto = models.IntegerField(null=True)


class Relacion_gastos(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    numero_relacion = models.CharField(max_length=128, null=True)
    fecha = models.DateTimeField(auto_now_add=False, null=True)
    periodo_desde = models.DateTimeField(auto_now_add=False, null=True)
    periodo_hasta = models.DateTimeField(auto_now_add=False, null=True)
    rut_solicitante = models.CharField(max_length=128, null=True)
    rut_autorizador = models.CharField(max_length=128, null=True)
    rut_aprobador = models.CharField(max_length=128, null=True)
    gastos_generales = models.ManyToManyField(Gastos_generales)
    total_boleta = models.IntegerField(null=True)
    total_factura = models.IntegerField(null=True)


class Presupuesto_subclases(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    valor = models.FloatField(null=True)
    subclase = models.ForeignKey(
        SubClase, on_delete=models.CASCADE, related_name="subclase"
    )
    utilidad = models.FloatField(null=True)


class Proyecto(models.Model):
    id = models.CharField(primary_key=True, max_length=128)
    productos = models.ManyToManyField(
        Producto,
        through="Producto_proyecto",
        through_fields=("producto", "proyecto"),
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
    relacion_gastos = models.ManyToManyField(Relacion_gastos)
    COMPLETO = "Completo"
    INCOMPLETO = "Incompleto"
    ESTADO_CHOICES = [
        (COMPLETO, "Completo"),
        (INCOMPLETO, "Incompleto"),
    ]
    estado = models.CharField(
        max_length=128, choices=ESTADO_CHOICES, default=INCOMPLETO, null=True
    )
    presupuesto_total = models.FloatField(null=True)
    presupuesto_subclases = models.ManyToManyField(Presupuesto_subclases)
    consolidacion = models.BooleanField(default=False, null=True)

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
        through="Calificacion_Proveedor",
        through_fields=("proveedor", "calificacion"),
        null=True
    )
    contactos_asociados = models.ManyToManyField(Contacto, null=True)
    ESPANOL = "ES"
    INGLES = "EN"
    IDIOMA_CHOICES = [
        (ESPANOL, "Español"),
        (INGLES, "Inglés"),
    ]
    idioma = models.CharField(
        max_length=128, choices=IDIOMA_CHOICES, default=ESPANOL, null=True
    )
    direccion = models.CharField(max_length=256, null=True)
    productos_no = models.ManyToManyField(Producto, null=True)

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
    URGENTE = "Urgente"
    FUTURO = "Futuro"
    ESTADO_COMPRAS_CHOICES = [
        (URGENTE, "Urgente"),
        (FUTURO, "Futuro"),
    ]
    status = models.CharField(
        max_length=128,
        choices=ESTADO_COMPRAS_CHOICES,
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
    utilizado = models.CharField(max_length=128, null=True)


class Producto_proyecto_cantidades(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    proyecto_asociado_cantidades = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="proyecto_asociado_cantidades",
        null=True,
    )
    producto_asociado_cantidades = models.ForeignKey(
        Producto_proyecto,
        on_delete=models.CASCADE,
        related_name="producto_asociado_cantidades",
        null=True,
    )
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="producto", null=True
    )
    precio = models.ForeignKey(
        Precio, on_delete=models.CASCADE, related_name="precio", null=True
    )
    cantidades = models.CharField(max_length=128, null=True)


class Cotizacion(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    nombre = models.CharField(max_length=128, null=True)
    proyecto_asociado = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="proyecto_asociado"
    )
    productos_asociados = models.ManyToManyField(
        Producto, related_name="productos_asociados"
    )
    productos_proyecto_asociados = models.ManyToManyField(
        Producto_proyecto_cantidades,
        related_name="productos_proyecto_asociados",
        null=True,
    )
    orden_compra = models.BooleanField(null=True)
    proveedor_asociado = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name="proveedor_asociado",
        null=True,
    )
    contacto_asociado = models.ManyToManyField(
        Contacto, related_name="contacto_asociado", null=True
    )
    fecha_salida = models.DateField(auto_now=False, auto_now_add=False, null=True)
    fecha_respuesta = models.DateField(auto_now=False, auto_now_add=False, null=True)
    fecha_actualizacion_precio = models.DateField(
        auto_now=False, auto_now_add=False, null=True
    )
    usuario_modificacion = models.CharField(max_length=128, null=True)


class User(AbstractBaseUser, PermissionsMixin):
    correo = models.CharField(max_length=128, unique=True)
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
    orden_compra = models.IntegerField(null=True)
    session_key = models.CharField(max_length=100, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "correo"


class Correlativo_cotizacion(models.Model):
    año = models.IntegerField(primary_key=True)
    numero = models.IntegerField()


class Correlativo_orden_compra(models.Model):
    año = models.IntegerField(primary_key=True)
    numero = models.IntegerField()


class Correlativo_producto(models.Model):
    producto = models.IntegerField(primary_key=True)
    numero = models.IntegerField()


class Permisos_notificacion(models.Model):
    nombre = models.CharField(max_length=128, primary_key=True)
    usuarios = models.ManyToManyField(User)


class Notificacion(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    tipo = models.CharField(max_length=128, null=True)
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
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


class RMC(models.Model):
    rut = models.CharField(max_length=128, primary_key=True)
    nombre = models.CharField(max_length=128, null=True)
    giro = models.CharField(max_length=128, null=True)
    direccion = models.CharField(max_length=128, null=True)


class Orden_compra(models.Model):
    id = models.CharField(max_length=128, primary_key=True)
    cotizacion_padre = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, null=True, related_name="cotizacion_padre"
    )
    cotizacion_hija = models.ForeignKey(
        Cotizacion, on_delete=models.CASCADE, null=True, related_name="cotizacion_hija"
    )
    condicion_entrega = models.CharField(max_length=128, null=True)
    condiciones_pago = models.CharField(max_length=128, null=True)
    status_llegada = models.CharField(max_length=128, null=True)
    status_financiero = models.CharField(max_length=128, null=True)
    forma_pago = models.CharField(max_length=128, null=True)
    destino_factura = models.ForeignKey(
        RMC, on_delete=models.CASCADE, null=True, related_name="destino_factura"
    )
    observaciones = models.TextField(null=True)
    planilla = models.FileField(upload_to="img", null=True, max_length=255)
    fecha_envio = models.DateField(auto_now=False, auto_now_add=False, null=True)


class Origin_charges(models.Model):
    origin_airport = models.CharField(max_length=128, primary_key=True)
    currency = models.CharField(max_length=128, null=True)
    pickup_min = models.FloatField(null=True)
    pickup_kg = models.FloatField(null=True)
    handling = models.FloatField(null=True)
    customs_clearence = models.FloatField(null=True)
    other_fees1_description = models.CharField(max_length=128, null=True)
    other_fees1_value_min = models.FloatField(null=True)
    other_fees1_value_kg = models.FloatField(null=True)
    other_fees2_description = models.CharField(max_length=128, null=True)
    other_fees2_value_min = models.FloatField(null=True)
    other_fees2_value_kg = models.FloatField(null=True)
    origin_transit_time = models.FloatField(null=True)


class Airfreight_charges(models.Model):
    origin_airport = models.CharField(max_length=128, primary_key=True)
    currency = models.CharField(max_length=128, null=True)
    freight_min = models.FloatField(null=True)
    freight_less_45 = models.FloatField(null=True)
    freight_45_100 = models.FloatField(null=True)
    freight_100_300 = models.FloatField(null=True)
    freight_300_500 = models.FloatField(null=True)
    freight_500_1000 = models.FloatField(null=True)
    freight_more_1000 = models.FloatField(null=True)
    fuel_surcharge_min = models.FloatField(null=True)
    fuel_surcharge_kg = models.FloatField(null=True)
    security_surcharge_min = models.FloatField(null=True)
    security_surcharge_kg = models.FloatField(null=True)
    cargo_screening_fee_min = models.FloatField(null=True)
    cargo_screening_fee_kg = models.FloatField(null=True)


class Destination_charges(models.Model):
    origin_airport = models.CharField(max_length=128, primary_key=True)
    currency = models.CharField(max_length=128, null=True)
    terminal_handling = models.FloatField(null=True)
    doc_fee_min = models.FloatField(null=True)
    doc_fee_max = models.FloatField(null=True)
    doc_fee_kg = models.FloatField(null=True)
    desconsolidation = models.FloatField(null=True)


class DHL(models.Model):
    origin_airport = models.CharField(max_length=128, primary_key=True)
    region = models.CharField(max_length=128, null=True)
    country = models.CharField(max_length=128, null=True)
    priority = models.CharField(max_length=128, null=True)
    origin = models.ForeignKey(
        Origin_charges,
        on_delete=models.CASCADE,
        null=True,
        related_name="origin_charges",
    )
    freight = models.ForeignKey(
        Airfreight_charges,
        on_delete=models.CASCADE,
        null=True,
        related_name="freight_charges",
    )
    destination = models.ForeignKey(
        Destination_charges,
        on_delete=models.CASCADE,
        null=True,
        related_name="destination_charges",
    )
    airline = models.CharField(max_length=128, null=True)
    direct_flight = models.CharField(max_length=128, null=True)
    departure_days = models.CharField(max_length=128, null=True)
    transit_time = models.CharField(max_length=128, null=True)


class Importaciones(models.Model):
    codigo = models.CharField(max_length=128, primary_key=True)
    codigo_referencial = models.CharField(max_length=128, null=True)
    origen = models.CharField(max_length=128, null=True)
    productos = models.ManyToManyField(
        Producto_proyecto_cantidades, related_name="productos_importacion"
    )
    proveedor = models.ForeignKey(Proveedor, null=True, on_delete=models.CASCADE)
    DHL_asociado = models.ForeignKey(
        DHL, on_delete=models.CASCADE, null=True, related_name="dhl"
    )
    transporte = models.CharField(max_length=128, null=True)
    kilos = models.FloatField(null=True)
    valor_flete = models.FloatField(null=True)
    valor_origen = models.FloatField(null=True)
    valor_destino = models.FloatField(null=True)
    gastos_despacho = models.FloatField(null=True)
    honorarios = models.FloatField(null=True)
    moneda_importacion = models.CharField(max_length=128, null=True)
    valor_moneda_importacion = models.FloatField(null=True)
    valor_dolar = models.FloatField(null=True)
    UF = models.FloatField(null=True)
    advalorem = models.FloatField(null=True)
    costo_producto = models.FloatField(null=True)
    fecha_emision = models.DateField(auto_now=False, auto_now_add=False, null=True)
    fecha_llegada = models.DateField(auto_now=False, auto_now_add=False, null=True)

class Cotizacion_DHL(models.Model):
    codigo = models.CharField(max_length=128, primary_key=True)
    direccion = models.CharField(max_length=128, null=True)
    carga_peligrosa = models.CharField(max_length=128, null=True)
    invoice = models.FileField(upload_to="img", null=True, max_length=255)
    info = models.FileField(upload_to="img", null=True, max_length=255)
    dgd = models.FileField(upload_to="img", null=True, max_length=255)
    msds = models.FileField(upload_to="img", null=True, max_length=255)
    usuario_modificacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )