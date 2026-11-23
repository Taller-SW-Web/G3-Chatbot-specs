# Tasks

## 1. Specs

- [x] 1.1 `creacion-reclamo`: reemplazar los ocho motivos de G3 por los cinco de G5, eliminar `OTRO` y los alias, y exigir detalle (mín. 20) para el motivo más cercano.
- [x] 1.2 `creacion-reclamo`: actualizar los ejemplos de payload y duplicados a los nuevos motivos y agregar el escenario de motivo inválido (`400 VALIDACION`).
- [x] 1.3 `retroalimentacion-cliente`: explicitar el bloque al pie del detalle, los textos de `409`/`422`/`400` y el `clienteId` derivado del `sub`.
- [x] 1.4 Validar con `npx @fission-ai/openspec validate --specs` (sin `--strict`).

## 2. Contratos y documentos

- [x] 2.1 `docs/contratos-integracion.md` §2.6: cinco motivos, sin `OTRO`, motivo más cercano + `detalle`, `400 VALIDACION`.
- [x] 2.2 `docs/contratos-integracion.md` §2.8: códigos `CSAT_ALREADY_SUBMITTED` y `ORDER_NOT_DELIVERED` con su significado en la UI.
- [x] 2.3 `docs/contratos-integracion.md` §2.9: CSAT al pie del detalle, `clienteId` del backend, `409`/`422` como estados informativos.
- [x] 2.4 `docs/contratos-integracion.md` §3.3 y §6: referencia al enum de reclamos y acuerdo A18.
- [x] 2.5 `docs/contratos-integracion.md`: evidencia G5 2026-11 completada con los siete casos reales (hora UTC, endpoint, HTTP, id).
- [x] 2.6 `docs/producto/reglas-negocio.md`: RN-RCL-02 con los cinco motivos; ajustar RN-CNV-38/39 si hace falta.
- [x] 2.7 `docs/producto/historias/EP-08-reclamos.md`, `EP-02-conversacion.md`, `docs/propuestas-ux.md`, `docs/conversacion/intenciones.md` y `dialogos-ejemplo.md`: quitar referencias a motivos que G5 no reconoce y alinear el texto de `422`.

## 3. Backend (`mod-postventa`) — pendiente en su PR

- [ ] 3.1 Eliminar `CLAIM_REASON_TO_G5` y validar `motivo` contra los cinco literales de G5 en `CreateClaimRequest`.
- [ ] 3.2 Responder `400 VALIDACION` con `errores[{campo: "motivo", mensaje}]` cuando el motivo no esté en la lista; no llamar a Ventas.
- [ ] 3.3 Quitar los alias `PRODUCTO_DEFECTUOSO`, `PRODUCTO_EQUIVOCADO`, `PEDIDO_INCOMPLETO`, `NO_RECIBIDO`, `COBRO_INCORRECTO`, `ATENCION` y `OTRO` del canal.
- [ ] 3.4 Confirmar que el CSAT sigue armando `clienteId` desde el `sub` y que el DTO rechaza `clienteId` del navegador.
- [ ] 3.5 Actualizar `docs/openapi.json` y las pruebas de contrato de reclamos y CSAT.

## 4. Frontend (`mod-postventa` / `mod-orders`) — pendiente en su PR

- [ ] 4.1 `reclamo.schema.ts` y `ReclamoForm`: ofrecer solo los cinco motivos; quitar `OTRO` y el valor por defecto `PRODUCTO_DEFECTUOSO`.
- [ ] 4.2 Mostrar el motivo más cercano como sugerencia editable y exigir detalle de 20 a 1000 caracteres.
- [ ] 4.3 Quitar `DeliveryRating` de `OrderHistoryPage`; conservarlo solo en `OrderDetailPage`.
- [ ] 4.4 Verificar los textos "Ya calificaste este pedido" y "Solo puedes calificar pedidos entregados" y que el cuerpo no incluya `clienteId`.
- [ ] 4.5 Ajustar las pruebas de `reclamoPage`, `orderHistoryPage` y `postventa-adapter` a los nuevos motivos.

## 5. QA y evidencia

- [x] 5.1 Ejecutar los siete casos de "Evidencia G5 2026-11" contra el entorno acordado y completar la tabla con hora UTC, endpoint, HTTP e id reales.
- [ ] 5.2 Probar un motivo fuera de la lista: `400 VALIDACION`, sin llamada a Ventas y sin reclamo creado.
- [ ] 5.3 Probar CSAT en el detalle: 201, 409 y 422; verificar que la lista de pedidos no muestra caritas.
- [ ] 5.4 Revisar que el bloque de reclamo no reutilice el enum de devoluciones.

## 6. Archivo

- [x] 6.1 Aplicar las deltas a las specs base y mover el cambio a `openspec/changes/archive/` (flujo del repo, 2026-11-22).

## Nota de archivo (2026-11-22)

Las deltas se aplicaron a `openspec/specs/creacion-reclamo/spec.md` y
`openspec/specs/retroalimentacion-cliente/spec.md`; el cambio se archivó como
`2026-11-22-alinear-postventa-g5-2026-11`. Las tareas 3.x y 4.x quedan abiertas a propósito: este
repositorio solo es la fuente de verdad de las specs, y los PR de backend (`mod-postventa`) y frontend
(`mod-orders`/`mod-postventa`) se abren en sus repositorios hermanos. La evidencia G5 se ejecutó el
2026-11-22 y quedó en `docs/contratos-integracion.md` §2.10; las comprobaciones de QA 5.2 a 5.4 siguen
abiertas hasta que existan esos PR.
