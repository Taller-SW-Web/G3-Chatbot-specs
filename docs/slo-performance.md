# SLO de rendimiento del backend

> Tarea H5-P1 de [`odd/tasks/hito-5.md`](../odd/tasks/hito-5.md). Fecha: 2026-11-24.
> Los scripts que los miden son H5-P2 y el workflow que los ejecuta, H5-P3, ambos en
> `G3-Chatbot-backend/tests/performance/k6/`.

Este documento fija los objetivos de rendimiento (SLO) de los tres flujos que el Hito 5 mide con
carga: **catálogo**, **chat** y **checkout**. No crea comportamiento nuevo. Las latencias salen de
los requisitos no funcionales que ya están en las specs, y este documento solo agrega lo que las
specs no dicen: la tasa de error, el throughput y las condiciones de la medición.

## 1. Condiciones de la medición

Los SLO se miden contra el **stack local o de CI**, nunca contra producción:

| Elemento | Valor |
|---|---|
| Backend | Una réplica de `uvicorn` con el código de `development` |
| Base de datos | PostgreSQL 18 en Docker, con las migraciones al día |
| Módulos externos | `MODULES_MODE=fake`: Seguridad, Productos, Ventas y Despacho en memoria ([ADR-0022](arquitectura/adr/ADR-0022-modulos-simulados-en-proceso-para-los-entornos-desplegados.md)) |
| LLM | `LLM_PROVIDER=fake`: un modelo con guion fijo que pide `buscar_productos` y cierra con texto, sin red |
| Broker | RabbitMQ en Docker, nunca CloudAMQP ([ADR-0030](arquitectura/adr/ADR-0030-rabbitmq-como-mecanismo-asincrono-del-outbox.md)), cuando existan el relay y el consumidor (H5-M2 y H5-M3); hasta entonces el outbox trabaja solo |

Por qué no se mide contra producción (restricción de `hito-5.md`):

- Railway tiene un solo entorno. Una corrida de carga degrada la demo y el fake de Ventas pierde los
  pedidos con cada despliegue.
- Una corrida contra CloudAMQP puede agotar la cuota mensual de mensajes (1 M al mes).
- Con los módulos reales, la latencia medida sería la de G2, G5, G6, G7 y OpenAI, no la del backend.

Consecuencia: **los SLO miden el costo propio del backend** (HTTP, casos de uso, base de datos,
bucle de herramientas y SSE). La latencia del LLM real y de los otros grupos queda fuera y se
controla con los timeouts por integración de [ADR-0010](arquitectura/adr/ADR-0010-integracion-sincrona-por-api-sin-eventos.md).

## 2. SLO por flujo

Las cifras de latencia son el p95 durante la ventana de carga sostenida. La columna "Origen" indica
el requisito de la spec del que sale cada cifra. Donde la spec cuenta el LLM o un módulo externo, el
SLO usa el mismo número como techo, porque el backend no puede gastar por sí solo más que el
presupuesto completo.

### 2.1 Catálogo (`mod-catalog`)

| Operación | Endpoint | p95 | Origen |
|---|---|---|---|
| Búsqueda con filtros | `GET /api/v1/catalogo/productos` | ≤ 800 ms | SPEC-06 · RNF (búsqueda excluido el LLM) |
| Detalle de producto | `GET /api/v1/catalogo/productos/{id}` | ≤ 800 ms | SPEC-06 · RNF, misma consulta a Productos |
| Promociones vigentes | `GET /api/v1/catalogo/promociones` | ≤ 800 ms | SPEC-08 · RNF (caché de 60 s) y SPEC-06 |
| Disponibilidad | `GET /api/v1/catalogo/disponibilidad` | ≤ 500 ms | SPEC-10 · RNF (consulta masiva ≤ 500 ms) |

### 2.2 Chat (`mod-chat`)

| Operación | Endpoint | p95 | Origen |
|---|---|---|---|
| Crear conversación | `POST /api/v1/chat/conversaciones` | ≤ 500 ms | Sin cifra en la spec; se fija igual que las lecturas puntuales |
| Primer evento SSE (`aceptado`) | `POST .../mensajes` (tiempo hasta el primer byte) | ≤ 2 s | SPEC-05 · RNF (primer fragmento) |
| Turno completo hasta `fin` | `POST .../mensajes` con texto | ≤ 6 s | SPEC-05 · RNF (turno completo) |
| Acción directa | `POST .../mensajes` con `accion` | ≤ 1,5 s | SPEC-05 · RNF (acciones directas por REST) |
| Historial | `GET .../mensajes` | ≤ 800 ms | Sin cifra en la spec; se fija igual que las consultas de SPEC-17 |

Con el LLM falso, el turno solo cuenta el costo propio del backend. Con el modelo real hay que sumar
la latencia de OpenAI, que el SLO no controla.

### 2.3 Checkout (`mod-cart` y `mod-checkout`)

| Operación | Endpoint | p95 | Origen |
|---|---|---|---|
| Agregar al carrito | `POST /api/v1/carrito/items` | ≤ 700 ms | SPEC-11 · RNF (agregar sin LLM) |
| Leer el carrito | `GET /api/v1/carrito` | ≤ 900 ms | SPEC-11 · RNF (lectura con recálculo) |
| Crear el checkout y el pedido | `POST /api/v1/checkout` | ≤ 1,5 s | SPEC-15 · RNF (creación del pedido) |
| Pagar | `POST /api/v1/checkout/{id}/pago` | ≤ 1 s | SPEC-14 · RNF (pago simulado) |

### 2.4 Tasa de error y throughput

| Flujo | Tasa de error | Carga sostenida | Throughput mínimo |
|---|---|---|---|
| Catálogo | < 1 % de respuestas 5xx o de red; 100 % de checks | 20 solicitudes/s durante 2 min | ≥ 19 solicitudes/s |
| Chat | < 1 %; ningún `429` | 10 clientes, cada uno envía un mensaje cada 3 a 5 s, durante 2 min | ≥ 1,5 mensajes/s (turnos y acciones directas) |
| Checkout | < 1 %; todos los pagos `APROBADO` | 1 cliente que compra en bucle durante 2 min | ≥ 0,3 compras/s |

Criterios de la tabla:

- **Tasa de error.** Cuenta como error toda respuesta 5xx, todo fallo de red y todo check fallido. Un
  `4xx` esperado por el escenario (por ejemplo un `409` de prueba) no se usa en estas corridas.
- **Chat sin `429`.** El límite de 20 mensajes por minuto por cliente (SPEC-05) es una regla de
  negocio, no un fallo de capacidad. La carga se diseña para no tocarlo: cada cliente virtual tiene
  su propia sesión anónima (`chat_sid`) y espera entre mensajes.
- **Checkout con un solo cliente.** El fake de Seguridad tiene un único cliente activo
  (`cliente@demo.pe`) y el carrito es uno por cliente, así que dos compras en paralelo pelearían por
  el mismo carrito. Por eso el checkout se mide en serie. Medirlo en paralelo exige sembrar más
  clientes en el fake de Seguridad, un cambio en `shared/` que queda pendiente.
- **Throughput.** La carga objetivo representa la demo del curso con holgura (unas decenas de
  clientes a la vez). No es una prueba de capacidad máxima.

## 3. Cómo se decide si se cumple

- Cada SLO es un *threshold* de k6. Si un threshold no se cumple, k6 termina con código distinto de
  cero y el workflow falla.
- El reporte de cada corrida (`k6-report.md` y el resumen JSON) compara el p95, la tasa de error y el
  throughput medidos con estos valores.
- Un SLO incumplido se corrige en el código o se renegocia en este documento con la evidencia. Nunca
  se relaja el threshold en el script sin cambiar este documento.

## 4. Resultados

### 2026-11-25 · corrida local sobre `development` `cf75beb`

Repetida después de los cambios del 2026-11-25 (contacto verificado en el checkout, backend #163, y
catálogo M5 de herramientas del chat, backend #166), con las mismas condiciones que la del 2026-11-24.
**Los tres flujos siguen cumpliendo todos los SLO**, con 0 % de errores y ningún `429`.

| Flujo | p95 más alto | Throughput medido | SLO de throughput |
|---|---|---|---|
| Catálogo | 26 ms (búsqueda) | 20,01 solicitudes/s | ≥ 19 solicitudes/s |
| Chat | 358 ms (turno completo; primer evento SSE 131 ms) | 2,30 mensajes/s | ≥ 1,5 mensajes/s |
| Checkout | 341 ms (pago) | 1,90 compras/s | ≥ 0,3 compras/s |

### 2026-11-24 · corrida local

Backend en la rama `feat/h5-p2-k6-performance` (sobre `development` `4fe2558`), PostgreSQL 18 en
Docker, módulos en fake, `LLM_PROVIDER=fake` y k6 2.4.0 en Docker. Ventana de 2 min por flujo,
corridos en serie. **Los tres flujos cumplen todos los SLO.**

| Flujo | Operación | p95 medido | SLO | Estado |
|---|---|---|---|---|
| Catálogo | Búsqueda | 18 ms | ≤ 800 ms | ✅ |
| Catálogo | Detalle | 13 ms | ≤ 800 ms | ✅ |
| Catálogo | Promociones | 14 ms | ≤ 800 ms | ✅ |
| Catálogo | Disponibilidad | 15 ms | ≤ 500 ms | ✅ |
| Chat | Crear conversación | 121 ms | ≤ 500 ms | ✅ |
| Chat | Primer evento SSE | 80 ms | ≤ 2 s | ✅ |
| Chat | Turno completo | 226 ms | ≤ 6 s | ✅ |
| Chat | Acción directa | 144 ms | ≤ 1,5 s | ✅ |
| Chat | Historial | 67 ms | ≤ 800 ms | ✅ |
| Checkout | Agregar al carrito | 80 ms | ≤ 700 ms | ✅ |
| Checkout | Leer el carrito | 68 ms | ≤ 900 ms | ✅ |
| Checkout | Crear el checkout | 77 ms | ≤ 1,5 s | ✅ |
| Checkout | Pagar | 259 ms | ≤ 1 s | ✅ |

| Flujo | Tasa de error | Throughput medido | SLO de throughput | Estado |
|---|---|---|---|---|
| Catálogo | 0,00 % (2 400 solicitudes) | 20,00 solicitudes/s | ≥ 19 solicitudes/s | ✅ |
| Chat | 0,00 %, 0 respuestas `429` | 2,34 mensajes/s | ≥ 1,5 mensajes/s | ✅ |
| Checkout | 0,00 %, todos los pagos aprobados | 2,28 compras/s | ≥ 0,3 compras/s | ✅ |

Lectura: con los módulos y el LLM en fake, el backend queda uno o dos órdenes de magnitud por debajo
de los techos. El margen es el presupuesto que queda para la latencia de los módulos reales y de
OpenAI. El workflow manual `performance.yml` ya está en `development` (H5-P3), pero aún no registra una corrida en GitHub Actions; la corrida local del 2026-11-25 es la evidencia vigente. El checkout se mide en serie hasta ampliar el fake de Seguridad ([backend#190](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/190)), y la corrida con RabbitMQ en Docker queda en [backend#168](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/168) (H5-P5).

## 5. Fuera de alcance

- Latencia del LLM real y de los módulos de otros grupos (se acotan con timeouts, ADR-0010).
- Pruebas de capacidad máxima, de resistencia de horas o con varias réplicas del backend.
- Métricas del frontend: van en H5-P4 (Lighthouse CI).
- Carga de adjuntos (SPEC-23) y postventa (SPEC-19 a 22).

## Referencias

- [`odd/tasks/hito-5.md`](../odd/tasks/hito-5.md): tareas H5-P1 a H5-P3 y restricciones de la medición.
- RNF de rendimiento en `openspec/specs/`: `busqueda-filtrado`, `ofertas-promociones`,
  `validacion-stock`, `motor-conversacion`, `gestion-carrito`, `grabacion-pedido` y `checkout-pago`.
- [ADR-0010](arquitectura/adr/ADR-0010-integracion-sincrona-por-api-sin-eventos.md): timeouts por integración.
- [ADR-0022](arquitectura/adr/ADR-0022-modulos-simulados-en-proceso-para-los-entornos-desplegados.md): módulos simulados en proceso.
