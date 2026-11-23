# Alinear postventa con el contrato real de G5 (motivos de reclamo y CSAT)

## Why

G5 (Ventas y Postventa) publicó el contrato definitivo de F5/F6 y pidió cerrar la integración. Dos
desalineaciones siguen abiertas en el canal:

1. **Motivos de reclamo.** G5 solo acepta cinco motivos y no expone `OTRO`:
   `INCUMPLIMIENTO_PLAZO_ENTREGA`, `PRODUCTO_DEFECTUOSO_O_INCORRECTO`,
   `COBRO_INDEBIDO_O_NO_RECONOCIDO`, `ATENCION_INADECUADA` e `INCUMPLIMIENTO_GARANTIA`. La spec
   vigente de `creacion-reclamo` lista ocho valores de G3 (incluidos `PRODUCTO_DEFECTUOSO`,
   `PRODUCTO_EQUIVOCADO`, `PEDIDO_INCOMPLETO`, `NO_RECIBIDO`, `COBRO_INCORRECTO`, `ATENCION` y
   `OTRO`) y el backend todavía los traduce en silencio. Un cliente puede elegir un valor que G5 no
   reconoce como tal y el reclamo queda clasificado con un motivo distinto al que declaró.
2. **CSAT.** `retroalimentacion-cliente` ya describe el CSAT vía Ventas con tres caritas (1/3/5),
   pero el texto de interfaz debe dejar explícito que el bloque vive al pie del **detalle** de un
   pedido `ENTREGADO` (no en la lista), que `409 CSAT_ALREADY_SUBMITTED` se muestra como "Ya
   calificaste este pedido" (no como error), que `422 ORDER_NOT_DELIVERED` se muestra como "Solo
   puedes calificar pedidos entregados" y que el `clienteId` lo arma el backend desde el `sub` del
   token, no lo envía el frontend.

El resultado esperado es una sola lista de motivos en todo el canal (spec, frontend, backend y
contratos) y un contrato de CSAT que no dependa de interpretaciones de la UI.

## What Changes

- **`creacion-reclamo` (SPEC-19), Requisito 1:** reemplaza los ocho motivos de G3 por los cinco de
  G5; elimina `OTRO` y los alias; exige que el cliente elija el motivo más cercano y explique el caso
  concreto en `detalle` (mínimo 20 caracteres, máximo 1000).
- **`creacion-reclamo`, Requisito 2:** actualiza el payload de ejemplo al motivo
  `PRODUCTO_DEFECTUOSO_O_INCORRECTO`; el resto del contrato (idempotencia, constancia, documento) no
  cambia.
- **`creacion-reclamo`, Requisito 3:** actualiza el ejemplo de duplicados al nuevo motivo. El
  criterio de duplicado (mismo pedido y motivo, estado abierto) y `forzar` no cambian (ADR-0027).
- **Escenario nuevo:** un motivo fuera de la lista responde `400 VALIDACION`, no se llama a Ventas y
  el formulario solo ofrece los cinco motivos del contrato.
- **`retroalimentacion-cliente` (SPEC-24), Requisito 2:** explicita la ubicación al pie del detalle,
  el texto de `409` y `422`, que el `clienteId` se deriva del `sub` en el backend y que una
  `puntuacion` fuera de 1/3/5 responde `400 VALIDACION`. Agrega escenarios para la lista de pedidos
  (sin bloque) y para el cuerpo enviado por el frontend.
- **Contratos:** `docs/contratos-integracion.md` §2.6, §2.8, §2.9 y §3.3 reflejan los cinco motivos
  y el contrato de CSAT; §2.10 documenta la evidencia real de G5 (siete casos, hora UTC / endpoint /
  HTTP / id) y las rutas BFF equivalentes.
- **Documentos de producto y conversación:** `reglas-negocio.md`, `EP-08-reclamos.md`,
  `EP-02-conversacion.md`, `propuestas-ux.md`, `intenciones.md` y `dialogos-ejemplo.md` dejan de
  mencionar motivos que G5 no reconoce.

## Capabilities

- `creacion-reclamo`: MODIFIED Requisitos 1, 2 y 3 (motivos, payload y duplicados).
- `retroalimentacion-cliente`: MODIFIED Requisito 2 (CSAT de la entrega).

## Impacto

- **Backend (`mod-postventa`):** hoy `CLAIM_REASON_TO_G5` acepta los ocho valores de G3 y los traduce
  a los cinco de G5. Debe validar contra los cinco valores, responder `400 VALIDACION` fuera de la
  lista y eliminar la traducción de alias. El CSAT ya arma `clienteId` desde `customer_id` y prohíbe
  campos extra; se conserva.
- **Frontend (`mod-postventa` / `mod-orders`):** `reclamo.schema.ts` y `ReclamoForm` deben ofrecer
  solo los cinco motivos; `DeliveryRating` debe quedar solo en el detalle y no en la lista de
  pedidos.
- **Datos:** no hay migración. `claim_ref` no guarda el motivo; el motivo vive en Ventas y la
  detección de duplicados usa el listado `/me`, como ya define ADR-0027.
- **Contrato:** no se agregan endpoints, estados ni campos; solo se alinean valores y textos.

## Fuera de alcance

- Cambiar los motivos de devolución o cambio (F3): su enum es distinto y sigue siendo el de
  `solicitud-devolucion-cambio` (`TALLA_INCORRECTA`, `NO_ERA_LO_QUE_ESPERABA`,
  `PRODUCTO_DEFECTUOSO`, `PRODUCTO_EQUIVOCADO_ENVIADO`, `YA_NO_LO_QUIERO`, `OTRO`).
- Agregar un motivo "OTRO" o reintroducir alias en el canal.
- Agregar endpoints, estados, tablas o migraciones.
- Adjuntar capturas crudas de la corrida: los resultados verificados están en
  `docs/contratos-integracion.md` §2.10.

## Rollback

El cambio es documental y de contrato. Si hubiera que revertir la implementación, se vuelve a la
versión anterior del canal, pero **no** se reintroduce `OTRO`: G5 no lo acepta y el reclamo
quedaría rechazado o mal clasificado. La lista de cinco motivos se conserva como línea base.

## Questions to Confirm

No quedan preguntas abiertas de producto. La lista de cinco motivos y los textos de `409`/`422` son
los publicados por G5; la evidencia de integración se ejecutó el 2026-11-22 y está en
`docs/contratos-integracion.md` §2.10.
