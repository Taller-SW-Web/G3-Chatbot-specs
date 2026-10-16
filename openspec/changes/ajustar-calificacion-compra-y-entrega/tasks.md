# Tasks

## 1. Specs

- [x] 1.1 Modificar el requisito 2 de SPEC-24: calificación del pedido al pie del detalle, solo `ENTREGADO`, caritas 1/3/5.
- [x] 1.2 Añadir el requisito 7 de SPEC-24: valoración de la experiencia de compra, local, popup con estrellas 1–5.
- [x] 1.3 Actualizar el narrativo de `spec.md` (Alcance, Contexto 2, "Fuera de alcance", resueltas, idempotencia) y el `design.md`.

## 2. Documentos transversales

- [x] 2.1 Añadir `purchase_rating` y `order_ref.csat_sent` a `docs/modelo-datos.md`.
- [x] 2.2 Contratos de integración: CSAT con token del cliente, rol CLIENTE, sin scope (acuerdo A15, ya en contratos-integracion.md por el PR de Ventas).
- [x] 2.3 Quitar la exclusión del CSAT en `notificacion-confirmacion` (SPEC-16).
- [x] 2.4 Marcar la pregunta abierta 9 de `docs/conversacion/README.md` como resuelta.
- [x] 2.5 Historias de usuario, reglas y trazabilidad; recalcular totales.

## 3. Coordinación

- [x] 3.1 Comentar en Ventas #9 y #37 la corrección (escala 1/3/5, `ENTREGADO`).
- [x] 3.2 Cerrar la pregunta de autenticación del CSAT cuando Ventas responda.

## 4. Correcciones de la PO

- [x] 4.1 Corregir inconsistencias de SPEC-24: la reacción enviada se puede cambiar (se quita su exclusión de "Fuera de alcance"); el escenario de caritas pasa a "Sin carita seleccionada"; el agradecimiento de ambas calificaciones es "¡Gracias por tu calificación!"; el límite de frecuencia de las calificaciones queda pendiente hasta el Hito 5-6 en `design.md`, sin valor. Para renombrar el escenario, el requisito 2 pasa a "Calificación de la entrega con caritas (CSAT, vía Ventas)" (REMOVED del anterior + ADDED), y la escala 5/3/1 y la regla `clienteId` = `sub` se movieron al escenario "Calificación enviada" para no superar los 500 caracteres del texto del requisito.

## 5. Verificación

- [x] 5.1 `npx @fission-ai/openspec validate ajustar-calificacion-compra-y-entrega --strict`
