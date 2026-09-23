# Diseño: Validación de stock

> Origen: SPEC-10 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /inventario/disponibilidad?skus=A,B,C` → `[{sku, available, estado}]` (agregado de ubicaciones) | 🟡 A5 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `StockConflictNotice` | Mensaje con las acciones "Ajustar a N" y "Quitar" por línea. |
| `AvailabilityBadge` | Disponible, pocas unidades o agotado (en tarjeta y detalle). |
| Manejo de `409` y `503` en `useCartMutations` | Muestra el aviso adecuado sin perder el estado del carrito. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `InventarioClient.disponibilidad(skus)` | Timeout de 3 s, sin caché para las decisiones. |
| `StockValidator.validar_adicion(sku, cantidadTotal)` | Devuelve OK o `STOCK_INSUFICIENTE` con el disponible. |
| `StockValidator.validar_carrito(carrito)` | Validación masiva con resultado por línea. |
| Herramienta `consultar_disponibilidad` | Esquema `{productoRef? | productoId?, talla?, color?}`. |
| `SimilaresService` | Busca productos de la misma categoría y rango de precio ±20 % con stock. |

## Desglose para issues

- [ ] `[INT]` Acordar con Productos la consulta masiva de disponibilidad por SKU (A5)
- [ ] `[BE]` `InventarioClient` y `StockValidator` (individual y masivo)
- [ ] `[BE]` `SimilaresService` y la herramienta `consultar_disponibilidad`
- [ ] `[FE]` `StockConflictNotice` y `AvailabilityBadge`
- [ ] `[QA]` Pruebas de todos los escenarios, incluidos el timeout y la carrera "stock bajó entre el agregado y el checkout"
