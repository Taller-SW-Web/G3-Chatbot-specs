# Tasks

## 1. Specs de capacidad

- [x] 1.1 `validacion-stock`: estados comerciales en lugar de cantidades (requisitos 1, 2 y 4).
- [x] 1.2 `busqueda-filtrado`: filtros reales y precio por llamada aparte (requisitos 1 y 3).
- [x] 1.3 `ofertas-promociones`: listado sin beneficio, `precio_oferta` y evaluación única (requisitos 1 a 4).
- [x] 1.4 `gestion-carrito`: descuento único con nombre por `promotion_id` (requisito 3).
- [x] 1.5 `cupones`: tabla por `code` y `customer_ref` (requisitos 1 a 4).
- [x] 1.6 `tarjetas-detalle-producto` y `recomendacion`: `STOCK_BAJO` y descripción nula.

## 2. Diseños y documentos

- [x] 2.1 Tablas de integración de los siete diseños y de `solicitud-devolucion-cambio`.
- [x] 2.2 `docs/contratos-integracion.md` §3.2 y acuerdo A7.

## 3. Pendiente

- [ ] 3.1 Actualizar historias de usuario y reglas (`docs/producto/historias/EP-03-descubrimiento.md`, `EP-04-carrito.md`, reglas RN-CAR-01 y RN-CAR-02) que mencionan cantidades, "pocas unidades ≤ 5", talla/color en búsqueda y beneficio de promociones.
- [ ] 3.2 Recalcular totales de requisitos y escenarios en README y trazabilidad.
- [ ] 3.3 Responder las preguntas pendientes a Productos y ajustar según su respuesta.
- [ ] 3.4 Archivar el cambio en un PR aparte.

## 4. Verificación

- [x] 4.1 `npx @fission-ai/openspec validate alinear-specs-con-productos --strict`
