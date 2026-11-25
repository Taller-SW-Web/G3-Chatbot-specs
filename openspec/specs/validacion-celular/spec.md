# Validación local de celular por OTP

> Origen: SPEC-04 · Grupo: Identidad · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03)

## Responsables

- **Sebastian:** OTP propio (`SmsSender` simulado) y formulario del OTP en el chat.
- **Alonso:** herramienta `verificar_celular`.
- **Nikol (QA):** casos de prueba a partir de los escenarios, pruebas E2E si el flujo es crítico y validación contra la definición de terminado.

## Purpose

Garantizar que el cliente tenga un contacto verificado para coordinar su compra y la entrega: por defecto el correo de la cuenta, verificado por Seguridad (G7) al registrarse, y de forma opcional el celular mediante un código OTP simulado, sin depender de un endpoint de Seguridad que no existe este ciclo.

## Contexto

🧩 **Cambio de diseño (23/09/2026).** El chatbot había pedido a Seguridad un mecanismo para verificar el celular de un cliente por OTP (acuerdo A2, su RF-10.4). Seguridad respondió por escrito en su acta de integración: **decidido fuera de alcance de este ciclo**. Su justificación: el SMS es simulado hasta el final del curso y el correo del cliente ya queda verificado por el registro (SPEC-01/SPEC-02), así que no van a construir el mecanismo genérico por canal este semestre. Dejan la puerta abierta a reevaluarlo en el Hito 4 si aparece un caso concreto que el registro no cubra — pero no es algo con lo que se pueda contar para este diseño.

Esto significa que el chatbot **no puede depender de Seguridad** para esta capacidad: ni hay un endpoint para disparar el OTP, ni hay forma de escribir el atributo `celularVerificado` de Seguridad desde otro módulo (su ADR-006 confirma que las consultas y validaciones de contacto no se exponen entre módulos).

El curso exige igual la "validación del número celular ... del cliente" para este canal. La solución: el chatbot implementa su **propia** verificación, autocontenida, sin tocar el perfil de Seguridad. Es el mismo patrón que ya usa Ventas para su pasarela de pago simulada — un adaptador propio, reemplazable más adelante si Seguridad decide construir el mecanismo compartido.

🧩 **Cambio de política (25/11/2026).** El correo de la cuenta se verifica al registrarse y Seguridad (G7) no permite iniciar sesión sin verificarlo. Por eso, cualquier cuenta activa ya tiene un contacto verificado: su correo. Exigir además un OTP de celular en cada compra duplicaba una garantía que el registro ya da y agregaba fricción innecesaria. La política aprobada deja el **celular como verificación opcional**, disponible desde "Mi cuenta"; el checkout usa el **correo del perfil** como contacto verificado por defecto y no pide verificar nada al cliente. El OTP sigue implementado y `CONTACTO_NO_VERIFICADO` queda como error defensivo para perfiles sin correo, G7 caído o sesión inválida. La decisión D2 registra el cambio; D1 se conserva como historial.

## Alcance

Incluye:
- Verificación local (propia del chatbot) del celular vigente en el perfil del cliente (`GET /auth/me` → `celular`), disponible de forma opcional desde "Mi cuenta" o cuando el cliente la pide.
- Envío de un código OTP simulado y su verificación, con las mismas reglas de vigencia, intentos y límite de reenvíos que ya usa el resto del sistema (SPEC-03, SPEC-14).
- Persistencia local de "celular verificado" ligada al cliente **y** al número exacto verificado — si el celular cambia en el perfil, la verificación local queda invalidada automáticamente.
- Almacén de desafíos OTP separado del registro de verificaciones: código de 6 dígitos **hasheado**, vigencia de 5 minutos, intentos y reenvíos limitados.
- Bloqueo defensivo del checkout cuando no hay un contacto verificado: por defecto el correo del perfil; el celular verificado localmente se acepta como alternativa. Se controla con `REQUIRE_VERIFIED_CONTACT` (nuevo) y `REQUIRE_PHONE_VERIFICATION` (modo legado).
- Verificación iniciada por el cliente ("quiero verificar mi celular").

### Fuera de alcance

- Cambio del número celular: es responsabilidad de Seguridad (su SPEC-16), fuera de este canal.
- Proveedor SMS real: se simula, igual que el pago (SPEC-14).
- Exigir el OTP de celular como requisito obligatorio para comprar: el correo verificado del perfil es el contacto por defecto (D2). El modo legado con `REQUIRE_PHONE_VERIFICATION=true` se conserva solo por compatibilidad.
- Verificación del correo por OTP: el correo se valida con enlace, ya cubierto por el registro (SPEC-01/SPEC-02) — Seguridad confirmó que esto satisface el requisito y no hace falta duplicarlo.
- Compartir el estado de esta verificación con otros canales (Marketplace, Retail): es una verificación local del chatbot, no del perfil del cliente en Seguridad. Si el cliente compra por otro canal, ese canal no ve esta verificación (y viceversa) — limitación conocida, aceptable mientras A2 siga fuera de alcance.

## Requirements

### Requirement: Contacto verificado antes del checkout
El sistema DEBE (SHALL) impedir iniciar el checkout (SPEC-14) cuando el cliente no tenga un contacto verificado. Por defecto, el contacto verificado es el **correo de la cuenta**, que Seguridad (G7) verificó al registrarse y exige para iniciar sesión; el **celular es opcional** y una verificación local vigente se acepta como alternativa. En el modo por defecto, el checkout no DEBE pedir al cliente que verifique nada. Cuando no se pueda confirmar un contacto verificado —perfil sin correo, Seguridad no disponible o una sesión inválida en el momento del guard— el backend DEBE responder `403 CONTACTO_NO_VERIFICADO` con el `motivo` correspondiente y no crear el pedido.

*Trazabilidad: SPEC-04 · Requisito 1.*

#### Scenario: Cuenta activa con correo verificado y celular sin OTP
- **DADO** un cliente autenticado cuya cuenta está activa y cuyo correo fue verificado por Seguridad (G7) al registrarse, y que no tiene una verificación local de celular
- **CUANDO** intenta pagar
- **ENTONCES** el checkout continúa sin pedir OTP ni mostrar el bloque `FORMULARIO/OTP_CELULAR`
- **Y** el snapshot del pedido usa el correo del perfil, no el `email` que envíe el cliente

#### Scenario: Celular verificado localmente
- **DADO** un cliente con correo verificado y además una verificación local vigente para el celular que tiene hoy en su perfil
- **CUANDO** intenta pagar
- **ENTONCES** el checkout continúa; la verificación del celular se acepta como contacto alternativo, pero no es obligatoria para comprar

#### Scenario: Perfil sin correo (defensivo)
- **DADO** un cliente autenticado cuyo perfil no expone un correo
- **CUANDO** intenta pagar
- **ENTONCES** el backend responde `403 CONTACTO_NO_VERIFICADO` con `motivo: SIN_CONTACTO_VERIFICADO` y el chat muestra "No pudimos confirmar un contacto verificado para tu compra"
- **Y** no se crea el checkout ni el pedido

#### Scenario: Seguridad no disponible al leer el perfil (defensivo)
- **DADO** que `GET /auth/me` no responde o devuelve un error al iniciar el checkout
- **CUANDO** el guard intenta obtener el correo del perfil
- **ENTONCES** el backend responde `403 CONTACTO_NO_VERIFICADO` con `motivo: SEGURIDAD_NO_DISPONIBLE`
- **Y** el checkout queda bloqueado: nunca se omite el guard asumiendo un contacto verificado

#### Scenario: Modo legado con REQUIRE_PHONE_VERIFICATION=true
- **DADO** un entorno con `REQUIRE_PHONE_VERIFICATION=true`
- **CUANDO** un cliente con correo verificado pero sin verificación local del celular vigente intenta pagar
- **ENTONCES** se aplica el comportamiento anterior: el backend responde `403 CELULAR_NO_VERIFICADO` y el chat muestra "Para coordinar la entrega necesitamos confirmar tu celular +51 9****4321" con el bloque `FORMULARIO/OTP_CELULAR`
- **Y** se guarda `accionPendiente = INICIAR_CHECKOUT`; si el cliente cambió de celular, la verificación anterior no aplica al número nuevo y debe verificar el vigente

#### Scenario: Ambos flags desactivados
- **DADO** un entorno con `REQUIRE_PHONE_VERIFICATION=false` y `REQUIRE_VERIFIED_CONTACT=false`
- **CUANDO** el cliente inicia el checkout sin verificación local de celular
- **ENTONCES** el checkout no se bloquea por contacto; los endpoints de OTP siguen disponibles para una verificación voluntaria

### Requirement: Envío y verificación del código
El sistema DEBE (SHALL) generar y enviar un OTP de 6 dígitos por un adaptador SMS **propio y simulado**, y verificarlo con las mismas reglas que ya usa el resto del chatbot: 5 minutos de vigencia, 3 intentos, 3 envíos cada 15 minutos. El código DEBE (SHALL) guardarse solo como hash, nunca en claro, junto con su expiración, el contador de intentos y la ventana de reenvíos; un código consumido no se puede reutilizar y un nuevo envío invalida el desafío anterior.

*Trazabilidad: SPEC-04 · Requisito 2.*

#### Scenario: Verificación exitosa
- **DADO** un código enviado por el simulador
- **CUANDO** el cliente ingresa el código correcto
- **ENTONCES** se guarda localmente `{customer_id, phone, verified_at}`, el desafío queda consumido, el chat muestra "¡Listo! Tu celular quedó verificado" y se ejecuta la `accionPendiente` si existe (por ejemplo, `INICIAR_CHECKOUT`)

#### Scenario: Código incorrecto
- **DADO** un código erróneo
- **CUANDO** se verifica
- **ENTONCES** se muestra "Código incorrecto. Te quedan N intentos"; al agotar los 3, se exige solicitar un código nuevo

#### Scenario: Código vencido
- **DADO** un código con más de 5 minutos
- **CUANDO** se ingresa
- **ENTONCES** se muestra "El código venció" y se habilita "Enviar otro código"

#### Scenario: Límite de envíos
- **DADO** 3 envíos en 15 minutos
- **CUANDO** se pide otro
- **ENTONCES** se muestra "Espera unos minutos antes de pedir otro código" con un temporizador

#### Scenario: Reenvío dentro del límite
- **DADO** un cliente con 2 envíos en los últimos 15 minutos y un desafío vigente
- **CUANDO** pide un código nuevo
- **ENTONCES** se envía un código nuevo, el anterior deja de valer y queda 1 envío disponible en la ventana

#### Scenario: Código ya consumido
- **DADO** un código que ya se usó para verificar el celular
- **CUANDO** se intenta verificar de nuevo
- **ENTONCES** se rechaza con `410 CODIGO_VENCIDO` o `401 CODIGO_INVALIDO` y no se crea una segunda verificación

### Requirement: El celular es incorrecto
El sistema DEBE (SHALL) orientar al cliente si el celular registrado no es el suyo, sin permitir cambiarlo desde el chat (ese cambio es responsabilidad de Seguridad y queda fuera de este canal).

*Trazabilidad: SPEC-04 · Requisito 3.*

#### Scenario: El cliente indica que el número no es el suyo
- **DADO** el paso de verificación
- **CUANDO** el cliente pulsa "Ese no es mi número" o lo escribe
- **ENTONCES** el chat explica que el cambio de celular se hace desde su perfil fuera del chatbot y conserva el carrito
- **Y** muestra un enlace al perfil solo si hay una URL externa configurada

#### Scenario: Verificación iniciada por el cliente
- **DADO** un cliente autenticado
- **CUANDO** escribe "quiero verificar mi celular"
- **ENTONCES** se muestra el estado actual ("Tu celular ya está verificado") o se inicia el flujo del Requisito 2

#### Scenario: OTP opcional desde "Mi cuenta"
- **DADO** un cliente autenticado que quiere verificar su celular de forma opcional desde `AccountPage`
- **CUANDO** pulsa "Verificar celular"
- **ENTONCES** se inicia el flujo del Requisito 2 dentro de la misma pantalla (envío del código, `OtpInput`, temporizador y reenvío, con las mismas reglas de vigencia, intentos y límite de envíos)
- **Y** al verificar, la etiqueta pasa a "Celular verificado" sin salir de la pantalla
- **Y** la compra ya estaba habilitada por el correo verificado de la cuenta: este paso no es requisito para el checkout

## Requisitos no funcionales

- **Seguridad:** el código OTP nunca pasa por el LLM ni se guarda en la tabla `message`; el formulario lo envía directo al endpoint. El backend guarda solo un **HMAC-SHA256** del código con `PHONE_OTP_SECRET`; el código en claro no se persiste ni se registra en logs. El celular se muestra enmascarado (`+51 9****4321`).
- **Almacenamiento:** los desafíos viven en una tabla propia (`phone_otp_challenge`) y el registro de verificaciones exitosas sigue en `local_phone_verification` (solo inserción). Un desafío nuevo invalida el anterior para el mismo cliente y número; solo puede haber uno activo por cliente.
- **Configuración:** el guard del checkout se controla con dos banderas, en este orden de precedencia:
  1. `REQUIRE_PHONE_VERIFICATION=true`: **modo legado**, exige únicamente el celular verificado localmente (`403 CELULAR_NO_VERIFICADO`).
  2. Si la anterior es `false`, `REQUIRE_VERIFIED_CONTACT=true`: exige un contacto verificado, ya sea el correo del perfil o el celular verificado localmente (`403 CONTACTO_NO_VERIFICADO`).
  3. Si ambas son `false`: no hay guard de contacto (solo para pruebas o demos).

  Supuesto explícito: en producción `REQUIRE_VERIFIED_CONTACT=true` y `REQUIRE_PHONE_VERIFICATION=false`; el modo legado se activa solo de forma deliberada. `REQUIRE_VERIFIED_CONTACT` es un interruptor de seguridad y, en la práctica, una cuenta activa siempre lo supera porque G7 exige el correo verificado para iniciar sesión. Si el equipo adopta otros valores por defecto, se actualizan esta sección y el ADR-0026.
- **Pruebas:** el `SimulatedSmsSender` propio expone el código generado únicamente por un mecanismo de prueba (variable de entorno `MODO_QA=true` que devuelve el código en la respuesta, o un log accesible solo en el entorno de pruebas), nunca en producción ni en una respuesta normal al cliente.
- **Purga:** los desafíos vencidos o consumidos no se conservan indefinidamente; el plazo de purga queda pendiente de decisión y se registra en [ADR-0026](../../../docs/arquitectura/adr/ADR-0026-almacen-de-otp-y-guard-de-celular.md). Mientras no se decida, no se reutilizan para verificar.
- **Autocontención:** el envío y la verificación del OTP no dependen de Seguridad en absoluto. El guard del checkout sí lee el perfil (`GET /auth/me`, ya usado por SPEC-03) para obtener el correo y el celular vigentes. Si Seguridad no responde, el checkout queda bloqueado con `403 CONTACTO_NO_VERIFICADO` (`motivo: SEGURIDAD_NO_DISPONIBLE`) y no se omite el guard; el cliente puede reintentar más tarde.
- **Reemplazo futuro:** el adaptador `SmsSender` se implementa detrás de una interfaz, para poder sustituirlo por el mecanismo de Seguridad sin tocar el resto del flujo, si en el Hito 4 deciden construirlo (ver acuerdo A2 actualizado).

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.

## Decisiones

- **D1 — OTP de celular completo (auditoría §4).** Se implementa la verificación completa: OTP de 6 dígitos, TTL de 5 minutos, 3 intentos, 3 reenvíos cada 15 minutos, código hasheado, `SmsSender`/`SimulatedSmsSender`, `CheckoutGuard` contra el celular vigente y bandera `REQUIRE_PHONE_VERIFICATION`. **Aprobada:** 2026-11-21. **Estado:** Implementado (2026-11-21); código mergeado en backend #141 (`b75fbea6`) y frontend #109 (`7432d463`). **Auditoría:** [auditoría de specs 2026-11](../../../docs/auditoria-specs-2026-11.md). **ADR:** [ADR-0026](../../../docs/arquitectura/adr/ADR-0026-almacen-de-otp-y-guard-de-celular.md).

- **D2 — Contacto verificado por correo, celular opcional (cambio de política).** El correo de la cuenta se verifica al registrarse y G7 no permite iniciar sesión sin verificarlo; por eso el correo del perfil es el contacto verificado por defecto y el checkout no debe pedir ninguna verificación al cliente. El celular queda como verificación **opcional** desde "Mi cuenta", con el OTP de D1 intacto. `CONTACTO_NO_VERIFICADO` se conserva como error defensivo para perfil sin correo, G7 caído o sesión inválida. Se añade `REQUIRE_VERIFIED_CONTACT` como interruptor de seguridad y `REQUIRE_PHONE_VERIFICATION` queda como modo legado, con la precedencia del RNF de configuración. **Aprobada:** 2026-11-25. **Estado:** Vigente. **Reemplaza:** el alcance obligatorio del guard de D1 en el modo por defecto; D1 se conserva como historial y su OTP sigue implementado. **ADR:** [ADR-0026](../../../docs/arquitectura/adr/ADR-0026-almacen-de-otp-y-guard-de-celular.md).
