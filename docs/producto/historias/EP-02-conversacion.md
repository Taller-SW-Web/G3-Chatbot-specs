# EP-02 · Motor de conversación — Historias de usuario

> Specs: [SPEC-05](../../../openspec/specs/motor-conversacion/spec.md), [SPEC-23](../../../openspec/specs/adjuntos-imagenes-chat/spec.md) · Área `CNV` · 19 historias · 94 puntos
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
- `SPEC-05 · Req. 3 · Scenario: Mensaje con imágenes adjuntas` — el turno incluye las imágenes como contenido multimodal (base64, nunca URLs), con las mismas herramientas y el máximo de 5 iteraciones (detalle en HU-CNV-16).

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
- `SPEC-05 · Req. 4 · Scenario: Envío con imágenes adjuntas` — el envío con `adjuntoIds` responde `202` y la respuesta llega con los mismos eventos `token`, `bloque` y `fin` (detalle en HU-CNV-15).

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
- `SPEC-05 · Req. 9 · Scenario: El cliente escribe su documento de identidad en el chat` — el número precedido por "DNI", "RUC", etc. se reemplaza por `[documento oculto]` y se ofrece "Ir al pago"; otras secuencias de dígitos no se tocan.
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
- `SPEC-05 · Req. 10 · Scenario: El LLM no puede analizar imágenes` — con un modelo sin visión o un LLM que falla, se avisa que la imagen no pudo analizarse y el texto se procesa con normalidad (detalle en HU-CNV-18).

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

## HU-CNV-13 · Saber que converso con un asistente virtual y cómo se usan mis datos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Must | 3 | Hito 3 | `SPEC-05 · Req. 12` | RN-CNV-19, RN-CNV-20, RN-CNV-21 | — |

**Como** cliente (anónimo o autenticado), **quiero** saber desde el primer mensaje que hablo con un asistente virtual, ver un aviso claro sobre el uso de mis datos y recibir alternativas si pido una persona, **para** decidir con información qué comparto en el chat y no esperar una atención que el canal no ofrece.

**Criterios de aceptación**
- `SPEC-05 · Req. 12 · Scenario: Presentación en la primera respuesta de una conversación` — la primera respuesta de cada conversación incluye una presentación de una línea con `ASSISTANT_NAME` como asistente virtual, y no se repite en las siguientes.
- `SPEC-05 · Req. 12 · Scenario: Aviso de privacidad antes de la primera interacción` — el aviso breve con enlace a la política se muestra junto al campo de chat, sin bloquear la navegación ni usar casillas premarcadas.
- `SPEC-05 · Req. 12 · Scenario: El cliente pregunta si habla con una persona` — el asistente aclara que es un asistente virtual, sin invocar herramientas.
- `SPEC-05 · Req. 12 · Scenario: El cliente pide hablar con un agente humano` — se explica que no hay asesores humanos y se ofrecen "Crear un reclamo" y "Mis pedidos", sin prometer una derivación.

**Prioridad:** Must: la transparencia sobre el uso de IA y el aviso de privacidad son condiciones para operar el canal con datos personales (ver [`docs/conversacion/privacidad.md`](../../conversacion/privacidad.md)).

**Notas:** reutiliza las tareas T5 (`Composer`, donde vive el aviso) y T17 (prompt del sistema v1) de SPEC-05; la guía de tono y el microcopy están en [`docs/conversacion/persona-tono.md`](../../conversacion/persona-tono.md). El texto de la política completa y el canal de contacto de la tienda están pendientes (ver [preguntas abiertas](../../conversacion/README.md#preguntas-abiertas)). **Al implementar:** confirmar si la tienda tiene un correo de atención (probable, sin verificar) y configurarlo como canal de contacto.

---

## HU-CNV-14 · Adjuntar imágenes a mi mensaje y saber cómo se usan

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 5 | Hito 4 | `SPEC-23 · Req. 1–2` | RN-CNV-22, RN-CNV-23 | — |

**Como** cliente (anónimo o autenticado), **quiero** adjuntar hasta 3 imágenes a mi mensaje, verlas antes de enviar y saber que se envían a un asistente con IA, **para** mostrarle lo que busco o lo que me pasa sin describirlo con palabras.

**Criterios de aceptación**
- `SPEC-23 · Req. 1 · Scenario: Adjuntar imágenes válidas` — se muestra una miniatura por imagen con su progreso de carga y un botón "Quitar", y el envío se habilita al terminar de subirse.
- `SPEC-23 · Req. 1 · Scenario: Más de 3 imágenes` — el frontend no sube la cuarta y avisa que el máximo es de 3 por mensaje.
- `SPEC-23 · Req. 1 · Scenario: Tipo o tamaño no permitido detectado en el cliente` — un archivo que no es JPG, PNG o WebP, o de más de 5 MB, se rechaza antes de subirlo con un mensaje claro.
- `SPEC-23 · Req. 1 · Scenario: Quitar una imagen antes de enviar` — la imagen desaparece del compositor y el backend elimina el adjunto pendiente.
- `SPEC-23 · Req. 1 · Scenario: Mensaje solo con imagen` — el envío se permite sin texto cuando hay al menos un adjunto.
- `SPEC-23 · Req. 2 · Scenario: Primera carga en el dispositivo` — el aviso de privacidad con enlace a la política aparece antes de abrir el selector de archivos.
- `SPEC-23 · Req. 2 · Scenario: Cargas posteriores` — tras confirmar el aviso, el selector se abre directamente.
- `SPEC-23 · Req. 2 · Scenario: El cliente cierra el aviso sin confirmar` — no se abre el selector y el envío de texto no se ve afectado.

**Prioridad:** Should: es una extensión posterior al núcleo del Hito 3; el flujo de compra por texto funciona sin ella.

**Notas:** reutiliza `Composer` (HU-CNV-04) y el aviso de privacidad de HU-CNV-13. Cubre `AttachmentButton`, `AttachmentPreviewList`, `validateImageFile` e `ImagePrivacyNotice`. La confirmación del aviso se recuerda por dispositivo (LocalStorage, con degradación si no está disponible).

---

## HU-CNV-15 · Subir y enviar mis imágenes de forma segura

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 8 | Hito 4 | `SPEC-23 · Req. 3–4` | RN-CNV-22, RN-CNV-26, RN-CNV-28 | Supabase Storage (bucket privado) |

**Como** cliente (anónimo o autenticado), **quiero** que mis imágenes se validen, se limpien de metadatos y se guarden de forma privada, y que viajen con mi mensaje, **para** compartir fotos sin exponer mi ubicación ni mis archivos.

**Criterios de aceptación**
- `SPEC-23 · Req. 3 · Scenario: Carga exitosa` — el backend verifica el tipo por firma binaria, elimina EXIF y ubicación, guarda imagen y miniatura y responde `201` con el `adjuntoId`.
- `SPEC-23 · Req. 3 · Scenario: Archivo cuyo contenido no coincide con su extensión` — se rechaza con `400 ADJUNTO_INVALIDO` y no se guarda nada.
- `SPEC-23 · Req. 3 · Scenario: Imagen que excede el tamaño o las dimensiones` — se rechaza con `400 ADJUNTO_INVALIDO`.
- `SPEC-23 · Req. 3 · Scenario: Conversación de otro cliente` — se responde `404 RECURSO_NO_ENCONTRADO` y no se guarda nada.
- `SPEC-23 · Req. 3 · Scenario: Cliente anónimo` — el visitante con `chat_sid` sube imágenes con las mismas reglas.
- `SPEC-23 · Req. 3 · Scenario: Falla el almacenamiento` — se responde `503`, no se crea el adjunto y la conversación de texto sigue funcionando.
- `SPEC-23 · Req. 4 · Scenario: Mensaje con texto y dos imágenes` — el mensaje liga los adjuntos, responde `202 {mensajeId}` y la respuesta llega por WebSocket.
- `SPEC-23 · Req. 4 · Scenario: Adjunto que no corresponde` — se responde `404` sin guardar el mensaje ni consumir el resto de los adjuntos.
- `SPEC-23 · Req. 4 · Scenario: Más de 3 adjuntos` — se responde `422 LIMITE_ADJUNTOS`.
- `SPEC-23 · Req. 4 · Scenario: Mensaje sin texto ni adjuntos` — se responde `400 VALIDACION`.
- `SPEC-23 · Req. 4 · Scenario: Adjuntos que el cliente no envía` — a las 24 horas el job de limpieza elimina el adjunto y sus archivos.

**Prioridad:** Should: sin esta base no hay imágenes en el chat, pero es una extensión posterior al núcleo del Hito 3.

**Notas:** incluye `AttachmentStorage`, `SupabaseAttachmentStorage`, `ImageProcessor`, `AdjuntoService` y la tabla `adjunto`. En 8 puntos está en el límite; si al refinar crece, dividir en "almacenamiento y procesamiento de imagen" y "carga y envío con adjuntos".

---

## HU-CNV-16 · Que el asistente entienda mis imágenes y me ayude a buscar productos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 8 | Hito 4 | `SPEC-23 · Req. 5–6` | RN-CNV-24, RN-CNV-25 | Proveedor LLM (`gpt-6-luna`, visión sin verificar ⚠️); PRO `GET /productos` 🟡 |

**Como** cliente, **quiero** que el asistente vea mis imágenes y las use para responder o buscar productos parecidos, **para** encontrar lo que quiero mostrándolo en vez de describirlo.

**Criterios de aceptación**
- `SPEC-23 · Req. 5 · Scenario: Descripción de una imagen` — el backend envía la imagen en base64 al LLM y el asistente describe lo que ve sin afirmar precios ni stock.
- `SPEC-23 · Req. 5 · Scenario: Las imágenes comparten la ventana de contexto` — las imágenes de mensajes fuera de los últimos 12 ya no se envían al LLM, pero su miniatura sigue visible.
- `SPEC-23 · Req. 5 · Scenario: Turno con imágenes de mensajes recientes` — una imagen dentro de la ventana se vuelve a enviar dentro del máximo de imágenes por turno.
- `SPEC-23 · Req. 5 · Scenario: Texto dentro de la imagen` — el texto de la imagen se trata como dato y no altera el comportamiento del asistente.
- `SPEC-23 · Req. 5 · Scenario: La imagen muestra datos sensibles` — el asistente no transcribe los datos y recuerda que se ingresan solo en la pantalla de pago.
- `SPEC-23 · Req. 6 · Scenario: Buscar algo parecido a una foto` — el LLM traduce la imagen a criterios de texto e invoca `buscar_productos`, con una aclaración de los criterios usados.
- `SPEC-23 · Req. 6 · Scenario: Los resultados no prometen parecido exacto` — el texto indica los criterios interpretados, sin afirmar que sean idénticos a la foto.
- `SPEC-23 · Req. 6 · Scenario: La imagen no permite deducir criterios` — el asistente hace una sola pregunta aclaratoria sin invocar herramientas.
- `SPEC-23 · Req. 6 · Scenario: Imagen sin relación con la tienda` — se aplica la regla de fuera de dominio de SPEC-05.

**Prioridad:** Should: aporta valor diferencial, pero depende de que el modelo elegido admita visión (pregunta abierta en [`alcance.md`](../alcance.md#preguntas-abiertas)).

**Notas:** incluye `LLMProvider` con partes de contenido, la lectura de imágenes en `InterpretarYResponderUseCase` y el registro de tokens y costo por turno. No hay búsqueda por similitud visual: solo criterios de texto sobre SPEC-06. La validación con el modelo real (soporte de visión y costo por imagen) es una tarea `[INT]` previa.

---

## HU-CNV-17 · Ver mis imágenes en el historial

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 5 | Hito 4 | `SPEC-23 · Req. 7` | RN-CNV-26 | Supabase Storage (URLs firmadas) |

**Como** cliente, **quiero** ver las imágenes que envié como miniaturas al retomar una conversación y ampliarlas, **para** recordar de qué hablábamos sin que mis imágenes queden expuestas públicamente.

**Criterios de aceptación**
- `SPEC-23 · Req. 7 · Scenario: Cargar el historial con imágenes` — cada mensaje incluye sus adjuntos con URLs firmadas de corta vida y el frontend muestra las miniaturas.
- `SPEC-23 · Req. 7 · Scenario: La URL firmada expiró` — el frontend pide una URL nueva, reintenta una vez y, si falla, muestra "Imagen no disponible".
- `SPEC-23 · Req. 7 · Scenario: Ampliar una imagen` — al tocar la miniatura se abre la imagen en una vista ampliada dentro de la aplicación.
- `SPEC-23 · Req. 7 · Scenario: Acceso a la imagen de otro cliente` — se responde `404` y no se emite ninguna URL firmada.
- `SPEC-23 · Req. 7 · Scenario: Recibir el mensaje en tiempo real` — el frontend usa la miniatura local ya cargada mientras el historial no se recarga.

**Prioridad:** Should: mejora la experiencia, pero el análisis de la imagen no depende de ella.

**Notas:** incluye `MessageAttachments`, `ImageViewer` y `GET /chat/adjuntos/{adjuntoId}`. El TTL de las URLs firmadas es de 5 minutos por defecto.

---

## HU-CNV-18 · Seguir conversando aunque falle el análisis de imágenes

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 3 | Hito 4 | `SPEC-23 · Req. 8` | RN-CNV-27 | Proveedor LLM |

**Como** cliente, **quiero** que si el asistente no puede analizar mi imagen me lo diga y siga atendiendo mi texto, **para** no quedarme bloqueado por una falla que no controlo.

**Criterios de aceptación**
- `SPEC-23 · Req. 8 · Scenario: El modelo configurado no admite imágenes` — se responde que la imagen no pudo analizarse y el texto del mensaje se procesa sin las imágenes.
- `SPEC-23 · Req. 8 · Scenario: El LLM falla o excede el tiempo con una imagen` — se aplica el modo degradado con el aviso y el mensaje y sus miniaturas permanecen en el historial.
- `SPEC-23 · Req. 8 · Scenario: No se puede leer la imagen del almacenamiento` — se omite esa imagen, se avisa y se continúa con el texto y las demás imágenes.
- `SPEC-23 · Req. 8 · Scenario: El flujo de texto no se ve afectado` — los mensajes solo de texto se procesan con normalidad.

**Prioridad:** Should: es resiliencia, en la misma línea que HU-CNV-11.

**Notas:** extiende `DegradedMode` (HU-CNV-11) con el indicador `LLM_VISION_ENABLED`.

---

## HU-CNV-19 · Limitar el uso de imágenes y conservar sus referencias (Habilitadora)

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-02 | Should | 5 | Hito 4 | `SPEC-23 · Req. 9–10` | RN-CNV-28, RN-CNV-29 | — |

**Como** equipo del canal, **quiero** limitar la carga de imágenes y conservar u eliminar de forma coherente sus registros y archivos, **para** controlar el costo del LLM y del almacenamiento y evitar archivos huérfanos.

**Criterios de aceptación**
- `SPEC-23 · Req. 9 · Scenario: Exceso de cargas` — más de 10 imágenes en 1 minuto reciben `429 DEMASIADAS_SOLICITUDES`.
- `SPEC-23 · Req. 9 · Scenario: El mensaje con imágenes cuenta como un mensaje` — el mensaje con imágenes se suma al límite de 20 mensajes por minuto de SPEC-05.
- `SPEC-23 · Req. 9 · Scenario: Adjuntos pendientes acumulados` — con 10 adjuntos pendientes en una conversación se responde `422 LIMITE_ADJUNTOS`.
- `SPEC-23 · Req. 10 · Scenario: Conversación archivada por inactividad` — el archivado automático no borra los adjuntos.
- `SPEC-23 · Req. 10 · Scenario: Se borra una conversación` — los registros se eliminan en cascada y un job elimina los archivos huérfanos con reintento.
- `SPEC-23 · Req. 10 · Scenario: Los adjuntos no se copian a Ventas` — las imágenes del chat no se reutilizan como evidencia de devolución.

**Prioridad:** Should: protege costo y almacenamiento; puede llegar después de la carga y el análisis.

**Notas:** habilitadora. El plazo de retención de los adjuntos está pendiente (pregunta abierta en [`alcance.md`](../alcance.md#preguntas-abiertas)). Incluye el job de limpieza de pendientes y de huérfanos.

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" del `design.md` de cada spec (`motor-conversacion` y `adjuntos-imagenes-chat`). Las tareas `[QA]` de escenarios se replican como una sub-issue por historia.

| Spec | Tarea → Historia |
|---|---|
| SPEC-05 | T1 `[FE]` AppShell y rutas → HU-CNV-01 · T2 `[FE]` Sidebar → HU-CNV-01 (relacionada: HU-CNV-02) · T3 `[FE]` HomePage → HU-CNV-03 · T4 `[FE]` ChatPage, useChat, MessageList → HU-CNV-05 · T5 `[FE]` Composer, QuickReplies, TypingIndicator, DegradedBanner → HU-CNV-04 (relacionadas: HU-CNV-11, HU-CNV-13) · T6 `[FE]` chatStore y puertos → HU-CNV-01 · T7 `[FE]` adaptadores Axios y WebSocket → HU-CNV-05 · T8 `[FE]` container.ts y apiConfig.ts → HU-CNV-01 · T9 `[BE]` modelos `conversacion` y `mensaje` → HU-CNV-01 · T10 `[BE]` `chatbot_router.py` → HU-CNV-01 · T11 `[BE]` `chatbot_ws_adapter.py` → HU-CNV-05 · T12 `[BE]` GestionarConversacionUseCase → HU-CNV-01 · T13 `[BE]` LLMProvider → HU-CNV-04 · T14 `[BE]` ToolRegistry, InterpretarYResponderUseCase, ActionDispatcher → HU-CNV-04 (relacionadas: HU-CNV-07, HU-CNV-09) · T15 `[BE]` SensitiveDataFilter y OutputValidator → HU-CNV-08 (relacionada: HU-CNV-10) · T16 `[BE]` DegradedMode y RateLimiter → HU-CNV-11 (relacionada: HU-CNV-12) · T17 `[BE]` prompt del sistema v1 → HU-CNV-04 (relacionada: HU-CNV-13) · T18 `[QA]` conjunto de evaluación y umbral en CI → HU-CNV-04 · T19 `[QA]` escenarios → HU-CNV-01 a HU-CNV-13 |
| SPEC-23 | T1 `[BE]` `AttachmentStorage` y `SupabaseAttachmentStorage` → HU-CNV-15 · T2 `[BE]` `ImageProcessor` → HU-CNV-15 · T3 `[BE]` modelo `adjunto` y migración → HU-CNV-15 · T4 `[BE]` `AdjuntoService` y `POST`/`DELETE` de adjuntos → HU-CNV-15 · T5 `[BE]` `GET /chat/adjuntos/{adjuntoId}` y URLs firmadas → HU-CNV-17 · T6 `[BE]` `adjuntoIds` en el envío de mensajes → HU-CNV-15 · T7 `[BE]` `LLMProvider` multimodal → HU-CNV-16 · T8 `[BE]` `InterpretarYResponderUseCase` con imágenes → HU-CNV-16 · T9 `[BE]` `DegradedMode` y `RateLimiter` → HU-CNV-18 (relacionada: HU-CNV-19) · T10 `[BE]` job de limpieza → HU-CNV-19 · T11 `[BE]` registro por turno de imágenes, tokens y costo → HU-CNV-16 · T12 `[FE]` `AttachmentButton`, `AttachmentPreviewList` y `validateImageFile` → HU-CNV-14 · T13 `[FE]` `ImagePrivacyNotice` → HU-CNV-14 · T14 `[FE]` `MessageAttachments` e `ImageViewer` → HU-CNV-17 · T15 `[FE]` `ChatbotApiPort`, adaptador Axios y `chatStore` → HU-CNV-14 (relacionada: HU-CNV-17) · T16 `[INT]` validar visión y costo con `gpt-6-luna` → HU-CNV-16 · T17 `[INT]` bucket privado de Supabase Storage → HU-CNV-15 · T18 `[QA]` escenarios → HU-CNV-14 a HU-CNV-19 · T19 `[QA]` seguridad de adjuntos → HU-CNV-15 (relacionadas: HU-CNV-16, HU-CNV-17) · T20 `[QA]` modo degradado de imágenes → HU-CNV-18 |
