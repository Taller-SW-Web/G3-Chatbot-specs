# ADR-0021: Streaming de la respuesta por Server-Sent Events en la respuesta del POST

## Estado

Aceptada. Reemplaza al [ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md).

## Fecha

2026-10-11

## Contexto

- El [ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md) fijó un WebSocket (`wss://<host>/api/v1/chat/ws?conversacionId=<id>`) para transmitir la respuesta del asistente, mientras el mensaje del cliente se enviaba por REST y respondía `202 {mensajeId}`. Su tabla de alternativas anotaba que Server-Sent Events (SSE) no se había evaluado.
- Con ese diseño, el proceso que recibe el `POST` y el proceso que mantiene el socket deben comunicarse. Con varias réplicas del backend esa comunicación exige un canal entre procesos, y la API se diseñó sin estado en memoria para admitir varias réplicas (SPEC-05 · RNF).
- El WebSocket añade un protocolo propio que operar: *handshake* con el token en un query param o subprotocolo, códigos de cierre, *heartbeat*, reconexión con backoff y reenvío de lo que falta del turno.
- El [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md) despliega la API en Railway como servicio de ejecución continua, no *serverless*. Falta verificar en el entorno desplegado que la plataforma no almacene en búfer ni corte las respuestas de streaming (tarea H3-03).

## Decisión

Mathias (líder del equipo) decidió el 2026-10-11 que **la respuesta del asistente ya no se transmite por un WebSocket: se transmite en la respuesta del `POST` que envía el mensaje, con Server-Sent Events.**

- **Endpoint:** `POST /api/v1/chat/conversaciones/{id}/mensajes` con cuerpo `{ "texto": "..." }`.
- **Errores antes del stream:** la validación y la pertenencia se resuelven antes de abrir el stream, como respuestas `application/problem+json` ordinarias (`400` de validación; `404` si la conversación no existe o no pertenece al solicitante).
- **Éxito:** respuesta `200` con `Content-Type: text/event-stream`. Los eventos, en orden:

| Evento | Payload | Cuándo |
|---|---|---|
| `aceptado` | `{ mensajeId }` | El mensaje del cliente quedó persistido |
| `token` | `{ texto }` | Cada fragmento de texto de la respuesta |
| `bloque` | `{ bloque }` | Un bloque estructurado queda listo |
| `degradado` | `{ motivo }` | El turno terminó en modo degradado; el cliente descarta los tokens recibidos antes de este evento y el texto de respaldo llega después como un `token` |
| `fin` | `{ mensajeId }` | Cierre del turno, con el id del mensaje del asistente ya persistido |
| `error` | `{ code }` | Falla inesperada a mitad del stream; el stream termina |

- **Sin WebSocket:** no existe un endpoint WebSocket. El cliente nunca abre una conexión persistente para el chat.
- **Fallback:** si el stream termina sin `fin` ni `error`, el frontend reconsulta una sola vez el historial (`GET /chat/conversaciones/{id}/mensajes`) y no hace *polling*. Esto reemplaza al antiguo comportamiento de "reconectar y reenviar lo que falta". Ver la enmienda del 2026-10-16.
- **Sin cambios respecto del ADR-0007:** REST sigue atendiendo las acciones con efecto y las lecturas, el estado de la conversación vive en PostgreSQL y el modo degradado sigue disponible. Las acciones (`accion`) y los adjuntos de imagen (`adjuntoIds`) del mismo endpoint conservan su definición vigente y **aún no están implementados en el backend**.

**Motivos**

- El proceso que recibe el mensaje es el mismo que transmite la respuesta, por lo que no hace falta un canal entre una petición REST y un socket y la API sigue sin estado entre réplicas.
- Hay menos piezas móviles: sin *handshake*, códigos de cierre, *heartbeat* ni protocolo de reconexión.
- La autenticación y las cookies funcionan igual que en el resto de la API REST; no hay token en un query string.
- Coincide con la forma en que los proveedores de LLM transmiten sus propias respuestas.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| WebSocket con un canal en memoria entre el `POST` y el socket | Solo funciona con una réplica y contradice el requisito de API sin estado |
| WebSocket con *pub/sub* entre procesos (por ejemplo, PostgreSQL `LISTEN/NOTIFY` o Redis) | Añade más infraestructura de la que el proyecto necesita |
| Enviar el mensaje por el propio WebSocket | No tiene estado compartido, pero conserva todo el costo de gestionar la conexión |
| Solo *polling*, sin streaming | No da el efecto "escribiendo en vivo". Además, tras un corte el *polling* nunca tendría éxito (ver la enmienda del 2026-10-16) |

## Consecuencias

**Positivas**
- Un solo protocolo para el chat: el envío y la respuesta viajan en la misma petición HTTP.
- La API sigue sin estado en memoria y admite varias réplicas sin canal adicional.
- Autenticación, cookies y errores `problem+json` iguales a los del resto de la API.

**Negativas y riesgos aceptados**
- Una segunda pestaña abierta en la misma conversación no ve el stream en vivo; ve el mensaje al recargar.
- El servidor no puede enviar mensajes no solicitados. Hoy nada lo necesita; si se requieren notificaciones *push*, tendrán su propia decisión.
- El frontend debe reemplazar su adaptador WebSocket por un lector de `fetch` con streaming, porque `EventSource` no admite `POST`.
- Los *proxies* no deben almacenar en búfer las respuestas HTTP de larga duración.

## Enmienda (2026-10-16): orden de los eventos en un turno degradado

El texto de respaldo de un turno degradado (modo degradado, límite de iteraciones y argumentos inválidos) ya no se entrega solo en el mensaje guardado: se emite también por el stream, de modo que el mensaje en vivo coincide con el almacenado. El orden de un turno degradado es:

`aceptado`, `token`\*, `degradado`, `token` (texto de respaldo), `bloque` (`ACCIONES_RAPIDAS`), `fin`

El cliente descarta los `token` recibidos **antes** de `degradado` y muestra el texto de respaldo que llega como `token` **después**. El resto del contrato de eventos no cambia.

## Enmienda (2026-10-16): sin polling tras un stream cortado

Si el stream SSE termina sin evento `fin` ni `error` (por ejemplo, se cae la conexión), el frontend no hace *polling*. Reconsulta el historial una sola vez (`GET /chat/conversaciones/{id}/mensajes`, arreglo simple de los últimos 50 mensajes, sin `desde`). Si ese historial ya contiene un mensaje del asistente posterior al último del cliente, reemplaza los mensajes locales por él. Si no lo contiene, o si la consulta falla, muestra el turno como incompleto con la acción "Reintentar", que reenvía el texto.

Motivo: cuando el cliente se desconecta a mitad del turno, el backend cancela el turno y no guarda la respuesta del asistente (se revierte, salvo que ya se haya ejecutado una herramienta); el mensaje del cliente sí está guardado antes de iniciar el stream. Por eso un *polling* repetido nunca tendría éxito. Reintentar envía un segundo mensaje del cliente, porque el primero ya está guardado. La consulta del historial no invoca al LLM, así que no genera costo de tokens.

## Referencias

- [ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md) (decisión reemplazada)
- [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md) (despliegue)
- `openspec/specs/motor-conversacion/spec.md` (Req. 4 y RNF *Escalabilidad del streaming*)
- `docs/contratos-integracion.md` §2.1
- [`c4.md`](../c4.md)
