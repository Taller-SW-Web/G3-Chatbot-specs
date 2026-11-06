# Consulta de ofertas y promociones

> Origen: SPEC-08 · Grupo: Descubrimiento · Requiere sesión: No · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`tarjetas-detalle-producto`](../tarjetas-detalle-producto/spec.md) (SPEC-09), Productos (SPEC-005, 006 y 013 de Productos)

## Responsables

- **Sonny:** consulta de ofertas vigentes para el canal.
- **Alonso:** herramienta de ofertas.
- **Diego:** banner y grid de productos en oferta en `HomePage`.
- **Nikol (QA):** casos de prueba a partir de los escenarios, pruebas E2E si el flujo es crítico y validación contra la definición de terminado.

## Purpose

Mostrar al cliente las ofertas y promociones vigentes habilitadas para el canal Chatbot y reflejar los descuentos correctamente en las tarjetas y en el carrito.

## Contexto

En Productos y Ofertas los beneficios comerciales vienen de tres fuentes:

1. **Oferta de precio de Pricing** (`precioOferta` con vigencia y alcance por canal).
2. **Promociones de modalidad `AUTOMATICA`**, habilitadas por canal (`MARKETPLACE`, `CHATBOT`, `RETAIL`), con prioridad y política de combinación.
3. **Cupones** (modalidad `CUPON`, SPEC-13).

El motor de Productos decide la mejor combinación sobre la cesta y expone una API de evaluación.

El cliente pregunta "¿qué ofertas tienen?", "¿hay descuentos en zapatillas Puma?" o "¿esto está en oferta?".

## Alcance

Incluye:
- Listado de promociones vigentes del canal `CHATBOT`, con nombre y vigencia (Productos no entrega todavía beneficio, alcance ni modalidad, ni permite filtrarlas por categoría o marca; A16).
- Productos con oferta de precio (`precio_oferta` vigente de `GET /precios`) dentro de los resultados de búsqueda (SPEC-06).
- Presentación del precio regular tachado, el precio de oferta y el porcentaje de ahorro en las tarjetas.
- Explicación de la vigencia ("válido hasta el 30/09").
- Uso de la evaluación de promociones de Productos para los totales del carrito (lo consume SPEC-11).

### Fuera de alcance

- Crear o editar promociones: es responsabilidad del Gestor Comercial en Productos.
- Notificaciones push de ofertas.
- Combos de productos como unidad vendible, salvo que Productos los exponga como producto consultable.

## Requirements

### Requirement: Listar promociones vigentes del canal
El sistema DEBE (SHALL) consultar las promociones vigentes del canal (`GET /api/v1/promociones?canal=CHATBOT&vigentes=true`) y mostrarlas con su nombre y vigencia. Productos no entrega todavía el beneficio ni el alcance de cada promoción, y comprometió ampliarlo para una etapa posterior; mientras tanto el chatbot no los inventa. El listado tampoco garantiza incluir todas las promociones que pueden aparecer en una evaluación (por ejemplo las de cupón privado).

*Trazabilidad: SPEC-08 · Requisito 1.*

#### Scenario: Consulta general de ofertas
- **DADO** 3 promociones vigentes para `CHATBOT`
- **CUANDO** el cliente pregunta "¿qué ofertas tienen?"
- **ENTONCES** se muestra el bloque `LISTA_PROMOCIONES` con las 3 (nombre y "válido hasta dd/mm") y, debajo, un carrusel de productos con `precio_oferta` vigente cuando existan

#### Scenario: Promociones filtradas
- **DADO** el mensaje "¿hay descuentos en zapatillas Puma?"
- **CUANDO** se consulta
- **ENTONCES** se buscan productos Puma de la categoría zapatillas (SPEC-06) y se muestran los que tengan `precio_oferta` vigente; el listado de promociones no se filtra por categoría ni marca porque Productos no lo permite

#### Scenario: Sin promociones vigentes
- **DADO** que no hay promociones vigentes para el canal
- **CUANDO** el cliente pregunta
- **ENTONCES** se responde "Por ahora no tenemos promociones activas" y se ofrece ver los productos más vendidos o nuevos

### Requirement: Mostrar precio de oferta en tarjetas y detalle
El sistema DEBE (SHALL) mostrar, cuando `precio_oferta` no sea nulo y esté vigente para el canal, el precio regular tachado, el precio de oferta y el porcentaje de ahorro redondeado.

*Trazabilidad: SPEC-08 · Requisito 2.*

#### Scenario: Producto con oferta de precio
- **DADO** un SKU con `precio_regular = 299.90` y `precio_oferta = 239.90`
- **CUANDO** se renderiza la tarjeta
- **ENTONCES** se ve ~~S/ 299.90~~ **S/ 239.90** y la etiqueta "-20 %"

#### Scenario: Oferta vencida entre consultas
- **DADO** una oferta que vence mientras el cliente conversa
- **CUANDO** el producto se vuelve a consultar o se recalcula el carrito
- **ENTONCES** se muestra el precio regular y, si estaba en el carrito, se informa "La oferta de X terminó; el precio ahora es S/ 299.90"

### Requirement: Explicar los beneficios aplicados en el carrito
El sistema DEBE (SHALL) mostrar en el carrito el resultado de la evaluación de Productos (`promotion_id`, `original_amount`, `discount_amount`, `result_amount`), sin calcular reglas de promoción por su cuenta y sin desglosar por línea.

*Trazabilidad: SPEC-08 · Requisito 3.*

#### Scenario: Promoción automática aplicada
- **DADO** un carrito elegible para una promoción
- **CUANDO** se recalcula el carrito
- **ENTONCES** el bloque `CARRITO` muestra una línea "Promoción <nombre>: -S/ 24.90" con el importe de `discount_amount`; si el `promotion_id` no se encuentra en el listado o es nulo, la línea dice "Descuento: -S/ 24.90" (comportamiento interino, no contrato de Productos)

#### Scenario: El cliente pregunta por qué no se aplicó una promoción
- **DADO** un carrito sin descuento
- **CUANDO** el cliente pregunta "¿por qué no me hicieron el descuento?"
- **ENTONCES** el asistente responde con el campo `reason` de la evaluación si existe, y si viene vacío dice que no tiene el detalle y no inventa condiciones

### Requirement: No revelar códigos de cupón
El sistema NO DEBE (SHALL NOT) mostrar ni inferir códigos de cupón en la consulta de ofertas; los cupones se aplican solo si el cliente ya tiene el código (SPEC-13).

*Trazabilidad: SPEC-08 · Requisito 4.*

#### Scenario: El cliente pide cupones
- **DADO** que existen cupones activos
- **CUANDO** el cliente pregunta "¿me das un cupón?"
- **ENTONCES** se responde que los cupones se distribuyen por campañas y que, si tiene uno, puede escribirlo para aplicarlo

#### Scenario: Promoción con cupón en el listado de Productos
- **DADO** que el listado de promociones incluya una promoción cuyo beneficio se obtiene con cupón
- **CUANDO** se arma `LISTA_PROMOCIONES`
- **ENTONCES** solo se muestran su nombre y vigencia, nunca un código (el listado de Productos no trae códigos)

## Requisitos no funcionales

- **Consistencia:** todo descuento mostrado proviene de Productos; el chatbot no calcula promociones.
- **Rendimiento:** caché de 60 s para el listado de promociones vigentes (nunca para la evaluación del carrito).
- **Formato:** importes con 2 decimales y el prefijo "S/"; fechas en `dd/mm` con hora de Lima.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
