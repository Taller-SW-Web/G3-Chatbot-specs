# Tasks

## 1. Spec

- [x] 1.1 `consulta-estado-pedido`: documentar `desde`/`hasta` como fechas ISO `YYYY-MM-DD` que filtran por `fechaCreacion` y se reenvían a `GET /api/v1/pedidos/me`.
- [x] 1.2 Agregar el escenario de filtro por rango y el de fecha inválida (`400 VALIDACION`).

## 2. Contratos y diseño

- [x] 2.1 `docs/contratos-integracion.md` §2.5.2: parámetros y errores de `GET /api/v1/pedidos`.
- [x] 2.2 `docs/contratos-integracion.md` §3.3: reflejar `desde`/`hasta` en `GET /api/v1/pedidos/me`.
- [x] 2.3 `openspec/specs/consulta-estado-pedido/design.md`: integración y reenvío sin transformación.

## 3. Producto

- [x] 3.1 Regla de negocio del listado con filtros de fecha.
- [x] 3.2 Criterios de aceptación y trazabilidad de la historia de seguimiento.

## 4. Validación y archivo

- [x] 4.1 `npx --yes @fission-ai/openspec validate --specs`.
- [x] 4.2 Aplicar las deltas a la spec base y archivar el cambio.
