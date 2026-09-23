# Notificación de confirmación por correo

> Origen: SPEC-16 · Grupo: Checkout · Requiere sesión: Sí (compra) · Depende de: [`grabacion-pedido`](../grabacion-pedido/spec.md) (SPEC-15)

## Purpose

Enviar al cliente, una sola vez por pedido, un correo con el detalle de su compra confirmada y el camino para hacerle seguimiento.

## Contexto

El curso exige al Chatbot "notificaciones por correo del pedido al cliente". Despacho declara fuera de su alcance la notificación al cliente final y la asigna a los canales y a Ventas. El chatbot envía, por lo tanto, el correo de confirmación de las compras hechas en su canal.

El cliente puede cerrar el chat justo después de pagar, así que el correo es su constancia fuera de la conversación.

## Alcance

Incluye:
- Disparo del correo cuando Ventas acepta la notificación `PAGADO` (SPEC-15).
- Plantilla HTML responsive con versión de texto plano.
- Contenido: número de pedido, fecha, líneas (nombre, variante, cantidad y precio), descuentos, cupón, envío, total, tarjeta enmascarada, dirección de entrega, plazo estimado y enlace al chat ("Consultar estado").
- Envío asíncrono con reintentos e idempotencia por pedido.

### Fuera de alcance

- Correos por los cambios de estado posteriores (despachado, entregado): requerirían consumir eventos de Ventas (mejora futura).
- Encuesta de satisfacción: es F5 de Ventas.
- SMS o notificaciones push.

## Requirements

### Requirement: Envío de la confirmación
El sistema DEBE (SHALL) encolar y enviar el correo de confirmación al correo de la cuenta cuando el pedido pasa a `PAGADO_NOTIFICADO`.

*Trazabilidad: SPEC-16 · Requisito 1.*

#### Scenario: Correo enviado
- **DADO** un pedido con el pago notificado a Ventas
- **CUANDO** el worker procesa `ENVIAR_CORREO`
- **ENTONCES** se envía a `maria@ejemplo.com` el asunto "Confirmamos tu pedido PED-2026-00891" con el detalle completo, y `notificacion` queda en `ENVIADA`

#### Scenario: Contenido fiel al pedido
- **DADO** un pedido con cupón y envío
- **CUANDO** se renderiza la plantilla
- **ENTONCES** los importes coinciden exactamente con el snapshot enviado a Ventas y la tarjeta aparece como "Visa •••• 1111"

### Requirement: Idempotencia y reintentos
El sistema DEBE (SHALL) enviar como máximo un correo de confirmación por pedido y reintentar ante fallos del proveedor.

*Trazabilidad: SPEC-16 · Requisito 2.*

#### Scenario: Reproceso del evento
- **DADO** un correo ya `ENVIADA` para el pedido
- **CUANDO** el worker recibe otra vez la tarea
- **ENTONCES** no se envía un segundo correo (clave única `pedido_id + tipo`)

#### Scenario: Proveedor SMTP caído
- **DADO** que el SMTP falla
- **CUANDO** se intenta el envío
- **ENTONCES** se reintenta hasta 3 veces (1 min, 5 min y 15 min); si falla, queda `FALLIDA` con `ultimo_error`, y el pedido y el chat no se ven afectados

### Requirement: El correo no bloquea la compra
El sistema DEBE (SHALL) confirmar la compra en el chat aunque el correo falle o se demore.

*Trazabilidad: SPEC-16 · Requisito 3.*

#### Scenario: Confirmación en el chat sin correo
- **DADO** un pedido confirmado con el correo aún pendiente
- **CUANDO** se muestra `CONFIRMACION_PEDIDO`
- **ENTONCES** el mensaje dice "Te enviaremos la confirmación a m****a@…", sin prometer que ya llegó

#### Scenario: El cliente pide reenviar el correo
- **DADO** un pedido con el correo `ENVIADA` o `FALLIDA`
- **CUANDO** el cliente escribe "no me llegó el correo"
- **ENTONCES** se sugiere revisar spam y se ofrece "Reenviar", que crea un reenvío (máx. 2 por pedido, tipo `REENVIO_CONFIRMACION`)

## Requisitos no funcionales

- **Seguridad:** credenciales SMTP en variables de entorno; remitente con SPF y DKIM configurados en el dominio del despliegue (en desarrollo se usa Mailtrap).
- **Privacidad:** el correo no incluye el documento ni el celular completo; la dirección solo se incluye porque es del propio cliente.
- **Compatibilidad:** la plantilla se prueba en Gmail y Outlook (web y móvil); ancho máximo de 600 px; estilos en línea.
- **Rendimiento:** el correo se envía dentro de los 60 s posteriores a la confirmación en el 95 % de los casos.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
