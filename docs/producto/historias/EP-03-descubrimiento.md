# EP-03 · Descubrimiento de productos — Historias de usuario

> Specs: [SPEC-06](../../../openspec/specs/busqueda-filtrado/spec.md), [SPEC-07](../../../openspec/specs/recomendacion/spec.md), [SPEC-08](../../../openspec/specs/ofertas-promociones/spec.md), [SPEC-09](../../../openspec/specs/tarjetas-detalle-producto/spec.md) · Área `CAT` · 16 historias · 61 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.
>
> **Atención:** todas las historias de esta épica consumen endpoints **provisionales** de Productos (acuerdo A5 🟡). Hasta homologarlos se desarrollan contra un mock (respx en backend, datos semilla).

---

## HU-CAT-01 · Buscar productos combinando filtros

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 5 | Hito 3 | `SPEC-06 · Req. 1` | RN-CAT-01, RN-CAT-02, RN-CAT-05 | Productos 🟡 (A5, A7) |

**Como** cliente, **quiero** pedir productos mezclando categoría, marca y rango de precio en una sola frase, **para** ver solo lo que me interesa y con el precio vigente del canal.

**Criterios de aceptación**
- `SPEC-06 · Req. 1 · Scenario: Categoría, marca y precio máximo` — la frase se traduce a `categoria`, `marca` y `precioMax`, y el carrusel muestra solo los que cumplen, por relevancia.
- `SPEC-06 · Req. 1 · Scenario: Rango de precios en lenguaje coloquial` — "entre 50 y 100 lucas" aplica `precioMin=50` y `precioMax=100` en PEN.
- `SPEC-06 · Req. 1 · Scenario: Solo productos activos` — los productos `BORRADOR` o `INACTIVO` no aparecen.

**Prioridad:** Must: el curso exige la búsqueda por precio, categoría y marca.

**Notas:** RNF: búsqueda (sin LLM) p95 ≤ 800 ms; precios en caché como máximo 60 s.

---

## HU-CAT-02 · Ser entendido aunque use sinónimos o escriba mal la marca

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 5 | Hito 3 | `SPEC-06 · Req. 2` | RN-CAT-03, RN-CAT-04 | Productos 🟡 (A5: `/categorias`, `/marcas`) |

**Como** cliente peruano, **quiero** usar palabras como "chimpunes" o escribir "naik" y que el chat me entienda, **para** no tener que conocer los nombres exactos del catálogo.

**Criterios de aceptación**
- `SPEC-06 · Req. 2 · Scenario: Sinónimo peruano` — "chimpunes" se mapea a "Calzado de fútbol" con el diccionario de sinónimos.
- `SPEC-06 · Req. 2 · Scenario: Marca mal escrita` — se aplica la marca con similitud ≥ 0,8 o se pregunta entre dos candidatas.
- `SPEC-06 · Req. 2 · Scenario: Marca que no existe en el catálogo` — se informa y se ofrecen hasta 6 marcas disponibles de la categoría.

**Prioridad:** Must: sin normalización, los filtros del LLM no calzan con los identificadores del catálogo.

---

## HU-CAT-03 · Refinar la búsqueda conversando o con chips

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Should | 5 | Hito 3 | `SPEC-06 · Req. 3` | — | Productos 🟡 (A5) |

**Como** cliente, **quiero** ajustar una búsqueda con frases como "más baratas" o quitando un chip de filtro, **para** afinar los resultados sin empezar de cero.

**Criterios de aceptación**
- `SPEC-06 · Req. 3 · Scenario: Refinar por precio` — se conservan los filtros y se ordena por precio ascendente (o se reduce `precioMax`).
- `SPEC-06 · Req. 3 · Scenario: Nueva búsqueda sin relación` — un pedido de otra categoría descarta los filtros previos.
- `SPEC-06 · Req. 3 · Scenario: Editar un filtro desde los chips` — quitar un chip repite la búsqueda sin ese filtro mediante una acción directa.

**Prioridad:** Should: mejora la experiencia de búsqueda; la búsqueda básica ya cubre el lineamiento.

---

## HU-CAT-04 · Ver más resultados o sugerencias si no hay coincidencias

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 3 | Hito 3 | `SPEC-06 · Req. 4` | RN-CAT-05 | Productos 🟡 (A5) |

**Como** cliente, **quiero** paginar resultados largos y recibir sugerencias cuando no hay coincidencias, **para** no quedarme sin opciones.

**Criterios de aceptación**
- `SPEC-06 · Req. 4 · Scenario: Más de 10 resultados` — se muestran 10 tarjetas, el texto "Mostrando 10 de N" y "Ver más".
- `SPEC-06 · Req. 4 · Scenario: Sin resultados` — se informa y se sugiere relajar el filtro más restrictivo.

**Prioridad:** Must: sin paginación ni manejo de vacío, la búsqueda queda incompleta.

---

## HU-CAT-05 · Saber cuándo el catálogo no está disponible

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 2 | Hito 3 | `SPEC-06 · Req. 5` | RN-CAT-06, RN-CAT-07 | Productos 🟡 (A5) |

**Como** cliente, **quiero** que el chat me avise cuando no puede consultar el catálogo, **para** no ver datos viejos como si estuvieran vigentes.

**Criterios de aceptación**
- `SPEC-06 · Req. 5 · Scenario: Productos no responde` — tras 4 s o un `5xx`, se informa la indisponibilidad y se ofrece reintentar.
- `SPEC-06 · Req. 5 · Scenario: Catálogo de categorías o marcas no disponible` — se usa la caché de menos de 24 h o, sin ella, solo texto libre.

**Prioridad:** Must, por el principio "nunca se asume disponibilidad" (README §1.3).

---

## HU-CAT-06 · Recibir recomendaciones según mi necesidad

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 5 | Hito 4 | `SPEC-07 · Req. 1` | RN-CAT-08, RN-CAT-09 | Productos 🟡 (A5, A7) |

**Como** cliente que sabe qué necesita pero no qué producto buscar, **quiero** describir mi necesidad y recibir una selección corta y justificada, **para** decidir rápido sin conocer el catálogo.

**Criterios de aceptación**
- `SPEC-07 · Req. 1 · Scenario: Necesidad con información suficiente` — se muestran hasta 5 tarjetas con una razón de una línea basada en atributos reales.
- `SPEC-07 · Req. 1 · Scenario: Necesidad incompleta` — el asistente pregunta una cosa a la vez, con chips y como máximo 2 preguntas.
- `SPEC-07 · Req. 1 · Scenario: El cliente no quiere responder preguntas` — se recomienda con la información disponible, priorizando productos versátiles.

**Prioridad:** Must: el curso exige la recomendación según las necesidades del cliente.

**Notas:** RNF: recomendación completa p95 ≤ 7 s; al menos 2 marcas distintas cuando existan.

---

## HU-CAT-07 · Recibir solo recomendaciones disponibles y veraces

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 3 | Hito 4 | `SPEC-07 · Req. 2` | RN-CAT-08 | Productos 🟡 (A5: disponibilidad) |

**Como** cliente, **quiero** que me recomienden solo productos que puedo comprar y que me digan con honestidad cuando no hay opciones, **para** no perder tiempo con productos agotados o inexistentes.

**Criterios de aceptación**
- `SPEC-07 · Req. 2 · Scenario: Producto recomendado sin stock` — un candidato sin stock se excluye y se reemplaza por el siguiente.
- `SPEC-07 · Req. 2 · Scenario: No hay productos que cumplan` — se informa con honestidad y se ofrecen las opciones más cercanas.

**Prioridad:** Must: una recomendación sin stock o inventada contradice el principio "el LLM no inventa datos".

---

## HU-CAT-08 · Recibir sugerencias de complementos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Should | 5 | Hito 4 | `SPEC-07 · Req. 3` | RN-CAT-10 | Productos 🟡 (A5: `/recomendaciones/candidatos`) |

**Como** cliente que acaba de agregar un producto, **quiero** ver hasta 3 complementos útiles y poder rechazarlos, **para** completar mi compra sin que me insistan.

**Criterios de aceptación**
- `SPEC-07 · Req. 3 · Scenario: Complemento tras agregar al carrito` — la confirmación incluye un mini carrusel de hasta 3 candidatos con stock.
- `SPEC-07 · Req. 3 · Scenario: Sin candidatos o servicio caído` — la confirmación se muestra sin la sección de complementos y sin error visible.
- `SPEC-07 · Req. 3 · Scenario: El cliente rechaza los complementos` — no se vuelven a sugerir en esa conversación salvo que los pida.

**Prioridad:** Should: aporta valor comercial, pero no es requisito del flujo de compra.

---

## HU-CAT-09 · Consultar las promociones vigentes del canal

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 3 | Hito 4 | `SPEC-08 · Req. 1` | RN-CAT-11 | Productos 🟡 (A5: `/promociones`) |

**Como** cliente, **quiero** preguntar qué ofertas hay (en general o por marca y categoría), **para** aprovechar los descuentos vigentes del canal.

**Criterios de aceptación**
- `SPEC-08 · Req. 1 · Scenario: Consulta general de ofertas` — se muestra `LISTA_PROMOCIONES` solo con las promociones del canal `CHATBOT`.
- `SPEC-08 · Req. 1 · Scenario: Promociones filtradas` — se muestran las promociones que aplican a la marca y categoría pedidas, más un carrusel con `precioOferta`.
- `SPEC-08 · Req. 1 · Scenario: Sin promociones vigentes` — se informa y se ofrecen productos más vendidos o nuevos.

**Prioridad:** Must: el curso exige la consulta de ofertas y promociones.

---

## HU-CAT-10 · Ver el precio de oferta en tarjetas y detalle

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 3 | Hito 4 | `SPEC-08 · Req. 2` | RN-CAT-12 | Productos 🟡 (A5: `/precios`) |

**Como** cliente, **quiero** ver el precio regular tachado, el precio de oferta y el porcentaje de ahorro, **para** reconocer una oferta de un vistazo.

**Criterios de aceptación**
- `SPEC-08 · Req. 2 · Scenario: Producto con oferta de precio` — se ve el regular tachado, la oferta y la etiqueta "-20 %".
- `SPEC-08 · Req. 2 · Scenario: Oferta vencida entre consultas` — se muestra el precio regular y se avisa si el producto estaba en el carrito.

**Prioridad:** Must: forma parte del lineamiento de ofertas y evita cobrar un precio distinto al mostrado.

---

## HU-CAT-11 · Entender los descuentos aplicados en mi carrito

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 3 | Hito 4 | `SPEC-08 · Req. 3` | RN-CAT-13 | Productos 🟡 (A5: `/promociones/evaluar`) |

**Como** cliente, **quiero** ver en mi carrito qué promoción se aplicó y por qué otra no, **para** entender el total que voy a pagar.

**Criterios de aceptación**
- `SPEC-08 · Req. 3 · Scenario: Promoción automática aplicada` — el bloque `CARRITO` muestra la línea de la promoción con los datos de la evaluación.
- `SPEC-08 · Req. 3 · Scenario: El cliente pregunta por qué no se aplicó una promoción` — se responde con el `motivo` que devuelve Productos, sin inventar condiciones.

**Prioridad:** Must: el total del carrito depende de la evaluación de Productos.

**Notas:** depende de HU-CAR-07 (totales del carrito).

---

## HU-CAT-12 · No recibir códigos de cupón en la consulta de ofertas

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Should | 1 | Hito 4 | `SPEC-08 · Req. 4` | RN-CAT-14 | Productos 🟡 (A5) |

**Como** negocio, **quiero** que el chat no revele códigos de cupón al listar ofertas, **para** que los cupones se usen solo en las campañas para las que se distribuyeron.

**Criterios de aceptación**
- `SPEC-08 · Req. 4 · Scenario: El cliente pide cupones` — se explica que los cupones se distribuyen por campañas y que puede escribir el suyo.
- `SPEC-08 · Req. 4 · Scenario: Promoción con cupón en el listado de Productos` — las promociones de modalidad `CUPON` se excluyen de `LISTA_PROMOCIONES`.

**Prioridad:** Should: protege las campañas; el esfuerzo es bajo y puede entrar junto con HU-CAT-09.

---

## HU-CAT-13 · Ver productos en un carrusel de tarjetas

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 5 | Hito 3 | `SPEC-09 · Req. 1` | RN-CAT-15 | Productos 🟡 (A5) |

**Como** cliente, **quiero** ver los productos como tarjetas con imagen, precio y disponibilidad en un carrusel, **para** comparar opciones rápidamente desde el móvil.

**Criterios de aceptación**
- `SPEC-09 · Req. 1 · Scenario: Carrusel estándar` — se muestran las tarjetas desplazables con los datos de `ProductoResumen` y `alt` descriptivo.
- `SPEC-09 · Req. 1 · Scenario: Imagen no disponible` — se muestra una imagen de reemplazo por categoría sin romper el diseño.
- `SPEC-09 · Req. 1 · Scenario: Producto agotado` — la tarjeta indica "Agotado", deshabilita "Agregar" y ofrece "Ver similares".

**Prioridad:** Must: todas las respuestas con productos se presentan con este bloque.

**Notas:** RNF de accesibilidad (`role="region"`, botones de 44×44 px) y de rendimiento (60 fps al hacer swipe).

---

## HU-CAT-14 · Agregar desde la tarjeta eligiendo la variante

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 3 | Hito 3 | `SPEC-09 · Req. 2` | RN-CAT-16 | Productos 🟡 (A5) |

**Como** cliente, **quiero** agregar un producto con un toque y que se me pida la talla o el color solo cuando hace falta, **para** no agregar por error una variante que no quiero.

**Criterios de aceptación**
- `SPEC-09 · Req. 2 · Scenario: Producto sin variantes` — "Agregar" envía `AGREGAR_AL_CARRITO` con el SKU único y muestra la confirmación.
- `SPEC-09 · Req. 2 · Scenario: Producto con variantes` — se abre `SELECTOR_VARIANTE` con las variantes agotadas deshabilitadas.

**Prioridad:** Must: el curso exige agregar productos al carrito.

---

## HU-CAT-15 · Ver el detalle de un producto

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 5 | Hito 3 | `SPEC-09 · Req. 3` | RN-CAT-17 | Productos 🟡 (A5: `/productos/{id}`) |

**Como** cliente, **quiero** abrir el detalle de un producto con su galería, características y disponibilidad por variante, **para** decidir con toda la información antes de agregarlo.

**Criterios de aceptación**
- `SPEC-09 · Req. 3 · Scenario: Detalle desde la tarjeta` — se abre `DETALLE_PRODUCTO` con galería, selector de talla y color, precio de la variante y cantidad (1–10).
- `SPEC-09 · Req. 3 · Scenario: Detalle pedido por texto` — "cuéntame más del tercero" muestra el mismo bloque y un resumen de 2 líneas.
- `SPEC-09 · Req. 3 · Scenario: Producto desactivado` — un producto que pasó a `INACTIVO` se informa como no disponible y se ofrecen similares.

**Prioridad:** Must: la elección de variante necesita la vista de detalle.

---

## HU-CAT-16 · Elegir talla y color escribiendo

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-03 | Must | 5 | Hito 3 | `SPEC-09 · Req. 4` | RN-CAT-16 | Productos 🟡 (A5) |

**Como** cliente, **quiero** decir "la quiero en 42 negra" y que el chat resuelva la variante exacta, **para** agregar al carrito conversando.

**Criterios de aceptación**
- `SPEC-09 · Req. 4 · Scenario: Talla y color completos` — se resuelve el SKU, se valida el stock y se agrega.
- `SPEC-09 · Req. 4 · Scenario: Falta un atributo` — se pregunta solo el atributo faltante con chips de valores disponibles.
- `SPEC-09 · Req. 4 · Scenario: Combinación inexistente o agotada` — se informa y se ofrecen las alternativas más cercanas.

**Prioridad:** Must: el curso exige agregar productos al carrito mediante conversación.

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de cada `design.md`. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-06 | T1 `[INT]` endpoint de búsqueda (A5, A7) → HU-CAT-01 · T2 `[BE]` ProductosClient y mock → HU-CAT-01 · T3 `[BE]` Normalizador → HU-CAT-02 · T4 `[BE]` herramienta `buscar_productos` → HU-CAT-01 · T5 `[BE]` `GET /catalogo/productos` y `BUSCAR_PAGINA` → HU-CAT-04 · T6 `[FE]` AppliedFiltersBar, LoadMoreButton, EmptyResults → HU-CAT-03 (relacionada: HU-CAT-04) · T7 `[QA]` → HU-CAT-01 a HU-CAT-05 |
| SPEC-07 | T1 `[BE]` `actividades.yaml` → HU-CAT-06 · T2 `[BE]` herramienta `recomendar_productos` → HU-CAT-06 · T3 `[BE]` CrossSellService → HU-CAT-08 · T4 `[INT]` API de candidatos (A5) → HU-CAT-08 · T5 `[FE]` variante de tarjeta, ClarifyingChips, CrossSellStrip → HU-CAT-06 (relacionada: HU-CAT-08) · T6 `[QA]` → HU-CAT-06 a HU-CAT-08 |
| SPEC-08 | T1 `[INT]` endpoints de promociones, precios y evaluación (A5) → HU-CAT-09 · T2 `[BE]` herramienta `consultar_promociones` → HU-CAT-09 · T3 `[BE]` PricingAdapter y EvaluacionClient → HU-CAT-10 (relacionada: HU-CAT-11) · T4 `[FE]` PromotionList, PriceTag, CartDiscountLines → HU-CAT-09 (relacionadas: HU-CAT-10, HU-CAT-11) · T5 `[QA]` → HU-CAT-09 a HU-CAT-12 |
| SPEC-09 | T1 `[FE]` ProductCarousel → HU-CAT-13 · T2 `[FE]` ProductCard, ImageWithFallback, badge → HU-CAT-13 · T3 `[FE]` ProductDetailSheet → HU-CAT-15 · T4 `[FE]` VariantSelector y QuantityStepper → HU-CAT-14 · T5 `[BE]` DTOs → HU-CAT-13 · T6 `[BE]` `CatalogoService.detalle()` y endpoint → HU-CAT-15 · T7 `[BE]` VarianteResolver y `ver_detalle_producto` → HU-CAT-16 · T8 `[QA]` → HU-CAT-13 a HU-CAT-16 |
