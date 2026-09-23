# Búsqueda y filtrado de productos

> Origen: SPEC-06 · Grupo: Descubrimiento · Requiere sesión: No · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`tarjetas-detalle-producto`](../tarjetas-detalle-producto/spec.md) (SPEC-09), Productos (SPEC-003, 004, 008, 011 y 013 de Productos)

## Purpose

Traducir la petición del cliente en filtros de catálogo válidos y devolver los productos activos que la cumplen, con su precio vigente para el canal Chatbot.

## Contexto

El cliente describe lo que busca en lenguaje natural mezclando criterios: categoría ("zapatillas", "polos", "pelotas"), marca, rango de precio en soles, talla, color o deporte. Productos y Ofertas es el dueño del catálogo, solo expone a los canales productos en estado `ACTIVO` y entrega los precios por canal a través de Pricing.

Las categorías y marcas del LLM ("Nike", "nike", "Naik") deben normalizarse contra los catálogos oficiales antes de consultar.

## Alcance

Incluye:
- Extracción de filtros por el LLM: `q` (texto libre), `categoria`, `marca`, `precioMin`, `precioMax`, `talla`, `color`, `soloOfertas` y `orden` (`PRECIO_ASC`, `PRECIO_DESC`, `RELEVANCIA`, `NOVEDAD`).
- Normalización de la categoría y la marca contra los catálogos de Productos (cacheados).
- Consulta paginada (10 por página) y presentación en carrusel (SPEC-09).
- Refinamiento conversacional ("más baratas", "solo Adidas", "en rojo").
- Chips de filtros aplicados, editables desde la UI.
- Manejo de búsquedas sin resultados.

### Fuera de alcance

- Búsqueda por imagen.
- Filtros por características técnicas avanzadas (drop, peso de la zapatilla, etc.) mientras Productos no exponga la búsqueda por características.
- Búsqueda semántica con embeddings propios: se usa la búsqueda de Productos.

## Requirements

### Requirement: Búsqueda con filtros combinados
El sistema DEBE (SHALL) convertir la petición en filtros normalizados, consultar solo productos `ACTIVO` y devolverlos con precio para el canal `CHATBOT`.

*Trazabilidad: SPEC-06 · Requisito 1.*

#### Scenario: Categoría, marca y precio máximo
- **DADO** el catálogo con zapatillas Adidas de S/ 199, 289 y 459
- **CUANDO** el cliente escribe "zapatillas adidas de menos de 300 soles"
- **ENTONCES** se consulta con `categoria=zapatillas`, `marca=Adidas` y `precioMax=300`, y el carrusel muestra solo las de S/ 199 y 289, ordenadas por relevancia

#### Scenario: Rango de precios en lenguaje coloquial
- **DADO** el mensaje "algo entre 50 y 100 lucas"
- **CUANDO** se interpreta
- **ENTONCES** se aplican `precioMin=50` y `precioMax=100` en PEN

#### Scenario: Solo productos activos
- **DADO** un producto en estado `BORRADOR` o `INACTIVO` que coincide con los filtros
- **CUANDO** se busca
- **ENTONCES** ese producto no aparece en los resultados

### Requirement: Normalización de categoría y marca
El sistema DEBE (SHALL) mapear los términos del cliente a categorías y marcas existentes, incluyendo sinónimos locales, y preguntar cuando no haya coincidencia confiable.

*Trazabilidad: SPEC-06 · Requisito 2.*

#### Scenario: Sinónimo peruano
- **DADO** el término "chimpunes"
- **CUANDO** se normaliza
- **ENTONCES** se mapea a la categoría "Calzado de fútbol" mediante el diccionario de sinónimos (`chimpunes`, `tachos` → fútbol; `polo` → camiseta; `buzo` → conjunto deportivo; `zapatillas de fulbito` → calzado de fútbol sala)

#### Scenario: Marca mal escrita
- **DADO** "naik"
- **CUANDO** se normaliza
- **ENTONCES** se aplica `Nike` si la similitud es ≥ 0,8; si hay dos candidatas cercanas, se pregunta "¿Te refieres a X o a Y?"

#### Scenario: Marca que no existe en el catálogo
- **DADO** una marca que no vende la tienda
- **CUANDO** se busca
- **ENTONCES** se informa "No trabajamos la marca X" y se ofrecen las marcas disponibles de esa categoría (máx. 6 chips)

### Requirement: Refinamiento conversacional
El sistema DEBE (SHALL) mantener los filtros vigentes en `conversacion.contexto.filtrosVigentes` y aplicar cambios incrementales.

*Trazabilidad: SPEC-06 · Requisito 3.*

#### Scenario: Refinar por precio
- **DADO** una búsqueda previa de "zapatillas Nike running"
- **CUANDO** el cliente escribe "más baratas"
- **ENTONCES** se conservan los filtros y se aplica `orden=PRECIO_ASC` (o se reduce `precioMax` al percentil 50 de los resultados previos)

#### Scenario: Nueva búsqueda sin relación
- **DADO** filtros vigentes de zapatillas
- **CUANDO** el cliente pide "pelotas de vóley"
- **ENTONCES** los filtros previos se descartan y se inicia una búsqueda nueva

#### Scenario: Editar un filtro desde los chips
- **DADO** el chip "Marca: Nike" en la cabecera del carrusel
- **CUANDO** el cliente lo quita
- **ENTONCES** se repite la búsqueda sin ese filtro mediante una acción directa (sin LLM)

### Requirement: Paginación y resultados vacíos
El sistema DEBE (SHALL) mostrar hasta 10 productos por carrusel, permitir cargar más y manejar la ausencia de resultados.

*Trazabilidad: SPEC-06 · Requisito 4.*

#### Scenario: Más de 10 resultados
- **DADO** 34 resultados
- **CUANDO** se muestra el carrusel
- **ENTONCES** aparecen 10 tarjetas con el texto "Mostrando 10 de 34" y el botón "Ver más", que trae la página siguiente

#### Scenario: Sin resultados
- **DADO** filtros sin coincidencias
- **CUANDO** se busca
- **ENTONCES** se responde "No encontré productos con esos filtros" con sugerencias para relajar el filtro más restrictivo (por ejemplo, "Quitar límite de precio" o "Ver otras marcas")

### Requirement: Tolerancia a fallos de Productos
El sistema DEBE (SHALL) informar cuando el catálogo no está disponible, sin mostrar datos obsoletos como si estuvieran vigentes.

*Trazabilidad: SPEC-06 · Requisito 5.*

#### Scenario: Productos no responde
- **DADO** que Productos excede 4 s o responde `5xx`
- **CUANDO** se busca
- **ENTONCES** se responde "No puedo consultar el catálogo en este momento, intenta en unos minutos" y se ofrece reintentar

#### Scenario: Catálogo de categorías o marcas no disponible
- **DADO** que falla la carga de categorías o marcas y existe una caché de menos de 24 h
- **CUANDO** se normaliza
- **ENTONCES** se usa la caché; sin caché, se busca solo por texto libre `q`

## Requisitos no funcionales

- **Rendimiento:** búsqueda (excluido el LLM) en p95 ≤ 800 ms. Caché de categorías y marcas de 10 min. Los resultados de búsqueda no se cachean más de 60 s y los precios nunca más de 60 s.
- **Consistencia:** el precio mostrado es el de Pricing para el canal `CHATBOT`; si Productos no devuelve precio para un SKU, el producto se muestra como "Precio no disponible" y no se puede agregar.
- **Escalabilidad:** el diccionario de sinónimos vive en un archivo de configuración versionado (`config/sinonimos.yaml`).

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
