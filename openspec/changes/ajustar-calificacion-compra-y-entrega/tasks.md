# Tasks

## 1. Specs

- [x] 1.1 Modificar el requisito 2 de SPEC-24: calificación del pedido al pie del detalle, solo `ENTREGADO`, caritas 1/3/5.
- [x] 1.2 Añadir el requisito 7 de SPEC-24: valoración de la experiencia de compra, local, popup con estrellas 1–5.
- [ ] 1.3 Actualizar el narrativo de `spec.md` (Alcance, Contexto 2, "Fuera de alcance", resueltas, idempotencia) y el `design.md`.

## 2. Documentos transversales

- [ ] 2.1 Añadir `purchase_rating` y `order_ref.csat_sent` a `docs/modelo-datos.md`.
- [ ] 2.2 Actualizar `docs/contratos-integracion.md` (CSAT: `ENTREGADO`, 1/3/5, `postventa:csat:escribir`).
- [ ] 2.3 Quitar la exclusión del CSAT en `notificacion-confirmacion` (SPEC-16).
- [ ] 2.4 Marcar la pregunta abierta 9 de `docs/conversacion/README.md` como resuelta.
- [ ] 2.5 Historias de usuario, reglas y trazabilidad; recalcular totales.

## 3. Coordinación

- [ ] 3.1 Comentar en Ventas #9 y #37 la corrección (escala 1/3/5, `ENTREGADO`).
- [ ] 3.2 Cerrar la pregunta de autenticación del CSAT cuando Ventas responda.

## 4. Verificación

- [x] 4.1 `npx @fission-ai/openspec validate ajustar-calificacion-compra-y-entrega --strict`
