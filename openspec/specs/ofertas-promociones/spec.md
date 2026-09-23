# Consulta de ofertas y promociones

> Origen: SPEC-08 · Grupo: Descubrimiento · Requiere sesión: No · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`tarjetas-detalle-producto`](../tarjetas-detalle-producto/spec.md) (SPEC-09), Productos (SPEC-005, 006 y 013 de Productos)

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
- Listado de promociones automáticas vigentes del canal `CHATBOT`, filtrable por categoría o marca.
- Listado de productos con oferta de precio (`soloOfertas=true`, SPEC-06).
- Presentación del precio regular tachado, el precio de oferta y el porcentaje de ahorro en las tarjetas.
- Explicación de la vigencia ("válido hasta el 30/09").
- Uso de la evaluación de promociones de Productos para los totales del carrito (lo consume SPEC-11).

### Fuera de alcance

- Crear o editar promociones: es responsabilidad del Gestor Comercial en Productos.
- Notificaciones push de ofertas.
- Combos de productos como unidad vendible, salvo que Productos los exponga como producto consultable.

## Requirements

### Requirement: Listar promociones vigentes del canal
El sistema DEBE (SHALL) consultar las promociones activas y vigentes habilitadas para `CHATBOT` (una lista de canales vacía significa todos los canales) y mostrarlas con su descripción, beneficio y vigencia.

*Trazabilidad: SPEC-08 · Requisito 1.*

#### Scenario: Consulta general de ofertas
- **DADO** 3 promociones automáticas vigentes para `CHATBOT` y 1 solo para `RETAIL`
- **CUANDO** el cliente pregunta "¿qué ofertas tienen?"
- **ENTONCES** se muestra el bloque `LISTA_PROMOCIONES` con las 3 del canal (nombre, beneficio como "20 % en toda la línea running", vigencia y el botón "Ver productos"), y no aparece la de `RETAIL`

#### Scenario: Promociones filtradas
- **DADO** el mensaje "¿hay descuentos en zapatillas Puma?"
- **CUANDO** se consulta
- **ENTONCES** se muestran las promociones cuyo alcance incluye productos Puma de la categoría zapatillas, y además un carrusel de productos Puma con `precioOferta`

#### Scenario: Sin promociones vigentes
- **DADO** que no hay promociones vigentes para el canal
- **CUANDO** el cliente pregunta
- **ENTONCES** se responde "Por ahora no tenemos promociones activas" y se ofrece ver los productos más vendidos o nuevos

### Requirement: Mostrar precio de oferta en tarjetas y detalle
El sistema DEBE (SHALL) mostrar, cuando exista `precioOferta` vigente para el canal, el precio regular tachado, el precio de oferta y el porcentaje de ahorro redondeado.

*Trazabilidad: SPEC-08 · Requisito 2.*

#### Scenario: Producto con oferta de precio
- **DADO** un SKU con `precioRegular = 299.90` y `precioOferta = 239.90`
- **CUANDO** se renderiza la tarjeta
- **ENTONCES** se ve ~~S/ 299.90~~ **S/ 239.90** y la etiqueta "-20 %"

#### Scenario: Oferta vencida entre consultas
- **DADO** una oferta que vence mientras el cliente conversa
- **CUANDO** el producto se vuelve a consultar o se recalcula el carrito
- **ENTONCES** se muestra el precio regular y, si estaba en el carrito, se informa "La oferta de X terminó; el precio ahora es S/ 299.90"

### Requirement: Explicar los beneficios aplicados en el carrito
El sistema DEBE (SHALL) mostrar en el carrito el descuento que devuelve la evaluación de Productos (promoción seleccionada, importe original, descuento e importe resultante), sin calcular reglas de promoción por su cuenta.

*Trazabilidad: SPEC-08 · Requisito 3.*

#### Scenario: Promoción automática aplicada
- **DADO** un carrito elegible para "2x1 en medias"
- **CUANDO** se recalcula el carrito
- **ENTONCES** el bloque `CARRITO` muestra la línea "Promoción 2x1 en medias: -S/ 24.90" con los datos de la evaluación

#### Scenario: El cliente pregunta por qué no se aplicó una promoción
- **DADO** un carrito que no alcanza la condición de una promoción
- **CUANDO** el cliente pregunta "¿por qué no me hicieron el descuento?"
- **ENTONCES** el asistente responde con el `motivo` que devuelve la evaluación de Productos (por ejemplo, "La promoción aplica a partir de S/ 200") y no inventa condiciones

### Requirement: No revelar códigos de cupón
El sistema NO DEBE (SHALL NOT) listar códigos de cupón en la consulta de ofertas; los cupones se aplican solo si el cliente ya tiene el código (SPEC-13).

*Trazabilidad: SPEC-08 · Requisito 4.*

#### Scenario: El cliente pide cupones
- **DADO** que existen promociones de modalidad `CUPON`
- **CUANDO** el cliente pregunta "¿me das un cupón?"
- **ENTONCES** se responde que los cupones se distribuyen por campañas y que, si tiene uno, puede escribirlo para aplicarlo

#### Scenario: Promoción con cupón en el listado de Productos
- **DADO** que la consulta de promociones devuelve una de modalidad `CUPON`
- **CUANDO** se arma `LISTA_PROMOCIONES`
- **ENTONCES** se excluye del listado

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
