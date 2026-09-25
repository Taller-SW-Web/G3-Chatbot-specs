# EP-08 · Reclamos — Historias de usuario

> Specs: [SPEC-19](../../../openspec/specs/creacion-reclamo/spec.md), [SPEC-20](../../../openspec/specs/consulta-reclamo/spec.md) · Área `RCL` · 7 historias · 22 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.
>
> Los reclamos son una **extensión** respecto de los lineamientos del curso (README §4). La creación se prioriza como Should porque otras pantallas la enlazan ("Reportar un problema") y responde al Libro de Reclamaciones; la consulta, como Could.

---

## HU-RCL-01 · Describir mi problema y revisar el reclamo antes de enviarlo

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-08 | Should | 5 | Hito 5–6 | `SPEC-19 · Req. 1` | RN-RCL-01, RN-RCL-02, RN-RCL-03 | Ventas ✅ (`GET /api/v1/pedidos`) |

**Como** cliente con un problema en un pedido, **quiero** contarlo con mis palabras y revisar un formulario ya prellenado, **para** reclamar sin llenar un formulario desde cero.

**Criterios de aceptación**
- `SPEC-19 · Req. 1 · Scenario: Reclamo expresado en lenguaje natural` — `preparar_reclamo` devuelve el formulario prellenado y editable con "Enviar reclamo".
- `SPEC-19 · Req. 1 · Scenario: Falta el pedido` — con varios pedidos se muestra `OrderList` para elegir.
- `SPEC-19 · Req. 1 · Scenario: Descripción insuficiente` — una descripción de menos de 20 caracteres se rechaza (máximo 1000).

**Prioridad:** Should (ver nota de la épica).

---

## HU-RCL-02 · Registrar mi reclamo y recibir un código

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-08 | Should | 5 | Hito 5–6 | `SPEC-19 · Req. 2` | RN-RCL-04, RN-RCL-05, RN-RCL-06, RN-CHK-01 | Ventas ✅ (A10: `POST /api/v2/reclamos`) |

**Como** cliente, **quiero** enviar mi reclamo con una confirmación explícita y recibir un código con la fecha límite de respuesta, **para** hacerle seguimiento.

**Criterios de aceptación**
- `SPEC-19 · Req. 2 · Scenario: Reclamo registrado` — se guarda `reclamo_ref` y se muestra la constancia con `codigoSeguimiento` y `fechaLimiteSLA`.
- `SPEC-19 · Req. 2 · Scenario: Cliente sin documento registrado` — el formulario pide el documento con el mismo validador de SPEC-12.
- `SPEC-19 · Req. 2 · Scenario: Doble envío` — la misma `Idempotency-Key` registra un solo reclamo.
- `SPEC-19 · Req. 2 · Scenario: El cliente cancela` — no se registra nada y el borrador se descarta.

**Prioridad:** Should (ver nota de la épica).

**Notas:** RNF: registro p95 ≤ 1 s; descripción truncada a 50 caracteres en logs.

---

## HU-RCL-03 · Evitar reclamos duplicados

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-08 | Should | 3 | Hito 5–6 | `SPEC-19 · Req. 3` | RN-RCL-07 | Ventas ✅ (A10: listado de reclamos) |

**Como** cliente, **quiero** que el chat me avise si ya tengo un reclamo abierto por el mismo problema, **para** consultar ese en lugar de duplicarlo.

**Criterios de aceptación**
- `SPEC-19 · Req. 3 · Scenario: Reclamo abierto existente` — se informa el código y el estado existentes con "Ver estado" y no se crea otro sin confirmación.
- `SPEC-19 · Req. 3 · Scenario: Reclamo previo ya atendido` — si el previo está `ATENDIDO` o `DERIVADO`, se permite sin aviso.

**Prioridad:** Should (ver nota de la épica).

**Notas:** RNF: consulta de duplicados p95 ≤ 500 ms.

---

## HU-RCL-04 · Conservar mi reclamo si falla el registro

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-08 | Should | 2 | Hito 5–6 | `SPEC-19 · Req. 4` | RN-RCL-08 | Ventas ✅ |

**Como** cliente, **quiero** que mi borrador no se pierda si el registro falla, **para** reintentar sin volver a escribir el reclamo.

**Criterios de aceptación**
- `SPEC-19 · Req. 4 · Scenario: Ventas no disponible` — se informa el fallo, se guarda el borrador 24 horas y se ofrece "Reintentar".
- `SPEC-19 · Req. 4 · Scenario: Pedido no válido para reclamar` — un `400` de Ventas se muestra de forma comprensible, normalizando `codigo` a `code`.

**Prioridad:** Should (ver nota de la épica).

---

## HU-RCL-05 · Listar y abrir mis reclamos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-08 | Could | 3 | Hito 5–6 | `SPEC-20 · Req. 1` | RN-RCL-11 | Ventas ✅ (A10) |

**Como** cliente, **quiero** ver mis reclamos y abrir uno por código o selección, **para** saber cuál está pendiente.

**Criterios de aceptación**
- `SPEC-20 · Req. 1 · Scenario: Un solo reclamo abierto` — se muestra directamente `ClaimStatusCard`.
- `SPEC-20 · Req. 1 · Scenario: Varios reclamos` — se muestra `ClaimList` con código, fecha, pedido, motivo y estado.
- `SPEC-20 · Req. 1 · Scenario: Código ajeno o inexistente` — ambos casos reciben "No encontré ese reclamo en tu cuenta".
- `SPEC-20 · Req. 1 · Scenario: Sin reclamos` — se informa y se ofrece "Reportar un problema con un pedido".

**Prioridad:** Could: extensión sin impacto en la compra; Ventas también notifica la respuesta.

---

## HU-RCL-06 · Leer el estado y la respuesta de mi reclamo

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-08 | Could | 3 | Hito 5–6 | `SPEC-20 · Req. 2` | RN-RCL-09, RN-RCL-10 | Ventas ✅ (A10) |

**Como** cliente, **quiero** ver en qué estado está mi reclamo y leer la respuesta tal como la escribió el equipo de ventas, **para** saber cómo se resolvió.

**Criterios de aceptación**
- `SPEC-20 · Req. 2 · Scenario: Reclamo atendido` — se muestra "Respondido" y el texto de la respuesta sin reformular.
- `SPEC-20 · Req. 2 · Scenario: Reclamo derivado` — se informa la derivación sin inventar el equipo destino.
- `SPEC-20 · Req. 2 · Scenario: Reclamo sin respuesta dentro del plazo` — se muestra "En revisión" con la fecha límite.

**Prioridad:** Could (igual que HU-RCL-05).

---

## HU-RCL-07 · Saber cuándo no se pueden consultar mis reclamos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-08 | Could | 1 | Hito 5–6 | `SPEC-20 · Req. 3` | — | Ventas ✅ |

**Como** cliente, **quiero** que el chat me avise si no puede consultar mis reclamos y me muestre lo que sabe localmente, **para** no ver información inventada.

**Criterios de aceptación**
- `SPEC-20 · Req. 3 · Scenario: Ventas no disponible` — se informa con "Reintentar" y se muestran código y fecha si existen en `reclamo_ref`.

**Prioridad:** Could (igual que HU-RCL-05).

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de cada `design.md`. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-19 | T1 `[BE]` herramienta `preparar_reclamo` → HU-RCL-01 · T2 `[BE]` ReclamoService → HU-RCL-02 (relacionadas: HU-RCL-03, HU-RCL-04) · T3 `[BE]` `VentasClient.reclamos` y su mock → HU-RCL-02 · T4 `[FE]` ClaimForm, ClaimReceipt, DuplicateClaimNotice → HU-RCL-01 (relacionadas: HU-RCL-02, HU-RCL-03) · T5 `[QA]` → HU-RCL-01 a HU-RCL-04 |
| SPEC-20 | T1 `[BE]` endpoints de consulta y listado → HU-RCL-05 · T2 `[BE]` ReclamoConsultaService → HU-RCL-06 · T3 `[BE]` herramientas `listar_reclamos` y `consultar_reclamo` → HU-RCL-05 · T4 `[FE]` ClaimList, ClaimStatusCard y entrada del menú → HU-RCL-05 (relacionada: HU-RCL-06) · T5 `[QA]` → HU-RCL-05 a HU-RCL-07 |
