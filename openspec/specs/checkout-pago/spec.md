# Checkout y simulación de pago con tarjeta

> Origen: SPEC-14 · Grupo: Checkout · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03), [`validacion-celular`](../validacion-celular/spec.md) (SPEC-04), [`validacion-stock`](../validacion-stock/spec.md) (SPEC-10), [`gestion-carrito`](../gestion-carrito/spec.md) (SPEC-11), [`direccion-cotizacion-envio`](../direccion-cotizacion-envio/spec.md) (SPEC-12), [`cupones`](../cupones/spec.md) (SPEC-13) · Se coordina con: [`grabacion-pedido`](../grabacion-pedido/spec.md) (SPEC-15) (grabación del pedido)

## Purpose

Llevar al cliente desde el carrito hasta un pago aprobado, mostrando un resumen fiel y cobrando exactamente el total confirmado, con un simulador de pasarela predecible para pruebas y demos.

## Contexto

El curso pide "grabación del pedido y pago con tarjeta" en el Chatbot, con **simulación** del pago. Ventas (F1) recibe el "pago confirmado" como notificación y excluye de su alcance el procesamiento del cobro, así que la simulación le corresponde al canal.

Es la operación más sensible del chatbot. Involucra dinero (simulado) y datos de tarjeta, y debe evitar cobros duplicados, totales distintos a los mostrados y la exposición de datos al LLM.

Secuencia acordada con SPEC-15:
1. Se confirma el resumen.
2. Se crea el pedido `CREADO` en Ventas.
3. Se ejecuta el pago simulado.
4. Si se aprueba, se notifica `PAGADO` a Ventas.
5. Si el pago falla de forma definitiva, se solicita la anulación.

## Alcance

Incluye:
- Verificación de precondiciones: sesión `CLIENTE`, celular verificado, carrito no vacío y válido, dirección con cobertura y cotización vigente.
- `CheckoutPage`, pantalla completa (no un bloque de chat) accedida desde `CartPage`: líneas, subtotal, descuentos, cupón, envío (SPEC-12), dirección (SPEC-12), total y el botón "Confirmar y pagar".
- 🧩 Según el wireframe, el método de pago es **únicamente tarjeta**: se descarta la opción "Efectivo / Pago contra entrega" que aparecía en el diseño, porque el curso pide explícitamente "simulación de pago con tarjeta" para este canal (ver §6).
- Sesión de checkout con vigencia de 15 minutos.
- Formulario de tarjeta seguro (fuera del LLM): número, titular, vencimiento MM/AA y CVV.
- Validación de la tarjeta (Luhn, marca por BIN, vencimiento y CVV).
- Simulador de pago con tarjetas de prueba deterministas.
- Hasta 3 intentos de pago por checkout; idempotencia por intento.

### Fuera de alcance

- Integración con una pasarela real (Niubiz, Culqi, Mercado Pago) y 3-D Secure.
- Pagos con Yape, PagoEfectivo, **contra entrega** o en cuotas. 🧩 El wireframe de `CheckoutPage` incluía "Efectivo / Pago contra entrega" como alternativa a la tarjeta; se descarta a propósito porque el lineamiento del curso pide "grabación del pedido y pago **con tarjeta**" para el Canal Chatbot. Si el equipo decide reincorporarlo más adelante, es una spec nueva, no una extensión de esta.
- Guardar tarjetas para compras futuras.
- Reembolsos: son responsabilidad de F4 de Ventas; la solicitud desde el chat se cubre en SPEC-21 y SPEC-22.
- Comprobante electrónico (boleta o factura).

## Requirements

### Requirement: Precondiciones del checkout
El sistema DEBE (SHALL) verificar las precondiciones al iniciar el checkout y resolver cada una en el chat antes de mostrar el resumen, en este orden: sesión (SPEC-03) → celular verificado (SPEC-04) → carrito válido (SPEC-10 y SPEC-11) → dirección y cotización (SPEC-12) → cupón vigente (SPEC-13).

*Trazabilidad: SPEC-14 · Requisito 1.*

#### Scenario: Todo listo
- **DADO** un cliente autenticado con el celular verificado, un carrito válido y una dirección cotizada
- **CUANDO** escribe "quiero pagar" o pulsa "Pagar"
- **ENTONCES** se navega a `CheckoutPage` con todos los importes calculados por el backend y el botón "Confirmar y pagar S/ X"

#### Scenario: Falta una precondición
- **DADO** un cliente sin dirección elegida
- **CUANDO** inicia el checkout
- **ENTONCES** el chat lo guía primero a elegir la dirección (SPEC-12) y luego continúa automáticamente al resumen

#### Scenario: Carrito vacío o solo con productos no disponibles
- **DADO** un carrito sin líneas válidas
- **CUANDO** se intenta pagar
- **ENTONCES** se responde "Tu carrito no tiene productos disponibles para comprar" con la acción "Buscar productos"

### Requirement: Confirmación del resumen y creación del checkout
El sistema DEBE (SHALL) crear la sesión de checkout y el pedido en Ventas (SPEC-15) solo cuando el cliente pulsa "Confirmar y pagar", revalidando stock, precios, promociones, cupón y envío en ese momento. Si el total cambió, se pide confirmar de nuevo.

*Trazabilidad: SPEC-14 · Requisito 2.*

#### Scenario: Confirmación sin cambios
- **DADO** un resumen con total de S/ 312.40
- **CUANDO** el cliente confirma
- **ENTONCES** `POST /checkout` (con `Idempotency-Key`) revalida todo, crea el checkout en `PENDIENTE_PAGO` con `expira_en` a 15 min y el pedido `CREADO` en Ventas, marca el carrito `EN_CHECKOUT` y muestra dentro de `CheckoutPage` el formulario de tarjeta con "Total a pagar: S/ 312.40"

#### Scenario: El total cambió al confirmar
- **DADO** que un precio o el costo de envío cambió desde que se mostró el resumen
- **CUANDO** el cliente confirma
- **ENTONCES** se responde `409 CARRITO_DESACTUALIZADO`, se muestra el nuevo resumen con los cambios resaltados y no se crea el pedido hasta una nueva confirmación

#### Scenario: Doble clic en confirmar
- **DADO** dos solicitudes `POST /checkout` con la misma `Idempotency-Key`
- **CUANDO** se procesan
- **ENTONCES** se devuelve el mismo checkout y se crea un único pedido

### Requirement: Captura segura de la tarjeta
El sistema DEBE (SHALL) capturar los datos de la tarjeta solo en el formulario `PAGO`, enviarlos directo a `POST /checkout/{id}/pago` y descartarlos tras la simulación; solo persiste la marca y los últimos 4 dígitos.

*Trazabilidad: SPEC-14 · Requisito 3.*

#### Scenario: Validación en el cliente
- **DADO** el formulario de pago
- **CUANDO** el cliente escribe el número
- **ENTONCES** se detecta la marca por BIN (Visa 4…, Mastercard 51–55/2221–2720, Amex 34/37), se formatea en grupos, se valida con Luhn, el vencimiento debe ser un mes actual o futuro y el CVV tiene 3 dígitos (4 en Amex); el botón "Pagar" se habilita solo con todos los campos válidos

#### Scenario: Datos de tarjeta fuera del formulario
- **DADO** que el cliente escribe su número de tarjeta en el chat
- **CUANDO** se envía
- **ENTONCES** se redacta antes de persistirlo y de enviarlo al LLM (SPEC-05 Req. 7) y se indica usar el formulario

#### Scenario: Validación en el servidor
- **DADO** una petición de pago con datos inválidos que evitó la validación del cliente
- **CUANDO** llega al backend
- **ENTONCES** se responde `400 VALIDACION`, no cuenta como intento y no se simula

### Requirement: Introspección antes de procesar el pago
El sistema DEBE (SHALL) introspeccionar el token del cliente contra Seguridad (`POST /auth/introspeccion`, con el token de servicio de `modulo-chatbot`) justo antes de simular el pago, y rechazar la operación si la sesión ya no es válida — aunque el JWT local todavía no haya expirado.

*Trazabilidad: SPEC-14 · Requisito 4.*

#### Scenario: Sesión sigue viva
- **DADO** un checkout `PENDIENTE_PAGO` y un cliente que va a pagar
- **CUANDO** el backend introspecciona su token y Seguridad responde `200 {activo: true}`
- **ENTONCES** continúa con la simulación del pago (Requisito 5)

#### Scenario: Sesión invalidada en Seguridad (cuenta bloqueada entre el login y el pago)
- **DADO** que Seguridad responde `200 {activo: false, motivo: USUARIO_INACTIVO}`
- **CUANDO** se intenta pagar
- **ENTONCES** el pago **no se procesa**, se responde `401 TOKEN_INVALIDO`, se cierra la sesión local (igual que un refresh inválido, SPEC-03) y se muestra "Tu sesión ya no es válida, vuelve a iniciar sesión"

#### Scenario: Seguridad no disponible para introspeccionar
- **DADO** que `POST /auth/introspeccion` no responde en 3 s
- **CUANDO** se intenta pagar
- **ENTONCES** no se procesa el pago (nunca se asume `activo: true` por defecto); se responde `503 SERVICIO_NO_DISPONIBLE` con "No pudimos confirmar tu sesión, intenta de nuevo en un momento"

### Requirement: Simulación del pago
El sistema DEBE (SHALL) procesar el pago con un simulador determinista según la tarjeta de prueba:

| Tarjeta | Resultado |
|---|---|
| `4111 1111 1111 1111`, `5555 5555 5555 4444`, `3782 822463 10005` | APROBADO |
| `4000 0000 0000 0002` | RECHAZADO · `FONDOS_INSUFICIENTES` |
| `4000 0000 0000 0069` | RECHAZADO · `DENEGADA_POR_EMISOR` |
| `4000 0000 0000 0119` | ERROR · `ERROR_PROCESAMIENTO` (se puede reintentar) |
| `4000 0000 0000 3220` | APROBADO con latencia de 5 s (para probar la espera) |
| Cualquier otra tarjeta válida por Luhn | APROBADO |

*Trazabilidad: SPEC-14 · Requisito 5.*

#### Scenario: Pago aprobado
- **DADO** un checkout `PENDIENTE_PAGO` vigente
- **CUANDO** se paga con `4111 1111 1111 1111`
- **ENTONCES** se registra un `intento_pago` `APROBADO` con `idTransaccion = SIM-<uuid>`, marca y `ultimos4`, el checkout pasa a `PAGO_APROBADO` y se dispara la notificación del pago a Ventas (SPEC-15)

#### Scenario: Pago rechazado con intentos restantes
- **DADO** el primer intento
- **CUANDO** se paga con `4000 0000 0000 0002`
- **ENTONCES** se responde `402 PAGO_RECHAZADO {motivo: FONDOS_INSUFICIENTES, intentosRestantes: 2}` y se muestra "Tu tarjeta fue rechazada por fondos insuficientes. Puedes intentar con otra tarjeta"; el formulario se limpia

#### Scenario: Tercer intento fallido
- **DADO** dos intentos rechazados
- **CUANDO** el tercero también falla
- **ENTONCES** el checkout pasa a `FALLIDO`, se solicita la anulación del pedido `CREADO` (SPEC-15), el carrito vuelve a `ACTIVO` y se informa "No pudimos procesar el pago. Tu carrito sigue guardado"

#### Scenario: Doble envío del pago
- **DADO** dos solicitudes de pago con la misma `Idempotency-Key`
- **CUANDO** se procesan
- **ENTONCES** se simula una sola vez y la segunda recibe el mismo resultado

### Requirement: Vigencia del checkout
El sistema DEBE (SHALL) expirar los checkouts no pagados en 15 minutos.

*Trazabilidad: SPEC-14 · Requisito 6.*

#### Scenario: Pago después de la expiración
- **DADO** un checkout creado hace 16 minutos
- **CUANDO** el cliente intenta pagar
- **ENTONCES** se responde `410 CHECKOUT_EXPIRADO`, se solicita la anulación del pedido `CREADO`, el carrito vuelve a `ACTIVO` y se ofrece "Volver a intentar", que genera un checkout nuevo con la revalidación completa

#### Scenario: Abandono
- **DADO** un checkout sin actividad por 15 minutos
- **CUANDO** lo detecta el job de expiración (cada minuto)
- **ENTONCES** se marca `EXPIRADO` y se encola la anulación del pedido `CREADO`

## Requisitos no funcionales

- **Seguridad (datos de tarjeta):** el PAN, el CVV y el vencimiento nunca se escriben en la BD, en logs, en trazas ni en el contexto del LLM. El body del endpoint de pago se excluye del logging del middleware. Se usa HTTPS obligatorio.
- **Seguridad (autorización):** antes del pago se verifica que el checkout pertenece al `sub` del token. 🧩 **Acuerdo A3, concedido (23/09/2026):** Seguridad otorgó el scope `tokens:introspeccion` a `modulo-chatbot`, publicado en su kit §5 — es exactamente el caso que su propia regla marca como obligatorio ("si la operación mueve dinero, introspeccionen"). El backend DEBE llamar a `POST /auth/introspeccion` con el token del cliente justo antes de procesar el pago (Requisito 4) y rechazar si `activo: false`. Las credenciales reales (`client_secret` de `modulo-chatbot`) las entrega Seguridad recién en el Hito 4; hasta entonces se prueba contra el mock con `client_secret=secreto-de-prueba`.
- **Idempotencia:** hay claves únicas en `checkout.idempotency_key` e `intento_pago.idempotency_key`.
- **Rendimiento:** el pago simulado (salvo la tarjeta de latencia) tarda p95 ≤ 1 s de extremo a extremo; el botón muestra "Procesando…" y queda deshabilitado.
- **Transparencia:** el formulario indica "Pago simulado – entorno académico. No uses tarjetas reales".
- **Accesibilidad:** los campos tienen el `autocomplete` adecuado (`cc-number`, `cc-exp`, `cc-csc`, `cc-name`) y los errores se anuncian.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen (se verifica la ausencia de datos de tarjeta en la BD, los logs y los prompts).
- No se han incorporado funcionalidades fuera del alcance.
