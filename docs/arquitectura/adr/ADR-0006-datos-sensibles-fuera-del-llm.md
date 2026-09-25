# ADR-0006: Datos sensibles fuera del LLM: formularios dedicados y redacción previa

## Estado

Aceptada

## Fecha

2026-09-24 (fecha en que se amplió la redacción al documento de identidad; el principio base del README no tiene fecha)

## Contexto

- El canal maneja contraseñas (SPEC-01, SPEC-03), códigos OTP (SPEC-03, SPEC-04), datos de tarjeta (SPEC-14) y documentos de identidad (SPEC-12).
- Todo lo que llega al LLM sale del Perú hacia el proveedor (`privacidad.md` §3) y todo lo que se persiste en `mensaje` queda en el historial.
- El cliente puede escribir esos datos en el chat aunque se le pida no hacerlo.

## Decisión

- **Captura por formularios dedicados.** Contraseñas, OTP, tarjeta, documento y dirección se capturan en formularios de la UI (`FORMULARIO/LOGIN`, `OTP_*`, `PaymentForm`, secciones de `CheckoutPage`) y se envían a endpoints dedicados, nunca al LLM (README §1.3.5).
- **Redacción previa.** `SensitiveDataFilter` reemplaza, **antes** de persistir el mensaje o enviarlo al LLM:
  - números de tarjeta de 13 a 19 dígitos que pasan Luhn → `[tarjeta oculta]`;
  - OTP de 6 dígitos tras pedir un código;
  - patrones de contraseña;
  - documentos precedidos por una palabra identificadora (DNI, RUC, CE, pasaporte) → `[documento oculto]`.
- **Minimización.** Al LLM solo va el nombre de pila del cliente, nunca el correo, el celular, la dirección completa ni el documento. `recibidoPor` (SPEC-18) llega solo al frontend.
- Los resultados de las herramientas van delimitados como datos, no como instrucciones (prompt injection, SPEC-05 · Req. 9).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Permitir que el LLM recoja estos datos en la conversación (*alternativa estándar, no documentada*) | Contradice el principio 5 del README y SPEC-05 · Req. 9: expondría datos al proveedor, al historial y a los logs |
| Redactar también direcciones escritas en el chat | No se pueden detectar de forma fiable; quedó como riesgo aceptado (`conversacion/README.md`, pregunta 17) |

## Consecuencias

**Positivas**
- Cubre OWASP LLM02 (divulgación de información sensible) y prepara el canal para reglas tipo PCI ([ADR-0014](ADR-0014-pago-simulado-detras-de-paymentgateway.md)).
- El historial de conversaciones no guarda datos que obliguen a un tratamiento más estricto.

**Negativas y riesgos aceptados**
- Una dirección escrita libremente en el chat puede llegar al LLM; se mitiga con el aviso de privacidad (SPEC-05 · Req. 12) y redirigiendo a `CheckoutPage`.
- La redacción por patrones puede fallar en casos límite; las secuencias sin palabra identificadora no se tocan.
- Sigue abierto qué ve el cliente en su propia burbuja cuando pega una tarjeta (`conversacion/README.md`, pregunta 15).

## Referencias

- `README.md` §1.3, principio 5 (línea 122)
- `openspec/specs/motor-conversacion/spec.md` Req. 9 (líneas 240-259) y RNF *Privacidad* (línea 326)
- `openspec/specs/motor-conversacion/design.md` (`SensitiveDataFilter`)
- `openspec/specs/direccion-cotizacion-envio/spec.md` RNF *Privacidad* (línea 164)
- `docs/conversacion/privacidad.md` §3, §4 y §8; `docs/conversacion/README.md`, preguntas 15 y 17
