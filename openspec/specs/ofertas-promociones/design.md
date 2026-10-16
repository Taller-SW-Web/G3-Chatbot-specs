# Diseño: Consulta de ofertas y promociones

> Origen: SPEC-08 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /promociones?canal=CHATBOT&vigentes=true` → `items[{ promotion_id, name, status, valid_from, valid_until, channels }]` | 🟡 A5 · scope `promociones:leer` pendiente |
| Productos | `GET /precios` | 🟡 A5 · scope `precios:leer` pendiente |
| Productos | `POST /promociones/evaluar` (lo usa SPEC-11) → `{ promotion_id, original_amount, discount_amount, result_amount, currency, reason }` | 🟡 A5 · scope `promociones:evaluar` pendiente |

🧩 `GET /promociones` no entrega beneficio, alcance por categoría/marca ni modalidad (`AUTOMATICA`/`CUPON`), y `evaluar` devuelve un solo descuento para la cesta. Productos respondió (A16) que el beneficio y el resumen de promociones se publicarán en una etapa posterior (aún no es contrato); mientras tanto el listado solo muestra nombre y vigencia. El nombre de la promoción en el carrito se resuelve por `promotion_id` contra el listado, sin TTL de caché contractual (los resultados solo se reutilizan dentro del turno); si no se encuentra, la línea dice "Descuento" (comportamiento interino). 🧩 El contrato real usa `precio_regular`, `precio_oferta`, `currency`, `channel_id`, `lines`, `quantity`, `coupon_code` y `customer_ref`; no se puede seguir usando nombres en español camelCase ni `canal`/`lineas`/`cupon`.

## Frontend

| Componente | Responsabilidad |
|---|---|
| `PromotionList` (bloque `LISTA_PROMOCIONES`) | Tarjetas de promoción con beneficio, vigencia y "Ver productos". |
| `PriceTag` | Precio regular tachado, oferta y badge de %; se reutiliza en tarjetas, detalle y carrito. |
| `CartDiscountLines` | Líneas de descuento del carrito con su nombre. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `consultar_promociones` | Esquema `{categoria?, marca?}`. |
| `PromocionesService` | Consulta, filtra por modalidad `AUTOMATICA` y canal, y mapea a `PromocionResumen`. |
| `PricingAdapter` | Normaliza `precio_regular`, `precio_oferta`, `currency` y `ahorroPct`. |
| `EvaluacionClient` | Wrapper de `POST /promociones/evaluar` usando `channel_id`, `lines`, `coupon_code` y `customer_ref`. |

## Desglose para issues

- [x] `[INT]` Acordar con Productos los endpoints reales de promociones, precios y evaluación (A5) — confirmado por Productos el 15/10 (A16)
- [ ] `[BE]` Herramienta `consultar_promociones` y `PromocionesService`
- [ ] `[BE]` `PricingAdapter` y `EvaluacionClient`
- [ ] `[FE]` `PromotionList`, `PriceTag` y `CartDiscountLines`
- [ ] `[QA]` Pruebas de todos los escenarios (incluida la exclusión por canal y por modalidad `CUPON`)
