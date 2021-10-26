from planificador.models import (
    Notificacion,
    Permisos_notificacion,
)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth import get_user_model
from datetime import datetime
import uuid


def crear_notificacion(
    tipo,
    correo_usuario,
    accion,
    modelo_base_datos,
    numero_modificado,
    id_modelo,
    nombre,
):
    hora_actual = datetime.now()
    usuario = get_user_model().objects.get(correo=correo_usuario)
    permiso_notificacion = Permisos_notificacion.objects.get(nombre=tipo)
    notificacion = Notificacion(
        id=uuid.uuid1(),
        tipo=tipo,
        accion=accion,
        usuario_modificacion=usuario,
        modelo_base_datos=modelo_base_datos,
        numero_modificado=numero_modificado,
        id_modelo=id_modelo,
        nombre=nombre,
        fecha=hora_actual,
    )
    notificacion.save()
    for i in permiso_notificacion.usuarios.all():
        i.notificaciones += 1
        i.save()
        if not notificacion.id_proyecto:
            texto_correo = "NOTIFICACIÓN: \nEstimado {} {}: \nEl usuario: {} {}, {} con detalle {} {} con fecha {}".format(
                i.nombre,
                i.apellido,
                notificacion.usuario_modificacion.nombre,
                notificacion.usuario_modificacion.apellido,
                notificacion.accion,
                notificacion.id_modelo,
                notificacion.nombre,
                notificacion.fecha,
            )
        else:
            texto_correo = "NOTIFICACIÓN: \nEstimado {} {}: \nEl usuario: {} {}, {} en el proyecto {} {} con fecha {}".format(
                i.nombre,
                i.apellido,
                notificacion.usuario_modificacion.nombre,
                notificacion.usuario_modificacion.apellido,
                notificacion.accion,
                notificacion.id_proyecto,
                notificacion.nombre,
                notificacion.fecha,
            )
        correo_enviador = "logistica@rmc.cl"
        clave_enviador = "RMC.1234"
        # CAMBIAR A i.correo
        correo_prueba = "tacorreahucke@gmail.com"
        mensaje = MIMEMultipart()
        mensaje["From"] = correo_enviador
        mensaje["To"] = correo_prueba
        mensaje["Subject"] = "NOTIFICACIÓN {}".format(notificacion.tipo)
        mensaje.attach(MIMEText(texto_correo, "plain"))
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(correo_enviador, clave_enviador)
        text = mensaje.as_string()
        session.sendmail(correo_enviador, correo_prueba, text)
        session.quit()


def texto_en_html(usuario):
    texto_html = """<meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
<style>@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:ital,wght@0,400;1,300&display=swap');</style>
<td style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">--</td>
<table style=" margin:0; padding:0 5px 0 0;">
	<tr>
    <!--Columna Logo-->
		<td style=" margin:0; padding:0; vertical-align:top;">
			<a href='http://www.rmc.cl' title="RMC Engineering Solutions" style="border:none; text-decoration:none;">
        <img moz-do-not-send="true" src="http://rmc.cl/signature_img/rmc_engineering.png" alt="" style="border:none; width:59px; height:59px; display:block;">
      </a>
		</td>
    <!--Columna Info + Representacion-->
		<td style="margin:0; padding:0;">
      <table cellspacing='0' cellpadding='0' border-spacing='0' style="padding:0; margin:0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; font-size:12px; mso-line-height-rule:exactly; line-height:11px; color: rgb(33, 33, 33); border-collapse:collapse; -webkit-text-size-adjust:none;">
				<!--Fila Nombre-->
				<tr style="margin:0;padding:0;">
          <td style="margin:0;padding:2px 0 0 0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <strong>
              <a href="mailto:{}" style="border:none; text-decoration:none; color: rgb(33, 33, 33);"><span style="color: rgb(33, 33, 33);">{}</span></a>
            </strong>
          </td>
        </tr>
        <tr style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">
          <td style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">&nbsp;</td>
        </tr>
				<!--Fila cargo-->
        <tr style="margin:0; padding:0;">
          <td style="margin:0; padding:0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <span style="color: rgb(33, 33, 33);"><i>{} - RMC Corporate</i></span>
          </td>
        </tr>
        <tr style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">
          <td style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">&nbsp;</td>
        </tr>
				<!--Fila Direccion-->
        <tr style="margin:0;padding:0;">
          <td style="margin:0;padding:0;font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <span style="color: rgb(33, 33, 33);"><i>Las Cinerarias #550 - Concón</i></span>
          </td>
        </tr>
        <tr style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">
          <td style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">&nbsp;</td>
        </tr>
				<!--Fila Telefono-->
        <tr style="margin:0; padding:0;">
          <td style="margin:0; padding:0; font-family: 'Roboto Condensed', Helvetica, Arial, sans-serif; white-space:nowrap;">
            <span style="color: rgb(33, 33, 33);"><i>C. {} - T.{}</i></span>
          </td>
        </tr>
        <tr style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">
          <td style="height:3px; max-height:3px; font-size:4px; mso-line-height-rule:exactly; line-height:3px;">&nbsp;</td>
        </tr>
				<!--Fila representantes-->
        <tr style="margin:0; padding:0;">
          <td style="margin:0; padding:0; vertical-align:middle;">
              <img moz-do-not-send="true" src="http://rmc.cl/signature_img/empresas_rep.png" alt="" style="border:none; width:280px; display:block;">
      		</td>
        </tr>
      </table>
    </td>
  </tr>
</table>
<td style="height:5px; max-height:5px; font-size:4px; mso-line-height-rule:exactly; line-height:4px;">&nbsp;</td>
""".format(
        usuario.correo,
        usuario.nombre
        + " "
        + usuario.apellido
        + " "
        + usuario.segundo_apellido[0].upper()
        + ".",
        usuario.cargo,
        usuario.celular,
        usuario.telefono,
    )
    return texto_html
