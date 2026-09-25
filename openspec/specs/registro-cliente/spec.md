# Registro de cliente desde el chat

> Origen: SPEC-01 · Grupo: Identidad · Requiere sesión: No · Depende de: Seguridad (SPEC-01 y SPEC-07 de Seguridad), [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05)

## Purpose

Permitir que un cliente cree su cuenta sin salir del chat, mediante un formulario seguro, y guiarlo hacia la verificación de su correo.

## Contexto

El cliente puede explorar el catálogo sin cuenta, pero para pagar, consultar pedidos o reclamar necesita una identidad. El dueño de la entidad usuario es el módulo de Seguridad y Usuarios, y el chatbot no puede almacenar usuarios ni contraseñas.

El contrato de Seguridad ya está publicado:

- `POST /auth/registro` crea la cuenta en estado `PENDIENTE_VERIFICACION` con el rol `CLIENTE`.
- Seguridad envía un enlace de verificación de un solo uso, válido por 24 horas.
- No abre sesión hasta que el correo se verifica.

## Alcance

Incluye:
- Apertura del formulario de registro cuando el cliente lo pide por texto, pulsa "Crear cuenta" o intenta una acción que requiere sesión y elige registrarse.
- Campos: `nombres`, `apellidos`, `correo`, `celular` (+51 seguido de 9 dígitos), `contrasena`, confirmación de la contraseña y `aceptaTerminos`.
- Validación en cliente con la política de contraseña obtenida de Seguridad.
- Envío del registro a Seguridad a través del BFF y manejo de todas sus respuestas.
- Conservación de la conversación y del carrito anónimo durante el registro.

### Fuera de alcance

- Registro con redes sociales: Seguridad no lo contempla.
- Registro de vendedores o administradores: no corresponde a un canal de cliente.
- Edición del perfil: pertenece a SPEC-16 de Seguridad y al Marketplace.

## Requirements

### Requirement: Apertura del formulario de registro
El sistema DEBE (SHALL) mostrar el formulario de registro como un bloque `FORMULARIO` de tipo `REGISTRO` (modal en escritorio, hoja inferior en móvil) cuando se detecta la intención de registrarse o se pulsa la acción correspondiente. Nunca solicita los datos del registro campo por campo en texto libre.

*Trazabilidad: SPEC-01 · Requisito 1.*

#### Scenario: Intención de registro expresada en lenguaje natural
- **DADO** un visitante sin sesión en una conversación activa
- **CUANDO** escribe "quiero crear una cuenta"
- **ENTONCES** el motor invoca la herramienta `solicitar_registro` y el chat responde con un mensaje breve más el bloque `FORMULARIO/REGISTRO`, sin pedir ningún dato por texto

#### Scenario: Acción protegida sin sesión
- **DADO** un visitante sin sesión con productos en el carrito
- **CUANDO** pide "quiero pagar"
- **ENTONCES** el chat informa que necesita una cuenta y ofrece las acciones rápidas "Iniciar sesión" y "Crear cuenta", y guarda en `conversacion.contexto.accionPendiente` la acción `INICIAR_CHECKOUT` para retomarla después

### Requirement: Validación en cliente
El sistema DEBE (SHALL) validar en el frontend el formato de todos los campos antes de enviarlos, usando la política obtenida de `GET /sesion/politica-contrasena` (cacheada durante la sesión del navegador), y mostrar los errores junto a cada campo.

*Trazabilidad: SPEC-01 · Requisito 2.*

#### Scenario: Formulario válido
- **DADO** un formulario con todos los campos en el formato correcto, las contraseñas coincidentes y los términos aceptados
- **CUANDO** el cliente pulsa "Crear cuenta"
- **ENTONCES** el botón se deshabilita, se muestra un indicador de carga y se envía `POST /api/v1/sesion/registro`

#### Scenario: Celular sin prefijo peruano
- **DADO** un celular ingresado como `987654321`
- **CUANDO** el campo pierde el foco
- **ENTONCES** el frontend normaliza el valor a `+51987654321` si tiene exactamente 9 dígitos y empieza con 9; con cualquier otro formato muestra "Ingresa un celular peruano de 9 dígitos" y no permite enviar

#### Scenario: Contraseña que no cumple la política
- **DADO** una contraseña que no cumple la longitud o la composición exigidas por la política
- **CUANDO** el cliente escribe
- **ENTONCES** se muestra en tiempo real la lista de reglas con su estado (cumplida o pendiente) y el envío queda bloqueado

### Requirement: Registro exitoso
El sistema DEBE (SHALL) reenviar el registro a `POST /auth/registro` de Seguridad, agregando siempre `canalOrigen: "CHATBOT"` al payload (🧩 lista cerrada definida por Seguridad — decide a qué pantalla lleva el enlace de verificación; ver SPEC-02 · Contexto, acuerdo A1). Ante `201`, informa en el chat que la cuenta fue creada y que debe verificar el correo, sin abrir sesión.

*Trazabilidad: SPEC-01 · Requisito 3.*

#### Scenario: Cuenta creada
- **DADO** un registro válido
- **CUANDO** Seguridad responde `201 {id, estado: PENDIENTE_VERIFICACION}`
- **ENTONCES** el modal se cierra y el chat muestra "Te enviamos un enlace a m****a@correo.com para activar tu cuenta. Vence en 24 horas." junto con las acciones "Reenviar correo" e "Ya verifiqué, iniciar sesión"
- **Y** el carrito anónimo y la conversación se conservan

#### Scenario: Doble envío
- **DADO** que el cliente pulsa "Crear cuenta" dos veces seguidas
- **CUANDO** se procesan las solicitudes
- **ENTONCES** solo se envía una petición a Seguridad (botón deshabilitado más un bloqueo en el BFF por correo durante 10 s)

### Requirement: Manejo de errores de Seguridad
El sistema DEBE (SHALL) mapear cada `code` de Seguridad a un mensaje claro, sin revelar si un correo ya existe.

*Trazabilidad: SPEC-01 · Requisito 4.*

#### Scenario: Correo no disponible
- **DADO** un correo que ya tiene cuenta
- **CUANDO** Seguridad responde `409 CORREO_NO_DISPONIBLE`
- **ENTONCES** el formulario muestra el texto genérico "Si el correo es válido, recibirás un mensaje con los pasos a seguir" y ofrece "Iniciar sesión", sin afirmar que la cuenta existe

#### Scenario: Errores de validación del servidor
- **DADO** una respuesta `400 VALIDACION` con `errores[{campo, mensaje}]`
- **CUANDO** el BFF la recibe
- **ENTONCES** el frontend muestra cada mensaje debajo del campo correspondiente y conserva los valores ingresados, salvo las contraseñas

#### Scenario: Política incumplida en el servidor
- **DADO** una respuesta `422 POLITICA_INCUMPLIDA`
- **CUANDO** el BFF la recibe
- **ENTONCES** se muestra el detalle de la política incumplida en el campo contraseña

#### Scenario: Seguridad no disponible
- **DADO** que Seguridad no responde en 5 s o devuelve `5xx`/`NO_DISPONIBLE`
- **CUANDO** se envía el registro
- **ENTONCES** el formulario muestra "No pudimos crear tu cuenta en este momento, intenta en unos minutos", conserva los datos (salvo las contraseñas) y el BFF responde `503 SERVICIO_NO_DISPONIBLE`

## Requisitos no funcionales

- **Seguridad:** la contraseña viaja solo por HTTPS del formulario al BFF y de ahí a Seguridad. Nunca se registra en logs, en la tabla `mensaje` ni en el contexto del LLM. El BFF aplica un rate limit de 5 registros por IP cada 10 minutos.
- **Privacidad:** el correo se muestra enmascarado en los mensajes del chat.
- **Accesibilidad:** el formulario se puede recorrer con el teclado, usa `label` asociados, anuncia los errores con `aria-live` y tiene contraste AA.
- **Rendimiento:** el BFF añade menos de 150 ms a la latencia de Seguridad (p95).

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen y tienen prueba automatizada.
- Los requisitos no funcionales aplicables se cumplen (se verifica que la contraseña no aparece en logs ni en la BD).
- No se han incorporado funcionalidades fuera del alcance.
