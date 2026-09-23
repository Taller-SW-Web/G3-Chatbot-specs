# Diseño: Consulta de estado de devolución y reembolso

> Origen: SPEC-22 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `GET /api/v2/devoluciones?clienteId=&estado=&tipo=&pagina=&tamano=` | ✅ `api-contract.md` §2.4 |
| Ventas | `GET /api/v2/devoluciones/{id}` (incluye `resolucion.reembolso`) | ✅ §2.3 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ReturnHistoryTab` (pestaña "Reembolsos" de `OrderHistoryPage`) | Lista completa desde Ventas, con paginación (`pagina`/`totalPaginas`). |
| `ReturnStatusCard` (bloque `ESTADO_DEVOLUCION`) | Estado del expediente, motivo, evidencia (miniaturas), resolución y el bloque de estado del reembolso cuando existe. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `GET /api/v1/devoluciones` · `GET /api/v1/devoluciones/{id}` | Proxy directo a Ventas, con `clienteId` tomado del token (nunca del cliente). |
| `DevolucionConsultaService` | Mapea los estados de F3, arma el mensaje del reembolso cuando el bloque existe, y usa `devolucion_ref` local solo como respaldo si Ventas no responde. |
| Herramientas `listar_devoluciones` y `consultar_devolucion` | Uso desde el chat. |

## Desglose para issues

- [ ] `[BE]` Endpoints de consulta y listado, proxy directo a Ventas
- [ ] `[BE]` `DevolucionConsultaService` con el mapeo de estados y del bloque de reembolso
- [ ] `[FE]` `ReturnHistoryTab` integrada en `OrderHistoryPage` (SPEC-17) y `ReturnStatusCard`
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la fidelidad del fundamento y del detalle del reembolso
