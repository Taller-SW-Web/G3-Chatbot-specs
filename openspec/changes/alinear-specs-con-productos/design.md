# Diseño

No hay decisiones de arquitectura nuevas. El `ProductosClient` traduce los nombres del BFF (camelCase) al contrato de Productos (`channel_id`, `lines`, `quantity`, `coupon_code`, `customer_ref`). Para armar un carrusel el BFF hace tres llamadas: búsqueda de productos, `GET /precios` y `GET /inventario/disponibilidad/comercial`, ambas por lote de SKU (hasta 100). La ruta de disponibilidad es provisional (`D-INV-01`); el cliente HTTP debe aislarla para poder cambiarla sin tocar el dominio.
