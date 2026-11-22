# Diseño: Creación de reclamo

> Origen: SPEC-19 · Especificación de comportamiento: [`spec.md`](spec.md) · Decisión: [ADR-0027](../../../docs/arquitectura/adr/ADR-0027-duplicados-de-postventa-y-forzar.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `POST /api/v2/reclamos` | ✅ `api-contract.md` §2.6 |
| Ventas | `GET /api/v2/reclamos/me?estado=` con token del cliente (detección de duplicados) | ✅ §2.10b (A15) |
| Ventas | `PATCH /api/v2/reclamos/{id}/respuesta` (solo lo usa el Gestor; el chatbot no lo llama) | ✅ §2.9 (referencia) |
| Ventas | `GET /api/v1/pedidos/me` con token del cliente (selección del pedido) | ✅ §1.4b (A15) |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ClaimForm` (bloque `FORMULARIO/RECLAMO`) | Pedido (solo lectura o selector), tipo, motivo (select con los cinco de G5 y sin `OTRO`), descripción con contador, documento (prellenado si existe), solución esperada, "Enviar reclamo" y "Cancelar". |
| `ClaimReceipt` (bloque `CONSTANCIA_RECLAMO`) | Código destacado con botón para copiar, fecha, plazo (`fechaLimiteSLA`) y "Ver estado" (SPEC-20). |
| `DuplicateClaimNotice` | Aviso de reclamo abierto con el código existente, su estado y "Registrar uno nuevo de todas formas"; al confirmar, el formulario reenvía con `forzar: true`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `preparar_reclamo` | Esquema `{pedidoRef?, tipo?, motivo?, descripcion?, pedidoCliente?}`; devuelve el formulario prellenado con el documento del último pedido (no registra). |
| `POST /api/v1/reclamos` | Endpoint invocado por el botón; valida la pertenencia del pedido, que `motivo` sea uno de los cinco de G5, detecta duplicados vía el listado real y registra con idempotencia. Acepta `forzar` (booleano, por defecto `false`). |
| `ReclamoService` | Borradores, resolución del documento reutilizado, detección de duplicados (previa y autoritativa) y registro. |
| `VentasClient.reclamos` | Cliente de Ventas para registrar, consultar y listar reclamos; normaliza `codigo` → `code`. |
| Tabla `claim_ref` | Ver `modelo-datos.md`. |

### Contrato de `POST /api/v1/reclamos`

- **Sesión:** `CLIENTE`. **Cabecera:** `Idempotency-Key` obligatoria.
- **Cuerpo:** el payload de Ventas de `spec.md` más `forzar` (booleano, por defecto `false`). `forzar` no se reenvía a Ventas: es una decisión del chatbot sobre su propia detección de duplicados. `motivo` solo acepta los cinco valores de G5; no se traducen alias ni se acepta `OTRO`. El formulario usa `descripcion` en la UI y el adapter la envía como `detalle` (mín. 20, máx. 1000).
- **Detección de duplicados (autoritativa):** antes de llamar a Ventas, consulta `GET /api/v1/reclamos` (proxy a `/me`) y busca un reclamo con el mismo `pedidoId` y `motivo` en estado `REGISTRADO` o `EN_PROCESO`. Los estados `ATENDIDO` y `DERIVADO` no cuentan como duplicado.
- **Si hay duplicado y `forzar=false`:** responde `409` con `application/problem+json`:

```json
{
  "status": 409,
  "code": "RECLAMO_DUPLICADO",
  "title": "Duplicate claim",
  "detail": "Ya existe un reclamo abierto para este pedido y motivo.",
  "reclamoId": "REC-2026-0042",
  "codigoSeguimiento": "REC-2026-0042",
  "estado": "EN_PROCESO"
}
```

- **Si hay duplicado y `forzar=true`:** registra el nuevo reclamo en Ventas con una nueva `Idempotency-Key` (la del envío) y responde `201` con la constancia nueva. No se reutiliza el código existente.
- **Si el listado de duplicados falla:** se registra el reclamo (fail-open) y se deja un `warning` con el `X-Correlation-Id`; el cliente no ve un error de duplicados. Supuesto explícito: si el equipo prefiere fail-closed, se responde `503 SERVICIO_NO_DISPONIBLE`.
- **Idempotencia:** dos envíos con la misma `Idempotency-Key` y el mismo `forzar` devuelven la misma constancia y crean un solo reclamo.

### Errores

| `code` | HTTP | Cuándo |
|---|---|---|
| `VALIDACION` | 400 | Faltan campos, la descripción no cumple el mínimo/máximo, el pedido no es del cliente o `motivo` no es uno de los cinco valores de G5. |
| `RECLAMO_DUPLICADO` | 409 | Existe un reclamo abierto para el mismo pedido y motivo y `forzar` es `false`. |
| `SERVICIO_NO_DISPONIBLE` | 503 | Ventas no responde al registrar; se conserva el borrador 24 h. |
| `DEMASIADAS_SOLICITUDES` | 429 | Rate limit de creación. |

G5 también rechaza un motivo fuera de su enum con `400 FORMATO_INVALIDO` (evidencia 2026-11-22, `docs/contratos-integracion.md` §2.10). El BFF valida antes de reenviar y expone `400 VALIDACION`, así que ese código de G5 no se propaga al frontend.

## Desglose para issues

- [ ] `[BE]` Herramienta `preparar_reclamo` con reutilización del documento y motivo validado contra los cinco de G5
- [ ] `[BE]` `ReclamoService`: detección de duplicados (previa y autoritativa), validación de `motivo` (`400 VALIDACION`) y registro con idempotencia
- [ ] `[BE]` `forzar` en `POST /reclamos` y `409 RECLAMO_DUPLICADO` con el código/estado existente
- [ ] `[BE]` `VentasClient.reclamos` (registrar, consultar, listar) con su mock, incluida la normalización de errores
- [ ] `[FE]` `ClaimForm`, `ClaimReceipt` y `DuplicateClaimNotice` con la acción "Registrar uno nuevo de todas formas"
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la detección de duplicados, el `forzar` y la caída del listado
