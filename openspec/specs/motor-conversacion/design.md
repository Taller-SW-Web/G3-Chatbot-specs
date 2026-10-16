# Diseño: Motor de conversación, conversaciones múltiples e interpretación de intención

> Origen: SPEC-05 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Componente | Uso | Estado |
|---|---|---|
| Proveedor LLM (Claude/OpenAI) | Interpretación y redacción; con SPEC-23, también contenido multimodal (imágenes en base64) | Definido por configuración; soporte de visión sin verificar (SPEC-23) |
| Supabase Storage (`AttachmentStorage`) | Lectura de las imágenes adjuntas al armar el turno (detalle en SPEC-23) | 🟡 Ver [`adjuntos-imagenes-chat`](../adjuntos-imagenes-chat/design.md) |
| Todos los clientes de módulos | A través de las herramientas | Ver `contratos-integracion.md` |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `AppShell` (inbound, orquesta) | Layout raíz del App Router de Next.js (componente de cliente): monta `Sidebar`, contiene las rutas `/` (`HomePage`), `/chat/[id]` (`ChatPage`), `/carrito` (`CartPage`), `/checkout` (`CheckoutPage`) y `/pedidos` (`OrderHistoryPage`), y mantiene el estado del stream SSE activo. |
| `Sidebar` | "Nuevo chat", campo "Buscar chats", lista de conversaciones recientes (título + vista previa), acceso al perfil y a `SesionIndicator` (SPEC-03). |
| `HomePage` | Banner de ofertas, grid de productos en oferta y el compositor de chat. |
| `ChatPage` + `useChat` | Orquesta la vista de una conversación: envía mensajes por REST, lee el stream SSE de la respuesta, renderiza `MessageList`. |
| `MessageList` / `MessageRenderer` | Mapea `Bloque.tipo` al componente correspondiente; muestra el efecto de streaming token por token. |
| `Composer` | Campo de texto (máx. 1000 caracteres), envío con Enter, deshabilitado mientras se espera. Con SPEC-23 admite hasta 3 imágenes adjuntas (`AttachmentButton`, `AttachmentPreviewList`) y envía sus `adjuntoIds` junto con el texto. |
| `QuickReplies` | Chips de acciones rápidas que envían `accion`. |
| `TypingIndicator` | Indicador "escribiendo…" mientras llegan tokens por SSE. |
| `DegradedBanner` | Aviso de modo degradado (sin LLM o con el stream interrumpido) y menú alternativo. |
| `chatStore` (Zustand) | Conversación activa, listado de conversaciones, mensajes, cola de envío y **token de sesión en LocalStorage** (ver §1.4). |
| Puerto `ChatbotApiPort` (dominio) | Contrato de los casos de uso hacia el adaptador REST. |
| Puerto `StreamingPort` (dominio) | Contrato de los casos de uso hacia el adaptador de streaming. |
| `Axios Adapter` (outbound) | Implementa `ChatbotApiPort`; interceptor JWT desde `chatStore`. |
| `SSE Adapter` (outbound) | Implementa `StreamingPort` con un lector de `fetch` con streaming (`EventSource` no admite `POST`); si el stream se corta, si el stream termina sin `fin` ni `error`, reconsulta el historial una sola vez. |
| `container.ts` / `apiConfig.ts` (infrastructure) | Inyección de dependencias y URL base del backend (variable pública `NEXT_PUBLIC_API_URL`). |

## Backend

| Componente | Responsabilidad |
|---|---|
| `chatbot_router.py` (adaptador inbound REST) | `POST/GET /conversaciones`, `GET /conversaciones/buscar`, `GET/POST /conversaciones/{id}/mensajes` (el `POST` acepta `adjuntoIds`, SPEC-23); invoca `ChatbotServicePort`. Valida y comprueba la pertenencia antes de abrir el stream (errores `problem+json`) y, en un envío de texto, responde `200 text/event-stream` con los eventos `aceptado`, `token`, `bloque`, `degradado`, `fin` y `error` ([ADR-0021](../../../docs/arquitectura/adr/ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md)). Los endpoints de adjuntos están en SPEC-23. |
| `ChatbotServicePort` (puerto inbound) | Contrato único que expone el adaptador REST hacia los casos de uso. |
| `GestionarConversacionUseCase` | Crear, listar, buscar y cargar historial; pertenencia por cliente o `chat_sid`. |
| `InterpretarYResponderUseCase` | Arma el prompt, llama al LLM, ejecuta herramientas (máx. 5 iteraciones y 1 reintento por error de validación), ensambla los bloques y los entrega como eventos del turno al adaptador REST, que los emite por SSE. Con SPEC-23, incluye en el contexto las imágenes de los últimos 12 mensajes como contenido multimodal (base64). |
| `LLMProvider` (puerto outbound) + `ClaudeProvider` / `OpenAIProvider` | Llamada con tools, streaming y timeouts. Con SPEC-23, acepta partes de contenido de texto e imagen y declara si el modelo admite visión. |
| `ToolRegistry` | Nombre, descripción, esquema Pydantic, `requiere_sesion`, `requiere_confirmacion` y handler (un caso de uso). |
| `ActionDispatcher` | Enruta las acciones de botones a los mismos handlers, sin pasar por `InterpretarYResponderUseCase`. |
| `SensitiveDataFilter` | Redacta tarjetas (Luhn), secuencias de 6 dígitos tras pedir un OTP, patrones de contraseña y números de documento precedidos por una palabra que los identifique (DNI, RUC, CE, pasaporte). |
| `OutputValidator` | Contrasta los precios y montos del texto transmitido con los resultados de las herramientas. |
| `DegradedMode` | Intérprete de palabras clave y menú, activo también cuando el stream falla. Con SPEC-23 cubre además el fallo de visión: avisa que la imagen no pudo analizarse y procesa el texto sin ella. |
| `RateLimiter` | Por cliente, IP y conversación. Un mensaje con imágenes cuenta como uno; el límite de cargas de imagen lo define SPEC-23. |
| `conversacion_postgres_adapter.py` (outbound) | Persistencia de conversaciones y mensajes en PostgreSQL. |
| `prompts/sistema.md` | Prompt del sistema versionado. |
| `evals/` | Script `pytest -m evals` que mide la precisión de intención. |

## Desglose para issues

- [ ] `[FE]` `AppShell` como layout raíz del App Router con las rutas `/`, `/chat/[id]`, `/carrito`, `/checkout` y `/pedidos`
- [ ] `[FE]` `Sidebar` con nuevo chat, búsqueda y listado de recientes
- [ ] `[FE]` `HomePage` con banner de ofertas y grid de productos
- [ ] `[FE]` `ChatPage`, `useChat`, `MessageList` y `MessageRenderer` con soporte de streaming
- [ ] `[FE]` `Composer`, `QuickReplies`, `TypingIndicator` y `DegradedBanner`
- [ ] `[FE]` `chatStore` (conversación activa, listado, mensajes, token) y puertos `ChatbotApiPort`/`StreamingPort`
- [ ] `[FE]` `Axios Adapter` (interceptor JWT) y `SSE Adapter` (lector de `fetch` con streaming y reconsulta única del historial)
- [ ] `[FE]` `container.ts` y `apiConfig.ts`
- [ ] `[BE]` Modelos `conversation` y `message` (con `title` derivado) y migraciones Alembic
- [ ] `[BE]` `chatbot_router.py`: conversaciones, búsqueda y mensajes
- [ ] `[BE]` Streaming SSE en la respuesta del `POST` de mensajes: eventos `aceptado`, `token`, `bloque`, `degradado`, `fin` y `error`
- [ ] `[BE]` `GestionarConversacionUseCase`
- [ ] `[BE]` Interfaz `LLMProvider` más una implementación inicial con streaming
- [ ] `[BE]` `ToolRegistry`, `InterpretarYResponderUseCase` y `ActionDispatcher`
- [ ] `[BE]` `SensitiveDataFilter` y `OutputValidator`
- [ ] `[BE]` `DegradedMode` y `RateLimiter`
- [ ] `[BE]` Prompt del sistema v1 y resumen de conversación
- [ ] `[QA]` Conjunto de evaluación de 120 frases y job de CI con umbral del 90 %
- [ ] `[BE]` Aceptar `adjuntoIds` en `POST /conversaciones/{id}/mensajes` y admitir contenido multimodal en `LLMProvider` e `InterpretarYResponderUseCase` (el detalle de adjuntos está en [`adjuntos-imagenes-chat`](../adjuntos-imagenes-chat/design.md))
- [ ] `[QA]` Pruebas de todos los escenarios (LLM y stream SSE mockeados); prueba de la reconsulta única del historial y de la acción "Reintentar" cuando el stream se corta
