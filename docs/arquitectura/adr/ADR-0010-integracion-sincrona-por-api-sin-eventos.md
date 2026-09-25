# ADR-0010: Integración síncrona por API, sin consumo ni publicación de eventos

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; `contratos-integracion.md` §5, revisado al 22/09/2026)

## Contexto

- La matriz del curso exige que toda integración entre módulos sea por API, sin acceso a bases de datos ajenas (README §1.3.6).
- Los módulos publican contratos REST (Seguridad, Ventas, Despacho) o los tienen en propuesta (Productos, A5).
- Seguridad tiene previsto un bus RabbitMQ (exchange `seguridad.usuarios`) desde la semana 12; Ventas no publica eventos que el chatbot consuma.
- El estado del pedido lo decide Ventas y el detalle del tránsito lo aporta Despacho (`contratos-integracion.md` §4).

## Decisión

- El chatbot se integra **de forma síncrona por API REST** con los cuatro módulos.
- **No consume eventos:** los estados de pedidos, reclamos, devoluciones y despachos se consultan bajo demanda cada vez que el cliente pregunta.
- **No publica eventos:** lo que tiene que avisar a otro módulo (pago aprobado, anulación) lo hace por API, con reintentos mediante el outbox propio ([ADR-0011](ADR-0011-outbox-transaccional.md)).
- Nunca se asume disponibilidad: si un módulo no responde en su timeout, la operación se rechaza de forma controlada (`503 SERVICIO_NO_DISPONIBLE` con `modulo`) y se informa al cliente.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Suscribirse a `pedido entregado` de Ventas y a `usuario.desactivado` de Seguridad (RabbitMQ) | Registrado como mejora posible, no para esta versión (`contratos-integracion.md` §5) |
| Replicar localmente estados de otros módulos (*alternativa estándar, no documentada*) | Contradice la regla de no duplicar datos ajenos ([ADR-0013](ADR-0013-solo-referencias-locales-a-agregados-externos.md)) y exigiría sincronización |

## Consecuencias

**Positivas**
- El estado que ve el cliente siempre es el vigente en el módulo dueño.
- No hace falta infraestructura de mensajería ni manejar eventos duplicados o desordenados.

**Negativas y riesgos aceptados**
- La disponibilidad y la latencia del canal dependen de las de cada módulo; se acotan con timeouts por integración (Seguridad 3–5 s, Productos 3–4 s, Despacho 4 s, Ventas 5 s) y degradación controlada (p. ej. SPEC-18 · Req. 4 muestra el estado de Ventas si Despacho no responde).
- Sin eventos no hay avisos proactivos: el cliente se entera de un cambio solo cuando consulta (los correos posteriores están fuera de alcance, SPEC-16).

## Referencias

- `docs/contratos-integracion.md` §4 y §5 (líneas 217-245)
- `README.md` §1.3, principios 6 y 7 (líneas 123-124)
- `docs/producto/alcance.md` §7, timeouts de integración (línea 213)
- `openspec/specs/seguimiento-despacho/spec.md` Req. 4
