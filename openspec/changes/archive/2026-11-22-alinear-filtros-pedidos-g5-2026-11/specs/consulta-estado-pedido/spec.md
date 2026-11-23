## MODIFIED Requirements

### Requirement: Identificar el pedido
El sistema DEBE (SHALL) determinar a qué pedido se refiere el cliente: si tiene un solo pedido no finalizado lo muestra directamente; si tiene varios, los lista para elegir; si da un número, lo busca.

El listado PUEDE (MAY) filtrarse con los parámetros opcionales `estado`, `desde` y `hasta`. `desde` y `hasta` son fechas ISO (`YYYY-MM-DD`) que filtran por `fechaCreacion` y se reenvían sin transformación a `GET /api/v1/pedidos/me` de Ventas; `page` y `pageSize` conservan la paginación existente. Una fecha con formato inválido DEBE (SHALL) responder `400 VALIDACION` sin llamar a Ventas.

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
