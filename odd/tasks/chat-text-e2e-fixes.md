# Chat: correcciones de la prueba E2E por texto

## Objetivo

Corregir los fallos del chat detectados el 2026-11-07 al probar en producción cada capacidad escribiendo el pedido en texto (sin botones).

## Problema

1. La búsqueda con filtros ("zapatillas Nike para correr de menos de 350 soles") no encuentra productos que existen.
2. El texto del asistente muestra "[importe no verificado]" en lugar de precios válidos.
3. Consultar la disponibilidad por nombre de producto falla ("falta identificar el producto").
4. Tras quitar el último producto, la tarjeta de carrito muestra el estado anterior.
5. Al vencer el access token, el envío por SSE responde 401, no se renueva la sesión y los mensajes siguientes se pierden hasta recargar.
6. "Vacía mi carrito" pide confirmar en pantalla, pero no aparece ninguna confirmación; "quiero crear una cuenta" con sesión iniciada no muestra nada.
7. El carrito muestra el precio regular (S/ 329.90) en lugar del precio de oferta (S/ 279.90) en modo fake.
8. Las imágenes del catálogo fake apuntan a `cdn.example.com`, que no existe.

## Por qué

La demo del Hito 4 usa el chat por texto. Productos (G6) publicó un gateway público de solo lectura, pero no tiene promociones cargadas y su filtro `precioMax` responde 503; se decidió seguir con el catálogo fake en producción.

## Alcance

Fallos 1 a 8. Fuera de alcance: herramientas de chat para pedidos, devoluciones, reclamos, cupones y checkout (punto 9 de la prueba), y el cambio a Productos real.

## Restricciones

- Backend: lo implementa Claude. Frontend: lo implementa Codex (worker de Orca).
- Sin migraciones de Alembic.
- Sin commits hasta que Mathias lo confirme.
- Modo TDD: sin configurar. Se ejecutan las verificaciones funcionales de cada repositorio.
- Imágenes: 6 de zapatillas, 2 de polos y 2 de mochilas (Unsplash, licencia libre), asignadas por categoría.

## Tareas

| ID | Ruta | Repositorio | Tarea | Estado |
|---|---|---|---|---|
| B1 | Delegada (escritor Claude) | backend | Búsqueda: palabras de relleno y sinónimos (correr → running), filtro de precio en el fake, descripción de la herramienta (`q` solo palabras clave) | [x] `8ce7501` |
| B2 | Delegada (escritor Claude) | backend | Validador de importes: aceptar montos de resultados de herramientas recientes de la conversación y `offer_price` | [x] `8ce7501` |
| B3 | Delegada (escritor Claude) | backend | Producto por nombre en `ver_detalle_producto` y `consultar_disponibilidad` | [x] `8ce7501` |
| B4 | Delegada (escritor Claude) | backend | Carrito vacío emite bloque `CARRITO` sin líneas; el último bloque de carrito del turno reemplaza a los anteriores | [x] `8ce7501` |
| B5 | Delegada (escritor Claude) | backend | Confirmación de vaciar carrito con `ACCIONES_RAPIDAS` (Sí, vaciar / Cancelar); registro con sesión iniciada responde texto | [x] `8ce7501` |
| B6 | Delegada (escritor Claude) | backend | Evaluación fake de promociones aplica el descuento de oferta vigente | [x] `8ce7501` |
| B7 | Delegada (escritor Claude) | backend | Imágenes reales por categoría en los seeds fake | [x] `8ce7501` |
| F1 | Delegada (Codex) | frontend | SSE: ante 401 `TOKEN_INVALIDO`, renovar sesión y reintentar una vez; mensaje claro para 401; no perder mensajes posteriores | [x] `dd59293` |
| T1 | Directa | ambos | PR, CI, merge y promoción a `main` (requiere confirmación) | [x] backend #78/#79, frontend #48/#49 |
| F2 | Delegada (Codex) | frontend | Banner "Ofertas de la semana" del inicio aplastado: título, texto y botón cortados | [x] `6b22217` (#50) |
| B8 | Delegada (escritor Claude; depuración) | backend | Confirmar "Sí, vaciar" responde `IntegrityError` y el nombre de la excepción llega al usuario | [x] `f0033dc` (#80) |

## Criterios de aceptación

- "zapatillas Nike para correr de menos de 350 soles" devuelve la Nike Revolution 7.
- Ningún mensaje del asistente contiene "[importe no verificado]" cuando el precio proviene de una herramienta de la conversación.
- "¿hay talla 42 de la Nike Revolution 7?" consulta la disponibilidad sin pasar por un carrusel.
- Quitar el último producto muestra un carrito vacío.
- Con el access token vencido y el refresh vigente, el mensaje se envía sin error visible.
- "Vacía mi carrito" muestra botones de confirmación y solo vacía al confirmar.
- Un cliente con sesión que pide registrarse recibe un texto, no un formulario vacío.
- El carrito fake refleja el descuento de oferta.
- Las imágenes del catálogo fake cargan.

## Verificaciones aplicables

- Backend: `ruff check .` y `python -m pytest tests/unit -q`.
- Frontend: `pnpm lint`, `pnpm typecheck` y `pnpm test`.

## Progreso

- 2026-11-07: prueba E2E en producción, análisis de causas y alcance acordado con Mathias (fallos 1 a 8; imágenes 6/2/2).
- 2026-11-07: B1 a B7 hechas en `fix/chat-text-e2e` (worktree `~/orca/workspaces/G3-Chatbot-backend/chat-text-e2e`), sin commitear.
  - B2: la causa real era que los importes de los bloques nunca se autorizaban (el adaptador quita `bloques` antes del modelo); ahora se autorizan importes de datos, bloques, `texto` y de los últimos 12 mensajes.
  - B3: cubre `ver_detalle_producto` y `consultar_disponibilidad`; `agregar_al_carrito` por nombre queda fuera.
  - Verificación (escritor y orquestador): `ruff check .` sin errores; `pytest tests/unit` 1062 en verde. 21 archivos, +794/−155.
  - Flaky previo observado una vez: `test_fake_ventas.py::test_order_ids_do_not_collide_across_restarts`.
  - F1 ampliada: agregar `VACIAR_CARRITO` a `CAMBIAN_CARRITO` en `ChatPage.tsx` para refrescar el contador del carrito.
- 2026-11-07: F1 hecha por Codex en `fix/chat-sse-token-refresh` (worktree `~/orca/workspaces/G3-Chatbot-frontend/chat-sse-token-refresh`), sin commitear.
  - Ante 401 con sesión, el SSE renueva con el `refreshSession` compartido (single-flight), aplica la sesión y reintenta una vez; si falla, cierra la sesión y muestra "Tu sesión expiró. Inicia sesión de nuevo para continuar.". Anónimos sin cambios.
  - `VACIAR_CARRITO` agregado a `CAMBIAN_CARRITO`.
  - Verificación del orquestador: `pnpm lint` 0 errores (5 warnings previos); `pnpm typecheck` limpio; `pnpm test` 413 en verde con `NODE_OPTIONS=--no-experimental-webstorage`.
  - Entorno: con Node 26 local fallan 39 pruebas también en la base (`localStorage` nativo de Node choca con jsdom); el CI usa Node 22.
- 2026-11-07: commits confirmados por Mathias: backend `8ce7501` (`fix/chat-text-e2e`) y frontend `dd59293` (`fix/chat-sse-token-refresh`), sin push. RDD desactivado (global off), sin revisión nativa. Siguiente: T1 (push, PR, CI y promoción) con confirmación.
- 2026-11-07: push y PRs abiertos con confirmación: backend #78 y frontend #48 hacia `development`. CI en verde en ambos (backend `test`, frontend `check` y preview de Vercel). Pendiente: merge y promoción a `main`, con confirmación.
- 2026-11-07: merge con squash (admin, como #76/#46): backend #78 `d306a56`, frontend #48 `635f349`. Promoción con merge commit: backend #79 `c9d08e6`, frontend #49 `5db38ac`. Despliegues en producción listos.
- 2026-11-07: re-prueba en producción. Funcionan: búsqueda con filtros (Revolution 7), detalle con precio S/ 279.90 sin "[importe no verificado]", stock por nombre (pide color), carrito vacío visible, descuento de oferta (S/ 329.90 − S/ 50.00 = S/ 279.90), confirmación de vaciar visible, imágenes de Unsplash.
  - Regresión B8: el clic en "Sí, vaciar" responde `{"code":"SERVICIO_NO_DISPONIBLE","texto":"IntegrityError"}`. Depuración delegada en `fix/chat-clear-cart-confirm` (worktree `~/orca/workspaces/G3-Chatbot-backend/chat-clear-cart-confirm`).
  - Brecha conocida: "agrega la Nike Revolution 7 talla 42 color blanco" falla si el producto no está en el último carrusel (`agregar_al_carrito` no acepta `nombre`).
- 2026-11-07: B8 hecha en `fix/chat-clear-cart-confirm`, sin commitear.
  - Causa (reproducida en PostgreSQL local): `reset_checkout` enviaba `None` a dos columnas JSONB, que SQLAlchemy envía como JSON `null`; los CHECK `jsonb_typeof(...) = 'object'` lo rechazan. Afecta a todo vaciado de carrito (chat y `DELETE /carrito`), no solo al flujo nuevo.
  - Arreglo: `null()` de SQLAlchemy; el error genérico del carrito ya no muestra el nombre de la excepción.
  - Verificación (escritor y orquestador): `ruff check .` sin errores; `pytest tests/unit` 1063 en verde; nueva prueba de integración en PostgreSQL 16 en verde.
  - Pendiente fuera de alcance: la misma fuga del nombre de la excepción en `manage_catalog_use_case.py:652` y `catalog_router.py:156`.
- 2026-11-07: B8 commit `f0033dc` confirmado; PR backend #80 hacia `development` con CI en verde (incluye integración en PostgreSQL 18). Pendiente: merge y promoción con confirmación.
- 2026-11-07: B8 en producción: merge #80 `fd5ed58`, promoción #81 `819da35`, despliegue de Railway listo. Re-prueba: "Sí, vaciar" responde `OK` ("Vaciamos tu carrito"), el contador del encabezado desaparece y "qué tengo en mi carrito?" muestra CARRITO (0).
- 2026-11-07: F2 hecha por Codex en `fix/home-banner-collapsed`, sin commitear. Causa: el banner es hijo de una columna flex con scroll y se encogía (de 254 px a 56 px en 390x667); arreglo `shrink-0` en `HomePage.tsx` y prueba e2e de los 4 slides en pantalla baja. Verificación: lint 0 errores, typecheck limpio, 413 pruebas unitarias; capturas antes/después en `~/orca/workspaces/G3-Chatbot-frontend/banner-*.png`.
- 2026-11-07: F2 commit `6b22217`; merge #50 `b5e2bac`, promoción #51 `df76a63`. Verificado en producción a 390x667: el banner mide 254 px con todo su contenido.
