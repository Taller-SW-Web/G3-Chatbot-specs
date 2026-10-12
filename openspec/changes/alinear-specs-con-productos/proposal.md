# Alinear las specs con el contrato real de Productos

## Why

Productos y Ofertas publicó su contrato HTTP 0.5.0 y su `ALINEACION_CHATBOT.md` (07/10/2026). Varias specs del chatbot asumían datos que el contrato no entrega (cantidades de stock, filtros por talla y color, beneficio de cada promoción, desglose de descuento por línea). Este cambio las alinea para que los desarrolladores construyan contra lo que realmente existe.

## What Changes

- **Stock:** pasa de cantidades (`available`) a la proyección comercial `DISPONIBLE`, `STOCK_BAJO`, `AGOTADO` (`GET /inventario/disponibilidad/comercial`). Se elimina el escenario "Stock parcial" y la acción "Ajustar a N"; la validación exacta de cantidades queda en Ventas (`409`).
- **Búsqueda:** solo filtros reales (`q`, categoría, marca, precio mínimo y máximo, orden por nombre). Talla y color viajan en `q`. "Más baratas" reduce `precioMax`. Precio y disponibilidad se piden aparte por SKU.
- **Ofertas:** el listado de promociones muestra nombre y vigencia; las ofertas por producto vienen de `precio_oferta`. Se elimina el filtrado de promociones por categoría o marca y la exclusión por modalidad.
- **Carrito:** el descuento es un único importe con el nombre resuelto por `promotion_id`.
- **Cupones:** el rechazo se traduce desde el `code` de Productos (lista cerrada); `customer_ref` es el `sub` del cliente.
- **Tarjetas y recomendación:** `disponibilidad` usa `STOCK_BAJO` en lugar de `POCAS_UNIDADES`; la descripción nula no rompe la tarjeta.
- Actualizar `docs/contratos-integracion.md` §3.2 y los diseños afectados; cerrar A7.

## Capabilities

- `validacion-stock`: MODIFIED requisitos 1, 2 y 4.
- `busqueda-filtrado`: MODIFIED requisitos 1 y 3.
- `ofertas-promociones`: MODIFIED requisitos 1 a 4.
- `gestion-carrito`: MODIFIED requisito 3.
- `cupones`: MODIFIED requisitos 1 a 4.
- `tarjetas-detalle-producto`: MODIFIED requisitos 1 y 3.
- `recomendacion`: MODIFIED requisito 2.

## Questions to Confirm

Decisiones asumidas por defecto (confirmar con el equipo):

1. **Sin cantidades:** con `STOCK_BAJO` se permite agregar con aviso; solo `AGOTADO` bloquea.
2. **"Más baratas":** se reduce `precioMax` al percentil 50 de los precios previos, porque Productos no ordena por precio.
3. **Promociones:** se muestran sin beneficio detallado ni filtro por categoría o marca.
4. **Talla y color:** se envían como texto en `q` y se confirman en el detalle.

Preguntas pendientes para Productos:

- ¿`GET /promociones` incluye promociones de cupón? ¿Planean exponer beneficio y alcance?
- ¿La búsqueda puede traer precio, disponibilidad y SKU de productos con variantes?
- ¿Planean exponer cantidades o filtros de talla y color?
