from django.contrib import admin

# Register your models here.
from .models import Producto, Proyecto, Proveedor, Producto_proyecto, Precio, SubClase, Clase, Contacto, Calificacion, Calificacion_Proveedor

admin.site.register(Precio)
admin.site.register(Proyecto)
admin.site.register(Producto)
admin.site.register(SubClase)
admin.site.register(Producto_proyecto)
admin.site.register(Clase)
admin.site.register(Contacto)
admin.site.register(Calificacion)
admin.site.register(Calificacion_Proveedor)

