# Hito 2: división de entregables

## Objetivo

Cubrir los cuatro entregables del Hito 2 (25 %) con evidencia de commits de todos los integrantes.

| Entregable | Estado inicial (verificado en los repos) |
|---|---|
| Repositorio GitHub con evidencia de uso de todos los integrantes | Faltan commits de David, Sonny, Diego y Alonso |
| Diseño e implementación de repositorios de BD | Diseño completo (`docs/modelo-datos.md`, MER); implementación vacía: los 20 archivos de `persistence/` tienen 0 bytes, `migrations/versions/` está vacía |
| Mockups y Sistema de Diseño | Mockups ya hechos (fuera del repo); falta enlazarlos y crear los tokens y componentes base |
| Experiencia de Usuario (3 propuestas) | No existen; las realiza Diego |

## Alcance y restricciones

- Cada integrante trabaja en rama propia y abre PR, para que quede evidencia por autor.
- Los modelos se definen sin generar migraciones. Solo Sebastian ejecuta `alembic revision --autogenerate`, una única vez, cuando los modelos estén en `main` (evita múltiples `heads`).
- Los modelos deben importarse en `models/__init__.py` o en `env.py`; de lo contrario autogenerate no los detecta.
- Snapshots de módulos externos: se guardan en `jsonb` con los nombres reales del contrato (`product_id`, `precio_regular`, `channel_id`), según `docs/modelo-datos.md`. Aplica a `cart_item`, `order_ref`, `claim_ref` y `return_ref`.
- Buena práctica de versionado de migraciones: los identificadores de revisión son secuenciales y de cuatro dígitos. La primera es `0001` y cada migración siguiente suma uno (`0002`, `0003`, ...), generada con `--rev-id` explícito. Los archivos se nombran `NNNN_descripcion_corta.py` (`file_template = %%(rev)s_%%(slug)s` en `alembic.ini`, que hoy está vacío). Nunca se editan ni se renumeran migraciones ya mergeadas en `main`; un cambio nuevo es siempre una migración nueva.
- Convención de nombres (acordada el 2026-10-02): todos los identificadores de la base (tablas, columnas, valores de enumeración, constraints e índices) van en inglés, según `docs/modelo-datos.md`. Las etiquetas de la interfaz siguen en español y las resuelve el frontend. Los valores que Ventas define en español (`CAMBIO`, `DEVOLUCION_DINERO`, `IMAGEN`) se guardan en inglés (`EXCHANGE`, `MONEY_REFUND`, `IMAGE`) y el adapter los traduce en ambos sentidos. El detalle está en `odd/tasks/db-english-naming.md`.
- Los archivos vacíos de `models/` y `*_postgres_adapter.py` conservan hoy su nombre en español. Al implementarlos, renómbralos a inglés (por ejemplo `carrito.py` pasa a `cart.py`) y mantén el patrón de `conversation.py` y `attachment.py`.
- Fuera de alcance: integración real con Productos y Despacho (scopes pendientes en Seguridad, Hito 4) y actualización de mocks (Hito 3).

## Tareas

### Fase 1: desbloqueo (Sebastian)

- [x] **H2-01** Confirmar la versión de PostgreSQL en el Supabase del equipo (`SELECT version();`) y decidir la generación de IDs: `server_default=text("uuidv7()")` si es PG18; si no, UUID v7 en la aplicación (por ejemplo `uuid6` o `uuid_utils`) o una función SQL propia. Luego dejar en `main` la `Base` declarativa, el engine/sesión y `env.py` de Alembic (incluye `alembic.ini` con `file_template = %%(rev)s_%%(slug)s` para el versionado `0001`, `0002`, ...), y documentar la decisión de IDs, la convención de `models/__init__.py` y la regla del snapshot `jsonb`.

### Fase 2: en paralelo (modelo + adapter + test, sin migración)

- [x] **H2-02** Sebastian: `local_phone_verification` (modelo + adapter; no existe tabla `customer`, `customer_id` es el `sub` del token); revisión técnica de los PR, empezando por los que tienen FKs entre sí (`cart` → `cart_item`, `checkout` → `payment_attempt`).
- [ ] **H2-03** Sonny: `cart`, `cart_item`, `order_ref`, `outbox` (SPEC-10, 11, 15).
- [ ] **H2-04** David (BD): `checkout`, `payment_attempt`, `claim_ref`, `return_ref`, `notification` (SPEC-12, 14, 16, 19 a 22).
- [ ] **H2-05** David (frontend): `MessageBubble` y `ProductCard` estáticos con datos mock, usando los tokens de Diego.
- [ ] **H2-06** Alonso: `message` y `evidence`; configuración de pytest con un test por adapter.
- [x] **H2-07** Mathias: `conversation` y `attachment` (SPEC-23) con sus adapters; CI que ejecute pytest (backend) y CI de frontend con pnpm.
- [ ] **H2-08** Diego: tokens y tema Tailwind, componentes base (Button, Input, Card), enlace al Figma en el README y 3 propuestas de UX en `docs/`.
- [ ] **H2-09** Nikol: checklist de evidencia del hito, casos de prueba iniciales y verificación de commits por integrante.

### Fase 3: cierre (Sebastian)

- [ ] **H2-10** Generar la migración inicial con `alembic revision --autogenerate --rev-id 0001 -m "initial schema"`, agregar a mano en esa migración la función `set_updated_at()` y un trigger `BEFORE UPDATE` en cada tabla con `updated_at` (`conversation`, `attachment`, `cart`, `cart_item`, `checkout`, `order_ref`, `notification`, `evidence`, `outbox`), porque autogenerate no detecta funciones ni triggers (regla de la fila Tiempos en `docs/modelo-datos.md`), y su `downgrade` debe eliminarlos; probarla contra Supabase (`alembic upgrade head` y `alembic downgrade base`) y hacer push.

## Criterios de aceptación

- Los cuatro integrantes sin commits (David, Sonny, Diego, Alonso) tienen al menos un commit propio mergeado en `main`.
- Las 14 tablas de `docs/modelo-datos.md` tienen modelo y adapter con contenido, y cada adapter tiene al menos un test.
- Existe una sola migración inicial, con revisión `0001`, que crea todas las tablas del modelo y los triggers de `updated_at`, y se puede revertir con `alembic downgrade base`.
- El README enlaza los mockups, el sistema de diseño y las 3 propuestas de UX.

## Riesgos

- **PostgreSQL 18 sin confirmar en Supabase:** de ello depende `uuidv7()`; se resuelve en H2-01 antes de que los demás escriban modelos.
- **Cuello de botella en Sebastian:** si tarda en la Fase 1 se bloquean los modelos; si tarda en la Fase 3 el entregable de BD queda sin migración.
- **Carga:** David y Sonny son los más cargados; esta división no la aumenta porque el diseño de tablas ya existe.
- **Dependencia de David con Diego:** H2-05 necesita los tokens de H2-08; si se retrasan, David empieza con estilos provisionales.

## Progreso

Estado al 2026-10-02, verificado contra `origin/development` del backend (refs locales, sin fetch).

| Tarea | Estado | Evidencia |
|---|---|---|
| H2-01 | Hecha (pendiente confirmar documentación de IDs, `models/__init__.py` y regla `jsonb`) | `581065c`, PR #28 |
| H2-02 | Hecha | `70818de`, PR #29; el test pasó a `test_local_phone_verification_adapter.py` con el renombre a inglés |
| H2-07 | Hecha | Backend `development`: `cd76f00` (modelos, adapters y tests de `conversation` y `attachment`, 23 tests en verde) y `2b65b7b` (CI con pip). Frontend `main`: `cb49bfc` (CI con pnpm, activo cuando exista `package.json` con lockfile) |
| H2-03 a H2-06, H2-08, H2-09 | No iniciadas | Los demás archivos de `persistence/` siguen con 0 bytes; no hay commits de David, Sonny, Diego y Alonso |
| H2-10 | Pendiente | `versions/` vacía; depende de H2-03, 04, 06 y 07 |

Criterios de aceptación: commits de los 4 integrantes 0/4; tablas con modelo y adapter 3/14 (`local_phone_verification`, `conversation` y `attachment` en `development`); migración `0001` inexistente; README sin enlaces a mockups, sistema de diseño ni UX.

Renombre a inglés del modelo de datos (2026-10-02): `docs/modelo-datos.md`, el resto de los specs y el diagrama `mer-logico` ya usan los nombres en inglés. El diagrama `mer-conceptual` se deja sin cambios por decisión del equipo.

Nota: la rama de integración del backend es `development` (no `develop`) y solo existe en backend.

Commits de la convención de nombres en inglés: specs `e095041` (`main`).

## Siguiente paso

Sonny, David, Alonso y Diego inician sus tareas de la Fase 2 sobre `development`, usando los nombres en inglés de `docs/modelo-datos.md`.
