# Diseño

No hay decisiones de arquitectura nuevas. El `ProductosClient` traduce los nombres del BFF (camelCase) al contrato de Productos (`channel_id`, `lines`, `quantity`, `coupon_code`, `customer_ref`). Para armar un carrusel el BFF hace tres llamadas: búsqueda de productos, `GET /precios` y `GET /inventario/disponibilidad/comercial`, ambas por lote de SKU (hasta 100). La ruta de disponibilidad es provisional (`D-INV-01`); el cliente HTTP debe aislarla para poder cambiarla sin tocar el dominio.

## Respuesta de Productos (15/10)

- La verificación por cantidad (`POST /inventario/disponibilidad/comercial/verificar`) y el GET comercial son provisionales: el cliente HTTP los aísla detrás de `InventarioClient`, y si la verificación no está disponible se usa solo el estado.
- `INDETERMINADO` no es `AGOTADO`: el dominio lo trata como "no confirmado" y nunca lo mapea a un rechazo.
- Para armar un carrusel con productos con variantes, el BFF pide hasta 10 detalles por página (no hay endpoint masivo) y agrupa los SKU en consultas de hasta 100. No hay TTL de caché contractual: solo se reutiliza dentro del turno.
- Los códigos de error de identificación o elegibilidad (SKU inexistente, inactivo, no comercializable, sin precio) se distinguen del stock agotado hasta que Productos publique su matriz.
- Ante `429` se respeta `Retry-After` si viene, sin fijar una cuota propia.
