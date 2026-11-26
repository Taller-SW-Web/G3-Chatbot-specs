# ADR-0028: Adjuntos del chat con almacenamiento externo privado, no disco local

## Estado

Aceptada

## Fecha

2026-11-21 (decisión del dueño, D2 de la [auditoría](../../auditoria-specs-2026-11.md))

## Contexto

- [ADR-0019](ADR-0019-imagenes-como-entrada-del-llm.md) ya decidió que las imágenes del chat se guardan en un bucket privado de Supabase Storage detrás del puerto `AttachmentStorage`, y que el LLM las recibe en base64, nunca por URL.
- La auditoría 2026-11 encontró que el modelo `attachment` existe pero no hay endpoints de carga, borrado ni URL firmada; `POST /mensajes` devuelve `501` si llega `adjuntoIds`.
- El dueño decidió el alcance completo (D2, 2026-11-21): storage, límites, EXIF, miniaturas, URL firmada, limpieza y `adjuntoIds`.
- El backend se despliega en contenedores (Railway) y el frontend en Vercel; no hay un volumen compartido persistente entre réplicas.

## Decisión

1. **Almacenamiento externo gestionado.** El destino de producción es Supabase Storage (bucket privado) a través del puerto `AttachmentStorage` (`guardar`, `leer`, `eliminar`, `url_firmada`). **El disco local del backend no es aceptable en producción**: un contenedor efímero perdería los archivos al reiniciar y no los compartiría entre réplicas. El adaptador se elige con `ATTACHMENT_STORAGE=local|supabase`: `local` (`LocalAttachmentStorage`) solo sirve para desarrollo y pruebas; `supabase` es el adaptador de producción. En producción el backend NO DEBE (SHALL NOT) arrancar con `local`.
2. **La base guarda solo referencias.** La tabla `attachment` conserva `storage_key`, `thumbnail_key`, tipo, tamaño, dimensiones y estado; nunca los bytes. El nombre original del archivo no se guarda.
3. **Ciclo de vida `PENDING` → `SENT`.** La carga crea el adjunto en `PENDING` sin mensaje; el `POST` de mensajes lo liga a un único mensaje y lo pasa a `SENT`. Un adjunto `SENT` no se puede quitar; uno `PENDING` sí, y el borrado elimina sus dos objetos.
4. **Validación y minimización.** El backend determina el tipo por firma binaria, rechaza contenido que no sea JPG/PNG/WebP, elimina EXIF y ubicación, re-codifica, acota dimensiones y genera una miniatura. Los límites son 3 imágenes por mensaje y 5 MB por imagen.
5. **Acceso privado.** El historial y la vista ampliada usan URLs firmadas de corta vida (5 minutos por defecto, configurables) emitidas por el backend tras verificar la pertenencia por `customer_id` o `chat_sid`. No hay URL pública ni se envía una URL al LLM.
6. **`adjuntoIds` en el mensaje.** `POST /chat/conversaciones/{id}/mensajes` acepta hasta 3 `adjuntoIds`, exige que pertenezcan a la conversación y estén `PENDING`, y responde `200 text/event-stream` como un mensaje de texto (ADR-0021).
7. **Limpieza.** Un job elimina adjuntos `PENDING` de más de 24 h y reconcilia archivos huérfanos del bucket; el borrado de una conversación elimina sus filas en cascada y el job borra los objetos. Un fallo de borrado se reintenta y se registra sin bloquear la conversación.
8. **Límites de uso.** 10 cargas por minuto por cliente o IP, 10 adjuntos pendientes por conversación y el límite general de mensajes de SPEC-05.

**Límites:** no se usa el almacenamiento de Ventas (la evidencia de devolución sigue siendo de SPEC-21), no se aceptan PDF en el chat, no hay búsqueda por similitud visual y el plazo de retención de los adjuntos sigue sin decidirse.

## Estado de implementación (2026-11-26)

> **El adaptador existe y producción ejecuta `development`.** `SupabaseAttachmentStorage`, el selector `ATTACHMENT_STORAGE=local|supabase` (`build_attachment_storage`) y el listado de objetos que usa la reconciliación de huérfanos están mergeados en `development` (backend PR #144, commit `e4faadf`). Desde el 2026-11-26 `main` es un placeholder de un commit con solo `README.md`; producción se despliega desde `development` ([ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md), enmienda del 2026-11-26). No hay promoción a `main`.
>
> **Lo que falta para cumplir este ADR:**
>
> 1. Crear el bucket privado y configurar `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `ATTACHMENT_BUCKET`, `ATTACHMENT_PUBLIC_BASE_URL` y `ATTACHMENT_SIGNING_SECRET` en la API y en el worker. El orden, la verificación y el rollback están en el [runbook de adjuntos en Supabase](../../operacion/adjuntos-supabase.md).
> 2. Cerrar el fail-closed de `APP_ENV=production` con `ATTACHMENT_STORAGE=local` ([backend#185](https://github.com/Taller-SW-Web/G3-Chatbot-backend/issues/185)).
> 3. Decidir si los archivos que hoy están en el volumen de Railway se migran al bucket o se aceptan como perdidos, y definir la política de backup de los objetos.
>
> **Riesgo mientras tanto:** el entorno de producción declara `ATTACHMENT_STORAGE=local` sobre un volumen de Railway; si el servicio se recrea, las imágenes del chat y las capturas de bugs (SPEC-24) se pierden, mientras las filas `attachment` y `feedback_suggestion.screenshot_key` siguen apuntando a claves inexistentes; la interfaz las muestra como "Imagen no disponible". El volumen no sustituye un storage externo: no ofrece backup propio ni lectura compartida entre réplicas.
>
> **Requisito vigente:** producción NO DEBE (SHALL NOT) arrancar con `local`. En el código de `development` el arranque solo registra un aviso (`BE/src/infrastructure/main.py:38-43`) en vez de abortar; la prohibición se aplica por configuración y la brecha de código se cierra en #185.
>
> **Criterio de cierre:** `ATTACHMENT_STORAGE=supabase` en el entorno de producción (`development`), con el bucket privado y las variables del runbook configuradas en la API y el worker, verificado con una carga, un reinicio del servicio y una lectura posterior.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Disco local del backend (`/uploads`) | El contenedor es efímero y no comparte archivos entre réplicas; se pierden al reiniciar y no hay backup ni URL firmada |
| Guardar los bytes en PostgreSQL | Hincha la base, complica backups y no aporta las funciones de storage (TTL, URLs firmadas, miniaturas) |
| Reutilizar el almacenamiento de Ventas | Mezcla imágenes de conversación con evidencia de devoluciones y envía a otro módulo imágenes que el cliente no presentó como evidencia |
| Bucket público | Expone imágenes privadas sin control de acceso; la spec exige pertenencia y URLs firmadas |
| API de archivos del proveedor LLM | Deja la imagen bajo la retención del proveedor y acopla el canal a un solo modelo (ADR-0005/ADR-0019) |

## Consecuencias

**Positivas**

- Los archivos sobreviven a reinicios y se comparten entre réplicas.
- El puerto `AttachmentStorage` permite cambiar de proveedor sin tocar casos de uso.
- La base queda liviana y las imágenes se sirven con permisos verificados.

**Negativas y riesgos aceptados**

- Dependencia del plan gratuito de Supabase (almacenamiento, ancho de banda y límites), ya registrada en ADR-0019.
- Credenciales de Storage en variables de entorno del backend; nunca en el frontend.
- El job de limpieza y la reconciliación bucket/tabla añaden complejidad operativa.
- La retención sigue sin plazo definido; mientras tanto, los archivos se conservan y el riesgo de privacidad se documenta en `privacidad.md`.
- La carga añade latencia (p95 ≤ 3 s) y el turno con imágenes es más caro; las metas son provisionales hasta medirlas con el modelo real.

## Referencias

- [`adjuntos-imagenes-chat/spec.md`](../../../openspec/specs/adjuntos-imagenes-chat/spec.md) y [`design.md`](../../../openspec/specs/adjuntos-imagenes-chat/design.md)
- [`adjuntos-supabase.md`](../../operacion/adjuntos-supabase.md) — runbook de bucket, variables, despliegue, verificación y rollback
- [`modelo-datos.md`](../../modelo-datos.md) — tabla `attachment`
- [ADR-0019](ADR-0019-imagenes-como-entrada-del-llm.md) — decisión original de imágenes y `AttachmentStorage`
- [ADR-0021](ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md) — `200 text/event-stream`
- [`auditoria-specs-2026-11.md`](../../auditoria-specs-2026-11.md) §4, D2
- [`contratos-integracion.md`](../../contratos-integracion.md) §2.1.1 (incluye `GET /chat/adjuntos/archivo`)
