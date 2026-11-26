# Runbook: adjuntos del chat en Supabase Storage

> **Estado verificado el 2026-11-26.** Este documento describe cómo llevar los adjuntos de SPEC-23 a un
> bucket privado de Supabase Storage y cómo volver atrás. **No afirma que producción ya use Supabase:**
> el adaptador está en `development` y producción ejecuta esa rama, pero la configuración sigue con
> `ATTACHMENT_STORAGE=local` sobre un volumen de Railway. `main` es un placeholder de un commit con solo
> `README.md`; no se promueve a `main`. Las decisiones que aún no están tomadas se marcan como pendientes, sin plazos.
>
> Alcance: operación del almacenamiento de adjuntos (SPEC-23) y de las capturas de bugs de SPEC-24.
> No cubre la base de datos, el LLM ni el resto del despliegue.

## 1. Estado de partida

| Elemento | Estado (2026-11-26) |
|---|---|
| Adaptador `SupabaseAttachmentStorage` | ✅ En `development` (backend PR #144, commit `e4faadf`), con `build_attachment_storage` y el listado de objetos que usa la reconciliación de huérfanos |
| Selector `ATTACHMENT_STORAGE=local\|supabase` | ✅ En `development`; el valor por defecto sigue siendo `local` |
| Fail-closed en producción | ✅ Desde backend #198: `APP_ENV=production` + `local` aborta salvo `ALLOW_LOCAL_ATTACHMENTS=true` |
| Rama de producción | `development` ([ADR-0020](../arquitectura/adr/ADR-0020-despliegue-en-railway-vercel-y-supabase.md), enmienda del 2026-11-26); contiene `src/shared/infrastructure/storage/` |
| `main` | Placeholder de un commit con solo `README.md`; no es rama de despliegue ni se promueve desde `development` |
| Bucket privado | 🟡 No creado ni documentado |
| Variables de storage en Railway | 🟡 Sin configurar; solo consta `ATTACHMENT_STORAGE=local` sobre un volumen |
| Migración de los archivos locales | 🟡 Sin decisión ni script; el volumen puede haberse perdido al recrear el servicio |
| Retención de adjuntos enviados | 🟡 Sin plazo definido (SPEC-23, pregunta abierta 2) |
| Backup de los objetos del bucket | 🟡 Sin política; los backups de Supabase cubren PostgreSQL, no Storage |

**Antes de empezar, decidir:**

1. Si los archivos que hoy están en el volumen se migran al bucket o se aceptan como perdidos (§9).
2. Quién tiene acceso al proyecto de Supabase y al entorno de Railway (credenciales, §3).
3. Qué commit de `development` está desplegado en producción y si API y worker comparten el mismo
   commit (§4, paso 0). `main` no es una rama de despliegue.

## 2. Cómo funciona el almacenamiento

- El puerto `AttachmentStorage` (`guardar`, `leer`, `eliminar`, `url_firmada`, `verificar_firma`,
  `listar_claves`) elige adaptador al arrancar: `local` o `supabase` (`BE/src/shared/infrastructure/storage/factory.py`).
- `SupabaseAttachmentStorage` usa la API de Storage con la clave de servicio: escribe en
  `object/{bucket}/{key}` con `x-upsert: true`, lee de `object/authenticated/...`, borra en
  `object/...` y lista en `object/list/{bucket}`. El bucket **nunca** se hace público.
- Las URLs firmadas **no** las emite Supabase: las firma la API con HMAC-SHA256 sobre `clave:exp` y
  apuntan a `GET /api/v1/chat/adjuntos/archivo`, que verifica la firma y transmite el objeto. El mismo
  mecanismo sirve para `local` y para `supabase` (`BE/src/shared/infrastructure/storage/signed_urls.py`).
- Las claves son `attachments/<hex>.<ext>` (imagen) y `attachments/<hex>_thumb.<ext>` (miniatura). Las
  capturas de bugs de SPEC-24 viven en el mismo bucket bajo `feedback/`.
- La API y el worker necesitan la misma configuración: la API escribe y firma; el worker ejecuta la
  limpieza de pendientes y de huérfanos. Si hay varias réplicas de la API, todas necesitan el mismo
  `ATTACHMENT_SIGNING_SECRET` para validar las URLs que emitió otra réplica.

## 3. Prerrequisitos

| Recurso | Quién lo provee | Dónde vive |
|---|---|---|
| Proyecto de Supabase con Storage habilitado | Dueño del proyecto | Consola de Supabase |
| `SUPABASE_URL` del proyecto | Dueño del proyecto | Configuración de Railway |
| `SUPABASE_SERVICE_KEY` (clave de servicio) | Dueño del proyecto | **Vault del equipo**; nunca en el repositorio ni en el frontend |
| `ATTACHMENT_SIGNING_SECRET` | Equipo de plataforma | **Vault del equipo**; uno por entorno |
| Acceso al entorno de Railway (API y worker) | Owner de Railway | Consola de Railway |
| Acceso al volumen de Railway, solo si se migra | Owner de Railway | Shell del servicio o copia del volumen |

> La clave de servicio **omite RLS**: cualquiera que la tenga puede leer y borrar todo el proyecto. No
> se expone en el navegador, no se registra en logs y se rota si se filtra.

## 4. Paso 0 — Verificar la rama y el entorno actual

Antes de tocar variables:

- [ ] Confirmar en Railway a qué rama está conectado el servicio de producción y si hay uno o dos
      servicios (API y worker). La topología de [ADR-0020](../arquitectura/adr/ADR-0020-despliegue-en-railway-vercel-y-supabase.md)
      separa el worker; el estado del 2026-11-24 registra un solo entorno y un solo servicio.
- [ ] Confirmar que el código desplegado contiene el adaptador. En el repositorio de backend:
      `git ls-tree -r --name-only origin/development -- src/shared/infrastructure/storage` (devuelve
      `factory.py`, `local_attachment_storage.py` y `supabase_attachment_storage.py`). Producción
      ejecuta `development`; `main` es un placeholder sin código.
- [ ] Revisar las variables actuales: `ATTACHMENT_STORAGE`, `ATTACHMENT_STORAGE_PATH`, `APP_ENV`,
      `OUTBOX_WORKER_ENABLED` y las URLs públicas.
- [ ] Anotar el volumen actual y su punto de montaje (`ATTACHMENT_STORAGE_PATH`, por defecto
      `var/attachments`) si se va a migrar.

Si el código desplegado no lee `ATTACHMENT_STORAGE`, el servicio no está ejecutando `development`:
primero hay que corregir la rama de despliegue y verificar el commit, no configurar `supabase`.

## 5. Paso 1 — Crear el bucket privado (requiere credenciales)

1. En Supabase → **Storage** → **New bucket**, crear `chat-attachments` (o el nombre que se use en
   `ATTACHMENT_BUCKET`).
2. Dejar **Public bucket desactivado**. No crear políticas de lectura pública: el backend accede con
   la clave de servicio y el usuario final solo ve URLs firmadas de la API.
3. Comprobar que la ruta pública no entrega objetos:
   `https://<project-ref>.supabase.co/storage/v1/object/public/chat-attachments/<clave>` debe fallar
   (400/404), nunca devolver la imagen.
4. Anotar la URL base del proyecto, sin `/storage/v1`: `https://<project-ref>.supabase.co`. El
   adaptador agrega `/storage/v1`.
5. Revisar los límites del plan gratuito (almacenamiento y ancho de banda) contra el volumen esperado
   de imágenes; es la pregunta abierta 5 de SPEC-23.

No hace falta crear carpetas: el adaptador crea `attachments/` y `feedback/` al escribir la primera
clave.

## 6. Paso 2 — Configurar las variables

Configurar **a la vez** en la API y en el worker. La aplicación valida al arrancar y falla si
`ATTACHMENT_STORAGE=supabase` sin URL y clave, o si en producción `ATTACHMENT_PUBLIC_BASE_URL` apunta a
`localhost`.

| Variable | Valor | ¿Secreta? | Notas |
|---|---|---|---|
| `ATTACHMENT_STORAGE` | `supabase` | No | `local` sigue siendo el valor por defecto del código, pero en producción aborta el arranque salvo la excepción |
| `ALLOW_LOCAL_ATTACHMENTS` | `false` | No | Solo excepción del PO para arrancar producción con `local`; no usar por defecto |
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` | No | Sin `/storage/v1` ni barra final |
| `SUPABASE_SERVICE_KEY` | Clave de servicio del proyecto | **Sí** | Vault; solo backend; omitir RLS |
| `ATTACHMENT_BUCKET` | `chat-attachments` | No | Debe coincidir con el bucket creado |
| `ATTACHMENT_PUBLIC_BASE_URL` | `https://<host-público>/api/v1` | No | Base de las URLs firmadas; en producción no puede ser `localhost`. Si hay gateway, debe ser la URL pública que enruta al backend |
| `ATTACHMENT_SIGNING_SECRET` | Cadena aleatoria larga | **Sí** | Obligatoria en producción; la misma en API, worker y réplicas. Rotarla invalida las URLs vivas (TTL de 5 min) |
| `ATTACHMENT_SIGNED_URL_TTL_SECONDS` | `300` | No | Opcional; TTL de las URLs firmadas |
| `ATTACHMENT_STORAGE_TIMEOUT_SECONDS` | `10` | No | Opcional; timeout de las llamadas a Storage |
| `ATTACHMENT_MAX_IMAGES_PER_TURN` | `6` | No | Opcional; costo del LLM |
| `ATTACHMENT_CLEANUP_INTERVAL_SECONDS` | `3600` | No | Opcional; frecuencia del job de limpieza en el worker |
| `ATTACHMENT_STORAGE_PATH` | — | No | Solo aplica a `local`; se ignora con `supabase` |

> Si `ATTACHMENT_STORAGE=supabase` está puesto pero falta `SUPABASE_URL` o `SUPABASE_SERVICE_KEY`, el
> proceso no arranca (`ValueError: ATTACHMENT_STORAGE=supabase requires SUPABASE_URL and
> SUPABASE_SERVICE_KEY`). Si en producción falta `ATTACHMENT_SIGNING_SECRET`, tampoco arranca por la
> validación de ajustes inseguros.

## 7. Paso 3 — Orden de despliegue

1. **Verificar el código desplegado.** Confirmar que producción ejecuta un commit de `development` que
   contiene `src/shared/infrastructure/storage/` y que el arranque no falla. `main` no es una rama de
   despliegue. Si el servicio usa migraciones de Alembic, deben terminar antes de la API.
2. **Configurar las variables del §6** en la API y en el worker, en un solo cambio. No configurar
   `ATTACHMENT_STORAGE=supabase` en un servicio y `local` en el otro: la API escribiría en Supabase y el
   worker buscaría huérfanos en el disco (o al revés).
3. **Reiniciar ambos servicios.** Un reinicio de Railway basta; no hace falta reconstruir la imagen.
4. **Revisar los logs de arranque:**
   - No debe aparecer `ATTACHMENT_STORAGE=local in production: uploads sit on the ephemeral container disk...`.
   - No debe aparecer `Refusing to start with APP_ENV=production and unsafe settings...`.
   - El worker debe registrar `Attachment cleanup started (every 3600s)`.
5. Si el arranque falla, corregir la variable faltante y reiniciar. No continuar con la verificación
   hasta que ambos procesos estén sanos.

> **Por qué primero el código y después las variables:** el adaptador ya está en `development` y
> producción ejecuta esa rama; el paso 1 solo confirma el commit desplegado. Poner `supabase` antes de
> verificar el código daría una falsa sensación de avance si el servicio estuviera en otra rama.

## 8. Paso 4 — Verificación post-despliegue

Requiere una conversación real (token de sesión o cookie `chat_sid`) y una imagen JPG/PNG/WebP de menos
de 5 MB. Los ejemplos usan `curl`; sustituir los marcadores.

```bash
API="https://<host-público>/api/v1"
TOKEN="<access-token>"
CONV="<conversacion-id>"
ADJUNTO="<adjunto-id>"
```

### 8.1 Subir

```bash
curl -sS -X POST "$API/chat/conversaciones/$CONV/adjuntos" \
  -H "Authorization: Bearer $TOKEN" \
  -F "archivo=@foto.png;type=image/png"
```

- [ ] Responde `201 {adjuntoId, mimeType, tamanioBytes, ancho, alto}`.
- [ ] En la tabla `attachment` aparece la fila en `PENDING` con `storage_key` y `thumbnail_key`.
- [ ] En el bucket aparecen los dos objetos bajo `attachments/`, con el mismo nombre que las claves.
- [ ] Si se usa una conversación anónima, repetir con `-b "chat_sid=<sid>"` en lugar del token.

Si responde `503 SERVICIO_NO_DISPONIBLE`, revisar en este orden: claves del §6, nombre del bucket,
conectividad desde Railway a `SUPABASE_URL` y logs del backend (`Attachment storage failed: ...` no
incluye la clave ni la URL).

### 8.2 Leer

```bash
curl -sS "$API/chat/adjuntos/$ADJUNTO" -H "Authorization: Bearer $TOKEN"
```

- [ ] Devuelve `{urlMiniatura, urlImagen, expiraEn}` con URLs hacia
      `.../chat/adjuntos/archivo?clave=...&exp=...&sig=...`.
- [ ] `curl -sS -D - -o /tmp/foto.png "<urlImagen>"` responde `200`, `Content-Type: image/png` y
      `Cache-Control: private, max-age=60`; el archivo abre y coincide con la imagen subida.
- [ ] Una URL con la firma alterada responde `403 FIRMA_INVALIDA`.
- [ ] Una URL expirada (o `exp` pasado) responde `403 FIRMA_INVALIDA`.
- [ ] La ruta pública del bucket (§5.3) sigue fallando.

### 8.3 Reiniciar y volver a leer

1. Reiniciar el servicio de la API desde Railway (y el worker, si es otro servicio).
2. Pedir una **URL firmada nueva** con `GET /chat/adjuntos/{adjuntoId}` (la anterior puede haber
   caducado) y abrirla.
3. [ ] La imagen sigue disponible tras el reinicio. Un reinicio normal conserva el volumen, así que
       esta prueba confirma que la lectura no depende de la memoria del proceso; la prueba de que los
       bytes están fuera del contenedor es que el objeto exista en el bucket (§8.1) y que la lectura
       funcione con el volumen desmontado en staging.
4. [ ] Enviar el mensaje con `adjuntoIds` y confirmar que el adjunto pasa a `SENT` y que la miniatura
       se ve en el historial tras recargar la conversación.
5. [ ] Revisar que los logs del turno no contienen la clave, la URL firmada, el base64 ni el nombre
       original del archivo.

## 9. Paso 5 — Migración o pérdida de los archivos locales

Contexto: los archivos actuales viven en el volumen de Railway, en las mismas claves relativas que
usaría el bucket (`attachments/...` y `feedback/...`). La base guarda esas claves exactas. No existe
un script de migración en el repositorio.

| Opción | Qué implica | Cuándo tiene sentido |
|---|---|---|
| **A. Aceptar la pérdida** | No se copia nada. Las imágenes antiguas quedan como "Imagen no disponible"; las filas `SENT` no se borran. No hay que tocar la base | Si el volumen está vacío, si los archivos ya se perdieron en una recreación o si su valor es bajo |
| **B. Migrar antes de activar Supabase** | Copiar cada objeto conservando su clave, verificar y después poner `ATTACHMENT_STORAGE=supabase` | Si el volumen todavía tiene archivos y se quiere conservar el historial |
| **C. Migrar después de activar Supabase** | La API ya no lee el volumen; el script debe acceder al volumen por fuera de la aplicación y copiar con la API de Storage | Solo si ya se activó Supabase y el volumen sigue disponible |

**Procedimiento de la opción B (requiere credenciales y un script de una sola ejecución):**

1. **Inventariar el volumen.** Contar archivos bajo `<ATTACHMENT_STORAGE_PATH>/attachments/` y
   `<ATTACHMENT_STORAGE_PATH>/feedback/`. Ignorar los `.tmp`.
2. **Inventariar la base.** Ejecutar consultas de solo lectura:

   ```sql
   SELECT count(*) FILTER (WHERE storage_key IS NOT NULL)   AS imagenes,
          count(*) FILTER (WHERE thumbnail_key IS NOT NULL) AS miniaturas
   FROM attachment;

   SELECT count(*) FILTER (WHERE screenshot_key IS NOT NULL) AS capturas
   FROM feedback_suggestion;
   ```

   Los conteos deben cuadrar con los archivos (una imagen y una miniatura por adjunto; una captura por
   sugerencia con bug). Si no cuadran, no migrar todavía: primero explicar la diferencia.
3. **Copiar sin transformar.** Subir cada archivo a `chat-attachments/<misma ruta relativa>` con la API
   de Storage y la clave de servicio, con `Content-Type` derivado de la extensión y `x-upsert: true`
   para que sea idempotente. No re-procesar imágenes ni renombrar claves: la base apunta a esas rutas.
4. **Verificar.** Repetir los conteos sobre el bucket; abrir al menos la imagen más antigua y la más
   reciente con una URL firmada (se puede emitir desde la API con el adjunto correspondiente).
5. **Activar Supabase** (§6 y §7) y repetir la verificación del §8.

**Precauciones:**

- El job de huérfanos solo borra claves bajo `attachments/`; `feedback/` se ignora. Si se migra solo
  `attachments/`, las capturas de bugs quedan inaccesibles pero no se borran.
- No borrar el volumen ni el bucket durante la transición: son las dos únicas copias.
- La migración no cambia la retención ni la privacidad; solo mueve bytes.

**Decisión pendiente:** A o B; C solo aplica si Supabase ya se activó y el volumen sigue disponible. No se fija plazo; se registra en el PR o en el seguimiento del hito.

## 10. Paso 6 — Rollback a `local`

Usar solo como contención ante una caída de Supabase, una clave comprometida o una migración fallida.
No es un estado aceptable en producción (ADR-0028).

1. Poner `ATTACHMENT_STORAGE=local` en la API y el worker, con `ATTACHMENT_STORAGE_PATH` apuntando a un
   volumen montado y persistente.
2. Reiniciar ambos servicios con `ALLOW_LOCAL_ATTACHMENTS=true` (la excepción del PO). Sin ese flag,
   producción aborta el arranque por el fail-closed de backend #198. Se acepta solo durante la ventana
   del incidente.
3. Las cargas nuevas van al disco. Las imágenes subidas mientras Supabase estuvo activo siguen en el
   bucket: la API no las encuentra en el disco y las muestra como "Imagen no disponible" hasta volver a
   `supabase`.
4. **No borrar el bucket** durante el rollback: es la única copia de esas imágenes.
5. Resolver la causa y volver a `supabase` (§6 y §7). Si durante la ventana se subieron imágenes a
   `local` que se quieren conservar, aplicar la migración del §9 antes de volver.
6. El rollback no protege de la pérdida por recreación del servicio: si el volumen no es persistente,
   las imágenes locales se pierden igual.

## 11. Limpieza, retención y riesgos abiertos

- **Pendientes sin enviar:** el worker borra los adjuntos `PENDING` de más de 24 h y sus dos objetos.
  Frecuencia: `ATTACHMENT_CLEANUP_INTERVAL_SECONDS` (3600 s por defecto), con
  `OUTBOX_WORKER_ENABLED=true`.
- **Huérfanos:** cada pasada lista el bucket y elimina las claves `attachments/` sin fila. Con el
  adaptador local listaba el disco; con Supabase lista el bucket, por lo que un fallo del listado se
  registra y se omiten los borrados de huérfanos de esa pasada.
- **Enviados:** no hay plazo de retención definido (SPEC-23, pregunta abierta 2). Mientras tanto, los
  archivos se conservan.
- **Backup:** los backups de Supabase cubren PostgreSQL, no los objetos de Storage. No hay política de
  backup del bucket; queda como decisión pendiente.
- **Cupo:** el plan gratuito puede agotar almacenamiento o ancho de banda; las imágenes se normalizan a
  2048 px y se limita el tamaño por imagen, pero no hay alerta de cupo.
- **Guarda de arranque:** desde backend #198, `APP_ENV=production` con `ATTACHMENT_STORAGE=local`
  **aborta el arranque** (fail-closed). La única excepción es `ALLOW_LOCAL_ATTACHMENTS=true`, aceptada
  explícitamente por el PO; en ese caso arranca con un WARNING y los adjuntos siguen siendo efímeros.
  Ver [ADR-0028](../arquitectura/adr/ADR-0028-adjuntos-almacenamiento-externo-privado.md).
- **Secretos:** rotar `SUPABASE_SERVICE_KEY` si se filtra; rotar `ATTACHMENT_SIGNING_SECRET` invalida
  las URLs firmadas vivas (caducan en minutos).

## 12. Checklist de cierre

- [ ] Código del adaptador desplegado desde `development` (commit verificado; `main` es placeholder).
- [ ] Bucket privado creado y ruta pública bloqueada.
- [ ] Variables del §6 configuradas en API y worker, con secretos en el vault.
- [ ] Arranque sin avisos de `local` ni de ajustes inseguros.
- [ ] Carga real `201` y objetos en el bucket.
- [ ] Lectura con URL firmada `200`; firma alterada `403`.
- [ ] Reinicio del servicio y lectura posterior correcta.
- [ ] Mensaje con `adjuntoIds` pasa el adjunto a `SENT` y muestra la miniatura.
- [ ] Logs sin claves, URLs firmadas, base64 ni nombres originales.
- [ ] Decisión de migración o pérdida registrada (§9).
- [ ] Rollback a `local` probado en staging, no en producción.

## 13. Referencias

- [ADR-0028](../arquitectura/adr/ADR-0028-adjuntos-almacenamiento-externo-privado.md) — decisión de
  almacenamiento externo privado.
- [ADR-0020](../arquitectura/adr/ADR-0020-despliegue-en-railway-vercel-y-supabase.md) — despliegue por
  rama y topología del worker.
- [`adjuntos-imagenes-chat/spec.md`](../../openspec/specs/adjuntos-imagenes-chat/spec.md) y
  [`design.md`](../../openspec/specs/adjuntos-imagenes-chat/design.md).
- [`contratos-integracion.md`](../contratos-integracion.md) §2.1.1 — endpoints de adjuntos.
- [`privacidad.md`](../conversacion/privacidad.md) — retención, transferencia y riesgos de las imágenes.
- [`auditoria-specs-2026-11.md`](../auditoria-specs-2026-11.md) — estado de SPEC-23 y H5-X1.
