## MODIFIED Requirements

### Requirement: Búsqueda con filtros combinados
El sistema DEBE (SHALL) convertir la petición en los filtros que admite `GET /api/v1/productos` (`q`, `categoriaId`, `marcaId`, `precioMin`, `precioMax`, `orden` por nombre, `canal=CHATBOT`, `pagina`, `tamanio`) y devolverlos con su precio vigente obtenido de `GET /api/v1/precios`. Productos no filtra por talla, color ni otros atributos, y `q` no garantiza coincidencias en atributos o variantes (respuesta de Productos, 15/10). Esos criterios viajan en `q` solo como ayuda, sin prometer que filtren, y se confirman en el detalle del producto. Productos comprometió filtros estructurados de variantes para una etapa posterior; cuando estén publicados en su OpenAPI se reemplaza este comportamiento.

*Trazabilidad: SPEC-06 · Requisito 1.*

#### Scenario: Categoría, marca y precio máximo
- **DADO** el catálogo con zapatillas Adidas de S/ 199, 289 y 459
- **CUANDO** el cliente escribe "zapatillas adidas de menos de 300 soles"
- **ENTONCES** se consulta con `categoriaId` de zapatillas, `marcaId` de Adidas y `precioMax=300`, y el carrusel muestra solo las de S/ 199 y 289

#### Scenario: Rango de precios en lenguaje coloquial
- **DADO** el mensaje "algo entre 50 y 100 lucas"
- **CUANDO** se interpreta
- **ENTONCES** se aplican `precioMin=50` y `precioMax=100` en PEN

#### Scenario: Talla o color como texto libre
- **DADO** el mensaje "zapatillas Nike rojas"
- **CUANDO** se interpreta
- **ENTONCES** la marca se resuelve a `marcaId` y "rojas" viaja en `q` como ayuda; el asistente no afirma que todos los resultados sean rojos, y el color o la talla exactos se confirman en el detalle del producto (SPEC-09), donde se informa si la variante no existe

#### Scenario: Solo productos activos
- **DADO** un producto en `BORRADOR` o `INACTIVO` que coincide con los filtros
- **CUANDO** se busca con `canal=CHATBOT`
- **ENTONCES** no aparece en los resultados, porque el catálogo solo devuelve lo elegible para el canal; el chatbot no amplía la visibilidad con el filtro `estado`

#### Scenario: Precio y disponibilidad de las tarjetas
- **DADO** una página de resultados
- **CUANDO** se arma el carrusel
- **ENTONCES** los SKU se obtienen de `sku_base` o, si el producto `tiene_variantes`, del detalle `GET /api/v1/productos/{productoId}` (no hay endpoint masivo de detalles), y se consultan el precio (`GET /api/v1/precios?skus=&canal=CHATBOT`) y la disponibilidad (`GET /api/v1/inventario/disponibilidad/comercial`) en llamadas por lotes de hasta 100 SKU, porque la búsqueda no devuelve precio ni stock

#### Scenario: Sin caché contractual
- **DADO** que Productos aún no publica una pauta de caché ni de concurrencia
- **CUANDO** se consulta precio, stock o detalle
- **ENTONCES** los resultados solo se reutilizan dentro del mismo turno, sin TTL propio, hasta que Productos publique su recomendación

### Requirement: Refinamiento conversacional
El sistema DEBE (SHALL) mantener los filtros vigentes en `conversation.context.filtrosVigentes` y aplicar cambios incrementales.

*Trazabilidad: SPEC-06 · Requisito 3.*

#### Scenario: Refinar por precio
- **DADO** una búsqueda previa de "zapatillas Nike running"
- **CUANDO** el cliente escribe "más baratas"
- **ENTONCES** se conservan los filtros y se reduce `precioMax` al percentil 50 de los precios de los resultados previos (Productos no ordena por precio todavía; comprometió `PRECIO_ASC` y `PRECIO_DESC` para una etapa posterior)

#### Scenario: Nueva búsqueda sin relación
- **DADO** filtros vigentes de zapatillas
- **CUANDO** el cliente pide "pelotas de vóley"
- **ENTONCES** los filtros previos se descartan y se inicia una búsqueda nueva

#### Scenario: Editar un filtro desde los chips
- **DADO** el chip "Marca: Nike" en la cabecera del carrusel
- **CUANDO** el cliente lo quita
- **ENTONCES** se repite la búsqueda sin ese filtro mediante una acción directa (sin LLM)
