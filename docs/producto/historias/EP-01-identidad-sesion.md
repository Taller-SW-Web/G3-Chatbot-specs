# EP-01 · Identidad y sesión — Historias de usuario

> Specs: [SPEC-01](../../../openspec/specs/registro-cliente/spec.md), [SPEC-02](../../../openspec/specs/verificacion-correo/spec.md), [SPEC-03](../../../openspec/specs/inicio-sesion/spec.md), [SPEC-04](../../../openspec/specs/validacion-celular/spec.md) · Área `IDE` · 14 historias · 50 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento (DADO/CUANDO/ENTONCES). Aquí solo se resume cada uno en una línea.

---

## HU-IDE-01 · Abrir el formulario de registro desde el chat

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 3 | Hito 3 | `SPEC-01 · Req. 1` | RN-IDE-15 | — |

**Como** visitante sin cuenta, **quiero** que el chat me muestre un formulario de registro cuando digo que quiero crear una cuenta o intento una acción que la requiere, **para** registrarme sin salir de la conversación ni dictar mis datos por texto.

**Criterios de aceptación**
- `SPEC-01 · Req. 1 · Scenario: Intención de registro expresada en lenguaje natural` — la herramienta `solicitar_registro` responde con el bloque `FORMULARIO/REGISTRO`, sin pedir datos por texto.
- `SPEC-01 · Req. 1 · Scenario: Acción protegida sin sesión` — al pedir pagar sin sesión se ofrecen "Iniciar sesión" y "Crear cuenta" y se guarda `accionPendiente = INICIAR_CHECKOUT`.

**Prioridad:** Must, porque el checkout exige sesión y el registro es la puerta de entrada de un cliente nuevo.

---

## HU-IDE-02 · Crear mi cuenta con validación inmediata

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 5 | Hito 3 | `SPEC-01 · Req. 2–3` | RN-IDE-01, RN-IDE-02, RN-IDE-03, RN-IDE-04, RN-IDE-05, RN-IDE-06 | Seguridad ✅ (A1 ✅) |

**Como** visitante, **quiero** completar el formulario de registro con validación en tiempo real y recibir la confirmación de que mi cuenta se creó, **para** saber de inmediato si mis datos son correctos y qué hacer a continuación.

**Criterios de aceptación**
- `SPEC-01 · Req. 2 · Scenario: Formulario válido` — con todos los campos válidos, el botón se deshabilita, aparece el indicador de carga y se envía el registro.
- `SPEC-01 · Req. 2 · Scenario: Celular sin prefijo peruano` — 9 dígitos que empiezan por 9 se normalizan a `+51…`; otro formato bloquea el envío.
- `SPEC-01 · Req. 2 · Scenario: Contraseña que no cumple la política` — la lista de reglas se actualiza en tiempo real y bloquea el envío.
- `SPEC-01 · Req. 3 · Scenario: Cuenta creada` — ante `201`, el chat muestra el correo enmascarado, las acciones "Reenviar correo" e "Ya verifiqué, iniciar sesión", y conserva carrito y conversación.
- `SPEC-01 · Req. 3 · Scenario: Doble envío` — dos pulsaciones seguidas generan una sola petición a Seguridad.

**Prioridad:** Must, por ser el alta de clientes que habilita la compra.

**Notas:** incluye el rate limit de 5 registros por IP cada 10 minutos y la redacción de contraseñas en logs (RNF de SPEC-01).

---

## HU-IDE-03 · Recibir mensajes claros ante errores del registro

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 3 | Hito 3 | `SPEC-01 · Req. 4` | RN-IDE-07 | Seguridad ✅ |

**Como** visitante, **quiero** entender qué falló cuando mi registro no se completa, sin que el sistema revele si un correo ya tiene cuenta, **para** corregir mis datos o reintentar con confianza.

**Criterios de aceptación**
- `SPEC-01 · Req. 4 · Scenario: Correo no disponible` — ante `409 CORREO_NO_DISPONIBLE` se muestra un texto genérico y se ofrece "Iniciar sesión", sin afirmar que la cuenta existe.
- `SPEC-01 · Req. 4 · Scenario: Errores de validación del servidor` — cada error de `400 VALIDACION` aparece bajo su campo y se conservan los valores (salvo contraseñas).
- `SPEC-01 · Req. 4 · Scenario: Política incumplida en el servidor` — el detalle de `422 POLITICA_INCUMPLIDA` aparece en el campo contraseña.
- `SPEC-01 · Req. 4 · Scenario: Seguridad no disponible` — tras 5 s o un `5xx`, se informa el fallo, se conservan los datos y el BFF responde `503 SERVICIO_NO_DISPONIBLE`.

**Prioridad:** Must: sin este manejo, el registro filtraría la existencia de cuentas.

---

## HU-IDE-04 · Activar mi cuenta desde el enlace de verificación

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 3 | Hito 3 | `SPEC-02 · Req. 1` | RN-IDE-08 | Seguridad ✅; A1 ✅ (acción pendiente: informar la URL de `/verificar-correo`) |

**Como** cliente recién registrado, **quiero** abrir el enlace de mi correo y ver que mi cuenta quedó activa, **para** volver al chat e iniciar sesión.

**Criterios de aceptación**
- `SPEC-02 · Req. 1 · Scenario: Enlace válido` — se canjea el token, se muestra "¡Tu cuenta está activa!" y se vuelve a la app con el login abierto.
- `SPEC-02 · Req. 1 · Scenario: Enlace vencido` — ante `410 ENLACE_EXPIRADO` se ofrece pedir un enlace nuevo.
- `SPEC-02 · Req. 1 · Scenario: Enlace ya usado` — ante `410 ENLACE_YA_USADO` se informa que la cuenta ya fue verificada y se ofrece iniciar sesión.
- `SPEC-02 · Req. 1 · Scenario: Página sin token` — sin `token` no se llama al backend y se muestra el formulario de reenvío.

**Prioridad:** Must: el curso exige la validación del correo del cliente.

**Notas:** mientras Seguridad no configure la URL del canal (A1), el enlace cae al destino por defecto `WEB`; la historia no se puede demostrar de punta a punta sin esa configuración.

---

## HU-IDE-05 · Pedir un nuevo enlace de verificación

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 3 | Hito 3 | `SPEC-02 · Req. 2–3` | RN-IDE-07, RN-IDE-09, RN-IDE-10 | Seguridad ✅ |

**Como** cliente que no recibió o perdió el enlace, **quiero** pedir uno nuevo desde el chat, desde la página de verificación o desde el login fallido, **para** poder activar mi cuenta sin ayuda externa.

**Criterios de aceptación**
- `SPEC-02 · Req. 2 · Scenario: Reenvío aceptado` — ante `202` se muestra un mensaje neutro que no confirma la existencia de la cuenta.
- `SPEC-02 · Req. 2 · Scenario: Límite de reenvíos` — al cuarto reenvío en una hora se muestra el aviso de `429`.
- `SPEC-02 · Req. 3 · Scenario: Login rechazado` — todo `401 CREDENCIALES_INVALIDAS` muestra el enlace secundario de reenvío sin sugerir que esa sea la causa.
- `SPEC-02 · Req. 3 · Scenario: Reenvío desde la pista del login` — el formulario de reenvío llega con el correo del login precargado.

**Prioridad:** Must: sin reenvío, un enlace vencido deja al cliente sin forma de activar su cuenta.

---

## HU-IDE-06 · Iniciar sesión con correo y contraseña

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 5 | Hito 3 | `SPEC-03 · Req. 1` | RN-IDE-10, RN-IDE-11, RN-IDE-13, RN-IDE-18 | Seguridad ✅ |

**Como** cliente registrado, **quiero** iniciar sesión desde el chat sin perder la conversación, **para** acceder a las acciones que requieren mi cuenta.

**Criterios de aceptación**
- `SPEC-03 · Req. 1 · Scenario: Login exitoso sin MFA` — se fija la cookie `chat_rt`, el frontend recibe el access token, el chat saluda por nombre y la conversación queda ligada al cliente.
- `SPEC-03 · Req. 1 · Scenario: Credenciales inválidas o cuenta no disponible` — se muestra un único mensaje genérico, se limpia la contraseña y se ofrece el reenvío de verificación.
- `SPEC-03 · Req. 1 · Scenario: Usuario sin rol CLIENTE` — se descartan los tokens, se cierra la sesión en Seguridad y se informa que la cuenta no puede comprar en este canal.

**Prioridad:** Must: el checkout, los pedidos y la postventa requieren sesión.

**Notas:** incluye la persistencia del access token en `chatStore` con LocalStorage y la restauración al recargar (riesgo XSS aceptado, README §1.4).

---

## HU-IDE-07 · Completar el inicio de sesión con segundo factor

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 5 | Hito 3 | `SPEC-03 · Req. 2` | RN-IDE-12 | Seguridad ✅ |

**Como** cliente con MFA activado, **quiero** ingresar el código que recibo por correo o SMS, **para** completar mi inicio de sesión en el chat.

**Criterios de aceptación**
- `SPEC-03 · Req. 2 · Scenario: Login con MFA por correo` — se guarda el `challengeToken` en cookie de 5 min, se solicita el código y se muestra `OtpInput` con cuenta regresiva de 5:00.
- `SPEC-03 · Req. 2 · Scenario: Código incorrecto` — se informan los intentos restantes y se limpia el campo.
- `SPEC-03 · Req. 2 · Scenario: Intentos agotados o código vencido` — se pide un código nuevo y se habilita "Reenviar código".
- `SPEC-03 · Req. 2 · Scenario: Límite de reenvíos de OTP` — la cuarta solicitud en 15 min muestra el aviso de `429` con temporizador.
- `SPEC-03 · Req. 2 · Scenario: Cambio a canal SMS` — el código se solicita por SMS y se muestra el celular enmascarado.

**Prioridad:** Must: una cuenta con MFA no puede entrar sin este paso.

---

## HU-IDE-08 · Retomar lo que estaba haciendo tras iniciar sesión

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 3 | Hito 3 | `SPEC-03 · Req. 3` | RN-IDE-15 | — |

**Como** cliente que tuvo que iniciar sesión a mitad de una acción, **quiero** que el chat continúe automáticamente con esa acción, **para** no tener que repetir lo que ya había pedido.

**Criterios de aceptación**
- `SPEC-03 · Req. 3 · Scenario: Login desde el intento de pago` — con `accionPendiente = INICIAR_CHECKOUT` el chat continúa al checkout y limpia la acción pendiente.
- `SPEC-03 · Req. 3 · Scenario: Login sin acción pendiente` — el chat saluda y ofrece "Ver mis pedidos", "Seguir comprando" y "Ver carrito".

**Prioridad:** Must: evita perder la compra en el punto de mayor abandono.

**Notas:** la continuación al checkout se demuestra de punta a punta en Hito 4, cuando exista SPEC-14.

---

## HU-IDE-09 · Conservar mi carrito anónimo al iniciar sesión

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 3 | Hito 3 | `SPEC-03 · Req. 4` | RN-IDE-16, RN-CAR-01, RN-CAR-07 | Productos 🟡 (A5, disponibilidad) |

**Como** visitante que armó un carrito antes de iniciar sesión, **quiero** que esos productos se unan a mi carrito de cliente, **para** no tener que agregarlos otra vez.

**Criterios de aceptación**
- `SPEC-03 · Req. 4 · Scenario: Ambos carritos con ítems` — las cantidades por SKU se suman (sujetas a stock y al tope de 10), el anónimo queda `FUSIONADO` y el chat informa la unión.
- `SPEC-03 · Req. 4 · Scenario: La fusión excede el stock` — la cantidad se ajusta al disponible y se informa el ajuste por línea.

**Prioridad:** Must: perder el carrito al autenticarse rompe el flujo de compra.

**Notas:** depende de HU-CAR-01 (validación de stock) y HU-CAR-05 (carrito persistido).

---

## HU-IDE-10 · Mantener mi sesión activa de forma segura

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 5 | Hito 3 | `SPEC-03 · Req. 5` | RN-IDE-13, RN-IDE-14 | Seguridad ✅ (JWKS) |

**Como** cliente autenticado, **quiero** que mi sesión se renueve sola mientras converso y que termine de forma clara si deja de ser válida, **para** no perder el hilo por un vencimiento de 15 minutos.

**Criterios de aceptación**
- `SPEC-03 · Req. 5 · Scenario: Renovación silenciosa` — una única renovación atiende las peticiones concurrentes y la petición original se reintenta.
- `SPEC-03 · Req. 5 · Scenario: Refresh inválido o reutilizado` — se limpia la sesión, se informa que terminó y la conversación sigue como anónima.
- `SPEC-03 · Req. 5 · Scenario: JWKS no disponible con caché vigente` — el token se valida con la copia en caché que contiene su `kid`.

**Prioridad:** Must: sin renovación, la sesión caería cada 15 minutos en medio de la compra.

---

## HU-IDE-11 · Cerrar sesión

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 2 | Hito 3 | `SPEC-03 · Req. 6` | RN-IDE-17 | Seguridad ✅ |

**Como** cliente autenticado, **quiero** cerrar mi sesión desde el menú o escribiéndolo, **para** proteger mi cuenta en un dispositivo compartido.

**Criterios de aceptación**
- `SPEC-03 · Req. 6 · Scenario: Logout desde el menú o por texto` — se cierra la sesión en Seguridad, se borran cookie y token, y la conversación continúa anónima con carrito vacío.
- `SPEC-03 · Req. 6 · Scenario: Logout con Seguridad caída` — el cierre local se completa igual y se registra el fallo.

**Prioridad:** Must, por ser la mitigación básica del riesgo de token en LocalStorage.

---

## HU-IDE-12 · Verificar mi celular antes del primer pago

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 3 | Hito 4 | `SPEC-04 · Req. 1` | RN-IDE-19 | Seguridad ✅ (`GET /auth/me`); A2 ✅ (decidido fuera de alcance de Seguridad) |

**Como** cliente autenticado que va a pagar, **quiero** que el sistema me pida confirmar mi celular solo cuando no está verificado para el número actual, **para** asegurar que la entrega se coordine con un número que controlo.

**Criterios de aceptación**
- `SPEC-04 · Req. 1 · Scenario: Primer checkout con celular sin verificar` — se responde `403 CELULAR_NO_VERIFICADO`, se muestra el bloque `FORMULARIO/OTP_CELULAR` y se guarda `accionPendiente`.
- `SPEC-04 · Req. 1 · Scenario: Celular ya verificado` — el checkout continúa sin pedir verificación.
- `SPEC-04 · Req. 1 · Scenario: El cliente cambió su celular desde la última verificación` — el número nuevo exige verificarse otra vez, detectado automáticamente.

**Prioridad:** Must: el curso exige la validación del número celular del cliente.

---

## HU-IDE-13 · Recibir y validar el código de mi celular

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Must | 5 | Hito 4 | `SPEC-04 · Req. 2` | RN-IDE-20 | — (adaptador SMS propio y simulado) |

**Como** cliente que debe verificar su celular, **quiero** recibir un código y validarlo con reglas claras de vigencia e intentos, **para** completar la verificación y seguir con el pago.

**Criterios de aceptación**
- `SPEC-04 · Req. 2 · Scenario: Verificación exitosa` — se guarda la verificación local y se ejecuta la acción pendiente.
- `SPEC-04 · Req. 2 · Scenario: Código incorrecto` — se informan los intentos restantes; al agotar 3 se exige un código nuevo.
- `SPEC-04 · Req. 2 · Scenario: Código vencido` — tras 5 minutos se informa el vencimiento y se habilita "Enviar otro código".
- `SPEC-04 · Req. 2 · Scenario: Límite de envíos` — tras 3 envíos en 15 minutos se muestra el aviso con temporizador.

**Prioridad:** Must, porque completa el lineamiento de validación del celular.

**Notas:** el código solo se expone en pruebas con `MODO_QA=true` (RNF de SPEC-04).

---

## HU-IDE-14 · Recibir orientación si el celular no es el mío o verificarlo por iniciativa propia

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-01 | Should | 2 | Hito 4 | `SPEC-04 · Req. 3` | RN-IDE-21 | Seguridad ✅ (`GET /auth/me`) |

**Como** cliente autenticado, **quiero** saber qué hacer si el celular registrado no es el mío y poder verificarlo cuando yo lo decida, **para** resolverlo sin perder mi carrito.

**Criterios de aceptación**
- `SPEC-04 · Req. 3 · Scenario: El cliente indica que el número no es el suyo` — el chat explica que el cambio se hace en el perfil, muestra el enlace y conserva el carrito.
- `SPEC-04 · Req. 3 · Scenario: Verificación iniciada por el cliente` — se muestra el estado actual o se inicia el flujo de HU-IDE-13.

**Prioridad:** Should: mejora la experiencia, pero el flujo obligatorio ya se cubre con HU-IDE-12 y HU-IDE-13.

---

## Asignación del desglose (`design.md`) a historias

Cada tarea de "Desglose para issues" se numera `T1…Tn` en el orden en que aparece en el `design.md` de su spec, y se crea como sub-issue de la historia indicada. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-01 | T1 `[FE]` AuthModal → HU-IDE-01 · T2 `[FE]` RegistroForm → HU-IDE-02 · T3 `[FE]` PasswordPolicyChecklist → HU-IDE-02 · T4 `[FE]` mapeo de errores → HU-IDE-03 · T5 `[BE]` `POST /sesion/registro` → HU-IDE-02 · T6 `[BE]` `GET /sesion/politica-contrasena` → HU-IDE-02 · T7 `[INT]` `SeguridadClient.registrar` contra Prism → HU-IDE-03 · T8 `[BE]` herramienta `solicitar_registro` → HU-IDE-01 · T9 `[BE]` filtro de logs → HU-IDE-02 · T10 `[QA]` → HU-IDE-01, 02, 03 |
| SPEC-02 | T1 `[FE]` VerificarCorreoPage → HU-IDE-04 · T2 `[FE]` ReenviarVerificacionForm → HU-IDE-05 · T3 `[FE]` abrir AuthModal por URL → HU-IDE-04 · T4 `[BE]` proxies de verificación y reenvío → HU-IDE-04 · T5 `[BE]` herramienta `reenviar_verificacion` → HU-IDE-05 · T6 `[INT]` pruebas contra Prism → HU-IDE-04 · T7 `[INT]` URL del enlace (A1) → HU-IDE-04 · T8 `[QA]` → HU-IDE-04, 05 |
| SPEC-03 | T1 `[FE]` LoginForm → HU-IDE-06 · T2 `[FE]` MfaStep/OtpInput → HU-IDE-07 · T3 `[FE]` slice de sesión en `chatStore` → HU-IDE-06 · T4 `[FE]` interceptor con refresh único → HU-IDE-10 · T5 `[FE]` SesionIndicator y menú → HU-IDE-11 · T6 `[BE]` endpoints de sesión → HU-IDE-06 · T7 `[BE]` JwtValidator → HU-IDE-10 · T8 `[BE]` `SesionService.post_login` → HU-IDE-08 (relacionada: HU-IDE-09) · T9 `[BE]` herramientas `solicitar_login`/`cerrar_sesion` → HU-IDE-06 · T10 `[INT]` pruebas contra Prism → HU-IDE-06 · T11 `[QA]` → HU-IDE-06 a HU-IDE-11 |
| SPEC-04 | T1 `[BE]` tabla `celular_verificacion_local` → HU-IDE-13 · T2 `[BE]` `SmsSender` → HU-IDE-13 · T3 `[BE]` endpoints OTP → HU-IDE-13 · T4 `[BE]` `CheckoutGuard` → HU-IDE-12 · T5 `[BE]` herramienta `verificar_celular` → HU-IDE-14 · T6 `[FE]` bloque `OTP_CELULAR` → HU-IDE-12 · T7 `[QA]` → HU-IDE-12, 13, 14 · T8 `[INT]` (opcional) → no se crea salvo que aparezca un caso concreto (A2) |
