## MODIFIED Requirements

### Requirement: Listar e identificar reclamos
El sistema DEBE (SHALL) listar los reclamos del cliente autenticado (`GET /api/v2/reclamos/me?pagina=&tamano=` con el token del cliente; Ventas filtra por el `sub` y el chatbot no envía `clienteId`) y permitir abrir uno por código o por selección.

*Trazabilidad: SPEC-20 · Requisito 1.*

#### Scenario: Un solo reclamo abierto
- **DADO** un cliente con un reclamo `REGISTRADO`
- **CUANDO** pregunta "¿en qué quedó mi reclamo?"
- **ENTONCES** se muestra directamente `ClaimStatusCard` de ese reclamo

#### Scenario: Varios reclamos
- **DADO** varios reclamos
- **CUANDO** el cliente pregunta por "mis reclamos"
- **ENTONCES** se muestra `ClaimList` con código, fecha, pedido, motivo y estado, para elegir

#### Scenario: Código ajeno o inexistente
- **DADO** un código que no pertenece al cliente o que no existe
- **CUANDO** se consulta
- **ENTONCES** se responde "No encontré ese reclamo en tu cuenta" en ambos casos (Ventas responde `404` para ambos, sin distinguir)

#### Scenario: Sin reclamos
- **DADO** un cliente sin reclamos
- **CUANDO** consulta
- **ENTONCES** se responde "No tienes reclamos registrados" y se ofrece "Reportar un problema con un pedido"
