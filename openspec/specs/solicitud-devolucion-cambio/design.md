# Diseño: Solicitud de devolución o cambio

> Origen: SPEC-21 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `POST /api/v2/devoluciones/evidencias/upload` | ✅ `api-contract.md` §2.1 |
| Ventas | `POST /api/v2/devoluciones` | ✅ §2.2 |
| Ventas | `GET /api/v2/devoluciones?clienteId=&estado=&tipo=` (detección de duplicados) | ✅ §2.4 |
| Ventas | `GET /api/v1/pedidos?clienteId=` (selección del pedido) | ✅ |
| Productos | Disponibilidad de la variante deseada (SPEC-10) | 🟡 A5 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ReturnForm` (bloque `FORMULARIO/DEVOLUCION`) | Pedido, línea(s), tipo, motivo, `VariantSelector` si es cambio, descripción, `EvidenceUploader`, "Enviar solicitud" y "Cancelar". |
| `EvidenceUploader` | Selector de hasta 3 archivos, previsualización, barra de progreso y opción de quitar. |
| `ReturnReceipt` (bloque `CONSTANCIA_DEVOLUCION`) | Código, pedido, tipo, motivo y estado inicial. |
| `DuplicateReturnNotice` | Aviso de solicitud abierta con el código existente y el enlace a su estado. |
| Entrada desde `OrderStatusCard` (SPEC-17) | Botón "Solicitar cambio o devolución" en pedidos `ENTREGADO`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `preparar_devolucion` | Esquema `{pedidoRef?, lineaRef?, tipo?, motivo?, varianteDeseada?, descripcion?}`; devuelve el formulario prellenado (no registra). |
| `POST /api/v1/evidencias` | Proxy directo hacia `POST /api/v2/devoluciones/evidencias/upload` de Ventas; guarda solo la referencia local. |
| `POST /api/v1/devoluciones` | Valida elegibilidad (7 días), evidencia obligatoria según el motivo, detecta duplicados vía el listado real de Ventas y registra con idempotencia. |
| `DevolucionService` | Orquesta la elegibilidad, el borrador, la evidencia, la detección de duplicados y el registro. |
| `VentasClient.devoluciones` | Cliente de Ventas para subir evidencia, registrar, consultar y listar devoluciones. |
| Job de limpieza local | Borra las referencias de evidencia de borradores no enviados tras 24 h (no toca el archivo en Ventas). |
| Tablas `devolucion_ref` y `evidencia` | Ver `modelo-datos.md`. |

## Desglose para issues

- [ ] `[BE]` Herramienta `preparar_devolucion` y gestión de borradores
- [ ] `[BE]` `POST /evidencias` como proxy hacia Ventas
- [ ] `[BE]` `DevolucionService`: elegibilidad, duplicados (vía listado real) y registro con idempotencia
- [ ] `[BE]` `VentasClient.devoluciones` (subir evidencia, registrar, consultar, listar) con su mock
- [ ] `[BE]` Job de limpieza de referencias locales de evidencia no enviada
- [ ] `[FE]` `ReturnForm`, `EvidenceUploader`, `ReturnReceipt` y `DuplicateReturnNotice`
- [ ] `[FE]` Botón "Solicitar cambio o devolución" en `OrderStatusCard`
- [ ] `[QA]` Pruebas de todos los escenarios, incluidos el plazo de 7 días, la detección de duplicados y el límite de tamaño de archivo
