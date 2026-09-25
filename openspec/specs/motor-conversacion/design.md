# Diseño: Motor de conversación, conversaciones múltiples e interpretación de intención

> Origen: SPEC-05 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Componente | Uso | Estado |
|---|---|---|
| Proveedor LLM (Claude/OpenAI) | Interpretación y redacción | Definido por configuración |
| Todos los clientes de módulos | A través de las herramientas | Ver `contratos-integracion.md` |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `AppShell` (inbound, orquesta) | Layout raíz del App Router de Next.js (componente de cliente): monta `Sidebar`, contiene las rutas `/` (`HomePage`), `/chat/[id]` (`ChatPage`), `/carrito` (`CartPage`), `/checkout` (`CheckoutPage`) y `/pedidos` (`OrderHistoryPage`), y suscribe la conexión WebSocket activa. |
| `Sidebar` | "Nuevo chat", campo "Buscar chats", lista de conversaciones recientes (título + vista previa), acceso al perfil y a `SesionIndicator` (SPEC-03). |
| `HomePage` | Banner de ofertas, grid de productos en oferta y el compositor de chat. |
| `ChatPage` + `useChat` | Orquesta la vista de una conversación: envía mensajes por REST, escucha el WebSocket, renderiza `MessageList`. |
| `MessageList` / `MessageRenderer` | Mapea `Bloque.tipo` al componente correspondiente; muestra el efecto de streaming token por token. |
| `Composer` | Campo de texto (máx. 1000 caracteres), envío con Enter, deshabilitado mientras se espera. |
| `QuickReplies` | Chips de acciones rápidas que envían `accion`. |
| `TypingIndicator` | Indicador "escribiendo…" mientras llegan tokens por WebSocket. |
| `DegradedBanner` | Aviso de modo degradado (sin LLM o sin WebSocket) y menú alternativo. |
| `chatStore` (Zustand) | Conversación activa, listado de conversaciones, mensajes, cola de envío y **token de sesión en LocalStorage** (ver §1.4). |
| Puerto `ChatbotApiPort` (dominio) | Contrato de los casos de uso hacia el adaptador REST. |
| Puerto `WebSocketPort` (dominio) | Contrato de los casos de uso hacia el adaptador de streaming. |
| `Axios Adapter` (outbound) | Implementa `ChatbotApiPort`; interceptor JWT desde `chatStore`. |
| `WebSocket Adapter` (outbound) | Implementa `WebSocketPort`; reconexión con backoff y *fallback* a *polling*. |
| `container.ts` / `apiConfig.ts` (infrastructure) | Inyección de dependencias y URL base del backend (variable pública `NEXT_PUBLIC_API_URL`). |

## Backend

| Componente | Responsabilidad |
|---|---|
| `chatbot_router.py` (adaptador inbound REST) | `POST/GET /conversaciones`, `GET /conversaciones/buscar`, `GET/POST /conversaciones/{id}/mensajes`; invoca `ChatbotServicePort`. |
| `chatbot_ws_adapter.py` (adaptador inbound WebSocket) | Handshake con JWT, suscripción por `conversacionId`, emisión de los eventos `token`, `bloque` y `fin`; invoca `ChatbotServicePort` solo para transmitir, nunca para ejecutar acciones. |
| `ChatbotServicePort` (puerto inbound) | Contrato único que exponen ambos adaptadores hacia los casos de uso. |
| `GestionarConversacionUseCase` | Crear, listar, buscar y cargar historial; pertenencia por cliente o `chat_sid`. |
| `InterpretarYResponderUseCase` | Arma el prompt, llama al LLM, ejecuta herramientas (máx. 5 iteraciones y 1 reintento por error de validación), ensambla los bloques y los transmite por el puerto de WebSocket. |
| `LLMProvider` (puerto outbound) + `ClaudeProvider` / `OpenAIProvider` | Llamada con tools, streaming y timeouts. |
| `ToolRegistry` | Nombre, descripción, esquema Pydantic, `requiere_sesion`, `requiere_confirmacion` y handler (un caso de uso). |
| `ActionDispatcher` | Enruta las acciones de botones a los mismos handlers, sin pasar por `InterpretarYResponderUseCase`. |
| `SensitiveDataFilter` | Redacta tarjetas (Luhn), secuencias de 6 dígitos tras pedir un OTP, patrones de contraseña y números de documento precedidos por una palabra que los identifique (DNI, RUC, CE, pasaporte). |
| `OutputValidator` | Contrasta los precios y montos del texto transmitido con los resultados de las herramientas. |
| `DegradedMode` | Intérprete de palabras clave y menú, activo también cuando el WebSocket falla. |
| `RateLimiter` | Por cliente, IP y conversación. |
| `conversacion_postgres_adapter.py` (outbound) | Persistencia de conversaciones y mensajes en PostgreSQL. |
| `prompts/sistema.md` | Prompt del sistema versionado. |
| `evals/` | Script `pytest -m evals` que mide la precisión de intención. |

## Desglose para issues

- [ ] `[FE]` `AppShell` como layout raíz del App Router con las rutas `/`, `/chat/[id]`, `/carrito`, `/checkout` y `/pedidos`
- [ ] `[FE]` `Sidebar` con nuevo chat, búsqueda y listado de recientes
- [ ] `[FE]` `HomePage` con banner de ofertas y grid de productos
- [ ] `[FE]` `ChatPage`, `useChat`, `MessageList` y `MessageRenderer` con soporte de streaming
- [ ] `[FE]` `Composer`, `QuickReplies`, `TypingIndicator` y `DegradedBanner`
- [ ] `[FE]` `chatStore` (conversación activa, listado, mensajes, token) y puertos `ChatbotApiPort`/`WebSocketPort`
- [ ] `[FE]` `Axios Adapter` (interceptor JWT) y `WebSocket Adapter` (reconexión y *fallback*)
- [ ] `[FE]` `container.ts` y `apiConfig.ts`
- [ ] `[BE]` Modelos `conversacion` y `mensaje` (con `titulo` derivado) y migraciones Alembic
- [ ] `[BE]` `chatbot_router.py`: conversaciones, búsqueda y mensajes
- [ ] `[BE]` `chatbot_ws_adapter.py`: handshake JWT, suscripción y eventos de streaming
- [ ] `[BE]` `GestionarConversacionUseCase`
- [ ] `[BE]` Interfaz `LLMProvider` más una implementación inicial con streaming
- [ ] `[BE]` `ToolRegistry`, `InterpretarYResponderUseCase` y `ActionDispatcher`
- [ ] `[BE]` `SensitiveDataFilter` y `OutputValidator`
- [ ] `[BE]` `DegradedMode` y `RateLimiter`
- [ ] `[BE]` Prompt del sistema v1 y resumen de conversación
- [ ] `[QA]` Conjunto de evaluación de 120 frases y job de CI con umbral del 90 %
- [ ] `[QA]` Pruebas de todos los escenarios (LLM y WebSocket mockeados); prueba de reconexión sin duplicar texto
