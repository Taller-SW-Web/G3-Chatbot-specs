# Diseño: Consulta de ofertas y promociones

> Origen: SPEC-08 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /promociones` | 🟡 A5 · scope `promociones:leer` pendiente |
| Productos | `GET /precios` | 🟡 A5 · scope `precios:leer` pendiente |
| Productos | `POST /promociones/evaluar` (lo usa SPEC-11) | 🟡 A5 · scope `promociones:evaluar` pendiente |

🧩 El contrato real usa `precio_regular`, `precio_oferta`, `currency`, `channel_id`, `lines`, `quantity`, `coupon_code` y `customer_ref`; no se puede seguir usando nombres en español camelCase ni `canal`/`lineas`/`cupon`.

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

- [ ] `[INT]` Acordar con Productos los endpoints reales de promociones, precios y evaluación (A5)
- [ ] `[BE]` Herramienta `consultar_promociones` y `PromocionesService`
- [ ] `[BE]` `PricingAdapter` y `EvaluacionClient`
- [ ] `[FE]` `PromotionList`, `PriceTag` y `CartDiscountLines`
- [ ] `[QA]` Pruebas de todos los escenarios (incluida la exclusión por canal y por modalidad `CUPON`)
