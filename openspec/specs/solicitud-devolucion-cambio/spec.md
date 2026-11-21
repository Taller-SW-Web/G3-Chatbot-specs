# Solicitud de devolución o cambio

> Origen: SPEC-21 · Grupo: Postventa · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03), [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`direccion-cotizacion-envio`](../direccion-cotizacion-envio/spec.md) (SPEC-12), [`consulta-estado-pedido`](../consulta-estado-pedido/spec.md) (SPEC-17), Ventas (F3)

## Responsables

- **David:** solicitud con evidencia y limpieza de evidencias.
- **Alonso:** herramienta de devolución.
- **Diego:** pestaña "Reembolsos" de `OrderHistoryPage`.
- **Nikol (QA):** casos de prueba a partir de los escenarios, pruebas E2E si el flujo es crítico y validación contra la definición de terminado.

## Purpose

Permitir al cliente solicitar, desde el chat, el cambio o la devolución con reembolso de un producto ya entregado, con evidencia cuando el motivo lo exige, y dejarle un código de seguimiento.

## Contexto

🧩 Esta spec se agregó a partir del wireframe de historial de pedidos, que incluye una pestaña "Reembolsos" con solicitudes en estado "Pendiente de aprobación" y un motivo ("Talla incorrecta"). Eso corresponde a la funcionalidad **F3 — Devoluciones y cambios** de Ventas y Postventa.

✅ El `api-contract.md` de Ventas (v1.3.0) publica F3 completo, incluidos los dos endpoints que faltaban (subida de evidencia y listado por cliente — acuerdos A10 y A13, ambos resueltos el 23/09). Reglas de negocio confirmadas:

- La solicitud solo se acepta sobre un pedido en estado `ENTREGADO` (confirmado por F1); si no lo está, responde `409`.
- **Plazo: 7 días naturales desde la entrega.** Fuera de ese plazo, o si falta evidencia obligatoria, responde `400`.
- El motivo es tipificado; si el motivo implica un defecto, **se exige evidencia** (fotos o PDF, como `{tipo: IMAGEN, url}`), subida primero a `POST /api/v2/devoluciones/evidencias/upload` — **Ventas hostea el archivo, el chatbot no necesita su propio bucket para la evidencia**. 🧩 Aclaración: las imágenes que el cliente adjunta al chat para que el asistente las interprete (SPEC-23) usan un bucket privado propio de Supabase Storage y no se reutilizan como evidencia; la evidencia se sigue subiendo a Ventas desde este formulario.
- El Gestor evalúa el expediente vía `PATCH /devoluciones/{id}/resolucion`: `SOLICITADA → EN_EVALUACION → APROBADA/RECHAZADA`, y un rechazo sin `fundamento` responde `400`.
- F3 nunca modifica el pedido en M1 directamente; solo lo consulta.
- `GET /api/v2/devoluciones/me` permite listar y detectar duplicados (Requisito 5), ya sin bloqueo.

Lo único que el contrato sigue sin modelar de forma estructurada: un campo explícito para la variante deseada en un `CAMBIO` (ver Requisito 4 y Fuera de alcance).

## Alcance

Incluye:
- Detección de la intención ("llegó de la talla equivocada", "quiero cambiar este producto", "quiero devolverlo").
- Selección del pedido y, dentro de él, de la línea o líneas a devolver o cambiar (no siempre es el pedido completo).
- Tipo de solicitud: `CAMBIO` (por otra talla/color/producto) o `DEVOLUCION_DINERO`.
- Motivo tipificado y, si corresponde, carga de evidencia fotográfica o en PDF, subida directo a Ventas.
- Verificación de elegibilidad: pedido `ENTREGADO` y dentro de los 7 días naturales desde la entrega.
- Aviso si ya existe una solicitud abierta para el mismo pedido, consultando el listado real de Ventas.
- Formulario de revisión y confirmación explícita antes de enviar.
- Registro en Ventas con idempotencia y constancia con código.

### Fuera de alcance

- Evaluación y decisión de la solicitud (`APROBADA`/`RECHAZADA`): la hace el Gestor en Ventas mediante `PATCH /devoluciones/{id}/resolucion`.
- Coordinación del recojo o del nuevo despacho: la hace Despacho, orquestada por Ventas (F3).
- Ejecución del reembolso: es F4 de Ventas.
- Anulación de un pedido antes de la entrega: es F2 de Ventas, no se ofrece en este canal.
- Indicar la variante deseada como un campo estructurado del pedido a Ventas: el contrato actual no lo modela; se envía en `descripcion` hasta que se confirme un campo dedicado.

## Requirements

### Requirement: Verificar elegibilidad
El sistema DEBE (SHALL) verificar, antes de mostrar el formulario, que el pedido está `ENTREGADO` (según SPEC-17) y dentro de los **7 días naturales** desde la fecha de entrega.

*Trazabilidad: SPEC-21 · Requisito 1.*

#### Scenario: Pedido elegible
- **DADO** un pedido `ENTREGADO` hace 5 días
- **CUANDO** el cliente inicia una solicitud sobre él
- **ENTONCES** se muestra el formulario de devolución/cambio

#### Scenario: Pedido no entregado
- **DADO** un pedido `EN_PREPARACION` o `DESPACHADO`
- **CUANDO** el cliente intenta solicitar una devolución
- **ENTONCES** se explica que solo se puede solicitar después de la entrega, y se ofrece "Reportar un problema con el envío" (SPEC-18) si el reclamo es por la demora

#### Scenario: Plazo vencido
- **DADO** un pedido `ENTREGADO` hace 9 días (más de 7 días naturales)
- **CUANDO** se intenta solicitar
- **ENTONCES** se informa "El plazo de 7 días para solicitar un cambio o devolución de este pedido ya venció" y se ofrece "Crear un reclamo" (SPEC-19) como alternativa

### Requirement: Elegir línea, tipo y motivo
El sistema DEBE (SHALL) permitir elegir una o más líneas del pedido, el tipo de solicitud y un motivo tipificado.

Motivos: `TALLA_INCORRECTA`, `NO_ERA_LO_QUE_ESPERABA`, `PRODUCTO_DEFECTUOSO`, `PRODUCTO_EQUIVOCADO_ENVIADO`, `YA_NO_LO_QUIERO`, `OTRO`.

*Trazabilidad: SPEC-21 · Requisito 2.*

#### Scenario: Selección de línea y motivo
- **DADO** un pedido con 2 líneas
- **CUANDO** el cliente escribe "las zapatillas me quedaron chicas, quiero cambiarlas por una talla más"
- **ENTONCES** el LLM invoca `preparar_devolucion {pedidoRef, lineaRef: "zapatillas", tipo: CAMBIO, motivo: TALLA_INCORRECTA}` y se muestra el formulario con esos campos prellenados y editables

#### Scenario: Motivo "producto defectuoso" exige evidencia
- **DADO** el motivo `PRODUCTO_DEFECTUOSO`
- **CUANDO** se arma el formulario
- **ENTONCES** el campo de evidencia (1 a 3 archivos) se marca obligatorio y el botón "Enviar solicitud" queda deshabilitado hasta que haya al menos uno válido

#### Scenario: Cambio — indicar la variante deseada
- **DADO** el tipo `CAMBIO`
- **CUANDO** se completa el formulario
- **ENTONCES** se pide la variante deseada (talla u color, usando el mismo `VariantSelector` de SPEC-09) para el producto de la línea elegida, validando su disponibilidad (SPEC-10)

### Requirement: Cargar evidencia fotográfica o en PDF
El sistema DEBE (SHALL) permitir adjuntar hasta 3 archivos (`image/jpeg`, `image/png`, `image/webp` o `application/pdf`, máx. 5 MB cada uno), subiéndolos directo al almacenamiento de Ventas.

*Trazabilidad: SPEC-21 · Requisito 3.*

#### Scenario: Carga exitosa
- **DADO** el formulario con el motivo `PRODUCTO_DEFECTUOSO`
- **CUANDO** el cliente adjunta 2 fotos válidas
- **ENTONCES** cada una se envía por `POST /api/v1/evidencias` (proxy del chatbot hacia `POST /api/v2/devoluciones/evidencias/upload` de Ventas), Ventas responde `201 {tipo, url, nombreArchivoOriginal, tamanioBytes, fechaSubida}`, se guarda la referencia ligada al borrador de la conversación y se muestra la miniatura con la opción de quitarla

#### Scenario: Archivo inválido
- **DADO** un archivo de más de 5 MB o de un tipo no permitido
- **CUANDO** se intenta adjuntar
- **ENTONCES** Ventas responde `400 Bad Request` y se muestra "El archivo debe pesar menos de 5 MB y ser una imagen o PDF"

#### Scenario: Evidencia sin enviar la solicitud
- **DADO** archivos subidos a un borrador que el cliente abandona sin enviar
- **CUANDO** pasan 24 horas
- **ENTONCES** el chatbot borra la referencia local (`evidence`) de su propia base de datos; el archivo en sí vive en el almacenamiento de Ventas y su retención es responsabilidad de ellos, no del chatbot

### Requirement: Confirmación explícita y registro
El sistema DEBE (SHALL) registrar la solicitud en Ventas solo cuando el cliente pulsa "Enviar solicitud", con una `Idempotency-Key`, y mostrar la constancia con un código.

Payload real `POST {VEN}/api/v2/devoluciones`:
```json
{ "pedidoId": "PED-2026-00891",
  "tipo": "CAMBIO",
  "motivo": "TALLA_INCORRECTA",
  "descripcion": "El botón de encendido no responde",
  "items": [{ "productoId": "PROD-101", "cantidad": 1 }],
  "evidencias": [{ "tipo": "IMAGEN", "url": "https://api.empresa.com/v2/uploads/evidencias/ev-981-foto1.jpg" }]
}
```

El cuerpo de `POST /api/v1/devoluciones` es ese payload más `forzar` (booleano, por defecto `false`); `forzar` es una decisión del chatbot y no se reenvía a Ventas.
🧩 El contrato no incluye un campo `varianteDeseada` explícito para el caso `CAMBIO`; mientras Ventas no lo confirme, se envía como parte de `descripcion` en texto libre y se coordina el cambio de variante por fuera (ver Fuera de alcance).

*Trazabilidad: SPEC-21 · Requisito 4.*

#### Scenario: Solicitud registrada
- **DADO** un formulario confirmado
- **CUANDO** Ventas responde `201 {devolucionId: "DEV-2026-0042", pedidoId, tipo, estado: SOLICITADA, fechaRegistro}`
- **ENTONCES** se guarda `return_ref` con `devolucionId` como código visible (Ventas ya usa un identificador legible, no hace falta generar uno propio), se ligan las evidencias subidas y se muestra "Te avisaremos cuando el equipo de ventas revise tu solicitud"

#### Scenario: Evidencia obligatoria faltante o plazo excedido
- **DADO** un motivo `PRODUCTO_DEFECTUOSO` sin evidencia, o una solicitud fuera de los 7 días naturales
- **CUANDO** se envía
- **ENTONCES** Ventas responde `400 Bad Request` y se muestra el motivo correspondiente

#### Scenario: Pedido no `ENTREGADO`
- **DADO** un pedido que no está `ENTREGADO`
- **CUANDO** se envía la solicitud
- **ENTONCES** Ventas responde `409 Conflict` y se informa que solo se puede solicitar después de la entrega

#### Scenario: Doble envío
- **DADO** dos envíos con la misma `Idempotency-Key`
- **CUANDO** se procesan
- **ENTONCES** se registra una sola solicitud

#### Scenario: Ventas no disponible
- **DADO** que Ventas no responde al registrar
- **CUANDO** se envía
- **ENTONCES** se informa que no se pudo registrar y se conserva el borrador (incluidas las referencias a la evidencia ya subida) por 24 horas, con "Reintentar"

#### Scenario: Duplicado detectado al registrar
- **DADO** una solicitud abierta para el mismo pedido y un envío sin `forzar`
- **CUANDO** llega el `POST /api/v1/devoluciones`
- **ENTONCES** se responde `409 DEVOLUCION_DUPLICADA` con `{ devolucionId, estado, pedidoId }`, no se llama a Ventas y el frontend muestra el aviso con la opción de forzar

### Requirement: Solicitud duplicada sobre el mismo pedido
El sistema DEBE (SHALL) detectar, antes de registrar, si ya existe una solicitud abierta para el mismo pedido, consultando `GET /api/v1/devoluciones` (proxy a `GET /api/v2/devoluciones/me?estado=` con el token del cliente) y filtrando por `pedidoId` en el backend del chatbot (el contrato publicado de Ventas no ofrece ese filtro; si Ventas lo agrega, se usa directamente). La detección DEBE (SHALL) repetirse en el `POST /api/v1/devoluciones` como comprobación autoritativa. Si existe una solicitud abierta y el cliente no envía `forzar: true`, el backend responde `409 DEVOLUCION_DUPLICADA` con el `devolucionId` y el estado existentes; con `forzar: true` registra una nueva. La `Idempotency-Key` sigue aplicando en ambos casos.

Estados abiertos: `SOLICITADA`, `EN_EVALUACION` y `APROBADA` (aún no completada). Estados cerrados: `RECHAZADA` y `COMPLETADA`.

*Trazabilidad: SPEC-21 · Requisito 5.*

#### Scenario: Solicitud abierta existente
- **DADO** una solicitud `EN_EVALUACION` para un pedido
- **CUANDO** el cliente intenta solicitar de nuevo sobre el mismo pedido sin `forzar`
- **ENTONCES** se informa el código existente (`DEV-2026-0042`) y su estado, con "Ver estado" (SPEC-22), y no se crea una nueva; si confirma, el formulario reenvía con `forzar: true`

#### Scenario: Solicitud previa ya resuelta
- **DADO** que la única solicitud previa sobre ese pedido está `RECHAZADA` o `COMPLETADA`
- **CUANDO** el cliente inicia una nueva
- **ENTONCES** se permite sin aviso (no es un duplicado, es una solicitud nueva sobre un caso ya cerrado)

#### Scenario: Registro forzado
- **DADO** una solicitud abierta para el mismo pedido y una confirmación explícita del cliente
- **CUANDO** se envía `POST /api/v1/devoluciones` con `forzar: true`
- **ENTONCES** se registra la nueva solicitud, se guarda su `return_ref` y se muestra una constancia nueva con su propio `devolucionId`

#### Scenario: Doble envío con `forzar`
- **DADO** dos envíos con la misma `Idempotency-Key` y `forzar: true`
- **CUANDO** se procesan
- **ENTONCES** se registra una sola solicitud y ambos reciben la misma constancia

#### Scenario: No se puede consultar el listado de duplicados
- **DADO** que `GET /api/v1/devoluciones` falla o excede el tiempo de espera al comprobar duplicados
- **CUANDO** el cliente envía una solicitud distinta
- **ENTONCES** el registro continúa (fail-open), se registra un aviso en los logs y el cliente no ve un error de duplicados; si el equipo prefiere bloquear, se cambia a `503 SERVICIO_NO_DISPONIBLE` en una decisión posterior

## Requisitos no funcionales

- **Confirmación:** ninguna solicitud se registra solo por la decisión del LLM (igual que SPEC-19).
- **Privacidad:** el chatbot nunca almacena el archivo de evidencia; solo la URL pública que Ventas genera. Esa URL no se envía al LLM.
- **Retención:** las referencias locales de evidencia de borradores no enviados se purgan a las 24 horas; el archivo en sí lo retiene Ventas según su propia política.
- **Rendimiento:** la carga de cada archivo tarda p95 ≤ 3 s (proxy hacia Ventas); el registro de la solicitud, p95 ≤ 1 s.
- **Mapeo de errores:** Ventas responde con la clave `codigo`; se normaliza al `code` interno.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.

## Decisiones

- **D4 — Duplicados de postventa (auditoría §4).** El chatbot detecta solicitudes abiertas del mismo pedido contra el listado real de Ventas; si existe una y el cliente no confirma, responde `409 DEVOLUCION_DUPLICADA` con el `devolucionId` y estado existentes. La confirmación explícita se expresa con `forzar: true` en `POST /api/v1/devoluciones`. **Aprobada:** 2026-11-21. **Estado:** en implementación; no se marca implementada hasta que el código mergee. **Auditoría:** [auditoría de specs 2026-11](../../../docs/auditoria-specs-2026-11.md). **ADR:** [ADR-0027](../../../docs/arquitectura/adr/ADR-0027-duplicados-de-postventa-y-forzar.md).
