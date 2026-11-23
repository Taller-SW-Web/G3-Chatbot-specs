# Alinear el listado de pedidos con los filtros de fecha de G5

## Why

G5 publicó los filtros opcionales `desde` y `hasta` para `GET /api/v1/pedidos/me`, y el BFF ya los
implementa en `GET /api/v1/pedidos`. La spec vigente de `consulta-estado-pedido` solo describe el
filtro por `estado` y la paginación, así que el contrato del canal queda incompleto para el change
manager del backend.

## What Changes

- **`consulta-estado-pedido` (SPEC-17), Requisito 1:** el listado acepta los parámetros opcionales
  `desde` y `hasta`, fechas ISO `YYYY-MM-DD` que filtran por `fechaCreacion`.
- Los filtros se reenvían **sin transformación** a `GET /api/v1/pedidos/me` de Ventas; `estado`,
  `page` y `pageSize` conservan su contrato actual.
- Una fecha inválida responde `400 VALIDACION` con `errores[{campo, mensaje}]`, sin llamar a Ventas.
- `docs/contratos-integracion.md` §2.5.2 y §3.3 reflejan los mismos parámetros.
- El diseño de `consulta-estado-pedido` y las reglas de producto se actualizan para no dejar el
  listado descrito a medias.

## Capabilities

- `consulta-estado-pedido`: MODIFIED Requisito 1.

## Impacto

- **Backend (`mod-orders`):** el endpoint ya implementa los filtros; el cambio fija el contrato y la
  validación (`YYYY-MM-DD`, `400 VALIDACION`).
- **Frontend:** no se agrega una pantalla ni un control nuevo; si la UI usa los filtros, consume el
  mismo contrato.
- **Datos:** sin migraciones ni columnas nuevas.

## Fuera de alcance

- Agregar otros filtros, endpoints o formatos de fecha distintos de `YYYY-MM-DD`.
- Cambiar la paginación, el orden o el mapeo de estados.
- Modificar la consulta de detalle o el seguimiento.

## Rollback

Si hubiera que revertir, se retiran `desde`/`hasta` del contrato y se vuelve al listado solo por
`estado`; no hay datos persistidos que migrar.
