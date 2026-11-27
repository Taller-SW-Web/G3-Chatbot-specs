# ADR-0031: Kong OSS en modo DB-less como API Gateway delante del backend

## Estado

Aceptada

## Fecha

2026-11-26

## Contexto

- El Hito 5 exige "uso de API Management y mecanismo asincrónico entre microservicios" (`odd/tasks/hito-5.md`, entregable 4). Hasta esta fecha el canal no cuenta con un API Gateway: solo expone el prefijo `/api/v1` en FastAPI, un limitador de tasa en memoria (`src/shared/infrastructure/http/dependencies/rate_limiter.py`), exportación estática de `docs/openapi.json` y el proxy de mismo origen de Next.js ([ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md)).
- El frontend (Next.js en Vercel) envía todas las peticiones del navegador a `/api/*` y las reenvía mediante `rewrites` hacia la variable de servidor `API_PROXY_TARGET` ([ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md)). Ese mismo origen permite conservar cookies de primera parte (`chat_sid` con `SameSite=Lax`, y `chat_rt`/`chat_chg` con `SameSite=Strict`, [ADR-0008](ADR-0008-access-token-en-localstorage-y-refresh-en-cookie.md)) sin configurar CORS.
- La respuesta del asistente se transmite por **Server-Sent Events (SSE)** en la respuesta `200 text/event-stream` de `POST /api/v1/chat/conversaciones/{id}/mensajes` ([ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md)). Cualquier capa intermedia delante del backend no debe almacenar en búfer esa respuesta ni cortarla antes de que concluya el turno del LLM.
- El backend corre en Railway (plan Hobby, presupuesto de USD 5 al mes, [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md)) y despliega producción desde `development`. No se dispone de cuenta persistente en AWS ni en Azure.
- El backend ya implementa validación de JWT con JWKS dinámico de Seguridad (G7), introspección en vivo para el checkout (SPEC-14) y endpoints públicos/anónimos con `chat_sid`. Además, mantiene reglas de rate limiting por IP (`login`, `registro`, `chat`, `adjuntos`, `reacciones`, `sugerencias`) y por campo del cuerpo JSON (`email` en registro y reenvío de verificación).

## Decisión

El canal Chatbot incorpora **Kong Gateway OSS (3.x) en modo DB-less declarativo** como capa de API Management delante del backend FastAPI.

### 1. Modo de operación y configuración declarativa

- Kong corre sin base de datos (`KONG_DATABASE=off`), cargado desde un archivo declarativo **`kong.yml`** versionado en el repositorio del backend (implementación en H5-G2).
- La Admin API se mantiene desactivada en producción (`KONG_ADMIN_LISTEN=off`) para reducir superficie de ataque; los cambios de rutas o políticas se hacen exclusivamente mediante PR sobre `kong.yml`.
- Se configura `KONG_PROXY_LISTEN=0.0.0.0:${PORT:-8000}` para respetar el puerto dinámico inyectado por Railway.

### 2. Despliegue, red y plan de reversa

- **Servicio propio en Railway:** Kong se despliega como un servicio independiente dentro del mismo proyecto de Railway que el backend FastAPI.
- **Tráfico interno hacia el backend:** Kong enruta las peticiones hacia el backend a través de la red privada de Railway (`http://<servicio-backend>.railway.internal:<puerto>`), de modo que el backend pueda dejar de exponerse directamente a Internet y todo el tráfico externo pase por el gateway.
- **Integración con Vercel ([ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md)):** el proxy de Next.js (`next.config.ts`) no cambia su arquitectura de mismo origen; únicamente se actualiza `API_PROXY_TARGET` en Vercel (Production y Preview) para apuntar a la URL pública del servicio Kong. Las cookies de primera parte (`chat_sid`, `chat_rt`, `chat_chg`) y la ausencia de CORS se preservan intactas.
- **Reversa rápida:** si el gateway presenta una falla durante la demostración, basta con apuntar `API_PROXY_TARGET` de vuelta a la URL del backend (manteniendo un dominio de respaldo deshabilitable o reactivable en Railway) sin redeploy de código.

### 3. Rutas, streaming SSE y trazabilidad

- **Enrutamiento base y timeouts del *service*:** Kong declara el *service* `chatbot-backend` hacia FastAPI con `read_timeout: 90000` (90 s), `write_timeout: 60000` y `connect_timeout: 10000` para cubrir el ciclo de tool calling del LLM y los *cold starts* de los módulos externos (G5/G6). Expone el prefijo `/api/v1` y `/health` para monitoreo y pruebas de disponibilidad; cualquier ruta no declarada devuelve `404` desde el gateway.
- **Ruta dedicada para SSE ([ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md)):** en Kong, `read_timeout` pertenece al *service* (configurado arriba en 90 s; si en el futuro se requiere un timeout distinto solo para el chat, se declara un *service* dedicado para SSE), mientras que `response_buffering` se configura en la *route*. El endpoint `POST /api/v1/chat/conversaciones/{id}/mensajes` se declara con una *route* regex específica (`~/api/v1/chat/conversaciones/[^/]+/mensajes$`) con `response_buffering: false` para no almacenar en búfer el stream. El backend conserva `X-Accel-Buffering: no` en la respuesta SSE.
- **Límite de tamaño de carga:** se aplica el plugin `request-size-limiting` en el borde con tope de **6 MB** en rutas de carga de adjuntos/evidencias de SPEC-21 y SPEC-23 (el margen de 1 MB extra absorbe el *overhead* del envoltorio `multipart/form-data` respecto al límite de **5 MB** del archivo que valida el backend en `settings.attachment_max_bytes` y `MAX_EVIDENCE_BYTES`), y **1 MB** en el resto de rutas JSON para rechazar payloads abusivos antes de que alcancen a FastAPI.
- **Trazabilidad y verificación (H5-G2):** se habilita el plugin `correlation-id` (cabecera `X-Request-ID`, modo *echo* y generación si falta) y cabeceras estándar de Kong (`X-Kong-Proxy-Latency` / `Via` o cabecera explícita `X-Gateway: kong` mediante `response-transformer`). La prueba de integración de H5-G2 valida que las peticiones atraviesan el gateway inspeccionando estas cabeceras y el enrutamiento contra Kong en Docker.

### 4. Autenticación (pass-through hacia el BFF)

- Kong OSS **no valida JWT contra JWKS ni realiza introspección**. El plugin `jwt` gratuito de Kong OSS exige secretos/claves estáticas por consumidor y no soporta descubrimiento ni rotación automática por JWKS (`/.well-known/jwks.json`), funcionalidad reservada a Kong Enterprise (OIDC). Además, el canal mezcla rutas anónimas (`chat_sid`), login/registro y validación en tiempo real por introspección en checkout (SPEC-14).
- En consecuencia, Kong opera en modo **pass-through** para `Authorization: Bearer <accessToken>` y las cookies `Cookie` / `Set-Cookie` (`chat_sid`, `chat_rt`, `chat_chg`), delegando la autenticación, la validación de rol `CLIENTE` y la introspección en `JwksTokenValidator` y `CheckoutGuard` dentro de FastAPI. Kong protege el borde mediante enrutamiento explícito, rate limiting y límites de tamaño.

### 5. Rate limiting en el borde (H5-G3)

- **Defensa en profundidad sin cambiar el contrato HTTP:** las reglas de aplicación en `rate_limiter.py` **se conservan en el backend**, de modo que los límites de negocio y las respuestas `429` en formato `application/problem+json` con `code` permanecen intactos para el frontend. Kong agrega el plugin `rate-limiting` (`policy: local`, adecuado para la topología de una sola instancia en Railway; si se escalan réplicas de Kong, se migra a `policy: redis`) como **tope perimetral** por IP en el borde para frenar abuso antes de consumir recursos de FastAPI.
- **IP real del cliente detrás de Vercel:** dado que las peticiones llegan desde el proxy de Vercel ([ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md)), Kong se configura con `KONG_TRUSTED_IPS=0.0.0.0/0,::/0`, `KONG_REAL_IP_HEADER=X-Forwarded-For` y `KONG_REAL_IP_RECURSIVE=on` para que el conteo se haga sobre la IP del cliente y no sobre la IP de salida de Vercel.
- **Políticas perimetrales en Kong** (usando únicamente ventanas nativas del plugin `rate-limiting`: `second`, `minute`, `hour`, `day`, `month`, `year`):

| Ruta / alcance | Tope perimetral en Kong (`rate-limiting`) | Regla de aplicación en `rate_limiter.py` (conservada) |
|---|---|---|
| Global `/api/v1` | `minute: 120` por IP | *(nuevo tope perimetral global)* |
| `POST /api/v1/sesion/login` | `minute: 15` por IP | `LOGIN_PER_IP` (10 req/min) |
| `POST /api/v1/sesion/registro` | `minute: 5`, `hour: 30` por IP | `REGISTER_PER_IP` (5 req / 10 min, ventana exacta solo en backend) |
| `POST /api/v1/chat/conversaciones/*/mensajes` | `minute: 25` por IP | `CHAT_MESSAGES_PER_MINUTE` (20 req/min) |
| `POST /api/v1/chat/conversaciones/*/adjuntos` | `minute: 15` por IP | `ATTACHMENT_UPLOADS_PER_MINUTE` (10 req/min) |
| `PUT /api/v1/chat/mensajes/*/reaccion` | `minute: 35` por IP | `REACTIONS_PER_MINUTE` (30 req/min) |
| `POST /api/v1/chat/sugerencias` | `hour: 10` por IP | `SUGGESTIONS_PER_HOUR` (5 req/hora) |

- **Reglas exclusivas del backend:** además de las ventanas no nativas de Kong (como 10 min en `REGISTER_PER_IP`), las reglas indexadas por un campo del cuerpo JSON (`REGISTER_DEBOUNCE_PER_EMAIL` y `RESEND_PER_EMAIL`) permanecen exclusivamente en `rate_limiter.py`.
- **Formato de respuesta `429`:** en uso normal el límite de aplicación del backend responde primero con `application/problem+json` y `code`. Si un cliente supera el tope perimetral (por ejemplo el global de 120 req/min), Kong corta la petición en el borde con `429 Too Many Requests`, cabeceras `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` y `Retry-After`, y cuerpo JSON `{"message": "API rate limit exceeded"}`.

### 6. Publicación de OpenAPI (H5-G3)

- Kong OSS no incluye Developer Portal (característica de Kong Konnect/Enterprise).
- Para publicar el contrato a través del gateway, Kong expone rutas explícitas de solo lectura (`/openapi.json` y `/docs` o `/redoc`) hacia la especificación OpenAPI servida por el backend (alineada con `docs/openapi.json` y verificada por el gate de CI `export_openapi.py --check`), bajo un límite de tasa propio y sin exponer rutas internas.

### 7. Límites

- Este ADR **no** cambia las llamadas salientes del backend hacia los otros grupos (G2, G5, G6, G7), que siguen siendo REST directas ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)).
- Este ADR **no** introduce Kong Enterprise, Kong Konnect ni Redis; si el tráfico requiere varias réplicas de Kong, la migración a `policy: redis` se documentará en un ADR posterior.
- La implementación del contenedor Kong, `kong.yml`, despliegue en Railway, cambio de `API_PROXY_TARGET` en Vercel y pruebas de integración corresponden a **H5-G2** y **H5-G3**.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Kong OSS con base de datos PostgreSQL (*estándar, no documentada*) | Agrega migraciones, esquema propio y acoplamiento a la BD sin necesidad real para un conjunto acotado de rutas; DB-less versiona la configuración en Git y arranca en segundos |
| KrakenD (*no documentada*) | Orientado a agregación/BFF; es más rígido con el *pass-through* transparente de cookies y streaming SSE |
| Apache APISIX (*no documentada*) | Requiere `etcd` en su topología estándar; introduce un servicio adicional que operar en Railway dentro del plazo del Hito 5 |
| NGINX puro / Traefik / Caddy (*no documentada*) | Son *reverse proxies* o controladores de ingress, no plataformas de API Management; carecen del modelo declarativo de servicios, rutas y plugins de gestión de APIs exigido por el entregable |
| AWS API Gateway / Azure APIM | Descartados por [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md): no hay cuenta cloud persistente y añaden latencia cross-cloud hacia Railway |

## Consecuencias

**Positivas**
- Cumple el entregable 4 de API Management con un gateway estándar de industria, declarativo y reproducible en Docker (CI y local) y en Railway.
- Centraliza el enrutamiento, el rate limiting perimetral, el control de tamaño de payloads, la trazabilidad (`X-Request-ID`) y la publicación de OpenAPI en una sola puerta de entrada.
- Mantiene intacto el esquema de mismo origen y cookies de primera parte de [ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md), sin necesidad de CORS ni cambios en la lógica de sesión del frontend.
- Permite cerrar el acceso público directo al backend usando la red privada de Railway.

**Negativas y riesgos aceptados**
- Agrega un salto de red y un nuevo punto de falla delante del backend (riesgo registrado en `odd/tasks/hito-5.md`). Mitigado con healthcheck y reversa rápida en `API_PROXY_TARGET`.
- Consumo adicional de memoria en Railway Hobby (~150–250 MB en reposo para Kong OSS).
- Con `policy: local`, el rate limit no es compartido si Kong escala a más de una réplica; se acepta para el despliegue de instancia única del Hito 5.
- Con `KONG_TRUSTED_IPS=0.0.0.0/0,::/0` y `KONG_REAL_IP_HEADER=X-Forwarded-For`, un cliente que llame directamente a la URL pública de Kong puede falsificar la cabecera `X-Forwarded-For` y evadir el límite perimetral por IP. No supone una regresión respecto al estado previo (el backend ya lee el primer salto de `X-Forwarded-For` en `rate_limiter.py:41-46`); si se requiere cerrar ese vector más adelante, se restringe el tráfico entrante a Vercel o se exige una cabecera secreta compartida entre el proxy y Kong.
- Las respuestas `429` emitidas por el tope perimetral de Kong no usan `application/problem+json` con `code` (a diferencia de los límites de aplicación conservados en FastAPI).
- Kong OSS no valida JWKS ni ofrece Developer Portal gestionado; la autenticación permanece en el BFF y OpenAPI se publica por rutas dedicadas en el gateway.

## Referencias

- [ADR-0008](ADR-0008-access-token-en-localstorage-y-refresh-en-cookie.md), [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md), [ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md), [ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md), [ADR-0030](ADR-0030-rabbitmq-como-mecanismo-asincrono-del-outbox.md)
- [`odd/tasks/hito-5.md`](../../../odd/tasks/hito-5.md) (tareas H5-G1, H5-G2, H5-G3 y riesgos)
- [`docs/arquitectura/c4.md`](../c4.md) (contenedores y vista de despliegue)
- [`docs/contratos-integracion.md`](../../contratos-integracion.md) (§1 cookies y §2 API propia)
- Backend (lectura, 2026-11-26): `src/shared/infrastructure/http/dependencies/rate_limiter.py`, `docs/openapi.json`
- Frontend (lectura, 2026-11-26): `next.config.ts`
