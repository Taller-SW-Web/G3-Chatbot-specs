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
- [x] **H2-03** Sonny: `cart`, `cart_item`, `order_ref`, `outbox` (SPEC-10, 11, 15).
- [x] **H2-04** David (BD): `checkout`, `payment_attempt`, `claim_ref`, `return_ref`, `notification` (SPEC-12, 14, 16, 19 a 22).
- [x] **H2-05** David (frontend): `MessageBubble` y `ProductCard` estáticos con datos mock, usando los tokens de Diego.
- [x] **H2-06** Alonso: `message` y `evidence`; configuración de pytest con un test por adapter.
- [x] **H2-07** Mathias: `conversation` y `attachment` (SPEC-23) con sus adapters; CI que ejecute pytest (backend) y CI de frontend con pnpm.
- [x] **H2-08** Diego: tokens y tema Tailwind, componentes base (Button, Input, Card), enlace al Figma en el README y 3 propuestas de UX en `docs/`.
- [x] **H2-09** Nikol: checklist de evidencia del hito, casos de prueba iniciales y verificación de commits por integrante.

### Fase 3: cierre (Sebastian)

- [x] **H2-10** Generar la migración inicial con `alembic revision --autogenerate --rev-id 0001 -m "initial schema"`, agregar a mano en esa migración la función `set_updated_at()` y un trigger `BEFORE UPDATE` en cada tabla con `updated_at` (`conversation`, `attachment`, `cart`, `cart_item`, `checkout`, `order_ref`, `notification`, `evidence`, `outbox`), porque autogenerate no detecta funciones ni triggers (regla de la fila Tiempos en `docs/modelo-datos.md`), y su `downgrade` debe eliminarlos; probarla contra Supabase (`alembic upgrade head` y `alembic downgrade base`) y hacer push.

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

Estado al 2026-10-16, verificado con `git fetch` contra `origin/main` y `origin/development` del backend (`Taller-SW-Web/G3-Chatbot-backend`) y del frontend (`Taller-SW-Web/G3-Chatbot-frontend`), y contra `origin/main` de specs. El detalle por tabla, la prueba de la migración y los casos de prueba están en [`docs/evidencia-hito-2.md`](../../docs/evidencia-hito-2.md).

La rama de integración del backend es `development`; el frontend también tiene una rama `development`. Todo lo del Hito 2 llegó a `main` del backend con el PR #34 (`development` → `main`, merge `da03d62`), incluida la migración `0001`. En el frontend llegó a `main` con el PR #16 (merge `8ac3667`).

| Tarea | Estado | Evidencia |
|---|---|---|
| H2-01 | Hecha (pendiente confirmar documentación de IDs, `models/__init__.py` y regla `jsonb`) | Backend `581065c`, PR #28 |
| H2-02 | Hecha | Backend `70818de` y `2d8267e`, PR #29; el test pasó a `test_local_phone_verification_adapter.py` con el renombre a inglés |
| H2-03 | Hecha | Backend `9e1e9d5` (`cart`, `cart_item`, `order_ref` y `outbox` con adapters y tests), PR #31 |
| H2-04 | Hecha | Backend `ee3238f` (`checkout`, `payment_attempt`, `notification`, `claim_ref` y `return_ref` con adapters y tests), PR #32 |
| H2-05 | Hecha | Frontend `1709805` (`MessageBubble` y `ProductCard` estáticos con mock) y `fd6141a` (rutas de import), PR #14 del frontend |
| H2-06 | Hecha | Backend `ea0ca2b` (`message` y `evidence` con pruebas) y `58052b1` (alineación con las specs en inglés), PR #30 |
| H2-07 | Hecha | Backend `cd76f00` (modelos, adapters y tests de `conversation` y `attachment`) y `2b65b7b` (CI con pip). Frontend `cb49bfc` (CI con pnpm) |
| H2-08 | Hecha | Frontend `b01d76b` ("paridad UI con Mockups", PR #15 del frontend): tokens en el `@theme` de `src/app/globals.css` y componentes base como clases `.wf-btn`, `.wf-input` y `.wf-card` (no hay componentes React `Button`, `Input` ni `Card` separados). Specs `2582579` (`docs/design-system.md`, PR #8) y `8f8423f` (enlace a Figma en el README y `docs/propuestas-ux.md`, PR #14) |
| H2-09 | Hecha | Specs `f705f6e` (`docs/evidencia-hito-2.md`), PR #13 |
| H2-10 | Hecha | Backend `7d12c68` (migración `0001_initial_schema.py` con `uuidv7()`, `set_updated_at()`, 9 triggers y su `downgrade`), PR #33 |

Criterios de aceptación:

| Criterio | Estado | Evidencia |
|---|---|---|
| David, Sonny, Diego y Alonso tienen al menos un commit propio en `main` | Cumplido (usuarios por confirmar) | David = Ankarmin (`ee3238f`, `1709805`), Sonny = SOoOnny, autor git "Gabriel" (`9e1e9d5`), Diego = Diego-ArevaloM (`b01d76b`, `2582579`), Alonso = Lume03 (`ea0ca2b`, `58052b1`). El vínculo entre cada usuario de GitHub y la persona es inferido del reparto y de las etiquetas `h2-NN` |
| Las 14 tablas tienen modelo y adapter con contenido, y cada adapter tiene al menos un test | Cumplido | 14/14 en `main` del backend; `cart_item` se prueba dentro de `test_cart_adapter.py` (ver `docs/evidencia-hito-2.md` §2.1) |
| Una sola migración `0001` con las tablas, los triggers de `updated_at` y `downgrade` | Cumplido | `0001_initial_schema.py` es la única en `versions/` de `main` y `development`; un solo head. Probada en local (PostgreSQL 16, base vacía) el 2026-10-16; no se repitió contra Supabase |
| El README enlaza los mockups, el sistema de diseño y las 3 propuestas de UX | Cumplido | README de specs, fila "Diseño": Figma, `docs/design-system.md` y `docs/propuestas-ux.md` (PR #14, merge `3b6fa53`) |

Pendientes verificados:

- Archivos vacíos (0 bytes) en `src/adapters/outbound/persistence/` de `main` del backend: `cliente_postgres_adapter.py` y `producto_postgres_adapter.py`, con nombre en español, y `__init__.py`, marcador de paquete. En `development` los dos primeros se renombraron a `customer_postgres_adapter.py` y `product_postgres_adapter.py`, pero siguen vacíos. Ninguno corresponde a una de las 14 tablas.
- `alembic upgrade head` falla en una instalación limpia desde `main` del backend: `env.py` convierte la URL a `psycopg2` y `requirements.txt` de `main` no lo incluye (hallazgo del Hito 3, según `odd/tasks/hito-3.md`). En `development` ya figura `psycopg2-binary` desde `4758b14` (H3-05); falta que llegue a `main`.

Renombre a inglés del modelo de datos (2026-10-02): `docs/modelo-datos.md`, el resto de los specs y el diagrama `mer-logico` ya usan los nombres en inglés. El diagrama `mer-conceptual` se deja sin cambios por decisión del equipo.

Commits de la convención de nombres en inglés: specs `e095041` (`main`).

## Siguiente paso

Dar por cerrado el Hito 2: las diez tareas tienen evidencia en `main` y se cumplen los cuatro criterios de aceptación. Los pendientes de arriba (archivos vacíos y `psycopg2` en `main`) se resuelven en el Hito 3, y los integrantes confirman su usuario de GitHub.
