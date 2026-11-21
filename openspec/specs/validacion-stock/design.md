# Diseño: Validación de stock

> Origen: SPEC-10 · Especificación de comportamiento: [`spec.md`](spec.md) · Decisión: [D3](../../../docs/auditoria-specs-2026-11.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /inventario/disponibilidad/comercial?skus=A,B,C&canal=CHATBOT` → `{ items: [{ sku, status }] }` con `status ∈ DISPONIBLE, STOCK_BAJO, AGOTADO, INDETERMINADO` (máx. 100 SKU) | 🟡 A5 · scope `inventario:disponibilidad:leer` pendiente · provisional (`D-INV-01`) |
| Productos | `POST /inventario/disponibilidad/comercial/verificar {channel_id: CHATBOT, fulfillment: {mode: ENVIO_DOMICILIO}, lines[{sku, quantity}]}` → `{evaluated_at, binding: false, items[{sku, requested_quantity, result, reason_code}]}` con `result` ∈ `SUFICIENTE`, `INSUFICIENTE`, `INDETERMINADO`; no vinculante y sin reserva | 🟡 A16 y A17 · provisional; falta implementación y scope |
| `mod-cart` | `ManageCartUseCase.validate_cart(cart)` vía `mod_cart.public` (validación masiva, una sola llamada) | 🟡 En implementación (D3, 2026-11-21) |
| `mod-checkout` | `POST /checkout` invoca `validate_cart` antes de crear checkout/pedido y mapea el resultado a `409 CARRITO_DESACTUALIZADO` | 🟡 En implementación (D3, 2026-11-21) |

🧩 Productos publicó solo la proyección comercial: el chatbot no recibe `location_id`, `on_hand`, `reserved`, `available` ni cantidades. La validación exacta de cantidades la hace Ventas con `409` al crear el pedido. La ruta sigue provisional hasta que se resuelva `D-INV-01`.

🧩 Cierre del 20/10 (A17): `fulfillment` es obligatorio y el chatbot envía siempre `mode: ENVIO_DOMICILIO`, sin `fulfillment_ref` (D1). El resultado se lee de `items[].result`, no de `veredicto`. Un lote incompleto, un SKU que no coincide, un estado desconocido o un payload fuera del esquema es "disponibilidad no obtenida", distinta de `INDETERMINADO` (D2). Ambas llamadas llevan el token de servicio (`aud=api-productos`, scope `inventario:disponibilidad:leer`) y el `X-Correlation-Id` del turno.

## Frontend

| Componente | Responsabilidad |
|---|---|
| `StockConflictNotice` | Mensaje de línea agotada con la acción "Quitar" y aviso de stock bajo. Muestra una entrada por cada elemento de `lineas`. |
| `AvailabilityBadge` | `DISPONIBLE`, `STOCK_BAJO`, `AGOTADO` o `INDETERMINADO` (en tarjeta y detalle). |
| Manejo de `409` y `503` en `useCartMutations` | Muestra el aviso adecuado sin perder el estado del carrito; con `lineas` resalta las líneas afectadas. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `InventarioClient.disponibilidad(skus)` | Timeout de 3 s, sin caché para las decisiones. |
| `StockValidator.validar_adicion(sku, cantidad)` | Devuelve OK, OK con aviso (`STOCK_BAJO` o `INDETERMINADO`, con avisos distintos), `SKU_AGOTADO`, `STOCK_INSUFICIENTE` (verificación por cantidad) o disponibilidad no obtenida (fila ausente, estado desconocido o payload incompatible), que nunca equivale a `SKU_AGOTADO`. |
| `StockValidator.validar_carrito(carrito)` | Validación masiva con resultado por línea; exige correspondencia exacta entre los SKU pedidos y los devueltos. |
| `ManageCartUseCase.validate_cart(carrito)` | Expone el resultado por línea a `mod-checkout` sin que este consulte Inventario por su cuenta. |
| Herramienta `consultar_disponibilidad` | Esquema `{productoRef? \| product_id?, talla?, color?}`. |
| `SimilaresService` | Busca productos de la misma categoría y rango de precio ±20 % con stock. |

### Contrato de la revalidación en `POST /checkout`

`POST /api/v1/checkout` ejecuta, en este orden: carrito existente y no vacío → `validate_cart` → cotización de envío → creación del checkout y del pedido. Si `validate_cart` devuelve al menos una línea bloqueante, no se crea checkout ni pedido y se responde:

```json
{
  "status": 409,
  "code": "CARRITO_DESACTUALIZADO",
  "title": "Cart changed",
  "detail": "Una o más líneas cambiaron desde que las agregaste.",
  "lineas": [
    { "sku": "ZAP-RUN-42-NEG", "nombre": "Zapatilla Run 42/Negro", "cantidad": 2, "motivo": "AGOTADO", "mensaje": "Se agotó mientras elegías." },
    { "sku": "POL-ALG-001-M", "nombre": "Polo Algodón M", "cantidad": 5, "motivo": "STOCK_INSUFICIENTE", "mensaje": "No hay stock suficiente para esa cantidad." }
  ],
  "summary": {
    "lineas": [{ "sku": "ZAP-RUN-42-NEG", "cantidad": 2, "precioUnitario": 299.9 }],
    "subtotal": 599.8,
    "descuento": 0.0,
    "costoEnvio": 12.5,
    "total": 612.3
  }
}
```

Reglas del contrato:

1. `lineas[].motivo` ∈ `AGOTADO | STOCK_INSUFICIENTE | NO_CONFIRMADO`; no incluye cantidades de stock porque Productos no las expone. `NO_CONFIRMADO` cubre una línea cuyo resultado no se pudo interpretar; el checkout no la deja pasar.
2. `summary` es el resumen recalculado por el servidor; el cliente debe confirmar de nuevo. `lineas` es el nombre que ya usa el caso de uso del checkout; si el código cambia de nombre, se actualiza este diseño y el frontend en el mismo PR.
3. Si la validación masiva no puede ejecutarse (timeout, error o payload incompatible), se responde `503 MODULO_NO_DISPONIBLE` con `{modulo: "products"}`; nunca se continúa asumiendo disponibilidad ni se marca `AGOTADO`. Una línea individual que llega `NO_CONFIRMADO` se trata como bloqueante en el `409`.
4. Un `409 STOCK_INSUFICIENTE` de Ventas al crear el pedido se conserva como segunda barrera; el primer rechazo por stock es el de `validate_cart`.
5. El carrito no cambia de estado por un `409`: sigue en `ACTIVE` para que el cliente pueda ajustarlo. No se crea checkout, pedido ni intento de pago.

## Desglose para issues

- [ ] `[INT]` Acordar con Productos la consulta masiva de disponibilidad por SKU (A5)
- [ ] `[BE]` `InventarioClient` y `StockValidator` (individual y masivo)
- [ ] `[BE]` `manage_cart_use_case.validate_cart` con resultado por línea y sin cantidades
- [ ] `[BE]` `POST /checkout` invoca `validate_cart`, responde `409 CARRITO_DESACTUALIZADO` con `lineas` y `503` si no puede validar
- [ ] `[BE]` `SimilaresService` y la herramienta `consultar_disponibilidad`
- [ ] `[FE]` `StockConflictNotice` (una entrada por línea) y `AvailabilityBadge`
- [ ] `[QA]` Pruebas de todos los escenarios, incluidos el timeout, la respuesta incompleta y la carrera "stock bajó entre el agregado y el checkout"
