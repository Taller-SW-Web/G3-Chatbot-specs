# Contratos de integración — Canal Chatbot

> Documento transversal migrado desde `specs-chatbot/`. Las referencias `SPEC-NN` corresponden a las capacidades de [`openspec/specs/`](../openspec/specs/) (ver el índice en el [README](../README.md#3-índice-de-especificaciones)). Las referencias a secciones numeradas de una spec (por ejemplo, "§4 Requisito 1") remiten a la línea *Trazabilidad* de cada requisito en su `spec.md`.

Este documento reúne en un solo lugar lo que el chatbot **expone** a su frontend, lo que **consume** de los demás módulos y los acuerdos que siguen pendientes. Cada endpoint externo lleva uno de dos estados:

- ✅ **Confirmado:** está definido en el repositorio del módulo dueño.
- 🟡 **Provisional:** es una propuesta nuestra y está pendiente de homologar.

Revisión basada en los repos al 22/09/2026:

- `Modulo-de-Seguridad` (openapi.yaml y kit-integracion.md)
- `G2-Despacho-Specs` (overview.md y api-contract.md)
- `Productos-y-Ofertas-docs/specs`
- `G5-Ventas-Postventas/specs`

---

## 1. Autenticación entre componentes

| Caso | Mecanismo |
|---|---|
| Frontend → backend del chatbot | `Authorization: Bearer <accessToken del cliente>`. Las rutas públicas (catálogo, chat anónimo) aceptan la petición sin token. |
| Backend del chatbot → validación del token del cliente | Validación **local** con el JWKS de Seguridad (`/auth/.well-known/jwks.json`), cacheado. Se verifica `iss=auth-service` y `tipo=acceso`, y que el claim `roles` contenga `CLIENTE`. |
| Backend del chatbot → otros módulos (a nombre del sistema) | Token de servicio `client_credentials` con `client_id=modulo-chatbot` (`POST /auth/token`), cacheado hasta 60 s antes de su `exp`. |
| Backend del chatbot → Seguridad (a nombre del cliente) | Se reenvía el token del cliente cuando el recurso es del titular (por ejemplo, `/usuarios/{id}/direcciones`). |
| Refresh token | Nunca llega al JavaScript. El BFF lo guarda en una cookie `httpOnly; Secure; SameSite=Strict; Path=/api/v1/sesion`. |

---

## 2. API expuesta por el backend del chatbot (para su frontend)

Prefijo: `/api/v1`. Todas las respuestas de error usan `application/problem+json`.

### 2.1 Conversaciones (SPEC-05)
🧩 Ampliado para soportar conversaciones múltiples (barra lateral) y streaming por WebSocket, según la arquitectura del equipo.

| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| POST | `/chat/conversaciones` | Opcional | Crea una conversación vacía y devuelve `conversacionId`. |
| GET | `/chat/conversaciones` | Opcional* | Lista las conversaciones (propias o de la sesión anónima), ordenadas por `ultimo_mensaje_en` descendente, con `titulo` y vista previa del último mensaje. Paginado. |
| GET | `/chat/conversaciones/buscar?q=` | Opcional* | Busca por texto en el título y los mensajes. |
| GET | `/chat/conversaciones/{id}/mensajes` | Opcional* | Devuelve el historial paginado de una conversación. |
| POST | `/chat/conversaciones/{id}/mensajes` | Opcional | Envía `{ "texto": "..." }` o `{ "accion": { "tipo": "...", "payload": {...} } }`. Responde `202 {mensajeId}` de inmediato; la respuesta del asistente se transmite por WebSocket (ver abajo), salvo las acciones directas, que devuelven el bloque en la misma respuesta REST. |

\* Una conversación ligada a un cliente solo la puede listar o leer ese cliente. Las anónimas se listan o leen con la cookie `chat_sid`.

**WebSocket** — `wss://<host>/api/v1/chat/ws?conversacionId=<id>`, autenticado con el mismo `accessToken` (query param o subprotocolo). Se usa **únicamente para transmitir la respuesta del asistente**; el cliente nunca envía mensajes por este canal. Eventos emitidos:

| Evento | Payload | Cuándo |
|---|---|---|
| `token` | `{ texto: string }` | Cada fragmento de texto de la respuesta |
| `bloque` | `{ bloque: Bloque }` | Cuando un bloque estructurado (carrusel, carrito, formulario…) queda listo |
| `fin` | `{ mensajeId }` | Cierre del turno |
| `error` | `{ code }` | Si el turno falla (el frontend cae a modo degradado, SPEC-05 Req. 10) |

Si el WebSocket no conecta, el frontend hace *polling* de `GET /chat/conversaciones/{id}/mensajes?desde=<mensajeId>` (ver SPEC-05 Req. 4).

**Tipos de bloque de respuesta** (`Bloque.tipo`): `TEXTO`, `CARRUSEL_PRODUCTOS`, `DETALLE_PRODUCTO`, `SELECTOR_VARIANTE`, `CARRITO`, `ACCIONES_RAPIDAS`, `FORMULARIO` (`REGISTRO`, `LOGIN`, `OTP_MFA`, `OTP_CELULAR`, `DIRECCION`, `PAGO`, `RECLAMO`, `DEVOLUCION`), `RESUMEN_CHECKOUT`, `CONFIRMACION_PEDIDO`, `LISTA_PEDIDOS`, `ESTADO_PEDIDO`, `LISTA_PROMOCIONES`, `CONSTANCIA_RECLAMO`, `ESTADO_RECLAMO`, `CONSTANCIA_DEVOLUCION`, `ESTADO_DEVOLUCION`, `ERROR`.

### 2.2 Sesión e identidad (SPEC-01 a SPEC-04)
| Método | Ruta | Proxy hacia Seguridad |
|---|---|---|
| POST | `/sesion/registro` | `POST /auth/registro` |
| POST | `/sesion/verificar-correo` | `POST /auth/verificar-correo` |
| POST | `/sesion/verificar-correo/reenviar` | `POST /auth/verificar-correo/reenviar` |
| POST | `/sesion/login` | `POST /auth/login` |
| POST | `/sesion/mfa/solicitar` | `POST /auth/otp/solicitar` |
| POST | `/sesion/mfa/verificar` | `POST /auth/otp/verificar` |
| POST | `/sesion/refresh` | `POST /auth/refresh` |
| POST | `/sesion/logout` | `POST /auth/logout` |
| GET | `/sesion/perfil` | `GET /auth/me` |
| GET | `/sesion/politica-contrasena` | `GET /password/politica` |
| POST | `/contacto/celular/solicitar-otp` | ✅ propio del chatbot (SPEC-04), no depende de Seguridad — ver acuerdo A2 |
| POST | `/contacto/celular/verificar-otp` | ✅ ídem |

### 2.3 Catálogo (SPEC-06 a SPEC-10)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/catalogo/productos` | Búsqueda con los filtros `q`, `categoria`, `marca`, `precioMin`, `precioMax`, `talla`, `color`, `soloOfertas`, `orden`, `pagina` y `tamanio` (máx. 10). |
| GET | `/catalogo/productos/{productoId}` | Detalle con variantes, precio para el canal y disponibilidad por SKU. |
| GET | `/catalogo/promociones` | Promociones vigentes para el canal `CHATBOT`. |
| GET | `/catalogo/disponibilidad?sku=` | Disponibilidad puntual de un SKU. |

### 2.4 Carrito, envío y cupones (SPEC-11 a SPEC-13)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/carrito` | Carrito actual (anónimo o del cliente) con totales recalculados. |
| POST | `/carrito/items` | `{ sku, cantidad }`: valida el stock y agrega o suma la línea. |
| PATCH | `/carrito/items/{itemId}` | `{ cantidad }`: con cantidad 0 elimina la línea. |
| DELETE | `/carrito/items/{itemId}` | Elimina la línea. |
| DELETE | `/carrito` | Vacía el carrito (requiere confirmación en la UI). |
| POST | `/carrito/cupon` | `{ codigo }`: valida el cupón y lo aplica. |
| DELETE | `/carrito/cupon` | Quita el cupón. |
| GET | `/direcciones` | Direcciones guardadas del cliente, usadas solo para prellenar el checkout (proxy de Seguridad). |
| POST | `/envio/cotizar` | 🧩 `{ nombreCompleto, direccionExacta, distrito, referencia? }`: cotiza el envío con los campos libres del checkout (SPEC-12) y lo fija en el checkout. El guardado en Seguridad (`POST /usuarios/{id}/direcciones`) ocurre solo si el cliente marca "Guardar esta dirección", junto con la creación del pedido. |

### 2.5 Checkout, pago y pedidos (SPEC-14 a SPEC-18)
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/checkout` | Crea la sesión de checkout y el pedido `CREADO` en Ventas, y devuelve el resumen. Requiere `Idempotency-Key`. |
| GET | `/checkout/{checkoutId}` | Estado del checkout. |
| POST | `/checkout/{checkoutId}/pago` | Datos de tarjeta, que se procesan en el simulador y **no se persisten**. Requiere `Idempotency-Key`. |
| GET | `/pedidos` | Pedidos del cliente (proxy de Ventas, filtrado por `sub`). |
| GET | `/pedidos/{pedidoId}` | Detalle, estado e historial. |
| GET | `/pedidos/{pedidoId}/seguimiento` | Hitos del despacho (proxy de Despacho). |

### 2.6 Reclamos (SPEC-19, SPEC-20) ✅
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/reclamos` | Registra el reclamo en Ventas. Requiere `Idempotency-Key`. |
| GET | `/reclamos` | Proxy de `GET /api/v2/reclamos?clienteId=` — reclamos del cliente. |
| GET | `/reclamos/{codigoSeguimiento}` | Proxy de `GET /api/v2/reclamos/{codigoSeguimiento}` — estado y respuesta del reclamo. |

### 2.7 Devoluciones y reembolsos (SPEC-21, SPEC-22) ✅
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/evidencias` | Proxy directo de `POST /api/v2/devoluciones/evidencias/upload` de Ventas; devuelve la misma URL que Ventas genera, para incluirla en el `POST /devoluciones`. |
| POST | `/devoluciones` | Registra la solicitud de devolución o cambio en Ventas. Requiere `Idempotency-Key`. |
| GET | `/devoluciones` | Proxy de `GET /api/v2/devoluciones?clienteId=` — trae **todas** las solicitudes del cliente, incluidas las de otros canales, no solo las que registró el chatbot. |
| GET | `/devoluciones/{devolucionId}` | Estado del expediente y, si aplica, el bloque `resolucion.reembolso` con el estado del extorno. |

### 2.8 Códigos de error propios
| `code` | HTTP | Significado |
|---|---|---|
| `REQUIERE_SESION` | 401 | La acción necesita sesión de cliente. |
| `CELULAR_NO_VERIFICADO` | 403 | El checkout requiere el celular verificado. |
| `STOCK_INSUFICIENTE` | 409 | Incluye `disponible` por SKU. |
| `PRODUCTO_NO_DISPONIBLE` | 409 | Producto o SKU inactivo. |
| `LIMITE_CANTIDAD` | 422 | Más de 10 unidades por línea o más de 20 líneas. |
| `SIN_COBERTURA` | 422 | El destino no tiene cobertura de Despacho. |
| `EVIDENCIA_INVALIDA` | 400 | Archivo mayor a 5 MB o tipo no permitido. |
| `DEVOLUCION_NO_ELEGIBLE` | 422 | El pedido no está `ENTREGADO`, está fuera de plazo, o falta evidencia obligatoria. |
| `CUPON_INVALIDO` | 422 | Incluye `motivo`. |
| `CARRITO_DESACTUALIZADO` | 409 | Cambió el precio, el stock o el cupón desde el resumen. |
| `PAGO_RECHAZADO` | 402 | Incluye `motivo` e `intentosRestantes`. |
| `CHECKOUT_EXPIRADO` | 410 | Pasaron más de 15 minutos. |
| `RECURSO_NO_ENCONTRADO` | 404 | También se usa cuando el recurso existe pero no pertenece al cliente. |
| `SERVICIO_NO_DISPONIBLE` | 503 | Falló un módulo externo; incluye `modulo`. |
| `DEMASIADAS_SOLICITUDES` | 429 | Se superó el rate limit. |
| `VALIDACION` | 400 | Incluye `errores[{campo, mensaje}]`. |
| `DATO_INVALIDO` | 400 | Específico del documento de identidad (`tipoDocumento`/`numeroDocumento`); el frontend lo evita validando antes con las reglas de `SPEC-12` · Requisito 1, pero Ventas también lo aplica del lado suyo. |

---

## 3. Endpoints consumidos

### 3.1 Seguridad y Usuarios — base `{SEG}/api/v1` (mock: Prism en `:4010`, sin prefijo)
| Endpoint | Uso | Spec | Estado |
|---|---|---|---|
| `GET /auth/.well-known/jwks.json` | Validar tokens en local | Todas | ✅ |
| `POST /auth/token` (client_credentials) | Token de servicio `modulo-chatbot` | 18 | ✅ |
| `POST /auth/registro` | Autorregistro, con `canalOrigen: "CHATBOT"` (acuerdo A1) | 01 | ✅ |
| `GET /password/politica` | Reglas de la contraseña para la validación en cliente | 01 | ✅ |
| `POST /auth/verificar-correo` · `/reenviar` | Verificación de correo | 02 | ✅ |
| `POST /auth/login` | Login (puede devolver `mfaRequerido`) | 03 | ✅ |
| `POST /auth/otp/solicitar` · `/verificar` | MFA en el login | 03 | ✅ |
| `POST /auth/refresh` · `/logout` · `GET /auth/me` | Gestión de sesión y perfil | 03 | ✅ |
| `GET/POST /usuarios/{id}/direcciones` | Direcciones de entrega (con token del titular) | 12 | ✅ |
| `POST /auth/introspeccion` | Antes del pago (opera con dinero) | 14 | ✅ acuerdo A3, scope `tokens:introspeccion` concedido |

🔴 Validación de celular por OTP para un canal autorizado (lo que usaba SPEC-04): **decidido fuera de alcance del ciclo** por Seguridad (acuerdo A2). SPEC-04 se rediseñó como una verificación propia del chatbot, sin llamar a Seguridad para esto.

Errores de Seguridad: RFC 7807 con `code`. Lista completa: `TOKEN_INVALIDO`, `SCOPE_INSUFICIENTE`, `CREDENCIALES_INVALIDAS`, `VALIDACION`, `POLITICA_INCUMPLIDA`, `CORREO_NO_DISPONIBLE`, `CODIGO_INVALIDO`, `OTP_INTENTOS_AGOTADOS`, `ENLACE_EXPIRADO`, `ENLACE_YA_USADO`, `REFRESCO_INVALIDO`, `DEMASIADAS_SOLICITUDES`, `NO_DISPONIBLE`.

🧩 **Aviso directo de Seguridad (corrige lo asumido antes):** `POST /auth/login` **nunca** responde `CUENTA_NO_DISPONIBLE`. Una cuenta bloqueada, inactiva o sin verificar responde exactamente igual que una contraseña incorrecta: `401 CREDENCIALES_INVALIDAS`, a propósito, para no revelar el estado de la cuenta. El chatbot no puede distinguir la causa en el login (ver SPEC-03 Requisito 1); por eso SPEC-02 ofrece el reenvío de verificación en *todo* login fallido, no solo cuando "corresponde". `CUENTA_NO_DISPONIBLE` puede seguir existiendo como código en otros endpoints de Seguridad, pero no en el login.

### 3.2 Productos y Ofertas — base `{PRO}/api/v1` 🟡 (las specs definen las capacidades; las rutas son una propuesta)
| Endpoint propuesto | Uso | Spec origen en Productos |
|---|---|---|
| `GET /productos?estado=ACTIVO&q=&categoriaId=&marcaId=&precioMin=&precioMax=&canal=CHATBOT&pagina=&tamanio=` | Búsqueda de catálogo (solo productos activos) | SPEC-003 Req. 3 |
| `GET /productos/{id}` (incluye variantes activas, atributos talla/color, imagen y SKU) | Detalle | SPEC-003, SPEC-004 |
| `GET /categorias` · `GET /marcas` | Normalizar los filtros del LLM | SPEC-008, SPEC-011 |
| `GET /precios?skus=&canal=CHATBOT` → `precioRegular`, `precioOferta`, `moneda`, `vigencia` | Precio para el canal | SPEC-013 |
| `GET /inventario/disponibilidad?skus=` → `available` por SKU (agregado) | Validación de stock | SPEC-015 |
| `GET /promociones?canal=CHATBOT&vigentes=true` | Ofertas vigentes | SPEC-006 Req. 8 |
| `POST /promociones/evaluar` `{canal, lineas[{sku,cantidad}], cupon?}` → promoción seleccionada, importe original, descuento e importe resultante | Totales del carrito | SPEC-006 Req. 9 |
| `POST /cupones/validar` `{codigo, canal, customerRef, lineas[]}` → `valido`, `motivo`, `descuento` e `importeResultante` (**sin consumir**) | Cupones | SPEC-005 Req. 5 |
| `GET /recomendaciones/candidatos?productoId=&canal=CHATBOT` | Venta cruzada y complementos | SPEC-007 |
| Peso (kg) y volumen (m³) por SKU | Cotizar el envío | ⚠️ **no está definido en ninguna spec de Productos** |

### 3.3 Ventas y Postventa — bases `{VEN}/api/v1` (M1 · F1, F2) y `{VEN}/api/v2` (M2 · F3, F4, F5, F6) ✅ contrato publicado (v1.3.0)
🧩 `api-contract.md` de Ventas pasó de 547 a 743 líneas el 23/09: agregó la subida de evidencia y los listados/consultas que faltaban de F3 y F6. M1 (pedidos) vive en `/api/v1`; M2 (postventa) vive en `/api/v2`.

| Endpoint | Uso | Referencia |
|---|---|---|
| `POST /api/v1/pedidos` (con `Idempotency-Key`) | Crear el pedido `CREADO` con el snapshot completo (`contacto`, `items`, `cupon`, `envio`, `pago`) | F1 §1.1 |
| `POST /api/v1/pedidos/{id}/pagos/notificacion` | Notificar el resultado del pago simulado (`APROBADO`/`RECHAZADO`); transiciona `CREADO → PAGADO` | F1 §1.2 |
| `GET /api/v1/pedidos/{id}` | Detalle, estado e historial | F1 §1.3 |
| `GET /api/v1/pedidos?clienteId=&estado=&desde=&hasta=&pagina=&tamano=` | Listado paginado del cliente (`{clienteId, contenido[], pagina, totalPaginas, totalElementos}`) | F1 §1.4 |
| `POST /api/v1/pedidos/{id}/anulaciones` `{motivo: PAGO_NO_COMPLETADO, comentario}` | Anular un pedido `CREADO` o `PAGADO` sin intervención del Gestor; responde `200` directo (no `202`, porque ese motivo no pasa por autorización) | F2 §1.7 |
| `POST /api/v2/reclamos` | Registrar un reclamo del Libro de Reclamaciones, con plazo confirmado de **15 días hábiles** | F6 §2.6 |
| `GET /api/v2/reclamos/{codigoSeguimiento}` | ✅ **Nuevo.** Detalle y `respuestaVisibleCliente` de un reclamo | F6 §2.7 |
| `GET /api/v2/reclamos?documento=&clienteId=&estado=&pagina=&tamano=` | ✅ **Nuevo.** Listado paginado por cliente o por documento; estados reales `REGISTRADO \| EN_PROCESO \| ATENDIDO \| DERIVADO` | F6 §2.8 |
| `PATCH /api/v2/reclamos/{id}/respuesta` | Solo lo usa el Gestor; el chatbot únicamente lee el resultado a través del detalle | F6 §2.9 |
| `POST /api/v2/devoluciones/evidencias/upload` | ✅ **Nuevo.** Sube la foto o PDF de evidencia (multipart, ≤ 5 MB) y devuelve `{tipo, url, nombreArchivoOriginal, tamanioBytes, fechaSubida}` — Ventas hostea el archivo, el chatbot no necesita bucket propio | F3 §2.1 |
| `POST /api/v2/devoluciones` | Registrar la solicitud de cambio o devolución. Plazo confirmado: **7 días naturales** desde la entrega | F3 §2.2 |
| `GET /api/v2/devoluciones/{id}` | Detalle del expediente; si la resolución fue `DEVOLUCION_DINERO` y ya se procesó, incluye `resolucion.reembolso{reembolsoId, estado, monto, moneda, transaccionPasarelaId, fechaEjecucion}` | F3 §2.3 |
| `GET /api/v2/devoluciones?clienteId=&estado=&tipo=&pagina=&tamano=` | ✅ **Nuevo.** Listado paginado, con `estadoReembolso` resumido por fila | F3 §2.4 |
| `POST /api/v2/reembolsos` | Solo lo ejecuta Ventas (F4) a partir de un origen válido; el chatbot nunca lo llama | F4 §2.4 (referencia) |

Notas que siguen vigentes sobre este contrato:
- Los estados de pedido usan guion bajo y sin tildes: `EN_PREPARACION`, no "EN PREPARACIÓN".
- El formato de error de Ventas usa la clave `codigo` (no `code`); `VentasClient` lo normaliza al `code` interno del chatbot.
- Las reglas de `contacto.tipoDocumento`/`numeroDocumento` (DNI, RUC, CE, PASAPORTE) ya están en su propio contrato, idénticas a las de `SPEC-12` · Requisito 1.

Códigos esperados: `400` datos incompletos o inconsistentes, `403` el cliente no es dueño del pedido, `404` inexistente, `409` sin stock, transición inválida o pedido en un estado que no admite la operación.

### 3.4 Despacho y Entrega — base `{DES}/api/v1`
| Endpoint | Uso | Estado |
|---|---|---|
| `POST /zonas/cotizar` `{distrito, codigoPostal?, pesoKg, volumenM3?}` → `coberturaDisponible`, `idZona`, `nombreZona`, `costoEnvio`, `moneda`, `plazoEstimadoDias` | Cotización (pública, con rate limit) | ✅ api-contract §2.1 |
| Seguimiento por `idPedido` con token de servicio → `estadoEtiqueta`, `fechaProgramada`, `distrito` e `hitos[]` | Seguimiento del pedido | 🟡 el overview (RT-04) exige token de servicio y la consulta por pedido; el api-contract lo publica como `GET /tracking/{codigoRastreo}` **público y con coordenadas**. Asumimos lo del overview. Ruta propuesta: `GET /seguimiento?idPedido=` |

---

## 4. Mapeo de estados del pedido para el cliente

El estado del pedido lo decide **Ventas**. Cuando el pedido está `DESPACHADO`, el detalle de tránsito lo aporta **Despacho**.

🧩 Los valores reales del enum de Ventas usan guion bajo y sin tildes (`EN_PREPARACION`, no "EN PREPARACIÓN"), confirmado en `api-contract.md` §1.4.

| Ventas (F1) | Despacho | Etiqueta en el chat |
|---|---|---|
| `CREADO` | — | Pendiente de pago |
| `PAGADO` | — | Pago confirmado |
| `EN_PREPARACION` | — | En preparación |
| `DESPACHADO` | `PENDIENTE_ASIGNACION` | En centro de despacho |
| `DESPACHADO` | `ASIGNADO` | Asignado a repartidor |
| `DESPACHADO` | `EN_CAMINO` | En camino |
| `DESPACHADO` | `FALLIDO` | No entregado, regresando al centro |
| `DESPACHADO` | `PENDIENTE_ASIGNACION` (reprogramado) | Entrega reprogramada para {fecha} |
| `DESPACHADO` | `DEVUELTO_A_ORIGEN` | Devuelto al centro de despacho (te contactaremos) |
| `ENTREGADO` | `ENTREGADO` | Entregado el {fecha} |
| `ANULADO` | `CANCELADO` o — | Anulado |

Nunca se muestra el motivo del fallo, el comentario del repartidor, sus datos ni coordenadas (RT-CA-08 y RT-CA-10 de Despacho).

---

## 5. Eventos

El chatbot **no consume eventos** en esta versión: los estados se consultan bajo demanda. Tampoco publica eventos a otros módulos; su integración es síncrona por API, con reintentos mediante outbox propio para la notificación de pago y los correos.

Mejoras posibles: suscribirse a `pedido entregado` de Ventas y a `usuario.desactivado` de Seguridad (RabbitMQ, exchange `seguridad.usuarios`, desde la semana 12).

---

## 6. Acuerdos pendientes (llevar a la sincronización de líderes)

🧩 Revisado contra `kit-integracion.md` de Seguridad y `api-contract.md` de Ventas (22/09/2026). Se agrega una columna de estado; los resueltos se dejan igual en la tabla, para que quede el historial de qué se acordó y cuándo.

| # | Estado | Módulo | Acuerdo | Impacta |
|---|---|---|---|---|
| A1 | ✅ Resuelto (23/09) | Seguridad | El enlace de verificación va a la pantalla del canal que originó el registro. **Aceptado con su forma, no la nuestra**: no se envía una URL en la petición (sería una redirección abierta); se envía `canalOrigen: "CHATBOT"` en `POST /auth/registro` (lista cerrada) y Seguridad resuelve la URL de su lado. Acción pendiente, no de diseño: avisarles por issue cuál es nuestra URL exacta de `/verificar-correo`. | SPEC-01, SPEC-02 |
| A2 | ✅ Decidido — fuera de alcance del ciclo (23/09) | Seguridad | La validación de celular por un canal autorizado **no se va a construir este semestre**. Justificación de Seguridad: el SMS es simulado y el correo ya queda verificado por el registro. Se reevalúa en Hito 4 solo si abrimos un issue con un caso concreto. **Consecuencia de diseño:** SPEC-04 se reescribió como una verificación local y autocontenida del chatbot, sin depender de Seguridad. | SPEC-04 |
| A3 | ✅ Concedido (23/09) | Seguridad | Scope `tokens:introspeccion` para `modulo-chatbot`, publicado en su kit §5. Credenciales reales recién en Hito 4; hasta entonces se prueba contra el mock. SPEC-14 ya lo usa como paso obligatorio antes de cada pago, siguiendo la propia regla de Seguridad ("si mueve dinero, introspeccionen"). | SPEC-14 |
| A4 | 🟡 Abierto | Seguridad / Despacho | Emisión del rol `SERVICIO_INTEGRACION` al token de servicio del chatbot para consultar el seguimiento. | SPEC-18 |
| A5 | 🟡 Abierto | Productos | Rutas y payloads concretos de catálogo, variantes, precios por canal, disponibilidad, promociones, evaluación, cupones y candidatos. | SPEC-06 a SPEC-13 |
| A6 | 🟡 Abierto — replanteado | Productos / Despacho | No es solo "falta el dato del peso": hay que decidir **quién agrega el peso y volumen del carrito**. Opción 1 (preferida): Despacho recibe líneas (`sku` + `cantidad`) en `/zonas/cotizar` y le pregunta el peso a Productos él mismo, sacando el cálculo de cada canal. Opción 2: Productos expone un endpoint de "peso total" que cada canal consulta antes de cotizar. Mientras no se decida, SPEC-12 sigue usando `pesos_por_categoria.yaml` como parche local. | SPEC-12 |
| A7 | 🟡 Abierto | Productos | Búsqueda por texto libre (`q`) sobre nombre, descripción y características. | SPEC-06, SPEC-07 |
| A8 | ✅ Resuelto | Ventas | `api-contract.md` publicado: creación de pedido, notificación de pago (`POST /pagos/notificacion`) y listado por cliente. | SPEC-15, SPEC-17 |
| A9 | ✅ Resuelto | Ventas | Anulación de un pedido `CREADO`/`PAGADO` por `PAGO_NO_COMPLETADO` iniciada por el canal: `POST /pedidos/{id}/anulaciones`, responde `200` directo. | SPEC-15 |
| A10 | ✅ Resuelto (23/09) | Ventas | Publicaron los cuatro endpoints que faltaban: `GET /api/v2/reclamos/{codigoSeguimiento}` (detalle), `GET /api/v2/reclamos?documento=&clienteId=&estado=` (listado), `GET /api/v2/devoluciones?clienteId=&estado=&tipo=` (listado) y, dentro de `GET /api/v2/devoluciones/{id}`, un bloque anidado `resolucion.reembolso` con el estado del extorno. SPEC-19, SPEC-20, SPEC-21 y SPEC-22 ya no tienen ningún requisito bloqueado. | SPEC-19, SPEC-20, SPEC-21, SPEC-22 |
| A11 | 🟡 Abierto | Despacho | Unificar el seguimiento: por `idPedido`, con token de servicio y sin coordenadas. | SPEC-18 |
| A12 | 🟡 Abierto | Despacho | Autenticación de la cotización para canales: pública o con API key. | SPEC-12 |
| A13 | ✅ Resuelto (23/09) | Ventas | Ventas hostea la evidencia ellos mismos: `POST /api/v2/devoluciones/evidencias/upload` (multipart, ≤ 5 MB, `image/jpeg`, `image/png`, `image/webp` o `application/pdf`) devuelve la URL que luego se manda en el `POST /devoluciones`. El chatbot **no necesita su propio bucket ni adaptador de almacenamiento** — solo un proxy del formulario hacia ese endpoint. | SPEC-21 |
| A14 | ✅ Resuelto (23/09) | Ventas | `contacto.tipoDocumento` y `contacto.numeroDocumento` son **siempre obligatorios** en la creación del pedido — no opcionales, se usan para emitir el comprobante y validar la entrega. Ventas confirmó por escrito las 4 expresiones regulares exactas (DNI, RUC con prefijo, CE, y **PASAPORTE**, que no estaba contemplado antes) y el código de error `400 DATO_INVALIDO` cuando no calzan. SPEC-12 · Requisito 1 ya tiene las reglas exactas. Aviso no urgente para otros canales: si Ventas exige el documento a todos, Marketplace y Retail probablemente necesiten las mismas reglas. | SPEC-12, SPEC-14, SPEC-15 |
