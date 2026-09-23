# Consulta de estado y respuesta del reclamo

> Origen: SPEC-20 · Grupo: Postventa · Requiere sesión: Sí · Depende de: [`creacion-reclamo`](../creacion-reclamo/spec.md) (SPEC-19), Ventas (F6)

## Purpose

Permitir al cliente conocer el estado de sus reclamos y leer la respuesta del equipo de ventas desde el chat.

## Contexto

✅ **Resuelto (23/09).** Ventas publicó los dos endpoints que faltaban (acuerdo A10): `GET /api/v2/reclamos/{codigoSeguimiento}` (detalle y respuesta) y `GET /api/v2/reclamos?documento=&clienteId=&estado=` (listado paginado). Esta spec, antes bloqueada, ya se implementa completa contra el backend real.

Estados reales confirmados por Ventas: `REGISTRADO`, `EN_PROCESO`, `ATENDIDO`, `DERIVADO` — dos más de los que se habían asumido antes (`REGISTRADO`/`ATENDIDO` solamente).

## Alcance

Incluye:
- Listado de los reclamos del cliente (recientes primero), vía `GET /api/v2/reclamos?clienteId=`.
- Consulta por código de seguimiento, vía `GET /api/v2/reclamos/{codigoSeguimiento}`.
- Detalle: estado, fechas, pedido, motivo, `fechaLimiteSLA` y `respuestaVisibleCliente` (si existe).
- Preguntas directas ("¿ya me respondieron?").

### Fuera de alcance

- Responder al reclamo o continuar la conversación con el equipo de ventas desde el chat.
- Reabrir, apelar o cerrar un reclamo.
- Notificaciones por correo de la respuesta: son responsabilidad de Ventas.

## Requirements

### Requirement: Listar e identificar reclamos
El sistema DEBE (SHALL) listar los reclamos del cliente autenticado (`GET /api/v2/reclamos?clienteId=&pagina=&tamano=`) y permitir abrir uno por código o por selección.

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

### Requirement: Mostrar el estado y la respuesta
El sistema DEBE (SHALL) mostrar el estado del reclamo con su etiqueta, su plazo, y la respuesta textual registrada por Ventas cuando exista.

| Estado (F6, real) | Etiqueta |
|---|---|
| `REGISTRADO` | "Recibido" |
| `EN_PROCESO` | "En revisión" |
| `ATENDIDO` | "Respondido" |
| `DERIVADO` | "Derivado a otro equipo" |

*Trazabilidad: SPEC-20 · Requisito 2.*

#### Scenario: Reclamo atendido
- **DADO** un reclamo `ATENDIDO` con `respuestaVisibleCliente`
- **CUANDO** se consulta
- **ENTONCES** se muestra el estado "Respondido" y el texto de la respuesta **tal como lo registró Ventas** (sin reformular por el LLM), en un bloque diferenciado

#### Scenario: Reclamo derivado
- **DADO** un reclamo `DERIVADO`
- **CUANDO** se consulta
- **ENTONCES** se muestra "Tu reclamo fue derivado a otro equipo para su atención" — sin inventar a cuál, salvo que `respuestaVisibleCliente` ya lo indique

#### Scenario: Reclamo sin respuesta dentro del plazo
- **DADO** un reclamo `REGISTRADO` o `EN_PROCESO` con `fechaLimiteSLA` vigente
- **CUANDO** se consulta
- **ENTONCES** se muestra "En revisión · Recibirás respuesta hasta el {fechaLimiteSLA}"

### Requirement: Tolerancia a fallos
El sistema DEBE (SHALL) informar la indisponibilidad de Ventas sin mostrar información inventada.

*Trazabilidad: SPEC-20 · Requisito 3.*

#### Scenario: Ventas no disponible
- **DADO** que Ventas no responde
- **CUANDO** se consulta un reclamo
- **ENTONCES** se muestra "No puedo consultar tus reclamos ahora" con "Reintentar", y el código y la fecha de registro si existen en `reclamo_ref` local

## Requisitos no funcionales

- **Seguridad:** el listado siempre filtra por `clienteId = sub` del token, y el detalle compara la pertenencia antes de mostrar.
- **Fidelidad:** la respuesta de Ventas (`respuestaVisibleCliente`) se muestra textual; el LLM puede introducirla ("Esto respondió el equipo de ventas:"), pero no resumirla ni modificarla.
- **Rendimiento:** la consulta tarda p95 ≤ 800 ms.
- **Mapeo de errores:** Ventas responde con la clave `codigo`; se normaliza al `code` interno.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
