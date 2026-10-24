## MODIFIED Requirements

### Requirement: Validar antes de agregar o incrementar
El sistema DEBE (SHALL) consultar la disponibilidad comercial del SKU (`GET /api/v1/inventario/disponibilidad/comercial`, que devuelve `DISPONIBLE`, `STOCK_BAJO`, `AGOTADO` o `INDETERMINADO`, sin cantidades) y verificar la cantidad pedida con la verificación no vinculante `POST /api/v1/inventario/disponibilidad/comercial/verificar` (`channel_id`, `fulfillment` y `lines[{sku, quantity}]`; responde `items[{sku, requested_quantity, result}]` con `result` igual a `SUFICIENTE`, `INSUFICIENTE` o `INDETERMINADO` y `binding=false`, sin reservar). El chatbot envía siempre `fulfillment: {mode: ENVIO_DOMICILIO}`, sin `fulfillment_ref`, porque este canal solo entrega a domicilio (RN-CHK-05) y no dispone de una referencia de cumplimiento de Productos; el resultado es informativo y no promete disponibilidad. La operación se rechaza si el SKU está `AGOTADO` o la verificación responde `INSUFICIENTE`. Con `DISPONIBLE` o `SUFICIENTE` se acepta; con `STOCK_BAJO` o `INDETERMINADO` se acepta con aviso, dentro del límite de 10 unidades por línea del carrito. El aviso de `STOCK_BAJO` es "Quedan pocas unidades" y el de `INDETERMINADO` es "No pudimos confirmar el stock"; `INDETERMINADO` nunca se comunica como pocas unidades. La decisión final la toma Ventas al crear el pedido (`409` por falta de stock). Si la verificación por cantidad no estuviera disponible, se usa solo el estado comercial.

*Trazabilidad: SPEC-10 · Requisito 1.*

#### Scenario: Stock suficiente
- **DADO** un SKU con estado `DISPONIBLE`
- **CUANDO** el cliente agrega 2
- **ENTONCES** la operación se acepta y el carrito queda con 2 unidades

#### Scenario: Stock parcial
- **DADO** un SKU con estado `STOCK_BAJO`
- **CUANDO** el cliente agrega 2
- **ENTONCES** la operación se acepta y el chat añade "Quedan pocas unidades; el stock no se reserva hasta completar el pago"

#### Scenario: Cantidad mayor a la disponible
- **DADO** un SKU con estado `STOCK_BAJO` y una verificación que responde `INSUFICIENTE` para la cantidad pedida
- **CUANDO** el cliente agrega 6
- **ENTONCES** no se agrega, se informa "No hay stock suficiente para esa cantidad" y se ofrece probar con menos unidades; no se menciona una cantidad exacta porque Productos no la expone

#### Scenario: Disponibilidad indeterminada
- **DADO** un SKU cuyo estado o verificación es `INDETERMINADO`
- **CUANDO** el cliente lo agrega
- **ENTONCES** la operación se acepta con el aviso "No pudimos confirmar el stock en este momento; lo verificaremos antes del pago", sin tratarlo como `AGOTADO` (comportamiento interino: Productos no define aún qué hace el cliente con `INDETERMINADO`, y Ventas confirma el stock al crear el pedido)

#### Scenario: SKU agotado
- **DADO** un SKU con estado `AGOTADO`
- **CUANDO** se intenta agregar
- **ENTONCES** no se agrega, se informa que está agotado y se ofrecen las variantes disponibles del mismo producto o, si no hay, hasta 3 productos similares que no estén agotados

#### Scenario: Contexto de cumplimiento de la verificación
- **DADO** un cliente que agrega un SKU, tenga o no una dirección elegida
- **CUANDO** se llama a la verificación por cantidad
- **ENTONCES** se envía `fulfillment: {mode: ENVIO_DOMICILIO}` sin `fulfillment_ref`, se lee `items[].result` y el mensaje al cliente no promete que el stock quedará disponible

### Requirement: Revalidar todo el carrito antes del checkout
El sistema DEBE (SHALL) revalidar la disponibilidad comercial de todas las líneas en una sola consulta masiva al iniciar el checkout y bloquearlo si alguna línea está `AGOTADO` o la verificación por cantidad de todas las líneas (una sola llamada) responde `INSUFICIENTE`. Una línea en `STOCK_BAJO` o `INDETERMINADO` no bloquea el checkout y muestra un aviso.

*Trazabilidad: SPEC-10 · Requisito 2.*

#### Scenario: El stock cambió desde que se agregó
- **DADO** un carrito con SKU-A cuyo estado pasó a `AGOTADO`
- **CUANDO** se inicia el checkout
- **ENTONCES** se responde `409 CARRITO_DESACTUALIZADO` con el detalle por línea, y el chat muestra "X se agotó mientras elegías" con el botón "Quitar del carrito"

#### Scenario: Línea con disponibilidad indeterminada
- **DADO** un carrito en el que una línea responde `INDETERMINADO`
- **CUANDO** se inicia el checkout
- **ENTONCES** el checkout continúa con el aviso de esa línea y Ventas confirma el stock al crear el pedido (comportamiento interino, no contrato de Productos)

#### Scenario: Todas las líneas disponibles
- **DADO** un carrito en el que ninguna línea está `AGOTADO`
- **CUANDO** se inicia el checkout
- **ENTONCES** la validación pasa y el checkout continúa (SPEC-14)

#### Scenario: Ventas rechaza por stock al crear el pedido
- **DADO** que la revalidación pasó pero Ventas responde `409` por falta de stock al crear el pedido (por ejemplo, cantidad mayor a la disponible)
- **CUANDO** ocurre
- **ENTONCES** se vuelve al carrito con la revalidación de todas las líneas y se informa al cliente "No hay stock suficiente para alguna de tus cantidades; ajusta tu carrito", sin cobrar (SPEC-15)

### Requirement: Nunca asumir disponibilidad
El sistema DEBE (SHALL) rechazar la adición o el checkout cuando no puede obtener una disponibilidad válida, y NO DEBE (SHALL NOT) tomar decisiones comerciales positivas a partir de respuestas incompletas o incompatibles: un lote al que le falta un SKU pedido, un SKU que no coincide exactamente con el pedido, un estado o resultado fuera de la lista del contrato, o un payload que no respeta el OpenAPI de Productos. Esos casos se tratan como "disponibilidad no obtenida", distinta de un `INDETERMINADO` contractual válido (que sí se acepta con aviso, Requisito 1), y nunca se interpretan como `AGOTADO`. Las respuestas `401`, `403`, `422`, `429` y `503` se manejan según su semántica HTTP y no se convierten en estados comerciales.

*Trazabilidad: SPEC-10 · Requisito 3.*

#### Scenario: Inventario no disponible al agregar
- **DADO** que Productos no responde en 3 s
- **CUANDO** el cliente agrega un producto
- **ENTONCES** no se agrega, se responde `503 SERVICIO_NO_DISPONIBLE` y el chat dice "No puedo confirmar el stock ahora; intenta en unos segundos" con el botón "Reintentar"

#### Scenario: Respuesta incompleta o incompatible
- **DADO** una consulta de disponibilidad cuya respuesta omite uno de los SKU pedidos, trae un estado desconocido o no respeta el esquema del contrato
- **CUANDO** el cliente agrega ese SKU o inicia el checkout
- **ENTONCES** se aplica el mismo tratamiento que si Productos no respondiera: no se agrega ni se continúa, no se informa que el SKU está agotado y el chat dice "No puedo confirmar el stock ahora; intenta en unos segundos"

#### Scenario: Disponibilidad no disponible solo para mostrar
- **DADO** una búsqueda en la que falla la consulta de disponibilidad, o falta la fila de un SKU, pero sí se obtuvieron los productos
- **CUANDO** se renderizan las tarjetas
- **ENTONCES** se muestran sin el badge de disponibilidad (ni "Disponible" ni "Agotado"), y la validación se hará al agregar

#### Scenario: Error de autorización o límite de frecuencia
- **DADO** que la consulta de disponibilidad responde `401`, `403` o `429`
- **CUANDO** se procesa la respuesta
- **ENTONCES** no se traduce en `AGOTADO` ni en `INDETERMINADO`: se trata como disponibilidad no obtenida, se registra con su `X-Correlation-Id` y, ante `429`, se respeta `Retry-After` si viene

### Requirement: Consulta explícita de disponibilidad
El sistema DEBE (SHALL) responder preguntas de stock sobre un producto o una variante con el estado comercial (`DISPONIBLE`, `STOCK_BAJO`, `AGOTADO` o `INDETERMINADO`), sin revelar cantidades (Productos no las expone ni las expondrá en el chatbot).

*Trazabilidad: SPEC-10 · Requisito 4.*

#### Scenario: Consulta de talla
- **DADO** el mensaje "¿tienen las Ultraboost en 40?"
- **CUANDO** se consulta
- **ENTONCES** se responde "Sí, hay disponibilidad en talla 40" (o "Quedan pocas unidades" si el estado es `STOCK_BAJO`, o "Está agotada en talla 40" si es `AGOTADO`) con el botón "Agregar" cuando no está agotada

#### Scenario: Disponibilidad que no se puede confirmar
- **DADO** una consulta cuyo estado es `INDETERMINADO`
- **CUANDO** se responde
- **ENTONCES** se dice "No puedo confirmar el stock ahora mismo" y no se afirma ni que hay ni que no hay

#### Scenario: Consulta de una variante inexistente
- **DADO** una talla que el producto no maneja
- **CUANDO** se consulta
- **ENTONCES** se informa qué tallas maneja el producto
