# Diseño: Seguimiento del despacho en ruta

> Origen: SPEC-18 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Despacho | `GET /api/v1/seguimientos/pedidos/{idPedido}` con token de servicio, scope `seguimientos:leer`, audience `api-despacho` | ✅ contrato y scope concedido a `modulo-chatbot` (Seguridad #31); credenciales reales en Hito 4 |
| Seguridad | `POST /auth/token` (`client_credentials`, `client_id=modulo-chatbot`) | ✅ |
| Seguridad / Despacho | Rol `SERVICIO_INTEGRACION` en el token de servicio del chatbot | 🟡 A4 pendiente; no confundir con los scopes concedidos en Seguridad #31 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ShipmentTracking` (dentro de `OrderStatusCard`) | Etiqueta, fecha programada, distrito e hitos del despacho. |
| `ShipmentMilestones` | Lista de hitos con iconos de estado. |
| Aviso de no disponible | Texto con "Reintentar". |

## Backend

| Componente | Responsabilidad |
|---|---|
| `GET /api/v1/pedidos/{id}/seguimiento` | Control de pertenencia (vía Ventas o `order_ref`) y consulta a Despacho. |
| `ServiceTokenProvider` | Obtiene y cachea el token `client_credentials` de Seguridad. |
| `DespachoClient.seguimiento(idPedido)` | Timeout de 4 s, renovación ante `401` y caché de 30 s. |
| `SeguimientoMapper` | Lista blanca de campos y mapeo de etiquetas. |
| Herramienta `consultar_seguimiento` (`{pedidoId? | pedidoRef?}`) | Uso desde el chat. |

## Desglose para issues

- [ ] `[INT]` Obtener y configurar las credenciales reales en Hito 4; gestionar con Seguridad el rol `SERVICIO_INTEGRACION` aún pendiente (A4)
- [ ] `[BE]` `ServiceTokenProvider` (compartido con otros clientes; se construye en Hito 4 con SPEC-14, HU-CHK-14, y aquí solo se reutiliza)
- [ ] `[BE]` `DespachoClient.seguimiento` y `SeguimientoMapper` con lista blanca
- [ ] `[BE]` Endpoint de seguimiento y herramienta `consultar_seguimiento`
- [ ] `[FE]` `ShipmentTracking` y `ShipmentMilestones`
- [ ] `[QA]` Pruebas de todos los escenarios, incluido el descarte de campos no permitidos
