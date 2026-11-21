# ADR-0012: `Idempotency-Key` en toda operación que crea algo en otro módulo o mueve dinero

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; convención del README §5, sin fecha)

## Contexto

- En móvil son frecuentes los reintentos por red inestable, los dobles toques y las recargas.
- Crear un pedido, cobrar, registrar un reclamo o una devolución dos veces tiene consecuencias económicas o legales (Libro de Reclamaciones).
- El outbox reintenta automáticamente las notificaciones ([ADR-0011](ADR-0011-outbox-transaccional.md)).
- Ventas acepta `Idempotency-Key` en `POST /api/v1/pedidos` (`contratos-integracion.md` §3.3).

## Decisión

Toda operación que crea algo en otro módulo o mueve dinero lleva una **`Idempotency-Key`**, y el chatbot guarda la clave con restricción de unicidad:

| Operación | Endpoint propio | Clave |
|---|---|---|
| Crear checkout y pedido en Ventas | `POST /checkout` | `checkout.idempotency_key` (única); se reenvía la misma a `POST /api/v1/pedidos` y se obtiene el mismo `pedidoId` |
| Pago simulado | `POST /checkout/{id}/pago` | `payment_attempt.idempotency_key` (única), una por intento |
| Notificación de pago a Ventas | Outbox | `transaccionId` |
| Registrar reclamo | `POST /reclamos` | `claim_ref.idempotency_key` (única) |
| Registrar devolución o cambio | `POST /devoluciones` | `return_ref.idempotency_key` (única) |
| Correo de confirmación | Outbox | Unicidad `(order_id, resend_number)` en `notification` |
| Reenviar la confirmación | `POST /pedidos/{id}/reenviar-confirmacion` | Cabecera obligatoria; se deduplica por cliente, pedido y clave: la misma clave devuelve la misma respuesta, sin otro correo y sin consumir un reenvío |
| Sugerencia o reporte de bug | `POST /sugerencias` | `feedback_suggestion.idempotency_key` (única) |

Dos solicitudes con la misma clave devuelven el mismo resultado sin duplicar el efecto. Para el pago, "el mismo resultado" significa el resultado **original**: repetir la clave de un intento rechazado devuelve el mismo error `402 PAGO_RECHAZADO` (o `503 ERROR_PROCESAMIENTO`), nunca una aprobación (ver `contratos-integracion.md` §2.5.1).

Las operaciones con clave natural no llevan `Idempotency-Key`: `POST /mensajes/{id}/reaccion` (upsert por mensaje), `POST /pedidos/{id}/valoracion-compra` (una por pedido, `409 VALORACION_YA_REGISTRADA`) y `POST /pedidos/{id}/csat` (una por pedido, `order_ref.csat_sent`).

> **Alineación 2026-11-21.** La lista anterior omitía el reenvío de confirmación y las sugerencias, que el backend ya exige (`orders_router.py:208`, `feedback_router.py:85-90`, `notification_service.py:182`). Se amplía la tabla al comportamiento implementado.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Deduplicar solo en el frontend deshabilitando botones (*alternativa estándar, no documentada*) | No cubre reintentos de red, recargas ni los reintentos del worker; se usa como complemento (botón "Procesando…"), no como garantía |

## Consecuencias

**Positivas**
- Los reintentos del frontend y del outbox son seguros; no hay pedidos, cobros, reclamos ni devoluciones duplicados.
- Cada escenario de idempotencia tiene su prueba en la spec (SPEC-14 · Req. 2 y 5; SPEC-15 · Req. 1; SPEC-19 · Req. 2; SPEC-21 · Req. 4).

**Negativas y riesgos aceptados**
- El frontend debe generar y conservar la clave durante los reintentos de una misma operación.
- El nombre de la cabecera no es uniforme en las specs: SPEC-19 indica `X-Idempotency-Key` hacia Ventas, el resto usa `Idempotency-Key`. Pendiente de confirmar contra el contrato de Ventas.

## Referencias

- `README.md` §5, Idempotencia
- `openspec/specs/checkout-pago/spec.md` (líneas 32, 72, 80, 154 y 177)
- `openspec/specs/grabacion-pedido/spec.md` (líneas 22, 94 y 174)
- `openspec/specs/creacion-reclamo/spec.md` Req. 2 (líneas 63 y 95)
- `openspec/specs/solicitud-devolucion-cambio/spec.md` Req. 4 (líneas 109 y 141)
- `docs/modelo-datos.md` tablas `checkout`, `payment_attempt`, `claim_ref`, `return_ref`, `notification`
