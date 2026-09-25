# Registro de decisiones de arquitectura (ADR)

Cada ADR documenta una decisión de arquitectura **ya tomada** en las specs o en los documentos transversales del repositorio, con su contexto, las alternativas y sus consecuencias. Siguen el formato de Michael Nygard ([adr.github.io](https://adr.github.io/)); para agregar uno, copia la [plantilla](plantilla.md).

Reglas:

- **Los ADR no crean decisiones.** Si una decisión cambia comportamiento, primero se cambia la spec mediante un cambio de OpenSpec (`openspec/changes/`) y después se actualiza o reemplaza el ADR.
- Lo que un ADR necesita y ningún documento decide se registra con estado **Propuesta** y se lista en sus preguntas abiertas.
- Un ADR aceptado no se reescribe: si la decisión cambia, se crea uno nuevo y el anterior pasa a **Reemplazada por ADR-NNNN**.
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
| [ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md) | REST para acciones y WebSocket solo para el streaming, con *fallback* y modo degradado | Aceptada | 2026-09-24 |
| [ADR-0008](ADR-0008-access-token-en-localstorage-y-refresh-en-cookie.md) | Access token en LocalStorage y refresh token en cookie `httpOnly` | Aceptada | 2026-09-24 |
| [ADR-0009](ADR-0009-token-de-servicio-con-servicetokenprovider.md) | Token de servicio `client_credentials` con `ServiceTokenProvider` desde el Hito 4 | Aceptada | 2026-09-24 |
| [ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md) | Integración síncrona por API, sin consumo ni publicación de eventos | Aceptada | 2026-09-24 |
| [ADR-0011](ADR-0011-outbox-transaccional.md) | Outbox transaccional para notificaciones a Ventas y correos | Aceptada | 2026-09-24 |
| [ADR-0012](ADR-0012-claves-de-idempotencia.md) | `Idempotency-Key` en toda operación que crea algo en otro módulo o mueve dinero | Aceptada | 2026-09-24 |
| [ADR-0013](ADR-0013-solo-referencias-locales-a-agregados-externos.md) | Solo referencias locales a agregados de otros módulos | Aceptada | 2026-09-24 |
| [ADR-0014](ADR-0014-pago-simulado-detras-de-paymentgateway.md) | Pago simulado con tarjeta detrás de `PaymentGateway` | Aceptada | 2026-09-24 |
| [ADR-0015](ADR-0015-verificacion-propia-del-celular-por-otp.md) | Verificación propia del celular por OTP con SMS simulado | Aceptada | 2026-09-23 |
| [ADR-0016](ADR-0016-direccion-en-checkoutpage-fuera-del-chat.md) | Dirección y documento solo en `CheckoutPage`, nunca por el chat ni el LLM | Aceptada | 2026-09-24 |
| [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) | Integración contra mocks con URLs base parametrizadas | Aceptada | 2026-09-24 |
| [ADR-0018](ADR-0018-agrupacion-del-nucleo-en-ocho-casos-de-uso.md) | Agrupación del núcleo del backend en 8 casos de uso | Propuesta | 2026-09-24 |

Las vistas que estas decisiones explican están en el [modelo C4](../c4.md).
