# Consulta de estado del pedido

> Origen: SPEC-17 · Grupo: Seguimiento · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03), [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), Ventas (F1), [`seguimiento-despacho`](../seguimiento-despacho/spec.md) (SPEC-18)

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
- Devoluciones o cambios: no se incluyen en este canal.
- Historial de pedidos con descarga de comprobantes.

## Requirements

### Requirement: Identificar el pedido
El sistema DEBE (SHALL) determinar a qué pedido se refiere el cliente: si tiene un solo pedido no finalizado lo muestra directamente; si tiene varios, los lista para elegir; si da un número, lo busca.

*Trazabilidad: SPEC-17 · Requisito 1.*

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

### Requirement: Mostrar el estado y la línea de tiempo
El sistema DEBE (SHALL) mostrar la etiqueta del estado actual, un resumen del pedido y la línea de tiempo con los hitos del historial (fecha y hora de Lima), y enriquecerla con Despacho cuando el estado sea `DESPACHADO` o `ENTREGADO`.

*Trazabilidad: SPEC-17 · Requisito 2.*

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
- **CUANDO** se muestra
- **ENTONCES** se ve "Anulado el {fecha}" con el motivo general del historial (sin detalles internos) y, si hubo pago, "Si corresponde un reembolso, se procesará al medio de pago original"

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

## Requisitos no funcionales

- **Seguridad:** el listado siempre filtra por `clienteId = sub` del token, y el detalle compara la pertenencia antes de mostrar; Ventas también lo valida.
- **Rendimiento:** la consulta tarda p95 ≤ 800 ms sin Despacho y ≤ 1,2 s con Despacho (llamadas en paralelo cuando se conoce el estado).
- **Privacidad:** no se muestran datos del repartidor ni el motivo de un fallo de entrega.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
