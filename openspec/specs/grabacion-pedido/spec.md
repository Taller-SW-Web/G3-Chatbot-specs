# Grabación del pedido

> Origen: SPEC-15 · Grupo: Checkout · Requiere sesión: Sí · Depende de: [`direccion-cotizacion-envio`](../direccion-cotizacion-envio/spec.md) (SPEC-12), [`checkout-pago`](../checkout-pago/spec.md) (SPEC-14), Ventas (F1 y F2)

## Purpose

Registrar en Ventas el pedido del cliente con un snapshot fiel de lo que confirmó, notificar el pago aprobado sin perderlo ante fallos, y liberar los pedidos cuyo pago no se completó.

## Contexto

Ventas y Postventa es el dueño del pedido (M1 — Pedidos). Su `api-contract.md` (v1.2.0) ya no está vacío y define, para el Canal Chatbot:

- La creación del pedido a partir de la solicitud de un canal, en un solo `POST` con los bloques `contacto`, `items`, `cupon`, `envio` y `pago` ya calculados, en estado `CREADO`.
- Una **notificación de pago separada** (`POST /pedidos/{id}/pagos/notificacion`), que transiciona `CREADO → PAGADO` cuando el pago se confirma.
- La anulación de un pedido `CREADO` o `PAGADO` por `PAGO_NO_COMPLETADO`, iniciada por el canal, sin intervención del Gestor.

🧩 Esto reemplaza el contrato provisional que se había supuesto antes (una sola llamada `PATCH /estado` para notificar el pago): ahora es un endpoint dedicado, con su propio formato.

## Alcance

Incluye:
- Creación del pedido `CREADO` en Ventas al confirmar el checkout, con `Idempotency-Key`, usando exactamente los campos de `api-contract.md` §1.1.
- Construcción del snapshot: `contacto` (incluye documento, SPEC-12), `items`, `cupon`, `envio` y `pago` (totales proyectados).
- Notificación del pago aprobado mediante `POST /pagos/notificacion`, con reintentos por outbox.
- Solicitud de anulación de los pedidos `CREADO`/`PAGADO` con pago fallido o checkout expirado.
- Referencia local (`pedido_ref`) y cierre del carrito.
- Bloque `CONFIRMACION_PEDIDO` en el chat.

### Fuera de alcance

- Consumo de stock y solicitud de despacho: los desencadena Ventas.
- Anulación a pedido del cliente de un pedido ya pagado y en preparación: es F2 de Ventas con autorización del Gestor; no se ofrece en este canal.
- Emisión del comprobante de pago.

## Requirements

### Requirement: Crear el pedido en Ventas
El sistema DEBE (SHALL) enviar a Ventas la solicitud de creación con el snapshot completo al confirmar el checkout, y guardar la referencia local.

Payload real `POST {VEN}/api/v1/pedidos`:
```json
{
  "canal": "CHATBOT",
  "contacto": {
    "clienteId": "<sub>",
    "nombreCompleto": "Juan Pérez Rodríguez",
    "tipoDocumento": "DNI",
    "numeroDocumento": "72458912",
    "telefono": "+51999888777",
    "email": "juan.perez@example.com"
  },
  "items": [
    { "productoId": "P-100", "sku": "ZAP-RUN-42-NEG", "descripcion": "Zapatilla X 42/Negro",
      "cantidad": 1, "precioUnitario": 299.90 }
  ],
  "cupon": { "codigo": "RUN10", "descuento": 30.00, "aplicado": true },
  "envio": {
    "modalidad": "DELIVERY", "costo": 12.50, "destinatario": "Juan Pérez",
    "departamento": "Lima", "provincia": "Lima", "distrito": "Miraflores",
    "direccion": "Av. Larco 1234, dpto. 502", "referencia": "Frente al parque Kennedy"
  },
  "pago": {
    "metodoPago": "TARJETA_CREDITO", "moneda": "PEN",
    "subtotal": 299.90, "descuentoCupon": 30.00, "costoEnvio": 12.50, "total": 282.40
  }
}
```

*Trazabilidad: SPEC-15 · Requisito 1.*

#### Scenario: Pedido creado
- **DADO** un checkout confirmado y revalidado (SPEC-14)
- **CUANDO** Ventas responde `201 {pedidoId, estado: CREADO, total, moneda, canal, fechaCreacion}`
- **ENTONCES** se guarda `pedido_ref` (`CREADO`) ligada al checkout y se habilita el formulario de pago

#### Scenario: Ventas rechaza por stock
- **DADO** un SKU que se agotó entre la revalidación y la creación
- **CUANDO** Ventas responde `409 Conflict`
- **ENTONCES** no se crea el checkout de pago, el carrito vuelve a `ACTIVO`, se ejecuta la revalidación de SPEC-10 y se muestra al cliente qué cambió

#### Scenario: Datos incompletos
- **DADO** un snapshot al que le falta el documento o la dirección (por un error de validación en el frontend que no se detectó antes)
- **CUANDO** Ventas responde `400 Bad Request`
- **ENTONCES** se registra como error interno (no debería ocurrir si SPEC-12 y SPEC-14 validaron bien) y se muestra "No pudimos registrar tu pedido, revisa tus datos e intenta de nuevo"

#### Scenario: Ventas no disponible al crear
- **DADO** que Ventas no responde en 5 s
- **CUANDO** se confirma el checkout
- **ENTONCES** se responde `503 SERVICIO_NO_DISPONIBLE`, no se pide la tarjeta y se muestra "No pudimos registrar tu pedido. No se realizó ningún cobro. Intenta en unos minutos"

#### Scenario: Reintento con la misma clave
- **DADO** un timeout en el que Ventas sí creó el pedido
- **CUANDO** el cliente reintenta
- **ENTONCES** se reenvía la misma `Idempotency-Key` y se obtiene el mismo `pedidoId`, sin duplicar el pedido

### Requirement: Notificar el pago aprobado
El sistema DEBE (SHALL) notificar a Ventas el pago aprobado a través del endpoint dedicado, con los datos de la transacción, y garantizar su entrega aunque Ventas falle temporalmente.

Payload real `POST {VEN}/api/v1/pedidos/{pedidoId}/pagos/notificacion`:
```json
{
  "transaccionId": "SIM-...",
  "resultado": "APROBADO",
  "monto": 282.40,
  "moneda": "PEN",
  "metodo": "TARJETA_CREDITO",
  "marcaTarjeta": "VISA",
  "ultimosCuatroDigitos": "1111",
  "fechaPago": "2026-09-22T21:41:00Z",
  "codigoAutorizacion": "SIM-AUTH-..."
}
```

*Trazabilidad: SPEC-15 · Requisito 2.*

#### Scenario: Notificación exitosa
- **DADO** un pago aprobado
- **CUANDO** se registra en el outbox (`NOTIFICAR_PAGO_VENTAS`) en la misma transacción que el intento de pago y el worker lo envía y recibe `200 {pedidoId, nuevoEstado: PAGADO, transaccionId, fechaTransicion}`
- **ENTONCES** `pedido_ref` pasa a `PAGADO_NOTIFICADO`, el checkout a `CONFIRMADO` y el carrito a `CONVERTIDO`, se encola el correo (SPEC-16) y el chat muestra `CONFIRMACION_PEDIDO` con el número de pedido, el total, la tarjeta `•••• 1111`, la dirección y "Te enviamos la confirmación a m****a@…"

#### Scenario: Ventas cae después del cobro
- **DADO** un pago aprobado y Ventas sin responder
- **CUANDO** falla la notificación
- **ENTONCES** el worker reintenta con backoff exponencial (5 intentos: 5 s, 15 s, 45 s, 2 min y 5 min); el chat muestra "Pago aprobado. Estamos confirmando tu pedido PED-…"; si se agotan los intentos, el registro queda `FALLIDO` para revisión manual

#### Scenario: Montos inconsistentes
- **DADO** que el monto notificado no coincide con el total del pedido
- **CUANDO** Ventas valida
- **ENTONCES** responde `400 Bad Request`; el worker no reintenta automáticamente (es un error de programación, no transitorio) y se alerta para revisión

#### Scenario: Pedido en un estado que no admite la notificación
- **DADO** un pedido que ya no está `CREADO` (por ejemplo, se anuló por expiración justo antes de que llegara la notificación tardía)
- **CUANDO** se notifica el pago
- **ENTONCES** Ventas responde `409 Conflict`; el worker registra la inconsistencia para revisión manual y **no reintenta** (reintentar no resolvería el conflicto)

### Requirement: Anular los pedidos no pagados
El sistema DEBE (SHALL) solicitar a Ventas la anulación de un pedido `CREADO` o `PAGADO` cuando el checkout termina en `FALLIDO` (3 rechazos) o `EXPIRADO`, con el motivo `PAGO_NO_COMPLETADO`.

Payload real `POST {VEN}/api/v1/pedidos/{pedidoId}/anulaciones`:
```json
{ "motivo": "PAGO_NO_COMPLETADO", "comentario": "Tiempo límite de espera agotado; cancelado por el canal" }
```

*Trazabilidad: SPEC-15 · Requisito 3.*

#### Scenario: Anulación directa
- **DADO** un checkout `FALLIDO` o `EXPIRADO` con un pedido `CREADO`
- **CUANDO** se procesa el outbox `SOLICITAR_ANULACION`
- **ENTONCES** Ventas responde `200 {pedidoId, estadoPedido: ANULADO, autorizacionRequerida: false, solicitudReembolsoGenerada: false}` (no `202`, porque `PAGO_NO_COMPLETADO` sobre `CREADO`/`PAGADO` no requiere autorización del Gestor) y `pedido_ref` pasa a `ANULADO`

#### Scenario: Pedido ya avanzó de estado
- **DADO** que Ventas responde `409 Conflict` porque el pedido ya está `DESPACHADO` o `ENTREGADO`
- **CUANDO** se procesa
- **ENTONCES** se registra la alerta para revisión manual y no se reintenta (en ese punto correspondería una devolución, SPEC-21, no una anulación)

### Requirement: Coherencia del snapshot
El sistema DEBE (SHALL) enviar a Ventas exactamente los importes mostrados y confirmados por el cliente: `pago.subtotal − pago.descuentoCupon + pago.costoEnvio = pago.total`.

*Trazabilidad: SPEC-15 · Requisito 4.*

#### Scenario: Verificación del total
- **DADO** un snapshot armado
- **CUANDO** se valida antes del envío
- **ENTONCES** si la suma no cuadra a 0,01 se aborta con un error interno y no se crea el pedido

#### Scenario: Líneas no disponibles
- **DADO** una línea marcada como "Ya no disponible"
- **CUANDO** se arma el snapshot
- **ENTONCES** se excluye del arreglo `items` y el resumen ya la había mostrado como excluida

## Requisitos no funcionales

- **Confiabilidad:** patrón outbox transaccional para la notificación de pago y las anulaciones; ningún pago aprobado se queda sin notificar sin una alerta.
- **Idempotencia:** `Idempotency-Key` en la creación = `checkout.idempotency_key`; en la notificación se usa `transaccionId` como clave.
- **Trazabilidad:** se registran `pedidoId`, `checkoutId`, `transaccionId` y los tiempos de cada paso con un `correlationId` propagado a Ventas en la cabecera `X-Correlation-Id`.
- **Rendimiento:** la creación del pedido tarda p95 ≤ 1,5 s (incluye la validación de Ventas con Productos).
- **Mapeo de errores:** Ventas responde errores con la clave `codigo` (no `code`); `VentasClient` normaliza al `code` interno del chatbot antes de propagarlo.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
