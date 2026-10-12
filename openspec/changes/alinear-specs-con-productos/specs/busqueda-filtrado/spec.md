## MODIFIED Requirements

### Requirement: Búsqueda con filtros combinados
El sistema DEBE (SHALL) convertir la petición en los filtros que admite `GET /api/v1/productos` (`q`, `categoriaId`, `marcaId`, `precioMin`, `precioMax`, `orden` por nombre, `canal=CHATBOT`, `estado=ACTIVO`, `pagina`, `tamanio`) y devolverlos con su precio vigente obtenido de `GET /api/v1/precios`. Los criterios que Productos no filtra (talla, color, deporte) se envían como texto libre en `q`.

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
- **ENTONCES** la marca se resuelve a `marcaId` y "rojas" viaja en `q`; la talla o el color exactos se confirman luego en el detalle del producto (SPEC-09)

#### Scenario: Solo productos activos
- **DADO** un producto en estado `BORRADOR` o `INACTIVO` que coincide con los filtros
- **CUANDO** se busca
- **ENTONCES** la consulta usa `estado=ACTIVO` y ese producto no aparece en los resultados

#### Scenario: Precio de las tarjetas
- **DADO** una página de resultados
- **CUANDO** se arma el carrusel
- **ENTONCES** los SKU de los productos se consultan en una sola llamada a `GET /api/v1/precios?skus=&canal=CHATBOT` y la disponibilidad en una sola llamada a `GET /api/v1/inventario/disponibilidad/comercial`, porque la búsqueda no devuelve precio ni stock

### Requirement: Refinamiento conversacional
El sistema DEBE (SHALL) mantener los filtros vigentes en `conversation.context.filtrosVigentes` y aplicar cambios incrementales.

*Trazabilidad: SPEC-06 · Requisito 3.*

#### Scenario: Refinar por precio
- **DADO** una búsqueda previa de "zapatillas Nike running"
- **CUANDO** el cliente escribe "más baratas"
- **ENTONCES** se conservan los filtros y se reduce `precioMax` al percentil 50 de los precios de los resultados previos (Productos no ordena por precio)

#### Scenario: Nueva búsqueda sin relación
- **DADO** filtros vigentes de zapatillas
- **CUANDO** el cliente pide "pelotas de vóley"
- **ENTONCES** los filtros previos se descartan y se inicia una búsqueda nueva

#### Scenario: Editar un filtro desde los chips
- **DADO** el chip "Marca: Nike" en la cabecera del carrusel
- **CUANDO** el cliente lo quita
- **ENTONCES** se repite la búsqueda sin ese filtro mediante una acción directa (sin LLM)
