# Alinear las specs con la respuesta de Ventas (G3-Chatbot-specs #9)

## Why

Ventas respondió el 12/10/2026 en el issue #9 y confirmó, con su contrato (`api-ventas.md` y `api-postventas.md`), cómo debe autenticarse el chatbot. Los listados del cliente ya no se piden con `clienteId` y token de servicio: son los endpoints `/me`, con el token del propio cliente. Las specs asumían lo anterior.

## What Changes

- **Listados del cliente:** `GET /api/v1/pedidos/me`, `GET /api/v2/devoluciones/me` y `GET /api/v2/reclamos/me`, con el token del cliente (rol `CLIENTE`, sin scope). Ventas filtra por `sub`; el chatbot nunca envía `clienteId`.
- **Paginación de pedidos:** `page` (desde 1) y `pageSize` (1 a 50); la respuesta es `{items, total, page, pageSize}` y cada ítem trae solo `pedidoId`, `canal`, `estado`, `total`, `moneda` y `fechaCreacion`.
- **CSAT:** `POST /api/v2/csat` usa el token del cliente (no existe el scope `postventa:csat:escribir`) y responde `403` si el `sub` no es el dueño del pedido. Escala `1`/`3`/`5`.
- **Webhook de pago:** `ventas:pagos:webhook` ya está concedido a `modulo-chatbot`; no se pide nada a Seguridad.
- **Detección de duplicados** de reclamos y devoluciones: usa los `/me`.
- Documentar el acuerdo A15 y la matriz de autenticación hacia Ventas en `docs/contratos-integracion.md`.

## Capabilities

- `consulta-reclamo`: MODIFIED requisito 1.
- `consulta-devolucion-reembolso`: MODIFIED requisito 1.
- `creacion-reclamo`: MODIFIED requisito 3 (duplicados).
- `solicitud-devolucion-cambio`: MODIFIED requisito 5 (duplicados).
- Diseños de `consulta-estado-pedido`, `grabacion-pedido` y los cuatro anteriores; `docs/contratos-integracion.md` §1 y §3.3.

## Questions to Confirm

Resueltas por Ventas el 12/10 (issue #9):

- Los detalles `GET /pedidos/{id}`, `/reclamos/{codigoSeguimiento}` y `/devoluciones/{id}` usan el token del cliente (rol `CLIENTE`).
- Para miniaturas y dirección del listado de pedidos, se pide el detalle de cada pedido; el listado `/pedidos/me` no se amplía.

Pendiente interno: cuántos detalles se piden por página de pedidos y si se reutiliza el snapshot `order_ref` (ver `tasks.md` 3.2).
