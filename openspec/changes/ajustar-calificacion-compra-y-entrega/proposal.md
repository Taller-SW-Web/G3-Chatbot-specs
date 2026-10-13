# Dos calificaciones: experiencia de compra y pedido entregado

## Why

SPEC-24 mostraba un modal de calificación justo tras el pago y lo enviaba a Ventas (`POST /api/v2/csat`). Ventas solo acepta calificar pedidos `ENTREGADO` (`422 ORDER_NOT_DELIVERED`) y admite una sola encuesta por pedido, así que ese flujo habría fallado siempre. El equipo decidió separar dos momentos: una valoración propia tras el pago (popup, estrellas) y la calificación de Ventas al entregarse (bloque al pie del detalle, caritas).

## What Changes

- **Valoración de la experiencia de compra (nueva, local):** popup "Califica tu compra" tras el pago, con estrellas de 1 a 5 y comentario opcional; se guarda en una tabla propia `purchase_rating` y no se envía a Ventas.
- **Calificación del pedido (CSAT de Ventas, modificada):** al pie del detalle de un pedido `ENTREGADO`, con tres caritas que se envían como 1, 3 y 5 (escala acordada por Ventas con Marketplace).
- El popup actual se conserva para la valoración propia; la calificación de Ventas no es popup, es un bloque al pie del detalle del pedido.
- Se corrige lo comunicado a Ventas en el issue #9 (estrellas 1–5): a Ventas se enviarán valores 1, 3 y 5 desde caritas.

## Capabilities

- `retroalimentacion-cliente`: MODIFIED requisito 2; ADDED requisito 7.
- `retroalimentacion-cliente/design.md`: componentes, tablas en inglés (`message_reaction`, `feedback_suggestion`, `purchase_rating`) y `order_ref.csat_sent`.

## Questions to Confirm

Decisiones asumidas (confirmar con el equipo):

1. La valoración propia usa estrellas de 1 a 5 en popup; la de Ventas usa caritas feliz, neutral y triste (5, 3, 1) en un bloque al pie.
2. La calificación del pedido no es proactiva: aparece cuando el cliente abre un pedido `ENTREGADO`. El chatbot no recibe aviso de entrega.
3. Si el cliente no responde, el bloque de entrega vuelve a aparecer al reabrir el pedido; el popup de compra no vuelve a mostrarse.
4. La calificación del pedido se ofrece para cualquier pedido `ENTREGADO` del cliente, aunque se haya creado en otro canal; Ventas rechaza duplicados con `409`.

Resuelto por Ventas el 12/10 (acuerdo A15): token del cliente, rol CLIENTE, 403 si el `sub` no es el dueño del pedido; sin scope.
