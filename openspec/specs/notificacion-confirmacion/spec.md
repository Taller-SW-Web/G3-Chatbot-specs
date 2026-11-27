# Notificación de confirmación por correo

> Origen: SPEC-16 · Grupo: Checkout · Requiere sesión: Sí (compra) · Depende de: [`grabacion-pedido`](../grabacion-pedido/spec.md) (SPEC-15)

## Responsables

- **David:** `EmailSender`, plantillas y tarea `SEND_EMAIL` en el outbox.
- **Sonny:** outbox que ejecuta la tarea.
- **Nikol (QA):** casos de prueba a partir de los escenarios, pruebas E2E si el flujo es crítico y validación contra la definición de terminado.

## Purpose

Enviar al cliente, una sola vez por pedido, un correo con el detalle de su compra confirmada y el camino para hacerle seguimiento.

## Contexto

El curso exige al Chatbot "notificaciones por correo del pedido al cliente". Despacho declara fuera de su alcance la notificación al cliente final y la asigna a los canales y a Ventas. El chatbot envía, por lo tanto, el correo de confirmación de las compras hechas en su canal.

El cliente puede cerrar el chat justo después de pagar, así que el correo es su constancia fuera de la conversación.

## Alcance

Incluye:
- Disparo del correo solo cuando Ventas responde la notificación del pago con `nuevoEstado: PAGADO` (SPEC-15); si responde `ANULADO`, no se envía confirmación.
- Plantilla HTML responsive con versión de texto plano.
- Contenido: número de pedido, fecha, líneas (nombre, variante, cantidad y precio), descuentos, cupón, envío, total, tarjeta enmascarada, dirección de entrega, plazo estimado y enlace al chat ("Consultar estado").
- Envío asíncrono con reintentos e idempotencia por pedido.

### Fuera de alcance

- Correos por los cambios de estado posteriores (despachado, entregado): requerirían consumir eventos de Ventas (mejora futura).
- Encuesta de satisfacción: la calificación de la entrega (CSAT de Ventas, F5) vive en [`retroalimentacion-cliente`](../retroalimentacion-cliente/spec.md) (SPEC-24), en el detalle del pedido entregado, y no se envía por correo.
- SMS o notificaciones push.

## Requirements

### Requirement: Envío de la confirmación
El sistema DEBE (SHALL) encolar y enviar el correo de confirmación al correo de la cuenta solo cuando Ventas responde la notificación del pago con `nuevoEstado: PAGADO` y el pedido pasa a `PAID_NOTIFIED`. El encolado lo hace el worker de outbox al procesar `NOTIFY_SALES_PAYMENT`, no el checkout, y es idempotente ante una reentrega de la tarea. Si Ventas responde `ANULADO` (pago tardío sobre un pedido anulado, por ejemplo por falta de stock), el sistema NO DEBE (SHALL NOT) enviar la confirmación.

*Trazabilidad: SPEC-16 · Requisito 1; SPEC-15 · Requisito 2; backend#182.*

#### Scenario: Correo enviado
- **DADO** un pedido con el pago notificado a Ventas
- **CUANDO** el worker procesa `SEND_EMAIL`
- **ENTONCES** se envía a `maria@ejemplo.com` el asunto "Confirmamos tu pedido PED-2026-00891" con el detalle completo, y `notification` queda en `SENT`

#### Scenario: Ventas anula el pedido tras el pago
- **DADO** un pago aprobado notificado sobre un pedido que Ventas ya anuló (pago tardío)
- **CUANDO** Ventas responde `200 {nuevoEstado: ANULADO}`
- **ENTONCES** el pedido pasa a `CANCELLED`, no se encola ni se envía el correo de confirmación y el cliente consulta la anulación y el reembolso en el estado del pedido (SPEC-17)

#### Scenario: Reentrega de la notificación del pago
- **DADO** una tarea `NOTIFY_SALES_PAYMENT` que se procesa otra vez y cuya respuesta vuelve a ser `nuevoEstado: PAGADO`
- **CUANDO** el worker intenta encolar la confirmación
- **ENTONCES** no se crea una segunda notificación, porque ya existe `(order_id, 0)`

#### Scenario: Contenido fiel al pedido
- **DADO** un pedido con cupón y envío
- **CUANDO** se renderiza la plantilla
- **ENTONCES** los importes coinciden exactamente con el snapshot enviado a Ventas y la tarjeta aparece como "Visa •••• 1111"

### Requirement: Idempotencia y reintentos
El sistema DEBE (SHALL) enviar como máximo un correo de confirmación por pedido y reintentar ante fallos del proveedor.

*Trazabilidad: SPEC-16 · Requisito 2.*

#### Scenario: Reproceso del evento
- **DADO** un correo ya `SENT` para el pedido
- **CUANDO** el worker recibe otra vez la tarea
- **ENTONCES** no se envía un segundo correo (clave única `(order_id, resend_number)`)

#### Scenario: Proveedor SMTP caído
- **DADO** que el SMTP falla
- **CUANDO** se intenta el envío
- **ENTONCES** se reintenta hasta 3 veces (1 min, 5 min y 15 min); si falla, queda `FAILED` con `last_error`, y el pedido y el chat no se ven afectados

### Requirement: El correo no bloquea la compra
El sistema DEBE (SHALL) confirmar la compra en el chat aunque el correo falle o se demore.

*Trazabilidad: SPEC-16 · Requisito 3.*

#### Scenario: Confirmación en el chat sin correo
- **DADO** un pedido confirmado por Ventas (`PAGADO`) con el correo aún pendiente
- **CUANDO** se muestra `CONFIRMACION_PEDIDO`
- **ENTONCES** el mensaje dice "Te enviaremos la confirmación a m****a@…", sin prometer que ya llegó; mientras Ventas no responda, el cliente ve "Pago recibido. Estamos confirmando tu pedido y te avisaremos por correo." (SPEC-14, Requisito 7)

#### Scenario: El cliente pide reenviar el correo
- **DADO** un pedido con el correo `SENT` o `FAILED`
- **CUANDO** el cliente escribe "no me llegó el correo"
- **ENTONCES** se sugiere revisar spam y se ofrece "Reenviar", que crea un reenvío (máx. 2 por pedido, tipo `CONFIRMATION_RESEND`)

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
