# Diseño: Solicitud de devolución o cambio

> Origen: SPEC-21 · Especificación de comportamiento: [`spec.md`](spec.md) · Decisión: [ADR-0027](../../../docs/arquitectura/adr/ADR-0027-duplicados-de-postventa-y-forzar.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `POST /api/v2/devoluciones/evidencias/upload` | ✅ `api-contract.md` §2.1 |
| Ventas | `POST /api/v2/devoluciones` | ✅ §2.2 |
| Ventas | `GET /api/v2/devoluciones/me?estado=&tipo=` con token del cliente (detección de duplicados) | ✅ §2.4b (A15) |
| Ventas | `GET /api/v1/pedidos/me` con token del cliente (selección del pedido) | ✅ §1.4b (A15) |
| Productos | `GET /inventario/disponibilidad/comercial?skus=&canal=CHATBOT` para la variante deseada (estado, sin cantidades) | 🟡 A5 · scope `inventario:disponibilidad:leer` pendiente |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ReturnForm` (bloque `FORMULARIO/DEVOLUCION`) | Pedido, línea(s), tipo, motivo, `VariantSelector` si es cambio, descripción, `EvidenceUploader`, "Enviar solicitud" y "Cancelar". |
| `EvidenceUploader` | Selector de hasta 3 archivos, previsualización, barra de progreso y opción de quitar. |
| `ReturnReceipt` (bloque `CONSTANCIA_DEVOLUCION`) | Código, pedido, tipo, motivo y estado inicial. |
| `DuplicateReturnNotice` | Aviso de solicitud abierta con el código existente y el enlace a su estado; al confirmar, el formulario reenvía con `forzar: true`. |
| Entrada desde `OrderStatusCard` (SPEC-17) | Botón "Solicitar cambio o devolución" en pedidos `ENTREGADO`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `preparar_devolucion` | Esquema `{pedidoRef?, lineaRef?, tipo?, motivo?, varianteDeseada?, descripcion?}`; devuelve el formulario prellenado (no registra). |
| `POST /api/v1/evidencias` | Proxy directo hacia `POST /api/v2/devoluciones/evidencias/upload` de Ventas; guarda solo la referencia local. |
| `POST /api/v1/devoluciones` | Valida elegibilidad (7 días), evidencia obligatoria según el motivo, detecta duplicados de forma previa y autoritativa, acepta `forzar` y registra con idempotencia. |
| `DevolucionService` | Orquesta la elegibilidad, el borrador, la evidencia, la detección de duplicados y el registro. |
| `VentasClient.devoluciones` | Cliente de Ventas para subir evidencia, registrar, consultar y listar devoluciones. |
| Job de limpieza local | Borra las referencias de evidencia de borradores no enviados tras 24 h (no toca el archivo en Ventas). |
| Tablas `return_ref` y `evidence` | Ver `modelo-datos.md`. |

### Evidencia y transacción

- **Pertenencia de la conversación:** `POST /api/v1/evidencias` acepta `conversacionId` opcional; antes de subir el archivo a Ventas verifica que esa conversación pertenezca al cliente autenticado. Si no existe o es ajena, responde `404 RECURSO_NO_ENCONTRADO` y **no llama a Ventas**.
- **Referencia local con `SAVEPOINT`:** `return_ref` se guarda dentro de un `SAVEPOINT`; un duplicado de `idempotency_key` no revierte el resto de la transacción (por ejemplo, las filas de `evidence`) y el reintento recupera la referencia existente en lugar de crear otra.

### Contrato de `POST /api/v1/devoluciones`

- **Sesión:** `CLIENTE`. **Cabecera:** `Idempotency-Key` obligatoria.
- **Cuerpo:** el payload de Ventas de `spec.md` más `forzar` (booleano, por defecto `false`). `forzar` no se reenvía a Ventas.
- **Detección de duplicados (autoritativa):** antes de llamar a Ventas, consulta `GET /api/v1/devoluciones` (proxy a `/me`) y busca una solicitud del mismo `pedidoId`, `motivo` y firma de líneas (`productoId` + `cantidad`) en estado abierto (`SOLICITADA`, `EN_EVALUACION` o `APROBADA`). `RECHAZADA` y `COMPLETADA` no cuentan.
- **Si hay duplicado y `forzar=false`:** responde `409` con `application/problem+json`:

```json
{
  "status": 409,
  "code": "DEVOLUCION_DUPLICADA",
  "title": "Duplicate return",
  "detail": "Ya existe una solicitud abierta para este pedido, motivo y líneas.",
  "devolucionId": "DEV-2026-0042",
  "estado": "EN_EVALUACION",
  "motivo": "TALLA_INCORRECTA"
}
```

- **Si hay duplicado y `forzar=true`:** registra la nueva solicitud en Ventas con la `Idempotency-Key` del envío y responde `201` con la constancia nueva. No se reutiliza el `devolucionId` existente.
- **Si el listado de duplicados falla:** se registra la solicitud (fail-open) y se deja un `warning` con el `X-Correlation-Id`; el cliente no ve un error de duplicados. Supuesto explícito: si el equipo prefiere fail-closed, se responde `503 SERVICIO_NO_DISPONIBLE`.
- **Idempotencia:** dos envíos con la misma `Idempotency-Key` y el mismo `forzar` devuelven la misma constancia y crean una sola solicitud.

### Errores

| `code` | HTTP | Cuándo |
|---|---|---|
| `VALIDACION` | 400 | Faltan campos o el cuerpo no cumple el schema. |
| `PEDIDO_NO_ENTREGADO` | 409 | El pedido no está `ENTREGADO`. Código de Ventas, propagado sin transformar. |
| `PLAZO_VENCIDO` | 400 | La solicitud está fuera de los 7 días naturales desde la entrega. Código de Ventas. |
| `EVIDENCIA_REQUERIDA` | 400 | El motivo exige evidencia y no se adjuntó. Código de Ventas; el formulario también deshabilita el envío. |
| `DEVOLUCION_DUPLICADA` | 409 | Existe una solicitud abierta para el mismo pedido, motivo y líneas y `forzar` es `false`. |
| `DEVOLUCION_EN_CURSO` | 409 | Ventas ya tiene una devolución no rechazada para esas unidades (carrera con la consulta previa). Código de Ventas. |
| `EVIDENCIA_INVALIDA` | 400 | Archivo mayor a 5 MB o tipo no permitido. |
| `ITEM_INVALIDO` / `DATOS_INVALIDOS` / `FORMATO_INVALIDO` / `CODIGO_INVALIDO` | 400 | Validaciones de Ventas sobre las líneas o el motivo; se propagan y el frontend usa el mensaje genérico. |
| `RECURSO_NO_ENCONTRADO` | 404 | La conversación de la evidencia no existe o no pertenece al cliente; no se sube a Ventas. |
| `SERVICIO_NO_DISPONIBLE` | 503 | Ventas no responde; se conserva el borrador 24 h. |

## Desglose para issues

- [ ] `[BE]` Herramienta `preparar_devolucion` y gestión de borradores
- [ ] `[BE]` `POST /evidencias` como proxy hacia Ventas, con validación de pertenencia de `conversacionId` (`404` sin llamar a Ventas)
- [ ] `[BE]` `DevolucionService`: elegibilidad, duplicados (previa y autoritativa) y registro con idempotencia; `return_ref` con `SAVEPOINT`
- [ ] `[BE]` `forzar` en `POST /devoluciones` y `409 DEVOLUCION_DUPLICADA` con el código/estado existente
- [ ] `[BE]` `VentasClient.devoluciones` (subir evidencia, registrar, consultar, listar) con su mock
- [ ] `[BE]` Job de limpieza de referencias locales de evidencia no enviada
- [ ] `[FE]` `ReturnForm`, `EvidenceUploader`, `ReturnReceipt` y `DuplicateReturnNotice` con la acción de forzar
- [ ] `[FE]` Botón "Solicitar cambio o devolución" en `OrderStatusCard`
- [ ] `[QA]` Pruebas de todos los escenarios, incluidos el plazo de 7 días, la detección de duplicados, el `forzar` y el límite de tamaño de archivo
