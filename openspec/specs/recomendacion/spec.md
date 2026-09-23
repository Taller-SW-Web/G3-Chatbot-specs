# Recomendación de productos por necesidad

> Origen: SPEC-07 · Grupo: Descubrimiento · Requiere sesión: No · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`busqueda-filtrado`](../busqueda-filtrado/spec.md) (SPEC-06), [`tarjetas-detalle-producto`](../tarjetas-detalle-producto/spec.md) (SPEC-09), [`validacion-stock`](../validacion-stock/spec.md) (SPEC-10), Productos (SPEC-007 de Productos)

## Purpose

Convertir una necesidad descrita en lenguaje natural en una selección corta y justificada de productos disponibles, y sugerir complementos cuando el cliente elige uno.

## Contexto

Muchos clientes no saben qué producto buscar; saben qué necesitan: "algo para empezar a trotar", "regalo para mi papá que juega pádel", "equipo para fútbol de mi hijo de 10 años". El curso exige "recomendación de productos según las necesidades expresadas por el cliente".

Productos y Ofertas ofrece reglas de merchandising (cross-sell y upsell) como **candidatos** (su SPEC-007), y deja explícitamente en el Chatbot la responsabilidad de interpretar la necesidad y el contexto conversacional.

## Alcance

Incluye:
- Extracción del perfil de la necesidad: deporte o actividad, uso (entrenamiento, competencia, casual), nivel, destinatario, talla o edad, presupuesto y preferencia de marca.
- Preguntas aclaratorias (máx. 2) cuando falta información clave.
- Traducción del perfil a una o varias búsquedas de catálogo (SPEC-06).
- Selección de 3 a 5 productos disponibles con una justificación breve por producto.
- Complementos (cross-sell) tras ver el detalle o agregar un producto, usando los candidatos de Productos.

### Fuera de alcance

- Recomendación basada en el historial de compras o en el comportamiento de otros usuarios.
- Configuración de reglas de cross-sell: es responsabilidad de Productos (SPEC-007).
- Recomendación de tallas por medidas corporales.

## Requirements

### Requirement: Recomendación a partir de una necesidad
El sistema DEBE (SHALL) interpretar la necesidad, ejecutar las búsquedas correspondientes y mostrar entre 3 y 5 productos con stock, cada uno con una razón de una línea basada solo en sus atributos reales.

*Trazabilidad: SPEC-07 · Requisito 1.*

#### Scenario: Necesidad con información suficiente
- **DADO** el mensaje "quiero empezar a correr, tengo unos 250 soles"
- **CUANDO** se procesa
- **ENTONCES** el LLM invoca `recomendar_productos {actividad: "running", nivel: "principiante", presupuestoMax: 250}`, el backend busca en zapatillas de running (y como opción en medias y polos técnicos dentro del presupuesto) y muestra hasta 5 tarjetas con razones como "Amortiguación para principiante · S/ 229"

#### Scenario: Necesidad incompleta
- **DADO** el mensaje "algo para mi hijo que juega fútbol"
- **CUANDO** falta la talla o la edad y la superficie de juego
- **ENTONCES** el asistente pregunta una sola cosa a la vez ("¿Juega en césped natural, sintético o losa?") y ofrece chips con las opciones, con un máximo de 2 preguntas antes de recomendar

#### Scenario: El cliente no quiere responder preguntas
- **DADO** una pregunta aclaratoria pendiente
- **CUANDO** el cliente responde "no sé, muéstrame algo"
- **ENTONCES** se recomienda con la información disponible, priorizando productos versátiles, y se indica que puede afinar después

### Requirement: Recomendaciones veraces y disponibles
El sistema DEBE (SHALL) recomendar únicamente productos activos con stock disponible y DEBE generar las justificaciones solo a partir de los atributos devueltos por Productos.

*Trazabilidad: SPEC-07 · Requisito 2.*

#### Scenario: Producto recomendado sin stock
- **DADO** que un candidato tiene `available = 0` en todas sus variantes
- **CUANDO** se arma la recomendación
- **ENTONCES** se excluye y se reemplaza por el siguiente candidato

#### Scenario: No hay productos que cumplan
- **DADO** un presupuesto de S/ 30 para zapatillas
- **CUANDO** no existe ninguna opción
- **ENTONCES** se informa con honestidad ("No tengo zapatillas en ese presupuesto; las más económicas cuestan S/ 149") y se ofrece ver esas opciones o accesorios dentro del presupuesto

### Requirement: Complementos (cross-sell)
El sistema DEBE (SHALL) sugerir complementos, como máximo una vez por producto agregado, usando los candidatos de merchandising de Productos para el canal `CHATBOT`.

*Trazabilidad: SPEC-07 · Requisito 3.*

#### Scenario: Complemento tras agregar al carrito
- **DADO** que el cliente agregó unas zapatillas de running
- **CUANDO** Productos devuelve candidatos (por ejemplo, medias técnicas o una botella)
- **ENTONCES** el mensaje de confirmación incluye "¿Te interesa complementarlo?" con un mini carrusel de hasta 3 candidatos con stock

#### Scenario: Sin candidatos o servicio caído
- **DADO** que la API de candidatos no devuelve nada o falla
- **CUANDO** se agrega el producto
- **ENTONCES** la confirmación se muestra sin la sección de complementos y sin error visible

#### Scenario: El cliente rechaza los complementos
- **DADO** que el cliente responde "no, gracias"
- **CUANDO** se registra la respuesta
- **ENTONCES** no se vuelven a sugerir complementos en lo que queda de la conversación, salvo que los pida (`contexto.crossSellSilenciado = true`)

## Requisitos no funcionales

- **Rendimiento:** la recomendación completa (con LLM) en p95 ≤ 7 s; se muestra "Buscando opciones para ti…".
- **Veracidad:** el `OutputValidator` (SPEC-05) rechaza justificaciones que mencionen atributos inexistentes en los datos del producto (la prueba compara con los atributos enviados).
- **Diversidad:** entre las recomendaciones debe haber al menos 2 marcas distintas cuando existan en el catálogo filtrado.
- **Transparencia:** el orden no favorece productos por comisión; prioriza el ajuste a la necesidad y luego la disponibilidad.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
