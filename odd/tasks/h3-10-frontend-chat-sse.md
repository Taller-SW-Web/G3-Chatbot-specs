# H3-10 (frontend): chat en streaming por SSE

Documento de la parte frontend de H3-10. El plan general del hito está en [`hito-3.md`](hito-3.md); aquí solo se siguen las tareas de esta funcionalidad.

## Objetivo

Reemplazar el transporte WebSocket del frontend por la lectura del stream SSE de `POST /api/v1/chat/conversaciones/{id}/mensajes` (ADR-0021) y conectar `ChatPage`, `ChatWindow` y `MessageBubble` al backend real, sin `mockData` en el flujo del chat.

## Problema

Estado verificado el 2026-10-16 sobre `development` del frontend (con el PR #19 de H3-15 ya integrado):

- `ChatPage` es 100% mock (palabras clave, `setTimeout`, semillas) y no pasa por ningún puerto.
- `useChat` no lo importa ningún componente; conserva la lógica de WebSocket, el polling y una respuesta simulada.
- `ChatbotApiAxiosAdapter.enviarMensaje` modela la respuesta 202 anterior y `conFallback` oculta los errores reales; `cargarHistorial(desde)` nunca consulta el backend.
- `MessageBubble` ya acepta `streaming` y renderiza bloques, pero `ChatWindow` no se los pasa.
- El `rewrite` de `/api/*` (ADR-0023) ya existe tras el PR #19; falta `API_PROXY_TARGET` por entorno (H3-18).

## Restricciones

- Contrato SSE: eventos `aceptado`, `token`, `bloque` (`{bloque}`), `degradado`, `fin` y `error` (solo `code`); los errores 400 y 404 llegan antes del stream como `application/problem+json`. Fuente de verdad: `src/adapters/inbound/http/sse.py` del backend.
- Sin Route Handlers ni Server Actions hacia el backend (ADR-0004).
- Con cabecera `Authorization` el backend responde `501` hasta que H3-09 entregue el validador de JWT; el visitante anónimo usa la cookie `chat_sid`.
- Modo TDD: sin configurar. Verificaciones funcionales: `pnpm lint`, `pnpm typecheck`, `pnpm test` y `pnpm build`.
- Rama `feature/h3-10-chat-sse` del frontend, PR contra `development`. Los commits esperan confirmación del responsable.

## Tareas

| ID | Tarea | Ruta |
|---|---|---|
| H3-10F-1 | Puerto de streaming y adaptador SSE con `fetch`, con pruebas del parser | Delegada (un redactor; más de dos archivos no triviales) |
| H3-10F-2 | Retirar WebSocket y `suscribirBloques`; reemplazar `enviarMensaje`; historial real con mapper de `blocks` y roles; quitar `conFallback` de los métodos del chat | Pendiente |
| H3-10F-3 | Borrador en el store (tokens, bloques, `degradado`, `error`) y reescritura de `useChat` | Pendiente |
| H3-10F-4 | Conectar `ChatPage`, `ChatWindow` y `MessageBubble`; retirar semillas y mocks del flujo | Pendiente |
| H3-10F-5 | Verificación completa, prueba manual con el backend local y OpenAI real, y corrección de la captura visual de Playwright | Pendiente |

- [x] H3-10F-1
- [ ] H3-10F-2
- [ ] H3-10F-3
- [ ] H3-10F-4
- [ ] H3-10F-5

## Decisión de entrega

Puede ir en un solo PR o en uno por tarea. Se decide al cerrar H3-10F-3, según el volumen acumulado.

## Criterios de aceptación

- El chat muestra la respuesta del asistente token a token, con los bloques que llegan por `bloque`.
- Un turno degradado descarta los tokens acumulados y muestra el aviso; un `error` cierra el stream con un mensaje por `code`.
- Los errores 400 y 404 previos al stream se muestran sin simular una respuesta.
- `ChatPage` y los componentes del chat no importan `mockData`.

## Preguntas abiertas

- Forma exacta del historial (`blocks` dentro de cada mensaje y paginación).
- Qué hacer con `mensajes` persistido en localStorage cuando el historial viene del backend.
- Criterio de `desde` para el polling si el stream se corta.
- Cómo se crea la conversación cuando la ruta es un identificador mock (`talla-42`).

## Progreso

Estado al 2026-10-16: H3-10F-1 hecha; H3-10F-2 es la siguiente. Copia en Engram: tema `odd/h3-10-frontend-chat-sse/tasks`.

## Siguiente paso

Iniciar H3-10F-2: retirar WebSocket y `suscribirBloques`, reemplazar `enviarMensaje` por el stream, historial real y sin `conFallback` en los métodos del chat.

### Cierre de H3-10F-1 (2026-10-16)

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-10F-1 | Delegada (un redactor; cinco archivos nuevos, ninguno existente modificado) | `ChatStreamPort` (unión `ChatStreamEvento` discriminada por `tipo` y `ChatStreamError`), parser SSE incremental puro y `ChatbotSseAdapter` con `fetch`, `credentials: "include"` y `AbortSignal`. Campos tomados de `sse.py`: `aceptado{mensajeId}`, `token{texto}`, `bloque{bloque}`, `degradado{motivo}`, `fin{mensajeId}`, `error{code}`. Un frame conocido con JSON inválido o campos faltantes se convierte en `error` con `STREAM_INVALIDO`; tras un `error` se cancela la lectura; un cuerpo de error que no es JSON da `ERROR_DESCONOCIDO`. 42 pruebas pasan (15 del parser, con corte en cada byte, y 18 del adaptador). `typecheck` y `build` pasan; `lint` sin errores y con 3 advertencias previas de `react-hooks/incompatible-library` | Código leído por el orquestador; `typecheck`, `test` y `lint` repetidos | Commit pendiente de confirmación del responsable, en `feature/h3-10-chat-sse` del frontend |

Nota: el adaptador aún no está conectado al `container` ni a ningún caso de uso (H3-10F-2 y H3-10F-3). El token se lee de `useChatStore.getState().accessToken`; mientras H3-09 no entregue el validador de JWT, el backend responde `501` si llega la cabecera `Authorization`, y hoy no hay token en el store.
