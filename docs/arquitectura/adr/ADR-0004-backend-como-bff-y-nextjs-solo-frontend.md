# ADR-0004: El backend actúa como BFF y Next.js solo como frontend

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; principios 1 y 8 del README, sin fecha)

## Contexto

- El canal consume cuatro módulos con credenciales de servicio (`client_id=modulo-chatbot`) que no pueden llegar al navegador.
- La matriz del curso prohíbe acceder a bases de datos ajenas: todo va por API (README §1.3.6).
- Next.js ofrece Route Handlers, Server Actions y componentes de servidor que podrían actuar como segundo backend.
- El `accessToken` vive en LocalStorage ([ADR-0008](ADR-0008-access-token-en-localstorage-y-refresh-en-cookie.md)), así que no existe en el servidor de Next.

## Decisión

- **El backend FastAPI es el BFF (backend for frontend).** El frontend solo habla con el backend del chatbot (`/api/v1`); es el backend quien llama a Seguridad, Productos, Ventas y Despacho. Los tokens de servicio se gestionan en el backend, nunca en el navegador.
- **Next.js se usa solo como frontend** (enrutamiento con App Router y renderizado de la interfaz). No se usan Route Handlers, Server Actions ni componentes de servidor para llamar al backend ni a otros módulos. Las pantallas que dependen de la sesión, el chat o el carrito son componentes de cliente (`'use client'`). La configuración de servidor de Next se limita a cabeceras de seguridad como la `Content-Security-Policy`.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Next.js como BFF (Route Handlers o Server Actions hacia los módulos) | Descartado de forma explícita (README §1.3.8): duplicaría la lógica de integración y el token no existe en el servidor de Next |
| Frontend que llama directo a cada módulo (*alternativa estándar, no documentada*) | Expondría credenciales de servicio en el navegador y rompería el principio 1 del README |

## Consecuencias

**Positivas**
- Un solo lugar concentra las integraciones, los timeouts, la normalización de errores (`codigo` → `code` de Ventas) y la gestión de tokens.
- El frontend depende de un único contrato (`contratos-integracion.md` §2).

**Negativas y riesgos aceptados**
- Todo pasa por el backend del chatbot: si no está disponible, el canal no funciona.
- Se pierde el renderizado en servidor de las pantallas con sesión.

## Referencias

- `README.md` §1.3, principios 1, 6 y 8 (líneas 118, 123 y 125)
- `docs/contratos-integracion.md` §1 (líneas 19-27) y §2
- `openspec/config.yaml` (contexto: "Next.js (App Router, frontend only, no BFF role)")
- `docs/producto/alcance.md` §3 y §7
