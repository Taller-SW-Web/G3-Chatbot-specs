# Diseño

## Decisiones

1. **Token del cliente solo donde Ventas lo exige.** El `ServiceTokenProvider` sigue firmando las llamadas de crear pedido, anular, notificar pago, registrar reclamo y registrar devolución. Los `/me` y `POST /api/v2/csat` reenvían el token del cliente que llegó al BFF; nunca se cachea ni se guarda.
2. **El chatbot no manda `clienteId` en consultas.** Ventas deriva la identidad del `sub`. En `POST /api/v2/csat` el cuerpo sí lleva `clienteId` (contrato de Ventas), que debe ser el `sub` del token.
3. **Paginación propia hacia el frontend.** El backend traduce `pagina`/`tamano` (desde 1 en la API del chatbot) a `page`/`pageSize` de pedidos y a `pagina`/`tamano` (desde 0) de devoluciones y reclamos.
4. **Sin sesión no hay listados.** Los `/me` exigen cuenta, coherente con la regla de producto: navegar sin cuenta, comprar y ver pedidos con cuenta.

## Fuera de este cambio

`retroalimentacion-cliente` (SPEC-24) ya incorpora el CSAT en su propio change (`ajustar-calificacion-compra-y-entrega`). Al fusionarlo, su diseño debe citar este acuerdo (A15) en lugar de la pregunta abierta sobre el token.
