# Diseño: Búsqueda y filtrado de productos

> Origen: SPEC-06 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /productos?estado=ACTIVO&q=&categoriaId=&marcaId=&precioMin=&precioMax=&canal=CHATBOT&pagina=&tamanio=` | 🟡 A5, A7 |
| Productos | `GET /categorias`, `GET /marcas` | 🟡 A5 |
| Productos | `GET /precios?skus=&canal=CHATBOT` (si la búsqueda no trae el precio) | 🟡 A5 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ProductCarousel` (SPEC-09) | Muestra los resultados. |
| `AppliedFiltersBar` | Chips de los filtros aplicados, con acción de quitar cada uno. |
| `LoadMoreButton` | Pide la página siguiente (acción `BUSCAR_PAGINA`). |
| `EmptyResults` | Mensaje y chips de sugerencia. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `buscar_productos` | Esquema `{q?, categoria?, marca?, precioMin?, precioMax?, talla?, color?, soloOfertas?, orden?, pagina?}`. |
| `CatalogoService.buscar()` | Normaliza, consulta, mapea a `ProductoResumen` y guarda `ultimoCarrusel` y `filtrosVigentes`. |
| `Normalizador` | Sinónimos, similitud (rapidfuzz) y caché de categorías y marcas. |
| `ProductosClient` | httpx con timeout de 4 s y token de servicio si Productos lo requiere. |
| `GET /api/v1/catalogo/productos` | Misma búsqueda para las acciones directas. |

## Desglose para issues

- [ ] `[INT]` Acordar con Productos el endpoint de búsqueda, sus filtros y el campo de precio por canal (A5, A7)
- [ ] `[BE]` `ProductosClient` (búsqueda, categorías, marcas y precios) más un mock respx con datos semilla
- [ ] `[BE]` `Normalizador` con `sinonimos.yaml` y fuzzy match
- [ ] `[BE]` Herramienta `buscar_productos` y `CatalogoService.buscar`
- [ ] `[BE]` Endpoint `GET /catalogo/productos` y acción `BUSCAR_PAGINA`
- [ ] `[FE]` `AppliedFiltersBar`, `LoadMoreButton` y `EmptyResults`
- [ ] `[QA]` Frases de búsqueda en el conjunto de evaluación (≥ 30) y pruebas de todos los escenarios
