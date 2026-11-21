## MODIFIED Requirements

### Requirement: Reclamos duplicados
El sistema DEBE (SHALL) avisar si ya existe un reclamo abierto (no `ATENDIDO` ni `DERIVADO`) para el mismo pedido y motivo, consultando `GET /api/v2/reclamos/me?estado=` con el token del cliente antes de mostrar el formulario de uno nuevo.

*Trazabilidad: SPEC-19 · Requisito 3.*

#### Scenario: Reclamo abierto existente
- **DADO** un reclamo `REGISTRADO` o `EN_PROCESO` para PED-…891 con motivo `PRODUCTO_DEFECTUOSO`
- **CUANDO** el cliente intenta registrar otro igual
- **ENTONCES** se informa el `codigoSeguimiento` existente y su estado, con "Ver estado" (SPEC-20), y no se crea uno nuevo sin que el cliente lo confirme explícitamente ("Registrar uno nuevo de todas formas")

#### Scenario: Reclamo previo ya atendido
- **DADO** que el único reclamo previo sobre ese pedido y motivo está `ATENDIDO` o `DERIVADO`
- **CUANDO** el cliente registra uno nuevo
- **ENTONCES** se permite sin aviso (no es un duplicado, es un caso ya cerrado)
