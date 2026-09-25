# KPIs del chatbot

> Indicadores de negocio y de calidad conversacional del Canal Chatbot. Los requisitos no funcionales técnicos siguen definidos en cada spec (ver §4); este documento **no** agrega requisitos a las specs. Las metas son **propuestas para la demo del curso** y se recalibran con la primera medición real.

## 1. Convenciones

- **Conversación medible:** una conversación con al menos un mensaje del cliente (las conversaciones vacías no aparecen en el listado, SPEC-05 · Req. 1).
- **Sesión de conversación:** tramo de mensajes de una conversación sin una pausa mayor a 30 minutos. *Propuesta*: el modelo de datos no define un "fin de conversación" (una conversación puede retomarse días después), así que los KPIs por sesión usan esta ventana de inactividad.
- **Turno:** un mensaje del cliente y la respuesta completa del asistente (evento `fin` o respuesta REST).
- **Estado de medición:**
  - ✅ **Medible hoy:** se calcula con tablas de [`modelo-datos.md`](../modelo-datos.md) o con el log por turno que exige SPEC-05 · RNF *Observabilidad*.
  - 🟠 **Requiere instrumentación nueva:** falta un campo o evento; se indica cuál y queda como propuesta (ver [preguntas abiertas](README.md#preguntas-abiertas)).
- **Entornos:** se excluye el tráfico de QA y de pruebas automáticas; en la demo, las tarjetas de prueba de rechazo (`…0002`, `…0069`, `…0119`) se reportan aparte porque su resultado es determinista (SPEC-14 · Req. 5).

## 2. KPIs de negocio

| KPI | Definición | Fórmula | Fuente de datos | Estado | Meta demo (propuesta) | Revisión |
|---|---|---|---|---|---|---|
| **Conversión carrito → pedido** | Carritos que terminan en pedido pagado | carritos `CONVERTIDO` / carritos con al menos una línea, por período | `carrito.estado`, `item_carrito` | ✅ | ≥ 30 % en sesiones guiadas de demo | Semanal |
| **Abandono del checkout** | Checkouts creados que no terminan pagados | checkouts `EXPIRADO` + `FALLIDO` / checkouts creados | `checkout.estado` | ✅ | ≤ 30 % | Semanal |
| **Abandono antes del checkout** | Clientes que pulsan "Pagar" y no llegan a crear el checkout | `iniciar_checkout` sin `POST /checkout` posterior en 30 min / `iniciar_checkout` | `mensaje.herramienta` + `checkout.creado_en` 🟠 (`checkout` no tiene `creado_en` explícito; se deriva de `expira_en − 15 min`) | ✅ (derivado) | ≤ 40 % | Semanal |
| **Éxito de pago** | Pagos aprobados sobre intentos válidos | `intento_pago` `APROBADO` / `intento_pago` totales (excluyendo tarjetas de rechazo de prueba) | `intento_pago.resultado`, `intento_pago.ultimos4` | ✅ | ≥ 95 % | Por hito |
| **Checkouts con 3 rechazos** | Checkouts que agotan los intentos | checkouts `FALLIDO` / checkouts con al menos un intento | `checkout.estado`, `checkout.intentos_pago` | ✅ | ≤ 5 % | Por hito |
| **Turnos promedio hasta comprar** | Esfuerzo conversacional de una compra | promedio de mensajes `CLIENTE` entre el primer mensaje de la conversación y la creación del checkout pagado | `mensaje` (rol, `creado_en`) + `checkout` + `carrito.conversacion_id` 🟠 (el carrito de cliente no guarda `conversacion_id`; hay que registrar en qué conversación se inició el checkout) | 🟠 | ≤ 8 turnos | Por hito |
| **Postventa autoservida** | Consultas de pedido, reclamo o devolución resueltas en el chat | turnos con `consultar_pedido`/`consultar_seguimiento`/`consultar_reclamo`/`consultar_devolucion` con `resultado_codigo = OK` / turnos con esas herramientas | `mensaje.herramienta`, `mensaje.resultado_codigo` | ✅ | ≥ 90 % | Por hito |

## 3. KPIs de calidad conversacional

| KPI | Definición | Fórmula | Fuente de datos | Estado | Meta demo (propuesta) | Revisión |
|---|---|---|---|---|---|---|
| **Precisión de intención** (offline) | Aciertos del LLM sobre el conjunto etiquetado | ver [`intenciones.md` §5](intenciones.md#5-conjunto-de-evaluación-evalsintencionesjsonl) | `evals/intenciones.jsonl` + `pytest -m evals` | ✅ | **≥ 90 %** (exigido por SPEC-05 · RNF *Calidad*) | En cada cambio de prompt o modelo (CI) |
| **Tasa de contención** | Sesiones resueltas sin abandono ni escalamiento | sesiones sin (a) abandono tras un error o fallback y (b) derivación a reclamo por "pedir humano" / sesiones | `mensaje` + etiqueta de intención por turno 🟠 + evento `ABANDONO` derivado de la ventana de 30 min | 🟠 | ≥ 70 % | Semanal |
| **Finalización de tarea por intención** | Intenciones cuyo objetivo se cumplió | por intención: turnos con herramienta esperada y `resultado_codigo = OK` seguido del resultado de negocio (p. ej., `INT-CAR-02` → línea creada) / turnos de esa intención | `mensaje.herramienta`, `mensaje.resultado_codigo` + etiqueta de intención 🟠 | 🟠 (parcial ✅ por herramienta) | ≥ 85 % en intenciones Must | Semanal |
| **Tasa de fallback ("no entendí")** | Turnos en que el asistente no pudo interpretar | turnos con respuesta de "no entendí" o reintento de argumentos agotado / turnos de texto | `mensaje.resultado_codigo = VALIDACION` tras el reintento (SPEC-05 · Req. 6) ✅ + marca de fallback general 🟠 | 🟠 | ≤ 10 % | Semanal |
| **Tasa de aclaración** | Turnos que terminan en una pregunta aclaratoria | turnos sin herramienta clasificados como `INT-SIS-05` / turnos de texto | etiqueta de intención por turno 🟠 | 🟠 | 10–25 % (menos indica suposiciones; más, fricción) | Semanal |
| **Fuera de dominio** | Mensajes ajenos a la tienda | turnos `INT-SIS-04` / turnos de texto | etiqueta de intención por turno 🟠 | 🟠 | Solo seguimiento | Mensual |
| **Pedidos de humano** | Frecuencia de `INT-SIS-07` | turnos `INT-SIS-07` / sesiones | etiqueta de intención por turno 🟠 | 🟠 | Solo seguimiento (insumo para decidir si se agrega un canal de contacto) | Mensual |
| **Tasa de modo degradado** | Turnos atendidos sin LLM | turnos respondidos por `DegradedMode` / turnos de texto | marca de modo degradado en `mensaje` o en el log 🟠 | 🟠 | ≤ 2 % | Diaria durante la demo |
| **Correcciones del validador de salida** | Precios del texto que no coincidían con las herramientas | turnos con corrección en `fin` / turnos con precio en el texto | log de `OutputValidator` 🟠 | 🟠 | 0 en la demo; cualquier caso se revisa | Por hito |
| **CSAT (propuesta)** | Satisfacción con la respuesta | 👍 / (👍 + 👎) | evento de valoración 🟠 (no existe en las specs) | 🟠 **Propuesta** | ≥ 80 % | Semanal |
| **Costo por conversación** | Costo del LLM por conversación medible | Σ (`tokens_entrada` × precio de entrada + `tokens_salida` × precio de salida) / conversaciones | `mensaje.tokens_entrada`, `mensaje.tokens_salida` + tabla de precios del modelo en configuración 🟠 | ✅ tokens · 🟠 precio | Línea base en Hito 3; después, no superar la línea base en más de 20 % tras cambios de prompt o modelo | Semanal |
| **Latencia percibida** | Tiempo hasta el primer fragmento y del turno completo | p95 de `mensaje.latencia_ms` (turno) y del primer evento `token` | `mensaje.latencia_ms` ✅; primer fragmento 🟠 (no hay campo) | ✅ / 🟠 | Las del RNF: ≤ 2 s y ≤ 6 s | Diaria durante la demo |

### CSAT: propuesta (no está en las specs)

Una sola pregunta, sin interrumpir la compra: después de un bloque `CONFIRMACION_PEDIDO`, `CONSTANCIA_RECLAMO` o `CONSTANCIA_DEVOLUCION`, o tras una despedida, se muestran dos botones "👍" / "👎" con el texto "¿Te sirvió esta conversación?". Es opcional, se muestra como máximo una vez por sesión y no se vuelve a pedir si el cliente lo ignora. No se debe confundir con la encuesta de satisfacción de Ventas (F5), que SPEC-16 deja fuera de alcance. Si el equipo la aprueba, se incorpora a SPEC-05 mediante un cambio de OpenSpec (acción directa `VALORAR_CONVERSACION` y un campo o tabla nueva); hasta entonces es solo una propuesta ([pregunta abierta 9](README.md#preguntas-abiertas)).

## 4. Métricas técnicas ya definidas en las specs

Se listan para tenerlas en un solo lugar; la definición vigente es la de cada spec.

| Métrica | Umbral | Fuente |
|---|---|---|
| Primer fragmento por WebSocket | p95 ≤ 2 s | [SPEC-05 · RNF](../../openspec/specs/motor-conversacion/spec.md) |
| Turno completo | p95 ≤ 6 s | SPEC-05 · RNF |
| Acción directa por REST | p95 ≤ 1,5 s | SPEC-05 · RNF |
| Conjunto de evaluación / precisión de intención | ≥ 120 frases / ≥ 90 % | SPEC-05 · RNF |
| Timeout del LLM | 15 s (luego modo degradado) | SPEC-05 · Req. 10 |
| Latencia añadida por el BFF al registro | p95 < 150 ms | [SPEC-01 · RNF](../../openspec/specs/registro-cliente/spec.md) |
| Validación local del JWT | < 5 ms | [SPEC-03 · RNF](../../openspec/specs/inicio-sesion/spec.md) |
| Búsqueda (sin LLM) | p95 ≤ 800 ms | [SPEC-06 · RNF](../../openspec/specs/busqueda-filtrado/spec.md) |
| Recomendación completa | p95 ≤ 7 s | [SPEC-07 · RNF](../../openspec/specs/recomendacion/spec.md) |
| Validación masiva de stock (20 SKU) | p95 ≤ 500 ms | [SPEC-10 · RNF](../../openspec/specs/validacion-stock/spec.md) |
| Carrito: lectura / modificación | p95 ≤ 900 ms / ≤ 700 ms | [SPEC-11 · RNF](../../openspec/specs/gestion-carrito/spec.md) |
| Cotización de envío | p95 ≤ 600 ms | [SPEC-12 · RNF](../../openspec/specs/direccion-cotizacion-envio/spec.md) |
| Pago simulado | p95 ≤ 1 s | [SPEC-14 · RNF](../../openspec/specs/checkout-pago/spec.md) |
| Creación del pedido | p95 ≤ 1,5 s | [SPEC-15 · RNF](../../openspec/specs/grabacion-pedido/spec.md) |
| Correo de confirmación | ≤ 60 s en el 95 % | [SPEC-16 · RNF](../../openspec/specs/notificacion-confirmacion/spec.md) |
| Consulta de pedido | p95 ≤ 800 ms (≤ 1,2 s con Despacho) | [SPEC-17 · RNF](../../openspec/specs/consulta-estado-pedido/spec.md) |
| Seguimiento | p95 ≤ 600 ms | [SPEC-18 · RNF](../../openspec/specs/seguimiento-despacho/spec.md) |
| Registro de reclamo / consulta de duplicados | p95 ≤ 1 s / ≤ 500 ms | [SPEC-19 · RNF](../../openspec/specs/creacion-reclamo/spec.md) |
| Consulta de reclamo | p95 ≤ 800 ms | [SPEC-20 · RNF](../../openspec/specs/consulta-reclamo/spec.md) |
| Carga de evidencia / registro de solicitud | p95 ≤ 3 s / ≤ 1 s | [SPEC-21 · RNF](../../openspec/specs/solicitud-devolucion-cambio/spec.md) |
| Consulta de devolución | p95 ≤ 800 ms | [SPEC-22 · RNF](../../openspec/specs/consulta-devolucion-reembolso/spec.md) |

## 5. Instrumentación nueva necesaria (resumen)

Nada de esto está en las specs ni en el modelo de datos; se propone para decidir en equipo ([pregunta abierta 16](README.md#preguntas-abiertas)).

| Necesidad | Propuesta mínima | KPIs que habilita |
|---|---|---|
| Etiqueta de intención por turno | Registrar el ID `INT-…` inferido (herramienta invocada o clasificación de sistema) en el log por turno de SPEC-05 · RNF *Observabilidad*, que ya exige registrar "la intención" | Contención, finalización, aclaración, fuera de dominio, pedidos de humano |
| Marca de respuesta de fallback | Valor fijo en el log por turno (`respuesta = FALLBACK`) | Tasa de fallback |
| Marca de modo degradado | Valor fijo en el log por turno (`modo = DEGRADADO`) | Tasa de modo degradado |
| Latencia del primer fragmento | Campo en el log por turno | Latencia percibida |
| Correcciones de `OutputValidator` | Contador en el log por turno | Correcciones del validador |
| Conversación donde se inició el checkout | `conversacion_id` en `checkout` o en el log de `iniciar_checkout` | Turnos hasta comprar |
| Valoración 👍/👎 | Acción directa y almacenamiento (solo si se aprueba el CSAT) | CSAT |
| Precio por token del modelo | Variable de configuración junto al proveedor y el modelo | Costo por conversación |

Todas las marcas nuevas respetan SPEC-05 · RNF *Observabilidad*: **sin datos personales en el texto del log**.

## 6. Cadencia de revisión

| Cadencia | Qué se revisa | Quién |
|---|---|---|
| En cada PR que cambie el prompt, las herramientas o el modelo | Precisión de intención en CI (bloqueante ≥ 90 %) | Tech lead |
| Diaria durante la semana de demo | Latencias p95, modo degradado, errores de módulos externos | Equipo de backend |
| Semanal | Conversión, abandono, contención, fallback, aclaración, costo | PO + equipo |
| Al cerrar cada hito | Éxito de pago, turnos hasta comprar, postventa autoservida; recalibrar metas | PO |
