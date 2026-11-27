# Diseño: Carrusel, tarjetas y detalle de producto

> Origen: SPEC-09 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /productos/{productoId}?canal=CHATBOT` | 🟡 A5 · scope `catalogo:leer` pendiente |
| Productos | `GET /inventario/disponibilidad/comercial?skus=&canal=CHATBOT` → `sku`, `status` (`DISPONIBLE`, `STOCK_BAJO`, `AGOTADO`, `INDETERMINADO`) | 🟡 A5 · scope pendiente |
| Productos | `GET /precios` | 🟡 A5 · scope `precios:leer` pendiente |

🧩 Productos entrega `product_id`, `name`, `description`, `images`, `tiene_variantes`, `sku_base` y `variants`; el BFF normaliza a `product_id`, `name`, `short_description`, `image`, `has_variants`, `single_sku` y `variants[]` (`sku`, `talla`, `color`). Ya no se asume `productoId`, `imagenUrl`, `descripcionBreve` ni un único `img`. Si `description` llega nula, el frontend debe manejarlo con fallback. Si ningún SKU tiene precio vigente, el BFF envía el precio vacío y el frontend muestra "Precio no disponible" con "Agregar" deshabilitado, nunca `S/ 0.00` (A17). Un producto sin variantes toma la disponibilidad de su `single_sku`; si no se obtuvo, la tarjeta va sin badge.

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ProductCarousel` | Scroll snap, flechas, teclado y contador "1/7". |
| `ProductCard` | Imagen, marca, nombre, `PriceTag`, badge de disponibilidad y botones. |
| `ProductDetailSheet` | Hoja expandible con galería, descripción, características y `VariantSelector`. |
| `VariantSelector` | Chips de talla y muestras de color; deshabilita combinaciones sin stock; muestra el precio del SKU elegido. |
| `QuantityStepper` | Rango 1–10. |
| `ImageWithFallback` | Imagen con reemplazo por categoría. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `ver_detalle_producto` | Esquema `{productoRef? | product_id?}`. |
| `CatalogoService.detalle()` | Une el producto, sus variantes, precios por SKU y la disponibilidad por SKU en `ProductoDetalle`. |
| `VarianteResolver` | Mapea atributos en texto ("42", "negra") a los `valor_id` del producto y devuelve el SKU, las faltantes o las alternativas. |
| DTOs `ProductoResumen`, `ProductoDetalle`, `VarianteDTO` | Contrato del bloque hacia el frontend con nombres reales de Productos. `CARRUSEL_PRODUCTOS.datos` añade `total` y `siguiente` (página + filtros normalizados) para la paginación. |
| `GET /api/v1/catalogo/productos/{id}` | Acceso directo desde la UI. |

## Desglose para issues

- [ ] `[FE]` `ProductCarousel` accesible y responsive
- [ ] `[FE]` `ProductCard`, `ImageWithFallback` y badge de disponibilidad
- [ ] `[FE]` `ProductDetailSheet` con galería
- [ ] `[FE]` `VariantSelector` y `QuantityStepper`
- [ ] `[BE]` DTOs de producto y variante con su mapeo desde Productos
- [ ] `[BE]` `CatalogoService.detalle()` y el endpoint de detalle
- [ ] `[BE]` `VarianteResolver` y la herramienta `ver_detalle_producto`
- [ ] `[QA]` Pruebas de todos los escenarios, pruebas de componentes con Testing Library y revisión de accesibilidad con axe
