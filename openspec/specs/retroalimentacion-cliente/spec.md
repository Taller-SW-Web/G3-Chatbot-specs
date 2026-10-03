# Retroalimentación del cliente

> Origen: SPEC-24 · Grupo: Transversal · Requiere sesión: Parcial (ver Requisitos) · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`grabacion-pedido`](../grabacion-pedido/spec.md) (SPEC-15), [`notificacion-confirmacion`](../notificacion-confirmacion/spec.md) (SPEC-16), [`adjuntos-imagenes-chat`](../adjuntos-imagenes-chat/spec.md) (SPEC-23), el cambio pendiente `openspec/changes/alinear-specs-con-prototipo` (pantalla "Mi cuenta", aún no aplicado a `inicio-sesion`) · Se relaciona con: Ventas (F5 — CSAT)

## Responsables

- **[completar]:** backend — endpoints propios, integración con Ventas (CSAT), reutilización de `AttachmentStorage`.
- **[completar]:** frontend — pulgares/copiar en el chat, modal de calificación, pantalla de sugerencias.
- **[completar] (QA):** casos de prueba a partir de los escenarios, verificación de que ninguno de los tres mecanismos bloquea el flujo principal si falla.

## Purpose

Darle al cliente tres formas distintas de opinar sobre su experiencia — una respuesta puntual del asistente, la compra que acaba de hacer, y la aplicación en general — sin interrumpir nunca el flujo principal de compra o conversación, y sin inventar almacenamiento propio donde ya existe un dueño (Ventas, para la satisfacción de la compra).

## Contexto

🧩 Esta spec se agrega a partir de tres mockups del equipo (02/10/2026) que unifican tres mecanismos de retroalimentación ya insinuados en otras partes del repo, pero nunca formalizados juntos:

1. **Reacciones rápidas (👍/👎) y copiar**, tras cada bloque de respuesta del asistente. Ya estaba *propuesto* en [`kpis.md` §3](../../docs/conversacion/kpis.md#csat-propuesta-no-está-en-las-specs) y en la [pregunta abierta 9](../../docs/conversacion/README.md#preguntas-abiertas) del repo, pero solo al final de una compra, reclamo o devolución, una vez por sesión. Esta spec **amplía** esa propuesta: al ser íconos persistentes y no un modal, se muestran tras cualquier bloque de respuesta del asistente, no solo al cierre de una tarea. Con esto, la pregunta abierta 9 queda resuelta por esta spec.
2. **Calificación de la compra (estrellas + comentario)**, tras la confirmación del pedido. Esto **es** la encuesta CSAT de Ventas (su F5), que `SPEC-16` había dejado fuera de alcance explícitamente ("Reembolsos: son responsabilidad de F4…" — en su redacción original, la encuesta CSAT no se mencionaba como parte del canal). Ventas ya publicó `POST /api/v2/csat` con `canal: "CHATBOT"` contemplado, así que esta spec la conecta ahí en vez de construir un almacenamiento propio. **Pendiente:** actualizar la sección "Fuera de alcance" de `SPEC-16` para quitar o matizar esa exclusión.
3. **Sugerencia o reporte de bug**, desde la pantalla "Mi cuenta" (sección "Ayúdanos a mejorar"). No tiene dueño en ningún otro módulo — es retroalimentación sobre el canal mismo, no sobre un pedido. Se diseña como una capacidad propia del chatbot, reutilizando el puerto `AttachmentStorage` que ya existe (SPEC-23) para la captura de pantalla opcional, en vez de construir un segundo mecanismo de carga de archivos.

✅ Los mockups usan dos nombres porque son dos cosas distintas, no una inconsistencia: **INKA** es la tienda (la marca que ve el cliente en el encabezado), y **Botleta** es el propio asistente conversacional, ya nombrado y aprobado en [`persona-tono.md`](../../docs/conversacion/persona-tono.md) ("Botleta: bot + atleta"). Por eso el modal de calificación habla en la voz de Botleta ("Tu opinión ayuda a Botleta a mejorar") mientras el encabezado de la app sigue mostrando INKA.

La pantalla "Mi cuenta" desde la que se accede a "Enviar sugerencia / Reportar bug" todavía no es parte de la spec base de `inicio-sesion`: vive en el cambio `openspec/changes/alinear-specs-con-prototipo`, sin aplicar. Si ese cambio se archiva con otro nombre de componente o de ruta, los Requisitos 4 y 5 de esta spec deben ajustarse.

## Alcance

Incluye:
- Reacciones 👍/👎 y "Copiar" tras cada bloque de respuesta del asistente en el chat.
- Modal "Califica tu compra" tras la confirmación del pedido (`CONFIRMACION_PEDIDO`), con estrellas (1 a 5) y comentario opcional, enviado a Ventas.
- Entrada "Ayúdanos a mejorar" en la pantalla "Mi cuenta".
- Formulario "Enviar sugerencia / Reportar bug": tipo (Sugerencia o Bug), título, descripción, correo de contacto prellenado, captura de pantalla opcional.
- Notificación interna al equipo cuando se envía una sugerencia o un bug.
- Límites de uso y tolerancia a fallos de los tres mecanismos, sin bloquear nunca el flujo principal.

### Fuera de alcance

- Edición o eliminación de una reacción ya enviada, o de una calificación ya enviada.
- Esta spec solo registra y notifica por correo (outbox); no hay bandeja ni interfaz de revisión dentro de la app. Cualquier seguimiento posterior con el cliente ocurre por correo, fuera del chat — tal como ya lo anticipa el texto de consentimiento del formulario.
- Las calificaciones de compra (CSAT) tampoco tienen panel propio: viven en Ventas, fuera de este repo.
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

### Requirement: Calificación de la compra (CSAT, vía Ventas)
El sistema DEBE (SHALL) mostrar, después del pago y una vez confirmado el pedido (`CONFIRMACION_PEDIDO`), un modal "Califica tu compra" con estrellas (1 a 5) y un comentario opcional, y DEBE (SHALL) enviar la calificación a Ventas (`POST /api/v2/csat`) en vez de almacenarla en el chatbot.

*Trazabilidad: SPEC-24 · Requisito 2. Conecta con Ventas F5 — CSAT; ver `docs/contratos-integracion.md`.*

#### Scenario: Calificación enviada
- **DADO** un pedido recién pagado y confirmado (`CONFIRMACION_PEDIDO`), con el modal de calificación abierto
- **CUANDO** el cliente toca una cantidad de estrellas y pulsa "Enviar calificación"
- **ENTONCES** se llama a `POST /api/v2/csat {pedidoId, clienteId, canal: "CHATBOT", puntuacion, comentario}`, Ventas responde `201`, y se reemplaza el modal por un agradecimiento breve

#### Scenario: Sin estrellas seleccionadas
- **DADO** el modal de calificación abierto
- **CUANDO** el cliente no ha tocado ninguna estrella
- **ENTONCES** el botón "Enviar calificación" permanece deshabilitado (tal como lo muestra el mockup)

#### Scenario: El cliente lo descarta
- **DADO** el modal de calificación abierto
- **CUANDO** el cliente toca "Ahora no"
- **ENTONCES** el modal se cierra sin enviar nada, y no se vuelve a mostrar para ese mismo pedido

#### Scenario: Encuesta ya registrada para ese pedido
- **DADO** que el cliente ya calificó ese pedido (por este canal o por otro)
- **CUANDO** Ventas responde `409 Conflict`
- **ENTONCES** el modal no se muestra (o, si ya estaba abierto, se cierra con un mensaje breve de "ya calificaste este pedido"), sin mostrarlo como error

#### Scenario: Ventas no disponible al calificar
- **DADO** que `POST /api/v2/csat` no responde
- **CUANDO** el cliente envía su calificación
- **ENTONCES** se informa "No pudimos enviar tu calificación, pero tu pedido ya está confirmado" y el modal se puede cerrar sin reintento automático (no es una operación crítica del flujo de compra)

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
- **ENTONCES** la captura se sube primero mediante el mismo puerto `AttachmentStorage` de SPEC-23 (bucket privado, sin lectura pública), se registra la sugerencia con la referencia al adjunto, y se muestra una confirmación con un código de seguimiento interno

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
- **ENTONCES** se registra igual, con el campo de adjunto vacío

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

## Requisitos no funcionales

- **Privacidad:** la captura de pantalla de un bug nunca se envía al LLM; vive en el mismo bucket privado que las imágenes del chat (SPEC-23), con el mismo tratamiento de URLs firmadas, nunca públicas.
- **No bloqueante:** ninguno de los tres mecanismos puede impedir ni demorar el flujo principal (conversar, pagar, ver el pedido). Todos los fallos de registro se degradan en silencio o con un mensaje breve, nunca con un bloqueo.
- **Rendimiento:** registrar una reacción, p95 ≤ 400 ms; enviar la calificación a Ventas, p95 ≤ 1 s; registrar una sugerencia (sin captura), p95 ≤ 1 s.
- **Idempotencia:** el envío de una calificación usa `pedidoId` como clave natural (Ventas ya responde `409` ante duplicados); el envío de una sugerencia usa una `Idempotency-Key` igual que el resto de operaciones que crean algo (ver convención general del repo).
- **Retención:** la captura de un bug sigue la misma política de retención que las imágenes del chat (SPEC-23 · pregunta abierta 10, todavía sin plazo fijado).

## Preguntas abiertas

1. 🟡 **¿La calificación requiere un scope nuevo de Seguridad?** El contrato de Ventas no documenta `security`/scopes por endpoint con el mismo detalle que Productos o Despacho — su sección 2.7 (CSAT) no tiene el bloque `Authorization` que sí tienen otras secciones del mismo contrato. **Por verse:** se abrió un issue en `Taller-SW-Web/G5-Ventas-Postventas` pidiendo que lo documenten; esta pregunta queda abierta hasta que respondan.

✅ **Resueltas con el equipo (02/10/2026):**
- INKA es la tienda y Botleta es el asistente: no hay conflicto de marca (ver "Contexto").
- La calificación de compra es un modal que aparece después de pagar, una vez confirmado el pedido.
- La bandeja de sugerencias/bugs no tiene panel propio: solo se registra, y el seguimiento posterior con el cliente es por correo (ver "Fuera de alcance").
- Los pulgares 👍/👎 sí se muestran tras cada bloque de respuesta del asistente, no solo al cierre de una tarea — se confirma el alcance ampliado respecto a la propuesta original de `kpis.md`. La pregunta abierta 9 de `docs/conversacion/README.md` queda completamente resuelta por esta spec.

## Criterio de completitud

- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- `SPEC-16` fue actualizada para reflejar que el CSAT ya no está fuera de alcance.
- La pregunta abierta 9 de `docs/conversacion/README.md` queda marcada como resuelta, enlazando a esta spec.
- No se han incorporado funcionalidades fuera del alcance.
