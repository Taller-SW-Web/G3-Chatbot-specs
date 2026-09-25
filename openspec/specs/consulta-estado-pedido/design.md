# Diseño: Consulta de estado del pedido

> Origen: SPEC-17 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `GET /api/v1/pedidos?clienteId=&estado=&desde=&hasta=&pagina=&tamano=` | ✅ `api-contract.md` §1.4 |
| Ventas | `GET /api/v1/pedidos/{id}` (detalle, estado e historial) | ✅ §1.3 |
| Despacho | Seguimiento por pedido (SPEC-18) | 🟡 A11 |

## Frontend

🧩 Según el wireframe, el historial de pedidos es una **pantalla propia** (`OrderHistoryPage`) con pestañas, no solo un bloque dentro del chat. Las pestañas "En proceso" y "Entregados" se cubren en esta spec; la pestaña "Reembolsos" se cubre en SPEC-21 y SPEC-22, pero vive en el mismo componente de pestañas.

| Componente | Responsabilidad |
|---|---|
| `OrderHistoryPage` (pantalla completa) | Contenedor con las pestañas "En proceso", "Entregados" y "Reembolsos" (esta última implementada en SPEC-22); accesible desde el menú de usuario y desde `SesionIndicator`. |
| `OrderHistoryTabs` | Pestaña "En proceso" (`CREADO`, `PAGADO`, `EN_PREPARACION`, `DESPACHADO`) y "Entregados" (`ENTREGADO`, `ANULADO`), cada una con su propio `GET /pedidos?estado=&pagina=&tamano=`. |
| `OrderCard` | Tarjeta de pedido con número, badge de estado, fecha, dirección resumida y miniaturas de los productos (hasta 3, con "+N productos"). |
| `OrderList` (bloque `LISTA_PEDIDOS`, dentro del chat) | Versión conversacional cuando el cliente pregunta por sus pedidos en lugar de abrir `OrderHistoryPage`; mismas tarjetas que `OrderCard`. |
| `OrderStatusCard` (bloque `ESTADO_PEDIDO`) | Resumen, etiqueta de estado, `OrderTimeline` y las acciones "Ver seguimiento", "Reportar un problema" y "Reenviar correo". |
| `OrderTimeline` | Pasos verticales con estados completado, actual y pendiente. |
| Menú de usuario → "Mis pedidos" | Navega a `OrderHistoryPage`; desde el chat, la acción directa `LISTAR_PEDIDOS` abre `OrderList`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `GET /api/v1/pedidos` · `GET /api/v1/pedidos/{id}` | Proxy con control de pertenencia. |
| `EstadoPedidoService` | Selecciona el pedido, mapea las etiquetas, arma la línea de tiempo y enriquece con Despacho (SPEC-18). |
| `EstadoMapper` | Tabla de `contratos-integracion.md §4`. |
| Herramientas `listar_pedidos` (`{soloEnCurso?}`) y `consultar_pedido` (`{pedidoId? | pedidoRef?}`) | Uso desde el chat. |

## Desglose para issues

- [x] `[INT]` Acordar con Ventas el listado por cliente y el formato del historial (A8, resuelto)
- [ ] `[BE]` Endpoints de pedidos con control de pertenencia
- [ ] `[BE]` `EstadoPedidoService` y `EstadoMapper`
- [ ] `[BE]` Herramientas `listar_pedidos` y `consultar_pedido`
- [ ] `[FE]` `OrderHistoryPage` con `OrderHistoryTabs` ("En proceso" y "Entregados"; la pestaña "Reembolsos" se agrega en SPEC-22)
- [ ] `[FE]` `OrderCard`, `OrderList`, `OrderStatusCard` y `OrderTimeline`
- [ ] `[FE]` Entrada "Mis pedidos" en el menú de usuario, hacia `OrderHistoryPage`
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la no divulgación de pedidos ajenos
