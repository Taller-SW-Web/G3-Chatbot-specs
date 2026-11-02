# Integraciones pendientes para el Hito 4 — qué nos falta y qué les falta

> Revisión hecha el **02/11/2026**, cinco días antes de la presentación del Hito 4 (07/11). Complementa a [`contratos-integracion.md`](contratos-integracion.md), que sigue siendo la referencia de endpoints y payloads. Aquí solo se lista **lo que falta para conectar de verdad** con cada módulo: lo que necesitamos de ellos y lo que ellos necesitan de nosotros.

Fuentes revisadas (rama por defecto al 02/11): `Modulo-de-Seguridad` y `Modulo-de-Seguridad-Backend` (rama `develop`), `G2-Despacho-Specs` y `G2-Despacho-Backend`, `G5-Ventas-Postventas` y `G5-Ventas-Postventas-Backend`, `G6-Productos-Ofertas-docs` y `G6-Productos-Ofertas-backend`, `G1-Marketplace-SPECS` y `G1-Marketplace-Backend`, `G4-Retail-specs` y `G4-Retail-backend`, más los issues abiertos que mencionan al chatbot. También se revisó nuestro backend (`main` y `development`).

Leyenda: 🔴 bloquea la conexión real · 🟡 hay que resolverlo pero no bloquea · 🟢 ya está.

---

## 0. Resumen

| Módulo | Estado del contrato | Lo que más bloquea hoy |
|---|---|---|
| **G7 Seguridad** | ✅ Publicado y desplegado en Render | 🔴 Nuestro backend rechaza los tokens reales (issuer fijo `auth-service`). 🔴 Falta que nos entreguen el `client_secret` real de `modulo-chatbot`. |
| **G5 Ventas y Postventa** | ✅ Cerrado (A15) e implementado en Render | 🔴 Nuestro adaptador de Ventas está vacío. |
| **G6 Productos y Ofertas** | ✅ Aceptado (A16/A17), OpenAPI `0.6.0-rc.2` | 🔴 No hay URL pública para consumirlos (Oracle en red privada). 🔴 No enviamos token de servicio. |
| **G2 Despacho** | ✅ Contrato cerrado, desplegado en Render | 🔴 El seguimiento por pedido no está implementado en su backend. 🔴 Nuestro adaptador de Despacho está vacío. |
| **G4 Retail** | Sin integración directa | 🟡 Sus specs asumen que el chatbot vende con retiro en tienda. |
| **G1 Marketplace** | Sin integración directa | — |

**Lo urgente de nuestro lado** (sección 7): hacer configurable el issuer, conectar el token de servicio a todos los clientes HTTP, escribir los adaptadores de Ventas, Despacho y cupones/recomendaciones, corregir el formato de `X-Correlation-Id`, fusionar los PR #22 y #23 de specs y mandarle a Seguridad nuestra URL de producción.

URLs de despliegue encontradas en sus repos:

| Módulo | URL base |
|---|---|
| Seguridad | `https://g7-auth-service.onrender.com/api/v1` (issuer `https://g7-auth-service.onrender.com/api/v1/auth`) |
| Ventas (gateway) | `https://g5-api-gateway.onrender.com` (M1: `g5-servicio-ventas.onrender.com`, M2: `g5-ventas-postventas-backend.onrender.com`) |
| Despacho (gateway) | `https://taller-api-gateway.onrender.com` |
| Productos | **No publicada** (Oracle + Tailscale, red privada) |
| Chatbot (nosotros) | Frontend `https://g3-chatbot-frontend.vercel.app` · Backend `https://g3-chatbot-backend.up.railway.app` |

---

## 1. G7 — Seguridad y Usuarios

Estado: contrato publicado, backend desplegado en Render. En `develop` ya están implementados el token de servicio (`POST /auth/token`), la introspección y la consulta de identidad (FEAT-05 y FEAT-06, fusionados el 01/11). Hay un runbook para crear clientes y un SQL de concesiones que ya incluye todas las filas de `modulo-chatbot`.

### 1.1 Lo que necesitamos de ellos

| # | Qué | Estado | Referencia |
|---|---|---|---|
| S1 | 🔴 Crear el cliente `modulo-chatbot` en producción y entregarnos el `client_secret` por un canal privado (no por issue ni PR). | Pendiente. Seguridad #10 sigue abierto; el runbook `docs/runbooks/clientes-servicio.md` describe el paso. | Seguridad #10 |
| S2 | 🔴 Ejecutar las concesiones de `modulo-chatbot`: `usuarios:leer`, `tokens:introspeccion` (api-seguridad); `cotizaciones:calcular`, `seguimientos:leer` (api-despacho); `ventas:pedidos:crear`, `ventas:pedidos:anular`, `ventas:pagos:webhook`, `postventa:devoluciones:escribir`, `postventa:reclamos:escribir` (api-ventas/api-postventa); los siete de Productos (`catalogo:leer`, `precios:leer`, `promociones:leer`, `promociones:evaluar`, `cupones:validar`, `recomendaciones:leer`, `inventario:disponibilidad:leer`, api-productos). | Todas "Aprobadas" en su matriz, ninguna aprovisionada. | `docs/migraciones-propuestas/concesiones-servicio.sql`, Seguridad #33, #42 |
| S3 | 🟡 Confirmar adónde lleva el enlace de verificación de correo cuando `canalOrigen=CHATBOT`. Hoy **todos** los canales van a `/verificar-correo` de la SPA de Seguridad con `&canal=CHATBOT`; la pantalla propia del chatbot "queda pendiente" en su código. Opciones: (a) que el enlace vaya a nuestra `/verificar-correo?token=…`, o (b) que su SPA verifique y nos devuelva a nuestra pantalla de login. | Abierto. | Seguridad #32, `CorreoVerificacionAdapter.java` |
| S4 | 🟡 Confirmar el `scope` que debemos pedir en `POST /auth/token` cuando el mismo cliente llama a varias APIs (¿un token con todos los scopes y `aud` múltiple, o un token por API?). Su kit dice que `aud` lleva la lista de APIs dueñas de los scopes concedidos. | Confirmar en la primera prueba. | Kit §5 «Scopes de la API de otro módulo» |

### 1.2 Lo que ellos necesitan de nosotros

| # | Qué | Estado |
|---|---|---|
| S5 | 🔴 Alinear el issuer: nuestro backend valida `iss == "auth-service"` (constante en `jwks_token_validator.py`), pero el issuer real es `https://g7-auth-service.onrender.com/api/v1/auth`. Seguridad pide que salga del documento de descubrimiento configurado por entorno, nunca del token. También hay que corregirlo en `contratos-integracion.md` L24, `inicio-sesion/spec.md` L166 y ADR-0009. | Pendiente nuestro. Seguridad lo marcó en `docs/integracion/correcciones-modulos.md` §G3. |
| S6 | 🟡 Retirar la espera del rol `SERVICIO_INTEGRACION` (nuestro A4). No existe: el servicio se identifica por `tipo: servicio` y `sub: modulo-chatbot`, y Despacho valida `aud` y scope. Afecta `contratos-integracion.md` (A4, A11), ADR-0009 y `seguimiento-despacho` (spec y design). | Pendiente nuestro. |
| S7 | 🟡 Pasarles la URL de producción de nuestra pantalla de verificación: `https://g3-chatbot-frontend.vercel.app/verificar-correo`. Seguridad #32 sigue esperando las URL de desarrollo y producción. | Pendiente nuestro. |
| S8 | 🟡 Confirmar que **no consumimos eventos** de `seguridad.usuarios` en este ciclo. Su catálogo de eventos dice "Chatbot: por confirmar". | Pendiente nuestro (respuesta de una línea). |

---

## 2. G5 — Ventas y Postventa

Estado: acuerdo cerrado (A15 / su `ACUERDO_G3_CHATBOT.md`, 12/10). Los endpoints que usamos están implementados en su backend (`/pedidos/me`, `/pedidos/{id}/pagos/notificacion`, `/anulaciones`, `/devoluciones/evidencias/upload`, `/devoluciones/me`, `/reclamos/me`, `/reclamos/{codigoSeguimiento}`, `/csat`) y desplegados en Render desde el 26/10.

### 2.1 Lo que necesitamos de ellos

| # | Qué | Estado |
|---|---|---|
| V1 | 🟢 Contrato y endpoints. | Listo. |
| V2 | 🟡 Confirmar que debemos usar el gateway (`https://g5-api-gateway.onrender.com`) como `SALES_BASE_URL` para M1 y M2. Su gateway rutea `/api/*/pedidos/**` a M1 y el resto a M2. | Confirmar. |
| V3 | 🟡 Una cuenta `CLIENTE` de prueba y un pedido `ENTREGADO` en su base, para probar CSAT, devoluciones y los `/me` en la nube. | Pedir. |

Novedades de su contrato desde el 12/10 (no nos obligan a nada):

- `GET /api/v1/pedidos/me` acepta ahora `desde` y `hasta` (`YYYY-MM-DD`, hora de Perú) y un error `400 RANGO_FECHAS_INVALIDO` (contrato M1 v1.8.0, 02/11, acuerdo H-06 con Marketplace).
- **Regla que sí nos afecta:** como el chatbot cobra antes de que Productos confirme el stock, si Productos rechaza la reserva el pedido pasa **`PAGADO → ANULADO`** (motivo `STOCK_NO_DISPONIBLE`) con reembolso automático por F4. El chat tiene que mostrar ese caso en el estado del pedido (etiqueta "Anulado" y mensaje de reembolso), no solo la anulación por pago no completado.

### 2.2 Lo que ellos necesitan de nosotros

| # | Qué | Estado |
|---|---|---|
| V4 | 🔴 Implementar el adaptador de Ventas. `ventas_api_adapter.py` está vacío (0 líneas) en `main` y `development`. | Pendiente nuestro. |
| V5 | 🟡 Responder la pregunta abierta de su C4 nivel 1 §5: "¿las solicitudes de postventa llegan siempre a través del chatbot?". Respuesta: sí, todo pasa por nuestro BFF; nuestro frontend nunca los llama directo. Escrituras con token de servicio y `/me`, detalles y CSAT con el token del cliente. | Pendiente nuestro. |
| V6 | 🟡 Enviar `canal: "CHATBOT"` en pedidos, reclamos y CSAT. El canal web se llama `MARKETPLACE`, nunca `WEB`. | Verificar en el adaptador. |

---

## 3. G6 — Productos y Ofertas

Estado: acuerdo A16/A17 **aceptado documentalmente** por ambos equipos (G6 docs #87, #99 y PR #104). Su contrato vigente es OpenAPI `0.6.0-rc.2` (01/11). Su plan H4 es: demo restringida sin JWT desde el 01/11, **JWT real el 06/11** y presentación el 07/11.

### 3.1 Lo que necesitamos de ellos

| # | Qué | Estado |
|---|---|---|
| P1 | 🔴 **Una URL base alcanzable** desde Railway. Su backend se despliega en Oracle con Tailscale (red privada) y su demo sin login "exige red privada". Marketplace también tiene `PRODUCTOS_BASE_URL=https://HOST_APROBADO` sin valor. Sin esto no hay conexión real. | Abierto. Preguntar en G6 backend #19 o #27. |
| P2 | 🔴 Que las operaciones del corte chatbot estén implementadas. Promociones (reglas y consultas HTTP, #72 y #73) e inventario E2E (#105) siguen abiertos al 02/11. | En curso en su lado. |
| P3 | 🟡 Saber si en la demo validan el JWT o aceptan llamadas sin token, y desde qué fecha exigen el token real (su plan dice 06/11). | Preguntar. |
| P4 | 🟡 Datos de catálogo, precios y stock cargados (DATA-002 y DATA-004 siguen abiertos, #12 y #14). | En curso en su lado. |
| P5 | 🟡 Matrices de errores B9/B10 (SKU inexistente o inactivo, límites, 422) y pauta de caché y concurrencia. | Sin issue asignado en su lado. |
| P6 | ⚪ Ampliaciones B3–B8 (filtros de talla y color, orden por precio, resumen de promociones, desglose por línea, monto faltante del cupón). | No vigentes; no contar con ellas en H4. |

### 3.2 Lo que ellos necesitan de nosotros

| # | Qué | Estado |
|---|---|---|
| P7 | 🔴 Enviar el token de servicio (`Authorization: Bearer`, `aud=api-productos`). Hoy `ProductsClient` e `InventoryClient` no mandan `Authorization`: `provide_service_token_provider` existe en el contenedor, pero nadie lo usa. | Pendiente nuestro (G3 backend #52). |
| P8 | 🔴 `X-Correlation-Id` como UUID **con guiones**, el mismo valor durante toda la interacción. `BaseModuleClient` genera `uuid4().hex` (sin guiones). | Pendiente nuestro. |
| P9 | 🟡 Adaptadores que faltan: `cupones_api_adapter.py` y `evaluacion_api_adapter.py` están vacíos, y no hay cliente de `GET /recomendaciones`. | Pendiente nuestro. |
| P10 | 🟡 Fusionar los PR #22 y #23 de este repo (A17). G6 lee nuestra `main` y anota que todavía tiene texto anterior a A17 y `pending-security-registration`. Al fusionar, aclarar que esa etiqueta significa *grant pendiente en G7*, no *falta de ratificación*. | PR abiertos desde el 24/10. |
| P11 | 🟡 Homologación D3: correr con `MODULES_MODE=http` contra sus servicios reales y entregar un reporte con entorno, versión del contrato, SHA de ambos lados, autenticación usada y evidencia. Se coordina en G6 backend #27, y ellos esperan nuestra aceptación explícita. | Pendiente de ambos. |
| P12 | 🟡 Frontend: estados de disponibilidad y "Precio no disponible" según D2 (G3 frontend #30). | Pendiente nuestro. |

---

## 4. G2 — Despacho y Entrega

Estado: contrato cerrado (cotización `POST /api/v1/cotizaciones` y seguimiento `GET /api/v1/seguimientos/pedidos/{idPedido}`, ambos con token de servicio y `aud=api-despacho`). Gateway desplegado en `https://taller-api-gateway.onrender.com`.

### 4.1 Lo que necesitamos de ellos

| # | Qué | Estado |
|---|---|---|
| D1 | 🔴 **Implementar el seguimiento** `GET /api/v1/seguimientos/pedidos/{idPedido}`. En su backend solo existe la regla de seguridad (`seguimientos:leer`); no hay controlador que lo atienda. | Preguntar fecha. |
| D2 | 🟡 Que su gateway en Render apunte a la Seguridad real (`SEGURIDAD_URL` sigue como `https://<host-real-de-seguridad>` en la plantilla) para aceptar nuestros tokens reales. | Confirmar. |
| D3 | 🟡 La cotización exacta depende de que G6 le conceda `productos:fisicos:leer` a `modulo-despacho` (G2-Despacho-Specs #15). Mientras tanto usan un catálogo de prueba en Gestión: confirmar qué SKU sirven para probar. | Depende de G6 y G7. |
| D4 | 🟡 Confirmar que `idPedido` es el mismo `pedidoId` que devuelve Ventas (el ejemplo usa `PED-2026-00891`). | Confirmar. |

Novedad del contrato: la respuesta de seguimiento trae `estadoEtiqueta` y etiquetas por hito; las podemos usar en lugar de nuestra tabla de la sección 4 de `contratos-integracion.md`, o mantener la nuestra.

### 4.2 Lo que ellos necesitan de nosotros

| # | Qué | Estado |
|---|---|---|
| D5 | 🔴 Implementar el adaptador de Despacho (`despacho_api_adapter.py` está vacío). Payload: `destino{direccion, distrito, codigoPostal?}` y `lineas[{sku, cantidad}]`. `distrito` es el único campo obligatorio del destino. | Pendiente nuestro. |
| D6 | 🟡 Tener el cliente técnico con `cotizaciones:calcular` y `seguimientos:leer`, guardar el `client_secret` y consultar el seguimiento solo por `idPedido` (su §11, "lo que piden a Marketplace y Chatbot"). | Depende de S1/S2. |
| D7 | 🟡 Manejar sus errores `DESP_ERROR_*`, incluido el nuevo `500 DESP_ERROR_PERSISTENCIA_COTIZACION`, y la cotización sin costo cuando no hay cobertura. | Pendiente nuestro. |

---

## 5. G4 — Retail

No hay llamadas entre nuestros módulos. Un solo punto:

| # | Qué | Dirección |
|---|---|---|
| R1 | 🟡 Sus specs F06 y F07 asumen que el chatbot puede vender con **retiro en tienda** (*store pickup*). Con A17-D1 el chatbot solo hace envío a domicilio (`fulfillment.mode=ENVIO_DOMICILIO`). Avisarles para que no esperen pedidos del chatbot en su flujo de retiro. | Nosotros → ellos |

## 6. G1 — Marketplace

Sin integración directa. Ellos comparten con nosotros los endpoints de Ventas (`/pedidos/me` tiene formato reducido por el acuerdo H-03 con ellos) y no deben heredar nuestros grants en Productos. No hay nada que pedir ni que entregar.

---

## 7. Lista de trabajo de nuestro lado, por prioridad

| Prioridad | Tarea | Repo | Ref. |
|---|---|---|---|
| 1 | Issuer y JWKS por configuración (`SECURITY_ISSUER`, `SECURITY_JWKS_URL` o descubrimiento); quitar `EXPECTED_ISSUER = "auth-service"`. | backend | S5 |
| 2 | Inyectar `ServiceTokenProvider` en los clientes de Productos, Ventas y Despacho, y pedir los scopes correctos. | backend | P7, S4 |
| 3 | `X-Correlation-Id` con UUID con guiones, propagado durante toda la interacción. | backend | P8 |
| 4 | Adaptadores de Ventas y Despacho, y de cupones, evaluación y recomendaciones de Productos. | backend | V4, D5, P9 |
| 5 | Fusionar los PR #22 y #23 de specs y corregir issuer y `SERVICIO_INTEGRACION` en specs y ADR-0009. | specs | P10, S5, S6 |
| 6 | Comentar en Seguridad #32 la URL de verificación de producción y confirmar que no consumimos eventos. | — | S7, S8, S3 |
| 7 | Responder a Ventas la pregunta del C4 (todo por nuestro BFF). | — | V5 |
| 8 | Mostrar `PAGADO → ANULADO` por `STOCK_NO_DISPONIBLE` con reembolso. | backend + frontend | §2.1 |
| 9 | Variables de producción en Railway: URLs base reales, `MODULES_MODE=http` en el entorno de homologación y el secreto real cuando llegue. | backend | S1, P11 |
| 10 | Avisar a Retail que no hay retiro en tienda por el chatbot. | — | R1 |

## 8. Mensajes para enviar

Estos son los pedidos que hay que hacer en sus repositorios (issue o comentario):

- **Seguridad #10 / #33:** pedir la creación de `modulo-chatbot` en producción, las concesiones de §1.1 S2 y la entrega privada del secreto, y preguntar cómo pedir el `scope` en `/auth/token` para varias APIs.
- **Seguridad #32:** URL de producción `https://g3-chatbot-frontend.vercel.app/verificar-correo` y la pregunta S3.
- **G6 backend #27:** URL base alcanzable, fecha del JWT real, datos de prueba y fecha para la prueba bilateral.
- **G2 (nuevo issue en G2-Despacho-Specs):** fecha del seguimiento por pedido, `SEGURIDAD_URL` real en el gateway, SKU de prueba e `idPedido` = `pedidoId`.
- **G5 (nuevo issue en G5-Ventas-Postventas):** respuesta V5, gateway como URL base y datos de prueba.
- **G4 (nuevo issue en G4-Retail-specs):** aviso R1.
