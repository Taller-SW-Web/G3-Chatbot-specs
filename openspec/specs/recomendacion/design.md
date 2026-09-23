# Diseño: Recomendación de productos por necesidad

> Origen: SPEC-07 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | Búsqueda de catálogo (ver SPEC-06) | 🟡 A5 |
| Productos | `GET /recomendaciones/candidatos?productoId=&canal=CHATBOT` | 🟡 A5 |
| Productos | `GET /inventario/disponibilidad?skus=` | 🟡 A5 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ProductCarousel` con la variante `recomendacion` | Tarjetas con una línea de "Por qué te lo recomiendo". |
| `ClarifyingChips` | Opciones rápidas para las preguntas aclaratorias. |
| `CrossSellStrip` | Mini carrusel de hasta 3 complementos dentro de la confirmación del carrito. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Herramienta `recomendar_productos` | Esquema `{actividad, uso?, nivel?, destinatario?, talla?, presupuestoMax?, marcaPreferida?}`. |
| `RecomendacionService` | Mapea la actividad a categorías (`config/actividades.yaml`), ejecuta búsquedas, filtra por stock, diversifica y limita a 5. |
| `CrossSellService` | Consulta candidatos, filtra por stock, respeta `crossSellSilenciado` y el máximo de una sugerencia por producto. |
| Integración con `CarritoService.agregar()` | Añade `CrossSellStrip` a la respuesta. |

## Desglose para issues

- [ ] `[BE]` `config/actividades.yaml` (running, fútbol, fútbol sala, vóley, básquet, pádel, tenis, gimnasio, natación, ciclismo) con sus categorías
- [ ] `[BE]` Herramienta `recomendar_productos` y `RecomendacionService`
- [ ] `[BE]` `CrossSellService` más la integración con la confirmación del carrito
- [ ] `[INT]` Cliente de la API de candidatos de Productos (A5)
- [ ] `[FE]` Variante `recomendacion` de la tarjeta, `ClarifyingChips` y `CrossSellStrip`
- [ ] `[QA]` 25 frases de necesidad en el conjunto de evaluación y pruebas de todos los escenarios
