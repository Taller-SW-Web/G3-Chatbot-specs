# Registro de decisiones de arquitectura (ADR)

Cada ADR documenta una decisión de arquitectura **ya tomada** en las specs o en los documentos transversales del repositorio, con su contexto, las alternativas y sus consecuencias. Siguen el formato de Michael Nygard ([adr.github.io](https://adr.github.io/)); para agregar uno, copia la [plantilla](plantilla.md).

Reglas:

- **Los ADR no crean decisiones.** Si una decisión cambia comportamiento, primero se cambia la spec mediante un cambio de OpenSpec (`openspec/changes/`) y después se actualiza o reemplaza el ADR.
- Lo que un ADR necesita y ningún documento decide se registra con estado **Propuesta** y se lista en sus preguntas abiertas.
- Un ADR aceptado no se reescribe: si la decisión cambia, se crea uno nuevo y el anterior pasa a **Reemplazada por ADR-NNNN**.
- Una enmienda fechada al final de un ADR aceptado (sección *Enmienda*) puede precisar su contexto sin reescribir la decisión original: ADR-0005 y ADR-0006 la usan para las imágenes de SPEC-23 (ADR-0019).
- La fecha es la que consta en los documentos para esa decisión; cuando no consta, es la fecha de registro (2026-09-24).

## Índice

| ID | Título | Estado | Fecha |
|---|---|---|---|
| [ADR-0001](ADR-0001-backend-python-fastapi.md) | Backend en Python 3.12 con FastAPI | Aceptada | 2026-09-24 |
| [ADR-0002](ADR-0002-arquitectura-hexagonal.md) | Arquitectura hexagonal en frontend y backend | Aceptada | 2026-09-24 |
| [ADR-0003](ADR-0003-aplicacion-propia-de-pantalla-completa.md) | Aplicación web propia de pantalla completa, no un widget embebido | Aceptada | 2026-09-24 |
| [ADR-0004](ADR-0004-backend-como-bff-y-nextjs-solo-frontend.md) | El backend actúa como BFF y Next.js solo como frontend | Aceptada | 2026-09-24 |
| [ADR-0005](ADR-0005-llm-con-tool-calling-detras-de-llmprovider.md) | LLM con tool calling detrás del puerto `LLMProvider`; datos comerciales solo desde herramientas | Aceptada | 2026-09-24 |
| [ADR-0006](ADR-0006-datos-sensibles-fuera-del-llm.md) | Datos sensibles fuera del LLM: formularios dedicados y redacción previa | Aceptada | 2026-09-24 |
| [ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md) | REST para acciones y WebSocket solo para el streaming, con *fallback* y modo degradado | Reemplazada por ADR-0021 | 2026-09-24 |
| [ADR-0008](ADR-0008-access-token-en-localstorage-y-refresh-en-cookie.md) | Access token en LocalStorage y refresh token en cookie `httpOnly` | Aceptada | 2026-09-24 |
| [ADR-0009](ADR-0009-token-de-servicio-con-servicetokenprovider.md) | Token de servicio `client_credentials` con `ServiceTokenProvider` desde el Hito 4 | Aceptada | 2026-09-24 |
| [ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md) | Integración síncrona por API, sin consumo ni publicación de eventos | Aceptada; modificada por ADR-0030 | 2026-09-24 |
| [ADR-0011](ADR-0011-outbox-transaccional.md) | Outbox transaccional para notificaciones a Ventas y correos | Aceptada; modificada por ADR-0030 | 2026-09-24 |
| [ADR-0012](ADR-0012-claves-de-idempotencia.md) | `Idempotency-Key` en toda operación que crea algo en otro módulo o mueve dinero | Aceptada | 2026-09-24 |
| [ADR-0013](ADR-0013-solo-referencias-locales-a-agregados-externos.md) | Solo referencias locales a agregados de otros módulos | Aceptada | 2026-09-24 |
| [ADR-0014](ADR-0014-pago-simulado-detras-de-paymentgateway.md) | Pago simulado con tarjeta detrás de `PaymentGateway` | Aceptada | 2026-09-24 |
| [ADR-0015](ADR-0015-verificacion-propia-del-celular-por-otp.md) | Verificación propia del celular por OTP con SMS simulado | Aceptada | 2026-09-23 |
| [ADR-0016](ADR-0016-direccion-en-checkoutpage-fuera-del-chat.md) | Dirección y documento solo en `CheckoutPage`, nunca por el chat ni el LLM | Aceptada | 2026-09-24 |
| [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) | Integración contra mocks con URLs base parametrizadas | Aceptada | 2026-09-24 |
| [ADR-0018](ADR-0018-agrupacion-del-nucleo-en-ocho-casos-de-uso.md) | Agrupación del núcleo del backend en 8 casos de uso | Propuesta | 2026-09-24 |
| [ADR-0019](ADR-0019-imagenes-como-entrada-del-llm.md) | Imágenes como entrada del LLM, con almacenamiento propio privado detrás de `AttachmentStorage` | Aceptada | 2026-09-26 |
| [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md) | Despliegue en Railway, Vercel y Supabase, con el worker como servicio único (provisional) | Aceptada | 2026-10-10 |
| [ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md) | Streaming de la respuesta por SSE en la respuesta del `POST`, sin WebSocket | Aceptada | 2026-10-11 |
| [ADR-0022](ADR-0022-modulos-simulados-en-proceso-para-los-entornos-desplegados.md) | Módulos simulados en proceso para los entornos desplegados | Aceptada | 2026-10-16 |
| [ADR-0023](ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md) | Proxy del frontend hacia la API (mismo origen) | Aceptada | 2026-10-16 |
| [ADR-0024](ADR-0024-calidad-y-seguridad-en-el-pipeline.md) | Pipeline de CI/CD con gate de calidad, seguridad y pruebas | Aceptada | 2026-11-25 |
| [ADR-0025](ADR-0025-monolito-modular-por-capacidad.md) | Monolito modular por capacidad en backend y frontend (homologa el ADR-0024 del backend) | Aceptada | 2026-11-21 |
| [ADR-0026](ADR-0026-almacen-de-otp-y-guard-de-celular.md) | Almacén de OTP y guard de contacto verificado en el checkout | Aceptada; actualizada 2026-11-25 (D2) | 2026-11-21 |
| [ADR-0027](ADR-0027-duplicados-de-postventa-y-forzar.md) | Duplicados de postventa con 409 y confirmación explícita (`forzar`) | Aceptada | 2026-11-21 |
| [ADR-0028](ADR-0028-adjuntos-almacenamiento-externo-privado.md) | Adjuntos del chat con almacenamiento externo privado, no disco local | Aceptada | 2026-11-21 |
| [ADR-0029](ADR-0029-modelo-de-datos-de-retroalimentacion.md) | Modelo de datos de retroalimentación: tablas propias y CSAT en Ventas | Aceptada | 2026-11-21 |
| [ADR-0030](ADR-0030-rabbitmq-como-mecanismo-asincrono-del-outbox.md) | RabbitMQ en CloudAMQP como mecanismo asíncrono del outbox, con consumidor en un proceso aparte | Aceptada | 2026-11-24 |
| [ADR-0031](ADR-0031-api-gateway-kong-oss.md) | Kong OSS en modo DB-less como API Gateway delante del backend | Aceptada | 2026-11-26 |
| [ADR-0032](ADR-0032-pipeline-ci-por-alcance.md) | Pipeline de CI por alcance, costo y evidencia | Aceptada | 2026-11-27 |

Las vistas que estas decisiones explican están en el [modelo C4](../c4.md).
