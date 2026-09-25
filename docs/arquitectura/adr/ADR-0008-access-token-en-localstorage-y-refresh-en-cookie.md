# ADR-0008: Access token en LocalStorage y refresh token en cookie `httpOnly`

## Estado

Aceptada (con riesgo aceptado)

## Fecha

2026-09-24 (fecha de registro; README §1.4 la registra como decisión del equipo, sin fecha)

## Contexto

- La arquitectura del equipo guarda el estado de sesión en `chatStore` (Zustand) respaldado por LocalStorage, y el interceptor de Axios adjunta el token en cada llamada REST y en el *handshake* del WebSocket.
- Antes se había propuesto que el BFF guardara el token en una cookie `httpOnly` y gestionara el refresh.
- Seguridad emite access tokens de 15 minutos y refresh tokens rotativos.
- Next.js se usa solo como frontend, sin sesión de servidor ([ADR-0004](ADR-0004-backend-como-bff-y-nextjs-solo-frontend.md)).

## Decisión

- El **`accessToken`** (15 min) se guarda en `chatStore` respaldado por **LocalStorage**; se restaura al recargar y se adjunta como `Authorization: Bearer`.
- El **`refreshToken`** nunca llega al JavaScript: el backend lo guarda en la cookie **`chat_rt`** (`httpOnly; Secure; SameSite=Strict; Path=/api/v1/sesion`) y lo rota en `POST /sesion/refresh`. El `challengeToken` del MFA va en otra cookie `httpOnly` (`chat_chg`, 5 min).
- El refresh y el logout tienen protección CSRF: cabecera `X-Requested-With` y verificación del `Origin`.
- `POST /sesion/logout` invalida el refresh en Seguridad y borra la cookie y la entrada de LocalStorage.
- Mitigaciones obligatorias del riesgo XSS:
  - se sanitiza todo contenido del LLM o de otros módulos (nunca `dangerouslySetInnerHTML` con texto no controlado);
  - `Content-Security-Policy` estricta;
  - access token de vida corta.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Access token en cookie `httpOnly` con refresh gestionado por el BFF (propuesta anterior) | Reemplazada por la decisión del equipo de usar `chatStore` + LocalStorage, que encaja con el interceptor de Axios y con el *handshake* del WebSocket (README §1.4) |
| Access y refresh token en LocalStorage (*alternativa estándar, no documentada*) | Un XSS robaría una sesión renovable indefinidamente; SPEC-03 prohíbe el refresh en LocalStorage |

## Consecuencias

**Positivas**
- El frontend adjunta el token sin depender de cookies en cada petición; la sesión se restaura al recargar.
- Un XSS roba como máximo 15 minutos de sesión, nunca el refresh.

**Negativas y riesgos aceptados**
- **Riesgo aceptado (R7):** el access token en LocalStorage es legible por cualquier script inyectado. Probabilidad media, impacto alto.
- Conviven dos mecanismos (Bearer + cookie) y el frontend debe manejar una única promesa de refresh concurrente.

## Referencias

- `README.md` §1.4 (líneas 127-135)
- `openspec/specs/inicio-sesion/spec.md` Alcance (línea 26), Req. 1 (líneas 42-49) y RNF *Seguridad*, *Mitigación XSS* y *Continuidad* (líneas 159-162)
- `openspec/specs/inicio-sesion/design.md` (cookies `chat_rt`, `chat_chg`)
- `docs/contratos-integracion.md` §1 (línea 27)
- `docs/producto/alcance.md` §9, riesgo R7
