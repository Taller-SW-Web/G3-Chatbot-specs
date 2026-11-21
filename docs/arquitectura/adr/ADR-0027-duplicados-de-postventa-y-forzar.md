# ADR-0027: Duplicados de postventa con 409 y confirmación explícita (`forzar`)

## Estado

Aceptada

## Fecha

2026-11-21 (decisión del dueño, D4 de la [auditoría](../../auditoria-specs-2026-11.md))

## Contexto

- Ventas expone `GET /api/v2/reclamos/me` y `GET /api/v2/devoluciones/me` con el token del cliente (A10/A15), y el chatbot los proxya como `GET /api/v1/reclamos` y `GET /api/v1/devoluciones`.
- `creacion-reclamo/spec.md` y `solicitud-devolucion-cambio/spec.md` ya piden avisar si existe un reclamo o una solicitud abierta antes de mostrar el formulario.
- La auditoría 2026-11 encontró que `postventa_service.py` no consulta el listado al crear: solo aplica idempotencia por `Idempotency-Key`. Un cliente puede registrar dos reclamos o dos devoluciones para el mismo pedido si cambia la clave.
- El contrato de Ventas no define una regla de duplicados; la decisión es del canal.

## Decisión

1. **La comprobación autoritativa vive en el `POST` del chatbot.** Antes de llamar a Ventas, `POST /api/v1/reclamos` y `POST /api/v1/devoluciones` consultan su listado `/me` y filtran en el backend del chatbot.
2. **Criterio de reclamo duplicado:** mismo `pedidoId` y mismo `motivo`, con estado `REGISTRADO` o `EN_PROCESO`. `ATENDIDO` y `DERIVADO` son casos cerrados y no bloquean.
3. **Criterio de devolución duplicada:** mismo `pedidoId`, mismo `motivo` y misma firma de líneas (`productoId` + `cantidad`), con estado abierto (`SOLICITADA`, `EN_EVALUACION` o `APROBADA`). `RECHAZADA` y `COMPLETADA` no bloquean. Es el criterio único de SPEC-21 (Requisito 5), del contrato (§2.7) y del backend (`BE/src/modules/mod_postventa/application/postventa_service.py:329-366`, `_duplicate_return`). *Alineación 2026-11-21: este punto decía solo "mismo `pedidoId`", lo que contradecía a la spec y al código.*
4. **Respuesta 409 con el código existente.** Sin confirmación, el backend responde `409 RECLAMO_DUPLICADO` o `409 DEVOLUCION_DUPLICADA` e incluye el identificador/código y el estado del registro existente; no se llama a Ventas.
5. **Confirmación explícita con `forzar: true`.** El cuerpo de ambos `POST` acepta `forzar` (booleano, por defecto `false`). Con `true`, el chatbot registra uno nuevo y responde `201` con su propia constancia. `forzar` no se reenvía a Ventas.
6. **La idempotencia no se sustituye.** Dos envíos con la misma `Idempotency-Key` y el mismo `forzar` devuelven la misma constancia y crean un solo registro.
7. **Fallo del listado: fail-open.** Si la consulta de duplicados falla, el registro continúa y se deja un `warning` con el `X-Correlation-Id`; el cliente no ve un error de duplicados. Supuesto explícito: si el equipo prefiere fail-closed, se responde `503 SERVICIO_NO_DISPONIBLE` y se actualiza este ADR.
8. **La UI no decide sola.** El aviso previo (`DuplicateClaimNotice` / `DuplicateReturnNotice`) es informativo; la opción "Registrar uno nuevo de todas formas" envía `forzar: true` y el backend vuelve a comprobar.

**Límites:** no se añade un endpoint de duplicados ni se cambia el contrato de Ventas. Si Ventas publica un filtro por pedido, el chatbot lo usará y eliminará el filtrado local.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Delegar la detección en Ventas | Su contrato no define duplicados y no acepta `forzar`; el canal quedaría sin control |
| Detectar solo en la UI antes de mostrar el formulario | Dos pestañas o un reintento pueden saltarse la comprobación; la comprobación autoritativa debe estar en el `POST` |
| Bloquear siempre los duplicados | Impide un segundo reclamo legítimo sobre el mismo pedido y motivo (por ejemplo, un defecto distinto) |
| Permitir siempre y avisar después | Genera duplicados y ruido operativo en Ventas |
| Usar solo la `Idempotency-Key` | Solo evita el doble clic con la misma clave; no evita dos envíos con claves distintas |

## Consecuencias

**Positivas**

- Un solo lugar decide si un registro es duplicado y el cliente confirma antes de crearlo.
- La respuesta 409 es accionable: trae el código existente para consultar su estado.
- Se mantiene la idempotencia existente y no se toca el contrato de Ventas.

**Negativas y riesgos aceptados**

- Cada creación hace una lectura adicional del listado `/me` (p95 ≤ 500 ms en la spec); si el listado es grande, Ventas debería exponer un filtro por pedido.
- El fail-open puede dejar pasar un duplicado si el listado está caído; se acepta porque bloquear el reclamo es peor para el cliente. Queda registrado y es revisable.
- La UI debe distinguir entre un 409 de duplicado y otros 409 (por ejemplo, pedido no entregado) para no mostrar el aviso equivocado.

## Referencias

- [`creacion-reclamo/spec.md`](../../../openspec/specs/creacion-reclamo/spec.md) · Requisito 3 y [`design.md`](../../../openspec/specs/creacion-reclamo/design.md)
- [`solicitud-devolucion-cambio/spec.md`](../../../openspec/specs/solicitud-devolucion-cambio/spec.md) · Requisito 5 y [`design.md`](../../../openspec/specs/solicitud-devolucion-cambio/design.md)
- [`contratos-integracion.md`](../../contratos-integracion.md) §2.6, §2.7 y §2.8
- [`auditoria-specs-2026-11.md`](../../auditoria-specs-2026-11.md) §4, D4
- [ADR-0012](ADR-0012-claves-de-idempotencia.md) — idempotencia que se conserva
