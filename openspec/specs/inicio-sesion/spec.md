# Inicio de sesión, MFA y gestión de sesión

> Origen: SPEC-03 · Grupo: Identidad · Requiere sesión: — · Depende de: Seguridad (SPEC-05, SPEC-06, SPEC-09 y SPEC-14 de Seguridad), [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`gestion-carrito`](../gestion-carrito/spec.md) (SPEC-11)

## Purpose

Autenticar al cliente desde el chat, con o sin MFA, y gestionar de forma segura su sesión (renovación y cierre), fusionando su carrito anónimo con el de su cuenta.

## Contexto

Seguridad autentica con correo y contraseña (`POST /auth/login`). Si la cuenta tiene segundo factor, responde con un `challengeToken` y exige un OTP de 6 dígitos (5 min, 3 intentos, 3 solicitudes cada 15 min).

Reglas del token:

- El `accessToken` dura 15 minutos.
- El `refreshToken` es de un solo uso: reutilizar uno viejo cierra todas las sesiones del usuario.
- Los tokens se validan en local con el JWKS.

El chatbot debe permitir iniciar sesión sin perder la conversación, retomar la acción que el cliente intentaba y mantener la sesión viva mientras conversa.

## Alcance

Incluye:
- Formulario de login (`AuthModal`, pestaña "Iniciar sesión").
- Flujo MFA: selección de canal (EMAIL o SMS), envío, ingreso del código, reintentos y reenvío.
- Gestión de tokens: el access token se guarda en `chatStore` respaldado por LocalStorage (decisión del equipo, ver README §1.4) y el refresh token vive en una cookie `httpOnly` gestionada por el backend.
- Renovación silenciosa del token y manejo de `REFRESCO_INVALIDO`.
- Validación local del JWT en el backend (JWKS cacheado, rol `CLIENTE`).
- Retoma de la acción pendiente tras el login.
- Fusión del carrito anónimo con el carrito del cliente.
- Cierre de sesión.

### Fuera de alcance

- Recuperación de contraseña: se muestra un enlace "¿Olvidaste tu contraseña?" hacia el flujo de Seguridad o del Marketplace; no se implementa en el chat.
- Activación o desactivación de MFA: es SPEC-10 de Seguridad.
- Inicio de sesión con redes sociales.

## Requirements

### Requirement: Inicio de sesión con correo y contraseña
El sistema DEBE (SHALL) autenticar al cliente contra Seguridad y, si no hay MFA, abrir la sesión: guardar el access token en `chatStore` respaldado por LocalStorage y el refresh token en cookie `httpOnly`.

*Trazabilidad: SPEC-03 · Requisito 1.*

#### Scenario: Login exitoso sin MFA
- **DADO** una cuenta activa sin MFA
- **CUANDO** el cliente envía correo y contraseña válidos
- **ENTONCES** el BFF recibe `accessToken` y `refreshToken`, fija la cookie `chat_rt` (`httpOnly; Secure; SameSite=Strict`), devuelve al frontend `{accessToken, expiresIn, usuario{id, nombreCompleto, correo}}`, y el chat saluda "Hola, María" y liga la conversación al `cliente_id`

#### Scenario: Credenciales inválidas o cuenta no disponible
- **DADO** una contraseña incorrecta, o una cuenta bloqueada, inactiva o sin verificar
- **CUANDO** Seguridad responde `401 CREDENCIALES_INVALIDAS`
- **ENTONCES** se muestra "Correo o contraseña incorrectos" sin indicar la causa real (Seguridad **no distingue** una contraseña mala de una cuenta no disponible; ambas devuelven el mismo código, a propósito, para no revelar el estado de la cuenta), se limpia el campo contraseña y se ofrece siempre el enlace "¿No verificaste tu correo? Reenviar verificación" (ver SPEC-02 Requisito 3), ya que el chatbot tampoco puede saber si ese fue el motivo

#### Scenario: Usuario sin rol CLIENTE
- **DADO** un login exitoso de un usuario cuyo token no contiene el rol `CLIENTE` (por ejemplo, un vendedor)
- **CUANDO** el BFF valida el token
- **ENTONCES** descarta los tokens, llama a `POST /auth/logout` y muestra "Esta cuenta no puede comprar desde este canal"

### Requirement: Segundo factor (MFA)
El sistema DEBE (SHALL) completar el login con OTP cuando Seguridad responde `mfaRequerido: true`.

*Trazabilidad: SPEC-03 · Requisito 2.*

#### Scenario: Login con MFA por correo
- **DADO** una cuenta con MFA
- **CUANDO** el login responde `{mfaRequerido: true, challengeToken, canal: EMAIL}`
- **ENTONCES** el BFF guarda el `challengeToken` en una cookie `httpOnly` de 5 min y solicita el código (`POST /auth/otp/solicitar`), y el frontend muestra `OtpInput` con "Enviamos un código a m****a@ejemplo.com" y una cuenta regresiva de 5:00

#### Scenario: Código incorrecto
- **DADO** un código erróneo
- **CUANDO** Seguridad responde `401 CODIGO_INVALIDO` con `intentosRestantes: 2`
- **ENTONCES** se muestra "Código incorrecto. Te quedan 2 intentos" y se limpia el campo

#### Scenario: Intentos agotados o código vencido
- **DADO** un tercer fallo (`OTP_INTENTOS_AGOTADOS`) o un código con más de 5 min (`410`)
- **CUANDO** se intenta verificar
- **ENTONCES** se muestra "Pide un código nuevo" y se habilita el botón "Reenviar código"

#### Scenario: Límite de reenvíos de OTP
- **DADO** 3 solicitudes de código en 15 minutos
- **CUANDO** se pide la cuarta
- **ENTONCES** se muestra "Espera unos minutos antes de pedir otro código" (`429`) y el botón se deshabilita con un temporizador

#### Scenario: Cambio a canal SMS
- **DADO** un cliente con celular registrado en el paso de OTP
- **CUANDO** elige "Enviar por SMS"
- **ENTONCES** se solicita el código con `canal: SMS` y se muestra el celular enmascarado (en desarrollo el SMS es simulado por Seguridad)

### Requirement: Retoma de la acción pendiente
El sistema DEBE (SHALL) ejecutar automáticamente, tras un login exitoso, la acción que el cliente intentaba antes de autenticarse (`conversacion.contexto.accionPendiente`).

*Trazabilidad: SPEC-03 · Requisito 3.*

#### Scenario: Login desde el intento de pago
- **DADO** `accionPendiente = INICIAR_CHECKOUT`
- **CUANDO** el login termina con éxito
- **ENTONCES** el chat continúa con el checkout (SPEC-12 a SPEC-14) sin que el cliente tenga que repetir "quiero pagar"
- **Y** se limpia `accionPendiente`

#### Scenario: Login sin acción pendiente
- **DADO** un login iniciado voluntariamente
- **CUANDO** termina con éxito
- **ENTONCES** el chat saluda y ofrece las acciones rápidas "Ver mis pedidos", "Seguir comprando" y "Ver carrito"

### Requirement: Fusión del carrito anónimo
El sistema DEBE (SHALL) fusionar el carrito anónimo de la conversación con el carrito activo del cliente al iniciar sesión.

*Trazabilidad: SPEC-03 · Requisito 4.*

#### Scenario: Ambos carritos con ítems
- **DADO** un carrito anónimo con 2 × SKU-A y un carrito del cliente con 1 × SKU-A y 1 × SKU-B
- **CUANDO** se inicia sesión
- **ENTONCES** el carrito resultante tiene 3 × SKU-A (sujeto a stock y al tope de 10, según SPEC-10 y SPEC-11) y 1 × SKU-B, el anónimo queda `FUSIONADO`, y el chat informa "Unimos los productos que agregaste con los de tu cuenta"

#### Scenario: La fusión excede el stock
- **DADO** que la suma de cantidades supera el stock disponible
- **CUANDO** se fusionan los carritos
- **ENTONCES** la cantidad se ajusta al disponible y se informa el ajuste por línea

### Requirement: Renovación y validación de la sesión
El sistema DEBE (SHALL) renovar el access token antes de que venza y DEBE validar cada petición protegida en local contra el JWKS de Seguridad.

*Trazabilidad: SPEC-03 · Requisito 5.*

#### Scenario: Renovación silenciosa
- **DADO** un access token a menos de 60 s de vencer o una respuesta `401 TOKEN_INVALIDO` del BFF
- **CUANDO** el frontend necesita hacer una petición
- **ENTONCES** llama una sola vez a `POST /api/v1/sesion/refresh` (las peticiones concurrentes esperan esa misma promesa), el BFF rota el refresh en la cookie y la petición original se reintenta

#### Scenario: Refresh inválido o reutilizado
- **DADO** que Seguridad responde `REFRESCO_INVALIDO`
- **CUANDO** se intenta renovar
- **ENTONCES** el BFF borra la cookie, el frontend limpia la sesión y el chat muestra "Tu sesión terminó, vuelve a iniciar sesión", conservando la conversación como anónima

#### Scenario: JWKS no disponible con caché vigente
- **DADO** que el JWKS no responde y hay una copia en caché con el `kid` del token
- **CUANDO** llega una petición
- **ENTONCES** el token se valida con la copia en caché (regla 2 del kit de Seguridad)

### Requirement: Cierre de sesión
El sistema DEBE (SHALL) cerrar la sesión en Seguridad y en el chatbot cuando el cliente lo pide.

*Trazabilidad: SPEC-03 · Requisito 6.*

#### Scenario: Logout desde el menú o por texto
- **DADO** un cliente autenticado
- **CUANDO** pulsa "Cerrar sesión" o escribe "cierra mi sesión"
- **ENTONCES** el BFF llama a `POST /auth/logout`, borra la cookie, el frontend descarta el token y la conversación continúa como anónima con un carrito vacío

#### Scenario: Logout con Seguridad caída
- **DADO** que Seguridad no responde al logout
- **CUANDO** el cliente cierra sesión
- **ENTONCES** el BFF borra igualmente la cookie y el token local, y registra el fallo en el log

## Requisitos no funcionales

- **Seguridad:** el access token se guarda en `chatStore` respaldado por LocalStorage (riesgo XSS aceptado, ver README §1.4) y el refresh token vive solo en la cookie `httpOnly`, nunca en LocalStorage. La cookie tiene `Path=/api/v1/sesion`. Hay protección CSRF en `/sesion/refresh` y `/sesion/logout` con la cabecera `X-Requested-With` y la verificación del `Origin`.
- **Seguridad:** la validación local verifica firma RS256, `iss=auth-service`, `exp` y `tipo=acceso`. El JWKS se cachea y se refresca ante un `kid` desconocido.
- **Mitigación XSS:** todo contenido que proviene del LLM o de otros módulos se sanitiza antes de renderizarse (nunca `dangerouslySetInnerHTML` con texto no controlado), el frontend aplica una cabecera `Content-Security-Policy` estricta y el access token es de vida corta (15 min), de modo que un XSS robe como máximo 15 minutos de sesión.
- **Continuidad:** al recargar la página se restaura el access token desde LocalStorage; si ya expiró o no existe, se intenta un refresh con la cookie.
- **Rendimiento:** la validación local del JWT tarda menos de 5 ms.
- **Bloqueos:** los bloqueos por intentos fallidos los aplica Seguridad (SPEC-14); el chatbot no implementa un contador propio.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen (se verifica que el refresh token nunca queda en LocalStorage y que al cerrar sesión se borra el access token de LocalStorage).
- No se han incorporado funcionalidades fuera del alcance.
