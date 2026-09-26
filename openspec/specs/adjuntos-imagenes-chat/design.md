# Diseño: Adjuntos de imágenes en el chat

> Origen: SPEC-23 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Componente | Uso | Estado |
|---|---|---|
| Proveedor LLM (`gpt-6-luna`, OpenAI) vía `LLMProvider` | Interpretación de las imágenes como partes de contenido en base64 junto con el texto | ⚠️ Soporte de visión y costo por imagen sin verificar (pregunta abierta 1 de la spec) |
| Supabase Storage (bucket privado) vía `AttachmentStorage` | Guardar y leer la imagen normalizada y su miniatura; emitir URLs firmadas | 🟡 Propio del chatbot, sin contrato de otro módulo; el plan gratuito impone límites (pregunta abierta 5) |
| PostgreSQL (Supabase) | Tabla `adjunto` con las referencias | ⚠️ PostgreSQL 18 sin confirmar en Supabase (pregunta abierta 3) |
| Búsqueda de Productos (SPEC-06) | Se invoca con los criterios de texto que el LLM deduce de la imagen | ✅ Sin cambios de contrato |
| Ventas | **No se integra**: las imágenes del chat no se reenvían como evidencia (SPEC-21) | ✅ |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `AttachmentButton` (en `Composer`) | Botón "Adjuntar" que abre el selector de archivos (`accept="image/jpeg,image/png,image/webp"`); deshabilitado con 3 imágenes ya adjuntas. |
| `ImagePrivacyNotice` | Aviso de la primera carga con enlace a la política de privacidad y botón "Entendido, adjuntar"; recuerda la confirmación en el dispositivo (LocalStorage, con degradación si no está disponible). |
| `AttachmentPreviewList` | Miniaturas locales de las imágenes pendientes con barra de progreso, estado de error con "Reintentar" y botón "Quitar". |
| `validateImageFile` (dominio) | Valida tipo, tamaño (máx. 5 MB) y cantidad (máx. 3) antes de subir; no reemplaza la validación del backend. |
| `MessageAttachments` (en `MessageRenderer`) | Miniaturas de las imágenes de un mensaje con URL firmada; pide una URL nueva ante un error de carga (un reintento) y muestra "Imagen no disponible" si falla. |
| `ImageViewer` | Vista ampliada de una imagen dentro de la aplicación, con URL firmada nueva, cierre con teclado y texto alternativo. |
| Puerto `ChatbotApiPort` (ampliado) | `subirAdjunto`, `eliminarAdjunto`, `obtenerUrlAdjunto` y `enviarMensaje` con `adjuntoIds`. |
| `chatStore` (ampliado) | Adjuntos pendientes de la conversación activa, su estado (`SUBIENDO`, `LISTO`, `ERROR`) y la caché de URLs firmadas con su `expiraEn`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/chat/conversaciones/{id}/adjuntos` (`chatbot_router.py`) | Recibe una imagen (`multipart/form-data`), verifica la pertenencia de la conversación, aplica `RateLimiter` y delega en `AdjuntoService`. |
| `GestionarConversacionUseCase` (ampliado) | Cubre la carga, el envío y la eliminación de adjuntos y la emisión de URLs firmadas, con la misma regla de pertenencia por `cliente_id` o `chat_sid`. |
| `AdjuntoService` | Valida el archivo, invoca a `ImageProcessor`, guarda mediante `AttachmentStorage`, crea la fila `adjunto`, liga los adjuntos al mensaje y elimina los pendientes o huérfanos. |
| `ImageProcessor` | Determina el tipo por la firma binaria, rechaza contenido que no es una imagen válida, elimina EXIF y ubicación, re-codifica, acota las dimensiones y genera la miniatura. |
| Puerto `AttachmentStorage` (outbound) | `guardar(clave, bytes, mime)`, `leer(clave) -> bytes`, `eliminar(clave)` y `url_firmada(clave, ttl)`. Sin lectura pública. |
| `SupabaseAttachmentStorage` (adaptador outbound) | Implementa el puerto con un bucket privado de Supabase Storage; credenciales y nombre del bucket por variables de entorno. En pruebas se reemplaza por un adaptador en memoria. |
| `LLMProvider` (ampliado) | Acepta mensajes con **partes de contenido** (`TextoParte`, `ImagenParte {mime, base64}`) además del texto simple; declara si el modelo admite visión. `OpenAIProvider` las traduce al formato del proveedor. |
| `InterpretarYResponderUseCase` (ampliado) | Al armar el turno, lee desde `AttachmentStorage` las imágenes de los últimos 12 mensajes (máx. 6 más recientes), las codifica en base64 y las incluye como `ImagenParte`. Nunca pasa URLs. Registra tokens y costo por turno. |
| `SensitiveDataFilter` | Sin cambios: sigue actuando solo sobre el texto. Las imágenes quedan fuera de su alcance (riesgo residual documentado). |
| `DegradedMode` (ampliado) | Cubre `LLM_VISION_ENABLED=false`, el rechazo del contenido de imagen por el proveedor, el tiempo excedido y la imagen ilegible: responde el aviso de imagen no analizada y procesa el texto sin imágenes. |
| `RateLimiter` (ampliado) | Agrega el límite de 10 cargas de imagen por minuto por cliente o IP y el tope de 10 adjuntos pendientes por conversación. |
| Job de limpieza de adjuntos | Elimina los adjuntos `PENDIENTE` de más de 24 h y los archivos huérfanos del bucket; reintenta los borrados fallidos y los registra sin datos personales. Se ejecuta en el worker de tareas junto con los demás jobs. |
| Tabla `adjunto` | Ver más abajo y `modelo-datos.md`. |

### Endpoints propios

Siguen las convenciones de `docs/contratos-integracion.md` §2: prefijo `/api/v1`, JSON en `camelCase`, errores `application/problem+json` con `code`.

| Método | Ruta | Sesión | Descripción |
|---|---|---|---|
| POST | `/chat/conversaciones/{id}/adjuntos` | Opcional | Sube una imagen (`multipart/form-data`, campo `archivo`). Responde `201 {adjuntoId, mimeType, tamanioBytes, ancho, alto}`. Errores: `400 ADJUNTO_INVALIDO`, `404 RECURSO_NO_ENCONTRADO`, `422 LIMITE_ADJUNTOS`, `429 DEMASIADAS_SOLICITUDES`, `503 SERVICIO_NO_DISPONIBLE`. |
| DELETE | `/chat/conversaciones/{id}/adjuntos/{adjuntoId}` | Opcional | Quita un adjunto `PENDIENTE` y elimina sus archivos. Un adjunto `ENVIADO` no se puede quitar (`409`). |
| GET | `/chat/adjuntos/{adjuntoId}` | Opcional | Emite una URL firmada nueva `{urlMiniatura, urlImagen, expiraEn}` para un adjunto de una conversación del solicitante. |
| POST | `/chat/conversaciones/{id}/mensajes` | Opcional | Se amplía el cuerpo con `adjuntoIds` (máx. 3). El texto pasa a ser opcional si hay al menos un adjunto. Sigue respondiendo `202 {mensajeId}`. |
| GET | `/chat/conversaciones/{id}/mensajes` | Opcional* | Cada mensaje incluye `adjuntos[{adjuntoId, mimeType, ancho, alto, urlMiniatura, expiraEn}]` con URLs firmadas de corta vida. |

Códigos de error nuevos (para `contratos-integracion.md` §2.8):

| `code` | HTTP | Significado |
|---|---|---|
| `ADJUNTO_INVALIDO` | 400 | Archivo mayor a 5 MB, tipo no permitido, contenido que no es una imagen válida o dimensiones fuera de rango. |
| `LIMITE_ADJUNTOS` | 422 | Más de 3 adjuntos por mensaje o más de 10 pendientes por conversación. |

### Modelo de datos (resumen)

La tabla `adjunto` se define en `docs/modelo-datos.md` (tabla `adjunto`). Columnas:

| Columna | Descripción |
|---|---|
| `id` | Identificador del adjunto (`uuid`, el `adjuntoId` de la API). |
| `conversacion_id` | Conversación a la que pertenece desde la carga (FK a `conversacion`, `ON DELETE CASCADE`). Define la pertenencia por `cliente_id` o `chat_sid`. |
| `mensaje_id` | Mensaje al que queda ligado al enviarse (FK nullable a `mensaje`, `ON DELETE CASCADE`); es `NULL` mientras el estado es `PENDIENTE`. |
| `estado` | `PENDIENTE` (subido y sin enviar) o `ENVIADO` (ligado a un mensaje). |
| `storage_key` | Clave aleatoria del objeto de la imagen normalizada en el bucket privado. |
| `miniatura_key` | Clave del objeto de la miniatura. |
| `mime_type` | Tipo detectado por firma binaria: `image/jpeg`, `image/png` o `image/webp`. |
| `size_bytes` | Tamaño de la imagen guardada. |
| `width`, `height` | Dimensiones de la imagen guardada, en píxeles. |
| `creado_en`, `actualizado_en` | Fecha de carga (la usa el job de limpieza de pendientes de 24 h) y de la última modificación (ligado al mensaje). |

Reglas: un adjunto se liga a un único mensaje; la base guarda solo referencias, nunca los bytes; el nombre original del archivo no se guarda; un índice parcial por `creado_en` (estado `PENDIENTE`) sirve al job de limpieza, uno por `(conversacion_id, estado)` al tope de pendientes y a la pertenencia, y otro por `mensaje_id` al armar el historial. La definición completa está en `docs/modelo-datos.md`.

### Encaje en los casos de uso del núcleo

No se agrega un caso de uso nuevo: la carga, el envío y las URLs firmadas se agrupan en `GestionarConversacionUseCase` y la lectura de imágenes para el LLM en `InterpretarYResponderUseCase` (ver ADR-0018, aún en estado Propuesta).

## Desglose para issues

- [ ] `[BE]` Puerto `AttachmentStorage` y adaptador `SupabaseAttachmentStorage` (bucket privado, URLs firmadas) con un adaptador en memoria para pruebas
- [ ] `[BE]` `ImageProcessor`: firma binaria, limpieza de EXIF y ubicación, dimensiones máximas, re-codificación y miniatura
- [ ] `[BE]` Modelo `adjunto` y migración Alembic (referencias, estado y claves de almacenamiento)
- [ ] `[BE]` `AdjuntoService` y `POST`/`DELETE /chat/conversaciones/{id}/adjuntos` con pertenencia, límites y códigos de error
- [ ] `[BE]` `GET /chat/adjuntos/{adjuntoId}` y URLs firmadas en `GET /conversaciones/{id}/mensajes` (TTL configurable)
- [ ] `[BE]` `adjuntoIds` en `POST /conversaciones/{id}/mensajes`: validación, ligado al mensaje y texto opcional
- [ ] `[BE]` `LLMProvider` con partes de contenido multimodales (`TextoParte`, `ImagenParte`) y el indicador `LLM_VISION_ENABLED`
- [ ] `[BE]` `InterpretarYResponderUseCase`: lectura de imágenes desde el almacenamiento, base64, ventana de 12 mensajes y máximo de imágenes por turno
- [ ] `[BE]` Extensión de `DegradedMode` (sin visión, LLM caído, imagen ilegible) y del `RateLimiter` (cargas por minuto y pendientes)
- [ ] `[BE]` Job de limpieza de adjuntos pendientes y de archivos huérfanos
- [ ] `[BE]` Registro por turno de imágenes, tokens y costo sin contenido de imagen en los logs
- [ ] `[FE]` `AttachmentButton`, `AttachmentPreviewList` y `validateImageFile` con los límites de tipo, tamaño y cantidad
- [ ] `[FE]` `ImagePrivacyNotice` de la primera carga
- [ ] `[FE]` `MessageAttachments` e `ImageViewer` con renovación de URLs firmadas y marcador "Imagen no disponible"
- [ ] `[FE]` Ampliación de `ChatbotApiPort`, del adaptador Axios y de `chatStore` para adjuntos pendientes y caché de URLs
- [ ] `[INT]` Validar con el modelo `gpt-6-luna` real el soporte de visión, el formato de las partes de imagen y el costo en tokens por imagen
- [ ] `[INT]` Configurar el bucket privado de Supabase Storage y comprobar los límites del plan gratuito
- [ ] `[QA]` Pruebas de todos los escenarios (LLM y almacenamiento mockeados), incluida la carga de un archivo con extensión falsa, la limpieza de EXIF y la ventana de 12 mensajes
- [ ] `[QA]` Pruebas de seguridad: pertenencia de adjuntos entre clientes, expiración de URLs firmadas, ausencia de URLs y de base64 en los logs, y texto instruccional dentro de una imagen
- [ ] `[QA]` Pruebas del modo degradado con `LLM_VISION_ENABLED=false`, falla del LLM y falla del almacenamiento, verificando que el flujo de texto sigue activo
