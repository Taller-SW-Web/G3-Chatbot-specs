# Diseño: Validación de stock

> Origen: SPEC-10 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /inventario/disponibilidad/comercial?skus=A,B,C&canal=CHATBOT` → `{ items: [{ sku, status }] }` con `status ∈ DISPONIBLE, STOCK_BAJO, AGOTADO, INDETERMINADO` (máx. 100 SKU) | 🟡 A5 · scope `inventario:disponibilidad:leer` pendiente · provisional (`D-INV-01`) |

🧩 Productos publicó (HTTP 0.5.0) solo la proyección comercial: el chatbot no recibe `location_id`, `on_hand`, `reserved`, `available` ni cantidades. La validación exacta de cantidades la hace Ventas con `409` al crear el pedido. La ruta sigue provisional hasta que se resuelva `D-INV-01`.

## Frontend

| Componente | Responsabilidad |
|---|---|
| `StockConflictNotice` | Mensaje de línea agotada con la acción "Quitar" y aviso de stock bajo. |
| `AvailabilityBadge` | Disponible, pocas unidades o agotado (en tarjeta y detalle). |
| Productos | `POST /inventario/disponibilidad/comercial/verificar {channel_id, lines[{sku, quantity}]}` → `SUFICIENTE`, `INSUFICIENTE` o `INDETERMINADO`, no vinculante y sin reserva | 🟡 A16 · provisional; falta implementación y scope |
| Manejo de `409` y `503` en `useCartMutations` | Muestra el aviso adecuado sin perder el estado del carrito. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `InventarioClient.disponibilidad(skus)` | Timeout de 3 s, sin caché para las decisiones. |
| `StockValidator.validar_adicion(sku, cantidad)` | Devuelve OK, OK con aviso (`STOCK_BAJO` o `INDETERMINADO`), `SKU_AGOTADO` o `STOCK_INSUFICIENTE` (verificación por cantidad). |
| `StockValidator.validar_carrito(carrito)` | Validación masiva con resultado por línea. |
| Herramienta `consultar_disponibilidad` | Esquema `{productoRef? | product_id?, talla?, color?}`. |
| `SimilaresService` | Busca productos de la misma categoría y rango de precio ±20 % con stock. |

## Desglose para issues

- [ ] `[INT]` Acordar con Productos la consulta masiva de disponibilidad por SKU (A5)
- [ ] `[BE]` `InventarioClient` y `StockValidator` (individual y masivo)
- [ ] `[BE]` `SimilaresService` y la herramienta `consultar_disponibilidad`
- [ ] `[FE]` `StockConflictNotice` y `AvailabilityBadge`
- [ ] `[QA]` Pruebas de todos los escenarios, incluidos el timeout y la carrera "stock bajó entre el agregado y el checkout"
