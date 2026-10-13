# Diseño: Consulta de estado de devolución y reembolso

> Origen: SPEC-22 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `GET /api/v2/devoluciones/me?estado=&tipo=&pagina=&tamano=` con token del cliente (rol `CLIENTE`) | ✅ `api-postventas.md` §2.4b (A15) |
| Ventas | `GET /api/v2/devoluciones/{id}` (incluye `resolucion.reembolso`) | ✅ §2.3, con token del cliente (A15) |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ReturnHistoryTab` (pestaña "Reembolsos" de `OrderHistoryPage`) | Lista completa desde Ventas, con paginación (`pagina`/`totalPaginas`). |
| `ReturnStatusCard` (bloque `ESTADO_DEVOLUCION`) | Estado del expediente, motivo, evidencia (miniaturas), resolución y el bloque de estado del reembolso cuando existe. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `GET /api/v1/devoluciones` · `GET /api/v1/devoluciones/{id}` | Proxy directo a Ventas (`/devoluciones/me` y `/devoluciones/{id}`) con el token del cliente; Ventas filtra por el `sub` y el chatbot nunca envía `clienteId`. |
| `DevolucionConsultaService` | Mapea los estados de F3, arma el mensaje del reembolso cuando el bloque existe, y usa `return_ref` local solo como respaldo si Ventas no responde. |
| Herramientas `listar_devoluciones` y `consultar_devolucion` | Uso desde el chat. |

## Desglose para issues

- [ ] `[BE]` Endpoints de consulta y listado, proxy directo a Ventas
- [ ] `[BE]` `DevolucionConsultaService` con el mapeo de estados y del bloque de reembolso
- [ ] `[FE]` `ReturnHistoryTab` integrada en `OrderHistoryPage` (SPEC-17) y `ReturnStatusCard`
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la fidelidad del fundamento y del detalle del reembolso
