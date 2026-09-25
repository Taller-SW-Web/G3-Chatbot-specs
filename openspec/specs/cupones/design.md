# Diseño: Cupones de descuento

> Origen: SPEC-13 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `POST /cupones/validar {codigo, canal: CHATBOT, customerRef, lineas[{sku, cantidad}]}` | 🟡 A5 |
| Productos | `POST /promociones/evaluar` con `cupon` (totales combinados) | 🟡 A5 |
| Ventas | Campo `cupon` en `POST /pedidos` | ✅ A8 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `CouponInput` (dentro de `CartBlock`) | Campo y botón "Aplicar"; estados de carga, error con motivo y aplicado con "Quitar". |
| `CartDiscountLines` | Línea "Cupón X: -S/ Y". |
| Avisos de retiro del cupón | Toast o mensaje en el chat. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST/DELETE /api/v1/carrito/cupon` | Aplicar o quitar desde la UI. |
| `CuponService` | Normaliza, valida, guarda en el carrito, revalida y traduce el motivo. |
| `CuponesClient` | Cliente de Productos. |
| `RateLimiter` (cupones) | 5 fallos cada 10 min por cliente. |
| Herramientas `aplicar_cupon` y `quitar_cupon` | Uso desde el chat. |
| Integración con `TotalesCalculator` y `CheckoutService` | Revalidación en los cambios y antes de crear el pedido. |

## Desglose para issues

- [ ] `[INT]` Acordar con Productos el endpoint de validación de cupones y el catálogo de motivos (A5)
- [ ] `[BE]` `CuponService`, `CuponesClient` y los endpoints aplicar/quitar
- [ ] `[BE]` Revalidación en `TotalesCalculator` y `CheckoutService`
- [ ] `[BE]` Rate limit de intentos y herramientas LLM
- [ ] `[FE]` `CouponInput` y los avisos de retiro
- [ ] `[QA]` Pruebas de todos los escenarios y de cada motivo de rechazo
