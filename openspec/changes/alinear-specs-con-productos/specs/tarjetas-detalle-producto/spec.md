## MODIFIED Requirements

### Requirement: Tarjetas en carrusel
El sistema DEBE (SHALL) representar cada lista de productos como un bloque `CARRUSEL_PRODUCTOS` con tarjetas que contienen los datos de `ProductoResumen`: `productoId`, `nombre`, `marca`, `imagenUrl`, `precio` (`PriceTag`), `descripcionBreve` (máx. 90 caracteres, a partir de `description`, omitida si es nula), `tieneVariantes`, `disponibilidad` (`DISPONIBLE`, `STOCK_BAJO`, `AGOTADO`, tal como las entrega Productos) y `skuUnico` (si no tiene variantes).

*Trazabilidad: SPEC-09 · Requisito 1.*

#### Scenario: Carrusel estándar
- **DADO** una búsqueda con 7 resultados
- **CUANDO** se renderiza el bloque
- **ENTONCES** se muestran 7 tarjetas desplazables horizontalmente, cada una con los datos anteriores y un `alt` descriptivo en la imagen

#### Scenario: Imagen no disponible
- **DADO** un producto cuya imagen no carga
- **CUANDO** se renderiza
- **ENTONCES** se muestra una imagen de reemplazo con el ícono de la categoría, sin romper el diseño

#### Scenario: Producto sin descripción
- **DADO** un producto con `description` nula
- **CUANDO** se renderiza la tarjeta
- **ENTONCES** no se muestra el bloque de descripción y el diseño no se rompe

#### Scenario: Producto agotado
- **DADO** un producto con todos sus SKU en `AGOTADO`
- **CUANDO** se renderiza
- **ENTONCES** la tarjeta muestra "Agotado" y el botón "Agregar" queda deshabilitado, con "Ver similares" como alternativa

#### Scenario: Pocas unidades
- **DADO** un SKU en `STOCK_BAJO`
- **CUANDO** se renderiza
- **ENTONCES** la tarjeta muestra "Pocas unidades" sin indicar cantidad

### Requirement: Detalle del producto
El sistema DEBE (SHALL) mostrar el detalle completo (`GET /api/v1/productos/{productoId}?canal=CHATBOT`) con sus variantes y la disponibilidad comercial por SKU al pulsar "Ver detalle" o al pedirlo por texto.

*Trazabilidad: SPEC-09 · Requisito 3.*

#### Scenario: Detalle desde la tarjeta
- **DADO** un producto con variantes
- **CUANDO** se pulsa "Ver detalle"
- **ENTONCES** se muestra `DETALLE_PRODUCTO` (hoja expandible dentro de `ChatPage` o `HomePage`) con galería, descripción (si existe), características, selector de talla y color a partir de `variants[].identifying_attributes`, precio de la variante elegida, cantidad (1–10) y "Agregar al carrito"

#### Scenario: Detalle pedido por texto
- **DADO** un carrusel previo
- **CUANDO** el cliente escribe "cuéntame más del tercero"
- **ENTONCES** se invoca `ver_detalle_producto {productoRef: 3}` y se muestra el mismo bloque, más un resumen en texto de 2 líneas

#### Scenario: Producto desactivado
- **DADO** un producto que pasó a `INACTIVO` después de mostrarse
- **CUANDO** se pide su detalle
- **ENTONCES** se informa "Este producto ya no está disponible" y se ofrecen similares
