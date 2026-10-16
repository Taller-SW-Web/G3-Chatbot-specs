# Propuestas de UX: retroalimentación del cliente

> Pendiente de la tarea H2-08 de [`odd/tasks/hito-2.md`](../odd/tasks/hito-2.md). Documenta las tres interacciones con las que el cliente opina sobre su experiencia, tal como las define SPEC-24 ([`retroalimentacion-cliente`](../openspec/specs/retroalimentacion-cliente/spec.md) y su [`design.md`](../openspec/specs/retroalimentacion-cliente/design.md)). No agrega comportamiento: si algo cambia, se cambia primero en la spec.

Diseño visual: [archivo de Figma del chatbot](https://www.figma.com/design/RjFXUJR82LQ2vSd6UP2xEj/Chatbot). SPEC-24 no referencia nodos concretos de Figma, por eso se enlaza el archivo general. Los tokens, componentes y reglas de accesibilidad citados abajo están en [`docs/design-system.md`](design-system.md).

**Fuente de las propuestas 2 y 3.** El `spec.md` base de SPEC-24 todavía describe el Requisito 2 con su redacción anterior: un modal de estrellas tras el pago que se envía a Ventas. El cambio [`ajustar-calificacion-compra-y-entrega`](../openspec/changes/ajustar-calificacion-compra-y-entrega/specs/retroalimentacion-cliente/spec.md), aún sin archivar, separa esa calificación en dos:

- el Requisito 2 modificado, con las caritas al pie del pedido `ENTREGADO`;
- un Requisito 7 nuevo, con el popup de estrellas que se guarda en el chatbot.

El `design.md`, el Alcance y las preguntas resueltas del `spec.md` ya siguen esa separación. Este documento también la sigue y cita los escenarios de ese cambio.

| # | Propuesta | Componente (`design.md`) | Destino del dato | Requisito |
|---|---|---|---|---|
| 1 | Reacción 👍/👎 a una respuesta del asistente | `MessageFeedback` + `useReaction` | Chatbot, tabla `message_reaction` | SPEC-24 · Requisito 1 |
| 2 | Calificación de la entrega (caritas 5/3/1) | `DeliveryRatingFooter` | Ventas, `POST /api/v2/csat` | SPEC-24 · Requisito 2 (modificado) |
| 3 | Valoración de la propia compra (estrellas 1 a 5) | `PurchaseRatingModal` | Chatbot, tabla `purchase_rating` | SPEC-24 · Requisito 7 (nuevo) |

Reglas comunes a las tres:

- **No bloquean el flujo principal.** Ninguna puede impedir ni demorar conversar, pagar o ver el pedido. Los fallos se degradan en silencio o con un mensaje breve, nunca con un bloqueo (requisito no funcional "No bloqueante").
- **No se editan ni se eliminan.** Una calificación ya enviada no se edita ni se elimina (Fuera de alcance). La reacción es la excepción, porque la spec permite cambiarla (propuesta 1).

---

## 1. Reacción 👍/👎 a una respuesta del asistente

**Objetivo.** Saber si una respuesta concreta del asistente le sirvió al cliente, sin interrumpir la conversación (Purpose de SPEC-24).

**Dónde y cuándo.**
- **Dónde:** en el chat, debajo de cada bloque de respuesta del asistente: texto, carrusel o la combinación de ambos en un mismo turno. La fila tiene tres controles: 👍, 👎 y "Copiar".
- **Cuándo:** después de cualquier bloque de respuesta, no solo al cierre de una tarea. Son íconos persistentes, no un modal.
- **Sesión:** no exige sesión. La reacción se liga al `cliente_id` o al `chat_sid`.

**Interacción paso a paso.**

1. El asistente termina de renderizar un bloque de respuesta. Debajo aparecen 👍, 👎 y "Copiar", sin ninguno seleccionado.
2. El cliente toca 👍 (o 👎). El ícono queda marcado como seleccionado al instante (estado optimista) y la reacción se registra ligada al `mensaje_id` y al `cliente_id` o `chat_sid`. La conversación sigue sin interrupción.
3. Si después toca el otro pulgar, la reacción se actualiza: solo queda una vigente, no se acumulan ambas, y se registra el cambio.
4. "Copiar" no es una reacción. Copia al portapapeles el texto plano del bloque, sin los datos de las tarjetas estructuradas, y lo confirma con un cambio breve del ícono. No se envía al backend.

**Estados.**

| Estado | Qué ve el cliente | Escenario |
|---|---|---|
| Vacío | Los dos pulgares sin seleccionar | Requisito 1 |
| Éxito | El pulgar tocado queda marcado; no hay mensaje adicional | "Reacción positiva" |
| Cambio | El nuevo pulgar queda marcado y el anterior se desmarca | "Cambiar de reacción" |
| Error | El ícono se marca igual. El registro se reintenta en segundo plano, sin mostrar error ni bloquear el chat | "Registro falla" |
| Ya enviado | Se ve la reacción vigente y puede cambiarse al otro pulgar; la spec no define cómo retirarla | "Cambiar de reacción" |
| Límite de uso | Por encima de 30 reacciones en 1 minuto (por cliente o `chat_sid`), las siguientes se ignoran en silencio, sin mensaje | "Exceso de reacciones" (Requisito 6) |

**Accesibilidad.** Se aplican las reglas de `design-system.md` §5.4, §8 y §9:

- Cada control es un botón con `aria-label`, nunca un ícono suelto. Los íconos siguen el set de §8: 16 px en controles y 2 px de trazo.
- Los pulgares, como alternan un estado seleccionado, usan `aria-pressed`, igual que los selectores de color y talla.
- La selección no se comunica solo con color.
- Foco visible: `outline` de 3 px en `accent/signal`.
- `prefers-reduced-motion` desactiva la animación de confirmación de "Copiar".

**Mobile-first.**
- La fila va bajo la burbuja del bot, que es blanca, alineada a la izquierda y con `max-w-[85%]` (§7).
- Usa la separación ícono-texto de 8 px y la escala de espaciado de 4 px (§4.1).
- Los controles están pensados para el marco móvil de hasta 430 px (§10).

**Correspondencia con SPEC-24.**
- Requisito 1 "Reacciones rápidas tras un bloque de respuesta", escenarios "Reacción positiva", "Cambiar de reacción", "Copiar el texto de la respuesta" y "Registro falla".
- Requisito 6, escenario "Exceso de reacciones".
- Requisito no funcional de rendimiento: registrar una reacción, p95 ≤ 400 ms.
- Resuelve la pregunta abierta 9 de [`docs/conversacion/README.md`](conversacion/README.md).

---

## 2. Calificación de la entrega (caritas 5/3/1)

**Objetivo.** Recoger la satisfacción del cliente con el pedido recibido. Es la encuesta CSAT de Ventas (F5), así que el chatbot la envía a Ventas en vez de guardarla como calificación propia.

**Dónde y cuándo.**
- **Dónde:** bloque fijo al pie de la pantalla de detalle del pedido (`OrderDetail`). No es una ventana emergente.
- **Cuándo aparece:** solo si el pedido está `ENTREGADO` y no está calificado.
- **Cuándo no aparece:** en `CREADO`, `PAGADO`, `EN_PREPARACION` o `DESPACHADO`.
- **No es proactiva:** el chatbot no recibe aviso de entrega, así que se ofrece cuando el cliente abre el pedido.
- **Pedidos de otro canal:** se ofrece para cualquier pedido `ENTREGADO` del cliente, aunque se haya creado en otro canal.

**Interacción paso a paso.**

1. El cliente abre el detalle de un pedido `ENTREGADO` que no ha calificado.
2. Al pie ve "¿Qué tal fue tu pedido?", tres caritas (feliz, neutral y triste), un comentario opcional y el botón "Enviar calificación", deshabilitado.
3. Toca una carita y el botón se habilita. Las caritas se envían como `puntuacion` 5 (feliz), 3 (neutral) y 1 (triste).
4. Pulsa "Enviar calificación". El backend valida que el pedido sea suyo y esté `ENTREGADO`, y llama a `POST /api/v2/csat {pedidoId, clienteId, canal: "CHATBOT", puntuacion, comentario}` con el token del cliente. El `clienteId` del cuerpo es el `sub` del token.
5. Ventas responde `201` y el bloque se reemplaza por un agradecimiento breve.

**Estados.**

| Estado | Qué ve el cliente | Escenario |
|---|---|---|
| Vacío | Bloque con las tres caritas sin seleccionar y "Enviar calificación" deshabilitado | "Sin estrellas seleccionadas" (así se llama en el cambio, aunque son caritas) |
| No aplica | Pedido no `ENTREGADO`: el bloque no aparece | "Pedido aún no entregado" |
| Descartado | Si sale sin responder, no se envía nada y el bloque vuelve a aparecer al reabrir ese pedido | "El cliente lo descarta" |
| Éxito | Ventas responde `201`; el bloque se reemplaza por un agradecimiento breve. La spec no fija el texto | "Calificación enviada" |
| Ya enviado | Ventas responde `409 CSAT_ALREADY_SUBMITTED`; el bloque se reemplaza por "Ya calificaste este pedido", sin presentarlo como error, y se marca `order_ref.csat_sent` | "Encuesta ya registrada para ese pedido" |
| Error: Ventas no responde | "No pudimos enviar tu calificación, intenta de nuevo más tarde". El bloque se conserva para reintentar y el detalle del pedido sigue usable | "Ventas no disponible al calificar" |
| Error: pedido ajeno (`403`) | "No pudimos enviar tu calificación, intenta de nuevo". El bloque se conserva | "El pedido no es del cliente" |
| Error: no entregado según Ventas (`422 ORDER_NOT_DELIVERED`) | El bloque se oculta y el detalle se refresca con el estado vigente | "Pedido no entregado según Ventas" |

**Accesibilidad.** Se aplican las reglas de `design-system.md` §2.6, §5.1 y §9:

- Las caritas son un grupo de opción única con `role="group"` y una etiqueta visible, como el selector de talla.
- Cada carita tiene `aria-label` con su significado y `aria-pressed` cuando está seleccionada. El estado nunca se indica solo con color.
- El agradecimiento y "Ya calificaste este pedido" se anuncian con `role="status" aria-live="polite"`.
- El botón deshabilitado usa `disabled:opacity-45 disabled:cursor-not-allowed`.
- El comentario es un `textarea` con estilo `.wf-input` y `aria-label`.

**Mobile-first.**
- El bloque va dentro del scroll de la pantalla de pedidos, sobre fondo `surface/cloud`, con tarjeta blanca `.wf-card` (§4.3 y §5.4).
- "Enviar calificación" usa el botón primario naranja `bg-action-primary text-surface-ink` (§5.1).
- Cumple con la grilla base de 16 px de margen en menos de 576 px (§4.4).

**Correspondencia con SPEC-24.**
- Requisito 2 "Calificación de la entrega (CSAT, vía Ventas)" en su versión modificada por `ajustar-calificacion-compra-y-entrega`, con los escenarios citados en la tabla.
- Requisitos no funcionales:
  - Rendimiento: enviar la calificación a Ventas, p95 ≤ 1 s.
  - Idempotencia: `pedidoId` como clave natural; Ventas responde `409` ante duplicados.
- Acuerdo A15 en [`docs/contratos-integracion.md`](contratos-integracion.md): token del cliente, rol `CLIENTE`, sin scope.

---

## 3. Valoración de la propia compra (estrellas 1 a 5)

**Objetivo.** Medir la experiencia de comprar en el chat, que es distinta de la satisfacción con el pedido recibido (propuesta 2). Es propia del chatbot: se guarda en `purchase_rating` y no se envía a Ventas.

**Dónde y cuándo.**
- **Dónde:** popup "Califica tu compra", montado junto con la confirmación del pedido (`OrderConfirmation`, SPEC-15).
- **Cuándo:** después del pago, una vez confirmado el pedido.
- **Comportamiento:** no bloquea la confirmación del pedido, y cada pedido admite una sola valoración.

**Interacción paso a paso.**

1. El cliente paga y se confirma el pedido. Sobre la confirmación aparece el popup "Califica tu compra" con estrellas de 1 a 5, un comentario opcional y los botones "Enviar calificación" (deshabilitado) y "Ahora no".
2. Toca una cantidad de estrellas y el botón "Enviar calificación" se habilita.
3. Pulsa "Enviar calificación". Se guarda `purchase_rating` con el pedido, el cliente, las estrellas y el comentario, que tiene un máximo de 500 caracteres según el modelo de `design.md`. El popup se reemplaza por un agradecimiento breve.
4. Si en cambio toca "Ahora no", el popup se cierra sin guardar nada y no vuelve a mostrarse para ese pedido en ese navegador.

**Estados.**

| Estado | Qué ve el cliente | Escenario |
|---|---|---|
| Vacío | Popup con las estrellas sin seleccionar y "Enviar calificación" deshabilitado | "Sin estrellas seleccionadas" |
| Descartado | "Ahora no" cierra el popup. El descarte se recuerda por pedido en el navegador (LocalStorage, con `orderId` como clave) y no en el backend: si se borra el almacenamiento o se usa otro dispositivo, el popup puede volver a mostrarse | "El cliente lo descarta" |
| Éxito | La valoración se guarda y el popup se reemplaza por un agradecimiento breve. La spec no fija el texto | "Valoración enviada" |
| Ya enviado | Si el pedido ya tiene valoración, el popup no aparece y no admite una segunda | "Una sola valoración por pedido" |
| Error | "No pudimos guardar tu opinión". La confirmación del pedido sigue visible y sin cambios | "Falla el guardado" |

**Accesibilidad.** Se aplican las reglas de `design-system.md` §6 (fila 12) y §9:

- El popup sigue el patrón de modal: overlay `bg-surface-ink/60` con `fade-in` y hoja `sheet bg-white rounded-t-lg p-4`.
- Se cierra tocando fuera o con `IconBtn X`, que lleva `aria-label`.
- Las estrellas forman un grupo con `role="group"` y etiqueta visible. Cada estrella tiene `aria-label` con su número ("1 estrella" a "5 estrellas") y `aria-pressed` en la seleccionada, y la cantidad se distingue por forma, no solo por color.
- El agradecimiento y el error se anuncian con `role="status" aria-live="polite"`.
- Foco visible en `accent/signal`.
- `prefers-reduced-motion` desactiva `sheet-up`.

**Mobile-first.**
- El popup es una hoja inferior dentro del marco móvil de hasta 430 px (§10).
- "Enviar calificación" usa el botón primario naranja y "Ahora no" un estilo secundario (§5.1).
- Los títulos en Oswald solo se usan si el popup lleva un H3 (§3.1).

**Correspondencia con SPEC-24.**
- Requisito 7 "Valoración de la experiencia de compra (propia del chatbot)", añadido por `ajustar-calificacion-compra-y-entrega`, con los escenarios citados en la tabla.
- Requisito no funcional de idempotencia: la valoración de la compra es única por pedido.
- Tabla `purchase_rating` en [`docs/modelo-datos.md`](modelo-datos.md).

---

## Otras interacciones de SPEC-24 (fuera de estas tres)

SPEC-24 define además el formulario "Enviar sugerencia / Reportar bug", al que se llega desde "Mi cuenta" → "Ayúdanos a mejorar" (Requisitos 3, 4 y 5), y que no forma parte de estas tres propuestas.
