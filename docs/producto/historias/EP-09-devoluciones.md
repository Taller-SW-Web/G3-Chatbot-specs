# EP-09 · Devoluciones y reembolsos — Historias de usuario

> Specs: [SPEC-21](../../../openspec/specs/solicitud-devolucion-cambio/spec.md), [SPEC-22](../../../openspec/specs/consulta-devolucion-reembolso/spec.md) · Área `DEV` · 9 historias · 31 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.
>
> Devoluciones, cambios y reembolsos son una **extensión** agregada a partir del wireframe de historial (README §4). Todas las historias se priorizan como Could.

---

## HU-DEV-01 · Saber si mi pedido es elegible para cambio o devolución

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 3 | Hito 5–6 | `SPEC-21 · Req. 1` | RN-DEV-01, RN-DEV-02 | Ventas ✅ (`GET /api/v1/pedidos/{id}`) |

**Como** cliente, **quiero** saber de inmediato si puedo pedir un cambio o una devolución de un pedido, **para** no llenar un formulario que después será rechazado.

**Criterios de aceptación**
- `SPEC-21 · Req. 1 · Scenario: Pedido elegible` — un pedido `ENTREGADO` hace 5 días muestra el formulario.
- `SPEC-21 · Req. 1 · Scenario: Pedido no entregado` — se explica que solo aplica tras la entrega y se ofrece reportar el envío.
- `SPEC-21 · Req. 1 · Scenario: Plazo vencido` — con más de 7 días naturales se informa el vencimiento y se ofrece crear un reclamo.

**Prioridad:** Could (ver nota de la épica).

**Notas:** incluye el botón "Solicitar cambio o devolución" en `OrderStatusCard` (SPEC-17).

---

## HU-DEV-02 · Elegir los productos, el tipo y el motivo de la solicitud

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 5 | Hito 5–6 | `SPEC-21 · Req. 2` | RN-DEV-03, RN-DEV-04, RN-DEV-07 | Productos 🟡 (A5: disponibilidad de la variante deseada) |

**Como** cliente, **quiero** indicar qué productos devuelvo o cambio, por qué, y qué variante quiero a cambio, **para** que mi solicitud llegue completa.

**Criterios de aceptación**
- `SPEC-21 · Req. 2 · Scenario: Selección de línea y motivo` — `preparar_devolucion` devuelve el formulario con línea, tipo y motivo prellenados y editables.
- `SPEC-21 · Req. 2 · Scenario: Motivo "producto defectuoso" exige evidencia` — la evidencia (1 a 3 archivos) pasa a ser obligatoria y bloquea el envío.
- `SPEC-21 · Req. 2 · Scenario: Cambio — indicar la variante deseada` — se pide la variante con `VariantSelector` y se valida su disponibilidad.

**Prioridad:** Could (ver nota de la épica).

---

## HU-DEV-03 · Adjuntar evidencia fotográfica o en PDF

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 5 | Hito 5–6 | `SPEC-21 · Req. 3` | RN-DEV-05, RN-DEV-06 | Ventas ✅ (A13: `/devoluciones/evidencias/upload`) |

**Como** cliente con un producto defectuoso, **quiero** adjuntar fotos o un PDF desde el chat, **para** respaldar mi solicitud.

**Criterios de aceptación**
- `SPEC-21 · Req. 3 · Scenario: Carga exitosa` — cada archivo se sube por el proxy a Ventas, se guarda la referencia y se muestra la miniatura con opción de quitarla.
- `SPEC-21 · Req. 3 · Scenario: Archivo inválido` — un archivo de más de 5 MB o de tipo no permitido se rechaza con el mensaje correspondiente.
- `SPEC-21 · Req. 3 · Scenario: Evidencia sin enviar la solicitud` — a las 24 horas se borra la referencia local; el archivo queda en Ventas.

**Prioridad:** Could (ver nota de la épica).

**Notas:** RNF: carga de cada archivo p95 ≤ 3 s; la URL de la evidencia no se envía al LLM.

---

## HU-DEV-04 · Registrar mi solicitud y recibir un código

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 5 | Hito 5–6 | `SPEC-21 · Req. 4` | RN-DEV-07, RN-DEV-08, RN-DEV-09 | Ventas ✅ (A10: `POST /api/v2/devoluciones`) |

**Como** cliente, **quiero** enviar mi solicitud con una confirmación explícita y recibir su código, **para** hacerle seguimiento.

**Criterios de aceptación**
- `SPEC-21 · Req. 4 · Scenario: Solicitud registrada` — ante `201` se guarda `devolucion_ref` con el `devolucionId` como código y se ligan las evidencias.
- `SPEC-21 · Req. 4 · Scenario: Evidencia obligatoria faltante o plazo excedido` — el `400` de Ventas se muestra con su motivo.
- ``SPEC-21 · Req. 4 · Scenario: Pedido no `ENTREGADO` `` — el `409` de Ventas se informa como "solo después de la entrega".
- `SPEC-21 · Req. 4 · Scenario: Doble envío` — la misma `Idempotency-Key` registra una sola solicitud.
- `SPEC-21 · Req. 4 · Scenario: Ventas no disponible` — se conserva el borrador (con la evidencia) 24 horas con "Reintentar".

**Prioridad:** Could (ver nota de la épica).

**Notas:** RNF: registro p95 ≤ 1 s.

---

## HU-DEV-05 · Evitar solicitudes duplicadas

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 3 | Hito 5–6 | `SPEC-21 · Req. 5` | RN-DEV-10 | Ventas ✅ (A10: listado de devoluciones) |

**Como** cliente, **quiero** que el chat me avise si ya tengo una solicitud abierta sobre el mismo pedido, **para** consultarla en lugar de duplicarla.

**Criterios de aceptación**
- `SPEC-21 · Req. 5 · Scenario: Solicitud abierta existente` — se informa el código y el estado existentes con "Ver estado" y no se crea otra sin confirmación.
- `SPEC-21 · Req. 5 · Scenario: Solicitud previa ya resuelta` — si la previa está `RECHAZADA` o `COMPLETADA`, se permite sin aviso.

**Prioridad:** Could (ver nota de la épica).

**Notas:** ver la pregunta abierta sobre el filtro `pedidoId` del listado de Ventas ([`alcance.md`](../alcance.md#preguntas-abiertas)).

---

## HU-DEV-06 · Ver todas mis solicitudes en la pestaña "Reembolsos"

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 3 | Hito 5–6 | `SPEC-22 · Req. 1` | RN-DEV-13 | Ventas ✅ (A10) |

**Como** cliente, **quiero** ver en un solo lugar todas mis solicitudes de cambio o devolución, incluidas las que hice por otros canales, **para** tener el panorama completo.

**Criterios de aceptación**
- `SPEC-22 · Req. 1 · Scenario: Pestaña "Reembolsos"` — se listan las solicitudes de todos los canales con código, pedido, fecha, motivo, `estadoReembolso` y badge.
- `SPEC-22 · Req. 1 · Scenario: Consulta por código` — se consulta la solicitud indicada y se muestra si pertenece al cliente.
- `SPEC-22 · Req. 1 · Scenario: Código ajeno o inexistente` — ambos casos reciben "No encontré esa solicitud en tu cuenta".
- `SPEC-22 · Req. 1 · Scenario: Sin solicitudes` — se informa que aún no hay solicitudes.

**Prioridad:** Could (ver nota de la épica).

**Notas:** la pestaña se integra en `OrderHistoryPage` (HU-SGT-01).

---

## HU-DEV-07 · Ver el estado de mi solicitud

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 3 | Hito 5–6 | `SPEC-22 · Req. 2` | RN-DEV-11, RN-DEV-12 | Ventas ✅ (A10) |

**Como** cliente, **quiero** ver si mi solicitud fue recibida, está en revisión, se aprobó o se rechazó y por qué, **para** saber qué esperar.

**Criterios de aceptación**
- `SPEC-22 · Req. 2 · Scenario: En revisión` — se muestra "En revisión · {motivo} · Pendiente de aprobación".
- `SPEC-22 · Req. 2 · Scenario: Rechazada` — se muestra el fundamento del Gestor sin reformular.
- `SPEC-22 · Req. 2 · Scenario: Aprobada como cambio` — se muestra "Aprobada · Coordinando el cambio con logística".

**Prioridad:** Could (ver nota de la épica).

---

## HU-DEV-08 · Ver el estado de mi reembolso

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 3 | Hito 5–6 | `SPEC-22 · Req. 3` | RN-DEV-12, RN-DEV-14 | Ventas ✅ (A10: `resolucion.reembolso`) |

**Como** cliente con una devolución de dinero aprobada, **quiero** ver el monto, el estado y la fecha del reembolso, **para** saber cuándo recibiré mi dinero.

**Criterios de aceptación**
- `SPEC-22 · Req. 3 · Scenario: Reembolso completado` — se muestra el monto reembolsado y la fecha.
- `SPEC-22 · Req. 3 · Scenario: Reembolso aprobado, aún sin bloque de reembolso` — se muestra "Tu reembolso está en proceso", sin inventar monto ni fecha.
- `SPEC-22 · Req. 3 · Scenario: Reembolso fallido` — se informa el problema sin detalles técnicos.

**Prioridad:** Could (ver nota de la épica).

---

## HU-DEV-09 · Saber cuándo no se pueden consultar mis devoluciones

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-09 | Could | 1 | Hito 5–6 | `SPEC-22 · Req. 4` | — | Ventas ✅ |

**Como** cliente, **quiero** que el chat me avise si no puede consultar mis devoluciones y me muestre lo que sabe localmente, **para** no ver estados inventados.

**Criterios de aceptación**
- `SPEC-22 · Req. 4 · Scenario: Ventas no disponible` — se informa con "Reintentar" y se muestran código y fecha si existen en `devolucion_ref` (solo solicitudes de este canal).

**Prioridad:** Could (ver nota de la épica).

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de cada `design.md`. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-21 | T1 `[BE]` herramienta `preparar_devolucion` y borradores → HU-DEV-02 · T2 `[BE]` `POST /evidencias` → HU-DEV-03 · T3 `[BE]` DevolucionService → HU-DEV-04 (relacionadas: HU-DEV-01, HU-DEV-05) · T4 `[BE]` `VentasClient.devoluciones` y su mock → HU-DEV-04 · T5 `[BE]` job de limpieza de evidencia → HU-DEV-03 · T6 `[FE]` ReturnForm, EvidenceUploader, ReturnReceipt, DuplicateReturnNotice → HU-DEV-02 (relacionadas: HU-DEV-03, HU-DEV-04, HU-DEV-05) · T7 `[FE]` botón en OrderStatusCard → HU-DEV-01 · T8 `[QA]` → HU-DEV-01 a HU-DEV-05 |
| SPEC-22 | T1 `[BE]` endpoints de consulta y listado → HU-DEV-06 · T2 `[BE]` DevolucionConsultaService → HU-DEV-07 (relacionada: HU-DEV-08) · T3 `[FE]` ReturnHistoryTab y ReturnStatusCard → HU-DEV-06 (relacionadas: HU-DEV-07, HU-DEV-08) · T4 `[QA]` → HU-DEV-06 a HU-DEV-09 |
