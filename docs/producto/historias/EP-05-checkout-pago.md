# EP-05 · Checkout y pago — Historias de usuario

> Specs: [SPEC-12](../../../openspec/specs/direccion-cotizacion-envio/spec.md), [SPEC-13](../../../openspec/specs/cupones/spec.md), [SPEC-14](../../../openspec/specs/checkout-pago/spec.md) · Área `CHK` · 16 historias · 65 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.

---

## HU-CHK-01 · Ingresar mi documento de identidad al pagar

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 5 | Hito 4 | `SPEC-12 · Req. 1` | RN-CHK-01, RN-CHK-02 | Ventas ✅ (A14) |

**Como** cliente que va a pagar, **quiero** ingresar mi tipo y número de documento con validación inmediata, y que se prellene en mis próximas compras, **para** que mi pedido no sea rechazado por un dato mal escrito.

**Criterios de aceptación**
- `SPEC-12 · Req. 1 · Scenario: DNI válido` — un DNI de 8 dígitos se acepta.
- `SPEC-12 · Req. 1 · Scenario: RUC con prefijo inválido` — un RUC que no empieza por 10, 15, 17 o 20 se rechaza en el cliente.
- `SPEC-12 · Req. 1 · Scenario: CE fuera de rango` — un CE de 7 caracteres se rechaza (exige de 8 a 12).
- `SPEC-12 · Req. 1 · Scenario: Pasaporte válido` — un pasaporte alfanumérico de 6 a 12 caracteres se acepta.
- `SPEC-12 · Req. 1 · Scenario: Documento inválido o vacío` — el error aparece junto al campo y el pago no se habilita.
- `SPEC-12 · Req. 1 · Scenario: Cliente recurrente` — el campo se prellena con el último documento usado en el canal y queda editable.

**Prioridad:** Must: Ventas no crea el pedido sin el documento (A14).

---

## HU-CHK-02 · Ingresar o reutilizar mi dirección de entrega

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 3 | Hito 4 | `SPEC-12 · Req. 2` | RN-CHK-03 | Seguridad ✅ (`GET /usuarios/{id}/direcciones`) |

**Como** cliente, **quiero** que la dirección venga prellenada con mi dirección guardada o escribirla en la misma pantalla de pago, **para** completar el checkout en pocos pasos.

**Criterios de aceptación**
- `SPEC-12 · Req. 2 · Scenario: Cliente con dirección guardada` — los campos llegan prellenados y editables con la nota "Usando tu dirección guardada · Cambiar".
- `SPEC-12 · Req. 2 · Scenario: Cliente sin direcciones guardadas` — los campos aparecen vacíos, con el distrito como selector obligatorio.
- `SPEC-12 · Req. 2 · Scenario: Validación de los campos` — con destinatario vacío o dirección de menos de 5 caracteres no se cotiza ni se habilita el pago.

**Prioridad:** Must: sin dirección no hay envío ni pedido.

---

## HU-CHK-03 · Guardar mi dirección para la próxima compra

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Should | 2 | Hito 4 | `SPEC-12 · Req. 3` | RN-CHK-04 | Seguridad ✅ (`POST /usuarios/{id}/direcciones`) |

**Como** cliente, **quiero** marcar "Guardar esta dirección" al pagar, **para** no tener que escribirla otra vez en mi próxima compra.

**Criterios de aceptación**
- `SPEC-12 · Req. 3 · Scenario: Cliente marca "Guardar esta dirección"` — se guarda en Seguridad junto con la creación del pedido; si falla, el checkout continúa y se informa.
- `SPEC-12 · Req. 3 · Scenario: Cliente no marca la casilla` — la dirección se usa solo para ese pedido y no se llama a Seguridad.

**Prioridad:** Should: es una comodidad; el pedido se puede crear sin guardar la dirección.

---

## HU-CHK-04 · Conocer el costo y el plazo del envío antes de pagar

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 8 | Hito 4 | `SPEC-12 · Req. 4` | RN-CHK-05, RN-CHK-06, RN-CHK-07, RN-CHK-08 | Despacho ✅ contrato / 🟡 autenticación (A12); Productos 🟡 (A6: peso y volumen) |

**Como** cliente, **quiero** saber si llegan a mi distrito, cuánto cuesta el envío y en cuántos días llega, **para** conocer el total real antes de pagar.

**Criterios de aceptación**
- `SPEC-12 · Req. 4 · Scenario: Destino con cobertura` — se muestran costo y plazo del envío y el total los incluye.
- `SPEC-12 · Req. 4 · Scenario: Destino sin cobertura` — se informa "Aún no llegamos a {distrito}", se bloquea el pago (`422 SIN_COBERTURA`) y se pide corregir el distrito.
- `SPEC-12 · Req. 4 · Scenario: Peso de producto no disponible` — se usa el peso por defecto de la categoría y se registra su uso.
- `SPEC-12 · Req. 4 · Scenario: Despacho no disponible` — tras 4 s no se asume costo, se ofrece "Reintentar" y el pago queda deshabilitado.

**Prioridad:** Must: el total a cobrar incluye el envío.

**Notas:** RNF: cotización p95 ≤ 600 ms. Riesgo por dos acuerdos abiertos (A6, A12).

---

## HU-CHK-05 · Mantener vigente la cotización de envío

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 3 | Hito 4 | `SPEC-12 · Req. 5` | RN-CHK-09 | Despacho ✅ / 🟡 (A12) |

**Como** cliente, **quiero** que el costo de envío se recalcule si cambio mi carrito o pasa mucho tiempo, **para** que el total que confirmo sea el correcto.

**Criterios de aceptación**
- `SPEC-12 · Req. 5 · Scenario: El carrito cambia después de cotizar` — la cotización se invalida y se recalcula al reabrir `CheckoutPage`.
- `SPEC-12 · Req. 5 · Scenario: Cotización vencida` — con más de 30 minutos se recotiza antes de crear el pedido y se muestra el nuevo total si cambió.

**Prioridad:** Must: evita cobrar un envío desactualizado.

---

## HU-CHK-06 · Aplicar un cupón de descuento

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 5 | Hito 4 | `SPEC-13 · Req. 1` | RN-CHK-10, RN-CHK-11, RN-CHK-12 | Productos 🟡 (A5: `/cupones/validar`) |

**Como** cliente con un código de descuento, **quiero** aplicarlo escribiéndolo en el chat o en el carrito, **para** ver su efecto real en el total antes de pagar.

**Criterios de aceptación**
- `SPEC-13 · Req. 1 · Scenario: Cupón válido por texto` — el cupón se valida con Productos y el carrito muestra el descuento y el total actualizado.
- `SPEC-13 · Req. 1 · Scenario: Código con espacios o minúsculas` — el código se normaliza antes de validarlo.
- `SPEC-13 · Req. 1 · Scenario: Reemplazar un cupón` — aplicar un segundo cupón válido pide confirmar el reemplazo.

**Prioridad:** Must: el lineamiento de ofertas y promociones se traza a SPEC-13 (README §4).

---

## HU-CHK-07 · Entender por qué mi cupón fue rechazado

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 3 | Hito 4 | `SPEC-13 · Req. 2` | RN-CHK-13 | Productos 🟡 (A5: catálogo de motivos) |

**Como** cliente, **quiero** saber en términos claros por qué no se aplicó mi cupón, **para** corregirlo o decidir si agrego productos.

**Criterios de aceptación**
- `SPEC-13 · Req. 2 · Scenario: Monto mínimo no alcanzado` — se responde `422 CUPON_INVALIDO {motivo: MONTO_MINIMO}` con el monto faltante y "Ver productos".
- `SPEC-13 · Req. 2 · Scenario: Cupón no combinable` — se informa que ya se aplica un beneficio mayor y el cupón no queda aplicado.

**Prioridad:** Must: un rechazo sin motivo genera reclamos y abandono del pago.

**Notas:** la tabla de 8 motivos y mensajes está en SPEC-13 · Req. 2; cada motivo requiere su prueba (desglose `[QA]`).

---

## HU-CHK-08 · Aplicar cupones solo con sesión iniciada

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 2 | Hito 4 | `SPEC-13 · Req. 3` | RN-CHK-14 | — |

**Como** visitante con un cupón, **quiero** que el chat me pida iniciar sesión y luego aplique mi cupón automáticamente, **para** no tener que volver a escribirlo.

**Criterios de aceptación**
- `SPEC-13 · Req. 3 · Scenario: Visitante anónimo con cupón` — se pide iniciar sesión y se guarda `accionPendiente = APLICAR_CUPON{codigo}`.
- `SPEC-13 · Req. 3 · Scenario: Cupón aplicado y cierre de sesión` — al volver a anónimo el cupón no se conserva.

**Prioridad:** Must: Productos exige `customerRef` para cupones con límite por cliente.

---

## HU-CHK-09 · Revalidar el cupón cuando cambia el carrito

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 3 | Hito 4 | `SPEC-13 · Req. 4` | RN-CHK-15 | Productos 🟡 (A5) |

**Como** cliente, **quiero** que el sistema me avise si mi cupón deja de aplicar por un cambio en el carrito, **para** no llevarme una sorpresa en el total.

**Criterios de aceptación**
- `SPEC-13 · Req. 4 · Scenario: Quitar productos invalida el cupón` — al bajar del mínimo el cupón se retira con aviso.
- `SPEC-13 · Req. 4 · Scenario: El cupón se agota antes de pagar` — el checkout se detiene con `409 CARRITO_DESACTUALIZADO`, se retira el cupón y se muestra el nuevo total.

**Prioridad:** Must: garantiza que el total enviado a Ventas coincide con la última evaluación.

---

## HU-CHK-10 · Proteger los cupones contra fuerza bruta (Habilitadora)

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Should | 2 | Hito 4 | `SPEC-13 · Req. 5` | RN-CHK-16 | — |

**Como** negocio, **quiero** limitar los intentos fallidos de cupones, **para** evitar que alguien adivine códigos por prueba y error.

**Criterios de aceptación**
- `SPEC-13 · Req. 5 · Scenario: Demasiados intentos inválidos` — con 5 inválidos en 10 minutos el siguiente recibe `429`.
- `SPEC-13 · Req. 5 · Scenario: Contador tras un cupón válido` — un cupón válido reinicia el contador.

**Prioridad:** Should: control de abuso; no bloquea el flujo de compra.

**Notas:** habilitadora.

---

## HU-CHK-11 · Iniciar el pago con las precondiciones resueltas

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 5 | Hito 4 | `SPEC-14 · Req. 1` | RN-CHK-17 | — (orquesta HU-IDE-06, HU-IDE-12, HU-CAR-02, HU-CHK-04, HU-CHK-09) |

**Como** cliente, **quiero** que al decir "quiero pagar" el chat resuelva en orden lo que falte (sesión, celular, carrito, dirección, cupón), **para** llegar al resumen de pago sin callejones sin salida.

**Criterios de aceptación**
- `SPEC-14 · Req. 1 · Scenario: Todo listo` — se navega a `CheckoutPage` con los importes calculados por el backend y el botón "Confirmar y pagar S/ X".
- `SPEC-14 · Req. 1 · Scenario: Falta una precondición` — sesión, celular, carrito o cupón se resuelven en el chat; si falta la dirección, se navega a `CheckoutPage` con la sección de dirección enfocada.
- `SPEC-14 · Req. 1 · Scenario: Carrito vacío o solo con productos no disponibles` — se informa y se ofrece "Buscar productos".

**Prioridad:** Must: es la entrada al pago con tarjeta que exige el curso.

**Notas:** la dirección se captura en `CheckoutPage`, no en el chat (pregunta abierta 4 de [`alcance.md`](../alcance.md#preguntas-abiertas), resuelta).

---

## HU-CHK-12 · Confirmar el resumen y registrar mi pedido

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 5 | Hito 4 | `SPEC-14 · Req. 2` | RN-CHK-18, RN-CHK-19 | Ventas ✅ (A8); Productos 🟡 (A5, revalidación) |

**Como** cliente, **quiero** confirmar el resumen final y que el sistema revalide todo en ese momento, **para** pagar exactamente el total que acepté.

**Criterios de aceptación**
- `SPEC-14 · Req. 2 · Scenario: Confirmación sin cambios` — se crea el checkout `PENDIENTE_PAGO` (vence en 15 min) y el pedido `CREADO`, y se muestra el formulario de tarjeta con el total.
- `SPEC-14 · Req. 2 · Scenario: El total cambió al confirmar` — se responde `409 CARRITO_DESACTUALIZADO`, se resaltan los cambios y no se crea el pedido hasta una nueva confirmación.
- `SPEC-14 · Req. 2 · Scenario: Doble clic en confirmar` — la misma `Idempotency-Key` devuelve el mismo checkout y un único pedido.

**Prioridad:** Must: es el paso de grabación del pedido que exige el curso.

**Notas:** depende de HU-PED-01 (creación en Ventas).

---

## HU-CHK-13 · Ingresar mi tarjeta en un formulario seguro

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 5 | Hito 4 | `SPEC-14 · Req. 3` | RN-CHK-20, RN-CHK-21, RN-CHK-22 | — |

**Como** cliente, **quiero** ingresar los datos de mi tarjeta en un formulario que valida lo que escribo y no los guarda, **para** pagar con confianza.

**Criterios de aceptación**
- `SPEC-14 · Req. 3 · Scenario: Validación en el cliente` — se detecta la marca por BIN, se valida con Luhn, vencimiento y CVV, y "Pagar" se habilita solo con todo válido.
- `SPEC-14 · Req. 3 · Scenario: Datos de tarjeta fuera del formulario` — un número escrito en el chat se redacta y se indica usar el formulario.
- `SPEC-14 · Req. 3 · Scenario: Validación en el servidor` — datos inválidos que evitaron la validación del cliente reciben `400 VALIDACION`, no cuentan como intento y no se simulan.

**Prioridad:** Must: es la captura del pago con tarjeta.

**Notas:** criterio de completitud de SPEC-14: verificar la ausencia de datos de tarjeta en la BD, los logs y los prompts.

---

## HU-CHK-14 · Validar mi sesión justo antes de cobrar

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 3 | Hito 4 | `SPEC-14 · Req. 4` | RN-CHK-23 | Seguridad ✅ (A3: `POST /auth/introspeccion`; credenciales reales desde Hito 4) |

**Como** cliente, **quiero** que el sistema confirme con Seguridad que mi sesión sigue válida antes de cobrarme, **para** que nadie pueda pagar con una cuenta bloqueada o una sesión robada.

**Criterios de aceptación**
- `SPEC-14 · Req. 4 · Scenario: Sesión sigue viva` — con `activo: true` el pago continúa.
- `SPEC-14 · Req. 4 · Scenario: Sesión invalidada en Seguridad (cuenta bloqueada entre el login y el pago)` — con `activo: false` el pago no se procesa, se responde `401` y se cierra la sesión local.
- `SPEC-14 · Req. 4 · Scenario: Seguridad no disponible para introspeccionar` — sin respuesta en 3 s el pago no se procesa y se responde `503`.

**Prioridad:** Must: Seguridad lo exige para toda operación que mueve dinero.

**Notas:** requiere el token de servicio de `modulo-chatbot`. El `ServiceTokenProvider` figura en el desglose de SPEC-18 (Hito 5–6), pero se construye en esta historia porque lo necesitan la introspección y el worker de Ventas (pregunta abierta 3 de [`alcance.md`](../alcance.md#preguntas-abiertas), resuelta).

---

## HU-CHK-15 · Pagar con tarjeta simulada

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 8 | Hito 4 | `SPEC-14 · Req. 5` | RN-CHK-19, RN-CHK-24, RN-CHK-25 | — (simulador propio) |

**Como** cliente, **quiero** pagar con mi tarjeta y saber de inmediato si se aprobó o por qué se rechazó, con opción de reintentar, **para** completar mi compra.

**Criterios de aceptación**
- `SPEC-14 · Req. 5 · Scenario: Pago aprobado` — se registra el intento `APROBADO` con `SIM-<uuid>`, el checkout pasa a `PAGO_APROBADO` y se dispara la notificación a Ventas.
- `SPEC-14 · Req. 5 · Scenario: Pago rechazado con intentos restantes` — se responde `402 PAGO_RECHAZADO` con el motivo y los intentos restantes, y el formulario se limpia.
- `SPEC-14 · Req. 5 · Scenario: Tercer intento fallido` — el checkout pasa a `FALLIDO`, se pide la anulación, el carrito vuelve a `ACTIVO` y se informa.
- `SPEC-14 · Req. 5 · Scenario: Doble envío del pago` — la misma `Idempotency-Key` simula una sola vez.

**Prioridad:** Must: el curso exige el pago con tarjeta (simulado) en este canal.

**Notas:** RNF: pago simulado p95 ≤ 1 s (salvo la tarjeta de latencia). Depende de HU-PED-02 (notificación) y HU-PED-03 (anulación).

---

## HU-CHK-16 · Expirar el checkout no pagado

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-05 | Must | 3 | Hito 4 | `SPEC-14 · Req. 6` | RN-CHK-26 | Ventas ✅ (A9, anulación) |

**Como** cliente, **quiero** que un pago que dejé a medias caduque de forma ordenada y pueda volver a intentarlo, **para** no quedar con un pedido colgado ni perder mi carrito.

**Criterios de aceptación**
- `SPEC-14 · Req. 6 · Scenario: Pago después de la expiración` — a los 16 minutos se responde `410 CHECKOUT_EXPIRADO`, se pide la anulación, el carrito vuelve a `ACTIVO` y se ofrece "Volver a intentar".
- `SPEC-14 · Req. 6 · Scenario: Abandono` — el job de cada minuto marca `EXPIRADO` y encola la anulación.

**Prioridad:** Must: sin expiración quedarían pedidos `CREADO` sin pagar en Ventas.

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de cada `design.md`. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-12 | T1 `[INT]` cerrar A6 y A12 → HU-CHK-04 · T2 `[BE]` DocumentoValidator → HU-CHK-01 · T3 `[BE]` EnvioService, DespachoClient, `pesos_por_categoria.yaml` → HU-CHK-04 (relacionada: HU-CHK-05) · T4 `[BE]` endpoint `envio/cotizar` → HU-CHK-04 · T5 `[BE]` GuardarDireccionOpcional → HU-CHK-03 · T6 `[FE]` BuyerDocumentSection → HU-CHK-01 · T7 `[FE]` AddressSection → HU-CHK-02 · T8 `[FE]` ShippingQuote → HU-CHK-04 · T9 `[QA]` → HU-CHK-01 a HU-CHK-05 |
| SPEC-13 | T1 `[INT]` endpoint de validación y motivos (A5) → HU-CHK-06 · T2 `[BE]` CuponService, CuponesClient, endpoints → HU-CHK-06 (relacionadas: HU-CHK-07, HU-CHK-08) · T3 `[BE]` revalidación → HU-CHK-09 · T4 `[BE]` rate limit y herramientas → HU-CHK-10 · T5 `[FE]` CouponInput y avisos → HU-CHK-06 · T6 `[QA]` → HU-CHK-06 a HU-CHK-10 |
| SPEC-14 | T1 `[BE]` modelos `checkout` e `intento_pago` → HU-CHK-12 · T2 `[BE]` CheckoutService (guardas y revalidación) → HU-CHK-11 · T3 `[BE]` IntrospeccionClient → HU-CHK-14 · T4 `[BE]` `POST /checkout` → HU-CHK-12 · T5 `[BE]` CardValidator y PaymentSimulator → HU-CHK-15 (relacionada: HU-CHK-13) · T6 `[BE]` `POST /checkout/{id}/pago` → HU-CHK-15 · T7 `[BE]` job de expiración y exclusión de logs → HU-CHK-16 · T8 `[BE]` herramienta `iniciar_checkout` → HU-CHK-11 · T9 `[FE]` CheckoutPage y CheckoutDiffNotice → HU-CHK-12 · T10 `[FE]` PaymentForm → HU-CHK-13 · T11 `[QA]` → HU-CHK-11 a HU-CHK-16 |
| SPEC-18 (adelantada) | T2 `[BE]` ServiceTokenProvider → HU-CHK-14 (se necesita en Hito 4 para la introspección y el worker de Ventas) |
