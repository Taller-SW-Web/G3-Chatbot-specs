# Hito 3: Demo 1

## Objetivo

Entregar la primera demo funcional y desplegada: un cliente se registra, inicia sesión, conversa con el asistente, busca productos y arma un carrito, con el frontend conectado al backend real.

## Problema

Estado verificado el 2026-10-10 contra `origin/development` de ambos repositorios.

| Área | Estado inicial |
|---|---|
| Backend | Solo está implementada la persistencia (modelos, adapters y migración `0001`). Dominio, puertos, casos de uso, HTTP, WebSocket, clientes httpx y NLP son archivos vacíos |
| Frontend | Interfaz construida con datos mock (`mockData.ts`); ya existen los puertos `ChatbotApiPort` y `WebSocketPort`, sus adapters y seis casos de uso, sin conexión al backend |
| CI backend | Ejecuta únicamente `pytest tests/unit`; sin lint, sin pruebas contra PostgreSQL y sin verificación de migraciones |
| CI frontend | Pasa en verde sin ejecutar nada: el workflow exige `pnpm-lock.yaml` y el repositorio no lo tiene |
| Despliegue | No existe en ningún repositorio; `docs/arquitectura/c4.md` lo lista como pregunta abierta, junto con la topología del worker |
| Ramas | `main` y `development` sin protección en ambos repositorios; dos PR del Hito 2 entraron sin aprobación |
| PR abiertos | Backend #35 (`feature/h3-motor-herramientas`, +1111 líneas, CI en verde, sin revisión) |

## Alcance

Según `docs/producto/epicas.md`:

- SPEC-01 a 03: registro, verificación de correo, inicio de sesión y gestión de sesión.
- SPEC-05 (núcleo): conversaciones múltiples, interpretación de intención, tool calling y streaming.
- SPEC-06 y 09: búsqueda y filtrado; carrusel, tarjetas y detalle de producto.
- SPEC-10 y 11: carrito y validación de stock.
- Pista de DevOps: CI, CD y despliegue de ambos repositorios.

Fuera de alcance: SPEC-04, 07, 08 y 23 (Hito 4), SPEC-24 (Hito 5–6, asignada a Nikol el 2026-10-14), checkout y pedido (Hito 4), seguimiento y postventa (Hito 5–6), e integración con las APIs reales de los otros módulos (credenciales desde el Hito 4; se usan mocks según ADR-0017).

## Restricciones

- Destinos de despliegue (decisión provisional del 2026-10-10, pendiente de ADR): backend en Railway plan Hobby, con la API y el worker como servicios separados; frontend en Vercel; base de datos en Supabase.
- Cada integrante trabaja en rama propia y abre PR contra `development`. Todo PR requiere CI en verde y una aprobación.
- Solo Sebastian genera migraciones de Alembic, con revisión secuencial (`0002`, `0003`, ...) y `--rev-id` explícito.
- Identificadores de base de datos en inglés; etiquetas de interfaz en español, resueltas por el frontend.
- El código del backend se escribe en inglés (decisión del 2026-10-11, alineada con el README): archivos, módulos, clases, funciones y variables. Los archivos vacíos del esqueleto con nombre en español se renombran antes de implementarlos. Queda pendiente definir cuándo se alinean los nombres en español ya existentes (métodos de los adapters de persistencia y el PR #35).
- Next.js se usa solo como frontend (ADR-0004): sin Route Handlers ni Server Actions hacia el backend.
- Precios, stock y descuentos provienen siempre de las herramientas, nunca del texto del LLM.
- Gestor de paquetes del frontend: pnpm (decisión del 2026-10-10, tarea H3-04). Cuando el cambio llegue a `development`, cada integrante debe actualizar su entorno local: instalar pnpm, eliminar `node_modules` y cualquier `package-lock.json` local, ejecutar `pnpm install` y no volver a usar `npm install`.
- Modo TDD: sin configurar. Se ejecutan las verificaciones funcionales de cada repositorio (`python -m pytest` en backend; `lint`, `typecheck`, `test` y `build` en frontend).

## Tareas

Ruta de cada tarea: delegada al responsable indicado, en su propia rama.

### Fase 0: desbloqueo

| ID | Responsable | Repositorio | Tarea |
|---|---|---|---|
| H3-00 | Nikol | specs | Cerrar H2-09 y actualizar `hito-2.md` con lo ya mergeado |
| H3-01 | Mathias | specs | ADR de despliegue y vista de despliegue en `c4.md`; resuelve la topología del worker |
| H3-02 | Mathias | backend, frontend | Protección de `main` y `development`: CI obligatorio y una aprobación |
| H3-03 | Mathias | backend | Dockerfile, endpoint de salud y esqueleto desplegado en Railway |
| H3-04 | Mathias | frontend | Confirmar el gestor de paquetes, versionar el lockfile para que el CI ejecute sus pasos y desplegar el frontend actual en Vercel con vista previa por PR |
| H3-05 | Sebastian | backend, specs | Puertos, contratos (herramienta → caso de uso, bloques, eventos WS), cliente httpx base y configuración por entorno |
| H3-06 | Sonny | backend | Mock de Productos (ADR-0017) |
| H3-07 | Sebastian | backend | Mock de Seguridad (ADR-0017) |
| H3-08 | Sebastian (revisa), Alonso (corrige) | backend | Revisar y mergear el PR #35 |

- [x] H3-00
- [x] H3-01
- [x] H3-02
- [x] H3-03
- [x] H3-04
- [x] H3-05
- [x] H3-06
- [x] H3-07
- [x] H3-08

### Fase 1: en paralelo

Reparto por funcionalidad vertical (ajuste del 2026-10-15, aprobado por Mathias): se pidió que cada integrante entregue una funcionalidad completa, backend y frontend. Las pantallas y componentes del design system ya existen en el frontend con datos mock (verificado el 2026-10-15 en `origin/development`: tokens en `globals.css`, clases `.wf-btn`, `.wf-input`, `.wf-chip` y `.wf-card`, formularios de auth, bloques de chat, `ProductCard`, `CartWidget` y páginas), por lo que la parte frontend de cada funcionalidad consiste en retirar `mockData` de su flujo y conectarla al backend real.

| ID | Responsable | Funcionalidad | Backend | Frontend |
|---|---|---|---|---|
| H3-09 | Sebastian | Registro y verificación de correo (SPEC-01 y 02) | Casos de uso y endpoints de registro y verificación | `RegistroForm` y pantalla de verificación conectados al backend |
| H3-10 | Mathias | Chat en streaming (SPEC-05 núcleo) | Bucle del agente (máximo 5 iteraciones), system prompt, `LLMProvider` y streaming por SSE (ADR-0021) | Lector de streaming SSE que reemplaza a `ChatbotWebSocketAdapter`; `ChatPage`, `ChatWindow` y `MessageBubble` conectados |
| H3-11 | Alonso | Herramientas, acciones rápidas y modo degradado | Declaración de las herramientas del hito, `ActionDispatcher`, `OutputValidator` y modo degradado | Render de los bloques `ACCIONES_RAPIDAS` y `BloqueError`, y aviso de modo degradado |
| H3-12 | Sonny | Búsqueda y catálogo (SPEC-06 y 09) | Herramientas de búsqueda, filtrado y detalle de producto | `CarruselProductos`, `ProductCard` y `DetalleProducto` con datos de las herramientas |
| H3-13 | David | Carrito y stock (SPEC-10 y 11) | Carrito y validación de stock | `CartWidget`, `BloqueCarrito` y `CartPage` conectados |
| H3-14 | Diego | Inicio y cierre de sesión (SPEC-03) | Inicio de sesión, MFA, refresh y cierre de sesión | `LoginForm`, `OtpMfaForm` y `AuthModal` conectados; almacenamiento del token, refresh y mitigaciones de XSS exigidas por SPEC-01 a 03 |
| H3-15 | Nikol | Gestión de conversaciones (SPEC-05 Req. 1) | Resaltado de la coincidencia en la búsqueda (pendiente de H3-10; propuesta: `ts_headline`) | `Sidebar` conectado: listar, crear y buscar conversaciones |

Tareas transversales:

| ID | Responsable | Repositorio | Tarea |
|---|---|---|---|
| H3-16 | Nikol | specs, frontend | Casos de prueba a partir de los escenarios de las specs del hito y E2E de humo con Playwright |
| H3-17 | Mathias | backend | CI: lint, pruebas de integración con PostgreSQL como servicio y verificación de `alembic upgrade head` |
| H3-18 | Mathias | backend, frontend | CD: `development` → staging y `main` → producción, con las migraciones como paso del despliegue; secretos por entorno (LLM, Supabase, URLs base de los mocks) |

Diego mantiene además el cuidado del design system (`docs/design-system.md`). Revisión cruzada para quienes escriben backend por primera vez: Sebastian revisa los PR de H3-14 y Mathias los de H3-15.

- [ ] H3-09
- [ ] H3-10
- [ ] H3-11
- [ ] H3-12
- [ ] H3-13
- [ ] H3-14
- [ ] H3-15
- [ ] H3-16
- [ ] H3-17
- [ ] H3-18

### Fase 2: integración y demo

| ID | Responsable | Repositorio | Tarea |
|---|---|---|---|
| H3-19 | Todos, coordina Nikol | backend, frontend | E2E sobre staging y corrección de fallas |
| H3-20 | Mathias | backend, frontend | Promoción a producción y guion de la demo |

- [ ] H3-19
- [ ] H3-20

## Criterios de aceptación

- En el entorno desplegado, un cliente se registra, verifica su correo, inicia sesión, conversa, busca productos y arma un carrito.
- Las respuestas llegan en streaming por SSE en la respuesta del `POST` (ADR-0021) y los datos comerciales de las tarjetas provienen de las herramientas.
- El frontend no depende de `mockData.ts` en los flujos del hito.
- Todo PR entra con CI en verde y una aprobación; el CI del frontend ejecuta de verdad `lint`, `typecheck`, `test` y `build`.
- Un merge a `main` despliega backend y frontend sin pasos manuales, con las migraciones aplicadas.
- El despliegue está documentado en un ADR y en `docs/arquitectura/c4.md`.

## Verificaciones aplicables

- Backend: `python -m pytest tests/unit`, pruebas de integración contra PostgreSQL y `alembic upgrade head` seguido de `alembic downgrade base`.
- Frontend: `lint`, `typecheck`, `test` y `build`.
- E2E: Playwright sobre staging.

## Entrega

Estrategia: `ask-on-risk`. El hito supera con holgura las 400 líneas modificadas; se entrega como PR independientes por tarea contra `development`, sin encadenar.

## Riesgos

- **Carga de Mathias:** concentra el bucle del agente y siete tareas de DevOps. Es el cuello de botella del hito; conviene reasignar H3-17 o posponerla hasta cerrar H3-10.
- **Carga de Sebastian en la Fase 0:** contratos, mock de Seguridad y revisión del PR #35. Si se atrasa, se detiene la Fase 1.
- **PR #35 sin revisar:** resuelto el 2026-10-14 (mergeado); quedan el acople con H3-10 y la prueba con el modelo real.
- **Fecha de la demo sin definir:** el plan no tiene fechas; hay que fijarla para ordenar la Fase 2.
- **Costo de Railway:** USD 5 al mes; falta definir quién aporta el medio de pago.
- **Backend nuevo para Diego y Nikol:** con el reparto vertical escriben backend por primera vez (H3-14 y H3-15). Se mitiga con revisión cruzada de Sebastian y Mathias.
- **Conflictos en archivos compartidos del frontend:** varias funcionalidades tocan `ChatbotApiAxiosAdapter.ts`, `ChatbotApiPort.ts`, `container.ts` y `mockData.ts`. Conviene PR pequeños y que cada uno retire solo el mock de su flujo.
- **Dependencia del chat:** H3-11, H3-12 y H3-13 muestran sus bloques dentro del chat; hasta que H3-10 conecte el streaming en el frontend, se prueban con el mock.

## Progreso

Estado al 2026-10-14: Fase 0 en curso (H3-01, H3-05, H3-06 y H3-08 cerradas; H3-04 a medias). Documento creado y versionado en `main`. Copia en Engram: tema `odd/hito-3/tasks`.

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-01 | Delegada (un redactor; ADR y `c4.md` son dos archivos no triviales) | ADR-0020 creado; vista de despliegue en `c4.md`; preguntas abiertas de topología del worker y despliegue cerradas. Los seis diagramas Mermaid de `c4.md` renderizan con `mermaid-cli`; enlaces a ADR-0020 verificados | RDD desactivado; nivel evaluado: pasivo | `11484dc` en `main` |
| H3-04 (en curso) | Delegada (un redactor para la migración); corrección de lint en línea | Migración a pnpm 10.34.6 y CI sin el paso que omitía las verificaciones; error de lint previo en `ChatPage.tsx` corregido. `lint`, `typecheck`, `test` y `build` pasan en local. Falta: push, CI en GitHub y despliegue en Vercel con vista previa por PR | RDD desactivado | `b5e0469` y `1794b10` en `development` del frontend, sin push |
| H3-08 (en curso) | En línea (revisión) | PR #35 revisado por Mathias el 2026-10-11: cambios solicitados. Bloqueante: `sensitive_data_filter.py` deja pasar contraseñas y tarjetas. Falta la corrección de Alonso y una nueva revisión | No aplica | No aplica |
| H3-06 (en revisión) | Delegada (un revisor, solo lectura) | PR #39 de Sonny revisado por Mathias el 2026-10-12: cambios solicitados. Bloqueantes: las respuestas 4xx de los módulos llegan al llamador como datos, la prueba del 404 no ejercita el cliente y los archivos conservan el nombre en español. La captura incompleta de errores de transporte está en `BaseModuleClient` (H3-05, Sebastian). Falta la corrección de Sonny y una nueva revisión | No aplica | No aplica |
| H3-10 (en curso) | Delegada (un mapeador y un redactor; más de cuatro archivos) | Primer tramo: esqueleto de FastAPI, `GET /health` y conversaciones (crear, listar, historial). 128 pruebas unitarias y 16 de integración pasan sobre PostgreSQL 18; flujo verificado por HTTP contra una base migrada. Falta: búsqueda, envío de mensajes, bucle del agente, `LLMProvider` y streaming de la respuesta por SSE (ADR-0021) | RDD desactivado | `ecab47c` en `feature/h3-10-conversations` del backend, sin push |
| H3-10 (en curso) | Delegada (un redactor; más de dos archivos no triviales) | Segundo tramo: puerto `LLMProvider` y adaptador de OpenAI (Chat Completions) con streaming y llamadas a herramientas, configurado por variables de entorno. 147 pruebas unitarias pasan con HTTP simulado; no se probó contra el modelo real porque aún no hay clave de API. Falta: búsqueda, envío de mensajes, bucle del agente y WebSocket | RDD desactivado; riesgo medio | `43ccbd1` en `feature/h3-10-conversations` del backend, sin push |
| H3-10 (en curso) | Delegada (un redactor; más de dos archivos no triviales) | Tercer tramo: caso de uso `InterpretAndRespondUseCase` (envío de mensaje, bucle LLM y herramientas con máximo 5 iteraciones, título, respuesta degradada), system prompt, puerto `ToolExecutorPort` con implementación vacía temporal y eventos para el WebSocket. 173 pruebas unitarias y 23 de integración pasan sobre PostgreSQL 18. Falta: transporte (REST y WebSocket), búsqueda y acople con el registro de herramientas del PR #35 | RDD desactivado; revisión del orquestador con dos correcciones aplicadas | `87db68c` en `feature/h3-10-conversations` del backend, sin push |
| H3-10 (en curso) | Delegada (un redactor en backend y un redactor de documentación en specs) | Cuarto tramo: `POST /api/v1/chat/conversaciones/{id}/mensajes` con la respuesta en streaming por SSE (eventos `aceptado`, `token`, `bloque`, `degradado`, `fin`, `error`), sin WebSocket; ADR-0021 reemplaza al ADR-0007 y se alinearon 22 documentos. 189 pruebas unitarias y 26 de integración pasan sobre PostgreSQL 18; flujo verificado por HTTP real contra una base migrada (sin clave de LLM: turno degradado con acciones rápidas). Falta: búsqueda y acople con el registro de herramientas del PR #35 | RDD desactivado; revisión del orquestador y prueba manual por HTTP | `273a6c4` en `feature/h3-10-conversations` del backend, sin push; `bdaf7a3` en specs |
| H3-10 (en curso) | Delegada (un redactor; más de dos archivos no triviales) | Quinto tramo: búsqueda de conversaciones en `GET /api/v1/chat/conversaciones/buscar?q=` sobre el título y los mensajes del cliente y del asistente, con los índices GIN existentes y sin migración. 202 pruebas unitarias y 34 de integración pasan sobre PostgreSQL 18. PR #36 integrado en `development` el 2026-10-12 con los cuatro primeros tramos. Falta: acople con el registro de herramientas del PR #35 y prueba con el modelo real | RDD desactivado; revisión del orquestador | `8711a49` directo en `development` del backend, sin PR por decisión de Mathias (cambio pequeño; excepción a la regla de rama propia y PR) |
| H3-10 (en curso) | Delegada (un mapeador y un redactor; más de dos archivos no triviales) | Sexto tramo: acople del bucle del agente con `ToolRegistry`. `RegistryToolAdapter` implementa `ToolExecutorPort` sobre el registro (traduce definiciones y contexto, `is_error` solo para los cuatro rechazos del registro, bloques fuera de los datos que ve el modelo); el puerto pasa de `block` a `blocks`; `build_tool_registry(handlers)` registra siempre `solicitar_registro` y solo los handlers comerciales que se le pasen, para que H3-12 y H3-13 conecten los suyos; se elimina `EmptyToolAdapter`. Además, por decisión de Mathias, el código no contiene referencias a hitos ni a tareas, solo a specs y ADR (`crear_registro_h3` → `build_tool_registry`, `HITO3_TOOL_CONTRACTS` → `TOOL_CONTRACTS`, `H3_ACTIONS` → `QUICK_ACTIONS`). 436 pruebas unitarias y 34 de integración pasan sobre PostgreSQL 18. Falta: prueba con el modelo real | RDD desactivado; revisión del orquestador | `a150de9` (refactor) y `7ac66a1` (acople) directo en `development` del backend, sin PR por decisión de Mathias |
| H3-10 (en curso) | Delegada (un redactor; más de dos archivos no triviales); prueba de humo en línea | Séptimo tramo: primera prueba contra la API real de OpenAI y migración de `OpenAIProvider` a la Responses API. Con Chat Completions todo turno quedaba degradado: `gpt-6-luna` rechaza herramientas cuando razona y solo acepta temperatura 0,6 con el razonamiento desactivado. El adaptador pasa a `client.responses.create` con `reasoning.effort` configurable por `LLM_REASONING_EFFORT` (por defecto `none`), `store=false`, herramientas con `strict=false` y temperatura solo cuando el razonamiento está en `none`; el puerto `LLMProvider` y el motor no cambian (enmienda del 2026-10-16 de ADR-0005). 451 pruebas unitarias y 34 de integración pasan sobre PostgreSQL 18. Prueba de humo por HTTP contra OpenAI: tres turnos sin degradar (3 a 5 s cada uno), streaming de tokens y vuelta completa con `solicitar_registro` | RDD desactivado; revisión del orquestador y prueba de humo real | `7bd2321` directo en `development` del backend, sin PR por decisión de Mathias |

Hallazgos de la prueba de humo con OpenAI (2026-10-16):

- **Herramienta usada fuera de lugar (resuelto en `d215350`):** ante "¿Tienen zapatillas Nike talla 42?" el modelo llamaba a `solicitar_registro` y mostraba el formulario de registro, porque es la única herramienta registrada. Su descripción indica ahora que se usa solo cuando el cliente pide crear una cuenta o registrarse. Verificado contra OpenAI: la búsqueda y la consulta de envío responden solo con texto y "Quiero registrarme" muestra el formulario.
- **Bloques sin `id` (resuelto en `d215350`):** el bloque `FORMULARIO` llegaba sin `id`, que el tipo `Bloque` del frontend exige. `RegistryToolAdapter` asigna un UUID a todo bloque de herramienta que llegue sin `id` y conserva el que ya trae.
- **Latencia:** de 3 a 5 s por turno completo con el system prompt real; un turno con herramienta hace dos llamadas al modelo.

Decisiones del segundo tramo de H3-10 (2026-10-11): primer proveedor OpenAI; temperatura 0,6 por defecto, que reemplaza el tope de 0,3 del ADR-0005 (enmienda del 2026-10-11); variables `LLM_PROVIDER`, `LLM_MODEL` (`gpt-6-luna`), `LLM_TEMPERATURE`, `LLM_MAX_TOKENS` (1024), `LLM_TIMEOUT_SECONDS` (15), `LLM_API_KEY` y `LLM_VISION_ENABLED`, ya incluidas en `.env.template`; sin reintentos del SDK para respetar el timeout. Sin verificar hasta tener la clave: que `gpt-6-luna` acepte `temperature`, `max_completion_tokens` e imágenes. El timeout del SDK es por fase de lectura, no un total; el límite estricto de 15 s corresponde al bucle del agente.

Decisiones provisionales del quinto tramo de H3-10 (2026-10-11): `q` vacío, ausente o de más de 100 caracteres responde `400 VALIDACION`; mismo formato, orden y paginación que el listado; no se buscan conversaciones sin título ni filas de herramientas; una consulta formada solo por palabras vacías devuelve una lista vacía. La configuración `spanish` ignora mayúsculas y tildes y une singular con plural, pero no encuentra palabras parciales. El resaltado que pide la spec ("resaltando la coincidencia") lo resuelve el backend con `ts_headline` en H3-15 (ver el cierre de H3-15 más abajo).

Decisiones del cuarto tramo de H3-10 (2026-10-11): transporte por SSE en la respuesta del `POST` (ADR-0021), decidido por Mathias. Provisionales: un cuerpo con `accion` o `adjuntoIds` responde `501 FUNCIONALIDAD_NO_DISPONIBLE`; campos desconocidos responden `400`; identificadores de las acciones rápidas (`BUSCAR_POR_CATEGORIA`, `VER_OFERTAS`, `VER_CARRITO`, `MIS_PEDIDOS`, `MIS_RECLAMOS`, `MIS_DEVOLUCIONES`); el bloque de respaldo usa la forma de `Bloque.ts` del frontend (`id`, `tipo: ACCIONES_RAPIDAS`, `acciones[{id, etiqueta}]`). Cambios que necesita el frontend (parte frontend de H3-10 desde el reparto vertical del 2026-10-15; antes H3-13): reemplazar el adaptador WebSocket por `fetch` con lectura del stream y `credentials: "include"`; leer el nombre del evento en `event:` y no en un campo `kind`; `bloque` llega como `{bloque}`; manejar `aceptado` y `degradado`; `error` trae solo `code`. Limitaciones conocidas: una desconexión del cliente surte efecto entre eventos, por lo que una llamada al LLM detenida retrasa la limpieza hasta el timeout; sin reanudación de un turno parcial; el historial devuelve `bloques` como `{"blocks": [...]}` y el frontend lo tipa como arreglo.

Decisiones provisionales del tercer tramo de H3-10 (2026-10-11): el límite de 15 s se aplica a cada llamada al LLM y no al turno completo; al llegar a la quinta iteración las herramientas pedidas no se ejecutan y se responde con un texto de respaldo; un segundo `ARGUMENTOS_INVALIDOS` en el mismo turno termina el turno; título con los primeros 40 caracteres del primer mensaje; mensaje de 1 a 1000 caracteres; el contexto usa solo mensajes del cliente y del asistente; si el cliente corta el stream se confirman las filas de herramientas ya ejecutadas; nombre del asistente por `ASSISTANT_NAME` (por defecto `Botleta`), ya incluida en `.env.template`. Textos de respaldo y tipo de bloque `QUICK_ACTIONS` propuestos por la implementación, no definidos en las specs. Fuera de este tramo: `OutputValidator`, filtro de datos sensibles, `DegradedMode`, adjuntos de imagen, límite de frecuencia y generación del resumen.

Decisiones provisionales de H3-10, pendientes de los contratos de H3-05: conversación ajena o inexistente responde `404`; listado como arreglo simple con `?pagina=` y 20 por página; historial con los últimos 50 mensajes sin los de herramientas; vista previa del último mensaje del cliente o del asistente; visitante anónimo por cookie `chat_sid` (se guarda su SHA-256, vigencia de 7 días); con cabecera `Authorization` responde `501` hasta que H3-09 entregue el validador de JWT.

Diferencias detectadas entre el contrato y el frontend: el frontend espera un arreglo sin metadatos de página y no envía `pagina`; espera un campo `fecha` con etiqueta legible que el backend no envía; tipa `bloques` como arreglo mientras `message.blocks` es un objeto.

Hallazgos que afectan al despliegue:

- Resuelto (H3-05): `alembic upgrade head` fallaba en una instalación limpia porque `env.py` convierte la URL a `psycopg2` y ese paquete no estaba en `requirements.txt`. Se añadió `psycopg2-binary` en el commit `4758b14` del backend.
- Decidido (2026-10-16): la cookie `chat_sid` usa `SameSite=Lax` y no hay CORS, por lo que con el frontend en Vercel y el backend en Railway el navegador no la enviaría (afecta también a la cookie de refresh, ADR-0008). El frontend llamará a la API en su propio origen mediante un proxy: [ADR-0023](../../docs/arquitectura/adr/ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md). La verificación del streaming SSE a través del proxy es el primer paso de H3-18.

Pendientes que deja H3-01: quién aporta el medio de pago de Railway. Decidido (2026-10-16): los mocks del entorno desplegado se resuelven con adaptadores falsos en proceso, seleccionados con `MODULES_MODE` ([ADR-0022](../../docs/arquitectura/adr/ADR-0022-modulos-simulados-en-proceso-para-los-entornos-desplegados.md)); afecta a H3-03, H3-06 y H3-07, y exige antes el puerto de salida de Seguridad (H3-09).

Cierre de H3-05 y avance de H3-04 (2026-10-14):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-05 | Delegada a Sebastian | PR #37 mergeado en `development` del backend: base de contratos de módulos, cliente httpx, DTO de bloques y SSE, configuración por entorno | Aprobación de PR | `e40ee4e` en `development` del backend |
| H3-04 | — | Migración a pnpm y lockfile ya en `development` del frontend (`b5e0469`, `1794b10`). Falta: despliegue en Vercel con vista previa por PR y verificar el CI en GitHub | — | — |
| H3-08 | En línea (revisión) y delegada (un revisor de solo lectura) | PR #35 de Alonso: las correcciones de `d50a3c8` resuelven el bloqueante del filtro de datos sensibles, los falsos positivos, la idempotencia, el `output_validator` y `degraded_mode`; 357 pruebas unitarias pasan. Residuales para un PR posterior: tarjetas con `/` o `_` como separador, contraseña con `! ` dentro del secreto, tests más fuertes (contraseña completa, `US$`) | Aprobado por Mathias el 2026-10-14; RDD desactivado | `3e974d3` (merge) en `development` del backend |
| H3-06 | En línea (revisión) y delegada (un revisor de solo lectura y un redactor para los residuales) | PR #39 de Sonny: las correcciones de `8cc6e61` resuelven los tres bloqueantes (4xx como `ModuleRequestError`, prueba del 404 por el cliente público, nombres en inglés). Residuales cerrados por Mathias directo en `development`: 4xx sin JSON conserva el estado, `ModuleRequestError` en `module_errors.py`, `MAX_SKUS_PER_CALL` compartido, errores de transporte de httpx traducidos en `base_client.py`. 395 pruebas unitarias pasan | Aprobado por Mathias el 2026-10-14; RDD desactivado | `a14bc5d` (merge) y `7ab8351` en `development` del backend |
| Limpieza de tests | En línea (renombrado mecánico) | Los tests con prefijo de hito pasan a llevar el nombre de lo que prueban (`test_module_contracts`, `test_product_inventory_clients`, `test_catalog_tools`, `test_conversation_attachment_persistence`) y `h3_tools.py` pasa a `catalog_tools.py`. Quedan sin renombrar `docs/h2-06-persistencia.md` y `docs/h3-motor-herramientas.md`. No se ejecutó el test de integración (requiere PostgreSQL) | RDD desactivado | `6d3c14b` en `development` del backend |

Alineación con las specs (2026-10-14): SPEC-24 queda en Hito 5–6 y no altera el alcance. El alineamiento con Ventas está mergeado (specs #12). El alineamiento con Productos HTTP 0.5.0 (specs #11) sigue abierto y puede obligar a ajustar H3-06 (PR #39) y H3-12. Sin avance verificable aún en H3-00, H3-09 y H3-11 a H3-18. Con el #35 y el #39 integrados, H3-11 y H3-12 quedan desbloqueadas.

Cierre de H3-02 (2026-10-15):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-02 | En línea (configuración de GitHub por API) | Protección clásica en `main` y `development` de backend y frontend: PR obligatorio con una aprobación, se descartan aprobaciones al llegar commits nuevos, check de CI obligatorio (`test` en backend, `check` en frontend; sin exigir rama al día), sin force-push ni borrado. `enforce_admins` desactivado por decisión de Mathias, para permitir commits directos de emergencia. El team `chatbot` pasa de admin a maintain en ambos repos, porque como admin podía saltarse la protección; Mathias conserva admin como owner de la organización. Verificado por API: protección aplicada en las cuatro ramas, `SebJoq21` con rol maintain, `MathiasTL` con rol admin | No aplica (configuración remota) | No aplica |

Riesgo residual de H3-02: los otros ocho owners de la organización `Taller-SW-Web` (incluye integrantes de otros grupos) siguen siendo admin y pueden saltarse la protección; solo los puede cambiar quien administre la organización. El resto del equipo pierde acceso a Settings de los repos (secretos, webhooks, integraciones), que queda a cargo de Mathias.

Cierre de H3-07 (2026-10-16):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-07 | Delegada a Sebastian; revisión delegada (un revisor de solo lectura) y correcciones delegadas (un redactor) | PR #40: `SecurityClient` sobre `BaseModuleClient` con las rutas del contrato §3.1, reenvío del token del titular (A15), 4xx como `ModuleRequestError`, seeds de respx. Correcciones de la revisión aplicadas por Mathias en la rama (`ee98b9c`): se elimina `introspeccion_api_adapter.py`; sin valor por defecto en código para `SECURITY_CLIENT_SECRET` (el cliente no arranca sin él; `.env.template` mantiene el secreto del mock); forma inesperada de direcciones como `ModuleUnavailableError`; un 2xx con cuerpo vacío devuelve `{}`; todo 401 del login responde `CREDENCIALES_INVALIDAS`; tests más fuertes. 420 pruebas unitarias pasan en local y en CI | Aprobado por Mathias el 2026-10-16; RDD desactivado | `b3804eb` (merge) en `development` del backend |

Pendientes de H3-07 para H3-09: puerto de salida para Seguridad (hoy el cliente no implementa un puerto, a diferencia de H3-06) y token de servicio (`/auth/token`, A3) antes del Hito 4. `docs/arquitectura-backend.md` (líneas 107 y 154) aún menciona `introspeccion_api_adapter.py`.

Cierre de H3-03 (2026-10-16):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-03 | Delegada (un mapeador y un redactor); despliegue en Railway hecho por Mathias desde el dashboard | `Dockerfile` (`python:3.12-slim`, usuario sin privilegios uid 10001, `uvicorn` como PID 1 en `${PORT:-8000}` con `--proxy-headers`, `HEALTHCHECK`) y `.dockerignore`. Verificado en local: build de 401 MB, `/health` responde 200 en el puerto 8000 y con `PORT=9000`, contenedor `healthy`, `alembic history` ve `0001 (head)`. Servicio en Railway (entorno *staging*, rama `development`, despliegue automático): `https://g3-chatbot-backend-staging.up.railway.app/health` responde 200. Healthcheck `/health` (60 s) y reinicio `On Failure` (3 reintentos) configurados en el dashboard: Railway ya no lee `railway.json` en servicios nuevos (*config as code* deprecado), por lo que se eliminó | PR #41 aprobado; RDD desactivado | `7a619b0` (merge del #41) y `e1433b5` (borra `railway.json`, directo en `development`) en el backend |

Cierre de H3-00 (2026-10-16):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-00 | Hecha por Nikol | H2-09 cerrada con `docs/evidencia-hito-2.md` (PR #13, `f705f6e`). `hito-2.md` actualizado: H2-03 a H2-10 marcadas con su commit y PR, los cuatro criterios de aceptación cumplidos y el vínculo entre cuentas de GitHub e integrantes confirmado por la PO. La evidencia marca como cumplido el criterio de enlaces del README (specs PR #14) | PR #16 mergeado | `d27a7e3` (merge del #16) en `main` de specs |

Fuera de H3-03, en H3-18: `DATABASE_URL`, migraciones como paso del despliegue, secretos por entorno, `MODULES_MODE` ([ADR-0022](../../docs/arquitectura/adr/ADR-0022-modulos-simulados-en-proceso-para-los-entornos-desplegados.md)), entorno de producción para `main` y prueba del SSE sin búfer a través del proxy de Vercel ([ADR-0023](../../docs/arquitectura/adr/ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md)).

Cierre de H3-04 (2026-10-16):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-04 | En línea (verificación); proyecto de Vercel creado por Mathias desde el dashboard | pnpm 10.34.6 y lockfile versionados en `development` del frontend; el CI de GitHub (`check`: lint, typecheck, test y build) pasa en `development`. Proyecto de Vercel (plan Hobby) conectado al repo por la app de GitHub; rama de producción `main` (rama por defecto del repo). `https://g3-chatbot-frontend.vercel.app/` responde 200 y el estado `Vercel` del último commit de `main` es `success`. Sin variables de entorno: el frontend usa sus mocks hasta H3-18 | No aplica (configuración remota) | `b5e0469` y `1794b10` en `development` del frontend |

Decisiones de H3-04 (Mathias, 2026-10-16): una sola URL del frontend, la de producción (`main`), sin entorno ni dominio de *staging* en Vercel. Las vistas previas por PR no forman parte del alcance: los cambios se prueban en local y luego en el despliegue. Lo mergeado en `development` no aparece en la URL hasta que se promueve a `main`. Con el proxy de [ADR-0023](../../docs/arquitectura/adr/ADR-0023-proxy-del-frontend-hacia-la-api-mismo-origen.md), producción del frontend apunta a producción del backend (H3-18).

Avance de H3-16 (2026-10-16):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-16 (en revisión) | Hecha por Nikol | `docs/casos-prueba-hito-3.md`: 126 casos, uno por escenario de las specs del hito (SPEC-01, 02, 03, 05, 06, 09, 10 y 11), con Dado, Cuando y Entonces tomados de la spec, nivel (23 E2E, 63 API, 3 de unidad y 28 de evaluación del LLM), tarea responsable y la prueba del backend que ya cita el escenario (10 casos). 9 escenarios quedan marcados fuera del hito (imágenes, checkout, pedido y promociones). Frontend: `tests/e2e/smoke.spec.ts` con siete pruebas de humo sin respuestas simuladas; E2E-01 (inicio) y E2E-02 (barra lateral) activas, E2E-03 a E2E-07 en `test.fixme` hasta que H3-09, H3-10, H3-12, H3-13 y H3-14 conecten su funcionalidad; `playwright.config.ts` acepta `E2E_BASE_URL` para correr contra un entorno desplegado. Verificado en local contra el backend y PostgreSQL 18: E2E-01 y E2E-02 pasan con H3-15 incluido; sin H3-15, E2E-02 falla porque "Nuevo chat" no llama al backend | Pendiente | `bb107d1` en `feature/h3-16-e2e-humo` del frontend |

Pendientes de H3-16 para H3-19: definir cómo obtiene la prueba el enlace de verificación de correo en staging (buzón de pruebas o token del mock de Seguridad) y una cuenta de prueba (`E2E_CORREO`, `E2E_CLAVE`) para E2E-05; con la decisión de H3-04 (solo producción en Vercel), la corrida sobre *staging* de H3-19 usa el frontend en local con `API_PROXY_TARGET` hacia el backend de *staging*; `E2E_BASE_URL=https://g3-chatbot-frontend.vercel.app` sirve para la verificación final en producción (H3-20).

Avance de H3-15 (2026-10-16):

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-15 (backend y frontend integrados) | Hecha por Nikol | Backend: `GET /chat/conversaciones/buscar` agrega `resaltado: {titulo, fragmento}` con tramos `{texto, coincide}`, calculado con `ts_headline` sobre la configuración `spanish` (resalta también singular y plural); `fragmento` sale del mensaje coincidente más reciente del cliente o del asistente y es `null` si solo coincidió el título; las marcas son caracteres de control que se quitan antes del texto guardado, para que el contenido no pueda falsificar una coincidencia. 463 pruebas pasan, 38 de integración sobre PostgreSQL 18. Frontend: `Sidebar` sin `MOCK_CONVERSACIONES` (listar con "Ver más", buscar con espera de 300 ms y `<mark>`, "Nuevo chat" con `POST` y navegación, estados de carga, vacío y error) y `rewrites` de `/api/*` hacia `API_PROXY_TARGET` (ADR-0023). Verificado en local de punta a punta (navegador, proxy de Next, backend y PostgreSQL 18) | Aprobado por Mathias el 2026-10-16: backend #42 y frontend #19 mergeados con squash; verificada la suite del backend contra PostgreSQL 18 (463 pruebas) y medido el costo de la búsqueda con 3000 conversaciones y 25 mensajes cada una (17,5 ms en `development` contra 19,5 ms con el PR), por lo que no se optimizó. RDD desactivado | `6ccaa8c` en `development` del backend (squash del #42); `4d29e84` en `development` del frontend (squash del #19); specs #18 mergeado |

Notas de H3-15: el `rewrite` del ADR-0023 entra con este PR del frontend; H3-18 solo debe configurar `API_PROXY_TARGET` por entorno. En *staging*, `POST /api/v1/chat/conversaciones` responde `500` (el listado responde `200` porque sin cookie no consulta la base): es consistente con la falta de `DATABASE_URL`, pendiente de H3-18. Mientras tanto, "Nuevo chat" muestra el error en el despliegue. `ChatPage` sigue con datos semilla (H3-10), por lo que una conversación abierta desde la barra lateral aún no muestra su historial real.

Avance de H3-10, parte frontend (2026-10-16): seguimiento propio en [`h3-10-frontend-chat-sse.md`](h3-10-frontend-chat-sse.md).

| Tarea | Ruta | Evidencia | Revisión | Commit |
|---|---|---|---|---|
| H3-10 frontend (en curso, sin PR) | Delegada (un redactor por tarea; cinco tareas más el Markdown, los botones mock y la documentación) | Transporte SSE con `fetch` (puerto, parser incremental y adaptador), retiro del WebSocket, historial real con mapper de `bloques`, estado del turno (reductor puro, caso de uso y hook `useChat`), interfaz conectada (`ChatPage`, `ChatWindow`, `MessageBubble`, Home crea la conversación real) y Markdown seguro para los mensajes del asistente con resaltado de códigos y promociones. Decisiones de Mathias: si el stream termina sin `fin` ni `error`, una sola reconsulta del historial y, sin respuesta, turno incompleto con "Reintentar", sin polling; el texto de respaldo de un turno degradado llega como `token` tras `degradado` (backend `69f184a`); Markdown con librería; botones de pedidos y devoluciones deshabilitados ("Próximamente"). Prueba en navegador con OpenAI real a través del proxy de Next: 331 tokens repartidos en 3,2 s, primer token a 1,19 s, herramientas correctas en conversaciones nuevas. Frontend: 164 pruebas, `lint` (0 errores), `typecheck` y `build` pasan. Specs enmendadas (ADR-0021, contrato, `motor-conversacion`, casos de prueba y documentos de producto) | RDD desactivado; código central leído por el orquestador | Siete commits en `feature/h3-10-chat-sse` del frontend (`3c04fe5` a `2435c3a`), sin push ni PR; `69f184a` directo en `development` del backend, sin push |

Hallazgos de la prueba en navegador que afectan a otras tareas:

- **H3-09:** el asistente anuncia el formulario de registro y la interfaz no lo muestra, porque el bloque `FORMULARIO` no se renderiza y `Bloque` no define su forma. Sin esto no se cumple "el cliente se registra".
- **H3-12:** tras pedir el registro, una pregunta de producto en la misma conversación volvió a devolver `FORMULARIO`; en conversaciones nuevas no ocurre. Revisar cuando existan las herramientas de búsqueda reales.
- **H3-18:** el backend lee `LLM_API_KEY` solo del entorno del proceso (no del archivo `.env`), y en desarrollo Next 16 bloquea `/_next` si se entra por `127.0.0.1` (usar `localhost`). La verificación del streaming por el proxy en local quedó hecha; falta repetirla en Vercel.
- **Latencia:** un turno con herramienta tardó más de 8 s una vez en el navegador; por script dio 3,4 s en dos corridas. No se reprodujo.

## Siguiente paso

Fase 0 cerrada. En la Fase 1, H3-15 está integrada (backend #42 y frontend #19) y la parte frontend de H3-10 está terminada en `feature/h3-10-chat-sse`: falta abrir el PR contra `development` (una sola entrega, porque las piezas dependen entre sí), empujar el commit `69f184a` del backend y marcar H3-10. Siguen H3-09 (que debe renderizar `FORMULARIO`), H3-11 (Alonso), H3-12 (Sonny, ajustada a Productos 0.5.0 cuando se mergee specs #11) y el resto según el reparto vertical del 2026-10-15. Siguen por decidir la fecha de la demo y la política de cookies entre dominios.
