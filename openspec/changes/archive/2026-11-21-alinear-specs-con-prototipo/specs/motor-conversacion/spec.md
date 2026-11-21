## MODIFIED Requirements

### Requirement: Conversaciones múltiples
El sistema DEBE (SHALL) permitir crear una nueva conversación en cualquier momento, listar las conversaciones del cliente (o de la sesión anónima) ordenadas por actividad reciente, y buscar entre ellas desde una pantalla propia.

*Trazabilidad: SPEC-05 · Requisito 1.*

#### Scenario: Nueva conversación desde la barra lateral
- **DADO** un cliente con conversaciones previas
- **CUANDO** pulsa "Nuevo chat"
- **ENTONCES** se crea una conversación vacía con `POST /api/v1/chat/conversaciones`, se navega a `ChatPage` y la barra lateral la agrega al tope de "Recientes" en cuanto tiene el primer mensaje (una conversación sin mensajes no aparece en el listado)

#### Scenario: Listado de conversaciones recientes
- **DADO** un cliente autenticado con 8 conversaciones
- **CUANDO** abre la barra lateral
- **ENTONCES** `GET /api/v1/chat/conversaciones?pagina=1` devuelve las conversaciones ordenadas por `last_message_at` descendente, con un título derivado del primer mensaje del cliente (máx. 40 caracteres) y una vista previa del último mensaje

#### Scenario: Buscar chats
- **DADO** la barra lateral abierta
- **CUANDO** el cliente pulsa "Buscar chats"
- **ENTONCES** se navega a `SearchChatsPage` (ruta `/buscar`), con el campo "Buscar conversaciones" enfocado y la lista "Recientes" con título, vista previa y fecha de cada conversación

#### Scenario: Buscar por texto
- **DADO** `SearchChatsPage`
- **CUANDO** el cliente escribe "zapatillas"
- **ENTONCES** `GET /api/v1/chat/conversaciones/buscar?q=zapatillas` devuelve las conversaciones cuyo título o mensajes contienen el término, resaltando la coincidencia
- **Y** al tocar un resultado se navega a `ChatPage` con esa conversación

#### Scenario: Búsqueda sin resultados
- **DADO** un término sin coincidencias
- **CUANDO** se busca
- **ENTONCES** se muestra `Sin resultados para "{término}"`

#### Scenario: Retomar una conversación
- **DADO** el listado de recientes
- **CUANDO** el cliente toca una conversación
- **ENTONCES** se navega a `ChatPage` con esa conversación, se cargan sus últimos 50 mensajes (`GET /conversaciones/{id}/mensajes`) y se restaura su memoria de trabajo (carrito visible, filtros, etc. según corresponda)

#### Scenario: Conversaciones anónimas y fusión al iniciar sesión
- **DADO** un visitante anónimo con 2 conversaciones (cookie `chat_sid`)
- **CUANDO** inicia sesión
- **ENTONCES** esas conversaciones quedan ligadas a su `customer_id` y aparecen en su listado junto con las que ya tenía

#### Scenario: Historial de pedidos desde la barra lateral
- **DADO** la barra lateral abierta
- **CUANDO** el cliente pulsa "Historial de pedidos"
- **ENTONCES** con sesión se navega a `OrderHistoryPage` en la pestaña "En proceso" (SPEC-17); sin sesión se abre `AuthModal` y, tras un login exitoso, se navega a `OrderHistoryPage`

### Requirement: Pantalla de inicio
El sistema DEBE (SHALL) mostrar, al abrir la app o al no tener ninguna conversación activa, una pantalla que combine un banner de ofertas, un grid de productos en oferta, el campo de conversación y las acciones rápidas fijas "Ver ofertas", "Rastrear pedido" y "Ayuda con devolución".

*Trazabilidad: SPEC-05 · Requisito 2.*

#### Scenario: Primera apertura
- **DADO** un visitante que abre la app por primera vez
- **CUANDO** carga `HomePage`
- **ENTONCES** se muestran el banner de ofertas (carrusel con indicadores) alimentado por `GET /catalogo/promociones` (SPEC-08), un grid de hasta 4 productos en oferta obtenido con la búsqueda `soloOfertas=true` (SPEC-06), el campo de chat en la parte inferior y las tres acciones rápidas fijas, sin necesidad de sesión

#### Scenario: Promociones no disponibles
- **DADO** que `GET /catalogo/promociones` (SPEC-08) todavía no está disponible (Hito 3), falla o no devuelve promociones vigentes
- **CUANDO** carga `HomePage`
- **ENTONCES** el banner de ofertas no se muestra, el grid de productos en oferta (SPEC-06), el campo de chat y las acciones rápidas fijas se muestran igual, y no se muestra ningún error al cliente

#### Scenario: Escribir desde la pantalla de inicio
- **DADO** el campo de chat de `HomePage`
- **CUANDO** el cliente escribe su primer mensaje y lo envía
- **ENTONCES** se crea la conversación en ese momento (no antes) y la app navega a `ChatPage` con ese primer mensaje ya enviado

#### Scenario: Agregar directo desde el grid de ofertas
- **DADO** un producto del grid de la pantalla de inicio
- **CUANDO** el cliente pulsa el botón "+"
- **ENTONCES** se ejecuta la misma acción directa `AGREGAR_AL_CARRITO` que en un carrusel de chat (SPEC-09 y SPEC-11), sin necesidad de abrir una conversación

## ADDED Requirements

### Requirement: Consultar en el chat desde una tarjeta
El sistema DEBE (SHALL) ofrecer en las tarjetas de pedido, seguimiento, solicitud de devolución o cambio y reclamo el botón "Preguntar en el chat", que abre una conversación nueva con un primer mensaje del cliente referido a ese elemento, y DEBE responderlo como cualquier otro turno con datos obtenidos de las herramientas.

*Trazabilidad: SPEC-05 · Requisito 13.*

#### Scenario: Desde una tarjeta de pedido
- **DADO** la tarjeta del pedido PED-2026-00891 en `OrderHistoryPage`
- **CUANDO** el cliente pulsa "Preguntar en el chat"
- **ENTONCES** se crea una conversación nueva, se navega a `ChatPage` y se envía como primer mensaje del cliente "Tengo una consulta sobre mi pedido PED-2026-00891"
- **Y** el asistente responde invocando `consultar_pedido` y muestra el bloque `ESTADO_PEDIDO` (SPEC-17)

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

### Requirement: Acciones rápidas fijas
El sistema DEBE (SHALL) mostrar en `HomePage` y `ChatPage` tres acciones rápidas fijas —"Ver ofertas", "Rastrear pedido" y "Ayuda con devolución"— que inician el flujo correspondiente sin que el cliente escriba.

*Trazabilidad: SPEC-05 · Requisito 14.*

#### Scenario: "Ver ofertas" desde la pantalla de inicio
- **DADO** un visitante sin sesión en `HomePage`
- **CUANDO** pulsa "Ver ofertas"
- **ENTONCES** se crea la conversación, se navega a `ChatPage`, la acción directa queda registrada en el historial y se responde con el bloque `LISTA_PROMOCIONES` (SPEC-08 · Requisito 1)

#### Scenario: "Rastrear pedido" con sesión
- **DADO** un cliente autenticado
- **CUANDO** pulsa "Rastrear pedido"
- **ENTONCES** se aplica la identificación del pedido de SPEC-17 · Requisito 1: con un solo pedido en curso se muestra `ESTADO_PEDIDO`; con varios, `LISTA_PEDIDOS`

#### Scenario: "Ayuda con devolución" con sesión
- **DADO** un cliente autenticado
- **CUANDO** pulsa "Ayuda con devolución"
- **ENTONCES** se inicia el flujo de SPEC-21: elegir el pedido entregado y, si es elegible, mostrar el formulario de devolución o cambio

#### Scenario: Acción que requiere sesión, sin sesión
- **DADO** un visitante sin sesión
- **CUANDO** pulsa "Rastrear pedido" o "Ayuda con devolución"
- **ENTONCES** el asistente explica que debe iniciar sesión, ofrece "Iniciar sesión" y "Crear cuenta" y guarda la `accionPendiente`
- **Y** tras un login exitoso el flujo continúa sin que el cliente repita la acción (SPEC-03 · Requisito 3)

#### Scenario: Convivencia con las acciones de una respuesta
- **DADO** una respuesta del asistente que trae sus propias acciones rápidas
- **CUANDO** se muestra
- **ENTONCES** las acciones de la respuesta aparecen junto al mensaje y las tres fijas siguen visibles en su lugar

#### Scenario: Mientras el asistente responde
- **DADO** un turno en curso
- **CUANDO** el cliente intenta pulsar una acción rápida fija
- **ENTONCES** las tres están deshabilitadas hasta que termina el turno