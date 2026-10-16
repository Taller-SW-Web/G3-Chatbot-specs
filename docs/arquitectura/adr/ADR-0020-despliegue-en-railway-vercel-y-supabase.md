# ADR-0020: Despliegue en Railway, Vercel y Supabase, con el worker como servicio único

## Estado

Aceptada (decisión provisional y revisable)

## Fecha

2026-10-10

## Contexto

- El Hito 3 exige una demo desplegada con el frontend conectado al backend real (`odd/tasks/hito-3.md`). Hasta esta fecha ningún documento define dónde se despliegan el frontend, el backend y la base de datos ([`c4.md`](../c4.md) tenía el despliegue como pregunta abierta).
- El backend necesita un **WebSocket persistente** para el streaming de la respuesta ([ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md)) y un **worker APScheduler** (`OutboxWorker` y jobs programados, [ADR-0011](ADR-0011-outbox-transaccional.md)) que debe correr de forma continua.
- La API se diseñó sin estado en memoria para admitir varias réplicas (SPEC-05 · RNF *Escalabilidad del WebSocket*). Si el scheduler corriera dentro de cada réplica, los jobs se ejecutarían más de una vez. Era la pregunta abierta 1 de `c4.md` (topología del worker).
- La base de datos ya está en Supabase, que además aloja el bucket de adjuntos ([ADR-0019](ADR-0019-imagenes-como-entrada-del-llm.md)).
- Next.js se usa solo como frontend ([ADR-0004](ADR-0004-backend-como-bff-y-nextjs-solo-frontend.md)).
- Los módulos externos se consumen mediante mocks en el Hito 3, porque las credenciales reales llegan en el Hito 4 ([ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md)).

## Decisión

Mathias (líder y DevOps) decidió el 2026-10-10 los destinos de despliegue. **La decisión es provisional ("por ahora") y se revisa si cambian las condiciones.**

| Pieza | Destino | Detalle |
|---|---|---|
| Backend: API | Railway, plan Hobby | Servicio FastAPI (REST y WebSocket) |
| Backend: worker | Railway, plan Hobby | Servicio aparte, construido desde la **misma imagen** del backend: APScheduler con `OutboxWorker` y jobs programados |
| Frontend | Vercel | Una vista previa (*preview deployment*) por cada pull request |
| Base de datos | Supabase | PostgreSQL, ya en uso |

**Topología del worker.** El worker corre como **proceso y servicio propio, en una única instancia**, nunca dentro del proceso de la API. La API puede escalar a varias réplicas sin duplicar jobs.

**Entornos y operación**

- La rama `development` despliega a *staging* y la rama `main` a producción.
- Las migraciones de Alembic se ejecutan como paso del despliegue.
- Los secretos se configuran por entorno: LLM, Supabase y URLs base de los mocks.
- En el Hito 3 los entornos desplegados usan los mocks de los módulos ([ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md)); pasar a los servicios reales es un cambio de configuración.

**Límites.** Este ADR no diseña el pipeline de CD (tarea H3-18) ni define dónde se alojan los mocks desplegados; eso lo decide [ADR-0022](ADR-0022-modulos-simulados-en-proceso-para-los-entornos-desplegados.md).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Backend *serverless* | El backend necesita un WebSocket persistente y un único proceso worker de larga duración |
| AWS | El acceso estudiantil disponible no pudo confirmarse como una cuenta persistente: las sesiones de Learner Lab detienen los recursos a las 4 horas |
| Railway con la prueba gratuita (*trial*) | La prueba es un único crédito de USD 5 válido por 30 días y no cubre el hito; abrir cuentas adicionales para repetirla lo trata Railway como abuso de la prueba |
| Scheduler dentro del proceso de la API | Con varias réplicas, cada una ejecutaría los jobs y el `OutboxWorker` más de una vez |

## Consecuencias

**Positivas**
- El WebSocket y el worker tienen un entorno de ejecución continuo, sin los límites de una plataforma *serverless*.
- Una sola imagen del backend sirve a ambos servicios, y la API escala sin duplicar jobs.
- Cada pull request del frontend tiene una vista previa para revisarlo.
- Los entornos *staging* y producción quedan separados por rama y por secretos.

**Negativas y riesgos aceptados**
- Costo de USD 5 al mes (el plan Hobby incluye USD 5 de uso). **Aún no está definido quién aporta el medio de pago.**
- El worker de instancia única es un punto único de falla: si cae, el outbox y los jobs se detienen hasta que el servicio se reinicie.
- La decisión es provisional; si cambia, se crea un ADR nuevo y este pasa a **Reemplazada por ADR-NNNN**.
- Falta el pipeline de CD que haga efectivos los entornos y las migraciones (tarea H3-18).

## Referencias

- `odd/tasks/hito-3.md` (restricciones, tareas H3-01, H3-03, H3-04 y H3-18, y riesgo *Costo de Railway*)
- [`c4.md`](../c4.md#vista-de-despliegue) (vista de despliegue)
- [ADR-0004](ADR-0004-backend-como-bff-y-nextjs-solo-frontend.md), [ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md), [ADR-0011](ADR-0011-outbox-transaccional.md), [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md), [ADR-0019](ADR-0019-imagenes-como-entrada-del-llm.md)

## Enmienda (2026-10-11)

El [ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md) reemplazó al ADR-0007: la respuesta del asistente ya no se transmite por un WebSocket persistente, sino por SSE en la respuesta del `POST`. Donde este ADR cita el WebSocket (contexto, tabla de destinos, alternativa *serverless* y consecuencias positivas), léase ahora "respuesta HTTP en streaming de larga duración". El worker de larga duración sigue siendo un motivo válido contra el backend *serverless*, y las respuestas en streaming de larga duración son otro. La decisión de despliegue no cambia.
