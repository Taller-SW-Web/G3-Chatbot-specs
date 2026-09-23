# Diseño: Creación de reclamo

> Origen: SPEC-19 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `POST /api/v2/reclamos` | ✅ `api-contract.md` §2.6 |
| Ventas | `GET /api/v2/reclamos?clienteId=&estado=` (detección de duplicados) | ✅ §2.8 |
| Ventas | `PATCH /api/v2/reclamos/{id}/respuesta` (solo lo usa el Gestor; el chatbot no lo llama) | ✅ §2.9 (referencia) |
| Ventas | `GET /api/v1/pedidos?clienteId=` (selección del pedido) | ✅ |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ClaimForm` (bloque `FORMULARIO/RECLAMO`) | Pedido (solo lectura o selector), tipo, motivo (select), descripción con contador, documento (prellenado si existe), solución esperada, "Enviar reclamo" y "Cancelar". |
| `ClaimReceipt` (bloque `CONSTANCIA_RECLAMO`) | Código destacado con botón para copiar, fecha, plazo (`fechaLimiteSLA`) y "Ver estado" (SPEC-20). |
| `DuplicateClaimNotice` | Aviso de reclamo abierto con el código existente, su estado y "Registrar uno nuevo de todas formas". |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `preparar_reclamo` | Esquema `{pedidoRef?, tipo?, motivo?, descripcion?, pedidoCliente?}`; devuelve el formulario prellenado con el documento del último pedido (no registra). |
| `POST /api/v1/reclamos` | Endpoint invocado por el botón; valida la pertenencia del pedido, detecta duplicados vía el listado real y registra con idempotencia. |
| `ReclamoService` | Borradores, resolución del documento reutilizado, detección de duplicados y registro. |
| `VentasClient.reclamos` | Cliente de Ventas para registrar, consultar y listar reclamos; normaliza `codigo` → `code`. |
| Tabla `reclamo_ref` | Ver `modelo-datos.md`. |

## Desglose para issues

- [ ] `[BE]` Herramienta `preparar_reclamo` con reutilización del documento
- [ ] `[BE]` `ReclamoService`: detección de duplicados (vía listado real) y registro con idempotencia
- [ ] `[BE]` `VentasClient.reclamos` (registrar, consultar, listar) con su mock, incluida la normalización de errores
- [ ] `[FE]` `ClaimForm`, `ClaimReceipt` y `DuplicateClaimNotice`
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la detección de duplicados
