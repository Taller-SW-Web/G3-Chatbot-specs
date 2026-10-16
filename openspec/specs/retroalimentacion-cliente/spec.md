# Retroalimentación del cliente

> Origen: SPEC-24 · Grupo: Transversal · Requiere sesión: Parcial (ver Requisitos) · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`grabacion-pedido`](../grabacion-pedido/spec.md) (SPEC-15), [`notificacion-confirmacion`](../notificacion-confirmacion/spec.md) (SPEC-16), [`adjuntos-imagenes-chat`](../adjuntos-imagenes-chat/spec.md) (SPEC-23, solo el puerto `AttachmentStorage`; no su tabla `attachment`), el cambio pendiente `openspec/changes/alinear-specs-con-prototipo` (pantalla "Mi cuenta", aún no aplicado a `inicio-sesion`) · Se relaciona con: Ventas (F5 — CSAT)

## Responsables

- **[completar]:** backend — endpoints propios, integración con Ventas (CSAT), reutilización de `AttachmentStorage`.
- **[completar]:** frontend — pulgares/copiar en el chat, modal de calificación, pantalla de sugerencias.
- **[completar] (QA):** casos de prueba a partir de los escenarios, verificación de que ninguno de los tres mecanismos bloquea el flujo principal si falla.

## Purpose

Darle al cliente tres formas distintas de opinar sobre su experiencia — una respuesta puntual del asistente, la compra que acaba de hacer, y la aplicación en general — sin interrumpir nunca el flujo principal de compra o conversación, y sin inventar almacenamiento propio donde ya existe un dueño (Ventas, para la satisfacción de la compra).

## Contexto

🧩 Esta spec se agrega a partir de tres mockups del equipo (02/10/2026) que unifican tres mecanismos de retroalimentación ya insinuados en otras partes del repo, pero nunca formalizados juntos:

1. **Reacciones rápidas (👍/👎) y copiar**, tras cada bloque de respuesta del asistente. Ya estaba *propuesto* en [`kpis.md` §3](../../docs/conversacion/kpis.md#csat-propuesta-no-está-en-las-specs) y en la [pregunta abierta 9](../../docs/conversacion/README.md#preguntas-abiertas) del repo, pero solo al final de una compra, reclamo o devolución, una vez por sesión. Esta spec **amplía** esa propuesta: al ser íconos persistentes y no un modal, se muestran tras cualquier bloque de respuesta del asistente, no solo al cierre de una tarea. Con esto, la pregunta abierta 9 queda resuelta por esta spec.
2. **Calificación del pedido (caritas + comentario)**, al pie del detalle de un pedido `ENTREGADO`, más una **valoración de la experiencia de compra** (popup con estrellas, tras el pago, propia del chatbot). La calificación del pedido **es** la encuesta CSAT de Ventas (su F5), que `SPEC-16` había dejado fuera de alcance explícitamente ("Reembolsos: son responsabilidad de F4…" — en su redacción original, la encuesta CSAT no se mencionaba como parte del canal). Ventas ya publicó `POST /api/v2/csat` con `canal: "CHATBOT"` contemplado, así que esta spec la conecta ahí en vez de construir un almacenamiento propio. **Pendiente:** actualizar la sección "Fuera de alcance" de `SPEC-16` para quitar o matizar esa exclusión.
3. **Sugerencia o reporte de bug**, desde la pantalla "Mi cuenta" (sección "Ayúdanos a mejorar"). No tiene dueño en ningún otro módulo — es retroalimentación sobre el canal mismo, no sobre un pedido. Se diseña como una capacidad propia del chatbot, reutilizando el puerto `AttachmentStorage` que ya existe (SPEC-23) para la captura de pantalla opcional, en vez de construir un segundo mecanismo de carga de archivos.

✅ Los mockups usan dos nombres porque son dos cosas distintas, no una inconsistencia: **INKA** es la tienda (la marca que ve el cliente en el encabezado), y **Botleta** es el propio asistente conversacional, ya nombrado y aprobado en [`persona-tono.md`](../../docs/conversacion/persona-tono.md) ("Botleta: bot + atleta"). Por eso el modal de calificación habla en la voz de Botleta ("Tu opinión ayuda a Botleta a mejorar") mientras el encabezado de la app sigue mostrando INKA.

La pantalla "Mi cuenta" desde la que se accede a "Enviar sugerencia / Reportar bug" todavía no es parte de la spec base de `inicio-sesion`: vive en el cambio `openspec/changes/alinear-specs-con-prototipo`, sin aplicar. Si ese cambio se archiva con otro nombre de componente o de ruta, los Requisitos 4 y 5 de esta spec deben ajustarse.

## Alcance

Incluye:
- Reacciones 👍/👎 y "Copiar" tras cada bloque de respuesta del asistente en el chat.
- Calificación del pedido al pie del detalle de un pedido `ENTREGADO`: tres caritas (1, 3, 5) y comentario opcional, enviada a Ventas. No es un modal.
- Valoración de la experiencia de compra: popup "Califica tu compra" tras el pago, con estrellas (1 a 5) y comentario opcional, guardada en el chatbot (no va a Ventas).
- Entrada "Ayúdanos a mejorar" en la pantalla "Mi cuenta".
- Formulario "Enviar sugerencia / Reportar bug": tipo (Sugerencia o Bug), título, descripción, correo de contacto prellenado, captura de pantalla opcional.
- Notificación interna al equipo cuando se envía una sugerencia o un bug.
- Límites de uso y tolerancia a fallos de los tres mecanismos, sin bloquear nunca el flujo principal.

### Fuera de alcance

- Eliminación de una reacción ya enviada (cambiarla de 👍 a 👎 o al revés sí está incluido, ver Requisito 1), y edición o eliminación de una calificación ya enviada.
- Esta spec solo registra y notifica por correo (outbox); no hay bandeja ni interfaz de revisión dentro de la app. Cualquier seguimiento posterior con el cliente ocurre por correo, fuera del chat — tal como ya lo anticipa el texto de consentimiento del formulario.
- La calificación del pedido (CSAT) no tiene panel propio: vive en Ventas, fuera de este repo. La valoración de la experiencia de compra se guarda en `purchase_rating`, sin interfaz de revisión en la app.
- Pedir la calificación de forma proactiva cuando el pedido se entrega: el chatbot no recibe aviso de entrega; se ofrece solo cuando el cliente abre el pedido.
- Encuestas periódicas o proactivas (NPS, encuestas por correo fuera de una compra): no están en los mockups revisados.

## Requirements

### Requirement: Reacciones rápidas tras un bloque de respuesta
El sistema DEBE (SHALL) mostrar, debajo de cada bloque de respuesta del asistente (texto, carrusel, o la combinación de ambos en un mismo turno), los controles 👍, 👎 y "Copiar", y DEBE (SHALL) registrar la reacción sin interrumpir la conversación.

*Trazabilidad: SPEC-24 · Requisito 1. Resuelve la pregunta abierta 9 de `docs/conversacion/README.md`, ampliándola a cualquier bloque de respuesta, no solo al cierre de una tarea.*

#### Scenario: Reacción positiva
- **DADO** un bloque de respuesta del asistente ya renderizado
- **CUANDO** el cliente toca 👍
- **ENTONCES** el ícono queda marcado como seleccionado, se registra la reacción ligada al `mensaje_id` y al `cliente_id` o `chat_sid`, y no se interrumpe la conversación

#### Scenario: Cambiar de reacción
- **DADO** un bloque ya marcado con 👍
- **CUANDO** el cliente toca 👎
- **ENTONCES** la reacción se actualiza a 👎 (no se acumulan ambas) y se registra el cambio

#### Scenario: Copiar el texto de la respuesta
- **DADO** un bloque de respuesta con texto
- **CUANDO** el cliente toca "Copiar"
- **ENTONCES** el texto plano del bloque (sin los datos de las tarjetas estructuradas) se copia al portapapeles del dispositivo, y se confirma con un cambio breve del ícono; no se envía al backend ni se registra como reacción

#### Scenario: Registro falla
- **DADO** que el backend no responde al registrar una reacción
- **CUANDO** el cliente toca 👍 o 👎
- **ENTONCES** el ícono se marca igual en el cliente (optimista) y el reintento del registro ocurre en segundo plano, sin mostrar error ni bloquear el chat

### Requirement: Acceso a retroalimentación desde "Mi cuenta"
El sistema DEBE (SHALL) mostrar en la pantalla "Mi cuenta" una sección "Ayúdanos a mejorar" con el botón "Enviar sugerencia / Reportar bug".

*Trazabilidad: SPEC-24 · Requisito 3. Depende de la pantalla "Mi cuenta" definida en el cambio `alinear-specs-con-prototipo` (aún sin aplicar a `inicio-sesion`).*

#### Scenario: Entrada visible para cualquier cliente autenticado
- **DADO** un cliente autenticado en "Mi cuenta"
- **CUANDO** la pantalla carga
- **ENTONCES** se muestra la sección "Ayúdanos a mejorar" con el botón, sin condición adicional (no depende de tener pedidos ni verificaciones previas)

### Requirement: Formulario de sugerencia o reporte de bug
El sistema DEBE (SHALL) permitir enviar una sugerencia o un reporte de error con tipo, título (mínimo 3 caracteres), descripción (mínimo 6, máximo 1000 caracteres), correo de contacto prellenado y editable, y una captura de pantalla opcional.

*Trazabilidad: SPEC-24 · Requisito 4.*

#### Scenario: Envío válido con captura
- **DADO** el formulario con tipo "Bug", título "No carga el carrito", descripción de 40 caracteres y una captura `.png` de 2 MB adjunta
- **CUANDO** el cliente pulsa "Enviar"
- **ENTONCES** la captura se sube primero mediante el mismo puerto `AttachmentStorage` de SPEC-23 (bucket privado, sin lectura pública), se registra la sugerencia con la clave de la captura (`screenshot_key`), y se muestra una confirmación con un código de seguimiento interno

#### Scenario: Campos obligatorios incompletos
- **DADO** un título de 2 caracteres o una descripción de 5 caracteres
- **CUANDO** el cliente intenta enviar
- **ENTONCES** el botón "Enviar" permanece deshabilitado y se muestra el texto de ayuda ("Completa el título (mín. 3) y la descripción (mín. 6) para activar Enviar"), igual que en el mockup

#### Scenario: Captura inválida
- **DADO** un archivo de más de 5 MB o que no es `image/jpeg` ni `image/png`
- **CUANDO** el cliente intenta adjuntarlo
- **ENTONCES** se rechaza en el cliente con un mensaje breve, sin impedir enviar el formulario sin captura

#### Scenario: Envío sin captura
- **DADO** un formulario válido sin ninguna imagen adjunta
- **CUANDO** el cliente pulsa "Enviar"
- **ENTONCES** se registra igual, sin clave de captura (`screenshot_key` nula)

#### Scenario: Backend no disponible al enviar
- **DADO** que el registro falla
- **CUANDO** el cliente pulsa "Enviar"
- **ENTONCES** se muestra "No pudimos enviar tu sugerencia, intenta de nuevo" y el formulario conserva lo escrito (salvo la captura, que debe adjuntarse de nuevo)

### Requirement: Notificación interna de sugerencias y bugs
El sistema DEBE (SHALL) notificar al equipo cuando se registra una sugerencia o un bug, reutilizando el mismo adaptador de correo de SPEC-16.

*Trazabilidad: SPEC-24 · Requisito 5.*

#### Scenario: Notificación enviada
- **DADO** una sugerencia o un bug recién registrado
- **CUANDO** se procesa el envío
- **ENTONCES** se encola un correo interno (dirección configurable) con el tipo, el título, la descripción, el correo de contacto del cliente y el enlace a la captura (si existe), usando el mismo `EmailSender`/outbox de SPEC-16

#### Scenario: Falla el envío del correo interno
- **DADO** que el correo interno falla
- **CUANDO** se reintenta (mismo mecanismo de outbox de SPEC-16)
- **ENTONCES** la sugerencia o el bug ya registrados no se pierden ni se marcan como fallidos frente al cliente; solo falla la notificación interna

### Requirement: Límites de uso de los tres mecanismos
El sistema DEBE (SHALL) limitar el envío de reacciones, calificaciones y sugerencias para evitar abuso, sin afectar el uso normal.

*Trazabilidad: SPEC-24 · Requisito 6.*

#### Scenario: Exceso de reacciones
- **DADO** un cliente o `chat_sid` que envía más de 30 reacciones en 1 minuto
- **CUANDO** intenta enviar otra
- **ENTONCES** se ignora en silencio (no se muestra error, es un límite anti-abuso, no una validación de negocio)

#### Scenario: Exceso de sugerencias
- **DADO** un cliente con 5 sugerencias o bugs enviados en 1 hora
- **CUANDO** intenta enviar otro
- **ENTONCES** se muestra "Ya enviaste varias sugerencias, intenta en un rato" y no se registra

### Requirement: Calificación de la entrega con caritas (CSAT, vía Ventas)
El sistema DEBE (SHALL) ofrecer la calificación del pedido (CSAT de Ventas) en un bloque fijo al pie del detalle de un pedido `ENTREGADO`, no en una ventana emergente, con tres caritas (feliz, neutral, triste) y un comentario opcional, y DEBE (SHALL) enviarla a Ventas (`POST /api/v2/csat`) en vez de almacenarla como calificación propia.

*Trazabilidad: SPEC-24 · Requisito 2. Ventas F5 — CSAT (`docs/contratos-integracion.md`); solo acepta pedidos `ENTREGADO`.*

#### Scenario: Calificación enviada
- **DADO** el detalle de un pedido `ENTREGADO` que el cliente no ha calificado
- **CUANDO** el cliente toca una carita y pulsa "Enviar calificación"
- **ENTONCES** se llama a `POST /api/v2/csat {pedidoId, clienteId, canal: "CHATBOT", puntuacion, comentario}`, con el `clienteId` igual al `sub` del token del cliente y `puntuacion` 5 (feliz), 3 (neutral) o 1 (triste), la escala acordada por Ventas con Marketplace; Ventas responde `201`, y el bloque se reemplaza por el agradecimiento "¡Gracias por tu calificación!"

#### Scenario: Sin carita seleccionada
- **DADO** el bloque de calificación visible al pie del detalle del pedido
- **CUANDO** el cliente no ha tocado ninguna de las tres caritas
- **ENTONCES** el botón "Enviar calificación" permanece deshabilitado hasta que elija una carita

#### Scenario: El cliente lo descarta
- **DADO** el bloque de calificación visible
- **CUANDO** el cliente no responde y sale de la pantalla
- **ENTONCES** no se envía nada, no se marca como calificado y el bloque vuelve a aparecer la próxima vez que abra ese pedido

#### Scenario: Encuesta ya registrada para ese pedido
- **DADO** que el cliente ya calificó ese pedido (por este canal o por otro)
- **CUANDO** Ventas responde `409 CSAT_ALREADY_SUBMITTED`
- **ENTONCES** el bloque se reemplaza por "Ya calificaste este pedido", sin mostrarlo como error, y se marca `order_ref.csat_sent`

#### Scenario: Ventas no disponible al calificar
- **DADO** que `POST /api/v2/csat` no responde
- **CUANDO** el cliente envía su calificación
- **ENTONCES** se informa "No pudimos enviar tu calificación, intenta de nuevo más tarde" y el bloque se conserva para reintentar; el detalle del pedido sigue usable

#### Scenario: El pedido no es del cliente
- **DADO** que Ventas responde `403` porque el `sub` del token no es el dueño del pedido
- **CUANDO** el cliente envía su calificación
- **ENTONCES** se muestra el error genérico "No pudimos enviar tu calificación, intenta de nuevo" y el bloque se conserva

#### Scenario: Pedido no entregado según Ventas
- **DADO** que Ventas responde `422 ORDER_NOT_DELIVERED` al enviar la calificación
- **CUANDO** el cliente envía su calificación
- **ENTONCES** el bloque se oculta y se refresca el detalle del pedido para mostrar su estado vigente

#### Scenario: Pedido aún no entregado
- **DADO** el detalle de un pedido en `CREADO`, `PAGADO`, `EN_PREPARACION` o `DESPACHADO`
- **CUANDO** se muestra la pantalla
- **ENTONCES** el bloque de calificación no aparece

### Requirement: Valoración de la experiencia de compra (propia del chatbot)
El sistema DEBE (SHALL) mostrar, después del pago y una vez confirmado el pedido, un popup "Califica tu compra" con estrellas (1 a 5) y comentario opcional, y DEBE (SHALL) guardar la valoración en el propio chatbot, sin enviarla a Ventas. No bloquea la confirmación del pedido.

*Trazabilidad: SPEC-24 · Requisito 7. Complementa el Requisito 2: esta valoración mide la experiencia de comprar en el chat; la del Requisito 2 mide el pedido recibido.*

#### Scenario: Valoración enviada
- **DADO** un pedido recién pagado y confirmado, con el popup abierto
- **CUANDO** el cliente toca una cantidad de estrellas y pulsa "Enviar calificación"
- **ENTONCES** se guarda `purchase_rating` con el pedido, el cliente, las estrellas (1 a 5) y el comentario, y el popup se reemplaza por el agradecimiento "¡Gracias por tu calificación!"

#### Scenario: Sin estrellas seleccionadas
- **DADO** el popup abierto
- **CUANDO** el cliente no ha tocado ninguna estrella
- **ENTONCES** el botón "Enviar calificación" permanece deshabilitado

#### Scenario: El cliente lo descarta
- **DADO** el popup abierto
- **CUANDO** el cliente toca "Ahora no"
- **ENTONCES** el popup se cierra sin guardar nada y no se vuelve a mostrar para ese mismo pedido en ese navegador. El descarte se recuerda por pedido en el navegador (LocalStorage, con `orderId` como clave), es por dispositivo por diseño y no se guarda en el backend; si se borra el almacenamiento o se abre en otro dispositivo, el popup puede volver a mostrarse

#### Scenario: Una sola valoración por pedido
- **DADO** un pedido con valoración de compra ya guardada
- **CUANDO** se vuelve a mostrar su confirmación
- **ENTONCES** el popup no aparece y no admite una segunda valoración

#### Scenario: Falla el guardado
- **DADO** que el backend no responde al guardar la valoración
- **CUANDO** el cliente pulsa "Enviar calificación"
- **ENTONCES** se muestra "No pudimos guardar tu opinión" y la confirmación del pedido sigue visible y sin cambios

## Requisitos no funcionales

- **Privacidad:** la captura de pantalla de un bug nunca se envía al LLM; vive en el mismo bucket privado que las imágenes del chat (SPEC-23), con el mismo tratamiento de URLs firmadas, nunca públicas. Se guarda como una clave de objeto propia de SPEC-24 (`feedback_suggestion.screenshot_key`), con la misma validación de tipo y tamaño del puerto; no usa la tabla `attachment`.
- **No bloqueante:** ninguno de los tres mecanismos puede impedir ni demorar el flujo principal (conversar, pagar, ver el pedido). Todos los fallos de registro se degradan en silencio o con un mensaje breve, nunca con un bloqueo.
- **Rendimiento:** registrar una reacción, p95 ≤ 400 ms; enviar la calificación a Ventas, p95 ≤ 1 s; registrar una sugerencia (sin captura), p95 ≤ 1 s.
- **Idempotencia:** el envío de la calificación del pedido usa `pedidoId` como clave natural (Ventas ya responde `409` ante duplicados); la valoración de la compra es única por pedido; el envío de una sugerencia usa una `Idempotency-Key` igual que el resto de operaciones que crean algo (ver convención general del repo).
- **Retención:** la captura de un bug sigue la misma política de retención que las imágenes del chat (SPEC-23 · pregunta abierta 10, todavía sin plazo fijado).

## Preguntas abiertas

1. ✅ **¿La calificación requiere un scope nuevo de Seguridad?** **Resuelta por Ventas (12/10/2026, acuerdo A15 en `docs/contratos-integracion.md`):** no requiere scope. `POST /api/v2/csat` se llama con el token del cliente (rol `CLIENTE`); Ventas valida el `sub` del JWT contra el dueño del `pedidoId` y responde `403` si no coincide. El scope `postventa:csat:escribir` no existe y no se solicita.

✅ **Resueltas con el equipo (02/10/2026):**
- INKA es la tienda y Botleta es el asistente: no hay conflicto de marca (ver "Contexto").
- ~~La calificación de compra es un modal que aparece después de pagar.~~ **Reemplazado (11/10/2026):** Ventas solo acepta calificar pedidos `ENTREGADO`, así que hay dos momentos: valoración de la compra (local, popup con estrellas) tras el pago, y calificación del pedido (Ventas, bloque al pie con caritas) en el detalle de un pedido entregado.
- La bandeja de sugerencias/bugs no tiene panel propio: solo se registra, y el seguimiento posterior con el cliente es por correo (ver "Fuera de alcance").
- Los pulgares 👍/👎 sí se muestran tras cada bloque de respuesta del asistente, no solo al cierre de una tarea — se confirma el alcance ampliado respecto a la propuesta original de `kpis.md`. La pregunta abierta 9 de `docs/conversacion/README.md` queda completamente resuelta por esta spec.

## Criterio de completitud

- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- `SPEC-16` fue actualizada para reflejar que el CSAT ya no está fuera de alcance.
- La pregunta abierta 9 de `docs/conversacion/README.md` queda marcada como resuelta, enlazando a esta spec.
- No se han incorporado funcionalidades fuera del alcance.
