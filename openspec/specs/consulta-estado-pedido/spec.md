# Consulta de estado del pedido

> Origen: SPEC-17 · Grupo: Seguimiento · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03), [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), Ventas (F1), [`seguimiento-despacho`](../seguimiento-despacho/spec.md) (SPEC-18)

## Responsables

- **Sonny:** consulta del estado y la línea de tiempo en Ventas.
- **Alonso:** herramienta de consulta de pedido.
- **Diego:** pestaña "En proceso" de `OrderHistoryPage`.
- **Nikol (QA):** casos de prueba a partir de los escenarios, pruebas E2E si el flujo es crítico y validación contra la definición de terminado.

## Purpose

Responder "¿dónde está mi pedido?" con el estado actual en lenguaje claro y su línea de tiempo, solo para pedidos del cliente autenticado.

## Contexto

Como el chatbot es el único canal conversacional, debe cubrir el ciclo visible del pedido. El estado lo decide Ventas (F1):

- Estados: `CREADO → PAGADO → EN_PREPARACION → DESPACHADO → ENTREGADO`, con la rama `ANULADO` (valores reales del enum, sin tildes ni espacios, confirmados en `api-contract.md` §1.4).
- Ofrece consulta por identificador (con historial ordenado) y listado por cliente con filtro de estado.
- Valida que el actor pueda acceder al pedido (RNF-02).

Cuando el pedido está `DESPACHADO`, el detalle del tránsito lo aporta Despacho (SPEC-18).

El curso exige la "consulta del estado de un pedido".

## Alcance

Incluye:
- Listado de los pedidos recientes del cliente (los 5 últimos, con "Ver más").
- Consulta de un pedido por número o por selección.
- Mapeo de los estados de Ventas (y de Despacho, si aplica) a etiquetas para el cliente (`contratos-integracion.md §4`).
- Línea de tiempo a partir del historial de Ventas.
- Respuestas a preguntas específicas ("¿ya llegó?", "¿cuándo llega?", "¿por qué se anuló?").
- Pedidos de cualquier canal del cliente: Ventas los lista por cliente.

### Fuera de alcance

- Anular un pedido desde el chat: es F2 de Ventas y no se ofrece en este canal (el cliente puede crear un reclamo).
- Solicitar o consultar devoluciones y cambios: no forman parte de esta spec; se cubren en SPEC-21 (`solicitud-devolucion-cambio`) y SPEC-22 (`consulta-devolucion-reembolso`).
- Historial de pedidos con descarga de comprobantes.

## Requirements

### Requirement: Identificar el pedido
El sistema DEBE (SHALL) determinar a qué pedido se refiere el cliente: si tiene un solo pedido no finalizado lo muestra directamente; si tiene varios, los lista para elegir; si da un número, lo busca.

El listado PUEDE (MAY) filtrarse con los parámetros opcionales `estado`, `desde` y `hasta`. `desde` y `hasta` son fechas ISO (`YYYY-MM-DD`) que filtran por `fechaCreacion` y se reenvían sin transformación a `GET /api/v1/pedidos/me` de Ventas; `page` y `pageSize` conservan la paginación existente. Una fecha con formato inválido o un rango invertido (`desde > hasta`) DEBEN (SHALL) responder `400 VALIDACION` sin llamar a Ventas.

*Trazabilidad: SPEC-17 · Requisito 1. Ampliado 2026-11 con los filtros `desde`/`hasta` publicados por G5.*

#### Scenario: Un solo pedido en curso
- **DADO** un cliente con un pedido `EN_PREPARACION` y otros ya `ENTREGADO`
- **CUANDO** escribe "¿dónde está mi pedido?"
- **ENTONCES** se muestra directamente `ESTADO_PEDIDO` del pedido en curso

#### Scenario: Varios pedidos en curso
- **DADO** dos pedidos no finalizados
- **CUANDO** el cliente pregunta por "mi pedido"
- **ENTONCES** se muestra `LISTA_PEDIDOS` con número, fecha, total, estado y canal de origen, para elegir

#### Scenario: Consulta por número
- **DADO** el mensaje "estado del PED-2026-00891"
- **CUANDO** se consulta
- **ENTONCES** se obtiene `GET /pedidos/PED-2026-00891` y se muestra su estado si pertenece al cliente

#### Scenario: Pedido de otro cliente o inexistente
- **DADO** un número que no existe o que pertenece a otro cliente
- **CUANDO** se consulta
- **ENTONCES** se responde "No encontré ese pedido en tu cuenta" en ambos casos (sin revelar su existencia) y se ofrece ver la lista de pedidos

#### Scenario: Cliente sin pedidos
- **DADO** un cliente sin pedidos
- **CUANDO** pregunta por su pedido
- **ENTONCES** se responde "Aún no tienes pedidos" con "Ver ofertas"

#### Scenario: Filtro por fechas de creación
- **DADO** un cliente con pedidos creados en fechas distintas
- **CUANDO** el BFF recibe `GET /api/v1/pedidos?desde=2026-01-01&hasta=2026-12-31`
- **ENTONCES** reenvía `desde` y `hasta` sin transformación a `GET /api/v1/pedidos/me` de Ventas, la respuesta solo incluye los pedidos cuya `fechaCreacion` cae en el rango indicado y se conservan `page` y `pageSize` de la paginación existente

#### Scenario: Fecha inválida en los filtros
- **DADO** una petición con `desde=2026-13-40` o un `hasta` con formato inválido
- **CUANDO** llega a `GET /api/v1/pedidos`
- **ENTONCES** responde `400 VALIDACION` con `errores[{campo: "desde"|"hasta", mensaje}]`, no se llama a Ventas y no se devuelve ningún listado

#### Scenario: Rango de fechas invertido
- **DADO** una petición con `desde=2026-12-31` y `hasta=2026-01-01` (fechas válidas, pero el rango está invertido)
- **CUANDO** llega a `GET /api/v1/pedidos`
- **ENTONCES** responde `400 VALIDACION` con `errores[{campo: "desde"|"hasta", mensaje}]`, no se llama a Ventas y no se devuelve ningún listado

### Requirement: Mostrar el estado y la línea de tiempo
El sistema DEBE (SHALL) mostrar la etiqueta del estado actual, un resumen del pedido y la línea de tiempo con los hitos del historial (fecha y hora de Lima), y enriquecerla con Despacho cuando el estado sea `DESPACHADO` o `ENTREGADO`.

*Trazabilidad: SPEC-17 · Requisito 2; SPEC-15 · Requisito 2; SPEC-16 · Requisito 1; backend#182.*

#### Scenario: Pedido en preparación
- **DADO** un pedido `EN_PREPARACION`
- **CUANDO** se muestra
- **ENTONCES** aparecen el paso "En preparación" resaltado, los pasos "Pago confirmado" (con fecha) y "Pedido registrado" completados, y los siguientes ("Despachado" y "Entregado") en gris

#### Scenario: Pedido despachado
- **DADO** un pedido `DESPACHADO`
- **CUANDO** se muestra
- **ENTONCES** el estado se completa con la etiqueta de Despacho (por ejemplo "En camino") y sus hitos (SPEC-18)

#### Scenario: Pedido anulado
- **DADO** un pedido `ANULADO`
- **CUANDO** se muestra en el detalle, el seguimiento o el chat
- **ENTONCES** se ve "Anulado el {fecha}" con `motivoAnulacion` (solo si el `motivo` del historial de Ventas está en la lista de códigos conocidos: `STOCK_NO_DISPONIBLE` y los de `MotivoAnulacion` de G5: `PAGO_NO_COMPLETADO`, `ERROR_SELECCION_PRODUCTO`, `ARREPENTIMIENTO_COMPRA`, `SOLICITUD_CLIENTE`, `ERROR_DATOS_ENVIO` y `DUPLICADO`; un motivo desconocido o de texto libre produce `motivoAnulacion: null` y el mensaje genérico "Tu pedido fue anulado.", sin que llegue al cliente ningún texto interno). `reembolso` ("Se procesará el reembolso al medio de pago original.") solo se informa cuando el pedido está `ANULADO` y hay evidencia de pago (`pago.estado` `CONFIRMADO` o `PAGADO` en `historialEstados`); el motivo solo elige el mensaje de anulación. Sin evidencia de pago (por ejemplo `PAGO_NO_COMPLETADO`), `reembolso` es `null`. Con motivo de stock sin pago el mensaje es "Tu pedido fue anulado por falta de stock."; con pago, "Tu pedido fue anulado por falta de stock. Se procesará el reembolso al medio de pago original."

#### Scenario: Pedido anulado por falta de stock
- **DADO** un pedido pagado (con `pago.estado` `CONFIRMADO` o `PAGADO` en el historial) que Ventas anuló con `historialEstados[estado=ANULADO].motivo = STOCK_NO_DISPONIBLE` (actor `SISTEMA_PRODUCTOS`)
- **CUANDO** el cliente consulta el detalle, el seguimiento o pregunta por el pedido en el chat
- **ENTONCES** el detalle devuelve `motivoAnulacion: STOCK_NO_DISPONIBLE`, `reembolso: "Se procesará el reembolso al medio de pago original."` y `historial[].motivo` (aplica la misma lista de códigos conocidos; un motivo desconocido se devuelve como `null`); el seguimiento devuelve ambos campos y el `mensaje` "Tu pedido fue anulado por falta de stock. Se procesará el reembolso al medio de pago original."; el chat responde "Tu pedido {pedidoId} fue anulado por falta de stock. Se procesará el reembolso al medio de pago original." y el bloque `ESTADO_PEDIDO` incluye `motivoAnulacion` y `reembolso` en `pedido` y `motivo` en el hito "Anulado"

#### Scenario: Pedido anulado por falta de stock sin pago
- **DADO** un pedido anulado con motivo `STOCK_NO_DISPONIBLE` sin evidencia de pago (ni `pago.estado` `CONFIRMADO` ni `PAGADO` en el historial)
- **CUANDO** el cliente consulta el detalle, el seguimiento o el chat
- **ENTONCES** `reembolso` es `null` y el mensaje es "Tu pedido fue anulado por falta de stock." sin promesa de reembolso

#### Scenario: Motivo de anulación desconocido
- **DADO** un pedido anulado cuyo `motivo` en el historial es un texto libre o un código fuera de la lista conocida
- **CUANDO** el cliente consulta el detalle, el seguimiento o el chat
- **ENTONCES** `motivoAnulacion` y `historial[].motivo` son `null` y el mensaje es "Tu pedido fue anulado."; no se expone texto interno de Ventas

#### Scenario: Pedido anulado nunca se muestra como confirmado
- **DADO** un pedido pagado que Ventas anuló por falta de stock, incluso cuando el pago llegó después de la anulación
- **CUANDO** se consulta en cualquier superficie
- **ENTONCES** el estado es "Anulado", no aparece como "Pago confirmado" ni se envió el correo de confirmación (SPEC-16)

### Requirement: Preguntas específicas
El sistema DEBE (SHALL) responder de forma directa las preguntas cerradas sobre el pedido usando los datos obtenidos.

*Trazabilidad: SPEC-17 · Requisito 3.*

#### Scenario: "¿Ya llegó?"
- **DADO** un pedido `ENTREGADO`
- **CUANDO** el cliente pregunta "¿ya llegó mi pedido?"
- **ENTONCES** se responde "Sí, se entregó el 23/09 a las 15:40" con "¿Tuviste algún problema? Reportar" (SPEC-19)

#### Scenario: "¿Cuándo llega?"
- **DADO** un pedido `PAGADO` con un plazo estimado de 2 días
- **CUANDO** el cliente pregunta
- **ENTONCES** se responde con la fecha estimada calculada a partir del plazo de la cotización (snapshot) o con la fecha programada de Despacho si ya existe

### Requirement: Tolerancia a fallos
El sistema DEBE (SHALL) informar la indisponibilidad de Ventas sin mostrar estados inventados.

*Trazabilidad: SPEC-17 · Requisito 4.*

#### Scenario: Ventas no disponible
- **DADO** que Ventas no responde
- **CUANDO** se consulta un pedido
- **ENTONCES** se responde "No puedo consultar tus pedidos en este momento" con "Reintentar"; si el pedido se creó en este canal, se puede mostrar su último estado conocido marcado como "último estado conocido"

#### Scenario: Despacho no disponible con el pedido despachado
- **DADO** un pedido `DESPACHADO` y Despacho caído
- **CUANDO** se consulta
- **ENTONCES** se muestra "Despachado" según Ventas, sin hitos de tránsito, y la nota "El detalle del envío no está disponible ahora"

### Requirement: Indicar si la calificación de la entrega ya se envió
El sistema DEBE (SHALL) exponer `csatEnviado` en el detalle del pedido, leído de `order_ref.csat_sent`, para que el frontend oculte el bloque de calificación de SPEC-24 cuando el cliente ya calificó el pedido. El campo DEBE (SHALL) ser `false` cuando no exista fila local o la calificación no se haya enviado.

*Trazabilidad: SPEC-24 · Requisito 2; SPEC-17 · Requisito 5.*

#### Scenario: Pedido ya calificado
- **DADO** un pedido `ENTREGADO` con `order_ref.csat_sent = true`
- **CUANDO** el cliente abre su detalle
- **ENTONCES** la respuesta incluye `csatEnviado: true` y el frontend no monta el bloque de calificación

#### Scenario: Pedido sin calificación enviada
- **DADO** un pedido `ENTREGADO` sin fila local en `order_ref` o con `csat_sent = false`
- **CUANDO** el cliente abre su detalle
- **ENTONCES** la respuesta incluye `csatEnviado: false` y el frontend muestra el bloque de calificación si el pedido sigue `ENTREGADO`

## Requisitos no funcionales

- **Seguridad:** el listado usa `GET /api/v1/pedidos/me` con el token del cliente, que Ventas filtra por `sub` sin aceptar `clienteId`; el detalle compara la pertenencia antes de mostrar y Ventas también la valida.
- **Rendimiento:** la consulta tarda p95 ≤ 800 ms sin Despacho y ≤ 1,2 s con Despacho (llamadas en paralelo cuando se conoce el estado).
- **Privacidad:** no se muestran datos del repartidor ni el motivo de un fallo de entrega.
- **Origen de los campos de anulación:** Ventas solo publica el motivo en `historialEstados[estado=ANULADO].motivo` (texto libre) y no tiene un objeto de reembolso para las anulaciones; el BFF deriva `motivoAnulacion` (solo códigos de la lista conocida) y `reembolso` (texto, solo con evidencia de pago) a partir del historial y del pago.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
