# ADR-0016: Dirección y documento solo en `CheckoutPage`, nunca por el chat ni el LLM

## Estado

Aceptada

## Fecha

2026-09-24 (se retiran `elegir_direccion` y `cotizar_envio` de las herramientas del LLM)

## Contexto

- El wireframe de `CheckoutPage` captura la dirección con **campos libres** (destinatario, dirección, distrito, referencia) en la misma pantalla de pago, no eligiendo entre direcciones guardadas.
- Ventas exige siempre `contacto.tipoDocumento` y `numeroDocumento` al crear el pedido (A14).
- SPEC-12 · RNF prohíbe enviar la dirección y el documento al LLM.
- SPEC-05 · Req. 3 listaba las herramientas `elegir_direccion` y `cotizar_envio`, y SPEC-14 describía un paso conversacional para "guiar a elegir la dirección": ambas cosas contradecían a SPEC-12.

## Decisión

- La dirección de entrega y el documento del comprador se capturan **solo en `CheckoutPage`** (`AddressSection`, `BuyerDocumentSection`), con los nombres de campo de Ventas. Se prellenan con la dirección predeterminada de Seguridad si existe; guardarla en Seguridad es opcional ("Guardar esta dirección", junto con la creación del pedido).
- La cotización se pide con `POST /api/v1/envio/cotizar` desde esa pantalla (Despacho, `modalidad: DELIVERY`, vigencia de 30 min).
- Se **retiraron** `elegir_direccion` y `cotizar_envio` de las herramientas del LLM. La intención de envío invoca `iniciar_checkout`, que lleva a `CheckoutPage` con la sección de dirección enfocada; si ya hay cotización vigente, `ver_carrito` la muestra.
- Si el cliente escribe su documento en el chat, se redacta ([ADR-0006](ADR-0006-datos-sensibles-fuera-del-llm.md)) y se le redirige a `CheckoutPage`.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Herramientas `elegir_direccion` y `cotizar_envio` en el chat (versión anterior de SPEC-05) | La dirección pasaría por el LLM, contra SPEC-12 · RNF *Privacidad* |
| Paso separado para elegir entre direcciones guardadas | Fuera de alcance (SPEC-12); el wireframe usa campos libres |

## Consecuencias

**Positivas**
- La dirección y el documento nunca llegan al proveedor LLM ni al historial del chat.
- Una sola pantalla valida el documento con las mismas expresiones regulares que Ventas (`DocumentoValidator`).

**Negativas y riesgos aceptados**
- Una dirección escrita libremente en el chat no se detecta de forma fiable y puede llegar al LLM (riesgo aceptado).
- El payload de `/envio/cotizar` difiere entre documentos (ver Referencias): conviene unificarlo.

## Referencias

- `docs/conversacion/README.md` pregunta 6, resuelta el 2026-09-24 (líneas 50-51)
- `docs/producto/alcance.md` pregunta 4 (líneas 257-258)
- `openspec/specs/direccion-cotizacion-envio/spec.md` Contexto (línea 17), Req. 1, 2 y 4 y RNF *Privacidad* (línea 164)
- `openspec/specs/motor-conversacion/spec.md` Req. 3 (línea 118)
- `openspec/specs/checkout-pago/spec.md` Req. 1
- Payload de cotización: `docs/contratos-integracion.md` §2.4 (línea 96, `{nombreCompleto, direccionExacta, distrito, referencia?}`) frente a `openspec/specs/direccion-cotizacion-envio/design.md` (`{destinatario, direccion, distrito, referencia?}`)
