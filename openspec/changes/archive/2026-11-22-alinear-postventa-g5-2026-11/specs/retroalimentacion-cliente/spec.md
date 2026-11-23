## MODIFIED Requirements

### Requirement: Calificación de la entrega con caritas (CSAT, vía Ventas)
El sistema DEBE (SHALL) ofrecer la calificación del pedido (CSAT de Ventas) en un bloque fijo al pie del detalle de un pedido `ENTREGADO` (`OrderDetail`), nunca en la lista de pedidos ni en una ventana emergente, con tres caritas (feliz, neutral, triste) y un comentario opcional, y DEBE (SHALL) enviarla a Ventas (`POST /api/v2/csat`) en vez de almacenarla como calificación propia.

El frontend NO DEBE (SHALL NOT) enviar `clienteId`: el backend lo arma con el `sub` del token del cliente. La interfaz DEBE (SHALL) mostrar `409 CSAT_ALREADY_SUBMITTED` como "Ya calificaste este pedido" (estado informativo, no error) y `422 ORDER_NOT_DELIVERED` como "Solo puedes calificar pedidos entregados".

*Trazabilidad: SPEC-24 · Requisito 2. Ventas F5 — CSAT (`docs/contratos-integracion.md`); solo acepta pedidos `ENTREGADO`. Alineado con el contrato real de G5 (2026-11).*

#### Scenario: Calificación enviada
- **DADO** el detalle de un pedido `ENTREGADO` que el cliente no ha calificado
- **CUANDO** el cliente toca una carita y pulsa "Enviar calificación"
- **ENTONCES** el frontend llama a `POST /api/v1/pedidos/{pedidoId}/csat {puntuacion, comentario?}` sin `clienteId`, el backend arma `{pedidoId, clienteId, canal: "CHATBOT", puntuacion, comentario}` con el `clienteId` igual al `sub` del token del cliente y lo reenvía a Ventas con ese mismo token, `puntuacion` es 5 (feliz), 3 (neutral) o 1 (triste), Ventas responde `201`, y el bloque se reemplaza por el agradecimiento "¡Gracias por tu calificación!"

#### Scenario: Sin carita seleccionada
- **DADO** el bloque de calificación visible al pie del detalle del pedido
- **CUANDO** el cliente no ha tocado ninguna de las tres caritas
- **ENTONCES** el botón "Enviar calificación" permanece deshabilitado hasta que elija una carita

#### Scenario: Puntuación fuera de la escala acordada
- **DADO** el bloque de calificación visible en el detalle de un pedido
- **CUANDO** llega una petición con `puntuacion` distinta de 1, 3 o 5 (por ejemplo, 4)
- **ENTONCES** responde `400 VALIDACION` con `errores[{campo: "puntuacion", mensaje}]`, no se llama a Ventas y no se marca `order_ref.csat_sent`

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
- **ENTONCES** se muestra "Solo puedes calificar pedidos entregados" en el bloque, sin presentarlo como error de red, y se refresca el detalle para mostrar el estado vigente; si el estado ya no es `ENTREGADO`, el bloque deja de mostrarse

#### Scenario: Pedido aún no entregado
- **DADO** el detalle de un pedido en `CREADO`, `PAGADO`, `EN_PREPARACION` o `DESPACHADO`
- **CUANDO** se muestra la pantalla
- **ENTONCES** el bloque de calificación no aparece

#### Scenario: La lista de pedidos no muestra el bloque
- **DADO** la pantalla de historial de pedidos con uno o más pedidos `ENTREGADO`
- **CUANDO** se muestra la lista
- **ENTONCES** no aparece ninguna carita ni el botón "Enviar calificación"; el bloque solo se muestra al pie del detalle de cada pedido

#### Scenario: El `clienteId` no viaja desde el navegador
- **DADO** el bloque de calificación visible en el detalle de un pedido
- **CUANDO** el cliente envía su calificación
- **ENTONCES** el cuerpo enviado por el frontend contiene solo `puntuacion` y, si existe, `comentario`; el backend obtiene el `clienteId` del `sub` del token y no acepta un `clienteId` enviado por el cliente
