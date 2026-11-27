# Diseño: Consulta de estado del pedido

> Origen: SPEC-17 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `GET /api/v1/pedidos/me?estado=&desde=&hasta=&page=&pageSize=` con token del cliente (rol `CLIENTE`) | ✅ `api-ventas.md` §1.4b (A15) |
| Ventas | `GET /api/v1/pedidos/{id}` (detalle, estado e historial) | ✅ §1.3, con token del cliente (A15) |
| Despacho | `GET /api/v1/seguimientos/pedidos/{idPedido}` (SPEC-18), scope `seguimientos:leer` concedido | ✅ contrato y scope (Seguridad #31); credenciales reales pendientes (el rol `SERVICIO_INTEGRACION` no existe; A4 retirado el 03/11) |

## Frontend

🧩 Según el wireframe, el historial de pedidos es una **pantalla propia** (`OrderHistoryPage`) con pestañas, no solo un bloque dentro del chat. Las pestañas "En proceso" y "Finalizados" se cubren en esta spec; la pestaña "Reembolsos" se cubre en SPEC-21 y SPEC-22, pero vive en el mismo componente de pestañas. **Decisión 2026-11-27:** "Finalizados" agrupa `ENTREGADO` y `ANULADO`; no se crea una quinta pestaña "Anulados" para no saturar la navegación móvil. Los anulados conservan su badge "Anulado" y el motivo/reembolso del detalle.

| Componente | Responsabilidad |
|---|---|
| `OrderHistoryPage` (pantalla completa, ruta `/pedidos`) | Contenedor con las pestañas "En proceso", "Finalizados" y "Reembolsos" (esta última implementada en SPEC-22); accesible desde el menú de usuario y desde `SesionIndicator`. |
| `OrderHistoryTabs` | Pestaña "En proceso" (`CREADO`, `PAGADO`, `EN_PREPARACION`, `DESPACHADO`) y "Finalizados" (`ENTREGADO`, `ANULADO`), cada una con su propio `GET /pedidos?estado=&pagina=&tamano=`. |
| `OrderCard` | Tarjeta de pedido con número, badge de estado, fecha, dirección resumida y miniaturas de los productos (hasta 3, con "+N productos"). El botón "VER DETALLE" navega a `/pedido?pedidoId={pedidoId}`. |
| `OrderDetailPage` (ruta `/pedido?pedidoId=`) | Detalle de solo lectura: cabecera con pedido, estado, total y fecha; secciones de productos (`items`), envío e historial. Si el estado es `ENTREGADO` y `!csatEnviado`, monta el slot `DeliveryRatingFooter` de `mod-postventa` al pie; no muestra el bloque de CSAT para otros estados ni cuando el pedido ya fue calificado. La ruta es singular para no chocar con `/pedidos/[tab]`, que es la pantalla con pestañas. |
| `OrderList` (bloque `LISTA_PEDIDOS`, dentro del chat) | Versión conversacional cuando el cliente pregunta por sus pedidos en lugar de abrir `OrderHistoryPage`; mismas tarjetas que `OrderCard`. |
| `OrderStatusCard` (bloque `ESTADO_PEDIDO`) | Resumen, etiqueta de estado, `OrderTimeline` y las acciones "Ver seguimiento", "Reportar un problema" y "Reenviar correo". |
| `OrderTimeline` | Pasos verticales con estados completado, actual y pendiente. |
| Menú de usuario → "Mis pedidos" | Navega a `OrderHistoryPage`; desde el chat, la acción directa `LISTAR_PEDIDOS` abre `OrderList`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `GET /api/v1/pedidos` · `GET /api/v1/pedidos/{id}` | Proxy hacia `/pedidos/me` y `/pedidos/{id}`; reenvía el token del cliente y Ventas filtra por `sub`. Reenvía `estado`, `desde`, `hasta`, `page` y `pageSize` sin transformación; `desde`/`hasta` son fechas ISO `YYYY-MM-DD` y una fecha inválida o un rango invertido (`desde > hasta`) responde `400 VALIDACION` sin llamar a Ventas. El detalle incluye `csatEnviado` (leído de `order_ref.csat_sent`; `false` si no hay fila local o no se envió), que el frontend usa para ocultar el slot CSAT. |
| `EstadoPedidoService` | Selecciona el pedido, mapea las etiquetas, arma la línea de tiempo y enriquece con Despacho (SPEC-18). Para un pedido `ANULADO` calcula `motivoAnulacion` (último `motivo` del historial `ANULADO`, solo si está en la lista de códigos conocidos: `STOCK_NO_DISPONIBLE` y `MotivoAnulacion` de G5; si no, `null`) y `reembolso` ("Se procesará el reembolso al medio de pago original." solo con evidencia de pago: `pago.estado` `CONFIRMADO` o `PAGADO` en el historial), y los expone en el detalle, el seguimiento y el chat con el mensaje de anulación por stock. |
| `EstadoMapper` | Tabla de `contratos-integracion.md §4`. |
| Herramienta `consultar_pedidos` (`{pedidoId?, estado?}`) | Uso desde el chat: sin `pedidoId` lista o muestra el pedido en curso; con `pedidoId`, el detalle. |

## Desglose para issues

- [x] `[INT]` Acordar con Ventas el listado por cliente y el formato del historial (A8, resuelto)
- [ ] `[BE]` Endpoints de pedidos con el token del cliente (`/pedidos/me`), filtros `desde`/`hasta`, paginación `page`/`pageSize` y `csatEnviado`
- [ ] `[BE]` Completar cada `OrderCard` (miniaturas y dirección resumida) con `GET /pedidos/{id}` por pedido, como recomienda Ventas, porque `/pedidos/me` solo trae `pedidoId`, `canal`, `estado`, `total`, `moneda` y `fechaCreacion`; limitar a los pedidos de la página y reutilizar el snapshot local `order_ref` si ya existe
- [ ] `[BE]` `EstadoPedidoService` y `EstadoMapper`
- [ ] `[BE]` Herramienta `consultar_pedidos` (lista y detalle)
- [ ] `[FE]` `OrderHistoryPage` con `OrderHistoryTabs` ("En proceso" y "Finalizados"; la pestaña "Reembolsos" se agrega en SPEC-22)
- [ ] `[FE]` `OrderCard`, `OrderList`, `OrderStatusCard` y `OrderTimeline`
- [ ] `[FE]` `OrderDetailPage` en `/pedido?pedidoId=`, con cabecera, items, envío, historial y slot `DeliveryRatingFooter` solo si `ENTREGADO` y `!csatEnviado`
- [ ] `[FE]` Entrada "Mis pedidos" en el menú de usuario, hacia `OrderHistoryPage`
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la no divulgación de pedidos ajenos
