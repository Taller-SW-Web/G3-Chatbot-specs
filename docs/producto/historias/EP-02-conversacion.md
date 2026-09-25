# EP-02 · Motor de conversación — Historias de usuario

> Spec: [SPEC-05](../../../openspec/specs/motor-conversacion/spec.md) · Área `CNV` · 12 historias · 57 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.

---

## HU-CNV-01 · Iniciar conversaciones nuevas y retomar las anteriores

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 5 | Hito 3 | `SPEC-05 · Req. 1` (escenarios 1, 2, 4 y 5) | RN-CNV-01, RN-CNV-02, RN-CNV-03 | — |

**Como** cliente (anónimo o autenticado), **quiero** abrir un chat nuevo cuando lo necesite y volver a mis conversaciones recientes desde la barra lateral, **para** separar mis compras y retomar una sin perder su contexto.

**Criterios de aceptación**
- `SPEC-05 · Req. 1 · Scenario: Nueva conversación desde la barra lateral` — "Nuevo chat" crea una conversación vacía, navega a `ChatPage` y solo aparece en "Recientes" al tener su primer mensaje.
- `SPEC-05 · Req. 1 · Scenario: Listado de conversaciones recientes` — el listado se ordena por último mensaje, con título de hasta 40 caracteres y vista previa.
- `SPEC-05 · Req. 1 · Scenario: Retomar una conversación` — se cargan los últimos 50 mensajes y se restaura la memoria de trabajo.
- `SPEC-05 · Req. 1 · Scenario: Conversaciones anónimas y fusión al iniciar sesión` — las conversaciones de `chat_sid` quedan ligadas al cliente al autenticarse.

**Prioridad:** Must: es la base de la aplicación de chat (`AppShell`, `Sidebar`, persistencia).

**Notas:** incluye el esqueleto de la app (`AppShell` con las rutas `/`, `/chat/[id]`, `/carrito`, `/checkout` y `/pedidos`), `chatStore`, los puertos y la inyección de dependencias.

---

## HU-CNV-02 · Buscar entre mis conversaciones

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 2 | Hito 3 | `SPEC-05 · Req. 1` (escenario 3) | — | — |

**Como** cliente con varias conversaciones, **quiero** buscar un término en mis chats, **para** encontrar rápido una conversación anterior.

**Criterios de aceptación**
- `SPEC-05 · Req. 1 · Scenario: Buscar chats` — la búsqueda devuelve las conversaciones cuyo título o mensajes contienen el término, con la coincidencia resaltada.

**Prioridad:** Should: mejora la navegación, pero no bloquea la compra.

---

## HU-CNV-03 · Ver ofertas y empezar a conversar desde la pantalla de inicio

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 5 | Hito 3 | `SPEC-05 · Req. 2` | RN-CNV-04 | Productos 🟡 (A5) |

**Como** visitante que abre la app, **quiero** ver ofertas destacadas y un campo para escribir en la misma pantalla, **para** empezar a comprar sin registrarme ni navegar menús.

**Criterios de aceptación**
- `SPEC-05 · Req. 2 · Scenario: Primera apertura` — se muestran el banner (SPEC-08), un grid de hasta 4 productos en oferta (SPEC-06, `soloOfertas=true`) y el campo de chat, sin sesión.
- `SPEC-05 · Req. 2 · Scenario: Promociones no disponibles` — sin promociones (Hito 3, falla o lista vacía) el banner se oculta y el grid y el chat se muestran igual, sin error.
- `SPEC-05 · Req. 2 · Scenario: Escribir desde la pantalla de inicio` — la conversación se crea al enviar el primer mensaje y la app navega a `ChatPage`.
- `SPEC-05 · Req. 2 · Scenario: Agregar directo desde el grid de ofertas` — el botón "+" ejecuta la acción directa `AGREGAR_AL_CARRITO` sin abrir una conversación.

**Prioridad:** Must: es la pantalla de entrada definida por el wireframe.

**Notas:** en Hito 3 se entrega con el grid alimentado por SPEC-06 y el banner oculto; el banner se activa en Hito 4 cuando está disponible SPEC-08 (HU-CAT-09). Decisión en la pregunta abierta 2 de [`alcance.md`](../alcance.md#preguntas-abiertas).

---

## HU-CNV-04 · Pedir lo que necesito en lenguaje natural

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 8 | Hito 3 | `SPEC-05 · Req. 3` | RN-CNV-05, RN-CNV-06 | Proveedor LLM (configuración) |

**Como** cliente, **quiero** escribir lo que busco con mis propias palabras y que el asistente elija la acción correcta, **para** comprar conversando sin aprender comandos.

**Criterios de aceptación**
- `SPEC-05 · Req. 3 · Scenario: Intención clara con parámetros` — el LLM invoca la herramienta con argumentos validados y la respuesta trae texto breve más el bloque estructurado.
- `SPEC-05 · Req. 3 · Scenario: Mensaje ambiguo` — se responde con una sola pregunta aclaratoria y acciones sugeridas, sin herramientas.
- `SPEC-05 · Req. 3 · Scenario: Fuera del dominio` — el asistente aclara que solo ayuda con compras en la tienda deportiva.

**Prioridad:** Must: el curso exige la consulta conversacional de productos en lenguaje natural.

**Notas:** incluye `LLMProvider`, `ToolRegistry`, el prompt del sistema v1 y el conjunto de evaluación (≥ 120 frases, precisión de intención ≥ 90 % en CI). En 8 puntos está en el límite; si al refinar crece, dividir en "orquestador y herramientas" y "conjunto de evaluación y CI".

---

## HU-CNV-05 · Ver la respuesta del asistente en tiempo real

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 8 | Hito 3 | `SPEC-05 · Req. 4` | RN-CNV-07 | — |

**Como** cliente, **quiero** ver la respuesta del asistente mientras se escribe y seguir recibiéndola aunque falle la conexión en vivo, **para** no quedarme esperando sin saber si el chat responde.

**Criterios de aceptación**
- `SPEC-05 · Req. 4 · Scenario: Envío y streaming normal` — el envío responde `202` y la respuesta llega por WebSocket con los eventos `token`, `bloque` y `fin`.
- `SPEC-05 · Req. 4 · Scenario: WebSocket no disponible` — tras 2 reintentos con backoff, el frontend consulta por *polling* cada 2 s.
- `SPEC-05 · Req. 4 · Scenario: Cliente con dos pestañas abiertas` — ambas pestañas reciben el streaming de la misma conversación.
- `SPEC-05 · Req. 4 · Scenario: Reconexión tras perder unos segundos` — el backend reenvía solo lo que falta del turno, sin duplicar texto.

**Prioridad:** Must: la arquitectura acordada transmite la respuesta del asistente por WebSocket.

**Notas:** RNF asociados: primer fragmento p95 ≤ 2 s y turno completo p95 ≤ 6 s.

---

## HU-CNV-06 · Referirme a productos mostrados antes

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 3 | Hito 3 | `SPEC-05 · Req. 5` | RN-CNV-08 | — |

**Como** cliente, **quiero** decir "el segundo" o "ese" refiriéndome a lo que el chat ya me mostró, **para** conversar de forma natural sin repetir nombres de productos.

**Criterios de aceptación**
- `SPEC-05 · Req. 5 · Scenario: Referencia ordinal a un carrusel` — "agrega el segundo en talla 42" se resuelve al producto y la variante del último carrusel.
- `SPEC-05 · Req. 5 · Scenario: Referencia sin contexto en esa conversación` — sin carrusel previo en esa conversación, el asistente pregunta a qué producto se refiere.

**Prioridad:** Must: el agregado al carrito por conversación (lineamiento del curso) depende de estas referencias.

---

## HU-CNV-07 · Ejecutar herramientas de forma segura (Habilitadora)

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 5 | Hito 3 | `SPEC-05 · Req. 6` | RN-CNV-09, RN-CNV-10, RN-CNV-11 | — |

**Como** cliente, **quiero** que el asistente nunca actúe con otra identidad, que me pida iniciar sesión cuando corresponde y que me pida confirmar las acciones con efecto económico, **para** confiar en que el chat no hará nada que yo no decidí.

**Criterios de aceptación**
- `SPEC-05 · Req. 6 · Scenario: Herramienta protegida sin sesión` — se devuelve `REQUIERE_SESION`, se muestra el login y se guarda la acción pendiente.
- `SPEC-05 · Req. 6 · Scenario: Argumentos inválidos del LLM` — se rechaza la llamada, se permite 1 reintento y luego se pide el dato al cliente.
- `SPEC-05 · Req. 6 · Scenario: Intento de suplantación` — se ignora cualquier `clienteId` de los argumentos y se usa el `sub` del token.

**Prioridad:** Must: es un control de seguridad del que dependen todas las herramientas protegidas.

**Notas:** habilitadora; el valor para el usuario es indirecto (seguridad y control).

---

## HU-CNV-08 · Recibir solo datos comerciales verídicos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 5 | Hito 3 | `SPEC-05 · Req. 7` | RN-CNV-12 | — |

**Como** cliente, **quiero** que los precios, el stock y los descuentos que veo sean los reales, **para** no tomar decisiones de compra con datos inventados por el asistente.

**Criterios de aceptación**
- `SPEC-05 · Req. 7 · Scenario: Pregunta de precio` — el precio sale de la tarjeta con datos de Productos; un precio distinto en el texto se corrige en el evento `fin`.
- `SPEC-05 · Req. 7 · Scenario: No hay datos para responder` — el asistente indica que no encontró el producto, sin inventar productos ni características.

**Prioridad:** Must: sin esta garantía, el total mostrado podría diferir del cobrado.

---

## HU-CNV-09 · Usar botones de acción rápida sin esperar al asistente

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 3 | Hito 3 | `SPEC-05 · Req. 8` | RN-CNV-13 | — |

**Como** cliente, **quiero** que los botones de las tarjetas y chips actúen de inmediato, **para** agregar o navegar sin depender de que el asistente interprete un texto.

**Criterios de aceptación**
- `SPEC-05 · Req. 8 · Scenario: Botón "Agregar" de una tarjeta` — la acción `AGREGAR_AL_CARRITO` se envía por REST, ejecuta el mismo caso de uso que la herramienta y responde con el bloque `CARRITO` sin abrir el WebSocket.

**Prioridad:** Must: todas las acciones directas de las demás épicas (tarjetas, carrito, chips) usan este mecanismo.

**Notas:** RNF: acciones directas p95 ≤ 1,5 s.

---

## HU-CNV-10 · Proteger mis datos sensibles y resistir instrucciones maliciosas

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 5 | Hito 3 | `SPEC-05 · Req. 9` | RN-CNV-14, RN-CNV-15 | — |

**Como** cliente, **quiero** que si escribo por error datos de mi tarjeta no queden guardados ni lleguen al asistente, y que nadie pueda manipular al chat para darme precios falsos, **para** comprar con seguridad.

**Criterios de aceptación**
- `SPEC-05 · Req. 9 · Scenario: El cliente escribe un número de tarjeta en el chat` — la secuencia se reemplaza por `[tarjeta oculta]` antes de persistirla o enviarla al LLM y se indica usar la pantalla de pago.
- `SPEC-05 · Req. 9 · Scenario: Instrucción maliciosa en el mensaje o en un dato` — el asistente no altera su comportamiento y los descuentos solo provienen de Productos.

**Prioridad:** Must: el README fija como principio que los datos sensibles nunca pasan por el LLM.

---

## HU-CNV-11 · Seguir comprando aunque el asistente falle

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 5 | Hito 3 | `SPEC-05 · Req. 10` | RN-CNV-16 | Proveedor LLM |

**Como** cliente, **quiero** un menú de opciones y búsqueda por palabra clave cuando el asistente no responde, **para** seguir comprando aunque el LLM esté caído.

**Criterios de aceptación**
- `SPEC-05 · Req. 10 · Scenario: El LLM no responde` — tras 15 s o un error, se responde por REST con el menú de acciones rápidas.
- `SPEC-05 · Req. 10 · Scenario: Búsqueda por palabra clave en modo degradado` — "zapatillas" ejecuta `buscar_productos {q}` con un intérprete simple.

**Prioridad:** Should: es resiliencia; el flujo de compra funciona mientras el LLM responde.

---

## HU-CNV-12 · Limitar el uso para proteger el servicio (Habilitadora)

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 3 | Hito 3 | `SPEC-05 · Req. 11` | RN-CNV-17, RN-CNV-18 | — |

**Como** equipo del canal, **quiero** limitar la frecuencia de mensajes y archivar conversaciones inactivas, **para** controlar el costo del LLM y mantener disponible el servicio para todos los clientes.

**Criterios de aceptación**
- `SPEC-05 · Req. 11 · Scenario: Exceso de mensajes` — más de 20 mensajes en 1 minuto reciben `429` y el aviso "Vas muy rápido, espera un momento".
- `SPEC-05 · Req. 11 · Scenario: Demasiadas conversaciones simultáneas` — con más de 50 conversaciones se archivan (sin borrar) las de más de 90 días sin actividad.

**Prioridad:** Should: protege costo y disponibilidad; puede llegar después de la demo de Hito 3 sin romper el flujo.

**Notas:** habilitadora.

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de `motor-conversacion/design.md`. Las tareas `[QA]` de escenarios se replican como una sub-issue por historia.

| Spec | Tarea → Historia |
|---|---|
| SPEC-05 | T1 `[FE]` AppShell y rutas → HU-CNV-01 · T2 `[FE]` Sidebar → HU-CNV-01 (relacionada: HU-CNV-02) · T3 `[FE]` HomePage → HU-CNV-03 · T4 `[FE]` ChatPage, useChat, MessageList → HU-CNV-05 · T5 `[FE]` Composer, QuickReplies, TypingIndicator, DegradedBanner → HU-CNV-04 (relacionada: HU-CNV-11) · T6 `[FE]` chatStore y puertos → HU-CNV-01 · T7 `[FE]` adaptadores Axios y WebSocket → HU-CNV-05 · T8 `[FE]` container.ts y apiConfig.ts → HU-CNV-01 · T9 `[BE]` modelos `conversacion` y `mensaje` → HU-CNV-01 · T10 `[BE]` `chatbot_router.py` → HU-CNV-01 · T11 `[BE]` `chatbot_ws_adapter.py` → HU-CNV-05 · T12 `[BE]` GestionarConversacionUseCase → HU-CNV-01 · T13 `[BE]` LLMProvider → HU-CNV-04 · T14 `[BE]` ToolRegistry, InterpretarYResponderUseCase, ActionDispatcher → HU-CNV-04 (relacionadas: HU-CNV-07, HU-CNV-09) · T15 `[BE]` SensitiveDataFilter y OutputValidator → HU-CNV-08 (relacionada: HU-CNV-10) · T16 `[BE]` DegradedMode y RateLimiter → HU-CNV-11 (relacionada: HU-CNV-12) · T17 `[BE]` prompt del sistema v1 → HU-CNV-04 · T18 `[QA]` conjunto de evaluación y umbral en CI → HU-CNV-04 · T19 `[QA]` escenarios → HU-CNV-01 a HU-CNV-12 |
