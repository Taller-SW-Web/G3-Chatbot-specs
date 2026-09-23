# Diseño: Carrusel, tarjetas y detalle de producto

> Origen: SPEC-09 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /productos/{id}` con variantes activas, atributos identificadores, imagen y SKU | 🟡 A5 |
| Productos | `GET /inventario/disponibilidad?skus=` | 🟡 A5 |
| Productos | `GET /precios?skus=&canal=CHATBOT` | 🟡 A5 |

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
| Herramienta `ver_detalle_producto` | Esquema `{productoRef? | productoId?}`. |
| `CatalogoService.detalle()` | Une el producto, sus variantes, precios por SKU y la disponibilidad por SKU en `ProductoDetalle`. |
| `VarianteResolver` | Mapea atributos en texto ("42", "negra") a los `valor_id` del producto y devuelve el SKU, las faltantes o las alternativas. |
| DTOs `ProductoResumen`, `ProductoDetalle`, `VarianteDTO` | Contrato del bloque hacia el frontend. |
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
