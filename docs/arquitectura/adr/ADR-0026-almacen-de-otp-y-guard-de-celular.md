# ADR-0026: Almacén de OTP y guard de celular verificado en el checkout

## Estado

Aceptada

## Fecha

2026-11-21 (decisión del dueño, D1 de la [auditoría](../../auditoria-specs-2026-11.md))

## Contexto

- [ADR-0015](ADR-0015-verificacion-propia-del-celular-por-otp.md) ya decidió que el chatbot verifica el celular con su propio OTP y `SimulatedSmsSender`, sin depender de Seguridad (acuerdo A2).
- El 2026-11-07 el equipo pospuso la implementación. La [auditoría 2026-11](../../auditoria-specs-2026-11.md) encontró que la tabla `local_phone_verification` solo guarda `customer_id`, `phone` y `verified_at`; no hay almacén de códigos, intentos ni reenvíos, el router de OTP no existe y el `CheckoutGuard` es un shim de `require_customer`.
- `validacion-celular/spec.md` exige 6 dígitos, 5 minutos, 3 intentos y 3 envíos cada 15 minutos, con un código que nunca pasa por el LLM.
- El dueño decidió retomar la implementación completa (D1, 2026-11-21): no se retira la verificación ni se deja el checkout sin guard.

## Decisión

1. **Separar el desafío de la prueba.** La tabla `local_phone_verification` sigue siendo el registro de verificaciones exitosas (solo inserción). Los desafíos OTP viven en una tabla propia, `phone_otp_challenge`, con `customer_id`, `phone`, `code_hash`, `expires_at`, `attempts`, `consumed_at` y `created_at`.
2. **Código hasheado.** El código de 6 dígitos se guarda solo como `HMAC-SHA256` con `PHONE_OTP_SECRET`; nunca en claro, en logs, en `message` ni en el prompt. La comparación se hace contra el hash del desafío vigente con comparación en tiempo constante.
3. **Un desafío activo por cliente.** Un nuevo `solicitar-otp` marca `consumed_at` en el anterior y crea otro; así no conviven códigos válidos. El contador de intentos se agota a los 3 fallos y el de reenvíos se calcula contando los desafíos creados en los últimos 15 minutos (`created_at`), no con una columna aparte.
4. **Puerto `SmsSender`.** La interfaz y `SimulatedSmsSender` se mantienen; el código solo se expone con `MODO_QA=true` en el entorno de pruebas. No se integra un proveedor SMS real.
5. **Endpoints propios.** `POST /api/v1/contacto/celular/solicitar-otp` (sin cuerpo; lee el celular vigente de `GET /auth/me`) y `POST /api/v1/contacto/celular/verificar-otp` (`{codigo}`). La respuesta y los errores están en `validacion-celular/design.md`.
6. **`CheckoutGuard` real.** `POST /checkout` compara el celular vigente del perfil con `local_phone_verification.phone` por valor exacto; si no coincide o no hay fila, responde `403 CELULAR_NO_VERIFICADO`. Si Seguridad no responde, el checkout se bloquea (no se omite la verificación).
7. **Bandera `REQUIRE_PHONE_VERIFICATION`.** Activa o desactiva el bloqueo por entorno. Supuesto explícito: por defecto `true` en producción y configurable a `false` para pruebas/demos; si el equipo adopta otro valor por defecto, se actualiza este ADR y la spec.
8. **Sin cambio de DAG.** `mod-auth` es dueño de los endpoints y escribe el desafío; `mod-checkout` solo lee la verificación a través del adaptador compartido de `shared/`. No se añade una dependencia directa `checkout → auth`.

**Límites de la decisión:** no cubre cambio de celular (es de Seguridad), SMS real, verificación compartida con otros canales ni el plazo de purga de desafíos vencidos. La retención queda pendiente y se registra en `modelo-datos.md`.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Guardar el OTP en columnas de `local_phone_verification` | Mezcla el desafío con la prueba exitosa: un envío nuevo tendría que borrar o sobrescribir una verificación válida, y se pierde la trazabilidad de `verified_at` |
| Guardar el código en claro | Un volcado de base o un log filtraría códigos válidos; la spec exige que no pase por el LLM ni por `message` |
| Usar Redis o memoria del proceso | Añade una dependencia operativa que el proyecto no tiene; el worker y las réplicas necesitan un almacén compartido y la base ya es la fuente de verdad |
| Mantener el `CheckoutGuard` como shim y no bloquear | Deja el requisito del curso sin cumplir y contradice `validacion-celular/spec.md`; fue el estado que la auditoría marcó como gap |
| Integrar un proveedor SMS real | Fuera de alcance (SPEC-04); el SMS es simulado en todo el curso |

## Consecuencias

**Positivas**

- El checkout exige una prueba real y el código nunca se almacena en claro.
- La verificación local sigue siendo reemplazable por el mecanismo de Seguridad sin tocar el resto del flujo.
- La separación desafío/prueba permite limpiar desafíos vencidos sin perder verificaciones históricas.

**Negativas y riesgos aceptados**

- Una tabla y una migración nuevas, más un job de purga cuyo plazo aún no está decidido.
- El checkout depende de `GET /auth/me`; si Seguridad no responde, se bloquea (decisión consciente: no se omite la verificación).
- La verificación no se comparte con Marketplace ni Retail mientras A2 siga fuera de alcance.
- El flag puede desactivar el guard en pruebas; si se configura mal en producción, el requisito no se cumple. Se mitiga con el valor por defecto `true` y una advertencia al arrancar cuando está desactivado.

## Referencias

- [`validacion-celular/spec.md`](../../../openspec/specs/validacion-celular/spec.md) y [`design.md`](../../../openspec/specs/validacion-celular/design.md)
- [`modelo-datos.md`](../../modelo-datos.md) — tablas `local_phone_verification` y `phone_otp_challenge`
- [ADR-0015](ADR-0015-verificacion-propia-del-celular-por-otp.md) — decisión original y actualización de implementación retomada
- [`auditoria-specs-2026-11.md`](../../auditoria-specs-2026-11.md) §4, D1
- [`contratos-integracion.md`](../../contratos-integracion.md) §2.2 y §2.8
