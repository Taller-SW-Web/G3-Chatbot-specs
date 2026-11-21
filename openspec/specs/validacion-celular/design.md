# Diseño: Validación local de celular por OTP

> Origen: SPEC-04 · Especificación de comportamiento: [`spec.md`](spec.md) · Decisión: [ADR-0026](../../../docs/arquitectura/adr/ADR-0026-almacen-de-otp-y-guard-de-celular.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Seguridad | `GET /auth/me` → `celular` (solo para saber qué número está vigente hoy) | ✅ |
| Seguridad | Mecanismo de validación de celular por canal | ✅ **Decidido fuera de alcance del ciclo** (acuerdo A2, acta de integración 23/09) — no se vuelve a asumir como pendiente; se reevalúa en Hito 4 solo si se abre un issue nuevo con un caso concreto |
| Propio | `POST /contacto/celular/solicitar-otp` y `POST /contacto/celular/verificar-otp` | 🟡 En implementación (D1, 2026-11-21) |

## Frontend

| Componente | Responsabilidad |
|---|---|
| Bloque `FORMULARIO/OTP_CELULAR` | Muestra el celular enmascarado y los botones "Enviar código" y "Ese no es mi número". |
| `OtpInput` (reutilizado de SPEC-03) | Ingreso del código, temporizador y reenvío. |
| `chatStore` (slice de sesión) | No depende de `celularVerificado` de Seguridad; el estado de verificación se consulta al backend propio del chatbot. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/contacto/celular/solicitar-otp` | Exige sesión `CLIENTE`; lee el celular vigente de `GET /auth/me`, genera un desafío y lo envía por `SmsSender`. No acepta un celular arbitrario en el cuerpo. |
| `POST /api/v1/contacto/celular/verificar-otp` | Valida el código contra el hash del desafío vigente, marca el desafío como consumido y guarda `local_phone_verification`; ejecuta la `accionPendiente`. |
| `SmsSender` (interfaz) + `SimulatedSmsSender` | Adaptador propio, reemplazable. El código solo se expone con `MODO_QA=true` y nunca en producción. |
| `CheckoutGuard.exigir_celular_verificado()` | Compara el `celular` vigente en `GET /auth/me` contra `local_phone_verification.phone` del cliente; exige coincidencia exacta. Si `REQUIRE_PHONE_VERIFICATION=false`, no bloquea. |
| Herramienta LLM `verificar_celular` | Devuelve el estado o el bloque de formulario; no recibe ni devuelve el código. |
| Tabla `phone_otp_challenge` | Desafío OTP vigente: `customer_id`, `phone`, `code_hash` (HMAC-SHA256 con `PHONE_OTP_SECRET`), `expires_at`, `attempts`, `consumed_at`, `created_at` (ver `modelo-datos.md`). |
| Tabla `local_phone_verification` | Verificación exitosa, solo inserción: `{customer_id, phone, verified_at}`. No guarda el código ni los intentos. |

### Endpoints propios

| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| POST | `/contacto/celular/solicitar-otp` | `CLIENTE` | Sin cuerpo (o `{}`). Responde `202 {enviado: true, celularEnmascarado, expiraEn}`. Con `MODO_QA=true` agrega `codigo` únicamente en el entorno de pruebas. |
| POST | `/contacto/celular/verificar-otp` | `CLIENTE` | Cuerpo `{ "codigo": "123456" }`. Responde `200 {celularVerificado: true, celularEnmascarado}`. |

**Supuesto explícito:** el contrato anterior es el que ya usan el backend y el frontend en las ramas de implementación; si cambia, se actualizan el `design.md`, el OpenAPI y el manifiesto del frontend en el mismo cambio.

### Errores

| `code` | HTTP | Cuándo |
|---|---|---|
| `VALIDACION` | 400 | El código no tiene exactamente 6 dígitos o falta el cuerpo esperado. |
| `CODIGO_INVALIDO` | 401 | Código incorrecto; incluye `intentosRestantes` (`0..2`). |
| `OTP_INTENTOS_AGOTADOS` | 401 | Se agotaron los 3 intentos; hay que solicitar un código nuevo. |
| `CODIGO_VENCIDO` | 410 | El desafío superó los 5 minutos o ya fue consumido. |
| `LIMITE_REENVIOS` | 429 | Se superaron los 3 envíos en 15 minutos; incluye `reintentarEn` y `Retry-After`. |
| `CELULAR_NO_DISPONIBLE` | 409 | El perfil no tiene un celular válido que verificar (supuesto explícito; si el equipo prefiere `422`, se ajusta en el PR). |
| `SERVICIO_NO_DISPONIBLE` | 503 | Seguridad no responde al leer el celular vigente; el checkout queda bloqueado, no se omite la verificación. |
| `CELULAR_NO_VERIFICADO` | 403 | `POST /checkout` con `REQUIRE_PHONE_VERIFICATION=true` y sin verificación vigente para el número actual. |

### Reglas de vigencia y límites

- Un desafío nuevo invalida el anterior del mismo `customer_id` y número (marca `consumed_at`); solo puede haber uno vigente por cliente.
- La comparación con `local_phone_verification` es por valor exacto del celular (`+51` + 9 dígitos). Si el perfil cambia de número, la verificación anterior no aplica.
- El código se guarda como HMAC-SHA256 con `PHONE_OTP_SECRET`; el hash no se devuelve, no se loguea y no se envía al LLM.
- Los intentos se reinician con cada desafío nuevo. El límite de reenvíos se calcula contando los desafíos creados para el cliente en los últimos 15 minutos (`created_at`), no con un contador aparte; la ventana se cuenta desde el primer envío.
- La bandera `REQUIRE_PHONE_VERIFICATION` se lee al arranque. Supuesto explícito: por defecto `true` en producción; `false` solo para pruebas/demos.

## Desglose para issues

- [ ] `[BE]` Tabla `phone_otp_challenge` y migración; `local_phone_verification` se mantiene solo para verificaciones exitosas
- [ ] `[BE]` `SmsSender` (interfaz) y `SimulatedSmsSender` con `MODO_QA`
- [ ] `[BE]` Endpoints `contacto/celular/solicitar-otp` y `/verificar-otp`, totalmente propios
- [ ] `[BE]` `CheckoutGuard` comparando el celular vigente contra la verificación local, con la bandera `REQUIRE_PHONE_VERIFICATION`
- [ ] `[BE]` Herramienta `verificar_celular`
- [ ] `[FE]` Bloque `FORMULARIO/OTP_CELULAR` reutilizando `OtpInput`
- [ ] `[QA]` Pruebas de todos los escenarios, incluido el cambio de celular que invalida la verificación previa, el reenvío, el código consumido y la bandera desactivada
- [ ] `[INT]` (opcional, Hito 4) Si surge un caso concreto que el registro no cubra, abrir un issue con la etiqueta `integracion` en el repo de Seguridad, citando el acta de integración y el caso puntual
