# ADR-0015: Verificación propia del celular por OTP con SMS simulado

## Estado

Aceptada

## Fecha

2026-09-23 (Seguridad decide dejar fuera del ciclo la validación de celular por canal, acuerdo A2)

## Contexto

- El curso exige "validación del número celular y correo del cliente" para este canal.
- El chatbot había pedido a Seguridad un mecanismo para verificar el celular por OTP (acuerdo A2, su RF-10.4).
- Seguridad respondió por escrito que queda **fuera de alcance del ciclo**: el SMS es simulado hasta el final del curso y el correo ya queda verificado en el registro. Se reevaluaría en el Hito 4 solo con un caso concreto.
- El correo se sigue verificando con Seguridad (SPEC-02).

## Decisión

- El chatbot implementa su **propia verificación del celular**, autocontenida y sin tocar el perfil de Seguridad:
  - El número a verificar es el vigente en `GET /auth/me` → `celular`.
  - El OTP es de 6 dígitos, con vigencia de 5 min, 3 intentos y 3 envíos cada 15 min (mismas reglas que SPEC-03).
  - Se envía por el puerto **`SmsSender`** con el adaptador **`SimulatedSmsSender`**, reemplazable.
  - Endpoints propios: `POST /api/v1/contacto/celular/solicitar-otp` y `/verificar-otp`.
- La verificación se guarda en `celular_verificacion_local` ligada al cliente **y al número exacto**; si el celular del perfil cambia, deja de valer automáticamente.
- `CheckoutGuard.exigir_celular_verificado()` bloquea el checkout (`403 CELULAR_NO_VERIFICADO`) mientras el celular vigente no tenga verificación local.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Verificación compartida en Seguridad (acuerdo A2) | Seguridad la decidió fuera de alcance del ciclo (2026-09-23) |
| Usar el flag `celularVerificado` de `GET /auth/me` | Seguridad no lo alimentará este ciclo; el chatbot no depende de él (`validacion-celular/design.md`) |
| Proveedor SMS real | Fuera de alcance (SPEC-04); el SMS es simulado en todo el curso |

## Consecuencias

**Positivas**
- Cumple el lineamiento del curso sin depender de un endpoint que no existirá.
- Mismo patrón de adaptador propio y reemplazable que el pago simulado ([ADR-0014](ADR-0014-pago-simulado-detras-de-paymentgateway.md)).

**Negativas y riesgos aceptados**
- La verificación no se comparte con otros canales (Marketplace, Retail) ni con el perfil de Seguridad: limitación conocida mientras A2 siga fuera de alcance.
- El canal pasa a guardar el celular completo, sin plazo de retención definido (`privacidad.md` §2).

## Referencias

- `openspec/specs/validacion-celular/spec.md` Contexto (líneas 11-15), Alcance (líneas 20-23), Fuera de alcance (línea 31), Req. 1 y 2
- `openspec/specs/validacion-celular/design.md`
- `docs/contratos-integracion.md` §2.2 (líneas 74-75), §3.1 (línea 162) y §6, acuerdo A2 (línea 256)
- `docs/modelo-datos.md` tabla `celular_verificacion_local`
