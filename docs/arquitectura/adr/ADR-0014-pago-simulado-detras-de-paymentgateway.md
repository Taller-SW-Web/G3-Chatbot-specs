# ADR-0014: Pago simulado con tarjeta detrás de `PaymentGateway`

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; decisión de SPEC-14, sin fecha)

## Contexto

- El curso pide "grabación del pedido y pago **con tarjeta**" para el Canal Chatbot, con **simulación** del pago.
- Ventas (F1) recibe el pago confirmado como notificación y excluye de su alcance el procesamiento del cobro, así que la simulación le corresponde al canal.
- El wireframe de `CheckoutPage` incluía "Efectivo / Pago contra entrega".
- El pago es la operación más sensible: involucra dinero (simulado), datos de tarjeta y riesgo de cobros duplicados.

## Decisión

- El pago se procesa con un **simulador determinista** (`PaymentSimulator`) que implementa el puerto outbound **`PaymentGateway`**. Una tabla de tarjetas de prueba define el resultado (`APROBADO`, `RECHAZADO` con motivo, `ERROR`, latencia), y el adaptador es reemplazable por una pasarela real.
- **Solo tarjeta.** Se retira el pago contra entrega del wireframe.
- **Reglas tipo PCI** aunque el pago sea simulado:
  - la tarjeta se captura solo en `PaymentForm` dentro de `CheckoutPage` y se envía directo a `POST /checkout/{id}/pago`, nunca por el chat;
  - un número de tarjeta pegado en el chat se redacta ([ADR-0006](ADR-0006-datos-sensibles-fuera-del-llm.md));
  - el PAN, el CVV y el vencimiento no se escriben en BD, logs, trazas ni prompts, y el body del endpoint se excluye del logging;
  - solo persisten la marca y los últimos 4 dígitos (`intento_pago`);
  - HTTPS obligatorio y aviso "Pago simulado – entorno académico. No uses tarjetas reales".
- Controles previos al cobro:
  - introspección de la sesión con Seguridad ([ADR-0009](ADR-0009-token-de-servicio-con-servicetokenprovider.md));
  - checkout vigente por 15 min (`ExpirarCheckouts` cada minuto);
  - máximo 3 intentos por checkout;
  - `Idempotency-Key` por intento ([ADR-0012](ADR-0012-claves-de-idempotencia.md)).
- El resultado aprobado se notifica a Ventas por el outbox ([ADR-0011](ADR-0011-outbox-transaccional.md)).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Pasarela real (Niubiz, Culqi, Mercado Pago) y 3-D Secure | Fuera de alcance (SPEC-14); el curso pide simulación |
| Yape, PagoEfectivo, pago contra entrega o cuotas | Fuera de alcance; el contra entrega del wireframe se descarta porque el curso pide tarjeta. Reincorporarlo sería una spec nueva |
| Capturar la tarjeta por el chat | Prohibido por SPEC-05 · Req. 9 y SPEC-14 · RNF |

## Consecuencias

**Positivas**
- Demos y pruebas reproducibles (tarjeta aprobada, rechazada tres veces, con latencia).
- Cambiar a una pasarela real solo exige un nuevo adaptador de `PaymentGateway`.

**Negativas y riesgos aceptados**
- No se valida contra un emisor real; el comportamiento real de una pasarela (3-D Secure, conciliación) queda fuera.
- Guardar tarjetas está fuera de alcance: el cliente las ingresa en cada compra.

## Referencias

- `openspec/specs/checkout-pago/spec.md` Contexto (líneas 11-13), Alcance y Fuera de alcance (líneas 27-37), Req. 3 a 6 y RNF (líneas 175-179)
- `openspec/specs/checkout-pago/design.md` (`PaymentSimulator`, línea 34; `ExpirarCheckouts`, línea 35)
- `README.md` §2, nota del checkout (línea 166)
- `docs/conversacion/privacidad.md` §4
- `docs/modelo-datos.md` tabla `intento_pago`
