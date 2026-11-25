# ADR-0026: Almacén de OTP y guard de contacto verificado en el checkout

## Estado

Aceptada; actualizada el 2026-11-25 (contacto verificado por correo, celular opcional)

## Fecha

2026-11-21 (decisión del dueño, D1 de la [auditoría](../../auditoria-specs-2026-11.md)); actualización de política 2026-11-25 (D2 de [`validacion-celular/spec.md`](../../../openspec/specs/validacion-celular/spec.md))

## Contexto

- [ADR-0015](ADR-0015-verificacion-propia-del-celular-por-otp.md) ya decidió que el chatbot verifica el celular con su propio OTP y `SimulatedSmsSender`, sin depender de Seguridad (acuerdo A2).
- El 2026-11-07 el equipo pospuso la implementación. La [auditoría 2026-11](../../auditoria-specs-2026-11.md) encontró que la tabla `local_phone_verification` solo guarda `customer_id`, `phone` y `verified_at`; no hay almacén de códigos, intentos ni reenvíos, el router de OTP no existe y el `CheckoutGuard` es un shim de `require_customer`.
- `validacion-celular/spec.md` exige 6 dígitos, 5 minutos, 3 intentos y 3 envíos cada 15 minutos, con un código que nunca pasa por el LLM.
- El dueño decidió retomar la implementación completa (D1, 2026-11-21): no se retira la verificación ni se deja el checkout sin guard.
- El 2026-11-25 se aprobó un cambio de política (D2): el correo de la cuenta se verifica al registrarse y G7 no permite iniciar sesión sin verificarlo, así que toda cuenta activa ya tiene un contacto verificado. El OTP de celular pasa a ser opcional y el checkout deja de exigirlo; `CONTACTO_NO_VERIFICADO` queda como error defensivo.

## Decisión

1. **Separar el desafío de la prueba.** La tabla `local_phone_verification` sigue siendo el registro de verificaciones exitosas (solo inserción). Los desafíos OTP viven en una tabla propia, `phone_otp_challenge`, con `customer_id`, `phone`, `code_hash`, `expires_at`, `attempts`, `consumed_at` y `created_at`.
2. **Código hasheado.** El código de 6 dígitos se guarda solo como `HMAC-SHA256` con `PHONE_OTP_SECRET`; nunca en claro, en logs, en `message` ni en el prompt. La comparación se hace contra el hash del desafío vigente con comparación en tiempo constante.
3. **Un desafío activo por cliente.** Un nuevo `solicitar-otp` marca `consumed_at` en el anterior y crea otro; así no conviven códigos válidos. El contador de intentos se agota a los 3 fallos y el de reenvíos se calcula contando los desafíos creados en los últimos 15 minutos (`created_at`), no con una columna aparte.
4. **Puerto `SmsSender`.** La interfaz y `SimulatedSmsSender` se mantienen; el código solo se expone con `MODO_QA=true` en el entorno de pruebas. No se integra un proveedor SMS real.
5. **Endpoints propios.** `POST /api/v1/contacto/celular/solicitar-otp` (sin cuerpo; lee el celular vigente de `GET /auth/me`) y `POST /api/v1/contacto/celular/verificar-otp` (`{codigo}`). La respuesta y los errores están en `validacion-celular/design.md`.
6. **`CheckoutGuard` de contacto.** En el modo por defecto (`REQUIRE_VERIFIED_CONTACT=true`, `REQUIRE_PHONE_VERIFICATION=false`), `POST /checkout` considera verificado el correo del perfil (`GET /auth/me`); el celular es opcional y una fila vigente en `local_phone_verification` para el número actual también satisface el guard. Si no hay correo, Seguridad no responde o la sesión no es válida, responde `403 CONTACTO_NO_VERIFICADO` con `motivo` (`SIN_CONTACTO_VERIFICADO`, `SEGURIDAD_NO_DISPONIBLE`, `SIN_SESION`) y `celularEnmascarado` opcional. El snapshot del pedido usa el correo del perfil, no el `email` que envíe el cliente.
7. **Banderas y precedencia.** `REQUIRE_PHONE_VERIFICATION=true` conserva el modo legado y exige solo el celular verificado (`403 CELULAR_NO_VERIFICADO`), con precedencia sobre el flag nuevo. Si está en `false`, `REQUIRE_VERIFIED_CONTACT` controla el guard por correo o celular verificado. Con ambos en `false` no hay guard, solo para pruebas/demos. Supuesto explícito: en producción `REQUIRE_VERIFIED_CONTACT=true` y `REQUIRE_PHONE_VERIFICATION=false`; si el equipo adopta otros valores por defecto, se actualizan este ADR y la spec.
8. **Sin cambio de DAG.** `mod-auth` es dueño de los endpoints y escribe el desafío; `mod-checkout` solo lee la verificación a través del adaptador compartido de `shared/`. No se añade una dependencia directa `checkout → auth`.

**Límites de la decisión:** no cubre cambio de celular (es de Seguridad), SMS real, verificación compartida con otros canales, verificación del correo (la hace G7 en el registro) ni el plazo de purga de desafíos vencidos. La retención queda pendiente y se registra en `modelo-datos.md`.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Guardar el OTP en columnas de `local_phone_verification` | Mezcla el desafío con la prueba exitosa: un envío nuevo tendría que borrar o sobrescribir una verificación válida, y se pierde la trazabilidad de `verified_at` |
| Guardar el código en claro | Un volcado de base o un log filtraría códigos válidos; la spec exige que no pase por el LLM ni por `message` |
| Usar Redis o memoria del proceso | Añade una dependencia operativa que el proyecto no tiene; el worker y las réplicas necesitan un almacén compartido y la base ya es la fuente de verdad |
| Mantener el `CheckoutGuard` como shim y no bloquear | Deja el checkout sin guard de contacto y contradice `validacion-celular/spec.md`; fue el estado que la auditoría marcó como gap |
| Integrar un proveedor SMS real | Fuera de alcance (SPEC-04); el SMS es simulado en todo el curso |
| Seguir exigiendo el OTP de celular en cada compra | Duplica la garantía del correo verificado por G7, agrega fricción y contradice la política aprobada el 2026-11-25 (D2) |
| Confiar en el `email` que envía el cliente en `contacto` | No es un contacto verificado; el guard y el snapshot deben usar el correo del perfil |

## Consecuencias

**Positivas**

- El checkout ya no exige un paso adicional al cliente: el correo verificado en el registro es el contacto por defecto y el OTP de celular queda como opción voluntaria.
- El código OTP nunca se almacena en claro y el celular sigue siendo verificable cuando el cliente lo necesita.
- La verificación local sigue siendo reemplazable por el mecanismo de Seguridad sin tocar el resto del flujo.
- La separación desafío/prueba permite limpiar desafíos vencidos sin perder verificaciones históricas.

**Negativas y riesgos aceptados**

- Una tabla y una migración nuevas, más un job de purga cuyo plazo aún no está decidido.
- El checkout depende de `GET /auth/me` para leer el correo y falla cerrado: si Seguridad no responde, responde `403 CONTACTO_NO_VERIFICADO` (`SEGURIDAD_NO_DISPONIBLE`). No se omite el guard.
- El OTP deja de ser requisito para comprar en el modo por defecto; su valor pasa a ser opcional y no bloquea el checkout.
- La verificación no se comparte con Marketplace ni Retail mientras A2 siga fuera de alcance.
- Si un perfil no expone correo, el cliente no puede comprar hasta que G7 lo corrija; es el caso defensivo que cubre `CONTACTO_NO_VERIFICADO`.
- Los flags pueden desactivar el guard en pruebas; si se configuran mal en producción, el requisito no se cumple. Se mitiga con los valores por defecto (`REQUIRE_VERIFIED_CONTACT=true`, `REQUIRE_PHONE_VERIFICATION=false`) y una advertencia al arrancar cuando el guard queda desactivado.

## Referencias

- [`validacion-celular/spec.md`](../../../openspec/specs/validacion-celular/spec.md) (D1 y D2) y [`design.md`](../../../openspec/specs/validacion-celular/design.md)
- [`checkout-pago/spec.md`](../../../openspec/specs/checkout-pago/spec.md) — precondición de contacto verificado
- [`verificacion-correo/spec.md`](../../../openspec/specs/verificacion-correo/spec.md) — correo verificado por G7 como contacto de compra por defecto
- [`modelo-datos.md`](../../modelo-datos.md) — tablas `local_phone_verification` y `phone_otp_challenge`
- [ADR-0015](ADR-0015-verificacion-propia-del-celular-por-otp.md) — decisión original y actualización de implementación retomada
- [`auditoria-specs-2026-11.md`](../../auditoria-specs-2026-11.md) §4, D1
- [`contratos-integracion.md`](../../contratos-integracion.md) §2.2 y §2.8
