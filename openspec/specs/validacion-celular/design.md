# Diseño: Validación local de celular por OTP

> Origen: SPEC-04 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Seguridad | `GET /auth/me` → `celular` (solo para saber qué número está vigente hoy) | ✅ |
| Seguridad | Mecanismo de validación de celular por canal | ✅ **Decidido fuera de alcance del ciclo** (acuerdo A2, acta de integración 23/09) — no se vuelve a asumir como pendiente; se reevalúa en Hito 4 solo si se abre un issue nuevo con un caso concreto |

## Frontend

| Componente | Responsabilidad |
|---|---|
| Bloque `FORMULARIO/OTP_CELULAR` | Muestra el celular enmascarado y los botones "Enviar código" y "Ese no es mi número". |
| `OtpInput` (reutilizado de SPEC-03) | Ingreso del código, temporizador y reenvío. |
| `chatStore` (slice de sesión) | No depende de `celularVerificado` de Seguridad; el estado de verificación se consulta al backend propio del chatbot. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/contacto/celular/solicitar-otp` | Genera el código, lo guarda con vigencia de 5 min y lo envía por `SmsSender`. |
| `POST /api/v1/contacto/celular/verificar-otp` | Valida el código, guarda `celular_verificado_local` y ejecuta la `accionPendiente`. |
| `SmsSender` (interfaz) + `SimulatedSmsSender` | Adaptador propio, reemplazable. |
| `CheckoutGuard.exigir_celular_verificado()` | Compara el `celular` vigente en `GET /auth/me` contra `celular_verificado_local.celular` del cliente; exige coincidencia exacta y vigencia. |
| Herramienta LLM `verificar_celular` | Devuelve el estado o el bloque de formulario. |
| Tabla `celular_verificacion_local` | Ver `modelo-datos.md`. |

## Desglose para issues

- [ ] `[BE]` Tabla `celular_verificacion_local` y migración
- [ ] `[BE]` `SmsSender` (interfaz) y `SimulatedSmsSender`
- [ ] `[BE]` Endpoints `contacto/celular/solicitar-otp` y `/verificar-otp`, totalmente propios
- [ ] `[BE]` `CheckoutGuard` comparando el celular vigente contra la verificación local
- [ ] `[BE]` Herramienta `verificar_celular`
- [ ] `[FE]` Bloque `FORMULARIO/OTP_CELULAR` reutilizando `OtpInput`
- [ ] `[QA]` Pruebas de todos los escenarios, incluido el caso de cambio de celular que invalida la verificación previa
- [ ] `[INT]` (opcional, Hito 4) Si surge un caso concreto que el registro no cubra, abrir un issue con la etiqueta `integracion` en el repo de Seguridad, citando el acta de integración y el caso puntual
