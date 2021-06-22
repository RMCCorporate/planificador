from django.contrib import admin

# Register your models here.
from .models import Producto, Proyecto, Proveedor, Producto_proyecto,  SubClase, Clase, Contacto, Calificacion, Calificacion_Proveedor, Precio, Filtro_producto, Cotizacion, Usuario, Producto_proveedor, Correlativo_cotizacion, Notificacion, Permisos_notificacion, Planilla

admin.site.register(Precio)
admin.site.register(Proyecto)
admin.site.register(Producto)
admin.site.register(Proveedor)
admin.site.register(SubClase)
admin.site.register(Producto_proyecto)
admin.site.register(Clase)
admin.site.register(Contacto)
admin.site.register(Calificacion)
admin.site.register(Calificacion_Proveedor)
admin.site.register(Filtro_producto)
admin.site.register(Cotizacion)
admin.site.register(Correlativo_cotizacion)
admin.site.register(Usuario)
admin.site.register(Producto_proveedor)
admin.site.register(Notificacion)
admin.site.register(Permisos_notificacion)
admin.site.register(Planilla)


