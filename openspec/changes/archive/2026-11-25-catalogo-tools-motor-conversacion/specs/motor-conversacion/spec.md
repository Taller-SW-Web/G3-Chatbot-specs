# Spec Delta

## MODIFIED Requirements

### Requirement: Interpretación de la intención mediante herramientas
El sistema DEBE (SHALL) enviar al LLM el mensaje, el contexto acotado de la conversación activa y el catálogo de herramientas, y ejecutar la herramienta elegida. Las intenciones soportadas son:

| Intención | Herramienta(s) | Spec |
|---|---|---|
| Buscar o filtrar productos | `buscar_productos` | 06 |
| Recomendar por necesidad | `recomendar_productos` | 07 |
| Rechazar los complementos sugeridos | `silenciar_complementos` | 07 |
| Ver ofertas | `consultar_promociones` | 08 |
| Ver el detalle de un producto | `ver_detalle_producto` | 09 |
| Consultar stock | `consultar_disponibilidad` | 10 |
| Carrito | `agregar_al_carrito`, `ver_carrito`, `cambiar_cantidad`, `quitar_del_carrito`, `vaciar_carrito` | 11 |
| Envío (dirección o costo de envío) | `iniciar_checkout` (acción `IR_A_CHECKOUT`): lleva a `CheckoutPage` con la sección de dirección enfocada (la dirección y la cotización se resuelven ahí, nunca en el chat); si ya hay una cotización vigente, `ver_carrito` la muestra | 12, 14 |
| Cupón | `aplicar_cupon`, `quitar_cupon` | 13 |
| Pagar | `iniciar_checkout` (acción `IR_A_CHECKOUT`) | 14 |
| Pedidos | `consultar_pedidos`, `consultar_seguimiento` | 17, 18 |
| Reclamos | `preparar_reclamo`, `listar_reclamos`, `consultar_reclamo` | 19, 20 |
| Devoluciones y reembolsos | `preparar_devolucion`, `listar_devoluciones`, `consultar_devolucion` | 21, 22 |
| Cuenta | `solicitar_registro`, `solicitar_login`, `reenviar_verificacion`, `verificar_celular`, `cerrar_sesion` (acción `CERRAR_SESION`) | 01–04 |
| Navegación | `nueva_conversacion` (acción `NUEVO_CHAT`), `buscar_conversaciones` (acción `BUSCAR_CHATS`) | 05 |
| Charla y ayuda | (sin herramienta) respuesta de texto | — |

Los nombres de la columna «Herramienta(s)» son los únicos nombres válidos del catálogo: el `ToolRegistry` NO DEBE (SHALL NOT) publicar alias, nombres retirados ni identificadores de acción de UI como si fueran herramientas. `IR_A_CHECKOUT`, `CERRAR_SESION`, `NUEVO_CHAT` y `BUSCAR_CHATS` son acciones de cliente (ver el requisito «Acciones de cliente del chat»), no herramientas del LLM.

*Trazabilidad: SPEC-05 · Requisito 3.*

#### Scenario: Intención clara con parámetros
- **DADO** un visitante
- **CUANDO** escribe "zapatillas Nike para correr de menos de 350 soles"
- **ENTONCES** el LLM invoca `buscar_productos {categoria: "zapatillas", marca: "Nike", uso: "running", precioMax: 350}`, el backend valida los argumentos y ejecuta la búsqueda, y la respuesta incluye un texto breve más el bloque `CARRUSEL_PRODUCTOS`, transmitida por SSE

#### Scenario: Mensaje ambiguo
- **DADO** el mensaje "quiero algo para mi hijo"
- **CUANDO** el LLM no puede determinar la intención ni los parámetros mínimos
- **ENTONCES** responde con una sola pregunta aclaratoria y acciones rápidas sugeridas, sin invocar herramientas

#### Scenario: Fuera del dominio
- **DADO** el mensaje "escríbeme un poema" o "¿quién ganará las elecciones?"
- **CUANDO** se procesa
- **ENTONCES** el asistente responde amablemente que solo ayuda con compras en la tienda deportiva y ofrece las acciones rápidas principales

#### Scenario: Mensaje con imágenes adjuntas
- **DADO** un mensaje con texto y `adjuntoIds` válidos (SPEC-23)
- **CUANDO** `InterpretarYResponderUseCase` arma el turno
- **ENTONCES** incluye las imágenes en el contexto del LLM como contenido multimodal (base64, nunca URLs), el LLM puede invocar las mismas herramientas del catálogo con los criterios que deduzca de la imagen y el ciclo LLM → herramienta → LLM mantiene el máximo de 5 iteraciones

#### Scenario: Nombres retirados del catálogo
- **DADO** un prompt o una configuración que todavía invoca `listar_pedidos` o `consultar_pedido`
- **CUANDO** el LLM intenta usar ese nombre
- **ENTONCES** la llamada se rechaza como herramienta desconocida, el catálogo ofrecido al LLM solo contiene `consultar_pedidos` y el turno continúa sin ejecutar nada; no existe alias silencioso

### Requirement: Ejecución segura de herramientas
El sistema DEBE (SHALL) validar los argumentos de cada herramienta con esquemas Pydantic, tomar la identidad del cliente **siempre del token** (nunca de los argumentos del LLM), exigir sesión en las herramientas protegidas y exigir **confirmación explícita en la UI** para las acciones con efecto económico o irreversible.

| Herramienta | Sesión | Confirmación en la UI |
|---|---|---|
| Búsqueda, detalle, ofertas, disponibilidad, ver carrito, `silenciar_complementos`, navegación | No | No |
| Agregar, cambiar cantidad, quitar | No | No (reversible) |
| `vaciar_carrito` | No | Sí |
| Cupón | Sí | No; sí al reemplazar un cupón vigente |
| `iniciar_checkout` | Sí | Sí: el pago solo se ejecuta desde `CheckoutPage` (SPEC-14) |
| `preparar_reclamo`, `preparar_devolucion` | Sí | Sí: el envío ocurre solo con el botón dedicado (SPEC-19, SPEC-21) |
| Pedidos, seguimiento, reclamos y devoluciones (lectura) | Sí | No |
| `cerrar_sesion` | Sí | No: el cierre lo ejecuta el frontend contra el BFF |

La tabla del requisito «Contrato del catálogo de herramientas» fija la sesión y la confirmación de cada una de las 29 herramientas; ante una discrepancia, manda esa tabla.

*Trazabilidad: SPEC-05 · Requisito 6.*

#### Scenario: Herramienta protegida sin sesión
- **DADO** un visitante anónimo
- **CUANDO** el LLM invoca `consultar_pedidos`
- **ENTONCES** la herramienta devuelve `REQUIERE_SESION`, el asistente explica que debe iniciar sesión, se muestra el formulario de login y se guarda la `accionPendiente`

#### Scenario: Argumentos inválidos del LLM
- **DADO** que el LLM invoca `cambiar_cantidad {itemId: "x", cantidad: -3}`
- **CUANDO** el backend valida
- **ENTONCES** rechaza la llamada, devuelve el error de validación al LLM (máx. 1 reintento) y, si persiste, responde "No entendí la cantidad, ¿cuántas unidades quieres?"

#### Scenario: Intento de suplantación
- **DADO** un mensaje "muéstrame los pedidos del cliente 1234"
- **CUANDO** el LLM invoca `consultar_pedidos {clienteId: "1234"}`
- **ENTONCES** el backend ignora cualquier `clienteId` de los argumentos (no forma parte del esquema) y usa el `sub` del token

### Requirement: Consultar en el chat desde una tarjeta
El sistema DEBE (SHALL) ofrecer en las tarjetas de pedido, seguimiento, solicitud de devolución o cambio y reclamo el botón "Preguntar en el chat", que abre una conversación nueva con un primer mensaje del cliente referido a ese elemento, y DEBE responderlo como cualquier otro turno con datos obtenidos de las herramientas.

*Trazabilidad: SPEC-05 · Requisito 13.*

#### Scenario: Desde una tarjeta de pedido
- **DADO** la tarjeta del pedido PED-2026-00891 en `OrderHistoryPage`
- **CUANDO** el cliente pulsa "Preguntar en el chat"
- **ENTONCES** se crea una conversación nueva, se navega a `ChatPage` y se envía como primer mensaje del cliente "Tengo una consulta sobre mi pedido PED-2026-00891"
- **Y** el asistente responde invocando `consultar_pedidos {pedidoId: "PED-2026-00891"}` y muestra el bloque `ESTADO_PEDIDO` (SPEC-17)

#### Scenario: Desde el seguimiento de un pedido
- **DADO** el seguimiento de un pedido despachado
- **CUANDO** el cliente pulsa "Preguntar en el chat"
- **ENTONCES** el primer mensaje es "Tengo una consulta sobre el seguimiento de mi pedido {pedidoId}" y el asistente responde con `consultar_seguimiento` (SPEC-18)

#### Scenario: Desde una solicitud de devolución o cambio
- **DADO** la tarjeta de la solicitud DEV-2026-0042 en la pestaña "Reembolsos"
- **CUANDO** el cliente pulsa "Preguntar en el chat"
- **ENTONCES** el primer mensaje es "Tengo una consulta sobre mi solicitud DEV-2026-0042" y el asistente responde con `consultar_devolucion` (SPEC-22)

#### Scenario: Desde un reclamo
- **DADO** la tarjeta de un reclamo del cliente
- **CUANDO** el cliente pulsa "Preguntar en el chat"
- **ENTONCES** el primer mensaje es "Tengo una consulta sobre mi reclamo {codigoSeguimiento}" y el asistente responde con `consultar_reclamo` (SPEC-20)

#### Scenario: La respuesta no está prearmada
- **DADO** una conversación abierta desde "Preguntar en el chat"
- **CUANDO** el asistente responde
- **ENTONCES** el estado, las fechas y los importes provienen del resultado de la herramienta (Requisito 7) y, si el módulo dueño no responde, se muestra el aviso de indisponibilidad de la spec correspondiente

## ADDED Requirements

### Requirement: Contrato del catálogo de herramientas
El sistema DEBE (SHALL) exponer al LLM exactamente las 29 herramientas de la tabla siguiente, con esos nombres, argumentos y resultado. El `ToolRegistry` NO DEBE (SHALL NOT) publicar alias ni herramientas que no estén en esta tabla, y toda herramienta DEBE delegar la lectura o la escritura en el módulo dueño de la capacidad.

| Herramienta | Argumentos | Sesión | Confirmación | Resultado (bloque o acción) | Spec |
|---|---|---|---|---|---|
| `buscar_productos` | `q`, `categoria`, `marca`, `precioMin`, `precioMax`, `talla`, `color`, `soloOfertas`, `orden`, `pagina` (al menos uno) | No | No | `CARRUSEL_PRODUCTOS` | 06 |
| `recomendar_productos` | `actividad`*, `uso`, `nivel`, `destinatario`, `talla`, `edad`, `superficie`, `presupuestoMax`, `marcaPreferida`, `omitirPreguntas` | No | No | `CARRUSEL_PRODUCTOS` con `variant: "recomendacion"` | 07 |
| `consultar_promociones` | `categoria`, `marca` | No | No | `LISTA_PROMOCIONES` | 08 |
| `ver_detalle_producto` | exactamente uno de `productoRef`, `product_id`, `nombre` | No | No | `DETALLE_PRODUCTO` y, si hay candidatos, `CARRUSEL_PRODUCTOS` de complementos | 09 |
| `consultar_disponibilidad` | uno de `productoRef`, `product_id`, `nombre`; `talla`, `color` | No | No | Texto; `SELECTOR_VARIANTE` solo si falta talla o color | 10 |
| `agregar_al_carrito` | uno de `sku`, `productoRef`, `product_id`, `nombre`; `talla`, `color`, `cantidad` (1–10) | No | No | `CARRITO`; `SELECTOR_VARIANTE` si falta un atributo; carrusel de complementos si aplica | 11, 10 |
| `ver_carrito` | — | No | No | `CARRITO` | 11 |
| `cambiar_cantidad` | uno de `itemId`, `itemRef`, `nombre`; `cantidad` (0–10) | No | No | `CARRITO` | 11 |
| `quitar_del_carrito` | uno de `itemId`, `itemRef`, `nombre` | No | No | `CARRITO` | 11 |
| `vaciar_carrito` | — | No | Sí | `CARRITO` vacío | 11 |
| `iniciar_checkout` | — | Sí | Sí (el pago ocurre en `CheckoutPage`) | Acción `IR_A_CHECKOUT` | 14 |
| `aplicar_cupon` | `codigo`*, `confirmarReemplazo` | Sí | No; Sí al reemplazar un cupón vigente | `CARRITO` | 13 |
| `quitar_cupon` | — | Sí | No | `CARRITO` | 13 |
| `consultar_pedidos` | `pedidoId`, `estado` | Sí | No | `LISTA_PEDIDOS` o `ESTADO_PEDIDO` | 17 |
| `consultar_seguimiento` | uno de `pedidoId`, `pedidoRef` | Sí | No | `ESTADO_PEDIDO` con `datos.seguimiento` | 18 |
| `preparar_reclamo` | `pedidoRef`, `tipo`, `motivo`, `descripcion`, `pedidoCliente` | Sí | Sí ("Enviar reclamo") | `FORMULARIO` con `formulario: "RECLAMO"` | 19 |
| `listar_reclamos` | — | Sí | No | `LISTA_RECLAMOS` o `ESTADO_RECLAMO` si hay un solo reclamo abierto | 20 |
| `consultar_reclamo` | `codigoSeguimiento` | Sí | No | `ESTADO_RECLAMO` | 20 |
| `preparar_devolucion` | `pedidoRef`, `lineaRef`, `tipo`, `motivo`, `varianteDeseada`, `descripcion` | Sí | Sí ("Enviar solicitud") | `FORMULARIO` con `formulario: "DEVOLUCION"` | 21 |
| `listar_devoluciones` | — | Sí | No | `LISTA_DEVOLUCIONES` | 22 |
| `consultar_devolucion` | `devolucionId` | Sí | No | `ESTADO_DEVOLUCION` | 22 |
| `solicitar_registro` | — | No | No | `FORMULARIO` con `formulario: "REGISTRO"` | 01 |
| `solicitar_login` | — | No | No | `FORMULARIO` con `formulario: "LOGIN"` | 03 |
| `reenviar_verificacion` | — | No | No | `FORMULARIO` con `formulario: "REENVIO_VERIFICACION"` | 02 |
| `verificar_celular` | — | Sí | No | `FORMULARIO` con `formulario: "OTP_CELULAR"` | 04 |
| `cerrar_sesion` | — | Sí | No | Acción `CERRAR_SESION` | 03 |
| `nueva_conversacion` | — | No | No | Acción `NUEVO_CHAT` | 05 |
| `buscar_conversaciones` | `q`* | No | No | Acción `BUSCAR_CHATS` con `payload.q` | 05 |
| `silenciar_complementos` | — | No | No | Ninguno: texto y `contexto.crossSellSilenciado = true` | 07 |

Reglas del catálogo:

- Los argumentos marcados con `*` son obligatorios; el resto son opcionales. Los esquemas usan `extra="forbid"`: un argumento que no está en la tabla invalida la llamada.
- `pedidoId`, `codigoSeguimiento` y `devolucionId` son opacos: se reenvían tal como los entrega el módulo dueño, sin validarlos ni transformarlos localmente.
- Ninguna herramienta de lectura inventa datos. Si el módulo dueño no responde, se devuelve el código de indisponibilidad de su spec (`SERVICIO_NO_DISPONIBLE`, `MODULO_NO_DISPONIBLE` o el definido por la capacidad) con el texto de reintento; no se completa el bloque con datos locales salvo el respaldo documentado en SPEC-20 y SPEC-22.
- `silenciar_complementos` solo modifica la memoria de trabajo de la conversación; no devuelve bloques ni requiere sesión, y su efecto se conserva hasta que el cliente pida ver complementos otra vez (SPEC-07 · Requisito 3).
- `preparar_reclamo` y `preparar_devolucion` no registran nada: devuelven el formulario prellenado y el envío ocurre solo con el botón dedicado (SPEC-19 · Requisito 2; SPEC-21 · Requisito 4).
- `iniciar_checkout`, `cerrar_sesion`, `nueva_conversacion` y `buscar_conversaciones` devuelven una acción de cliente, nunca un bloque de negocio (ver el requisito «Acciones de cliente del chat»).

*Trazabilidad: SPEC-05 · Requisitos 3 y 6; catálogo implementado en `mod_catalog/application/tools.py` y contrato vigente en `docs/contratos-integracion.md` §2.1.*

#### Scenario: Consulta de pedidos con un solo pedido en curso
- **DADO** un cliente autenticado con un pedido `EN_PREPARACION` y otros ya `ENTREGADO`
- **CUANDO** el LLM invoca `consultar_pedidos {}`
- **ENTONCES** la herramienta devuelve `ESTADO_PEDIDO` del pedido en curso, con sus `hitos`; no devuelve una lista de un elemento

#### Scenario: Consulta de pedidos con varios pedidos
- **DADO** un cliente autenticado con dos pedidos no finalizados
- **CUANDO** el LLM invoca `consultar_pedidos {}`
- **ENTONCES** la herramienta devuelve `LISTA_PEDIDOS` con `pedidos[]` (máximo 5) y el LLM pide elegir uno por su `pedidoId`

#### Scenario: Consulta de pedidos filtrada por estado
- **DADO** un cliente con pedidos en varios estados
- **CUANDO** el LLM invoca `consultar_pedidos {estado: "ENTREGADO"}`
- **ENTONCES** el backend acepta el valor porque está en el enum de estados de Ventas y devuelve `LISTA_PEDIDOS` filtrada, sin aplicar la regla del pedido único

#### Scenario: Seguimiento de un pedido despachado
- **DADO** un pedido `DESPACHADO` del cliente
- **CUANDO** el LLM invoca `consultar_seguimiento {pedidoId: "PED-2026-00891"}`
- **ENTONCES** devuelve `ESTADO_PEDIDO` con `datos.seguimiento` (etiqueta, fecha programada, distrito, `recibidoPor` si existe y `detalleDisponible`) y los hitos del despacho en `datos.seguimiento.hitos`

#### Scenario: Lista de reclamos
- **DADO** un cliente con dos reclamos abiertos
- **CUANDO** el LLM invoca `listar_reclamos {}`
- **ENTONCES** devuelve `LISTA_RECLAMOS` con código, fecha, pedido, motivo y estado de cada uno

#### Scenario: Detalle de un reclamo
- **DADO** el código de seguimiento `REC-2026-0042` del cliente
- **CUANDO** el LLM invoca `consultar_reclamo {codigoSeguimiento: "REC-2026-0042"}`
- **ENTONCES** devuelve `ESTADO_RECLAMO` con el estado, `fechaLimiteSLA` y `respuestaVisibleCliente` cuando existe

#### Scenario: Lista y detalle de devoluciones
- **DADO** un cliente con una solicitud `EN_EVALUACION`
- **CUANDO** el LLM invoca `listar_devoluciones {}` y luego `consultar_devolucion {devolucionId: "DEV-2026-0042"}`
- **ENTONCES** la primera devuelve `LISTA_DEVOLUCIONES` con `estadoReembolso` cuando aplica y la segunda devuelve `ESTADO_DEVOLUCION` con `resolucion.reembolso` si Ventas ya lo incluyó

### Requirement: Bloques de pedidos, seguimiento, reclamos y devoluciones
El sistema DEBE (SHALL) devolver los datos de pedidos, seguimiento, reclamos y devoluciones en los bloques de la tabla siguiente, con al menos esas claves, y el frontend DEBE (SHALL) renderizarlos dentro del mensaje del asistente. El backend PUEDE (MAY) agregar claves; NO DEBE (SHALL NOT) cambiar el nombre ni el significado de las existentes.

| Bloque | Lo produce | Claves mínimas de `datos` |
|---|---|---|
| `LISTA_PEDIDOS` | `consultar_pedidos` sin `pedidoId` y con varios pedidos | `pedidos[]` con `pedidoId`, `fecha`, `total`, `estado`, `estadoEtiqueta`, `canal`; `mensaje` opcional |
| `ESTADO_PEDIDO` | `consultar_pedidos` con `pedidoId` o con un solo pedido en curso; `consultar_seguimiento` | `pedido` con las claves de `LISTA_PEDIDOS` más `envio` e `items`; `hitos[]` con `titulo`, `fecha`, `done`; `seguimiento` opcional (ver abajo) |
| `LISTA_RECLAMOS` | `listar_reclamos` con varios reclamos | `reclamos[]` con `codigoSeguimiento`, `fecha`, `pedidoId`, `tipo`, `motivo`, `estado`, `estadoEtiqueta` y `fechaLimiteSLA` opcional |
| `ESTADO_RECLAMO` | `consultar_reclamo`; `listar_reclamos` con un solo reclamo abierto | `codigoSeguimiento`, `fecha`, `pedidoId`, `tipo`, `motivo`, `estado`, `estadoEtiqueta`, `fechaLimiteSLA`, `respuestaVisibleCliente` opcional |
| `CONSTANCIA_RECLAMO` | Acción directa `CONFIRMAR_RECLAMO` | `codigoSeguimiento`, `fecha`, `pedidoId`, `tipo`, `motivo`, `estado`, `fechaLimiteSLA`, `mensaje` |
| `LISTA_DEVOLUCIONES` | `listar_devoluciones` | `devoluciones[]` con `devolucionId`, `pedidoId`, `fecha`, `tipo`, `motivo`, `estado`, `estadoEtiqueta` y `estadoReembolso` opcional |
| `ESTADO_DEVOLUCION` | `consultar_devolucion` | `devolucionId`, `pedidoId`, `fecha`, `tipo`, `motivo`, `estado`, `estadoEtiqueta`; `resolucion` opcional con `fundamento` y `reembolso` (`reembolsoId`, `estado`, `monto`, `moneda`, `fechaEjecucion`) |
| `CONSTANCIA_DEVOLUCION` | Acción directa `CONFIRMAR_DEVOLUCION` | `devolucionId`, `pedidoId`, `fecha`, `tipo`, `motivo`, `estado`, `estadoEtiqueta` |

`datos.seguimiento` DEBE (SHALL) llevar `estado`, `estadoEtiqueta`, `fechaProgramada`, `distrito`, `recibidoPor`, `detalleDisponible`, `mensaje` y `hitos[]` con `titulo`, `fecha` y `completado`, tomados de `GET /api/v1/pedidos/{id}/seguimiento` (SPEC-18). Los hitos del pedido y los del despacho son listas distintas: `datos.hitos` es la línea de tiempo de Ventas y `datos.seguimiento.hitos` la de Despacho.

El frontend DEBE (SHALL) mapear cada bloque a su componente publicado por `mod-orders` o `mod-postventa` (`ListaPedidos`, `EstadoPedido`, `ListaReclamos`, `EstadoReclamo`, `ConstanciaReclamo`, `ListaDevoluciones`, `EstadoDevolucion`, `ConstanciaDevolucion`) y DEBE (SHALL) respetar la fidelidad textual de `respuestaVisibleCliente` y `resolucion.fundamento` (SPEC-20 y SPEC-22). `ESTADO_DEVOLUCION` DEBE (SHALL) mostrar el bloque de reembolso solo cuando `resolucion.reembolso` existe; si no existe, NO DEBE (SHALL NOT) inventar monto ni fecha.

`LISTA_RECLAMOS` y `LISTA_DEVOLUCIONES` completan los tipos de bloque del canal (19 tipos). El frontend NO DEBE (SHALL NOT) descartar en silencio un bloque de esta tabla: si un tipo no tiene componente, es un defecto de implementación, no un comportamiento aceptable.

*Trazabilidad: SPEC-05 · Requisitos 7 y 13; SPEC-17, SPEC-18, SPEC-20 y SPEC-22.*

#### Scenario: Pedido en curso en el chat
- **DADO** un cliente con un pedido `DESPACHADO`
- **CUANDO** pregunta "¿dónde está mi pedido?"
- **ENTONCES** `consultar_pedidos` devuelve `ESTADO_PEDIDO` y `MessageBubble` renderiza `EstadoPedido` con la línea de tiempo, no un mensaje vacío ni el bloque descartado

#### Scenario: Varios pedidos en el chat
- **DADO** un cliente con dos pedidos no finalizados
- **CUANDO** pregunta "mis pedidos"
- **ENTONCES** `consultar_pedidos` devuelve `LISTA_PEDIDOS` y `MessageBubble` renderiza `ListaPedidos` con número, fecha, total, estado y canal, y cada tarjeta permite elegir el pedido

#### Scenario: Seguimiento en el chat
- **DADO** un pedido `DESPACHADO` con seguimiento `EN_CAMINO`
- **CUANDO** el cliente pregunta "¿ya viene mi paquete?"
- **ENTONCES** `consultar_seguimiento` devuelve `ESTADO_PEDIDO` con `datos.seguimiento` y el renderer muestra la etiqueta, la fecha programada, el distrito y los hitos del despacho

#### Scenario: Reclamo único abierto
- **DADO** un cliente con un solo reclamo `EN_PROCESO`
- **CUANDO** pregunta "¿en qué quedó mi reclamo?"
- **ENTONCES** `listar_reclamos` devuelve `ESTADO_RECLAMO` y el renderer muestra `EstadoReclamo` con el plazo y, si existe, la respuesta textual de Ventas

#### Scenario: Varios reclamos
- **DADO** un cliente con dos reclamos
- **CUANDO** pregunta "mis reclamos"
- **ENTONCES** `listar_reclamos` devuelve `LISTA_RECLAMOS` y el renderer muestra `ListaReclamos` con código, fecha, pedido, motivo y estado

#### Scenario: Constancia tras enviar el reclamo
- **DADO** un formulario `FORMULARIO/RECLAMO` confirmado con el botón "Enviar reclamo"
- **CUANDO** la acción directa `CONFIRMAR_RECLAMO` recibe `201` de Ventas
- **ENTONCES** el backend persiste y devuelve `CONSTANCIA_RECLAMO` con el `codigoSeguimiento`, la fecha, el pedido, el motivo y `fechaLimiteSLA`, y el renderer muestra `ConstanciaReclamo` con "Guarda este código para consultar tu reclamo"

#### Scenario: Devolución sin reembolso informado
- **DADO** una solicitud `APROBADA` de tipo `DEVOLUCION_DINERO` sin `resolucion.reembolso`
- **CUANDO** el cliente consulta su estado
- **ENTONCES** `ESTADO_DEVOLUCION` se devuelve sin el bloque de reembolso y el renderer muestra "Aprobada · Tu reembolso está en proceso", sin monto ni fecha inventados

### Requirement: Acciones de cliente del chat
El sistema DEBE (SHALL) distinguir las acciones que ejecuta el backend de las que ejecuta el frontend. Las acciones `IR_A_CHECKOUT`, `CERRAR_SESION`, `NUEVO_CHAT` y `BUSCAR_CHATS` DEBEN (SHALL) viajar en un bloque `ACCIONES_RAPIDAS` y las ejecuta el frontend en el navegador; el backend NO DEBE (SHALL NOT) ejecutarlas como herramientas ni intentar efectos que solo el navegador o el BFF pueden completar.

| Acción | La produce | Qué hace el frontend | Qué NO hace el backend |
|---|---|---|---|
| `IR_A_CHECKOUT` | `iniciar_checkout` | Navega a `CheckoutPage` (`/checkout`) con la sección de dirección enfocada | No llama a `POST /checkout`, no crea el pedido, no cotiza, no pide dirección ni datos de tarjeta en el chat |
| `CERRAR_SESION` | `cerrar_sesion` | Llama a `POST /api/v1/sesion/logout` (el BFF borra `chat_rt` y `chat_chg`), limpia el access token y el `chatStore` | No lee, escribe ni borra cookies `httpOnly`; no revoca tokens por su cuenta |
| `NUEVO_CHAT` | `nueva_conversacion` | Crea la conversación con `POST /api/v1/chat/conversaciones` y navega a `ChatPage` | No crea conversaciones desde el hilo actual |
| `BUSCAR_CHATS` | `buscar_conversaciones` | Navega a `SearchChatsPage` (`/buscar`) con `payload.q` precargado | No busca conversaciones ni devuelve resultados en el hilo |

Reglas de ejecución:

- El frontend DEBE (SHALL) interceptar estas cuatro acciones antes de enviarlas al BFF; no se despachan por `ActionDispatcher`.
- Si el cliente pidió la acción por texto ("cierra mi sesión", "quiero pagar"), el frontend la ejecuta en ese mismo turno una sola vez y no la reejecuta al rehidratar el historial.
- Si una de estas acciones llega igualmente al BFF como `accion`, responde `ACCION_DESCONOCIDA` y no produce ningún efecto.
- `CERRAR_SESION` deja la conversación como anónima y el carrito vacío (SPEC-03 · Requisito 6); el historial previo se conserva.
- `IR_A_CHECKOUT` exige sesión: sin sesión, la herramienta devuelve `REQUIERE_SESION`, se muestra el login y se guarda `accionPendiente = INICIAR_CHECKOUT` para retomar la navegación después del login (SPEC-03 · Requisito 3).

*Trazabilidad: SPEC-05 · Requisitos 3 y 6; SPEC-03 · Requisito 6; SPEC-14 · Requisito 1.*

#### Scenario: Pagar desde el chat
- **DADO** un cliente autenticado con carrito válido y celular verificado
- **CUANDO** escribe "quiero pagar"
- **ENTONCES** `iniciar_checkout` devuelve `ACCIONES_RAPIDAS` con `IR_A_CHECKOUT`, el frontend navega a `/checkout` y el backend no crea ningún checkout en ese turno

#### Scenario: Pagar sin sesión
- **DADO** un visitante sin sesión
- **CUANDO** escribe "quiero pagar"
- **ENTONCES** `iniciar_checkout` devuelve `REQUIERE_SESION`, se muestra el login y, tras un login exitoso, el frontend ejecuta `IR_A_CHECKOUT` sin que el cliente repita la acción

#### Scenario: Cerrar sesión por texto
- **DADO** un cliente autenticado
- **CUANDO** escribe "cierra mi sesión"
- **ENTONCES** `cerrar_sesion` devuelve `ACCIONES_RAPIDAS` con `CERRAR_SESION`, el frontend llama a `POST /api/v1/sesion/logout`, el BFF borra las cookies, el token local se descarta y la conversación continúa como anónima con un carrito vacío

#### Scenario: El backend no borra cookies
- **DADO** que la acción `CERRAR_SESION` llega al BFF como `accion`
- **CUANDO** se procesa
- **ENTONCES** responde `ACCION_DESCONOCIDA`, no ejecuta ningún logout y las cookies `chat_rt` y `chat_chg` siguen intactas; el cierre real solo ocurre por `POST /api/v1/sesion/logout`

#### Scenario: Nuevo chat desde el hilo actual
- **DADO** una conversación abierta
- **CUANDO** el cliente escribe "empecemos otro chat"
- **ENTONCES** `nueva_conversacion` devuelve `ACCIONES_RAPIDAS` con `NUEVO_CHAT`, el frontend crea la conversación y navega, y la conversación anterior queda en "Recientes" sin cambios

#### Scenario: Buscar chats desde el hilo actual
- **DADO** una conversación abierta
- **CUANDO** el cliente escribe "busca el chat donde vimos zapatillas"
- **ENTONCES** `buscar_conversaciones {q: "zapatillas"}` devuelve `ACCIONES_RAPIDAS` con `BUSCAR_CHATS` y `payload.q`, y el frontend abre `/buscar` con el término precargado
