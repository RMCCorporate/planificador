from django.contrib import admin

# Register your models here.
from .models import Producto, Proyecto, Proveedor, Producto_proyecto

admin.site.register(Producto)
admin.site.register(Proyecto)
admin.site.register(Proveedor)
admin.site.register(Producto_proyecto)
