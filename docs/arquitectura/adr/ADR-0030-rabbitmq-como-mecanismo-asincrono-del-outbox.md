# ADR-0030: RabbitMQ en CloudAMQP como mecanismo asíncrono del outbox, con consumidor en un proceso aparte

## Estado

Aceptada

## Fecha

2026-11-24

## Contexto

- El Hito 5 exige "uso de API Management y mecanismo asincrónico entre microservicios" (`odd/tasks/hito-5.md`, entregable 4). Hoy el outbox ([ADR-0011](ADR-0011-outbox-transaccional.md)) es asíncrono, pero lo escribe y lo procesa **el mismo proceso**: no hay comunicación asíncrona entre procesos.
- El worker actual es un bucle `asyncio` que arranca en el *lifespan* de FastAPI cuando `OUTBOX_WORKER_ENABLED=true` (`src/shared/infrastructure/worker/outbox_loop.py`). En producción corre dentro del único servicio de Railway. Cada trabajo se toma con `FOR UPDATE SKIP LOCKED`, de uno en uno.
- La tabla `outbox` tiene cuatro tipos (`ck_outbox_type`): `NOTIFY_SALES_PAYMENT`, `REQUEST_CANCELLATION`, `SEND_EMAIL` y `SEND_FEEDBACK_EMAIL`. Sus estados son `PENDING`, `PROCESSED` y `FAILED` (`ck_outbox_status`), con `attempts` entre 0 y 5 (`ck_outbox_attempts`).
- El 2026-11-24 se verificó que producción tiene todos los módulos en modo `http` (`SALES_MODE`, `SECURITY_MODE`, `PRODUCTS_MODE`, `DISPATCH_MODE` y `MODULES_MODE`); no hay fakes desplegados. Un proceso separado del API puede, por tanto, llamar a Ventas con el token de servicio ([ADR-0009](ADR-0009-token-de-servicio-con-servicetokenprovider.md)).
- La integración con los módulos externos sigue siendo REST síncrona ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)); Seguridad (G7) tiene su propio bus RabbitMQ (`seguridad.usuarios`), que no es del chatbot.
- Límites del plan gratuito de CloudAMQP "Little Lemur": 1 M de mensajes al mes, 20 conexiones, 100 colas, 10 000 mensajes en cola, límite de conexiones nuevas por segundo y borrado de las colas inactivas durante 28 días.

## Decisión

El chatbot usa **RabbitMQ alojado en CloudAMQP** como mecanismo asíncrono entre procesos, alimentado por el outbox. Cubre **los cuatro tipos** de tarea del outbox. Este ADR no cambia las llamadas a los módulos externos, que siguen siendo REST ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)); solo cambia quién las ejecuta.

**El outbox se mantiene (relay).** Las tareas se siguen escribiendo en la misma transacción que el cambio de estado local ([ADR-0011](ADR-0011-outbox-transaccional.md)). El worker deja de llamar a Ventas y al SMTP y pasa a ser un **relay**:

- Publica cada tarea pendiente en RabbitMQ con **confirmaciones del publicador** (*publisher confirms*), mensajes persistentes y `mandatory=true` (un mensaje sin ruta se trata como fallo).
- Solo después de la confirmación del broker marca la fila como `PROCESSED` y hace commit. Si publica y el commit falla, la tarea se vuelve a publicar: la entrega es *al menos una vez* y el consumidor es idempotente.
- Si el broker no responde o rechaza la publicación, la fila **queda `PENDING`** y se reprograma `next_attempt_at` con backoff acotado (por ejemplo 5 s a 60 s). Estos fallos **no incrementan `attempts`**, para que una caída larga del broker no lleve las tareas a `FAILED` (el contador llegaría a 5 en unos 8 minutos). No se pierde ningún evento: es la demostración de H5-M4.
- Sigue viviendo donde corre hoy el worker: el *lifespan* de la API, activado por `OUTBOX_WORKER_ENABLED`. `SKIP LOCKED` permite más de una instancia sin duplicar la publicación.

**Topología (declarada por el consumidor y por el relay al arrancar, de forma idempotente).**

| Elemento | Nombre | Detalle |
|---|---|---|
| Exchange principal | `chatbot.eventos` | `topic`, durable |
| Cola de Ventas | `chatbot.ventas` | durable; enlazada con `ventas.#` |
| Cola de notificaciones | `chatbot.notificaciones` | durable; enlazada con `notificaciones.#` |
| Exchange de mensajes muertos | `chatbot.eventos.dlx` | `direct`, durable |
| Colas de mensajes muertos | `chatbot.ventas.dlq`, `chatbot.notificaciones.dlq` | durables; enlazadas al DLX con su propio nombre como clave |
| Colas de reintento (espera) | `<cola>.retry.<espera>` | una por cada espera de la política; sin consumidor; `x-message-ttl` igual a la espera y *dead-letter* a la cola de origen mediante el exchange por defecto |

Claves de enrutamiento por tipo de tarea:

| Tipo del outbox | Clave | Cola |
|---|---|---|
| `NOTIFY_SALES_PAYMENT` | `ventas.pago.notificar` | `chatbot.ventas` |
| `REQUEST_CANCELLATION` | `ventas.anulacion.solicitar` | `chatbot.ventas` |
| `SEND_EMAIL` | `notificaciones.correo.confirmacion` | `chatbot.notificaciones` |
| `SEND_FEEDBACK_EMAIL` | `notificaciones.correo.retroalimentacion` | `chatbot.notificaciones` |

Con las esperas de cada cola (más abajo) son 12 colas en total, muy por debajo del límite de 100.

**Mensaje.** Cuerpo JSON igual al `payload` de la tarea; `content_type: application/json`; `delivery_mode: 2` (persistente); propiedad `message_id` igual al **`id` de la fila del outbox** (clave de trazabilidad y de deduplicación); `correlation_id` copiado de `payload.correlation_id` cuando existe; cabeceras `type` (tipo del outbox) y `x-attempt` (intento actual, desde 1).

**Consumidor.** Es un **proceso aparte** del API: un servicio propio de Railway, o un comando de arranque distinto sobre la misma imagen del backend (por ejemplo `python -m src.infrastructure.consumer`; el nombre lo fija H5-M3). Reglas:

- Una **única conexión persistente** por proceso (CloudAMQP limita las conexiones nuevas por segundo), con reconexión automática.
- Confirmación manual (`ack`) solo después de procesar o de derivar el mensaje; `prefetch` acotado y configurable (`RABBITMQ_PREFETCH`, valor inicial 10).
- Al arrancar **declara** exchange, colas, enlaces y colas de reintento, para que se recreen si CloudAMQP borra las colas inactivas.
- Expone un *healthcheck* HTTP mínimo (puerto `PORT`) que informa de la conexión abierta y de la suscripción activa.
- **Reutiliza los manejadores existentes**: `VentasClient` con el token de servicio (`notify_payment`, `cancel_order`), `NotificationService.handle_send_email_task` y el notificador de retroalimentación. La lógica de despacho por tipo se extrae del `OutboxProcessor` para que la compartan el modo `direct` y el consumidor.
- Mantiene la idempotencia existente: `transaccionId` para el pago ([ADR-0012](ADR-0012-claves-de-idempotencia.md)) y `(order_id, resend_number)` para el correo (una notificación `SENT` se omite). Por eso un mensaje duplicado es inocuo.

**Reintentos.** Se conserva la semántica de la política actual, ahora sobre colas de espera con TTL y no sobre `next_attempt_at`:

- Cualquier error que no sea `400` ni `409` es reintentable (`5xx`, `429` y otros `4xx`, *timeout*, fallo de red), igual que en el worker actual; se republica (con confirmación) en la cola de espera correspondiente con `x-attempt + 1`; al vencer el TTL el broker lo devuelve a su cola de origen. Solo entonces se hace `ack` del original.
- Esperas para `chatbot.ventas`: 5 s, 15 s, 45 s, 2 min y 5 min (5 intentos). Esperas para `chatbot.notificaciones`: 1 min, 5 min y 15 min (3 reintentos), que son las del correo en SPEC-16; el contador de intentos del correo sigue en la tabla `notification`.
- Un error no reintentable (`400`, `409`) o el agotamiento de intentos escribe la fila del outbox como `FAILED` con `last_error` (`marcar_fallido`), publica el mensaje en el DLX (cae en la `.dlq` de su cola) y hace `ack`. Si la escritura en la base falla, no se hace `ack`: el mensaje se reentrega.
- Las tareas `FAILED` siguen requiriendo revisión manual; la `.dlq` conserva el mensaje original con `x-attempt` y el motivo para reproducirlo.
- En modo `broker` el consumidor no usa `marcar_reintento` ni `next_attempt_at` del outbox para los reintentos del consumidor.

**Cambio de esquema: ninguno.** Se eligió **no agregar un estado `PUBLISHED` ni columnas**. En modo `broker`, `PROCESSED` significa "el broker confirmó la publicación" y `processed_at` es la hora de esa confirmación. Se reutilizan `PENDING` (aún no publicada o broker caído), `PROCESSED` (publicada) y `FAILED` (el consumidor la dio por perdida). El coste aceptado es que la tabla no distingue "publicada" de "consumida"; se observa en los registros del consumidor y en las colas de CloudAMQP. Si el equipo prefiere ese estado, hace falta una migración de Alembic que modifique `ck_outbox_status` y el índice parcial, y **solo Sebastian genera las migraciones** (regla del equipo, revisión secuencial con `--rev-id` explícito); no se decide aquí.

**Interruptor de reversa.** Una variable `OUTBOX_DISPATCH_MODE` con valores `broker` y `direct`:

- `direct` es el comportamiento actual (el worker llama a Ventas y al SMTP) y es el valor por omisión, de modo que el código nuevo no cambia nada hasta que se configure `broker`.
- `broker` exige `RABBITMQ_URL`; la configuración falla al arrancar si falta.
- Si CloudAMQP falla durante la presentación, se cambia a `direct` en Railway y se reinicia el servicio. Antes se detiene el consumidor (o se vacían las colas) para que no procese en paralelo mensajes ya publicados: una anulación repetida respondería `409` y se marcaría `FAILED`.

**Coexistencia con `NOTIFICATION_SEND_INLINE=true`.** No cambia. El correo se sigue enviando en línea desde la petición y, si sale bien, la fila queda `PROCESSED` y el relay nunca la ve. El relay conserva `INLINE_EMAIL_GRACE` (30 s): un `SEND_EMAIL` más joven que ese plazo no se publica. Si el envío en línea falla, la fila sigue `PENDING` (con su `next_attempt_at` de 1, 5 o 15 min) y el relay la publica cuando vence; el consumidor la procesa y, como `(order_id, resend_number)` ya está `SENT` o sigue pendiente, no puede enviarse dos veces.

**Configuración y secretos.** `RABBITMQ_URL` (con `amqps://`) solo se define en Railway y en los secretos de GitHub, nunca en el repositorio ni en los registros. Variables nuevas: `OUTBOX_DISPATCH_MODE`, `RABBITMQ_URL`, `RABBITMQ_PREFETCH`.

**Biblioteca.** El backend es FastAPI con SQLAlchemy asíncrono y `httpx`; ya no lleva cliente de mensajería. Se adopta **`aio-pika`** (cliente `asyncio` sobre `aiormq`, con conexión robusta, confirmaciones del publicador y `prefetch`), que encaja con el bucle de eventos existente; se agrega a `requirements.txt` en H5-M2.

**Pruebas y cuota.** Las pruebas de integración y de rendimiento usan un RabbitMQ en Docker (servicio de CI o local), **nunca CloudAMQP**: una corrida de carga puede agotar la cuota mensual. Cada reintento cuenta como un mensaje más de esa cuota.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Mantener solo el outbox en proceso ([ADR-0011](ADR-0011-outbox-transaccional.md)) | El enunciado del Hito 5 pide un mecanismo asíncrono *entre* microservicios; el outbox en proceso no comunica procesos |
| Pasar por el broker solo los correos (`SEND_EMAIL`, `SEND_FEEDBACK_EMAIL`) | Lo descartó el dueño de la decisión a favor de los cuatro tipos: producción ya tiene todos los módulos en `http` y el consumidor puede llamar a Ventas |
| Publicar directamente en la transacción, sin outbox (*alternativa estándar, no documentada*) | Sin la tabla, una caída del broker perdería el evento de un pago ya aprobado; el outbox lo retiene |
| Redis Streams u otro broker (*no documentada*) | Sin ventaja para este alcance; RabbitMQ ya es el estándar del curso y de Seguridad, y CloudAMQP ofrece un plan gratuito |
| Reutilizar el bus `seguridad.usuarios` de G7 | Es de otro grupo y de otro dominio (usuarios); mezclar eventos del chatbot en él crea acoplamiento y dependencia de su operación |
| Estado `PUBLISHED` nuevo en `outbox` | Distinguiría publicada de consumida, pero exige una migración de Alembic; se difiere (ver "Cambio de esquema") |

## Consecuencias

**Positivas**
- Cumple el entregable 4: la API publica y otro proceso consume, con confirmaciones, `ack` manual, reintentos con backoff y DLQ.
- El consumidor es un proceso aparte: escala y se reinicia sin tocar la API.
- No se pierde ningún evento si el broker cae: el outbox retiene y el relay publica cuando vuelve.
- Sin cambio de esquema ni migración. El interruptor `OUTBOX_DISPATCH_MODE` permite volver al comportamiento anterior sin redeploy de código.

**Negativas y riesgos aceptados**
- Una dependencia externa más durante la demostración (CloudAMQP). Se mitiga con el outbox y con el interruptor de reversa.
- Consistencia eventual más larga: entre el pago y que Ventas lo reciba hay ahora un salto por el broker y los reintentos con espera.
- Las tareas en la DLQ y las `FAILED` requieren revisión manual. El endpoint `/admin/outbox-fallidos` que menciona [ADR-0011](ADR-0011-outbox-transaccional.md) no existe todavía ([C4](../c4.md)); hasta entonces se revisan con SQL y con la consola de CloudAMQP.
- `PROCESSED` no prueba que el consumidor terminó, solo que el broker confirmó (ver "Cambio de esquema").
- Cuota del plan: 1 M de mensajes al mes, 20 conexiones, 100 colas, 10 000 mensajes en cola y borrado de colas tras 28 días inactivas (mitigado con la declaración al arrancar). Las pruebas de carga nunca van contra CloudAMQP.
- La entrega es al menos una vez: la corrección depende de la idempotencia de `transaccionId` y de `(order_id, resend_number)`.

## Referencias

- [ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md), [ADR-0011](ADR-0011-outbox-transaccional.md), [ADR-0012](ADR-0012-claves-de-idempotencia.md), [ADR-0009](ADR-0009-token-de-servicio-con-servicetokenprovider.md), [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md)
- `odd/tasks/hito-5.md` (decisiones, tareas H5-M1 a H5-M4, riesgos)
- Backend (lectura, 2026-11-24): `src/shared/infrastructure/worker/outbox_worker.py`, `outbox_loop.py`; `src/shared/infrastructure/db/models/outbox.py`; `src/shared/infrastructure/persistence/outbox_postgres_adapter.py`; `src/modules/mod_orders/application/notification_service.py`; `src/modules/mod_checkout/module.py`; `src/shared/infrastructure/config/settings.py`
- `docs/arquitectura/c4.md` (contenedor "Worker de tareas" y vista de despliegue)
