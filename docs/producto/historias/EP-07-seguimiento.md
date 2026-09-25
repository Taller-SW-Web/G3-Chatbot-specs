# EP-07 · Seguimiento de pedidos — Historias de usuario

> Specs: [SPEC-17](../../../openspec/specs/consulta-estado-pedido/spec.md), [SPEC-18](../../../openspec/specs/seguimiento-despacho/spec.md) · Área `SGT` · 8 historias · 28 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.

---

## HU-SGT-01 · Encontrar mi pedido rápidamente

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Must | 5 | Hito 5–6 | `SPEC-17 · Req. 1` | RN-SGT-02, RN-SGT-03, RN-SGT-04, RN-SGT-05 | Ventas ✅ (A8) |

**Como** cliente autenticado, **quiero** preguntar "¿dónde está mi pedido?" o abrir "Mis pedidos" y llegar al pedido correcto, **para** consultar su estado sin buscar números.

**Criterios de aceptación**
- `SPEC-17 · Req. 1 · Scenario: Un solo pedido en curso` — se muestra directamente `ESTADO_PEDIDO` del pedido en curso.
- `SPEC-17 · Req. 1 · Scenario: Varios pedidos en curso` — se muestra `LISTA_PEDIDOS` con número, fecha, total, estado y canal para elegir.
- `SPEC-17 · Req. 1 · Scenario: Consulta por número` — se consulta el pedido indicado y se muestra si pertenece al cliente.
- `SPEC-17 · Req. 1 · Scenario: Pedido de otro cliente o inexistente` — ambos casos reciben "No encontré ese pedido en tu cuenta".
- `SPEC-17 · Req. 1 · Scenario: Cliente sin pedidos` — se responde "Aún no tienes pedidos" con "Ver ofertas".

**Prioridad:** Must: el curso exige la consulta del estado de un pedido.

**Notas:** incluye `OrderHistoryPage` con las pestañas "En proceso" y "Entregados" (la pestaña "Reembolsos" es HU-DEV-06) y la entrada "Mis pedidos" del menú.

---

## HU-SGT-02 · Ver el estado y la línea de tiempo de mi pedido

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Must | 5 | Hito 5–6 | `SPEC-17 · Req. 2` | RN-SGT-01, RN-SGT-06, RN-SGT-07 | Ventas ✅; Despacho 🟡 (A11, enriquecimiento) |

**Como** cliente, **quiero** ver el estado actual de mi pedido en palabras claras y su línea de tiempo, **para** saber qué pasó y qué falta.

**Criterios de aceptación**
- `SPEC-17 · Req. 2 · Scenario: Pedido en preparación` — el paso actual aparece resaltado, los anteriores completados y los siguientes en gris.
- `SPEC-17 · Req. 2 · Scenario: Pedido despachado` — el estado se completa con la etiqueta y los hitos de Despacho.
- `SPEC-17 · Req. 2 · Scenario: Pedido anulado` — se muestra "Anulado el {fecha}" con el motivo general y, si hubo pago, el aviso de reembolso.

**Prioridad:** Must: es el núcleo de la consulta de estado.

**Notas:** el escenario "Pedido despachado" depende de HU-SGT-05; sin A11 se prueba contra mock.

---

## HU-SGT-03 · Obtener respuestas directas sobre mi pedido

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Should | 3 | Hito 5–6 | `SPEC-17 · Req. 3` | RN-SGT-08 | Ventas ✅; Despacho 🟡 (A11) |

**Como** cliente, **quiero** preguntar "¿ya llegó?" o "¿cuándo llega?" y recibir una respuesta concreta, **para** no tener que interpretar la línea de tiempo.

**Criterios de aceptación**
- `SPEC-17 · Req. 3 · Scenario: "¿Ya llegó?"` — un pedido `ENTREGADO` responde con fecha y hora de entrega y ofrece "Reportar".
- `SPEC-17 · Req. 3 · Scenario: "¿Cuándo llega?"` — se responde con la fecha estimada del plazo cotizado o la fecha programada de Despacho.

**Prioridad:** Should: mejora la conversación; la información ya está en la línea de tiempo.

---

## HU-SGT-04 · Saber cuándo no se puede consultar mi pedido

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Must | 2 | Hito 5–6 | `SPEC-17 · Req. 4` | RN-SGT-09 | Ventas ✅; Despacho 🟡 |

**Como** cliente, **quiero** que el chat me diga cuándo no puede consultar mis pedidos, en lugar de mostrar un estado inventado, **para** confiar en lo que veo.

**Criterios de aceptación**
- `SPEC-17 · Req. 4 · Scenario: Ventas no disponible` — se informa con "Reintentar" y, para pedidos del canal, el último estado conocido marcado como tal.
- `SPEC-17 · Req. 4 · Scenario: Despacho no disponible con el pedido despachado` — se muestra "Despachado" según Ventas, sin hitos y con la nota correspondiente.

**Prioridad:** Must, por el principio "nunca se asume disponibilidad".

---

## HU-SGT-05 · Seguir mi paquete en ruta

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Should | 5 | Hito 5–6 | `SPEC-18 · Req. 1` | RN-SGT-10, RN-SGT-12 | Despacho 🟡 (A11); Seguridad/Despacho 🟡 (A4) |

**Como** cliente con un pedido despachado, **quiero** ver la etapa del envío, la fecha programada y los hitos con hora, **para** organizarme para recibirlo.

**Criterios de aceptación**
- `SPEC-18 · Req. 1 · Scenario: En camino` — se muestran la etiqueta, la fecha programada, el distrito y los hitos con hora.
- `SPEC-18 · Req. 1 · Scenario: Aún sin despacho` — un `404` de Despacho se informa como "aún se está preparando", no como error.
- `SPEC-18 · Req. 1 · Scenario: Entregado` — se muestra la fecha y hora de entrega y, si existe, quién recibió.

**Prioridad:** Should: el curso traza la consulta de estado a SPEC-17 y SPEC-18, pero este detalle depende de dos acuerdos abiertos (A4, A11); el estado básico ya lo cubre HU-SGT-02. Ver la pregunta abierta en [`alcance.md`](../alcance.md#preguntas-abiertas).

---

## HU-SGT-06 · Enterarme de entregas fallidas o reprogramadas

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Should | 3 | Hito 5–6 | `SPEC-18 · Req. 2` | RN-SGT-11 | Despacho 🟡 (A11) |

**Como** cliente, **quiero** saber si mi entrega falló, se reprogramó o volvió al centro, **para** actuar a tiempo sin que se expongan detalles internos.

**Criterios de aceptación**
- `SPEC-18 · Req. 2 · Scenario: Entrega fallida` — se muestra "No entregado, regresando al centro" sin motivo ni comentario del repartidor.
- `SPEC-18 · Req. 2 · Scenario: Reprogramado` — los hitos muestran el fallo y la nueva fecha programada.
- `SPEC-18 · Req. 2 · Scenario: Devuelto a origen` — se informa la devolución al centro y se ofrece "Reportar un problema".

**Prioridad:** Should, igual que HU-SGT-05.

---

## HU-SGT-07 · Recibir respuestas honestas sobre la ubicación del repartidor

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Should | 2 | Hito 5–6 | `SPEC-18 · Req. 3` | RN-SGT-11 | Despacho 🟡 (A11) |

**Como** cliente, **quiero** una respuesta clara cuando pregunto dónde está exactamente el repartidor, **para** entender qué información existe sin que se expongan sus datos.

**Criterios de aceptación**
- `SPEC-18 · Req. 3 · Scenario: El cliente pide la ubicación exacta` — se explica que el seguimiento es por etapas, sin ubicación en tiempo real ni datos del repartidor.
- `SPEC-18 · Req. 3 · Scenario: Respuesta con campos no permitidos` — coordenadas, dirección completa o datos del repartidor se descartan por lista blanca.

**Prioridad:** Should, igual que HU-SGT-05; la lista blanca es obligatoria en cuanto se integre Despacho.

---

## HU-SGT-08 · Consultar Despacho con credenciales de servicio y degradar ante fallos (Habilitadora)

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-07 | Should | 3 | Hito 5–6 | `SPEC-18 · Req. 4` | RN-SGT-13, RN-SGT-14 | Seguridad ✅ (`POST /auth/token`); A4 🟡; A11 🟡 |

**Como** equipo del canal, **quiero** que la consulta a Despacho use un token de servicio vigente y degrade con elegancia, **para** que el cliente siempre vea al menos el estado según Ventas.

**Criterios de aceptación**
- `SPEC-18 · Req. 4 · Scenario: Token de servicio vencido` — el token se renueva antes de llamar; ante `401` se renueva una vez y se reintenta.
- `SPEC-18 · Req. 4 · Scenario: Despacho no disponible` — tras 4 s se muestra el estado según Ventas con "Reintentar".

**Prioridad:** Should, igual que HU-SGT-05.

**Notas:** habilitadora. El `ServiceTokenProvider` de este desglose se adelanta a HU-CHK-14 (Hito 4); aquí solo se reutiliza.

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de cada `design.md`. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-17 | T1 `[INT]` listado por cliente e historial (A8, ya resuelto) → HU-SGT-01 (se crea cerrada) · T2 `[BE]` endpoints de pedidos con control de pertenencia → HU-SGT-01 · T3 `[BE]` EstadoPedidoService y EstadoMapper → HU-SGT-02 · T4 `[BE]` herramientas `listar_pedidos` y `consultar_pedido` → HU-SGT-01 · T5 `[FE]` OrderHistoryPage y OrderHistoryTabs → HU-SGT-01 · T6 `[FE]` OrderCard, OrderList, OrderStatusCard, OrderTimeline → HU-SGT-02 · T7 `[FE]` entrada "Mis pedidos" → HU-SGT-01 · T8 `[QA]` → HU-SGT-01 a HU-SGT-04 |
| SPEC-18 | T1 `[INT]` unificar seguimiento (A11) y rol de servicio (A4) → HU-SGT-08 · T2 `[BE]` ServiceTokenProvider → **HU-CHK-14** (adelantada a Hito 4) · T3 `[BE]` `DespachoClient.seguimiento` y SeguimientoMapper → HU-SGT-05 (relacionada: HU-SGT-07) · T4 `[BE]` endpoint y herramienta `consultar_seguimiento` → HU-SGT-05 · T5 `[FE]` ShipmentTracking y ShipmentMilestones → HU-SGT-05 · T6 `[QA]` → HU-SGT-05 a HU-SGT-08 |
