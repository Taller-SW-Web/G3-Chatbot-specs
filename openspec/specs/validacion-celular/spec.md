# Validación local de celular por OTP

> Origen: SPEC-04 · Grupo: Identidad · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03)

## Responsables

- **Sebastian:** OTP propio (`SmsSender` simulado) y formulario del OTP en el chat.
- **Alonso:** herramienta `verificar_celular`.
- **Nikol (QA):** casos de prueba a partir de los escenarios, pruebas E2E si el flujo es crítico y validación contra la definición de terminado.

## Purpose

Garantizar, dentro del propio chatbot, que el cliente controla el celular que va a recibir su pedido, mediante un código OTP simulado, sin depender de un endpoint de Seguridad que no existe este ciclo.

## Contexto

🧩 **Cambio de diseño (23/09/2026).** El chatbot había pedido a Seguridad un mecanismo para verificar el celular de un cliente por OTP (acuerdo A2, su RF-10.4). Seguridad respondió por escrito en su acta de integración: **decidido fuera de alcance de este ciclo**. Su justificación: el SMS es simulado hasta el final del curso y el correo del cliente ya queda verificado por el registro (SPEC-01/SPEC-02), así que no van a construir el mecanismo genérico por canal este semestre. Dejan la puerta abierta a reevaluarlo en el Hito 4 si aparece un caso concreto que el registro no cubra — pero no es algo con lo que se pueda contar para este diseño.

Esto significa que el chatbot **no puede depender de Seguridad** para esta capacidad: ni hay un endpoint para disparar el OTP, ni hay forma de escribir el atributo `celularVerificado` de Seguridad desde otro módulo (su ADR-006 confirma que las consultas y validaciones de contacto no se exponen entre módulos).

El curso exige igual la "validación del número celular ... del cliente" para este canal. La solución: el chatbot implementa su **propia** verificación, autocontenida, sin tocar el perfil de Seguridad. Es el mismo patrón que ya usa Ventas para su pasarela de pago simulada — un adaptador propio, reemplazable más adelante si Seguridad decide construir el mecanismo compartido.

## Alcance

Incluye:
- Verificación local (propia del chatbot) del celular vigente en el perfil del cliente (`GET /auth/me` → `celular`), antes del primer checkout.
- Envío de un código OTP simulado y su verificación, con las mismas reglas de vigencia, intentos y límite de reenvíos que ya usa el resto del sistema (SPEC-03, SPEC-14).
- Persistencia local de "celular verificado" ligada al cliente **y** al número exacto verificado — si el celular cambia en el perfil, la verificación local queda invalidada automáticamente.
- Almacén de desafíos OTP separado del registro de verificaciones: código de 6 dígitos **hasheado**, vigencia de 5 minutos, intentos y reenvíos limitados.
- Bloqueo del checkout mientras el celular vigente no esté verificado localmente, activable por la bandera `REQUIRE_PHONE_VERIFICATION`.
- Verificación iniciada por el cliente ("quiero verificar mi celular").

### Fuera de alcance

- Cambio del número celular: es responsabilidad de Seguridad (su SPEC-16), fuera de este canal.
- Proveedor SMS real: se simula, igual que el pago (SPEC-14).
- Verificación del correo por OTP: el correo se valida con enlace, ya cubierto por el registro (SPEC-01/SPEC-02) — Seguridad confirmó que esto satisface el requisito y no hace falta duplicarlo.
- Compartir el estado de esta verificación con otros canales (Marketplace, Retail): es una verificación local del chatbot, no del perfil del cliente en Seguridad. Si el cliente compra por otro canal, ese canal no ve esta verificación (y viceversa) — limitación conocida, aceptable mientras A2 siga fuera de alcance.

## Requirements

### Requirement: Exigir el celular verificado antes del checkout
El sistema DEBE (SHALL) impedir iniciar el checkout (SPEC-14) si el celular vigente del cliente no tiene una verificación local vigente, y DEBE ofrecer la verificación en ese momento.

*Trazabilidad: SPEC-04 · Requisito 1.*

#### Scenario: Primer checkout con celular sin verificar
- **DADO** un cliente autenticado sin un registro de verificación local para su celular actual
- **CUANDO** intenta pagar
- **ENTONCES** el backend responde `403 CELULAR_NO_VERIFICADO` y el chat muestra "Para coordinar la entrega necesitamos confirmar tu celular +51 9****4321" con el bloque `FORMULARIO/OTP_CELULAR`
- **Y** se guarda `accionPendiente = INICIAR_CHECKOUT`

#### Scenario: Celular ya verificado
- **DADO** un cliente con una verificación local vigente para el celular que tiene hoy en su perfil
- **CUANDO** intenta pagar
- **ENTONCES** el checkout continúa sin pedir verificación

#### Scenario: El cliente cambió su celular desde la última verificación
- **DADO** un cliente que verificó `+51987654321` la semana pasada y luego cambió su celular en su perfil a `+51911222333` (RF-16.7 de Seguridad, fuera de este chatbot)
- **CUANDO** intenta pagar
- **ENTONCES** la verificación local no aplica al número nuevo (se comparan por valor exacto), se exige verificar de nuevo con `+51911222333`, y esto se detecta automáticamente sin que el cliente tenga que avisar

### Requirement: Envío y verificación del código
El sistema DEBE (SHALL) generar y enviar un OTP de 6 dígitos por un adaptador SMS **propio y simulado**, y verificarlo con las mismas reglas que ya usa el resto del chatbot: 5 minutos de vigencia, 3 intentos, 3 envíos cada 15 minutos. El código DEBE (SHALL) guardarse solo como hash, nunca en claro, junto con su expiración, el contador de intentos y la ventana de reenvíos; un código consumido no se puede reutilizar y un nuevo envío invalida el desafío anterior.

*Trazabilidad: SPEC-04 · Requisito 2.*

#### Scenario: Verificación exitosa
- **DADO** un código enviado por el simulador
- **CUANDO** el cliente ingresa el código correcto
- **ENTONCES** se guarda localmente `{customer_id, phone, verified_at}`, el desafío queda consumido, el chat muestra "¡Listo! Tu celular quedó verificado" y se ejecuta la `accionPendiente`

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

#### Scenario: Bandera de exigencia desactivada
- **DADO** un entorno con `REQUIRE_PHONE_VERIFICATION=false`
- **CUANDO** el cliente inicia el checkout sin verificación local
- **ENTONCES** el checkout no se bloquea por celular; los endpoints de OTP siguen disponibles para una verificación voluntaria

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

#### Scenario: Verificación iniciada desde "Mi cuenta"
- **DADO** un cliente autenticado cuyo celular vigente no tiene una verificación local
- **CUANDO** pulsa "Verificar celular" en `AccountPage`
- **ENTONCES** se inicia el flujo del Requisito 2 dentro de la misma pantalla (envío del código, `OtpInput`, temporizador y reenvío, con las mismas reglas de vigencia, intentos y límite de envíos)
- **Y** al verificar, la etiqueta pasa a "Celular verificado" sin salir de la pantalla

## Requisitos no funcionales

- **Seguridad:** el código OTP nunca pasa por el LLM ni se guarda en la tabla `message`; el formulario lo envía directo al endpoint. El backend guarda solo un **HMAC-SHA256** del código con `PHONE_OTP_SECRET`; el código en claro no se persiste ni se registra en logs. El celular se muestra enmascarado (`+51 9****4321`).
- **Almacenamiento:** los desafíos viven en una tabla propia (`phone_otp_challenge`) y el registro de verificaciones exitosas sigue en `local_phone_verification` (solo inserción). Un desafío nuevo invalida el anterior para el mismo cliente y número; solo puede haber uno activo por cliente.
- **Configuración:** `REQUIRE_PHONE_VERIFICATION` activa o desactiva el bloqueo del checkout. Supuesto explícito: su valor por defecto es `true` en producción y puede fijarse en `false` por entorno para pruebas o demos; si el equipo adopta otro valor por defecto, se actualiza esta sección y el ADR-0026.
- **Pruebas:** el `SimulatedSmsSender` propio expone el código generado únicamente por un mecanismo de prueba (variable de entorno `MODO_QA=true` que devuelve el código en la respuesta, o un log accesible solo en el entorno de pruebas), nunca en producción ni en una respuesta normal al cliente.
- **Purga:** los desafíos vencidos o consumidos no se conservan indefinidamente; el plazo de purga queda pendiente de decisión y se registra en [ADR-0026](../../../docs/arquitectura/adr/ADR-0026-almacen-de-otp-y-guard-de-celular.md). Mientras no se decida, no se reutilizan para verificar.
- **Autocontención:** esta capacidad no depende de ningún endpoint de Seguridad más allá de leer el celular vigente (`GET /auth/me`, ya usado por SPEC-03). Si Seguridad no responde, el checkout queda bloqueado con "No pudimos confirmar tu celular ahora" (no se omite la verificación), pero el envío y la verificación del OTP en sí no dependen de Seguridad en absoluto.
- **Reemplazo futuro:** el adaptador `SmsSender` se implementa detrás de una interfaz, para poder sustituirlo por el mecanismo de Seguridad sin tocar el resto del flujo, si en el Hito 4 deciden construirlo (ver acuerdo A2 actualizado).

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.

## Decisiones

- **D1 — OTP de celular completo (auditoría §4).** Se implementa la verificación completa: OTP de 6 dígitos, TTL de 5 minutos, 3 intentos, 3 reenvíos cada 15 minutos, código hasheado, `SmsSender`/`SimulatedSmsSender`, `CheckoutGuard` contra el celular vigente y bandera `REQUIRE_PHONE_VERIFICATION`. **Aprobada:** 2026-11-21. **Estado:** Implementado (2026-11-21); código mergeado en backend #141 (`b75fbea6`) y frontend #109 (`7432d463`). **Auditoría:** [auditoría de specs 2026-11](../../../docs/auditoria-specs-2026-11.md). **ADR:** [ADR-0026](../../../docs/arquitectura/adr/ADR-0026-almacen-de-otp-y-guard-de-celular.md).
