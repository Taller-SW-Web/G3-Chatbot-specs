# Tasks

## 1. Specs de capacidad

- [x] 1.1 `consulta-reclamo`: listado con `/reclamos/me` (requisito 1).
- [x] 1.2 `consulta-devolucion-reembolso`: listado con `/devoluciones/me` (requisito 1).
- [x] 1.3 `creacion-reclamo` y `solicitud-devolucion-cambio`: duplicados con los `/me`.

## 2. Diseños y documentos

- [x] 2.1 Tablas de integración de seis diseños y del diseño de `grabacion-pedido`.
- [x] 2.2 `docs/contratos-integracion.md` §1, §3.3, A8 y nuevo A15; `modelo-datos.md` y `trazabilidad.md`.

## 3. Pendiente

- [ ] 3.1 Con el change `ajustar-calificacion-compra-y-entrega` fusionado: en `retroalimentacion-cliente` reemplazar la pregunta abierta del token por el acuerdo A15.
- [ ] 3.2 Definir en la implementación cuántos detalles se piden por página de pedidos y cuándo se reutiliza el snapshot `order_ref` (Ventas recomienda el detalle por pedido).
- [x] 3.3 Token de los tres detalles confirmado por Ventas: token del cliente.
- [ ] 3.4 Responder en el issue #9 enlazando este cambio, para que Ventas documente `ACUERDO_G3_CHATBOT.md`.
- [ ] 3.5 Archivar el cambio en un PR aparte.
