# ADR-0023: Proxy del frontend hacia la API (mismo origen)

## Estado

Aceptada

## Fecha

2026-10-16

## Contexto

- El frontend (Next.js 16) se despliega en Vercel y el backend en Railway ([ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md)): son sitios distintos.
- La cookie `chat_sid` (visitante anónimo, `SameSite=Lax`) y la cookie de refresh ([ADR-0008](ADR-0008-access-token-en-localstorage-y-refresh-en-cookie.md)) no se enviarían entre sitios, y el backend no tiene CORS configurado.
- El frontend toma la URL base de la API de `NEXT_PUBLIC_API_BASE_URL` (`src/infrastructure/config/apiConfig.ts`, en el repositorio del frontend).
- La respuesta del asistente se transmite por SSE ([ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md)), por lo que el proxy no debe almacenarla en búfer.

## Decisión

Mathias (líder del equipo) decidió el 2026-10-16 que **el navegador llama a la API en el propio origen del frontend, bajo `/api/*`, y Next.js reenvía las peticiones al backend de Railway.**

- **Reenvío:** `rewrites` en `next.config.ts` hacia la URL del backend de cada entorno, configurada con una variable de entorno de servidor (por ejemplo, `API_PROXY_TARGET`). Backend de *staging*: `https://g3-chatbot-backend-staging.up.railway.app`.
- **Efecto:** mismo origen para el navegador. No hay CORS, las cookies son de primera parte y se conserva `SameSite=Lax`. Las vistas previas por pull request funcionan sin lista de orígenes permitidos.
- **Backend:** debe confiar en las cabeceras `X-Forwarded-*` (uvicorn ya corre con `--proxy-headers`).
- **Verificación temprana obligatoria (primer paso de H3-18):** comprobar que el streaming SSE ([ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md)) no se almacena en búfer al pasar por el `rewrite` de Vercel.
  - Si se almacena en búfer: reemplazar el `rewrite` de la ruta de streaming por un *route handler* de Next.js que reenvíe el flujo.
  - Segundo respaldo: dominio propio con subdominios (primera alternativa descartada, abajo).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Dominio propio con subdominios `app.` y `api.` (mismo sitio, `Lax` funciona, CORS con credenciales) | Exige comprar un dominio y configurar el DNS en ambas plataformas. Se conserva como respaldo |
| `SameSite=None; Secure` con CORS y credenciales | Safari y Firefox bloquean por defecto las cookies de terceros, por lo que el inicio de sesión y la sesión fallarían para parte de los usuarios; además crece la superficie de CSRF |

## Consecuencias

**Positivas**
- Sin CORS.
- Cookies de primera parte con `SameSite=Lax`.
- Las vistas previas por pull request funcionan sin configuración de orígenes.

**Negativas y riesgos aceptados**
- Un salto adicional por Vercel añade latencia.
- Se aplican los límites de funciones y de proxy de Vercel.
- El comportamiento del streaming a través del proxy debe verificarse.
- El backend recibe las peticiones desde Vercel: la limitación de tasa debe usar `X-Forwarded-For`.

## Referencias

- [ADR-0008](ADR-0008-access-token-en-localstorage-y-refresh-en-cookie.md) (cookie de refresh)
- [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md) (despliegue)
- [ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md) (streaming SSE)
- `odd/tasks/hito-3.md` (tarea H3-18)
- [`c4.md`](../c4.md#vista-de-despliegue) (vista de despliegue)
