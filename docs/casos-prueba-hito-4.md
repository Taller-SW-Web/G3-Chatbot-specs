# Casos de prueba del Hito 4

> Tarea H4-Q1 de [`odd/tasks/hito-4.md`](../odd/tasks/hito-4.md): casos de prueba a partir de los escenarios de las specs del hito y E2E de humo con Playwright. Fecha: 2026-11-06.

Cada caso sale de un escenario (`#### Scenario`) de las specs del alcance del hito, sin reinterpretarlo: **Dado** es la precondición, **Cuando** la acción y **Entonces** el resultado esperado. Si una spec cambia, el caso cambia con ella.

Los casos se escribieron contra las specs de `main` al 2026-11-06. Hay cambios de OpenSpec sin archivar que modifican specs de este alcance: `alinear-specs-con-productos` (SPEC-07, 08 y 13, PR #22 y #23) y `alinear-specs-con-prototipo` (SPEC-04 y 12). Cuando se archiven, hay que regenerar las tablas afectadas.

## Resumen

| Spec | Archivo | Casos | Fuera del hito |
|---|---|---|---|
| SPEC-04 · Validación local de celular por OTP | [`validacion-celular`](../openspec/specs/validacion-celular/spec.md) | 9 | 0 |
| SPEC-07 · Recomendación de productos por necesidad | [`recomendacion`](../openspec/specs/recomendacion/spec.md) | 8 | 0 |
| SPEC-08 · Consulta de ofertas y promociones | [`ofertas-promociones`](../openspec/specs/ofertas-promociones/spec.md) | 9 | 0 |
| SPEC-12 · Dirección de entrega, documento del comprador y cotización de envío | [`direccion-cotizacion-envio`](../openspec/specs/direccion-cotizacion-envio/spec.md) | 17 | 0 |
| SPEC-13 · Cupones de descuento | [`cupones`](../openspec/specs/cupones/spec.md) | 11 | 0 |
| SPEC-14 · Checkout y simulación de pago con tarjeta | [`checkout-pago`](../openspec/specs/checkout-pago/spec.md) | 18 | 0 |
| SPEC-15 · Grabación del pedido | [`grabacion-pedido`](../openspec/specs/grabacion-pedido/spec.md) | 13 | 0 |
| SPEC-16 · Notificación de confirmación por correo | [`notificacion-confirmacion`](../openspec/specs/notificacion-confirmacion/spec.md) | 6 | 0 |
| **Total** | | **91** | **0** |

De los 91 casos del hito: 10 de nivel E2E, 59 de nivel API, 8 de nivel Unidad, 14 de nivel Eval. 0 ya tienen una prueba automatizada en el backend que cita el escenario.

## Cómo leer las tablas

- **Nivel:** dónde se automatiza el caso.
  - **E2E:** recorrido en el navegador con Playwright (frontend, `tests/e2e`).
  - **API:** prueba del backend por HTTP o contra PostgreSQL, con los módulos externos simulados (ADR-0017).
  - **Unidad:** lógica pura, sin red (esquemas del frontend o funciones del backend).
  - **Eval:** depende de cómo el LLM interpreta el texto; se verifica con conversaciones de evaluación en `tests/evals` del backend y no con aserciones exactas sobre el texto. La parte determinista (herramienta llamada y argumentos) se cubre con un LLM simulado.
- **Tarea:** tarea del Hito 4 que implementa el escenario y que debe dejar la prueba en verde.
- **Humo:** prueba E2E de humo que recorre el caso (ver la sección siguiente).
- **Prueba existente:** archivo del backend cuyo docstring cita el escenario (`SPEC-xx Req. n · Scenario: ...`), en `development` al 2026-11-06 (commit `04ed44c`). Ninguna prueba de `development` cita todavía un escenario de este alcance; las pruebas de H4-F1, H4-F2, H4-F3 y H4-F5 están en PR sin fusionar.
- **Fuera del hito:** el escenario pertenece a una funcionalidad de un hito posterior; se lista para no perder la trazabilidad, pero no se ejecuta en el Hito 4. En este alcance no hay ninguno: las ocho specs están dentro del Hito 4 y ningún escenario depende de SPEC-17 a SPEC-24.

## E2E de humo

Archivo: `tests/e2e/smoke.spec.ts` del frontend. Los recorridos del Hito 4 siguen el flujo principal de la demo, SPEC-12 → 13 → 14 → 15 → 16: dirección y envío, cupón, pago, pedido grabado y correo de confirmación. Este documento solo los define; no se modificó `smoke.spec.ts`. Playwright no corre en CI (activarlo es H4-C3); antes de la demo se ejecutan contra producción.

Recorridos del Hito 3:

- E2E-03, E2E-06 y E2E-07 se pueden automatizar. Según `hito-4.md` (estado del 2026-11-03), siguen en `test.fixme`; activarlos es H4-C3.
- E2E-04 (registro y verificación del correo) y E2E-05 (inicio y cierre de sesión) no se pueden automatizar contra Seguridad G7 real: el registro envía correos reales y el inicio de sesión exige el código de MFA. Se prueban a mano en producción o en local con `SECURITY_MODE=fake`.

| ID | Recorrido | Casos | Estado al 2026-11-06 |
|---|---|---|---|
| E2E-08 | Desde el carrito, pulsar "Pagar", completar la dirección en `CheckoutPage` y ver el costo y el plazo de envío | CP-H4-14-01, CP-H4-12-07, CP-H4-12-08, CP-H4-12-12 | Por escribir: no existe en `smoke.spec.ts`. Depende de H4-F1, H4-F3, sin registro de cierre en el Progreso de `hito-4.md` al 2026-11-06 |
| E2E-09 | Aplicar un cupón válido al carrito y ver el descuento en el total | CP-H4-13-01 | Por escribir: no existe en `smoke.spec.ts`. Depende de H4-F2, sin registro de cierre en el Progreso de `hito-4.md` al 2026-11-06 |
| E2E-10 | Validar la tarjeta en el formulario, confirmar el checkout y pagar con la tarjeta de prueba aprobada | CP-H4-12-05, CP-H4-14-07, CP-H4-14-13 | Por escribir: no existe en `smoke.spec.ts`. Depende de H4-F3, sin registro de cierre en el Progreso de `hito-4.md` al 2026-11-06 |
| E2E-11 | Ver el pedido grabado y el bloque `CONFIRMACION_PEDIDO` con el correo enmascarado | CP-H4-15-06, CP-H4-16-05 | Por escribir: no existe en `smoke.spec.ts`. Depende de H4-F4, H4-F5, sin registro de cierre en el Progreso de `hito-4.md` al 2026-11-06 |
| E2E-12 | Pedir el reenvío del correo de confirmación y ver los reenvíos restantes | CP-H4-16-06 | Por escribir: no existe en `smoke.spec.ts`. Depende de H4-F5, sin registro de cierre en el Progreso de `hito-4.md` al 2026-11-06 |

Cómo ejecutarlas:

```bash
# Con el backend en local
API_PROXY_TARGET=http://localhost:8000 pnpm test:e2e tests/e2e/smoke.spec.ts

# Contra producción, ya desplegada en Vercel (H4-P1)
E2E_BASE_URL=https://g3-chatbot-frontend.vercel.app pnpm test:e2e tests/e2e/smoke.spec.ts
```

E2E-08 a E2E-11 requieren una sesión de cliente con el celular verificado. Contra producción eso implica el MFA de G7, así que esa parte del recorrido se prepara a mano o con `SECURITY_MODE=fake` en local.

## Casos por spec

### SPEC-04 · Validación local de celular por OTP

Fuente: [`openspec/specs/validacion-celular/spec.md`](../openspec/specs/validacion-celular/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-04-01 | Req. 1 · Primer checkout con celular sin verificar | un cliente autenticado sin un registro de verificación local para su celular actual | intenta pagar | el backend responde `403 CELULAR_NO_VERIFICADO` y el chat muestra "Para coordinar la entrega necesitamos confirmar tu celular +51 9****4321" con el bloque `FORMULARIO/OTP_CELULAR` y se guarda `accionPendiente = INICIAR_CHECKOUT` | API | H4-F7 | — | — |
| CP-H4-04-02 | Req. 1 · Celular ya verificado | un cliente con una verificación local vigente para el celular que tiene hoy en su perfil | intenta pagar | el checkout continúa sin pedir verificación | API | H4-F7 | — | — |
| CP-H4-04-03 | Req. 1 · El cliente cambió su celular desde la última verificación | un cliente que verificó `+51987654321` la semana pasada y luego cambió su celular en su perfil a `+51911222333` (RF-16.7 de Seguridad, fuera de este chatbot) | intenta pagar | la verificación local no aplica al número nuevo (se comparan por valor exacto), se exige verificar de nuevo con `+51911222333`, y esto se detecta automáticamente sin que el cliente tenga que avisar | API | H4-F7 | — | — |
| CP-H4-04-04 | Req. 2 · Verificación exitosa | un código enviado por el simulador | el cliente ingresa el código correcto | se guarda localmente `{customer_id, phone, verified_at}`, el chat muestra "¡Listo! Tu celular quedó verificado" y se ejecuta la `accionPendiente` | API | H4-F7 | — | — |
| CP-H4-04-05 | Req. 2 · Código incorrecto | un código erróneo | se verifica | se muestra "Código incorrecto. Te quedan N intentos"; al agotar los 3, se exige solicitar un código nuevo | API | H4-F7 | — | — |
| CP-H4-04-06 | Req. 2 · Código vencido | un código con más de 5 minutos | se ingresa | se muestra "El código venció" y se habilita "Enviar otro código" | API | H4-F7 | — | — |
| CP-H4-04-07 | Req. 2 · Límite de envíos | 3 envíos en 15 minutos | se pide otro | se muestra "Espera unos minutos antes de pedir otro código" con un temporizador | API | H4-F7 | — | — |
| CP-H4-04-08 | Req. 3 · El cliente indica que el número no es el suyo | el paso de verificación | el cliente pulsa "Ese no es mi número" o lo escribe | el chat explica que el cambio de celular se hace desde su perfil de cuenta, muestra el enlace al perfil (fuera del chatbot) y conserva el carrito | Eval | H4-F7 | — | — |
| CP-H4-04-09 | Req. 3 · Verificación iniciada por el cliente | un cliente autenticado | escribe "quiero verificar mi celular" | se muestra el estado actual ("Tu celular ya está verificado") o se inicia el flujo del Requisito 2 | Eval | H4-F7 | — | — |

### SPEC-07 · Recomendación de productos por necesidad

Fuente: [`openspec/specs/recomendacion/spec.md`](../openspec/specs/recomendacion/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-07-01 | Req. 1 · Necesidad con información suficiente | el mensaje "quiero empezar a correr, tengo unos 250 soles" | se procesa | el LLM invoca `recomendar_productos {actividad: "running", nivel: "principiante", presupuestoMax: 250}`, el backend busca en zapatillas de running (y como opción en medias y polos técnicos dentro del presupuesto) y muestra hasta 5 tarjetas con razones como "Amortiguación para principiante · S/ 229" | Eval | H4-F6 | — | — |
| CP-H4-07-02 | Req. 1 · Necesidad incompleta | el mensaje "algo para mi hijo que juega fútbol" | falta la talla o la edad y la superficie de juego | el asistente pregunta una sola cosa a la vez ("¿Juega en césped natural, sintético o losa?") y ofrece chips con las opciones, con un máximo de 2 preguntas antes de recomendar | Eval | H4-F6 | — | — |
| CP-H4-07-03 | Req. 1 · El cliente no quiere responder preguntas | una pregunta aclaratoria pendiente | el cliente responde "no sé, muéstrame algo" | se recomienda con la información disponible, priorizando productos versátiles, y se indica que puede afinar después | Eval | H4-F6 | — | — |
| CP-H4-07-04 | Req. 2 · Producto recomendado sin stock | que un candidato tiene `available = 0` en todas sus variantes | se arma la recomendación | se excluye y se reemplaza por el siguiente candidato | API | H4-F6 | — | — |
| CP-H4-07-05 | Req. 2 · No hay productos que cumplan | un presupuesto de S/ 30 para zapatillas | no existe ninguna opción | se informa con honestidad ("No tengo zapatillas en ese presupuesto; las más económicas cuestan S/ 149") y se ofrece ver esas opciones o accesorios dentro del presupuesto | Eval | H4-F6 | — | — |
| CP-H4-07-06 | Req. 3 · Complemento tras agregar al carrito | que el cliente agregó unas zapatillas de running | Productos devuelve candidatos (por ejemplo, medias técnicas o una botella) | el mensaje de confirmación incluye "¿Te interesa complementarlo?" con un mini carrusel de hasta 3 candidatos con stock | API | H4-F6 | — | — |
| CP-H4-07-07 | Req. 3 · Sin candidatos o servicio caído | que la API de candidatos no devuelve nada o falla | se agrega el producto | la confirmación se muestra sin la sección de complementos y sin error visible | API | H4-F6 | — | — |
| CP-H4-07-08 | Req. 3 · El cliente rechaza los complementos | que el cliente responde "no, gracias" | se registra la respuesta | no se vuelven a sugerir complementos en lo que queda de la conversación, salvo que los pida (`contexto.crossSellSilenciado = true`) | Eval | H4-F6 | — | — |

### SPEC-08 · Consulta de ofertas y promociones

Fuente: [`openspec/specs/ofertas-promociones/spec.md`](../openspec/specs/ofertas-promociones/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-08-01 | Req. 1 · Consulta general de ofertas | 3 promociones automáticas vigentes para `CHATBOT` y 1 solo para `RETAIL` | el cliente pregunta "¿qué ofertas tienen?" | se muestra el bloque `LISTA_PROMOCIONES` con las 3 del canal (nombre, beneficio como "20 % en toda la línea running", vigencia y el botón "Ver productos"), y no aparece la de `RETAIL` | Eval | H4-F6 | — | — |
| CP-H4-08-02 | Req. 1 · Promociones filtradas | el mensaje "¿hay descuentos en zapatillas Puma?" | se consulta | se muestran las promociones cuyo alcance incluye productos Puma de la categoría zapatillas, y además un carrusel de productos Puma con `precioOferta` | Eval | H4-F6 | — | — |
| CP-H4-08-03 | Req. 1 · Sin promociones vigentes | que no hay promociones vigentes para el canal | el cliente pregunta | se responde "Por ahora no tenemos promociones activas" y se ofrece ver los productos más vendidos o nuevos | Eval | H4-F6 | — | — |
| CP-H4-08-04 | Req. 2 · Producto con oferta de precio | un SKU con `precioRegular = 299.90` y `precioOferta = 239.90` | se renderiza la tarjeta | se ve ~~S/ 299.90~~ **S/ 239.90** y la etiqueta "-20 %" | Unidad | H4-F6 | — | — |
| CP-H4-08-05 | Req. 2 · Oferta vencida entre consultas | una oferta que vence mientras el cliente conversa | el producto se vuelve a consultar o se recalcula el carrito | se muestra el precio regular y, si estaba en el carrito, se informa "La oferta de X terminó; el precio ahora es S/ 299.90" | API | H4-F6 | — | — |
| CP-H4-08-06 | Req. 3 · Promoción automática aplicada | un carrito elegible para "2x1 en medias" | se recalcula el carrito | el bloque `CARRITO` muestra la línea "Promoción 2x1 en medias: -S/ 24.90" con los datos de la evaluación | API | H4-F6 | — | — |
| CP-H4-08-07 | Req. 3 · El cliente pregunta por qué no se aplicó una promoción | un carrito que no alcanza la condición de una promoción | el cliente pregunta "¿por qué no me hicieron el descuento?" | el asistente responde con el `motivo` que devuelve la evaluación de Productos (por ejemplo, "La promoción aplica a partir de S/ 200") y no inventa condiciones | Eval | H4-F6 | — | — |
| CP-H4-08-08 | Req. 4 · El cliente pide cupones | que existen promociones de modalidad `CUPON` | el cliente pregunta "¿me das un cupón?" | se responde que los cupones se distribuyen por campañas y que, si tiene uno, puede escribirlo para aplicarlo | Eval | H4-F6 | — | — |
| CP-H4-08-09 | Req. 4 · Promoción con cupón en el listado de Productos | que la consulta de promociones devuelve una de modalidad `CUPON` | se arma `LISTA_PROMOCIONES` | se excluye del listado | API | H4-F6 | — | — |

### SPEC-12 · Dirección de entrega, documento del comprador y cotización de envío

Fuente: [`openspec/specs/direccion-cotizacion-envio/spec.md`](../openspec/specs/direccion-cotizacion-envio/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-12-01 | Req. 1 · DNI válido | un cliente que completa `tipoDocumento: DNI` y `numeroDocumento: 72458912` | valida el formulario | se acepta, porque cumple `^[0-9]{8}$` | Unidad | H4-F1 | — | — |
| CP-H4-12-02 | Req. 1 · RUC con prefijo inválido | `tipoDocumento: RUC` y `numeroDocumento: 30458912345` | valida el formulario | se rechaza en el cliente antes de enviarlo, porque el RUC no empieza por `10`, `15`, `17` o `20`, aunque tenga 11 dígitos | Unidad | H4-F1 | — | — |
| CP-H4-12-03 | Req. 1 · CE fuera de rango | `tipoDocumento: CE` y `numeroDocumento: 1234567` (7 caracteres) | valida el formulario | se rechaza, porque el CE exige de 8 a 12 caracteres, no de 6 a 12 como se pensaba antes | Unidad | H4-F1 | — | — |
| CP-H4-12-04 | Req. 1 · Pasaporte válido | `tipoDocumento: PASAPORTE` y `numeroDocumento: A1234567` | valida el formulario | se acepta, porque cumple `^[a-zA-Z0-9]{6,12}$` | Unidad | H4-F1 | — | — |
| CP-H4-12-05 | Req. 1 · Documento inválido o vacío | un `numeroDocumento` vacío o con un formato que no corresponde al `tipoDocumento` elegido | el cliente intenta pagar | se muestra el error junto al campo y no se habilita el pago (el frontend nunca deja llegar esto a Ventas, pero si ocurriera, Ventas también lo rechaza con `400 DATO_INVALIDO`) | E2E | H4-F1 | E2E-10 | — |
| CP-H4-12-06 | Req. 1 · Cliente recurrente | un cliente que ya completó su documento en una compra anterior en este canal | vuelve a comprar | el campo se prellena con el último documento usado (guardado en `checkout.summary` de su pedido anterior, nunca en el perfil de Seguridad, que no lo modela) y queda editable | API | H4-F1 | — | — |
| CP-H4-12-07 | Req. 2 · Cliente con dirección guardada | un cliente con la dirección predeterminada "Av. Larco 1234, dpto. 502, Miraflores" | abre `CheckoutPage` | los campos `destinatario`, `direccion` (con su `distrito`) y `referencia` vienen prellenados y editables, con la nota "Usando tu dirección guardada · Cambiar" | E2E | H4-F1 | E2E-08 | — |
| CP-H4-12-08 | Req. 2 · Cliente sin direcciones guardadas | un cliente sin direcciones en Seguridad | abre `CheckoutPage` | los campos aparecen vacíos, con `distrito` como un selector obligatorio (ubigeo, que también resuelve `departamento` y `provincia`) | E2E | H4-F1 | E2E-08 | — |
| CP-H4-12-09 | Req. 2 · Validación de los campos | un `destinatario` vacío o una `direccion` de menos de 5 caracteres | el cliente intenta cotizar o pagar | se muestran los errores por campo y no se cotiza ni se habilita el pago | E2E | H4-F1 | — | — |
| CP-H4-12-10 | Req. 3 · Cliente marca "Guardar esta dirección" | el checkbox marcado y los campos válidos | el cliente confirma el pedido (SPEC-14) | el backend llama a `POST /usuarios/{id}/direcciones` con el token del cliente antes o junto con la creación del pedido; si Seguridad falla al guardarla, el checkout **continúa igual** y se informa "No pudimos guardar tu dirección para la próxima vez" | API | H4-F1 | — | — |
| CP-H4-12-11 | Req. 3 · Cliente no marca la casilla | el checkbox sin marcar | se confirma el pedido | la dirección se usa solo para ese pedido y no se llama a Seguridad para guardarla | API | H4-F1 | — | — |
| CP-H4-12-12 | Req. 4 · Destino con cobertura | una dirección en Miraflores y un carrito de 1,2 kg | Despacho responde `coberturaDisponible: true, costoEnvio: 12.50, plazoEstimadoDias: 1` | `CheckoutPage` muestra "Envío a Miraflores: S/ 12.50 · llega en 1 día hábil aprox." y el total a pagar lo incluye | E2E | H4-F1 | E2E-08 | — |
| CP-H4-12-13 | Req. 4 · Destino sin cobertura | un distrito fuera de cobertura | Despacho responde `coberturaDisponible: false` | se informa "Aún no llegamos a {distrito}" bajo el campo de dirección, se bloquea el botón de pago (`422 SIN_COBERTURA`) y se pide corregir el distrito | API | H4-F1 | — | — |
| CP-H4-12-14 | Req. 4 · Peso de producto no disponible | que Productos no informa el peso de un SKU | se calcula el peso total | se usa el peso por defecto de su categoría (`config/pesos_por_categoria.yaml`) como parche mientras se resuelve el acuerdo A6, y se registra el uso del valor por defecto | API | H4-F1 | — | — |
| CP-H4-12-15 | Req. 4 · Despacho no disponible | que el cotizador no responde en 4 s | se cotiza | no se asume ningún costo; se muestra "No pude calcular el envío ahora" con el botón "Reintentar" y el pago queda deshabilitado | API | H4-F1 | — | — |
| CP-H4-12-16 | Req. 5 · El carrito cambia después de cotizar | una cotización vigente en `CheckoutPage` | el cliente vuelve al carrito y agrega otro producto | la cotización se invalida y se recalcula automáticamente al reabrir `CheckoutPage` | API | H4-F1 | — | — |
| CP-H4-12-17 | Req. 5 · Cotización vencida | una cotización con más de 30 minutos | el cliente confirma el pago | se recotiza antes de crear el pedido y, si el costo cambió, se muestra el nuevo total antes de continuar | API | H4-F1 | — | — |

### SPEC-13 · Cupones de descuento

Fuente: [`openspec/specs/cupones/spec.md`](../openspec/specs/cupones/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-13-01 | Req. 1 · Cupón válido por texto | un cliente autenticado con un carrito de S/ 300 elegible | escribe "aplica el cupón RUN10" | se invoca `aplicar_cupon {codigo: "RUN10"}`, Productos responde `valido: true, descuento: 30.00` y el carrito muestra "Cupón RUN10: -S/ 30.00" con el total actualizado | Eval | H4-F2 | E2E-09 | — |
| CP-H4-13-02 | Req. 1 · Código con espacios o minúsculas | el código " run10 " | se aplica | se normaliza (trim y mayúsculas) antes de validar | Unidad | H4-F2 | — | — |
| CP-H4-13-03 | Req. 1 · Reemplazar un cupón | un carrito con el cupón A | el cliente aplica el cupón B y este es válido | se pregunta "¿Reemplazo el cupón A por B?" y, al confirmar, queda solo B | API | H4-F2 | — | — |
| CP-H4-13-04 | Req. 2 · Monto mínimo no alcanzado | un cupón con un mínimo de S/ 200 y un carrito de S/ 150 | se aplica | se responde `422 CUPON_INVALIDO {motivo: MONTO_MINIMO}` y se muestra "Te faltan S/ 50.00", con el botón "Ver productos" | API | H4-F2 | — | — |
| CP-H4-13-05 | Req. 2 · Cupón no combinable | que Productos determina que la mejor alternativa para la cesta no incluye el cupón | se valida | se informa que ya se aplica un beneficio mayor y el cupón no queda aplicado | API | H4-F2 | — | — |
| CP-H4-13-06 | Req. 3 · Visitante anónimo con cupón | un visitante sin sesión | intenta aplicar un cupón | se pide iniciar sesión y se guarda `accionPendiente = APLICAR_CUPON{codigo}` para aplicarlo automáticamente después | API | H4-F2 | — | — |
| CP-H4-13-07 | Req. 3 · Cupón aplicado y cierre de sesión | un cliente con cupón que cierra sesión | el carrito vuelve a ser anónimo | el cupón no se conserva en el carrito anónimo | API | H4-F2 | — | — |
| CP-H4-13-08 | Req. 4 · Quitar productos invalida el cupón | un cupón con mínimo de S/ 200 aplicado a un carrito de S/ 250 | el cliente quita productos y el carrito baja a S/ 180 | el cupón se retira y se informa "Quitamos el cupón RUN10 porque tu compra ya no alcanza el mínimo" | API | H4-F2 | — | — |
| CP-H4-13-09 | Req. 4 · El cupón se agota antes de pagar | un cupón válido al aplicarlo | al iniciar el checkout Productos responde `AGOTADO` | el checkout se detiene con `409 CARRITO_DESACTUALIZADO`, el cupón se retira y se muestra el nuevo total antes de continuar | API | H4-F2 | — | — |
| CP-H4-13-10 | Req. 5 · Demasiados intentos inválidos | un cliente con 5 cupones inválidos en 10 minutos | intenta otro | se responde `429` y el mensaje "Demasiados intentos, espera unos minutos" | API | H4-F2 | — | — |
| CP-H4-13-11 | Req. 5 · Contador tras un cupón válido | un cliente con 3 intentos inválidos | aplica un cupón válido | el contador de intentos fallidos se reinicia | API | H4-F2 | — | — |

### SPEC-14 · Checkout y simulación de pago con tarjeta

Fuente: [`openspec/specs/checkout-pago/spec.md`](../openspec/specs/checkout-pago/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-14-01 | Req. 1 · Todo listo | un cliente autenticado con el celular verificado, un carrito válido y una dirección cotizada | escribe "quiero pagar" o pulsa "Pagar" | se navega a `CheckoutPage` con todos los importes calculados por el backend y el botón "Confirmar y pagar S/ X" | E2E | H4-F3 | E2E-08 | — |
| CP-H4-14-02 | Req. 1 · Falta una precondición | un cliente sin dirección elegida | inicia el checkout | se navega a `CheckoutPage` con la sección de dirección enfocada (campos libres de SPEC-12) y, al cotizarse el envío, se muestra el resumen con los importes actualizados sin volver al chat | E2E | H4-F3 | — | — |
| CP-H4-14-03 | Req. 1 · Carrito vacío o solo con productos no disponibles | un carrito sin líneas válidas | se intenta pagar | se responde "Tu carrito no tiene productos disponibles para comprar" con la acción "Buscar productos" | API | H4-F3 | — | — |
| CP-H4-14-04 | Req. 2 · Confirmación sin cambios | un resumen con total de S/ 312.40 | el cliente confirma | `POST /checkout` (con `Idempotency-Key`) revalida todo, crea el checkout en `PENDING_PAYMENT` con `expires_at` a 15 min y el pedido `CREADO` en Ventas, marca el carrito `IN_CHECKOUT` y muestra dentro de `CheckoutPage` el formulario de tarjeta con "Total a pagar: S/ 312.40" | API | H4-F3 | — | — |
| CP-H4-14-05 | Req. 2 · El total cambió al confirmar | que un precio o el costo de envío cambió desde que se mostró el resumen | el cliente confirma | se responde `409 CARRITO_DESACTUALIZADO`, se muestra el nuevo resumen con los cambios resaltados y no se crea el pedido hasta una nueva confirmación | API | H4-F3 | — | — |
| CP-H4-14-06 | Req. 2 · Doble clic en confirmar | dos solicitudes `POST /checkout` con la misma `Idempotency-Key` | se procesan | se devuelve el mismo checkout y se crea un único pedido | API | H4-F3 | — | — |
| CP-H4-14-07 | Req. 3 · Validación en el cliente | el formulario de pago | el cliente escribe el número | se detecta la marca por BIN (Visa 4…, Mastercard 51–55/2221–2720, Amex 34/37), se formatea en grupos, se valida con Luhn, el vencimiento debe ser un mes actual o futuro y el CVV tiene 3 dígitos (4 en Amex); el botón "Pagar" se habilita solo con todos los campos válidos | Unidad | H4-F3 | E2E-10 | — |
| CP-H4-14-08 | Req. 3 · Datos de tarjeta fuera del formulario | que el cliente escribe su número de tarjeta en el chat | se envía | se redacta antes de persistirlo y de enviarlo al LLM (SPEC-05 Req. 9) y se indica usar el formulario | API | H4-F3 | — | — |
| CP-H4-14-09 | Req. 3 · Validación en el servidor | una petición de pago con datos inválidos que evitó la validación del cliente | llega al backend | se responde `400 VALIDACION`, no cuenta como intento y no se simula | API | H4-F3 | — | — |
| CP-H4-14-10 | Req. 4 · Sesión sigue viva | un checkout `PENDING_PAYMENT` y un cliente que va a pagar | el backend introspecciona su token y Seguridad responde `200 {activo: true}` | continúa con la simulación del pago (Requisito 5) | API | H4-F3 | — | — |
| CP-H4-14-11 | Req. 4 · Sesión invalidada en Seguridad (cuenta bloqueada entre el login y el pago) | que Seguridad responde `200 {activo: false, motivo: USUARIO_INACTIVO}` | se intenta pagar | el pago **no se procesa**, se responde `401 TOKEN_INVALIDO`, se cierra la sesión local (igual que un refresh inválido, SPEC-03) y se muestra "Tu sesión ya no es válida, vuelve a iniciar sesión" | API | H4-F3 | — | — |
| CP-H4-14-12 | Req. 4 · Seguridad no disponible para introspeccionar | que `POST /auth/introspeccion` no responde en 3 s | se intenta pagar | no se procesa el pago (nunca se asume `activo: true` por defecto); se responde `503 SERVICIO_NO_DISPONIBLE` con "No pudimos confirmar tu sesión, intenta de nuevo en un momento" | API | H4-F3 | — | — |
| CP-H4-14-13 | Req. 5 · Pago aprobado | un checkout `PENDING_PAYMENT` vigente | se paga con `4111 1111 1111 1111` | se registra un `payment_attempt` `APPROVED` con `idTransaccion = SIM-<uuid>`, marca y `last4`, el checkout pasa a `PAYMENT_APPROVED` y se dispara la notificación del pago a Ventas (SPEC-15) | E2E | H4-F3 | E2E-10 | — |
| CP-H4-14-14 | Req. 5 · Pago rechazado con intentos restantes | el primer intento | se paga con `4000 0000 0000 0002` | se responde `402 PAGO_RECHAZADO {motivo: FONDOS_INSUFICIENTES, intentosRestantes: 2}` y se muestra "Tu tarjeta fue rechazada por fondos insuficientes. Puedes intentar con otra tarjeta"; el formulario se limpia | API | H4-F3 | — | — |
| CP-H4-14-15 | Req. 5 · Tercer intento fallido | dos intentos rechazados | el tercero también falla | el checkout pasa a `FAILED`, se solicita la anulación del pedido `CREADO` (SPEC-15), el carrito vuelve a `ACTIVE` y se informa "No pudimos procesar el pago. Tu carrito sigue guardado" | API | H4-F3 | — | — |
| CP-H4-14-16 | Req. 5 · Doble envío del pago | dos solicitudes de pago con la misma `Idempotency-Key` | se procesan | se simula una sola vez y la segunda recibe el mismo resultado | API | H4-F3 | — | — |
| CP-H4-14-17 | Req. 6 · Pago después de la expiración | un checkout creado hace 16 minutos | el cliente intenta pagar | se responde `410 CHECKOUT_EXPIRADO`, se solicita la anulación del pedido `CREADO`, el carrito vuelve a `ACTIVE` y se ofrece "Volver a intentar", que genera un checkout nuevo con la revalidación completa | API | H4-F3 | — | — |
| CP-H4-14-18 | Req. 6 · Abandono | un checkout sin actividad por 15 minutos | lo detecta el job de expiración (cada minuto) | se marca `EXPIRED` y se encola la anulación del pedido `CREADO` | API | H4-F3 | — | — |

### SPEC-15 · Grabación del pedido

Fuente: [`openspec/specs/grabacion-pedido/spec.md`](../openspec/specs/grabacion-pedido/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-15-01 | Req. 1 · Pedido creado | un checkout confirmado y revalidado (SPEC-14) | Ventas responde `201 {pedidoId, estado: CREADO, total, moneda, canal, fechaCreacion}` | se guarda `order_ref` (`CREATED`) ligada al checkout y se habilita el formulario de pago | API | H4-F4 | — | — |
| CP-H4-15-02 | Req. 1 · Ventas rechaza por stock | un SKU que se agotó entre la revalidación y la creación | Ventas responde `409 Conflict` | no se crea el checkout de pago, el carrito vuelve a `ACTIVE`, se ejecuta la revalidación de SPEC-10 y se muestra al cliente qué cambió | API | H4-F4 | — | — |
| CP-H4-15-03 | Req. 1 · Datos incompletos | un snapshot al que le falta el documento o la dirección (por un error de validación en el frontend que no se detectó antes) | Ventas responde `400 Bad Request` | se registra como error interno (no debería ocurrir si SPEC-12 y SPEC-14 validaron bien) y se muestra "No pudimos registrar tu pedido, revisa tus datos e intenta de nuevo" | API | H4-F4 | — | — |
| CP-H4-15-04 | Req. 1 · Ventas no disponible al crear | que Ventas no responde en 5 s | se confirma el checkout | se responde `503 SERVICIO_NO_DISPONIBLE`, no se pide la tarjeta y se muestra "No pudimos registrar tu pedido. No se realizó ningún cobro. Intenta en unos minutos" | API | H4-F4 | — | — |
| CP-H4-15-05 | Req. 1 · Reintento con la misma clave | un timeout en el que Ventas sí creó el pedido | el cliente reintenta | se reenvía la misma `Idempotency-Key` y se obtiene el mismo `pedidoId`, sin duplicar el pedido | API | H4-F4 | — | — |
| CP-H4-15-06 | Req. 2 · Notificación exitosa | un pago aprobado | se registra en el outbox (`NOTIFY_SALES_PAYMENT`) en la misma transacción que el intento de pago y el worker lo envía y recibe `200 {pedidoId, nuevoEstado: PAGADO, transaccionId, fechaTransicion}` | `order_ref` pasa a `PAID_NOTIFIED`, el checkout a `CONFIRMED` y el carrito a `CONVERTED`, se encola el correo (SPEC-16) y el chat muestra `CONFIRMACION_PEDIDO` con el número de pedido, el total, la tarjeta `•••• 1111`, la dirección y "Te enviaremos la confirmación a m****a@…" (SPEC-16: sin prometer que ya llegó) | E2E | H4-F4 | E2E-11 | — |
| CP-H4-15-07 | Req. 2 · Ventas cae después del cobro | un pago aprobado y Ventas sin responder | falla la notificación | el worker reintenta con backoff exponencial (5 intentos: 5 s, 15 s, 45 s, 2 min y 5 min); el chat muestra "Pago aprobado. Estamos confirmando tu pedido PED-…"; si se agotan los intentos, el registro queda `FAILED` para revisión manual | API | H4-F4 | — | — |
| CP-H4-15-08 | Req. 2 · Montos inconsistentes | que el monto notificado no coincide con el total del pedido | Ventas valida | responde `400 Bad Request`; el worker no reintenta automáticamente (es un error de programación, no transitorio) y se alerta para revisión | API | H4-F4 | — | — |
| CP-H4-15-09 | Req. 2 · Pedido en un estado que no admite la notificación | un pedido que ya no está `CREADO` (por ejemplo, se anuló por expiración justo antes de que llegara la notificación tardía) | se notifica el pago | Ventas responde `409 Conflict`; el worker registra la inconsistencia para revisión manual y **no reintenta** (reintentar no resolvería el conflicto) | API | H4-F4 | — | — |
| CP-H4-15-10 | Req. 3 · Anulación directa | un checkout `FAILED` o `EXPIRED` con un pedido `CREADO` | se procesa el outbox `REQUEST_CANCELLATION` | Ventas responde `200 {pedidoId, estadoPedido: ANULADO, autorizacionRequerida: false, solicitudReembolsoGenerada: false}` (no `202`, porque `PAGO_NO_COMPLETADO` sobre `CREADO`/`PAGADO` no requiere autorización del Gestor) y `order_ref` pasa a `CANCELLED` (el adapter traduce el `ANULADO` de Ventas al valor local) | API | H4-F4 | — | — |
| CP-H4-15-11 | Req. 3 · Pedido ya avanzó de estado | que Ventas responde `409 Conflict` porque el pedido ya está `DESPACHADO` o `ENTREGADO` | se procesa | se registra la alerta para revisión manual y no se reintenta (en ese punto correspondería una devolución, SPEC-21, no una anulación) | API | H4-F4 | — | — |
| CP-H4-15-12 | Req. 4 · Verificación del total | un snapshot armado | se valida antes del envío | si la suma no cuadra a 0,01 se aborta con un error interno y no se crea el pedido | API | H4-F4 | — | — |
| CP-H4-15-13 | Req. 4 · Líneas no disponibles | una línea marcada como "Ya no disponible" | se arma el snapshot | se excluye del arreglo `items` y el resumen ya la había mostrado como excluida | API | H4-F4 | — | — |

### SPEC-16 · Notificación de confirmación por correo

Fuente: [`openspec/specs/notificacion-confirmacion/spec.md`](../openspec/specs/notificacion-confirmacion/spec.md).

| ID | Escenario | Dado | Cuando | Entonces | Nivel | Tarea | Humo | Prueba existente |
|---|---|---|---|---|---|---|---|---|
| CP-H4-16-01 | Req. 1 · Correo enviado | un pedido con el pago notificado a Ventas | el worker procesa `SEND_EMAIL` | se envía a `maria@ejemplo.com` el asunto "Confirmamos tu pedido PED-2026-00891" con el detalle completo, y `notification` queda en `SENT` | API | H4-F5 | — | — |
| CP-H4-16-02 | Req. 1 · Contenido fiel al pedido | un pedido con cupón y envío | se renderiza la plantilla | los importes coinciden exactamente con el snapshot enviado a Ventas y la tarjeta aparece como "Visa •••• 1111" | Unidad | H4-F5 | — | — |
| CP-H4-16-03 | Req. 2 · Reproceso del evento | un correo ya `SENT` para el pedido | el worker recibe otra vez la tarea | no se envía un segundo correo (clave única `(order_id, resend_number)`) | API | H4-F5 | — | — |
| CP-H4-16-04 | Req. 2 · Proveedor SMTP caído | que el SMTP falla | se intenta el envío | se reintenta hasta 3 veces (1 min, 5 min y 15 min); si falla, queda `FAILED` con `last_error`, y el pedido y el chat no se ven afectados | API | H4-F5 | — | — |
| CP-H4-16-05 | Req. 3 · Confirmación en el chat sin correo | un pedido confirmado con el correo aún pendiente | se muestra `CONFIRMACION_PEDIDO` | el mensaje dice "Te enviaremos la confirmación a m****a@…", sin prometer que ya llegó | E2E | H4-F5 | E2E-11 | — |
| CP-H4-16-06 | Req. 3 · El cliente pide reenviar el correo | un pedido con el correo `SENT` o `FAILED` | el cliente escribe "no me llegó el correo" | se sugiere revisar spam y se ofrece "Reenviar", que crea un reenvío (máx. 2 por pedido, tipo `CONFIRMATION_RESEND`) | Eval | H4-F5 | E2E-12 | — |

## Registro de ejecución

Se completa con la ejecución contra producción antes de la demo (H4-P1): fecha, commit desplegado de cada repositorio, casos que pasan, casos que fallan con su incidencia y casos bloqueados.
