# Tasks

## 1. Specs de capacidad

- [x] 1.1 `validacion-stock`: estados comerciales en lugar de cantidades (requisitos 1, 2 y 4).
- [x] 1.2 `busqueda-filtrado`: filtros reales y precio por llamada aparte (requisitos 1 y 3).
- [x] 1.3 `ofertas-promociones`: listado sin beneficio, `precio_oferta` y evaluación única (requisitos 1 a 4).
- [x] 1.4 `gestion-carrito`: descuento único con nombre por `promotion_id` (requisito 3).
- [x] 1.5 `cupones`: tabla por `code` y `customer_ref` (requisitos 1 a 4).
- [x] 1.6 `tarjetas-detalle-producto` y `recomendacion`: `STOCK_BAJO` y descripción nula.

## 2. Diseños y documentos

- [x] 2.1 Tablas de integración de los diseños afectados (incluido `gestion-carrito`) y de `solicitud-devolucion-cambio`.
- [x] 2.2 `docs/contratos-integracion.md` §3.2 y acuerdo A7.

## 3. Pendiente

- [x] 3.1 Actualizar historias de usuario y reglas (`docs/producto/historias/EP-03-descubrimiento.md`, `EP-04-carrito.md`, reglas RN-CAR-01 y RN-CAR-02) que mencionan cantidades, "pocas unidades ≤ 5", talla/color en búsqueda y beneficio de promociones. Hecho al archivar: términos de stock, talla y color, orden por precio, beneficio y modalidad de promociones (RN-CAT-11, RN-CAT-14, RN-CAR-01, `intenciones.md`, `dialogos-ejemplo.md`), criterios de aceptación con los escenarios nuevos (EP-03, EP-04, EP-05) y `docs/casos-prueba-hito-3.md` (SPEC-06, 09, 10 y 11).
- [x] 3.2 Recalcular totales de requisitos y escenarios en README y trazabilidad (119 requisitos, 399 escenarios, 374 citados por historias).
- [x] 3.3 Responder las preguntas pendientes a Productos y ajustar según su respuesta (respondidas por Productos el 15/10, acuerdo A16; ver 5.1).
- [x] 3.4 Archivar el cambio en un PR aparte.
- [ ] 3.5 Cuando Productos publique las ampliaciones (filtros de variantes, orden por precio, resumen de promociones, desglose por línea, monto faltante, matriz de errores y límites), reemplazar los comportamientos interinos y actualizar los specs.
- [ ] 3.6 Confirmar con Seguridad (#33) el registro y la concesión de los siete scopes.

## 4. Verificación

- [x] 4.1 `npx @fission-ai/openspec validate alinear-specs-con-productos --strict`

## 5. Respuesta de Productos (15/10)

- [x] 5.1 Ajustar los deltas y diseños a la respuesta de Productos (`INDETERMINADO`, verificación por cantidad, SKU por variantes, tratamiento de errores, acuerdo A16).

## 6. Cierre de compatibilidad de Productos (20/10, A17)

- [x] 6.1 `validacion-stock`: `fulfillment` con `ENVIO_DOMICILIO` y `items[].result` (D1); requisito 3 con respuestas incompletas o incompatibles distintas de `INDETERMINADO` (D2); aviso de `INDETERMINADO` distinto del de `STOCK_BAJO`.
- [x] 6.2 `tarjetas-detalle-producto`: "Precio no disponible" en lugar de `S/ 0.00` y disponibilidad sin valor por defecto.
- [x] 6.3 Diseños de `validacion-stock`, `busqueda-filtrado`, `gestion-carrito` y `tarjetas-detalle-producto`, y `docs/contratos-integracion.md` §3.2 y acuerdo A17 (token de servicio, `X-Correlation-Id`, `canal`, sin `estado`, adaptadores falsos).
- [ ] 6.4 Responder D1 a D3 en G6-Productos-Ofertas-docs #87.
- [ ] 6.5 Abrir los issues de backend y frontend con las correcciones de código.
- [ ] 6.6 Definir con Mathias el entorno de la homologación con `MODULES_MODE=http` (D3).
