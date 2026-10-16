## MODIFIED Requirements

### Requirement: Solicitud duplicada sobre el mismo pedido
El sistema DEBE (SHALL) avisar si ya existe una solicitud abierta para el mismo pedido, consultando `GET /api/v2/devoluciones/me?estado=` con el token del cliente antes de mostrar el formulario de una nueva y filtrando por `pedidoId` en el backend del chatbot (el contrato publicado de Ventas no ofrece ese filtro; si Ventas lo agrega, se usa directamente).

*Trazabilidad: SPEC-21 · Requisito 5.*

#### Scenario: Solicitud abierta existente
- **DADO** una solicitud `EN_EVALUACION` para un pedido
- **CUANDO** el cliente intenta solicitar de nuevo sobre el mismo pedido
- **ENTONCES** se informa el código existente (`DEV-2026-0042`) y su estado, con "Ver estado" (SPEC-22), y no se crea una nueva sin que el cliente lo confirme explícitamente

#### Scenario: Solicitud previa ya resuelta
- **DADO** que la única solicitud previa sobre ese pedido está `RECHAZADA` o `COMPLETADA`
- **CUANDO** el cliente inicia una nueva
- **ENTONCES** se permite sin aviso (no es un duplicado, es una solicitud nueva sobre un caso ya cerrado)
