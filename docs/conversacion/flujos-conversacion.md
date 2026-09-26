# Flujos de conversación

> Diagramas del diseño conversacional sobre las specs de [`openspec/specs/`](../../openspec/specs/). Resumen visual: el detalle normativo (textos, códigos, límites) está en cada spec citada. Los diagramas usan Mermaid y se renderizan en GitHub.

## (a) Máquina de estados global de la conversación

Estados de la **experiencia** del cliente, no de la tabla `conversacion` (cuyos estados son `ACTIVA`, `ARCHIVADA` y `CERRADA`, ver [`modelo-datos.md`](../modelo-datos.md)). "Degradado" y "Limitado" se superponen a la sesión: al salir de ellos se vuelve al estado de sesión anterior.

Fuentes: SPEC-05 · Req. 1, 2, 4, 10, 11, 12; SPEC-03 · Req. 1, 3, 5, 6.

```mermaid
stateDiagram-v2
    direction LR
    state "Inicio (HomePage + aviso de privacidad)" as Inicio
    state "Conversando anónimo (chat_sid)" as Anonimo
    state "Conversando autenticado (rol CLIENTE)" as Autenticado
    state "Esperando login (accionPendiente guardada)" as EsperaLogin
    state "Modo degradado (sin LLM o sin WebSocket)" as Degradado
    state "Limitado (429)" as Limitado

    [*] --> Inicio
    Inicio --> Anonimo: primer mensaje sin sesión
    Inicio --> Autenticado: primer mensaje con sesión
    Anonimo --> EsperaLogin: herramienta protegida devuelve REQUIERE_SESION
    EsperaLogin --> Autenticado: login OK, se ejecuta la acción pendiente
    EsperaLogin --> Anonimo: cancela el login
    Anonimo --> Autenticado: login voluntario, se fusionan carrito y conversaciones
    Autenticado --> Anonimo: logout o refresh inválido, carrito vacío
    Anonimo --> Degradado: LLM mayor a 15 s o error
    Autenticado --> Degradado: LLM mayor a 15 s o error
    Degradado --> Anonimo: LLM responde de nuevo
    Degradado --> Autenticado: LLM responde de nuevo
    Anonimo --> Limitado: más de 20 mensajes por minuto
    Autenticado --> Limitado: más de 20 mensajes por minuto
    Limitado --> Anonimo: pasa la ventana
    Limitado --> Autenticado: pasa la ventana
```

Notas:
- La primera respuesta del asistente en cada conversación incluye la presentación como asistente virtual (SPEC-05 · Req. 12).
- Si el WebSocket falla, la respuesta llega por *polling* cada 2 s tras 2 reintentos (SPEC-05 · Req. 4); eso no cambia el estado de sesión.
- Si el LLM falla, las acciones directas por botón siguen funcionando porque no pasan por el LLM (SPEC-05 · Req. 8).

## (b) Descubrimiento → carrito

Fuentes: SPEC-05 · Req. 3, 5; SPEC-06 · Req. 1–5; SPEC-07 · Req. 1–3; SPEC-09 · Req. 1–4; SPEC-10 · Req. 1, 3; SPEC-11 · Req. 1.

```mermaid
flowchart TD
    A["Mensaje del cliente"] --> B{"¿Intención clara?"}
    B -- "No" --> C["Una pregunta aclaratoria + acciones rápidas<br/>(sin herramientas)"]
    C --> A
    B -- "Busca un producto" --> D["buscar_productos<br/>filtros normalizados"]
    B -- "Describe una necesidad" --> E{"¿Falta información clave?"}
    E -- "Sí, menos de 2 preguntas hechas" --> F["Pregunta con chips"]
    F --> A
    E -- "No, o ya se hicieron 2" --> G["recomendar_productos<br/>3 a 5 con stock y razón"]
    D --> H{"¿Productos responde en 4 s?"}
    H -- "No" --> H1["'No puedo consultar el catálogo en este momento…'<br/>+ Reintentar"]
    H -- "Sí, sin resultados" --> H2["'No encontré productos con esos filtros'<br/>+ relajar filtro"]
    H -- "Sí" --> I["CARRUSEL_PRODUCTOS<br/>máx. 10 + Ver más"]
    G --> I
    I --> J{"Cliente elige"}
    J -- "Ver detalle / 'el tercero'" --> K["ver_detalle_producto<br/>DETALLE_PRODUCTO"]
    J -- "Agregar / 'agrega el segundo en 42'" --> L{"¿Variante completa?"}
    K --> L
    L -- "Falta un atributo" --> M["Pregunta solo ese atributo<br/>SELECTOR_VARIANTE o chips"]
    M --> L
    L -- "Sí" --> N{"Stock en vivo en 3 s"}
    N -- "Sin respuesta" --> N1["503 · 'No puedo confirmar el stock ahora…'<br/>+ Reintentar"]
    N -- "Agotado" --> N2["Otras variantes o hasta 3 similares"]
    N -- "Parcial" --> N3["409 STOCK_INSUFICIENTE<br/>'¿Agrego N más?'"]
    N -- "Suficiente" --> O{"¿Límites 10 por línea / 20 líneas?"}
    N3 -- "Sí, agregar" --> O
    O -- "Excede" --> O1["422 LIMITE_CANTIDAD o tope de 20 líneas"]
    O -- "OK" --> P["Línea creada o sumada<br/>CARRITO resumido + Ver carrito / Seguir comprando / Pagar"]
    P --> Q{"¿Hay complementos y no se silenciaron?"}
    Q -- "Sí" --> R["'¿Te interesa complementarlo?'<br/>mini carrusel de hasta 3"]
    Q -- "No" --> S(["Sigue comprando o paga"])
    R --> S
```

## (c) Checkout y pago

El orden de precondiciones es el de SPEC-14 · Req. 1: sesión → celular verificado → carrito válido → dirección y cotización → cupón vigente. Sesión, celular, carrito y cupón se resuelven en el chat; **la dirección y la cotización se resuelven en `CheckoutPage`**, nunca por texto.

Fuentes: SPEC-14 · Req. 1–6; SPEC-03 · Req. 3; SPEC-04 · Req. 1–2; SPEC-10 · Req. 2; SPEC-11 · Req. 3; SPEC-12 · Req. 1–5; SPEC-13 · Req. 4; SPEC-15 · Req. 1–3; SPEC-16 · Req. 3.

```mermaid
flowchart TD
    A["'quiero pagar' o botón Pagar<br/>iniciar_checkout"] --> B{"1. ¿Sesión CLIENTE?"}
    B -- "No" --> B1["REQUIERE_SESION<br/>login o registro<br/>accionPendiente = INICIAR_CHECKOUT"]
    B1 --> B
    B -- "Sí" --> C{"2. ¿Celular verificado?"}
    C -- "No" --> C1["403 CELULAR_NO_VERIFICADO<br/>FORMULARIO/OTP_CELULAR<br/>6 dígitos, 5 min, 3 intentos"]
    C1 --> C
    C -- "Sí" --> D{"3. ¿Carrito válido?<br/>revalidación masiva de stock"}
    D -- "Vacío o sin líneas válidas" --> D1["'Tu carrito no tiene productos disponibles para comprar'"]
    D -- "Cambió el stock" --> D2["409 CARRITO_DESACTUALIZADO<br/>Ajustar o Quitar"]
    D2 --> D
    D -- "OK" --> E["Navega a CheckoutPage"]
    E --> F{"4. ¿Dirección y cotización vigentes?<br/>(en CheckoutPage)"}
    F -- "Falta dirección" --> F1["Sección de dirección enfocada<br/>campos libres + documento"]
    F1 --> F2["POST /envio/cotizar"]
    F2 --> F3{"Resultado de Despacho"}
    F3 -- "Sin cobertura" --> F1
    F3 -- "Sin respuesta en 4 s" --> F4["'No pude calcular el envío ahora'<br/>pago deshabilitado"]
    F3 -- "Con cobertura" --> G
    F -- "Sí" --> G{"5. ¿Cupón vigente?"}
    G -- "Dejó de ser válido" --> G1["Se retira con aviso<br/>nuevo total"]
    G1 --> H
    G -- "Sí o sin cupón" --> H["Resumen + 'Confirmar y pagar S/ X'"]
    H --> I["POST /checkout con Idempotency-Key<br/>revalida todo"]
    I -- "Total cambió" --> I1["409 CARRITO_DESACTUALIZADO<br/>nuevo resumen"]
    I1 --> H
    I -- "Ventas sin respuesta en 5 s" --> I2["503 · sin cobro"]
    I -- "OK" --> J["Checkout PENDIENTE_PAGO, expira en 15 min<br/>Pedido CREADO en Ventas<br/>FORMULARIO/PAGO"]
    J --> K{"Pagar: introspección de sesión"}
    K -- "activo false" --> K1["401 · cierra sesión"]
    K -- "Sin respuesta en 3 s" --> K2["503 · no se cobra"]
    K -- "activo true" --> L{"¿Más de 15 min?"}
    L -- "Sí" --> L1["410 CHECKOUT_EXPIRADO<br/>anulación · carrito ACTIVO<br/>Volver a intentar"]
    L -- "No" --> M{"Simulador"}
    M -- "APROBADO" --> N["PAGO_APROBADO · outbox notifica a Ventas<br/>CONFIRMACION_PEDIDO · correo en cola"]
    M -- "RECHAZADO o ERROR" --> O{"¿Intento 3?"}
    O -- "No" --> O1["402 PAGO_RECHAZADO<br/>intentosRestantes · formulario limpio"]
    O1 --> K
    O -- "Sí" --> O2["FALLIDO · anulación PAGO_NO_COMPLETADO<br/>carrito ACTIVO<br/>'No pudimos procesar el pago. Tu carrito sigue guardado'"]
```

## (d) Postventa: estado, seguimiento, reclamo y devolución

Fuentes: SPEC-17 · Req. 1–4; SPEC-18 · Req. 1–4; SPEC-19 · Req. 1–4; SPEC-20 · Req. 1–3; SPEC-21 · Req. 1–5; SPEC-22 · Req. 1–4.

```mermaid
flowchart TD
    A["Cliente con sesión pregunta por un pedido"] --> B{"¿Qué quiere?"}
    B -- "Estado / ¿dónde está?" --> C{"¿Cuántos pedidos en curso?"}
    C -- "Uno" --> C1["consultar_pedido<br/>ESTADO_PEDIDO"]
    C -- "Varios" --> C2["LISTA_PEDIDOS para elegir"]
    C -- "Ninguno" --> C3["'Aún no tienes pedidos' + Ver ofertas"]
    C2 --> C1
    C1 --> D{"¿DESPACHADO o ENTREGADO?"}
    D -- "No" --> D1["Línea de tiempo de Ventas"]
    D -- "Sí" --> E["consultar_seguimiento"]
    E -- "Despacho sin respuesta en 4 s" --> E1["Estado según Ventas<br/>'El detalle del envío no está disponible ahora'<br/>+ Reintentar"]
    E -- "OK" --> E2["Etiqueta, fecha programada, distrito, hitos<br/>(lista blanca, sin GPS ni repartidor)"]
    E2 -- "FALLIDO o DEVUELTO_A_ORIGEN" --> R
    B -- "Reportar un problema" --> R["preparar_reclamo"]
    R --> R1{"¿Reclamo abierto con mismo pedido y motivo?"}
    R1 -- "Sí" --> R2["Muestra código y estado<br/>Ver estado / Registrar uno nuevo de todas formas"]
    R1 -- "No" --> R3["FORMULARIO/RECLAMO prellenado"]
    R2 -- "Registrar igual" --> R3
    R3 -- "Enviar reclamo" --> R4{"Ventas"}
    R4 -- "201" --> R5["CONSTANCIA_RECLAMO<br/>plazo de 15 días hábiles (fechaLimiteSLA)"]
    R4 -- "Sin respuesta" --> R6["Borrador guardado 24 h + Reintentar"]
    R3 -- "Cancelar" --> R7["Borrador descartado"]
    B -- "Cambio o devolución" --> V["preparar_devolucion"]
    V --> V1{"¿ENTREGADO y dentro de 7 días naturales?"}
    V1 -- "No entregado" --> V2["Solo después de la entrega<br/>+ Reportar un problema con el envío"]
    V1 -- "Plazo vencido" --> V3["'El plazo de 7 días… ya venció'<br/>+ Crear un reclamo"]
    V3 --> R
    V1 -- "Sí" --> V4{"¿Solicitud abierta para el pedido?"}
    V4 -- "Sí" --> V5["Muestra código y estado<br/>no crea otra sin confirmación"]
    V4 -- "No" --> V6["FORMULARIO/DEVOLUCION<br/>línea, tipo, motivo, variante deseada<br/>evidencia obligatoria si es defectuoso"]
    V6 -- "Enviar solicitud" --> V7["CONSTANCIA_DEVOLUCION"]
    B -- "Consultar reclamo o devolución" --> W["consultar_reclamo / consultar_devolucion<br/>respuesta y fundamento textuales de Ventas"]
```

## (e) Secuencia de un turno de texto

Un mensaje de texto viaja por REST y la respuesta vuelve por WebSocket (SPEC-05 · Req. 4). Las acciones con efecto no viajan por WebSocket (README §1.3). Las acciones directas de botones siguen otro camino: REST → `ActionDispatcher` → caso de uso, sin LLM (SPEC-05 · Req. 8).

Fuentes: SPEC-05 · Req. 3, 4, 6, 7, 9 y `motor-conversacion/design.md`; README §1.3.

> 🧩 Con imágenes adjuntas (SPEC-23) el envío lleva `adjuntoIds` y, al armar el turno, `InterpretarYResponderUseCase` lee las imágenes de los últimos 12 mensajes desde `AttachmentStorage` y las envía a `LLMProvider` en base64 (máx. 6 por turno). Si el modelo no admite imágenes o falla, `DegradedMode` avisa que la imagen no pudo analizarse y el texto se procesa igual.

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend (ChatPage)
    participant REST as chatbot_router.py
    participant UC as InterpretarYResponderUseCase
    participant F as SensitiveDataFilter
    participant LLM as LLMProvider
    participant TR as ToolRegistry y caso de uso
    participant MOD as Módulo externo
    participant WS as chatbot_ws_adapter.py

    FE->>REST: POST /chat/conversaciones/{id}/mensajes con texto
    REST->>REST: RateLimiter (más de 20 por minuto responde 429)
    REST-->>FE: 202 con mensajeId
    REST->>UC: procesar turno
    UC->>F: redactar tarjeta, OTP y contraseña
    F-->>UC: texto seguro, persistido en mensaje
    UC->>LLM: prompt del sistema, resumen, últimos 12 mensajes y herramientas
    LLM-->>UC: tool call con argumentos
    UC->>TR: validar con Pydantic, sesión y confirmación, identidad desde el token
    TR->>MOD: llamada HTTP con timeout
    MOD-->>TR: datos (tratados como datos, no como instrucciones)
    TR-->>UC: resultado truncado y bloque estructurado
    UC->>LLM: resultado de la herramienta
    LLM-->>UC: texto en streaming
    UC->>WS: eventos token
    WS-->>FE: token, token, token
    UC->>WS: evento bloque
    WS-->>FE: bloque (CARRUSEL_PRODUCTOS, CARRITO y otros)
    UC->>UC: OutputValidator compara precios del texto con los resultados
    UC->>WS: evento fin con mensajeId y correcciones
    WS-->>FE: fin
    Note over UC,LLM: Si el LLM no responde en 15 s, DegradedMode responde por REST con el menú
    Note over FE,WS: Si el WebSocket no conecta, 2 reintentos y luego polling cada 2 s
```
