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
| Backend del chatbot → validación del token del cliente | Validación **local** con el JWKS de Seguridad (`/auth/.well-known/jwks.json`), cacheado. El emisor esperado (`iss`) sale de la configuración por entorno (`SECURITY_EXPECTED_ISSUER`), tomado del documento de descubrimiento de Seguridad (`/api/v1/auth/.well-known/openid-configuration`; valor en producción `https://g7-auth-service.onrender.com/api/v1/auth`) y nunca del propio token. Se verifica además `tipo=acceso` y que el claim `roles` contenga `CLIENTE`. |
| Backend del chatbot → otros módulos (a nombre del sistema) | Token de servicio `client_credentials` con `client_id=modulo-chatbot` (`POST /auth/token`), cacheado hasta 60 s antes de su `exp`. |
| Backend del chatbot → Ventas (a nombre del cliente) | Se reenvía el token del cliente (`Authorization: Bearer`, rol `CLIENTE` en el claim `roles`; no es un scope) en `GET /api/v1/pedidos/me`, `GET /api/v2/devoluciones/me`, `GET /api/v2/reclamos/me` y `POST /api/v2/csat`. Ventas filtra por el `sub` del JWT y no acepta `clienteId` en esos endpoints. Es la única excepción a «el canal usa su propio token» (confirmado por Ventas, G3-Chatbot-specs #9, 12/10). |
| Backend del chatbot → Seguridad (a nombre del cliente) | Se reenvía el token del cliente cuando el recurso es del titular (por ejemplo, `/usuarios/{id}/direcciones`). |
| Backend del chatbot → Supabase Storage (imágenes del chat, SPEC-23) | Credencial de servicio de Supabase en variables de entorno del backend, nunca en el frontend; bucket **privado**. El frontend solo recibe URLs firmadas de corta vida emitidas por el backend. **Estado (2026-11-27):** el adaptador `SupabaseAttachmentStorage` y el selector `ATTACHMENT_STORAGE=local\|supabase` están en `development` (backend #144); producción aún conserva `local` hasta configurar el bucket y las variables. El checklist de cierre está en el [runbook §13](operacion/adjuntos-supabase.md#13-estado-de-cierre-2026-11-27). El disco local no es aceptable en producción (sistema de archivos efímero de Railway). |
| Refresh token | Nunca llega al JavaScript. El BFF lo guarda en una cookie `httpOnly; Secure; SameSite=Strict; Path=/api/v1/sesion`. |

**Cookies del canal** (alineado el 2026-11-21 con `BE/src/modules/mod_auth/adapters/http/session_router.py:224,272` y `mod_chat/adapters/http/chatbot_router.py:88`):

| Cookie | Uso | Atributos | Vigencia |
|---|---|---|---|
| `chat_rt` | Refresh token de la sesión (SPEC-03) | `httpOnly; Secure; SameSite=Strict; Path=/api/v1/sesion` | 7 días (`REFRESH_MAX_AGE_SECONDS`) |
| `chat_chg` | Desafío MFA pendiente (`challengeToken`, SPEC-03 Req. 2) | `httpOnly; Secure; SameSite=Strict; Path=/api/v1/sesion` | 5 minutos |
| `chat_sid` | Identifica al visitante anónimo y sus conversaciones | `httpOnly; Secure; SameSite=Lax` (sin `Path` restringido) | 7 días |

`Secure` se aplica según la configuración del entorno (`Secure` desactivado solo en desarrollo local por HTTP).

`POST /sesion/refresh` y `POST /sesion/logout` exigen además la cabecera `X-Requested-With` y verifican el `Origin` (protección CSRF, ADR-0008).

---

## 2. API expuesta por el backend del chatbot (para su frontend)

Prefijo: `/api/v1`. Todas las respuestas de error usan `application/problem+json`.

### 2.1 Conversaciones (SPEC-05)
🧩 Ampliado para soportar conversaciones múltiples (barra lateral) y streaming de la respuesta por SSE en el `POST` de mensajes (ADR-0021), según la arquitectura del equipo.

| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| POST | `/chat/conversaciones` | Opcional | Crea una conversación vacía y devuelve `conversacionId`. |
| GET | `/chat/conversaciones` | Opcional* | Lista las conversaciones (propias o de la sesión anónima), ordenadas por `last_message_at` descendente, con `titulo` y vista previa del último mensaje. Paginado. |
| GET | `/chat/conversaciones/buscar?q=` | Opcional* | Busca por texto en el título y los mensajes del cliente y del asistente. Devuelve la misma forma y paginación que el listado y agrega en cada fila `resaltado: {titulo, fragmento}`: `titulo` es el título completo y `fragmento` un extracto del mensaje coincidente más reciente (`null` si solo coincidió el título). Ambos son listas de tramos `{texto, coincide}`, donde `coincide: true` marca las palabras encontradas. Los tramos son texto plano: el cliente los muestra como texto y nunca los interpreta como HTML. `q` vacío o de más de 100 caracteres responde `400 VALIDACION`. |
| GET | `/chat/conversaciones/{id}/mensajes` | Opcional* | Devuelve el historial paginado de una conversación. Cada mensaje con imágenes incluye `adjuntos[{adjuntoId, mimeType, ancho, alto, urlMiniatura, expiraEn}]` con URLs firmadas de corta vida (SPEC-23). |
| POST | `/chat/conversaciones/{id}/mensajes` | Opcional | Envía `{ "texto": "...", "adjuntoIds": ["..."] }` (`adjuntoIds` opcional, máx. 3; el texto es opcional si hay al menos un adjunto, ver 2.1.1) o `{ "accion": { "tipo": "...", "payload": {...} } }`. Los errores de validación (`400`) y de pertenencia (`404`: la conversación no existe o no es del solicitante) se responden antes del stream como `application/problem+json`. En un envío de texto responde `200` con `Content-Type: text/event-stream` y la respuesta del asistente se transmite en esa misma respuesta (ver abajo); las acciones directas siguen devolviendo el bloque en la respuesta REST. Las acciones directas y `adjuntoIds` están implementados (SPEC-23; backend #141 / frontend #109). |

\* Una conversación ligada a un cliente solo la puede listar o leer ese cliente. Las anónimas se listan o leen con la cookie `chat_sid`.

🧩 Tipos directos propuestos para las acciones rápidas fijas (sin LLM, registrados en el historial): `VER_OFERTAS` → `consultar_promociones`; `RASTREAR_PEDIDO` → identificación y consulta de pedido/seguimiento; `AYUDA_DEVOLUCION` → `preparar_devolucion`. Las dos últimas requieren sesión y conservan la acción pendiente para retomar después del login.

🧩 **Acciones de cliente (2026-11-25, M5).** `IR_A_CHECKOUT`, `CERRAR_SESION`, `NUEVO_CHAT` y `BUSCAR_CHATS` viajan en un bloque `ACCIONES_RAPIDAS` y las ejecuta el frontend; no se envían al BFF como `accion` (si llegan, responden `ACCION_DESCONOCIDA`). `IR_A_CHECKOUT` navega a `/checkout` sin crear el checkout; `CERRAR_SESION` llama a `POST /api/v1/sesion/logout` (el BFF borra las cookies) y limpia el token local; `NUEVO_CHAT` crea la conversación con `POST /conversaciones`; `BUSCAR_CHATS` abre `/buscar` con `payload.q`. Ver SPEC-05 · Req. «Acciones de cliente del chat».

**Streaming SSE** — en el `POST /chat/conversaciones/{id}/mensajes`, la respuesta `200 text/event-stream` lleva la respuesta del asistente. Se autentica como el resto de la API REST (mismo `accessToken` y cookies; sin token en query string). No hay endpoint WebSocket y el cliente nunca abre una conexión persistente para el chat. `EventSource` no admite `POST`, por lo que el frontend usa un lector de `fetch` con streaming. Eventos emitidos, en orden:

| Evento | Payload | Cuándo |
|---|---|---|
| `aceptado` | `{ mensajeId }` | El mensaje del cliente quedó persistido |
| `token` | `{ texto: string }` | Cada fragmento de texto de la respuesta |
| `bloque` | `{ bloque: Bloque }` | Cuando un bloque estructurado (carrusel, carrito, formulario…) queda listo |
| `degradado` | `{ motivo }` | El turno terminó en modo degradado (SPEC-05 Req. 10); el cliente descarta los tokens recibidos antes de este evento y el texto de respaldo llega después como un `token`, seguido de `bloque` `ACCIONES_RAPIDAS` y `fin` |
| `fin` | `{ mensajeId }` | Cierre del turno, con el id del mensaje del asistente ya persistido |
| `error` | `{ code }` | Falla inesperada a mitad del stream; el stream termina |

Si el stream termina sin evento `fin` ni `error` (por ejemplo, se cae la conexión), el frontend no hace *polling*: reconsulta una sola vez `GET /chat/conversaciones/{id}/mensajes` (arreglo simple de los últimos 50 mensajes, sin `desde`). Si ese historial ya contiene un mensaje del asistente posterior al último del cliente, reemplaza los mensajes locales por él; si no, o si la consulta falla, muestra el turno como incompleto con la acción "Reintentar", que reenvía el texto como un mensaje nuevo del cliente (ver SPEC-05 Req. 4). Los *proxies* no deben almacenar en búfer la respuesta.

**Tipos de bloque de respuesta** (`Bloque.tipo`): `TEXTO`, `CARRUSEL_PRODUCTOS`, `DETALLE_PRODUCTO`, `SELECTOR_VARIANTE`, `CARRITO`, `ACCIONES_RAPIDAS`, `FORMULARIO` (`REGISTRO`, `LOGIN`, `REENVIO_VERIFICACION`, `OTP_MFA`, `OTP_CELULAR`, `DIRECCION`, `PAGO`, `RECLAMO`, `DEVOLUCION`), `RESUMEN_CHECKOUT`, `CONFIRMACION_PEDIDO`, `LISTA_PEDIDOS`, `ESTADO_PEDIDO`, `LISTA_PROMOCIONES`, `LISTA_RECLAMOS`, `CONSTANCIA_RECLAMO`, `ESTADO_RECLAMO`, `LISTA_DEVOLUCIONES`, `CONSTANCIA_DEVOLUCION`, `ESTADO_DEVOLUCION`, `ERROR`.

### 2.1.1 Adjuntos de imágenes (SPEC-23)
🧩 Nuevo. Las imágenes se suben antes de enviar el mensaje y se guardan en un almacenamiento privado propio del chatbot (destino de producción: bucket privado de Supabase; pendiente, ver §1 y ADR-0028) (no son la evidencia de devolución de 2.7, que se sube a Ventas). Sesión opcional: la pertenencia se controla por `customer_id` o por la cookie `chat_sid` de la conversación.

| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| POST | `/chat/conversaciones/{id}/adjuntos` | Opcional | Sube una imagen (`multipart/form-data`, campo `archivo`; `image/jpeg`, `image/png` o `image/webp`, máx. 5 MB). El backend valida el contenido real, elimina EXIF y ubicación, normaliza y guarda la imagen con su miniatura. Responde `201 {adjuntoId, mimeType, tamanioBytes, ancho, alto}`. Errores: `400 ADJUNTO_INVALIDO`, `404 RECURSO_NO_ENCONTRADO`, `422 LIMITE_ADJUNTOS`, `429 DEMASIADAS_SOLICITUDES`, `503 SERVICIO_NO_DISPONIBLE`. |
| DELETE | `/chat/conversaciones/{id}/adjuntos/{adjuntoId}` | Opcional | Quita un adjunto `PENDING` y elimina sus archivos. Un adjunto `SENT` no se puede quitar (`409`). |
| GET | `/chat/adjuntos/archivo?clave=&exp=&sig=` | Ninguna (la firma es la autorización) | Sirve el archivo de una URL firmada emitida por el backend. `clave` (1 a 300 caracteres), `exp` (segundos Unix) y `sig` (HMAC-SHA256 hexadecimal de 64 caracteres sobre `clave:exp` con `ATTACHMENT_SIGNING_SECRET`). `403 FIRMA_INVALIDA` si la firma no coincide o `exp` pasó; `404 RECURSO_NO_ENCONTRADO` si no existe; claves con caracteres fuera de `[A-Za-z0-9/_.-]` o con `..` se rechazan. Responde con `Cache-Control: private, max-age=60`. Aplica a ambos adaptadores: el backend firma la URL y sirve el objeto; el bucket de Supabase permanece privado y no se expone. |
| GET | `/chat/adjuntos/{adjuntoId}` | Opcional | Emite una URL firmada nueva `{urlMiniatura, urlImagen, expiraEn}` para un adjunto de una conversación del solicitante; `404 RECURSO_NO_ENCONTRADO` si pertenece a otro cliente. |

Límites provisionales: máx. 3 adjuntos por mensaje, 10 cargas por minuto por cliente o IP, 10 adjuntos pendientes por conversación (los no enviados se eliminan a las 24 h) y URLs firmadas de 5 minutos. Al LLM las imágenes viajan en base64 leídas por el backend, nunca como URL. Las imágenes del chat no se reenvían a Ventas.

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
| GET | `/sesion/perfil` | `GET /auth/me`; agrega `celularVerificado` desde la verificación local y `ultimoDocumento` opcional `{ tipo, numeroEnmascarado }`, tomado de `tipoDocumento` y `documentoEnmascarado` de `/auth/me` o, si Seguridad no los envía, del checkout más reciente del canal (null si no hay documento) |
| GET | `/sesion/politica-contrasena` | `GET /password/politica` |
| POST | `/contacto/celular/solicitar-otp` | ✅ Implementado (D1, 2026-11-21; backend #141 · `b75fbea6`, frontend #109 · `7432d463`): propio del chatbot (SPEC-04), no depende de Seguridad — ver acuerdo A2. Sin cuerpo; lee el celular vigente de `/auth/me` y responde `202 {enviado: true, celularEnmascarado, expiraEn}` (con `codigo` solo si `MODO_QA=true`). |
| POST | `/contacto/celular/verificar-otp` | ✅ Implementado (D1, 2026-11-21; backend #141 · `b75fbea6`, frontend #109 · `7432d463`): cuerpo `{codigo}`; responde `200 {celularVerificado: true, celularEnmascarado}`. Errores `400 VALIDACION`, `401 CODIGO_INVALIDO` (con `intentosRestantes`), `401 OTP_INTENTOS_AGOTADOS`, `410 CODIGO_VENCIDO`, `429 LIMITE_REENVIOS` (con `reintentarEn` y `Retry-After`), `409 CELULAR_NO_DISPONIBLE`, `503 SERVICIO_NO_DISPONIBLE`. |

### 2.3 Catálogo (SPEC-06 a SPEC-10)
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/catalogo/productos` | Búsqueda con los filtros `q`, `categoria`, `marca`, `precioMin`, `precioMax`, `talla`, `color`, `soloOfertas`, `orden`, `pagina` y `tamanio` (máx. 10). `orden` ∈ `relevancia \| precio_asc \| precio_desc \| nombre_asc \| nombre_desc`; `relevancia` por defecto y `400 VALIDACION` para cualquier otro valor. |
| GET | `/catalogo/productos/{productoId}` | Detalle con variantes, precio para el canal y disponibilidad por SKU. |
| GET | `/catalogo/promociones` | Promociones vigentes para el canal `CHATBOT`. |
| GET | `/catalogo/disponibilidad?sku=` | Disponibilidad puntual de un SKU. |

### 2.4 Carrito, envío y cupones (SPEC-11 a SPEC-13)
| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| GET | `/carrito` | Opcional | Carrito actual (anónimo o del cliente) con totales recalculados. |
| POST | `/carrito/items` | Opcional | `{ sku, cantidad }`: valida el stock y agrega o suma la línea. |
| PATCH | `/carrito/items/{itemId}` | Opcional | `{ cantidad }`: con cantidad 0 elimina la línea. |
| DELETE | `/carrito/items/{itemId}` | Opcional | Elimina la línea. |
| DELETE | `/carrito` | Opcional | Vacía el carrito (`{ confirmado: true }`; requiere confirmación en la UI). |
| POST | `/carrito/cupon` | Obligatoria (`CLIENTE`) | `{ codigo }`: normaliza (`trim` + mayúsculas), valida contra Productos sin consumir y aplica al carrito. |
| DELETE | `/carrito/cupon` | Obligatoria (`CLIENTE`) | Quita el cupón activo del carrito y recalcula los totales. |
| GET | `/direcciones` | Obligatoria (`CLIENTE`) | Direcciones guardadas del cliente, usadas solo para prellenar el checkout (proxy de Seguridad con token del titular). |
| POST | `/envio/cotizar` | Obligatoria (`CLIENTE`) | 🧩 `{ nombreCompleto?, destinatario?, direccionExacta?, direccion?, distrito, departamento?, provincia?, referencia? }`: cotiza el envío con los campos libres del checkout (SPEC-12) contra Despacho. El guardado en Seguridad (`POST /usuarios/{id}/direcciones`) ocurre solo si el cliente marca "Guardar esta dirección", junto con la creación del pedido. |

#### 2.4.1 Contratos detallados de Cupones (SPEC-13)
- **`POST /api/v1/carrito/cupon`** (requiere sesión `CLIENTE`; parámetro opcional de consulta `?conversacionId=<uuid>`):
  - **Cuerpo de entrada:** `{ "codigo": "RUN10", "confirmarReemplazo": false }` (`codigo` de 1 a 40 caracteres, se normaliza con `strip().upper()`).
  - **Respuesta `200 OK`:** `{ "mensaje": "...", "cupon": { "codigo": "RUN10", "descuento": 30.00, "moneda": "PEN", "promocionId": "PROMO-10" }, "carrito": { "lineas": [...], "subtotal": 300.00, "descuentos": [{ "nombre": "Cupón RUN10", "monto": 30.00 }], "costoEnvio": null, "total": 270.00, "avisos": [] } }`.
  - **Errores (`application/problem+json`):**
    - `400 VALIDACION`: código vacío o formato inválido.
    - `401 REQUIERE_SESION`: visitante sin sesión (`customerRef` obligatorio para validar límites por cliente).
    - `409 REQUIERE_CONFIRMACION_REEMPLAZO`: ya existe un cupón activo distinto y `confirmarReemplazo` es `false`; incluye `cuponActual` y `cuponNuevo`.
    - `422 CUPON_INVALIDO`: cupón rechazado por Productos; incluye `motivo` (`INEXISTENTE`, `EXPIRADO`, `NO_VIGENTE`, `AGOTADO`, `LIMITE_CLIENTE`, `MONTO_MINIMO`, `NO_APLICA_PRODUCTOS`, `NO_APLICA_CANAL`, `NO_COMBINABLE`) y opcionalmente `montoMinimo` / `montoFaltante`.
    - `429 DEMASIADAS_SOLICITUDES`: más de 5 intentos fallidos en 10 minutos para el mismo cliente (SPEC-13 Req. 5).
    - `503 MODULO_NO_DISPONIBLE`: Productos no disponible (`modulo: "products"`).
- **`DELETE /api/v1/carrito/cupon`** (requiere sesión `CLIENTE`):
  - **Respuesta `200 OK`:** `{ "mensaje": "...", "carrito": { ... } }` con el carrito recalculado sin cupón.
  - **Errores:** `401 REQUIERE_SESION`, `503 MODULO_NO_DISPONIBLE`.

#### 2.4.2 Contratos detallados de Direcciones y Cotización de Envío (SPEC-12)
- **`GET /api/v1/direcciones`** (requiere sesión `CLIENTE`):
  - **Respuesta `200 OK`:** `{ "direcciones": [{ "id": "...", "etiqueta": "Casa", "destinatario": "Juan Pérez", "departamento": "Lima", "provincia": "Lima", "distrito": "Miraflores", "direccion": "Av. Larco 1234, dpto. 502", "referencia": "Frente al parque", "predeterminada": true }] }`.
  - **Errores:** `401 REQUIERE_SESION`, `503 MODULO_NO_DISPONIBLE` (`modulo: "security"`).
- **`POST /api/v1/envio/cotizar`** (requiere sesión `CLIENTE`):
  - **Cuerpo de entrada:** acepta los nombres de campo de Ventas (`destinatario`, `direccion`) y sus alias del formulario de checkout (`nombreCompleto`, `direccionExacta`), además de `distrito` (obligatorio), `departamento` (por defecto `"Lima"`), `provincia` (por defecto `"Lima"`), `referencia` (opcional) y `conversacionId` (opcional).
  - **Respuesta `200 OK`:** `{ "coberturaDisponible": true, "costoEnvio": 12.50, "moneda": "PEN", "plazoEstimadoDias": 1, "fechaEstimadaEntrega": "2026-11-06", "nombreZona": "Lima Metropolitana", "modalidad": "DELIVERY", "distrito": "Miraflores" }`.
  - **Errores (`application/problem+json`):**
    - `400 VALIDACION`: `destinatario`/`nombreCompleto` vacío, `direccion`/`direccionExacta` menor a 5 caracteres, `distrito` vacío o carrito sin líneas (`DESP_ERROR_DESTINO_REQUERIDO`, `DESP_ERROR_LINEAS_VACIAS`, `DESP_ERROR_CANTIDAD_INVALIDA`).
    - `401 REQUIERE_SESION`: cliente no autenticado.
    - `409 PRODUCTO_NO_DISPONIBLE`: SKU inexistente en Despacho/Productos (`DESP_ERROR_PRODUCTO_NO_ENCONTRADO`).
    - `422 SIN_COBERTURA`: Despacho responde `coberturaDisponible: false` para el distrito indicado; incluye `distrito`.
    - `429 DEMASIADAS_SOLICITUDES`: límite de cotizaciones excedido (`DESP_ERROR_LIMITE_COTIZACION`).
    - `503 MODULO_NO_DISPONIBLE`: timeout (> 4 s), caída de Despacho/Productos o respuesta de Despacho sin `costoEnvio` o sin plazo (`plazoEstimadoDiasHabiles` o `plazoEstimadoDias`); incluye `modulo: "dispatch"`. No se supone un costo de cero ni un plazo de un día.

### 2.5 Checkout, pago y pedidos (SPEC-14 a SPEC-18)
| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| POST | `/checkout` | Obligatoria (`CLIENTE`) | Crea la sesión de checkout (vigencia 15 min) y el pedido `CREADO` en Ventas, y devuelve el resumen. Requiere `Idempotency-Key`. |
| GET | `/checkout/{checkoutId}` | Obligatoria (`CLIENTE`) | Estado del checkout, expiración e intentos restantes. |
| POST | `/checkout/{checkoutId}/pago` | Obligatoria (`CLIENTE`) | Datos de tarjeta, que se procesan en el simulador y **no se persisten**. Requiere `Idempotency-Key`. |
| GET | `/pedidos` | Obligatoria (`CLIENTE`) | Pedidos del cliente (proxy de Ventas `/api/v1/pedidos/me`, filtrado por `sub`). |
| GET | `/pedidos/{pedidoId}` | Obligatoria (`CLIENTE`) | Detalle, estado e historial del pedido (proxy de Ventas con token del titular). |
| GET | `/pedidos/{pedidoId}/seguimiento` | Obligatoria (`CLIENTE`) | Hitos del despacho (proxy de Despacho con token de servicio, tras verificar pertenencia). |
| POST | `/pedidos/{pedidoId}/reenviar-confirmacion` | Obligatoria (`CLIENTE`) | Reenvía el correo de confirmación del pedido (máx. 2 por pedido, SPEC-16 · Req. 3). Requiere `Idempotency-Key`. Se invoca desde la acción "Reenviar" de la UI, no como herramienta del LLM. |

#### 2.5.1 Contratos detallados de Checkout y Simulación de Pago (SPEC-14, SPEC-15)
- **`POST /api/v1/checkout`** (requiere sesión `CLIENTE` y cabecera `Idempotency-Key`):
  - **Cuerpo de entrada:**
    ```json
    {
      "cartId": "uuid-opcional",
      "conversacionId": "uuid-opcional",
      "guardarDireccion": false,
      "direccion": {
        "destinatario": "Juan Pérez",
        "nombreCompleto": "Juan Pérez",
        "departamento": "Lima",
        "provincia": "Lima",
        "distrito": "Miraflores",
        "direccion": "Av. Larco 1234, dpto. 502",
        "direccionExacta": "Av. Larco 1234, dpto. 502",
        "referencia": "Frente al parque Kennedy"
      },
      "contacto": {
        "nombreCompleto": "Juan Pérez Rodríguez",
        "tipoDocumento": "DNI",
        "numeroDocumento": "72458912",
        "telefono": "+51999888777",
        "email": "juan.perez@example.com"
      }
    }
    ```
  - `cartId` es opcional; si se indica, debe identificar un carrito del cliente autenticado. El servidor obtiene las líneas del carrito propio y resuelve precios, disponibilidad, descuentos y cupón con Productos, y costo y plazo de envío con Despacho, según SPEC-14. El cliente y el LLM no envían líneas ni importes. La respuesta contiene el resumen calculado por el servidor.
  - **Contacto verificado y snapshot:** el guard de contacto usa el correo del perfil (`GET /auth/me`), no el `email` de `contacto`; el snapshot del pedido también toma el correo del perfil. El `email` que envíe el cliente no reemplaza al correo verificado de la cuenta.
  - **Validación de `contacto.tipoDocumento` / `numeroDocumento` (SPEC-12 Req. 1, A14):**
    - `DNI`: `^[0-9]{8}$`
    - `RUC`: `^(10|15|17|20)[0-9]{9}$`
    - `CE`: `^[a-zA-Z0-9]{8,12}$`
    - `PASAPORTE`: `^[a-zA-Z0-9]{6,12}$`
    - `contacto` se valida con `BuyerContactDTO`: `nombreCompleto` es obligatorio y se aplican los patrones de documento anteriores. Si falta o es inválido un dato de `contacto`, responde `400 DATO_INVALIDO`.
  - **Respuesta `201 Created`:**
    ```json
    {
      "id": "uuid-checkout",
      "cartId": "uuid-cart",
      "pedidoId": "PED-2026-00891",
      "status": "PENDING_PAYMENT",
      "total": 282.40,
      "moneda": "PEN",
      "expiresAt": "2026-11-05T18:15:00Z",
      "intentosRestantes": 3,
      "summary": { "contacto": { ... }, "direccion": { ... }, "lineas": [...], "subtotal": 299.90, "descuento": 30.00, "costoEnvio": 12.50, "total": 282.40 },
      "avisoDireccion": null
    }
    ```
    *(Si `guardarDireccion` es `true` y Seguridad falla al guardar la dirección, el checkout continúa igual y `avisoDireccion` informa `"No pudimos guardar tu dirección para la próxima vez"`, SPEC-12 Req. 3).*
  - **Errores (`application/problem+json`):**
    - `400 VALIDACION`: falta cabecera `Idempotency-Key`, dirección incompleta o el cuerpo contiene campos no admitidos, incluidos líneas e importes.
    - `400 DATO_INVALIDO`: falta o es inválido un dato de `contacto`, incluidos `nombreCompleto`, `tipoDocumento` y `numeroDocumento` (A14).
    - `401 REQUIERE_SESION` / `401 TOKEN_INVALIDO`: sin sesión o token inválido.
    - `403 CONTACTO_NO_VERIFICADO`: no se pudo confirmar un contacto verificado (SPEC-04 / SPEC-14 Req. 1). Incluye `motivo` (`SIN_SESION`, `SEGURIDAD_NO_DISPONIBLE`, `SIN_CONTACTO_VERIFICADO`) y, si el perfil tiene celular, `celularEnmascarado` opcional. Es defensivo: una cuenta activa con correo verificado no lo recibe.
    - `403 CELULAR_NO_VERIFICADO`: modo legado con `REQUIRE_PHONE_VERIFICATION=true`; el celular vigente no tiene verificación local (SPEC-04).
    - `409 CARRITO_VACIO`: el carrito no tiene líneas disponibles para comprar.
    - `409 STOCK_INSUFICIENTE` / `409 PRODUCTO_NO_DISPONIBLE`: validación de stock fallida en Productos o rechazo `409` de Ventas al crear el pedido (segunda barrera). Se responde `409` con su `code`, nunca `500` (`BE/src/modules/mod_checkout/adapters/http/checkout_router.py:66-67`).
    - `409 CARRITO_DESACTUALIZADO`: cambió el precio, el stock, el cupón o la cotización respecto al resumen confirmado; incluye `lineas` con las líneas bloqueantes (`motivo`: `AGOTADO`, `STOCK_INSUFICIENTE` o `NO_CONFIRMADO`, con `nombre` y `mensaje`) y `summary` actualizado por el servidor. No se crea checkout ni pedido hasta que el cliente confirme el nuevo resumen.
      ```json
      { "status": 409, "code": "CARRITO_DESACTUALIZADO", "title": "Cart changed", "lineas": [{ "sku": "ZAP-RUN-42-NEG", "nombre": "Zapatilla Run 42/Negro", "cantidad": 2, "motivo": "AGOTADO", "mensaje": "Se agotó mientras elegías." }], "summary": { "lineas": [{ "sku": "ZAP-RUN-42-NEG", "cantidad": 1, "precioUnitario": 299.90 }], "subtotal": 299.90, "descuento": 30.00, "costoEnvio": 12.50, "total": 282.40 } }
      ```
    - `422 SIN_COBERTURA`: el distrito no tiene cobertura de Despacho.
    - `503 ERROR_VENTAS`: Ventas respondió con un error no clasificable al crear el pedido (distinto de `409` por stock y de `400` por datos); el checkout no se crea y se puede reintentar con la misma `Idempotency-Key` (`checkout_router.py:68`, `manage_checkout_use_case.py:373-374`).
    - `503 MODULO_NO_DISPONIBLE` / `503 SERVICIO_NO_DISPONIBLE`: Ventas, Productos o Despacho no disponible; también cuando la revalidación de stock no puede obtener una respuesta válida (no se asume disponibilidad).
  - **Guard de contacto y precedencia de flags (SPEC-04):** `REQUIRE_PHONE_VERIFICATION=true` activa el modo legado y exige solo el celular verificado localmente; si está en `false`, `REQUIRE_VERIFIED_CONTACT=true` (valor por defecto en producción) acepta el correo del perfil o el celular verificado localmente; con ambos en `false` no hay guard (solo pruebas/demos). El modo legado tiene precedencia sobre el flag nuevo. Una cuenta activa con correo verificado supera el guard por defecto.

- **`GET /api/v1/checkout/{checkoutId}`** (requiere sesión `CLIENTE`):
  - **Respuesta `200 OK`:** misma estructura que `POST /checkout` (`status` ∈ `PENDING_PAYMENT | PAYMENT_APPROVED | CONFIRMED | FAILED | EXPIRED`).
  - **Errores:** `401 REQUIERE_SESION`, `404 RECURSO_NO_ENCONTRADO` (no existe o pertenece a otro cliente).

- **`POST /api/v1/checkout/{checkoutId}/pago`** (requiere sesión `CLIENTE` y cabecera `Idempotency-Key`):
  - **Cuerpo de entrada** (excluido de logs; nunca se persiste PAN, vencimiento ni CVV):
    ```json
    {
      "numeroTarjeta": "4111111111111111",
      "titular": "JUAN PEREZ",
      "vencimiento": "12/28",
      "cvv": "123"
    }
    ```
  - **Respuesta `200 OK`:**
    ```json
    {
      "id": "uuid-attempt",
      "checkoutId": "uuid-checkout",
      "pedidoId": "PED-2026-00891",
      "resultado": "APROBADO",
      "marca": "VISA",
      "ultimos4": "1111",
      "monto": 282.40,
      "moneda": "PEN",
      "idTransaccion": "SIM-7f8a9b0c"
    }
    ```
  - **Reintento con la misma `Idempotency-Key`:** devuelve el resultado **original** del intento, sin procesar otro pago ni consumir otro intento. Si el intento original fue aprobado, responde `200` con la misma aprobación y el mismo `idTransaccion`; si fue rechazado o falló, responde de nuevo el mismo error (`402 PAGO_RECHAZADO` o `503 ERROR_PROCESAMIENTO`, con `intentosRestantes` recalculado desde el checkout). Un intento rechazado NUNCA se informa como `APROBADO`. Si la clave se usó en otro checkout, responde `409 CONFLICTO`. *Alineación 2026-11-21 con `BE/src/modules/mod_checkout/application/manage_checkout_use_case.py:602-608` (rama `fix/audit-wave-0-1`); antes, la repetición de un intento rechazado se respondía como aprobada (hallazgo BE-AUD-01).*
  - **Errores (`application/problem+json`):**
    - `400 VALIDACION`: falta `Idempotency-Key`, falla algoritmo de Luhn, marca no soportada, tarjeta vencida o CVV inválido (no descuenta intento, SPEC-14 Req. 3).
    - `401 REQUIERE_SESION` / `401 TOKEN_INVALIDO`: el JWT no es válido o la introspección contra Seguridad (`POST /auth/introspeccion`, A3) devolvió `activo: false` (SPEC-14 Req. 4).
    - `402 PAGO_RECHAZADO`: tarjeta rechazada por el simulador; incluye `motivo` (`FONDOS_INSUFICIENTES`, `RECHAZADO_POR_EMISOR`, `INTENTOS_AGOTADOS`) e `intentosRestantes` (`0..2`). En el 3.er rechazo (`intentosRestantes: 0`) el checkout pasa a `FAILED` y se encola la anulación del pedido `CREADO` en el outbox.
    - `404 RECURSO_NO_ENCONTRADO`: el checkout no existe o pertenece a otro cliente.
    - `410 CHECKOUT_EXPIRADO`: transcurrieron más de 15 minutos desde la creación del checkout; el checkout pasa a `EXPIRED` y se encola la anulación del pedido `CREADO`.
    - `503 ERROR_PROCESAMIENTO`: error transitorio del simulador (`4000 0000 0000 0119` -> `PROCESSING_ERROR`, se puede reintentar; incluye `motivo` e `intentosRestantes`).
    - `503 SERVICIO_NO_DISPONIBLE`: falla de `POST /auth/introspeccion` en Seguridad (nunca se asume `activo: true` por defecto).

#### 2.5.2 Contratos detallados de Pedidos y Seguimiento (SPEC-16, SPEC-17, SPEC-18)
- **`GET /api/v1/pedidos?estado=&desde=&hasta=&page=1&pageSize=10`** (requiere sesión `CLIENTE`):
  - Reenvía el token del cliente a `GET /api/v1/pedidos/me` de Ventas (A15).
  - `desde` y `hasta` son opcionales, fechas ISO `YYYY-MM-DD`; filtran por `fechaCreacion` y se reenvían **sin transformación** a `GET /api/v1/pedidos/me` de Ventas. `estado`, `page` y `pageSize` mantienen su contrato actual. Un rango invertido (`desde > hasta`) responde `400 VALIDACION` sin llamar a Ventas.
  - **Respuesta `200 OK`:**
    ```json
    {
      "items": [
        {
          "pedidoId": "PED-2026-00891",
          "canal": "CHATBOT",
          "estado": "EN_PREPARACION",
          "estadoEtiqueta": "En preparación",
          "total": 282.40,
          "moneda": "PEN",
          "fechaCreacion": "2026-11-05T18:02:00Z"
        }
      ],
      "total": 1,
      "page": 1,
      "pageSize": 10
    }
    ```
  - **Errores:** `400 VALIDACION` (incluye `desde` o `hasta` con formato inválido o `desde > hasta`), `401 REQUIERE_SESION`, `503 MODULO_NO_DISPONIBLE` (`modulo: "sales"`).

- **`GET /api/v1/pedidos/{pedidoId}`** (requiere sesión `CLIENTE`):
  - Reenvía el token del cliente a `GET /api/v1/pedidos/{pedidoId}` de Ventas (A15). Si Ventas responde `403` o `404`, el BFF responde `404 RECURSO_NO_ENCONTRADO` para no revelar la existencia de pedidos ajenos (SPEC-17 Req. 1).
  - **Respuesta `200 OK`:**
    ```json
    {
      "pedidoId": "PED-2026-00891",
      "canal": "CHATBOT",
      "estado": "DESPACHADO",
      "estadoEtiqueta": "En camino",
      "total": 282.40,
      "moneda": "PEN",
      "fechaCreacion": "2026-11-05T18:02:00Z",
      "items": [
        { "productoId": "P-100", "sku": "ZAP-RUN-42-NEG", "descripcion": "Zapatilla X 42/Negro", "cantidad": 1, "precioUnitario": 299.90 }
      ],
      "envio": {
        "destinatario": "Juan Pérez",
        "distrito": "Miraflores",
        "direccion": "Av. Larco 1234, dpto. 502",
        "costo": 12.50,
        "plazoEstimadoDias": 1
      },
      "historial": [
        { "estado": "CREADO", "etiqueta": "Pendiente de pago", "fecha": "2026-11-05T18:00:00Z", "completado": true },
        { "estado": "PAGADO", "etiqueta": "Pago confirmado", "fecha": "2026-11-05T18:02:00Z", "completado": true },
        { "estado": "EN_PREPARACION", "etiqueta": "En preparación", "fecha": "2026-11-05T19:00:00Z", "completado": true },
        { "estado": "DESPACHADO", "etiqueta": "Despachado", "fecha": "2026-11-06T09:00:00Z", "completado": true }
      ],
      "csatEnviado": false,
      "seguimientoDisponible": true
    }
    ```
  - **Errores:** `401 REQUIERE_SESION`, `404 RECURSO_NO_ENCONTRADO`, `503 MODULO_NO_DISPONIBLE`.
  - **`csatEnviado`:** `true` si el chatbot ya marcó la calificación de la entrega como enviada en `order_ref.csat_sent` (tras un `201` o un `409 CSAT_ALREADY_SUBMITTED`); `false` si no hay fila local o aún no se calificó. El frontend lo usa para ocultar el slot de CSAT de `mod-postventa` sin volver a preguntar a Ventas. Un pedido de otro canal sin fila local llega como `false`; si ya estaba calificado, Ventas responde `409` al enviar.

- **`GET /api/v1/pedidos/{pedidoId}/seguimiento`** (requiere sesión `CLIENTE`):
  - Verifica primero que `pedidoId` pertenezca al cliente en Ventas (SPEC-18 Req. 1) y luego consulta `GET /api/v1/seguimientos/pedidos/{pedidoId}` en Despacho con el token de servicio de `modulo-chatbot` (`aud=api-despacho`, scope `seguimientos:leer`, A11/A4).
  - **Lista blanca obligatoria (SPEC-18 Req. 3 y RNF Privacidad):** de Despacho solo se aceptan `pedidoId`, `estado`, `estadoEtiqueta`, `fechaProgramada`, `distrito`, `hitos[{estado, etiqueta, fecha}]` (payload real de Despacho), `recibidoPor` (solo para la UI del frontend, nunca para el LLM) y `detalleDisponible`. Se descartan coordenadas GPS, teléfono/datos del repartidor, dirección completa y motivos internos de fallo.
  - **Mapeo de hitos.** Despacho publica el texto de cada hito como `etiqueta`. El BFF (`SeguimientoMapper`) lo normaliza a `titulo` en la respuesta de `/pedidos/{pedidoId}/seguimiento`, que es el campo que consumen la UI y el LLM; `titulo` no existe en el contrato de G2. `fecha` pasa sin cambios. G2 no publica `completado`: el BFF lo agrega como `true` cuando falta.
  - Si el pedido está `PAGADO` o `EN_PREPARACION` y Despacho responde `404`, no es un error: devuelve `200 OK` con `detalleDisponible: false`, `estado: "EN_PREPARACION"`, `estadoEtiqueta: "En preparación"`, `hitos: []` y `mensaje: "Tu pedido aún se está preparando; te mostraremos el seguimiento cuando salga del centro de despacho"`.
  - **Respuesta `200 OK`:**
    ```json
    {
      "pedidoId": "PED-2026-00891",
      "estado": "EN_CAMINO",
      "estadoEtiqueta": "En camino",
      "fechaProgramada": "2026-11-06",
      "distrito": "Miraflores",
      "hitos": [
        { "titulo": "Recibido en centro de despacho", "fecha": "2026-11-06T10:00:00-05:00", "completado": true },
        { "titulo": "Asignado a repartidor", "fecha": "2026-11-06T14:30:00-05:00", "completado": true },
        { "titulo": "En camino", "fecha": "2026-11-06T16:00:00-05:00", "completado": true }
      ],
      "recibidoPor": null,
      "detalleDisponible": true,
      "mensaje": null
    }
    ```
  - **Errores:** `401 REQUIERE_SESION`, `404 RECURSO_NO_ENCONTRADO` (pedido ajeno o inexistente en Ventas), `503 MODULO_NO_DISPONIBLE`.
  - **Origen de `hitos[].titulo`:** el BFF lo obtiene de `etiqueta` en la respuesta de Despacho; el contrato expuesto al frontend y al LLM conserva `titulo` y agrega `completado` (`true` si G2 no lo envía). No se reenvía el payload crudo de G2.

- **`POST /api/v1/pedidos/{pedidoId}/reenviar-confirmacion`** (requiere sesión `CLIENTE` y cabecera `Idempotency-Key`):
  - Verifica pertenencia del pedido y encola un reenvío de confirmación (`CONFIRMATION_RESEND`, máx. 2 reenvíos por pedido, SPEC-16 Req. 3).
  - La deduplicación se identifica por cliente, pedido y `Idempotency-Key`: repetir la misma clave devuelve el mismo resultado sin encolar otro correo ni consumir otro reenvío.
  - **Respuesta `202 Accepted`:**
    ```json
    {
      "ok": true,
      "pedidoId": "PED-2026-00891",
      "reenviosRestantes": 1,
      "correoEnmascarado": "j***z@example.com"
    }
    ```
  - **Errores (`application/problem+json`):** `400 VALIDACION` (falta `Idempotency-Key`), `401 REQUIERE_SESION`, `404 RECURSO_NO_ENCONTRADO`, `429 LIMITE_REENVIOS_EXCEDIDO` (ya se realizaron los 2 reenvíos permitidos para ese pedido).

### 2.6 Reclamos (SPEC-19, SPEC-20) ✅
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/reclamos` | Registra el reclamo en Ventas. Requiere `Idempotency-Key`. Acepta `forzar: boolean` (por defecto `false`): si existe un reclamo abierto del mismo pedido y motivo y no se fuerza, responde `409 RECLAMO_DUPLICADO` con `{reclamoId, codigoSeguimiento, estado}`. |
| GET | `/reclamos` | Proxy de `GET /api/v2/reclamos/me` con el token del cliente — reclamos del cliente. |
| GET | `/reclamos/{codigoSeguimiento}` | Proxy de `GET /api/v2/reclamos/{codigoSeguimiento}` — estado y respuesta del reclamo. |

**Motivos de reclamo (contrato real de G5, 2026-11).** G5 solo acepta cinco valores y **no existe `OTRO`**: `INCUMPLIMIENTO_PLAZO_ENTREGA`, `PRODUCTO_DEFECTUOSO_O_INCORRECTO`, `COBRO_INDEBIDO_O_NO_RECONOCIDO`, `ATENCION_INADECUADA` e `INCUMPLIMIENTO_GARANTIA`. El formulario ofrece solo esos cinco; el cliente elige el más cercano y explica el caso concreto en `detalle` (20 a 1000 caracteres). Un `motivo` fuera de la lista —incluidos los alias antiguos `PRODUCTO_DEFECTUOSO`, `PRODUCTO_EQUIVOCADO`, `PEDIDO_INCOMPLETO`, `NO_RECIBIDO`, `COBRO_INCORRECTO`, `ATENCION` y `OTRO`— responde `400 VALIDACION` con `errores[{campo: "motivo", mensaje}]` y no se reenvía a Ventas. Si la petición llega **directo** a G5 saltándose el BFF, G5 responde `400 FORMATO_INVALIDO` (ver §2.10); el contrato del chatbot sigue siendo `VALIDACION`.

### 2.7 Devoluciones y reembolsos (SPEC-21, SPEC-22) ✅
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/evidencias` | Proxy de `POST /api/v2/devoluciones/evidencias/upload` de Ventas; devuelve la misma URL que Ventas genera, para incluirla en el `POST /devoluciones`. Acepta `conversacionId` opcional: si se envía y no pertenece al cliente (o no existe), responde `404 RECURSO_NO_ENCONTRADO` y **no llama a Ventas**. |
| POST | `/devoluciones` | Registra la solicitud de devolución o cambio en Ventas. Requiere `Idempotency-Key`. Acepta `forzar: boolean` (por defecto `false`): si existe una solicitud abierta (`SOLICITADA`, `EN_EVALUACION` o `APROBADA`) para el mismo pedido, motivo y líneas y no se fuerza, responde `409 DEVOLUCION_DUPLICADA` con `{devolucionId, estado, motivo}`. |
| GET | `/devoluciones` | Proxy de `GET /api/v2/devoluciones/me` con el token del cliente — trae **todas** las solicitudes del cliente, incluidas las de otros canales, no solo las que registró el chatbot. |
| GET | `/devoluciones/{devolucionId}` | Estado del expediente y, si aplica, el bloque `resolucion.reembolso` con el estado del extorno. |

### 2.8 Códigos de error propios
| `code` | HTTP | Significado |
|---|---|---|
| `REQUIERE_SESION` | 401 | La acción necesita sesión de cliente. |
| `DATO_INVALIDO` | 400 | Un dato de `contacto` del checkout falta o no cumple las reglas de nombre y documento de Ventas (A14). |
| `CONTACTO_NO_VERIFICADO` | 403 | El checkout no pudo confirmar un contacto verificado en el modo por defecto. Incluye `motivo` (`SIN_SESION`, `SEGURIDAD_NO_DISPONIBLE`, `SIN_CONTACTO_VERIFICADO`) y `celularEnmascarado` opcional; es defensivo (SPEC-04 / SPEC-14 Req. 1). |
| `CELULAR_NO_VERIFICADO` | 403 | Modo legado: el checkout requiere el celular verificado localmente (`REQUIRE_PHONE_VERIFICATION=true`). |
| `STOCK_INSUFICIENTE` | 409 | Cantidad no disponible para uno o más SKU; no incluye cantidades, porque Productos no las expone (A16). También lo devuelve `POST /checkout` cuando Ventas rechaza el pedido por stock (segunda barrera, SPEC-10). |
| `ERROR_VENTAS` | 503 | Ventas falló al crear el pedido en `POST /checkout` con un error no clasificable; no se crea checkout y se puede reintentar con la misma `Idempotency-Key`. |
| `ERROR_PROCESAMIENTO` | 503 | Error transitorio del simulador de pago en `POST /checkout/{id}/pago` (`PROCESSING_ERROR`); incluye `motivo` e `intentosRestantes`. |
| `PRODUCTO_NO_DISPONIBLE` | 409 | Producto o SKU inactivo. |
| `LIMITE_CANTIDAD` | 422 | Más de 10 unidades por línea o más de 20 líneas. |
| `SIN_COBERTURA` | 422 | El destino no tiene cobertura de Despacho. |
| `EVIDENCIA_INVALIDA` | 400 | Archivo mayor a 5 MB o tipo no permitido (evidencia de devolución, SPEC-21). |
| `EVIDENCIA_REQUERIDA` | 400 | El motivo de la devolución exige evidencia y no se adjuntó (SPEC-21; código de Ventas propagado). |
| `ADJUNTO_INVALIDO` | 400 | Imagen adjunta al chat (SPEC-23) mayor a 5 MB, de tipo no permitido, con contenido que no es una imagen válida o con dimensiones fuera de rango. |
| `LIMITE_ADJUNTOS` | 422 | Más de 3 adjuntos por mensaje o más de 10 adjuntos pendientes por conversación (SPEC-23). |
| `PEDIDO_NO_ENTREGADO` | 409 | La devolución se pidió sobre un pedido que no está `ENTREGADO` (SPEC-21; código de Ventas propagado). |
| `PLAZO_VENCIDO` | 400 | La devolución está fuera de los 7 días naturales desde la entrega (SPEC-21; código de Ventas propagado). |
| `DEVOLUCION_EN_CURSO` | 409 | Ya existe una devolución no rechazada para esas unidades (SPEC-21; código de Ventas propagado). |
| `RECLAMO_DUPLICADO` | 409 | Existe un reclamo abierto para el mismo pedido y motivo y no se envió `forzar: true`; incluye el `codigoSeguimiento` y el estado existentes. |
| `CSAT_ALREADY_SUBMITTED` | 409 | Código de Ventas propagado: ya existe una encuesta para ese pedido. El chatbot lo muestra como "Ya calificaste este pedido", no como error, y marca `order_ref.csat_sent`. |
| `ORDER_NOT_DELIVERED` | 422 | Código de Ventas propagado: el pedido no está `ENTREGADO` y no admite CSAT. El chatbot lo muestra como "Solo puedes calificar pedidos entregados" y refresca el detalle; no es un error de red. |
| `DEVOLUCION_DUPLICADA` | 409 | Existe una solicitud abierta para el mismo pedido, motivo y líneas y no se envió `forzar: true`; incluye el `devolucionId` y el estado existentes. |
| `VALORACION_YA_REGISTRADA` | 409 | El pedido ya tiene una valoración de compra; no se admite una segunda. |
| `CODIGO_VENCIDO` | 410 | El desafío OTP superó los 5 minutos o ya fue consumido (SPEC-04). |
| `OTP_INTENTOS_AGOTADOS` | 401 | Se agotaron los 3 intentos del OTP; hay que solicitar uno nuevo (SPEC-04). |
| `LIMITE_REENVIOS` | 429 | Se superaron los 3 envíos de OTP en 15 minutos; incluye `reintentarEn` (SPEC-04). |
| `CUPON_INVALIDO` | 422 | Incluye `motivo` (`INEXISTENTE`, `EXPIRADO`, `NO_VIGENTE`, `AGOTADO`, `LIMITE_CLIENTE`, `MONTO_MINIMO`, `NO_APLICA_PRODUCTOS`, `NO_APLICA_CANAL`, `NO_COMBINABLE`). |
| `REQUIERE_CONFIRMACION_REEMPLAZO` | 409 | El carrito ya tiene un cupón aplicado y se debe confirmar su reemplazo (`cuponActual`, `cuponNuevo`). |
| `CARRITO_VACIO` | 409 | El carrito no contiene líneas disponibles para iniciar el checkout (SPEC-14 Req. 1). |
| `CARRITO_DESACTUALIZADO` | 409 | Cambió el precio, el stock, el cupón o la cotización desde el resumen confirmado; el cuerpo incluye `lineas` bloqueantes y `summary` actualizado por el servidor para nueva confirmación. |
| `PAGO_RECHAZADO` | 402 | Incluye `motivo` e `intentosRestantes`. |
| `CHECKOUT_EXPIRADO` | 410 | Pasaron más de 15 minutos. |
| `LIMITE_REENVIOS_EXCEDIDO` | 429 | Ya se enviaron los 2 reenvíos de confirmación por correo permitidos para el pedido (SPEC-16 Req. 3). |
| `RECURSO_NO_ENCONTRADO` | 404 | También se usa cuando el recurso existe pero no pertenece al cliente. |
| `MODULO_NO_DISPONIBLE` / `SERVICIO_NO_DISPONIBLE` | 503 | Falló un módulo externo; incluye `modulo`. |
| `DEMASIADAS_SOLICITUDES` | 429 | Se superó el rate limit. |
| `VALIDACION` | 400 | Incluye `errores[{campo, mensaje}]`. En reclamos también se usa cuando `motivo` no es uno de los cinco valores de G5 (SPEC-19 · Requisito 1); en CSAT, cuando `puntuacion` no es 1, 3 o 5 (SPEC-24 · Requisito 2). |
| `DATO_INVALIDO` | 400 | Específico del documento de identidad (`tipoDocumento`/`numeroDocumento`); el frontend lo evita validando antes con las reglas de `SPEC-12` · Requisito 1, pero Ventas también lo aplica del lado suyo. |

### 2.9 Retroalimentación (SPEC-24)
🧩 Nuevo (D5, 2026-11-21). Cuatro mecanismos: reacciones, sugerencias/bugs, CSAT de la entrega y valoración de la compra.

| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| POST | `/mensajes/{mensajeId}/reaccion` | Opcional (`CLIENTE` o `chat_sid`) | `{reaccion: "POSITIVE"\|"NEGATIVE"}`; upsert por mensaje y autor. Responde `200 {mensajeId, reaccion}`. `404 RECURSO_NO_ENCONTRADO` si el mensaje no es de la conversación; `429 DEMASIADAS_SOLICITUDES` (la UI lo ignora en silencio). |
| POST | `/pedidos/{pedidoId}/valoracion-compra` | `CLIENTE` | `{estrellas: 1..5, comentario?}`; una por pedido. Responde `201 {valoracionId, estrellas}`. `409 VALORACION_YA_REGISTRADA`. |
| POST | `/pedidos/{pedidoId}/csat` | `CLIENTE` | `mod-postventa` hace de proxy a `POST /api/v2/csat` de Ventas; el chatbot no guarda una calificación propia. El cuerpo del frontend es `{puntuacion, comentario?}` y **no lleva `clienteId`**: el backend lo arma con el `sub` del token y reenvía el token del cliente a Ventas. Solo se ofrece al pie del detalle de un pedido `ENTREGADO`, no en la lista. `puntuacion` solo acepta 1, 3 o 5; otro valor responde `400 VALIDACION` antes de llamar a Ventas. Marca `order_ref.csat_sent` con `201` o `409`. Si el pedido no es del cliente (Ventas responde `403`) o no existe, el BFF responde `404 RECURSO_NO_ENCONTRADO` para no revelar su existencia (`SPEC-17` · Requisito 1). `409 CSAT_ALREADY_SUBMITTED` se muestra como "Ya calificaste este pedido"; `422 ORDER_NOT_DELIVERED`, como "Solo puedes calificar pedidos entregados". |
| POST | `/sugerencias` | `CLIENTE` | `multipart/form-data` con `tipo` (`SUGERENCIA`/`BUG`), `titulo`, `descripcion`, `correoContacto`, `captura?` (JPG/PNG ≤ 5 MB) e `Idempotency-Key`. Responde `201 {sugerenciaId, codigoSeguimiento}`. Errores `400 VALIDACION`, `400 ADJUNTO_INVALIDO`, `429 DEMASIADAS_SOLICITUDES`. |

La captura usa el puerto `AttachmentStorage` de SPEC-23 y se guarda en `feedback_suggestion.screenshot_key`; no usa la tabla `attachment`. La notificación interna se encola por outbox (`SEND_EMAIL`) y su estado vive en `feedback_suggestion.notification_status`; un fallo no se muestra al cliente.

### 2.10 Evidencia G5 2026-11
Corrida real contra G5 el **2026-11-22**. El gateway `https://g5-api-gateway.onrender.com` no fue usable server-to-server: devolvió un challenge de Cloudflare y `429`. Por eso se usaron los servicios directos **M1** (`https://g5-servicio-ventas.onrender.com`) y **M2** (`https://g5-ventas-postventas-backend.onrender.com`). El BFF del chatbot expone esas operaciones bajo su propio prefijo `/api/v1`; la columna "Ruta BFF" indica la ruta equivalente. **La tabla EV-01..EV-05 cubre los cinco motivos de reclamo, uno por caso.**

Cuentas usadas: cuenta principal (`sub be1f271e-...`, dueña de 90101/90102) y cuenta secundaria (`sub 5068e541-...`, dueña de 90201).

| Servicio G5 | Base ejecutada | Operaciones de esta corrida | Ruta BFF equivalente |
|---|---|---|---|
| M1 | `https://g5-servicio-ventas.onrender.com` | Pedidos: listado y detalle | `/api/v1/pedidos...` |
| M2 | `https://g5-ventas-postventas-backend.onrender.com` | Reclamos, devoluciones y CSAT | `/api/v1/reclamos...`, `/api/v1/devoluciones...`, `/api/v1/pedidos/{pedidoId}/csat` |

| Caso | Operación | Endpoint ejecutado (G5) | HTTP | Hora UTC | id | Ruta BFF equivalente | Nota |
|---|---|---|---|---|---|---|---|
| EV-01 | Reclamo `INCUMPLIMIENTO_PLAZO_ENTREGA` | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/reclamos` | 201 | 2026-11-22T18:20:13Z | `REC-2026-0009` | `POST /api/v1/reclamos` | Motivo 1 de 5 |
| EV-02 | Reclamo `PRODUCTO_DEFECTUOSO_O_INCORRECTO` | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/reclamos` | 201 | 2026-11-22T18:27:06Z | `REC-2026-0010` | `POST /api/v1/reclamos` | Motivo 2 de 5 |
| EV-03 | Reclamo `COBRO_INDEBIDO_O_NO_RECONOCIDO` | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/reclamos` | 201 | 2026-11-22T18:27:06Z | `REC-2026-0011` | `POST /api/v1/reclamos` | Motivo 3 de 5 |
| EV-04 | Reclamo `ATENCION_INADECUADA` | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/reclamos` | 201 | 2026-11-22T18:27:07Z | `REC-2026-0012` | `POST /api/v1/reclamos` | Motivo 4 de 5 |
| EV-05 | Reclamo `INCUMPLIMIENTO_GARANTIA` | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/reclamos` | 201 | 2026-11-22T18:27:08Z | `REC-2026-0013` | `POST /api/v1/reclamos` | Motivo 5 de 5 |
| EV-06 | CSAT de pedido `ENTREGADO`: primer envío y reintento | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/csat` | 201 / 409 `CSAT_ALREADY_SUBMITTED` | 2026-11-22T18:22:39Z (aprox.) / 18:22:41Z | `PED-2026-90201` | `POST /api/v1/pedidos/{pedidoId}/csat` | Primer envío 201; reintento inmediato 409. 90101 y 90102 ya tenían CSAT (409) antes de esta corrida |
| EV-07 | CSAT de pedido no entregado | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/csat` | 422 `ORDER_NOT_DELIVERED` | 2026-11-22T18:23:13Z | `PED-2026-90103` | `POST /api/v1/pedidos/{pedidoId}/csat` | Pedido en estado `PAGADO` |

**Controles adicionales de la misma corrida**

| Control | Endpoint ejecutado (G5) | Resultado | Hora UTC | id / nota |
|---|---|---|---|---|
| Reclamo con `motivo: "OTRO"` | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/reclamos` | 400 `FORMATO_INVALIDO` | 2026-11-22T18:23:14Z | Sin id. G5 rechaza el motivo fuera de su enum; el BFF valida antes y expone `400 VALIDACION` (SPEC-19) |
| Listado de pedidos `/pedidos/me` | `GET https://g5-servicio-ventas.onrender.com/api/v1/pedidos/me` | 200, 11 pedidos | 2026-11-22T18:19:54Z | Filtros `estado`, `desde`, `hasta`, `page` y `pageSize` verificados; BFF `GET /api/v1/pedidos` |
| Detalle de pedido propio | `GET https://g5-servicio-ventas.onrender.com/api/v1/pedidos/{id}` | 200 | 2026-11-22T18:19:55Z | Pedido de la cuenta dueña; BFF `GET /api/v1/pedidos/{id}` |
| Detalle de pedido ajeno | `GET https://g5-servicio-ventas.onrender.com/api/v1/pedidos/{id}` | 403 `ACCESO_DENEGADO` | 2026-11-22T18:19:58Z | El BFF lo traduce a `404 RECURSO_NO_ENCONTRADO`, igual que un pedido inexistente, por SPEC-17 |
| Devolución en 90201 | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/devoluciones` | 201, `DEV-2026-0028` | 2026-11-22T18:22:42Z | `motivo: "OTRO"` + evidencia; BFF `POST /api/v1/devoluciones` |
| Devolución en 90101/90102 | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/devoluciones` | 400 `PLAZO_VENCIDO` | 2026-11-22T18:20:10Z (90101) / 2026-11-22T18:22:04Z (90102) | Entregados el 15/11 y el 08/11; es dato de prueba de G5, no un fallo del canal |
| Devolución con `TALLA_INCORRECTA` directo a G5 | `POST https://g5-ventas-postventas-backend.onrender.com/api/v2/devoluciones` | 400 `FORMATO_INVALIDO` | 2026-11-22T18:21:39Z | G5 no acepta ese literal en F3; el mapeo del adapter a `OTRO` es obligatorio (SPEC-21) |

**Lectura de la evidencia.** EV-01..EV-05 confirman que G5 acepta los cinco motivos y que el canal no debe enviar `OTRO`. EV-06 confirma el `201` inicial y el `409` de reintento; EV-07 confirma el `422` cuando el pedido no está `ENTREGADO`. Los `409` de 90101/90102 (ya calificados) y los `400 PLAZO_VENCIDO` de esas mismas cuentas (entregadas el 15/11 y 08/11) son **datos de prueba de G5, no fallos de G3**; 90201 se usó para el CSAT nuevo y para la devolución `DEV-2026-0028`. El `400 FORMATO_INVALIDO` de `motivo: "OTRO"` es la respuesta directa de G5 al saltarse el BFF; el contrato del chatbot sigue siendo `400 VALIDACION` porque valida antes de reenviar.

**Script reproducible.** `backend/scripts/verify_g5_integration.py` documenta y repite la corrida: `--dry-run` es el modo por defecto (imprime el plan sin llamadas de escritura), `--execute` requiere `G5_BEARER_TOKEN` (token de cliente), apunta a los servicios directos M1/M2 y escribe `docs/evidencia-g5-<UTC>.md`; no imprime ni guarda el token.

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

Errores de Seguridad: RFC 7807 con `code`. Lista completa: `TOKEN_INVALIDO`, `SCOPE_INSUFICIENTE`, `CREDENCIALES_INVALIDAS`, `VALIDACION`, `POLITICA_INCUMPLIDA`, `CORREO_NO_DISPONIBLE`, `CODIGO_INVALIDO` (con `intentosRestantes`), `OTP_INTENTOS_AGOTADOS`, `OTP_EXPIRADO` (410), `PASSWORD_CADUCADA` (403), `ENLACE_EXPIRADO`, `ENLACE_YA_USADO`, `REFRESCO_INVALIDO`, `DEMASIADAS_SOLICITUDES`, `NO_DISPONIBLE`.

🧩 **Aviso directo de Seguridad (corrige lo asumido antes):** `POST /auth/login` **nunca** responde `CUENTA_NO_DISPONIBLE`. Una cuenta bloqueada, inactiva o sin verificar responde exactamente igual que una contraseña incorrecta: `401 CREDENCIALES_INVALIDAS`, a propósito, para no revelar el estado de la cuenta. El chatbot no puede distinguir la causa en el login (ver SPEC-03 Requisito 1); por eso SPEC-02 ofrece el reenvío de verificación en *todo* login fallido, no solo cuando "corresponde". `CUENTA_NO_DISPONIBLE` puede seguir existiendo como código en otros endpoints de Seguridad, pero no en el login.

### 3.2 Productos y Ofertas — base `{PRO}/api/v1` ✅ contrato real (scopes concedidos)

> Los siete scopes de Productos están **concedidos** a `modulo-chatbot` por Seguridad (consulta Q2 del 10/11); el token de servicio los incluye y G6 validó el flujo real. `productos:fisicos:leer` pertenece a **Despacho**, no al chatbot. El resumen por API está en §3.5.

| Endpoint | Uso | Scope requerido | Estado |
|---|---|---|---|
| `GET /productos?q=&categoriaId=&marcaId=&canal=CHATBOT&pagina=&tamanio=&precioMin=&precioMax=&orden=` (`orden`: `NOMBRE_ASC`, `NOMBRE_DESC`) | Búsqueda y listado del catálogo (no devuelve precio ni disponibilidad). No se envía `estado`: es un filtro de backoffice (A17) | `catalogo:leer` | ✅ Concedido (G7, 10/11) |
| `GET /productos/{productoId}?canal=CHATBOT` | Detalle de producto con variantes | `catalogo:leer` | ✅ Concedido (G7, 10/11) |
| `GET /categorias` | Catálogo de categorías | `catalogo:leer` | ✅ Concedido (G7, 10/11) |
| `GET /marcas` | Catálogo de marcas | `catalogo:leer` | ✅ Concedido (G7, 10/11) |
| `GET /precios?skus=&canal=&at=` | Precios por SKU/canal (`precio_regular`, `precio_oferta`, vigencia) | `precios:leer` | ✅ Concedido (G7, 10/11) |
| `GET /precios/skus/{sku}?canal=CHATBOT` | Precio de un SKU; sin `canal` Pricing devuelve el precio global | `precios:leer` | ✅ Concedido (G7, 10/11) |
| `GET /promociones?canal=CHATBOT&vigentes=true` (`canal` obligatorio) | Promociones vigentes | `promociones:leer` | ✅ Concedido (G7, 10/11) |
| `POST /promociones/evaluar` | Evaluación del carrito y cupones | `promociones:evaluar` | ✅ Concedido (G7, 10/11) |
| `POST /cupones/validar` | Validación de cupón sin consumir | `cupones:validar` | ✅ Concedido (G7, 10/11) |
| `GET /recomendaciones?productoId=&canal=CHATBOT` | Recomendaciones `CROSS_SELL`/`UPSELL` | `recomendaciones:leer` | ✅ Concedido (G7, 10/11) |
| `GET /inventario/disponibilidad/comercial?skus=A,B,C&canal=CHATBOT` (1 a 100 SKU) | Disponibilidad comercial: solo `sku` y `status` (`DISPONIBLE`, `STOCK_BAJO`, `AGOTADO`, `INDETERMINADO`); provisional (`D-INV-01`), no reserva stock. `INDETERMINADO` nunca se trata como `AGOTADO` | `inventario:disponibilidad:leer` | ✅ Concedido (G7, 10/11) |
| `POST /inventario/disponibilidad/comercial/verificar` `{channel_id: CHATBOT, fulfillment: {mode: ENVIO_DOMICILIO}, lines[{sku, quantity}]}` | Verificación comercial por cantidad: `items[{sku, requested_quantity, result, reason_code}]` con `result` ∈ `SUFICIENTE`, `INSUFICIENTE`, `INDETERMINADO`; siempre no vinculante (`binding=false`), sin reserva ni saldos. `fulfillment` es obligatorio; el chatbot no envía `fulfillment_ref` (A17 · D1). Contrato provisional (`D-INV-01`) | `inventario:disponibilidad:leer` | ✅ Concedido (G7, 10/11) |
| `POST /productos/datos-fisicos/consulta` | Datos físicos por SKU (lo usa Despacho) | `productos:fisicos:leer` | ✅ Concedido a `modulo-despacho`, no a `modulo-chatbot` |

🧩 **Alineación HTTP 0.5.0 (`integraciones/ALINEACION_CHATBOT.md` de Productos, 07/10/2026):** el BFF conserva camelCase internamente y su adaptador traduce al contrato publicado. Mapeo: `canal` → `channel_id`, `lineas[{sku,cantidad}]` → `lines[{sku,quantity,product_id?}]`, `cupon` → `coupon_code`, `customerRef` → `customer_ref`. `customer_ref` es el `sub` del token del **cliente** (nunca el del token de servicio) y `null` en anónimo; si el cupón limita usos por cliente, Productos responde `code: CUSTOMER_REF_REQUERIDO`. La ruta de disponibilidad es `/inventario/disponibilidad/comercial`, no `/inventario/disponibilidad`.

🧩 **Lo que Productos no entrega** (y las specs ya no asumen): cantidades de stock (solo los estados `DISPONIBLE`/`STOCK_BAJO`/`AGOTADO`/`INDETERMINADO` y la verificación por cantidad, sin saldos); precio y disponibilidad dentro de la búsqueda (se consultan aparte por SKU); filtros de talla, color y `soloOfertas`; orden por precio; beneficio, alcance y modalidad de cada promoción en `GET /promociones` (solo `promotion_id`, `name`, `status`, vigencia y `channels`); desglose por línea en `POST /promociones/evaluar` (devuelve un único `discount_amount`, un `promotion_id` y `reason`); el monto mínimo exacto de un cupón rechazado. Productos respondió el 15/10 (acuerdo A16) y comprometió ampliaciones para una etapa posterior (P1): filtros de variantes, orden por precio, resumen de promociones, desglose por línea y monto faltante; no se tratan como contrato vigente hasta que las publique en su OpenAPI.

🧩 **Cierre de compatibilidad del 20/10 (A17):** todas las llamadas a Productos llevan `Authorization: Bearer <token de servicio>` de `modulo-chatbot` (audiencia `api-productos`, con el scope de cada operación) y un `X-Correlation-Id` en formato UUID que se conserva durante todo el turno, el mismo en cada llamada del turno. El OpenAPI de Productos es la referencia de solicitudes, respuestas, validaciones y errores. Un resultado de lote incompleto, un SKU que no coincide exactamente, un estado desconocido o un payload incompatible no producen decisiones comerciales positivas y se distinguen de un `INDETERMINADO` válido (D2). `401`, `403`, `422`, `429` y `503` se tratan según su semántica y no se convierten en estados comerciales. Las respuestas de los adaptadores falsos (`MODULES_MODE=fake`) no son evidencia de inventario, precio ni promociones reales, y deben devolver la misma forma que el OpenAPI (sin SKU con sufijos inventados ni disponibilidad por defecto). Si falta el precio vigente, se muestra "Precio no disponible", nunca `S/ 0.00`.

🧩 Payloads reales del contrato: `product_id`, `category_id`/`categoria_id`, `name`, `description`, `images`, `channel_id`, `lines`, `quantity`, `coupon_code`, `customer_ref`, `precio_regular`, `precio_oferta`, `currency` y paginación con `items`/`tamanio`.

### 3.3 Ventas y Postventa — bases `{VEN}/api/v1` (M1 · F1, F2) y `{VEN}/api/v2` (M2 · F3, F4, F5, F6) ✅ contrato publicado (v1.3.0)
🧩 `api-contract.md` de Ventas pasó de 547 a 743 líneas el 23/09: agregó la subida de evidencia y los listados/consultas que faltaban de F3 y F6. M1 (pedidos) vive en `/api/v1`; M2 (postventa) vive en `/api/v2`.

| Endpoint | Uso | Referencia |
|---|---|---|
| `POST /api/v1/pedidos` (con `Idempotency-Key`) | Crear el pedido `CREADO` con el snapshot completo (`contacto`, `items`, `cupon`, `envio`, `pago`) | F1 §1.1 |
| `POST /api/v1/pedidos/{id}/pagos/notificacion` | Notificar el resultado del pago simulado (`APROBADO`/`RECHAZADO`); transiciona `CREADO → PAGADO`. Responde `{pedidoId, nuevoEstado, transaccionId, fechaTransicion}`: `PAGADO` confirma el pedido; `ANULADO` indica un pago tardío sobre un pedido anulado (el pago queda `CONFIRMADO` y Ventas solicita el reembolso) | F1 §1.2 |
| `GET /api/v1/pedidos/{id}` | Detalle, estado e historial. Con token del cliente (rol `CLIENTE`) solo devuelve pedidos propios. ✅ El outbox también lo lee con **token de servicio** (scope `ventas:pedidos:consultar`, confirmado; verificado el 2026-11-27 23:01 UTC, `X-Correlation-Id` `a7c3edba-94db-405f-85ff-316eed5f3957`: G7 concede el scope y G5 respondió 200 a la lectura con token de servicio; evidencia en specs #119 y actualización del contrato de G5 pedida en G5-Ventas-Postventas-Backend#85) solo para confirmar que un pedido ya está `ANULADO` tras un `409 PEDIDO_NO_ANULABLE`; el motivo de la anulación está en `historialEstados[estado=ANULADO].motivo` | F1 §1.3 |
| `GET /api/v1/pedidos/me?estado=&desde=&hasta=&page=&pageSize=` | ✅ **Cambio (12/10).** Listado de los pedidos del cliente autenticado, con **token del cliente** (rol `CLIENTE`, sin scope; identidad por `sub`, nunca `clienteId`). Paginación `page` (desde 1) y `pageSize` (1 a 50, por defecto 10); `desde` y `hasta` son fechas ISO `YYYY-MM-DD` opcionales que filtran por `fechaCreacion`. Responde `{items[{pedidoId, canal, estado, total, moneda, fechaCreacion}], total, page, pageSize}`. Reemplaza al listado `GET /api/v1/pedidos?clienteId=`, que ahora es solo del Gestor | F1 §1.4b |
| `POST /api/v1/pedidos/{id}/anulaciones` `{motivo: PAGO_NO_COMPLETADO, comentario}` | Anular un pedido `CREADO` o `PAGADO` sin intervención del Gestor; responde `200` directo (no `202`, porque ese motivo no pasa por autorización) | F2 §1.7 |
| `POST /api/v2/reclamos` | Registrar un reclamo del Libro de Reclamaciones, con plazo confirmado de **15 días hábiles**. Motivos aceptados (no existe `OTRO`): `INCUMPLIMIENTO_PLAZO_ENTREGA`, `PRODUCTO_DEFECTUOSO_O_INCORRECTO`, `COBRO_INDEBIDO_O_NO_RECONOCIDO`, `ATENCION_INADECUADA`, `INCUMPLIMIENTO_GARANTIA` | F6 §2.6 |
| `GET /api/v2/reclamos/{codigoSeguimiento}` | ✅ **Nuevo.** Detalle y `respuestaVisibleCliente` de un reclamo | F6 §2.7 |
| `GET /api/v2/reclamos/me?estado=&pagina=&tamano=` | ✅ **Cambio (12/10).** Listado de los reclamos del cliente autenticado, con **token del cliente** (rol `CLIENTE`, sin scope; identidad por `sub`, sin `clienteId` ni `documento`); estados reales `REGISTRADO \| EN_PROCESO \| ATENDIDO \| DERIVADO`. Reemplaza al listado por `clienteId`/`documento`, que ahora es solo del Gestor | F6 §2.10b |
| `PATCH /api/v2/reclamos/{id}/respuesta` | Solo lo usa el Gestor; el chatbot únicamente lee el resultado a través del detalle | F6 §2.9 |
| `POST /api/v2/devoluciones/evidencias/upload` | ✅ **Nuevo.** Sube la foto o PDF de evidencia (multipart, ≤ 5 MB) y devuelve `{tipo, url, nombreArchivoOriginal, tamanioBytes, fechaSubida}` — Ventas hostea el archivo, el chatbot no necesita bucket propio | F3 §2.1 |
| `POST /api/v2/devoluciones` | Registrar la solicitud de cambio o devolución. Plazo confirmado: **7 días naturales** desde la entrega | F3 §2.2 |
| `GET /api/v2/devoluciones/{id}` | Detalle del expediente; si la resolución fue `DEVOLUCION_DINERO` y ya se procesó, incluye `resolucion.reembolso{reembolsoId, estado, monto, moneda, transaccionPasarelaId, fechaEjecucion}` | F3 §2.3 |
| `GET /api/v2/devoluciones/me?estado=&tipo=&pagina=&tamano=` | ✅ **Cambio (12/10).** Listado de las solicitudes del cliente autenticado, con **token del cliente** (rol `CLIENTE`, sin scope; identidad por `sub`); con `estadoReembolso` resumido por fila y sin `clienteId` en la raíz. Reemplaza al listado por `clienteId`, que ahora es solo del Gestor | F3 §2.4b |
| `POST /api/v2/csat` `{pedidoId, clienteId, canal: "CHATBOT", puntuacion, comentario?}` | ✅ **Confirmado (12/10).** Calificación de la entrega (SPEC-24), con **token del cliente** (rol `CLIENTE`, no scope). Ventas valida el `sub` contra el dueño del `pedidoId`: `403` si no coincide; el BFF lo normaliza a `404 RECURSO_NO_ENCONTRADO` (anti-enumeración). Solo para pedidos `ENTREGADO` (`422 ORDER_NOT_DELIVERED`); `409 CSAT_ALREADY_SUBMITTED` si ya existe. `puntuacion` acepta 1 a 5, pero el acuerdo H-04 usa solo `1`, `3` y `5` | F5 §2.7 |
| `POST /api/v2/reembolsos` | Solo lo ejecuta Ventas (F4) a partir de un origen válido; el chatbot nunca lo llama | F4 §2.4 (referencia) |

Notas que siguen vigentes sobre este contrato:
- **Autenticación hacia Ventas (confirmada por Ventas el 12/10; actualizada el 2026-11-26).** Con **token de servicio** del canal: `POST /api/v1/pedidos` (`ventas:pedidos:crear`), `POST /api/v1/pedidos/{id}/anulaciones` (`ventas:pedidos:anular`) y `POST /api/v1/pedidos/{id}/pagos/notificacion` (`ventas:pagos:webhook`). Con **token del cliente** (rol `CLIENTE`): `POST /api/v2/devoluciones`, `POST /api/v2/reclamos`, la carga de evidencia, los tres `/me` y `POST /api/v2/csat`. G5 eligió la Opción A (token del cliente) para F3/F6 en su #67, así que `postventa:devoluciones:escribir` y `postventa:reclamos:escribir` **no se necesitan**; el scope `postventa:csat:escribir` **no existe** y no se solicita.
- **Lectura con token de servicio (confirmada; verificado el 2026-11-27 23:01 UTC, `X-Correlation-Id` `a7c3edba-94db-405f-85ff-316eed5f3957`: G7 concede el scope y G5 respondió 200 a la lectura con token de servicio; evidencia en specs #119 y actualización del contrato de G5 pedida en G5-Ventas-Postventas-Backend#85):** `GET /api/v1/pedidos/{id}` con el scope `ventas:pedidos:consultar`, concedido a `modulo-chatbot`. El texto publicado del contrato de Ventas (`ventas.yaml`, líneas 398-399 de los fixtures de contrato del backend) figura desactualizado: indica que el scope es para `modulo-postventa` y que un token de servicio de canal no tiene acceso. Si G5 respondiera `403`, la reconciliación de `409 PEDIDO_NO_ANULABLE` (SPEC-15) no se activa y el `409` se mantiene como fallo permanente. Ver también §3.5.
- **Detalles por identificador (confirmado por Ventas el 12/10):** `GET /api/v1/pedidos/{id}`, `GET /api/v2/reclamos/{codigoSeguimiento}` y `GET /api/v2/devoluciones/{id}` piden el token del cliente (rol `CLIENTE`), nunca el de servicio del canal; la única excepción, confirmada, es la lectura de reconciliación de `GET /api/v1/pedidos/{id}` descrita arriba (si G5 respondiera `403`, rige esta regla sin excepción). Ventas valida el `sub` contra el dueño del recurso en los tres.
- **Listado de pedidos:** `/pedidos/me` es un endpoint compartido entre canales y tiene formato reducido por acuerdo con Marketplace (H-03). Ventas recomienda pedir `GET /pedidos/{id}` por cada pedido cuando se necesiten miniaturas o dirección, en lugar de ampliar el listado.
- Los estados de pedido usan guion bajo y sin tildes: `EN_PREPARACION`, no "EN PREPARACIÓN".
- El formato de error de Ventas usa la clave `codigo` (no `code`); `VentasClient` lo normaliza al `code` interno del chatbot.
- Las reglas de `contacto.tipoDocumento`/`numeroDocumento` (DNI, RUC, CE, PASAPORTE) ya están en su propio contrato, idénticas a las de `SPEC-12` · Requisito 1.
- La base de datos del chatbot guarda los valores de enumeración en inglés (`EXCHANGE`, `MONEY_REFUND`, `IMAGE`); el adapter los traduce en ambos sentidos a los literales de Ventas (`CAMBIO`, `DEVOLUCION_DINERO`, `IMAGEN`). Ver [`modelo-datos.md`](modelo-datos.md).

Códigos esperados: `400` datos incompletos o inconsistentes, `403` el cliente no es dueño del pedido, `404` inexistente, `409` sin stock, transición inválida o pedido en un estado que no admite la operación.

### 3.4 Despacho y Entrega — base `{DES}/api/v1`
| Endpoint | Uso | Estado |
|---|---|---|
| `POST /api/v1/cotizaciones` con `Auth: service-token`, scope `cotizaciones:calcular`, audience `api-despacho` → `destino`, `lineas[]`, `coberturaDisponible`, `tipoCotizacion`, `nombreZona`, `costoEnvio`, `moneda`, `plazoEstimadoDiasHabiles`, `fechaEstimadaEntrega` | Cotización real del pedido | ✅ contrato y scope concedido a `modulo-chatbot` (Seguridad #31, cerrado); credenciales reales en Hito 4 |
| `GET /api/v1/seguimientos/pedidos/{idPedido}` con token de servicio, scope `seguimientos:leer` | Seguimiento del pedido; G2 envía cada hito con `estado`, `etiqueta` y `fecha`; el BFF agrega `completado` al exponerlo | ✅ contrato y scope concedido a `modulo-chatbot` (Seguridad #31, cerrado); credenciales reales en Hito 4 |

**Notas de integración**
- El canal ya no manda `pesoKg` ni `volumenM3`; el payload real usa `destino` y, si aplica, `lineas` con `sku` + `cantidad`.
- Los errores propios de Despacho son: `DESP_ERROR_DESTINO_REQUERIDO`, `DESP_ERROR_LINEAS_VACIAS`, `DESP_ERROR_CANTIDAD_INVALIDA`, `DESP_ERROR_PRODUCTO_NO_ENCONTRADO`, `DESP_ERROR_DATOS_FISICOS_INCOMPLETOS`, `DESP_ERROR_PRODUCTOS_NO_DISPONIBLE`, `DESP_ERROR_LIMITE_COTIZACION`.

### 3.5 Scopes de `modulo-chatbot` por API

| API | Scope | Estado |
|---|---|---|
| Seguridad | `tokens:introspeccion` | ✅ Concedido |
| Productos | `catalogo:leer`, `precios:leer`, `promociones:leer`, `promociones:evaluar`, `cupones:validar`, `recomendaciones:leer`, `inventario:disponibilidad:leer` | ✅ Concedidos (G7, 10/11) |
| Ventas | `ventas:pedidos:crear`, `ventas:pagos:webhook`, `ventas:pedidos:anular` | ✅ Concedidos (G7, 22/11) |
| Ventas | `ventas:pedidos:consultar` | ✅ Concedido por G7 a `modulo-chatbot` (lectura de reconciliación del outbox, SPEC-15); verificado el 2026-11-27 23:01 UTC, `X-Correlation-Id` `a7c3edba-94db-405f-85ff-316eed5f3957`: G7 concede el scope y G5 respondió 200 a la lectura con token de servicio; evidencia en specs #119 y actualización del contrato de G5 pedida en G5-Ventas-Postventas-Backend#85 |
| Postventa | `postventa:devoluciones:escribir`, `postventa:reclamos:escribir` | ❌ No necesarios: G5 eligió token del cliente para F3/F6 (Opción A, G5 #67) |
| Despacho | `cotizaciones:calcular`, `seguimientos:leer` | ✅ Concedidos |
| Productos / Despacho | `productos:fisicos:leer` | ✅ Concedido a `modulo-despacho`; el chatbot no lo usa |

El cliente sigue enviando `audience` al pedir el token, pero G7 lo ignora y deriva `aud` de los scopes concedidos (Seguridad #108). El token vigente incluye `api-despacho`, `api-productos`, `api-seguridad` y `api-ventas`.

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
| `ANULADO` | `CANCELADO` o — | Anulado el {fecha} (ver §4.1) |

### 4.1 Contrato de un pedido `ANULADO`

Ventas solo publica el motivo en `historialEstados[estado=ANULADO].motivo` (texto libre) y no tiene un objeto de reembolso para las anulaciones. El chatbot deriva los campos del detalle, el seguimiento y el chat:

| Campo | Regla |
|---|---|
| Etiqueta | "Anulado el {fecha}", con la fecha del último hito `ANULADO` del historial; si el historial no trae fecha, "Anulado". |
| `motivoAnulacion` | Solo si el `motivo` está en la lista conocida: `STOCK_NO_DISPONIBLE` y los códigos de `MotivoAnulacion` de Ventas (`PAGO_NO_COMPLETADO`, `ERROR_SELECCION_PRODUCTO`, `ARREPENTIMIENTO_COMPRA`, `SOLICITUD_CLIENTE`, `ERROR_DATOS_ENVIO` y `DUPLICADO`). Un motivo desconocido o de texto libre produce `null`. |
| `reembolso` | "Se procesará el reembolso al medio de pago original." solo con evidencia de pago (`pago.estado` `CONFIRMADO` o `PAGADO` en `historialEstados`); sin evidencia de pago es `null`. |
| Mensajes | Con motivo de stock y pago: "Tu pedido fue anulado por falta de stock. Se procesará el reembolso al medio de pago original."; con stock sin pago: "Tu pedido fue anulado por falta de stock."; con motivo desconocido: "Tu pedido fue anulado." |

El `historialEstados` crudo de Ventas no se expone. El contrato completo, con sus escenarios, está en `openspec/specs/consulta-estado-pedido/spec.md` (Scenario: Pedido anulado).

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
| A4 | ✅ Resuelto / retirado (03/11) | Seguridad / Despacho | Se retira la espera del rol `SERVICIO_INTEGRACION`: ese rol no existe. El servicio se identifica por `tipo: servicio` y `sub: modulo-chatbot`, y Despacho valida `aud` (`api-despacho`) y el scope (`seguimientos:leer`, `cotizaciones:calcular`). Los scopes `cotizaciones:calcular` y `seguimientos:leer` ya fueron concedidos por Seguridad #31; las credenciales reales llegan en Hito 4. | SPEC-18 |
| A5 | 🟡 En seguimiento (Seguridad #33) | Productos | El contrato real está definido en `api/openapi.yaml` y los payloads se alinearon. Seguridad aceptó registrar/conceder los siete scopes solicitados cuando el PO de Productos confirme que corresponden a su lista oficial; Productos ratificó esa lista el 15/10 (A16) y coordina el registro con Seguridad; hasta esa confirmación, siguen sin estar concedidos a `modulo-chatbot`. | SPEC-06 a SPEC-13 |
| A6 | ✅ Resuelto en el contrato real | Productos / Despacho | El canal ya no calcula ni envía peso/volumen; ahora Despacho recibe `destino` y `lineas`, y consulta datos físicos con Productos cuando hace falta. El chatbot no lleva `pesos_por_categoria.yaml` ni calcula peso localmente. | SPEC-12 |
| A7 | ✅ Resuelto (07/10) | Productos | Búsqueda por texto libre (`GET /productos?q=`) confirmada en `ALINEACION_CHATBOT.md`. Aclaración del 15/10: `q` no garantiza coincidencias en atributos ni variantes. | SPEC-06, SPEC-07 |
| A8 | ✅ Resuelto (actualizado 12/10) | Ventas | `api-contract.md` publicado: creación de pedido, notificación de pago (`POST /pagos/notificacion`) y listado por cliente, que desde el 12/10 es `GET /api/v1/pedidos/me` con el token del cliente. | SPEC-15, SPEC-17 |
| A9 | ✅ Resuelto | Ventas | Anulación de un pedido `CREADO`/`PAGADO` por `PAGO_NO_COMPLETADO` iniciada por el canal: `POST /pedidos/{id}/anulaciones`, responde `200` directo. | SPEC-15 |
| A10 | ✅ Resuelto (23/09) | Ventas | Publicaron los cuatro endpoints que faltaban: `GET /api/v2/reclamos/{codigoSeguimiento}` (detalle), `GET /api/v2/reclamos?documento=&clienteId=&estado=` (listado), `GET /api/v2/devoluciones?clienteId=&estado=&tipo=` (listado) y, dentro de `GET /api/v2/devoluciones/{id}`, un bloque anidado `resolucion.reembolso` con el estado del extorno. SPEC-19, SPEC-20, SPEC-21 y SPEC-22 ya no tienen ningún requisito bloqueado. | SPEC-19, SPEC-20, SPEC-21, SPEC-22 |
| A11 | ✅ Resuelto (02/10) | Despacho | Contrato confirmado para seguimiento por `idPedido`, con token de servicio y sin coordenadas: `GET /api/v1/seguimientos/pedidos/{idPedido}`; scope `seguimientos:leer` concedido en Seguridad #31. Pendiente operativo: credenciales reales en Hito 4. El rol `SERVICIO_INTEGRACION` (A4) quedó retirado el 03/11: no existe. | SPEC-18 |
| A12 | ✅ Resuelto (02/10) | Despacho / Seguridad | Cotización autenticada con token de servicio, `aud=api-despacho` y scope `cotizaciones:calcular`; scope concedido en Seguridad #31. Las credenciales reales se entregan en Hito 4. | SPEC-12 |
| A13 | ✅ Resuelto (23/09) | Ventas | Ventas hostea la evidencia ellos mismos: `POST /api/v2/devoluciones/evidencias/upload` (multipart, ≤ 5 MB, `image/jpeg`, `image/png`, `image/webp` o `application/pdf`) devuelve la URL que luego se manda en el `POST /devoluciones`. El chatbot **no necesita su propio bucket ni adaptador de almacenamiento para la evidencia** — solo un proxy del formulario hacia ese endpoint. (Aclaración posterior: las imágenes adjuntas al chat, SPEC-23, son otro flujo y sí usan un bucket privado propio de Supabase Storage.) | SPEC-21 |
| A14 | ✅ Resuelto (23/09) | Ventas | `contacto.tipoDocumento` y `contacto.numeroDocumento` son **siempre obligatorios** en la creación del pedido — no opcionales, se usan para emitir el comprobante y validar la entrega. Ventas confirmó por escrito las 4 expresiones regulares exactas (DNI, RUC con prefijo, CE, y **PASAPORTE**, que no estaba contemplado antes) y el código de error `400 DATO_INVALIDO` cuando no calzan. SPEC-12 · Requisito 1 ya tiene las reglas exactas. Aviso no urgente para otros canales: si Ventas exige el documento a todos, Marketplace y Retail probablemente necesiten las mismas reglas. | SPEC-12, SPEC-14, SPEC-15 |
| A15 | ✅ Resuelto (12/10) | Ventas | Respuestas en G3-Chatbot-specs #9: (1) `ventas:pagos:webhook` ya está concedido a `modulo-chatbot`; (2) `/pedidos/me`, `/devoluciones/me` y `/reclamos/me` se llaman con el token del cliente, sin scope, filtrando por `sub`; (3) `POST /api/v2/csat` también usa el token del cliente (`403` si el `sub` no es el dueño del pedido; el BFF lo normaliza a `404 RECURSO_NO_ENCONTRADO` para no revelar si existe), con puntuación `1`/`3`/`5` y comentario libre, y se muestra en el detalle del pedido entregado; (4) A8, A9, A13 y A14 coinciden con las specs vigentes; (5) los tres detalles por identificador también piden el token del cliente, y para miniaturas y dirección del listado de pedidos conviene pedir el detalle de cada pedido. Ventas documentará el acuerdo en `integraciones/ACUERDO_G3_CHATBOT.md` cuando enlacemos este cambio. | SPEC-15, SPEC-17, SPEC-19 a 22, SPEC-24 |
| A16 | ✅ Respondido (15/10) | Productos | Respuesta oficial en G6-Productos-Ofertas-docs #87, sobre el contrato candidato OpenAPI `0.6.0-rc.1` (estable no significa desplegado). Confirmado: las diez operaciones del chatbot más `GET /precios/skus/{sku}` (`combos` queda fuera); los siete scopes (concedidos por G7 el 10/11); cuatro estados de disponibilidad (con `INDETERMINADO`) y verificación por cantidad no vinculante; umbral global de `STOCK_BAJO` con ajuste por SKU; precio y stock separados de la búsqueda; consultas por lotes de hasta 100 SKU y sin endpoint masivo de detalle; `customer_ref` = `sub` del cliente. Comprometido para una etapa posterior (P1, aún no es contrato): filtros de talla y color, orden por precio, resumen de promociones, desglose por línea, monto faltante del cupón; matriz de errores y límites (B9, B10) sin cuota numérica. Sin fecha. **Nota 2026-11-27:** G6 publica hoy `0.7.0-rc.3`; la homologación formal debe confirmar la versión, el SHA y el entorno usados en la corrida real. Seguimiento: G6 Docs #99 y G6 Backend #27. | SPEC-06 a SPEC-13 |
| A17 | 🟡 Respondido por G3 (23/10) · homologación pendiente | Productos | Cierre de compatibilidad del 20/10 en G6-Productos-Ofertas-docs #87, sin reabrir A16. G3 consolidó A16 en las specs principales (archivo de `alinear-specs-con-productos`) y corrigió las referencias a cantidades. **D1 aceptado:** la verificación por cantidad envía siempre `fulfillment: {mode: ENVIO_DOMICILIO}`, sin `fulfillment_ref`, y su resultado es informativo. **D2 aceptado:** lotes incompletos, SKU ausentes o que no coinciden, estados desconocidos y payloads incompatibles son "disponibilidad no obtenida", distinta de `INDETERMINADO`, y nunca se tratan como `AGOTADO`. **D3 aceptado en principio:** la homologación se hará con `MODULES_MODE=http` (ya existe en el backend), separada de las pruebas con adaptadores falsos; el entorno donde corre lo define Mathias. Las correcciones de código se piden por issue en los repositorios de backend y frontend. Pendiente de G6: URL, versión, SHA y evidencia del entorno, y la matriz B9–B10. Seguimiento: G6 Docs #99 y G6 Backend #27. Los siete scopes y las credenciales ya están concedidos y en uso (Seguridad #108). | SPEC-06 a SPEC-13 |
| A18 | ✅ Evidencia entregada (2026-11-22) | Ventas (G5) | G5 publicó el contrato definitivo de postventa: cinco motivos de reclamo (`INCUMPLIMIENTO_PLAZO_ENTREGA`, `PRODUCTO_DEFECTUOSO_O_INCORRECTO`, `COBRO_INDEBIDO_O_NO_RECONOCIDO`, `ATENCION_INADECUADA`, `INCUMPLIMIENTO_GARANTIA`), sin `OTRO`; el cliente elige el más cercano y lo detalla. La corrida real usó los servicios directos M1/M2 porque el gateway devolvió challenge de Cloudflare y `429`. EV-01..EV-05 cubren los cinco motivos (`REC-2026-0009` a `REC-2026-0013`), EV-06/07 cubren CSAT `201`/`409` y `422`, 90201 se usó para el CSAT nuevo y la devolución `DEV-2026-0028`, y 90101/90102 ya estaban calificados (409) y sus devoluciones fuera de plazo (400 `PLAZO_VENCIDO`). Esos `409` y `400 PLAZO_VENCIDO` son **datos de prueba de G5, no fallos del canal**. Detalle y rutas BFF en §2.10. | SPEC-19, SPEC-21, SPEC-24 |
