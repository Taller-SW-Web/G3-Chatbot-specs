# Validación de stock

> Origen: SPEC-10 · Grupo: Carrito · Requiere sesión: No · Depende de: Productos (SPEC-015 de Productos), [`tarjetas-detalle-producto`](../tarjetas-detalle-producto/spec.md) (SPEC-09) · La usan: [`gestion-carrito`](../gestion-carrito/spec.md) (SPEC-11), [`checkout-pago`](../checkout-pago/spec.md) (SPEC-14), [`grabacion-pedido`](../grabacion-pedido/spec.md) (SPEC-15)

## Purpose

Verificar contra el inventario real la disponibilidad de cada SKU antes de agregarlo o incrementarlo en el carrito, y de nuevo antes de crear el pedido.

## Contexto

El stock pertenece a Productos y Ofertas y se controla por **SKU vendible** y ubicación (`on_hand`, `reserved`, `available`). Su SPEC-015 aclara tres puntos:

- La consulta de disponibilidad **no es una reserva ni una garantía**.
- El consumo definitivo ocurre cuando Ventas confirma el pedido (`order.confirmed`).
- Las vistas de disponibilidad son eventualmente consistentes.

Ventas, por su parte, vuelve a validar el stock al crear el pedido y responde `409` si no hay disponibilidad (F1 CA-03).

El chatbot debe evitar que el cliente agregue o intente pagar más unidades de las disponibles y nunca asumir disponibilidad cuando no puede consultarla.

## Alcance

Incluye:
- Consulta de `available` agregado por SKU antes de cada adición o incremento.
- Validación masiva de todas las líneas antes del checkout.
- Mensajes con la cantidad disponible y opciones para ajustar.
- Alternativas cuando un SKU está agotado (otras variantes o productos similares).
- Consulta explícita del cliente ("¿tienen la talla 40?").

### Fuera de alcance

- Reserva de stock al agregar al carrito: el contrato de reserva de Inventario no está homologado con Ventas y la reserva la decide Ventas.
- Stock por tienda física o retiro en tienda.
- Aviso cuando un producto vuelve a tener stock.

## Requirements

### Requirement: Validar antes de agregar o incrementar
El sistema DEBE (SHALL) consultar la disponibilidad del SKU y aceptar la operación solo si `cantidadEnCarrito + cantidadSolicitada ≤ available`.

*Trazabilidad: SPEC-10 · Requisito 1.*

#### Scenario: Stock suficiente
- **DADO** un SKU con `available = 12` y 0 unidades en el carrito
- **CUANDO** el cliente agrega 2
- **ENTONCES** la operación se acepta y el carrito queda con 2 unidades

#### Scenario: Stock parcial
- **DADO** un SKU con `available = 3` y 2 unidades ya en el carrito
- **CUANDO** el cliente pide agregar 2 más
- **ENTONCES** se responde `409 STOCK_INSUFICIENTE {disponible: 3}` y el chat dice "Solo quedan 3 unidades; ya tienes 2 en tu carrito. ¿Agrego 1 más?" con los botones "Sí, agregar 1" y "No"

#### Scenario: SKU agotado
- **DADO** un SKU con `available = 0`
- **CUANDO** se intenta agregar
- **ENTONCES** se informa que está agotado y se ofrecen las variantes disponibles del mismo producto o, si no hay, hasta 3 productos similares con stock

### Requirement: Revalidar todo el carrito antes del checkout
El sistema DEBE (SHALL) revalidar la disponibilidad de todas las líneas en una sola consulta masiva al iniciar el checkout y bloquearlo si alguna línea no se puede cumplir.

*Trazabilidad: SPEC-10 · Requisito 2.*

#### Scenario: El stock cambió desde que se agregó
- **DADO** un carrito con 3 × SKU-A cuyo `available` bajó a 1
- **CUANDO** se inicia el checkout
- **ENTONCES** se responde `409 CARRITO_DESACTUALIZADO` con el detalle por línea, y el chat muestra "Mientras elegías, quedó 1 unidad de X" con los botones "Ajustar a 1" y "Quitar del carrito"

#### Scenario: Todas las líneas disponibles
- **DADO** un carrito con stock suficiente en todas las líneas
- **CUANDO** se inicia el checkout
- **ENTONCES** la validación pasa y el checkout continúa (SPEC-14)

#### Scenario: Ventas rechaza por stock al crear el pedido
- **DADO** que la revalidación pasó pero Ventas responde `409` por falta de stock al crear el pedido
- **CUANDO** ocurre
- **ENTONCES** se vuelve al carrito con la revalidación de todas las líneas y se informa al cliente, sin cobrar (SPEC-15)

### Requirement: Nunca asumir disponibilidad
El sistema DEBE (SHALL) rechazar la adición o el checkout cuando no puede obtener la disponibilidad.

*Trazabilidad: SPEC-10 · Requisito 3.*

#### Scenario: Inventario no disponible al agregar
- **DADO** que Productos no responde en 3 s
- **CUANDO** el cliente agrega un producto
- **ENTONCES** no se agrega, se responde `503 SERVICIO_NO_DISPONIBLE` y el chat dice "No puedo confirmar el stock ahora; intenta en unos segundos" con el botón "Reintentar"

#### Scenario: Disponibilidad no disponible solo para mostrar
- **DADO** una búsqueda en la que falla la consulta de disponibilidad pero sí se obtuvieron los productos
- **CUANDO** se renderizan las tarjetas
- **ENTONCES** se muestran sin el badge de disponibilidad, y la validación se hará al agregar

### Requirement: Consulta explícita de disponibilidad
El sistema DEBE (SHALL) responder preguntas de stock sobre un producto o una variante sin revelar cantidades exactas grandes.

*Trazabilidad: SPEC-10 · Requisito 4.*

#### Scenario: Consulta de talla
- **DADO** el mensaje "¿tienen las Ultraboost en 40?"
- **CUANDO** se consulta
- **ENTONCES** se responde "Sí, hay disponibilidad en talla 40" (o "Quedan pocas unidades" si son ≤ 5) con el botón "Agregar"

#### Scenario: Consulta de una variante inexistente
- **DADO** una talla que el producto no maneja
- **CUANDO** se consulta
- **ENTONCES** se informa qué tallas maneja el producto

## Requisitos no funcionales

- **Consistencia:** las decisiones de agregar o hacer checkout usan una consulta en vivo, sin caché. La caché (≤ 30 s) solo se permite para los badges de las tarjetas.
- **Rendimiento:** la consulta masiva para el checkout (hasta 20 SKUs) se hace en una sola llamada con p95 ≤ 500 ms.
- **Transparencia:** los mensajes aclaran que el stock no queda reservado hasta completar el pago ("Te recomendamos completar tu compra pronto").
- **Privacidad comercial:** no se exponen cantidades exactas mayores a 5.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
