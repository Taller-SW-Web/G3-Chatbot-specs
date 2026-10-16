# Alinear las specs con el contrato real de Productos

## Why

Productos y Ofertas publicó su contrato HTTP 0.5.0 y su `ALINEACION_CHATBOT.md` (07/10/2026). Varias specs del chatbot asumían datos que el contrato no entrega (cantidades de stock, filtros por talla y color, beneficio de cada promoción, desglose de descuento por línea). Este cambio las alinea para que los desarrolladores construyan contra lo que realmente existe.

## What Changes

- **Stock:** pasa de cantidades (`available`) a la proyección comercial `DISPONIBLE`, `STOCK_BAJO`, `AGOTADO`, `INDETERMINADO` (`GET /inventario/disponibilidad/comercial`) y a la verificación por cantidad no vinculante (`POST .../verificar`). El escenario "Stock parcial" se reinterpreta para `STOCK_BAJO` (ya no ajusta a una cantidad) y se elimina la acción "Ajustar a N"; la validación exacta de cantidades queda en Ventas (`409`).
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

Productos respondió el 15/10/2026 en el issue #87 (acuerdo A16). Quedó confirmado lo que sigue y se refleja en este cambio:

- Estados de disponibilidad con `INDETERMINADO` y verificación por cantidad no vinculante; el umbral de `STOCK_BAJO` es global con ajuste por SKU, y no se promete ni se calcula una cantidad.
- Precio y stock se consultan aparte de la búsqueda, por lotes de hasta 100 SKU; los SKU de las variantes salen del detalle (sin endpoint masivo).
- Los siete scopes son los de `modulo-chatbot`; falta el registro y la concesión en Seguridad.

Decisiones interinas asumidas (confirmar con el equipo; se reemplazan cuando Productos publique sus ampliaciones):

1. **Talla y color:** viajan en `q` solo como ayuda, sin prometer que filtren, y se confirman en el detalle.
2. **"Más baratas":** se reduce `precioMax` al percentil 50 hasta que exista `PRECIO_ASC`/`PRECIO_DESC`.
3. **Promociones:** se muestran con nombre y vigencia; el nombre de la promoción aplicada en el carrito se busca por `promotion_id` y, si no aparece, se dice "Descuento".
4. **`INDETERMINADO`:** se acepta con aviso y no bloquea el checkout; Ventas confirma el stock al crear el pedido.
5. **Verificación por cantidad:** es provisional; si no está disponible, se usa solo el estado comercial.

Pendiente de Productos (etapa posterior, sin fecha): filtros de variantes, orden por precio, resumen y alcance de promociones, desglose por línea, monto faltante del cupón, pauta de caché y concurrencia, y la matriz de errores y límites (SKU inexistente o inactivo, validaciones, `429`).
