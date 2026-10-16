## MODIFIED Requirements

### Requirement: Calificación de la entrega (CSAT, vía Ventas)
El sistema DEBE (SHALL) ofrecer la calificación del pedido (CSAT de Ventas) al pie de la pantalla de detalle de un pedido cuyo estado sea `ENTREGADO`, con tres caritas (feliz, neutral, triste) y un comentario opcional, y DEBE (SHALL) enviarla a Ventas (`POST /api/v2/csat`) en vez de almacenarla como calificación propia. Las caritas se envían como `puntuacion` 5 (feliz), 3 (neutral) y 1 (triste), la escala acordada por Ventas con Marketplace. El `clienteId` del cuerpo DEBE (MUST) ser igual al `sub` del token del cliente. No es una ventana emergente: es un bloque fijo al pie de la pantalla.

*Trazabilidad: SPEC-24 · Requisito 2. Conecta con Ventas F5 — CSAT; ver `docs/contratos-integracion.md`. Ventas solo acepta calificar pedidos `ENTREGADO` (`422 ORDER_NOT_DELIVERED`).*

#### Scenario: Calificación enviada
- **DADO** el detalle de un pedido `ENTREGADO` que el cliente no ha calificado
- **CUANDO** el cliente toca una carita y pulsa "Enviar calificación"
- **ENTONCES** se llama a `POST /api/v2/csat {pedidoId, clienteId, canal: "CHATBOT", puntuacion, comentario}`, Ventas responde `201`, y el bloque se reemplaza por un agradecimiento breve

#### Scenario: Sin estrellas seleccionadas
- **DADO** el bloque de calificación visible al pie del detalle del pedido
- **CUANDO** el cliente no ha tocado ninguna carita
- **ENTONCES** el botón "Enviar calificación" permanece deshabilitado

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

## ADDED Requirements

### Requirement: Valoración de la experiencia de compra (propia del chatbot)
El sistema DEBE (SHALL) mostrar, después del pago y una vez confirmado el pedido, un popup "Califica tu compra" con estrellas (1 a 5) y comentario opcional, y DEBE (SHALL) guardar la valoración en el propio chatbot, sin enviarla a Ventas. No bloquea la confirmación del pedido.

*Trazabilidad: SPEC-24 · Requisito 7. Complementa el Requisito 2: esta valoración mide la experiencia de comprar en el chat; la del Requisito 2 mide el pedido recibido.*

#### Scenario: Valoración enviada
- **DADO** un pedido recién pagado y confirmado, con el popup abierto
- **CUANDO** el cliente toca una cantidad de estrellas y pulsa "Enviar calificación"
- **ENTONCES** se guarda `purchase_rating` con el pedido, el cliente, las estrellas (1 a 5) y el comentario, y el popup se reemplaza por un agradecimiento breve

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
