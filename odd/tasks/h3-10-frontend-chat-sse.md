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
- [x] H3-10F-2
- [x] H3-10F-3
- [x] H3-10F-4
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

Estado al 2026-10-16: H3-10F-1 a H3-10F-4 hechas; H3-10F-5 es la siguiente y única pendiente. Copia en Engram: tema `odd/h3-10-frontend-chat-sse/tasks`.

## Siguiente paso

Iniciar H3-10F-5: probar el chat de punta a punta en un navegador contra el backend local con OpenAI real (la interfaz aún no se ha ejecutado), corregir los E2E de Playwright que rompe H3-10F-4, reescribir `docs/arquitectura-frontend.md` para SSE y decidir qué hacer con las rutas mock que quedan (ver pendientes de H3-10F-4).

### Cierre de H3-10F-1 (2026-10-16)

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-10F-1 | Delegada (un redactor; cinco archivos nuevos, ninguno existente modificado) | `ChatStreamPort` (unión `ChatStreamEvento` discriminada por `tipo` y `ChatStreamError`), parser SSE incremental puro y `ChatbotSseAdapter` con `fetch`, `credentials: "include"` y `AbortSignal`. Campos tomados de `sse.py`: `aceptado{mensajeId}`, `token{texto}`, `bloque{bloque}`, `degradado{motivo}`, `fin{mensajeId}`, `error{code}`. Un frame conocido con JSON inválido o campos faltantes se convierte en `error` con `STREAM_INVALIDO`; tras un `error` se cancela la lectura; un cuerpo de error que no es JSON da `ERROR_DESCONOCIDO`. 42 pruebas pasan (15 del parser, con corte en cada byte, y 18 del adaptador). `typecheck` y `build` pasan; `lint` sin errores y con 3 advertencias previas de `react-hooks/incompatible-library` | Código leído por el orquestador; `typecheck`, `test` y `lint` repetidos | Commit pendiente de confirmación del responsable, en `feature/h3-10-chat-sse` del frontend |

Nota: el adaptador aún no está conectado al `container` ni a ningún caso de uso (H3-10F-2 y H3-10F-3). El token se lee de `useChatStore.getState().accessToken`; mientras H3-09 no entregue el validador de JWT, el backend responde `501` si llega la cabecera `Authorization`, y hoy no hay token en el store.

### Cierre de H3-10F-2 (2026-10-16)

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-10F-2 | Delegada (un redactor; más de dos archivos no triviales) | Verificado en el backend: el historial es un arreglo simple de los últimos 50 mensajes, `rol` ya llega como `user` o `bot` y `bloques` llega como `{"blocks": [...]}` o `null`. Se eliminan `WebSocketPort`, `ChatbotWebSocketAdapter`, `useChat` (sin importadores), `suscribirBloques`, `enviarMensaje`, `wsReintentos` y `MOCK_MENSAJES`. `container.ws` pasa a `container.stream`. `cargarHistorial` es un `GET` real sin fallback, con `mapearHistorial` (desenvuelve `blocks`, lanza ante un mensaje mal formado) y sin parámetro `desde`. `enviarMensajeUseCase` usa el puerto de streaming y valida de 1 a 1000 caracteres. 59 pruebas pasan (17 nuevas); `typecheck`, `lint` (0 errores, 3 advertencias previas) y `build` pasan | Código central leído por el orquestador; `typecheck`, `test`, `lint` y `build` repetidos | Commit pendiente de confirmación del responsable, en `feature/h3-10-chat-sse` del frontend |

Pendientes que deja H3-10F-2:

- `docs/arquitectura-frontend.md` sigue describiendo WebSocket, polling con `?desde=`, `WebSocketPort`, `ChatbotWebSocketAdapter` y `useChat` (líneas 15-16, 31-36, 51, 84, 102 y 113-118). Se reescribe para SSE en una pasada de documentación al cerrar H3-10F-5.
- `pollingMs` en `apiConfig.ts` quedó sin consumidor; decidir en H3-10F-3 si el polling de respaldo se mantiene o se elimina.
- `ChatPage.tsx` línea 47 conserva un comentario sobre `useChat` que quedará obsoleto; se corrige en H3-10F-4.
- Resuelto: la forma del historial (pregunta abierta de este documento).

### Cierre de H3-10F-3 (2026-10-16)

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-10F-3 | Delegada (un redactor; más de dos archivos no triviales) | Decisión de Mathias: si el stream termina sin `fin` ni `error`, una sola consulta del historial y, si no aparece la respuesta, aviso de turno incompleto con reintento, sin polling. Verificado en el backend: pedir el historial no llama al LLM, y ante una desconexión del cliente el turno se cancela y no se guarda la respuesta (`interpret_and_respond_use_case.py`, línea 158). El estado del turno es local al hook (reductor puro `turnoChat.ts`), la orquestación está en `ejecutarTurnoUseCase` y `useChat` es solo pegamento de React. `chatStore` deja de persistir mensajes: se quitan `mensajes`, `escribiendo` y sus acciones (sin consumidores), con `version: 1` y una migración que descarta lo antiguo, y `partialize` conserva los demás campos persistidos. Se elimina `pollingMs`. 81 pruebas pasan (22 nuevas); `typecheck`, `lint` (0 errores, 3 advertencias previas) y `build` pasan | Reductor, caso de uso, hook y diff del store leídos por el orquestador; `typecheck`, `test`, `lint` y `build` repetidos | Commit pendiente de confirmación del responsable, en `feature/h3-10-chat-sse` del frontend |

Pendientes que deja H3-10F-3:

- **Turno degradado:** el backend guarda el texto del turno degradado (`DEGRADED_TEXT`) pero el stream solo envía `degradado`, el bloque de acciones rápidas y `fin`. En vivo, el mensaje consolidado queda con texto vacío y el bloque; al recargar el historial aparece con su texto. Opciones: que el backend emita ese texto como `token` después de `degradado` (compatible con el contrato, porque el cliente solo descarta los tokens anteriores), o que el frontend use un texto de respaldo. Decidir antes de H3-10F-4.
- El `reductor` no conserva en el mensaje consolidado la marca de que el turno fue degradado; si la interfaz necesita el aviso después de `fin`, hay que añadirla.
- `useChat` no tiene prueba propia: no contiene lógica y la cubren el reductor y el caso de uso.

### Cierre de H3-10F-4 (2026-10-16)

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-10F-4 | Delegada (un redactor; más de dos archivos no triviales) | Decisión de Mathias sobre el turno degradado: el backend emite el texto de respaldo como `token` después de `degradado` (commit `69f184a` directo en `development` del backend; 496 pruebas pasan sobre PostgreSQL 18). `HomePage` crea una conversación real y deja el primer mensaje en un campo transitorio de `chatStore` (no persistido); `ChatPage` lo envía una sola vez tras cargar el historial. `ChatPage` usa `useChat` sin semillas ni palabras clave; `ChatWindow` y `MessageBubble` muestran mensajes reales, el borrador en streaming, el indicador de escritura y avisos de error o turno incompleto con "Reintentar"; un fallo previo al stream devuelve el texto al campo. Las acciones rápidas envían su etiqueta como texto, porque `accion` responde 501. La lógica de presentación está en funciones puras (`chatPresentacion.ts`). `DETALLE_PRODUCTO` y `RESUMEN_CHECKOUT` se muestran; `CARRUSEL_PRODUCTOS` y `CONFIRMACION_PEDIDO` se muestran inertes; `CARRITO` y los demás tipos sin forma definida no se renderizan. 108 pruebas pasan (27 nuevas); `typecheck`, `lint` (0 errores, 3 advertencias previas) y `build` pasan | Código de `ChatPage`, `HomePage`, `useChat` y `chatStore` leído por el orquestador; `typecheck`, `test`, `lint` y `build` repetidos. La interfaz NO se ha ejecutado en un navegador | Commit pendiente de confirmación del responsable, en `feature/h3-10-chat-sse` del frontend |

Pendientes que deja H3-10F-4:

- La interfaz del chat aún no se ha probado en un navegador; es el primer paso de H3-10F-5.
- Rutas mock que quedan y ahora caen en el estado de error del historial: `OrderHistoryPage` y `SeguimientoPage` (`/chat/consulta`) y `DevolucionPage` (`/chat/devolucion-compra`). Pertenecen a pedidos y devoluciones (Hitos 4 a 6); decidir si se desactivan los botones o se dejan hasta entonces. Además, `mensajePendiente` ya no tiene consumidor.
- Playwright: `tests/e2e/visual.spec.ts` navega a `/chat/talla-42`, que ahora muestra el error de historial, así que la captura `visual-chat.png` deja de ser válida. `home.spec.ts` no se ve afectado.
- La grilla de productos de Home sigue con `PRODUCTOS_MOCK` y el botón de agregar solo actualiza la insignia del carrito (pertenece a la búsqueda y el carrito reales).
- El botón de foto queda deshabilitado en Home y en el chat ("Próximamente"); `AttachmentPopup` no se usa, pero el archivo se conserva.
- Los bloques `CARRITO`, `SELECTOR_VARIANTE`, `FORMULARIO`, `LISTA_*`, `ESTADO_*` y `CONSTANCIA_*` no se renderizan; los cubren las tareas de herramientas, carrito y registro.
- Cambio mayor al heurístico de 400 líneas (unas 450 añadidas y 480 retiradas) porque `ChatPage` se reescribió por completo.
