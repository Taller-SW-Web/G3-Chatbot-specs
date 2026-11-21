## MODIFIED Requirements

### Requirement: Listar e identificar solicitudes
El sistema DEBE (SHALL) listar todas las solicitudes de devolución/cambio del cliente, consultando `GET /api/v2/devoluciones/me` directamente, con el token del cliente (Ventas filtra por el `sub`; el chatbot no envía `clienteId`), sin importar el canal donde se originaron.

*Trazabilidad: SPEC-22 · Requisito 1.*

#### Scenario: Pestaña "Reembolsos"
- **DADO** un cliente con 2 solicitudes, una registrada desde el chatbot y otra desde el Marketplace
- **CUANDO** abre la pestaña "Reembolsos" de `OrderHistoryPage`
- **ENTONCES** se listan ambas, con código, pedido, fecha, motivo resumido, `estadoReembolso` (cuando aplica) y badge de estado

#### Scenario: Consulta por código
- **DADO** el mensaje "¿qué pasó con mi solicitud DEV-2026-0042?"
- **CUANDO** se consulta
- **ENTONCES** se obtiene `GET /api/v2/devoluciones/DEV-2026-0042` y se muestra su estado si pertenece al cliente

#### Scenario: Código ajeno o inexistente
- **DADO** un código que no existe o que pertenece a otro cliente
- **CUANDO** se consulta
- **ENTONCES** se responde "No encontré esa solicitud en tu cuenta" en ambos casos

#### Scenario: Sin solicitudes
- **DADO** un cliente sin devoluciones registradas en ningún canal
- **CUANDO** abre la pestaña "Reembolsos"
- **ENTONCES** se muestra "Aún no tienes solicitudes de cambio o devolución"
