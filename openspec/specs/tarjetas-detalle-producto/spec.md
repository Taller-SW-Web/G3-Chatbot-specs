# Carrusel, tarjetas y detalle de producto

> Origen: SPEC-09 · Grupo: Descubrimiento · Requiere sesión: No · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`ofertas-promociones`](../ofertas-promociones/spec.md) (SPEC-08), [`validacion-stock`](../validacion-stock/spec.md) (SPEC-10), [`gestion-carrito`](../gestion-carrito/spec.md) (SPEC-11), Productos (SPEC-003 y 004 de Productos)

## Purpose

Presentar los productos de forma visual y accionable, y permitir ver el detalle y elegir la variante exacta (talla y color) para agregarla al carrito.

## Contexto

Una lista de productos en texto plano es difícil de leer en un chat. Cada respuesta con productos se presenta como un carrusel de tarjetas con las que se puede interactuar.

En Productos, un producto puede tener variantes (`tiene_variantes = true`) identificadas por talla, color u otras características LISTA. Cada variante es un SKU vendible con su propia imagen, y el stock se controla por SKU. Por eso no se puede agregar al carrito un producto con variantes sin elegir la variante.

## Alcance

Incluye:
- Tarjeta de producto: imagen, marca, nombre, precio (con oferta), descripción breve, indicador de disponibilidad y los botones "Ver detalle" y "Agregar".
- Carrusel horizontal (máx. 10 tarjetas) con navegación por flechas, swipe y teclado.
- Detalle de producto: galería, descripción, características, selector de variantes con disponibilidad por SKU, cantidad y "Agregar al carrito".
- Selección de la variante por texto ("en talla 42 negra") o por la UI.

### Fuera de alcance

- Reseñas y calificaciones de productos.
- Guía de tallas interactiva (se muestra como enlace si Productos provee la URL).
- Zoom avanzado o vista 360° de las imágenes.

## Requirements

### Requirement: Tarjetas en carrusel
El sistema DEBE (SHALL) representar cada lista de productos como un bloque `CARRUSEL_PRODUCTOS` con tarjetas que contienen los datos de `ProductoResumen`: `productoId`, `nombre`, `marca`, `imagenUrl`, `precio` (`PriceTag`), `descripcionBreve` (máx. 90 caracteres), `tieneVariantes`, `disponibilidad` (`DISPONIBLE`, `POCAS_UNIDADES` si quedan ≤ 5, `AGOTADO`) y `skuUnico` (si no tiene variantes).

*Trazabilidad: SPEC-09 · Requisito 1.*

#### Scenario: Carrusel estándar
- **DADO** una búsqueda con 7 resultados
- **CUANDO** se renderiza el bloque
- **ENTONCES** se muestran 7 tarjetas desplazables horizontalmente, cada una con los datos anteriores y un `alt` descriptivo en la imagen

#### Scenario: Imagen no disponible
- **DADO** un producto cuya imagen no carga
- **CUANDO** se renderiza
- **ENTONCES** se muestra una imagen de reemplazo con el ícono de la categoría, sin romper el diseño

#### Scenario: Producto agotado
- **DADO** un producto con todas sus variantes con `available = 0`
- **CUANDO** se renderiza
- **ENTONCES** la tarjeta muestra "Agotado" y el botón "Agregar" queda deshabilitado, con "Ver similares" como alternativa

### Requirement: Agregar desde la tarjeta
El sistema DEBE (SHALL) agregar directamente los productos sin variantes y DEBE pedir la variante en los productos con variantes.

*Trazabilidad: SPEC-09 · Requisito 2.*

#### Scenario: Producto sin variantes
- **DADO** una pelota con `skuUnico`
- **CUANDO** se pulsa "Agregar"
- **ENTONCES** se envía la acción `AGREGAR_AL_CARRITO {sku, cantidad: 1}` (SPEC-10 y SPEC-11) y aparece la confirmación

#### Scenario: Producto con variantes
- **DADO** unas zapatillas con tallas del 38 al 44
- **CUANDO** se pulsa "Agregar"
- **ENTONCES** se abre el bloque `SELECTOR_VARIANTE` con las tallas y colores disponibles; las variantes agotadas aparecen deshabilitadas

### Requirement: Detalle del producto
El sistema DEBE (SHALL) mostrar el detalle completo con sus variantes activas y la disponibilidad por SKU al pulsar "Ver detalle" o al pedirlo por texto.

*Trazabilidad: SPEC-09 · Requisito 3.*

#### Scenario: Detalle desde la tarjeta
- **DADO** un producto con variantes
- **CUANDO** se pulsa "Ver detalle"
- **ENTONCES** se muestra `DETALLE_PRODUCTO` (hoja expandible dentro de `ChatPage` o `HomePage`) con galería, descripción, características, selector de talla y color, precio de la variante elegida, cantidad (1–10) y "Agregar al carrito"

#### Scenario: Detalle pedido por texto
- **DADO** un carrusel previo
- **CUANDO** el cliente escribe "cuéntame más del tercero"
- **ENTONCES** se invoca `ver_detalle_producto {productoRef: 3}` y se muestra el mismo bloque, más un resumen en texto de 2 líneas

#### Scenario: Producto desactivado
- **DADO** un producto que pasó a `INACTIVO` después de mostrarse
- **CUANDO** se pide su detalle
- **ENTONCES** se informa "Este producto ya no está disponible" y se ofrecen similares

### Requirement: Selección de variante por lenguaje natural
El sistema DEBE (SHALL) resolver la talla y el color expresados en texto a un SKU concreto y preguntar solo lo que falte.

*Trazabilidad: SPEC-09 · Requisito 4.*

#### Scenario: Talla y color completos
- **DADO** el detalle de unas zapatillas con variantes talla×color
- **CUANDO** el cliente escribe "la quiero en 42 negra"
- **ENTONCES** se resuelve el SKU con talla 42 y color negro, se valida el stock y se agrega

#### Scenario: Falta un atributo
- **DADO** un producto con talla y color
- **CUANDO** el cliente escribe "en 42"
- **ENTONCES** se pregunta "¿En qué color?" con chips de los colores disponibles en talla 42

#### Scenario: Combinación inexistente o agotada
- **DADO** que no existe la talla 42 en rojo, o está agotada
- **CUANDO** se solicita
- **ENTONCES** se informa y se ofrecen las alternativas más cercanas (42 en otros colores o rojo en 41 y 43)

## Requisitos no funcionales

- **Rendimiento:** imágenes con `loading="lazy"` y un tamaño de miniatura ≤ 400 px (si Productos ofrece variantes de tamaño); el carrusel mantiene 60 fps al hacer swipe en un móvil de gama media.
- **Accesibilidad:** el carrusel usa `role="region"` con `aria-label`, flechas accesibles, foco visible y navegación con ← →; los botones tienen al menos 44×44 px.
- **Responsive:** en móvil se ve 1,2 tarjetas (con indicio de desplazamiento) y en escritorio 2,5 tarjetas dentro del contenedor de la conversación o del grid de inicio.
- **Consistencia:** los datos de la tarjeta vienen del backend en `ProductoResumen`; el frontend no calcula precios ni disponibilidad.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
