# Diseño: Consulta de ofertas y promociones

> Origen: SPEC-08 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /promociones?canal=CHATBOT&vigentes=true&categoriaId=&marcaId=` | 🟡 A5 |
| Productos | `GET /precios?skus=&canal=CHATBOT` (`precioRegular`, `precioOferta` y vigencia) | 🟡 A5 |
| Productos | `POST /promociones/evaluar` (lo usa SPEC-11) | 🟡 A5 |

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
| `PricingAdapter` | Normaliza `precioRegular`, `precioOferta` y `ahorroPct`. |
| `EvaluacionClient` | Wrapper de `POST /promociones/evaluar` (lo usa SPEC-11). |

## Desglose para issues

- [ ] `[INT]` Acordar con Productos los endpoints de promociones, precios y evaluación (A5)
- [ ] `[BE]` Herramienta `consultar_promociones` y `PromocionesService`
- [ ] `[BE]` `PricingAdapter` y `EvaluacionClient`
- [ ] `[FE]` `PromotionList`, `PriceTag` y `CartDiscountLines`
- [ ] `[QA]` Pruebas de todos los escenarios (incluida la exclusión por canal y por modalidad `CUPON`)
