# Verificación de correo

> Origen: SPEC-02 · Grupo: Identidad · Requiere sesión: No · Depende de: [`registro-cliente`](../registro-cliente/spec.md) (SPEC-01), Seguridad (SPEC-02 de Seguridad)

## Purpose

Que el cliente active su cuenta desde el enlace recibido y vuelva al chat listo para iniciar sesión, pudiendo pedir un nuevo enlace si el anterior venció.

## Contexto

Tras el registro, la cuenta queda en `PENDIENTE_VERIFICACION` y no puede iniciar sesión. Seguridad envía un correo con un **enlace** (no un código) de un solo uso, válido por 24 horas. Ese token se canjea con `POST /auth/verificar-correo`.

El reenvío (`POST /auth/verificar-correo/reenviar`) responde siempre `202`, para no revelar qué cuentas existen, y admite 3 solicitudes por hora por correo.

🧩 **Acuerdo A1, resuelto (23/09/2026).** Habíamos pedido que el enlace de verificación llevara a nuestro propio frontend. Seguridad lo aceptó, pero con su propia forma: no se les envía una URL en la petición (sería una redirección abierta, con el token de verificación viajando en el enlace); en su lugar, el registro incluye `canalOrigen: "CHATBOT"` (lista cerrada: `WEB`, `CHATBOT`, `RETAIL`, `MARKETPLACE`, definida en su `RegistroRequest`), y Seguridad resuelve la URL de destino de su lado, con la configuración que le indiquemos. **Acción pendiente, no de diseño:** avisarles por issue cuál es nuestra URL exacta de `/verificar-correo` para que la configuren contra `CHATBOT`; mientras no se los digamos, el enlace cae al destino por defecto (`WEB`).

El curso exige al Canal Chatbot la "validación del correo del cliente"; esta spec la cubre.

## Alcance

Incluye:
- Página del frontend `/verificar-correo?token=...` que canjea el token.
- Mensajes de resultado: éxito, enlace vencido y enlace ya usado.
- Reenvío del enlace desde el chat o desde la página de resultado.
- Retorno a la conversación previa con el login abierto.

### Fuera de alcance

- Verificación por código OTP de correo: Seguridad usa enlace para el registro.
- Cambio de correo: es SPEC-16 de Seguridad (usa el mismo endpoint, pero no se ofrece desde el chatbot).
- Plantilla y envío del correo de verificación: los gestiona Seguridad.

## Requirements

### Requirement: Canje del enlace de verificación
El sistema DEBE (SHALL) canjear automáticamente el token al abrir la página de verificación y mostrar el resultado.

*Trazabilidad: SPEC-02 · Requisito 1.*

#### Scenario: Enlace válido
- **DADO** un token vigente y no usado
- **CUANDO** el cliente abre `/verificar-correo?token=abc`
- **ENTONCES** el frontend llama a `POST /api/v1/sesion/verificar-correo {token}`, Seguridad responde `204` y se muestra "¡Tu cuenta está activa!" con el botón "Volver al chat e iniciar sesión", que navega a la app con `AuthModal` abierto en la pestaña de login

#### Scenario: Enlace vencido
- **DADO** un token con más de 24 horas
- **CUANDO** se canjea
- **ENTONCES** Seguridad responde `410 ENLACE_EXPIRADO` y la página muestra "Este enlace venció" con un campo de correo y el botón "Enviarme un enlace nuevo"

#### Scenario: Enlace ya usado
- **DADO** un token que ya fue canjeado
- **CUANDO** se abre de nuevo
- **ENTONCES** Seguridad responde `410 ENLACE_YA_USADO` y la página muestra "Tu cuenta ya fue verificada" con el botón "Iniciar sesión"

#### Scenario: Página sin token
- **DADO** que se abre `/verificar-correo` sin el parámetro `token`
- **CUANDO** carga la página
- **ENTONCES** no se llama al backend y se muestra el formulario de reenvío

### Requirement: Reenvío del enlace
El sistema DEBE (SHALL) permitir solicitar un nuevo enlace indicando el correo y DEBE responder siempre con un mensaje neutro.

*Trazabilidad: SPEC-02 · Requisito 2.*

#### Scenario: Reenvío aceptado
- **DADO** un cliente que pulsa "Reenviar correo" en el chat o en la página
- **CUANDO** el BFF llama a `POST /auth/verificar-correo/reenviar` y recibe `202`
- **ENTONCES** se muestra "Si hay una cuenta pendiente con ese correo, te enviamos un enlace nuevo", sin confirmar la existencia de la cuenta

#### Scenario: Límite de reenvíos
- **DADO** un correo con 3 reenvíos en la última hora
- **CUANDO** se solicita el cuarto
- **ENTONCES** Seguridad responde `429 DEMASIADAS_SOLICITUDES` y se muestra "Ya enviamos varios enlaces. Revisa tu bandeja y spam, o intenta en una hora"

### Requirement: Pista ante cualquier login fallido
El sistema DEBE (SHALL) ofrecer siempre el reenvío del enlace cuando un login falla, sin afirmar que la causa sea la falta de verificación. 🧩 Seguridad confirmó que el login **nunca** distingue una contraseña incorrecta de una cuenta bloqueada, inactiva o sin verificar: todas responden `401 CREDENCIALES_INVALIDAS` por igual, a propósito, para no revelar el estado de la cuenta. Por eso el chatbot tampoco puede mostrar la pista solo "cuando corresponda" — la ofrece siempre que el login falla, como una opción más, nunca como un diagnóstico.

*Trazabilidad: SPEC-02 · Requisito 3.*

#### Scenario: Login rechazado
- **DADO** un login que devuelve `401 CREDENCIALES_INVALIDAS` (por cualquier causa)
- **CUANDO** se muestra el error
- **ENTONCES** el formulario muestra "Correo o contraseña incorrectos" junto con el enlace secundario "¿No verificaste tu correo? Reenviar verificación", sin dar a entender que esa sea la causa

#### Scenario: Reenvío desde la pista del login
- **DADO** que el cliente pulsa "Reenviar verificación" en el formulario de login
- **CUANDO** se abre el formulario de reenvío
- **ENTONCES** el campo correo viene precargado con el correo usado en el login

## Requisitos no funcionales

- **Seguridad:** el token de la URL no se registra en logs del frontend (analytics) ni del backend. La página hace `history.replaceState` para quitar el token de la barra de direcciones después del canje.
- **Privacidad:** ningún mensaje permite deducir si un correo está registrado.
- **Usabilidad:** la página de verificación funciona como una vista independiente de la app (no requiere que haya una conversación abierta) y es responsive.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
