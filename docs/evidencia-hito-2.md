# Evidencia del Hito 2

> Tarea H2-09 de [`odd/tasks/hito-2.md`](../odd/tasks/hito-2.md): checklist de evidencia del hito, casos de prueba iniciales y verificación de commits por integrante.

Verificado el 2026-10-16 contra los remotos, después de `git fetch` de los tres repositorios:

| Repositorio | `origin/main` | `origin/development` |
|---|---|---|
| `Taller-SW-Web/G3-Chatbot-backend` | `da03d62` (PR #34) | `7a619b0` (PR #41) |
| `Taller-SW-Web/G3-Chatbot-frontend` | `ddfd565` (PR #18) | `1794b10` |
| `Taller-SW-Web/G3-Chatbot-specs` | `2379f52` | no existe |

El usuario de GitHub de cada commit se obtuvo de la API de GitHub (`author.login`). La rama es la del PR que llevó el commit a `development` o a `main`.

## 1. Commits por integrante

La PO confirmó el 2026-10-16 el vínculo entre cada cuenta de GitHub y su integrante: SEBASTIAN / SebJoq21 = Sebastian, Ankarmin = David, Gabriel (cuenta SOoOnny) = Sonny, Lume03 = Alonso, Mathias Torres Lezama / MathiasTL = Mathias, Diego-ArevaloM = Diego y nikaaat / Nikol Medrano = Nikol. La asignación de cada commit a una tarea sale de su etiqueta `h2-NN` y del reparto del hito; los dos commits de H2-08 no llevan etiqueta (ver notas).

| Tarea | Integrante | Usuario GitHub | Repo | Rama (PR) | Hash | Fecha | Asunto |
|---|---|---|---|---|---|---|---|
| H2-01 | Sebastian | SebJoq21 | backend | `feature/h2-01-base` (#28) | `581065c` | 2026-10-02 | feat(h2-01): base BD async PG18 + Alembic 0001-ready (Sebastian) |
| H2-02 | Sebastian | SebJoq21 | backend | `feature/h2-02-celular` (#29) | `70818de` | 2026-10-02 | feat(h2-02): modelo + adapter celular_verificacion_local + test (Sebastian) |
| H2-02 | Sebastian | SebJoq21 | backend | `feature/h2-02-celular` (#29) | `2d8267e` | 2026-10-02 | chore(h2-02): ignora .env local (Sebastian) |
| H2-03 | Sonny (autor git "Gabriel") | SOoOnny | backend | `feature/h2-03-cart-order-outbox` (#31) | `9e1e9d5` | 2026-10-02 | feat(h2-03): cart, cart_item, order_ref y outbox con adapters y tests |
| H2-04 | David | Ankarmin | backend | `feature/h2-04-david-checkout-postventa` (#32) | `ee3238f` | 2026-10-02 | feat(h2-04): checkout, payment_attempt, notification, claim_ref y return_ref con adapters y tests |
| H2-05 | David | Ankarmin | frontend | `feature/h2-05-david-mock` (#14) | `1709805` | 2026-10-02 | feat(h2-05): MessageBubble y ProductCard estaticos con mock |
| H2-05 | David | Ankarmin | frontend | `feature/h2-05-david-mock` (#14) | `fd6141a` | 2026-10-03 | fix(h2-05): corregir rutas de import a ../../../domain |
| H2-06 | Alonso | Lume03 | backend | `feature/h2-06-mensaje-evidencia` (#30) | `ea0ca2b` | 2026-10-02 | feat(h2-06): persistencia de mensajes y evidencias con pruebas |
| H2-06 | Alonso | Lume03 | backend | `feature/h2-06-mensaje-evidencia` (#30) | `58052b1` | 2026-10-02 | fix(h2-06): alinear message y evidence con las specs en ingles |
| H2-07 | Mathias Torres Lezama | MathiasTL | backend | `development` (llegó a `main` por #34) | `cd76f00` | 2026-10-02 | feat(h2-07): add conversation and attachment persistence with English names |
| H2-07 | Mathias Torres Lezama | MathiasTL | backend | `development` (llegó a `main` por #34) | `2b65b7b` | 2026-10-02 | ci(backend): add pytest workflow and ignore python caches |
| H2-07 | Mathias Torres Lezama | MathiasTL | frontend | sin PR asociado (está en `main`) | `cb49bfc` | 2026-10-02 | ci(frontend): add pnpm workflow |
| H2-08 (parcial) | Diego | Diego-ArevaloM | frontend | `feat/paridad-mockups` (#15) | `b01d76b` | 2026-10-03 | feat: paridad UI con Mockups |
| H2-08 (parcial) | Diego | Diego-ArevaloM | specs | `docs/design-system` (#8) | `2582579` | 2026-10-05 | docs: agregar design system Inka Athletics |
| H2-09 | Nikol Medrano | nikaaat | specs | `docs/h2-09-evidencia` | este documento | 2026-10-16 | Pendiente de PR y merge |
| H2-10 | Sebastian | SebJoq21 | backend | `feature/h2-10-migracion-0001` (#33) | `7d12c68` | 2026-10-02 | feat(h2-10): migracion 0001 initial schema + uuidv7/set_updated_at + deploy Supabase (Sebastian) |
| H2-10 | Sebastian | SebJoq21 | backend | `feature/h2-10-migracion-0001` (#33) | `abda0e8` | 2026-10-02 | feat: Se agregó el archivo .env.template |

Notas:

- La fila H2-08 de `b01d76b` es la que indica el reparto. El commit `2582579` de specs se agrega porque es del mismo autor y corresponde al sistema de diseño de H2-08. Ninguno de los dos commits lleva la etiqueta `h2-08`.
- Antes de esta tarea, Nikol no tenía commits etiquetados `h2-09`. Su único commit en el frontend en esas fechas es `98d5908` (2026-10-12, "docs: reflejar mobile-first y regla de cuenta en AGENTS.md", PR #18), que no pertenece al Hito 2.

### Criterio: commit propio mergeado en `main`

Para cada commit se comprobó con `git merge-base --is-ancestor <hash> origin/main` que es alcanzable desde `main`.

| Integrante | Usuario GitHub | ¿Commit en `main`? | Evidencia |
|---|---|---|---|
| David | Ankarmin | Sí | backend `ee3238f` (#32, llegó a `main` por #34); frontend `1709805` y `fd6141a` (#14, llegaron a `main` por #16) |
| Sonny | SOoOnny (autor git "Gabriel") | Sí | backend `9e1e9d5` (#31, llegó a `main` por #34) |
| Diego | Diego-ArevaloM | Sí | frontend `b01d76b` (#15, llegó a `main` por #16); specs `2582579` (#8) |
| Alonso | Lume03 | Sí | backend `ea0ca2b` y `58052b1` (#30, llegaron a `main` por #34) |

Estado: **cumplido**, con la identidad de cada cuenta confirmada por la PO el 2026-10-16.

## 2. Checklist de criterios de aceptación

| Criterio | Estado | Evidencia |
|---|---|---|
| Los cuatro integrantes sin commits tienen al menos un commit propio en `main` | Cumplido | Sección 1 (identidades confirmadas por la PO el 2026-10-16) |
| Las 14 tablas tienen modelo y adapter con contenido, y cada adapter tiene al menos un test | Cumplido | Tabla 2.1. Quedan dos archivos vacíos que no corresponden a ninguna de las 14 tablas |
| Una sola migración inicial `0001`, con los triggers de `updated_at` y su downgrade | Cumplido | Sección 2.2 |
| El README enlaza los mockups, el sistema de diseño y las 3 propuestas de UX | Pendiente | Sección 2.3. Lo cubre otro PR |

### 2.1 Tablas, modelos, adapters y tests (backend `origin/main`, `da03d62`)

Las 14 tablas son las del Hito 2. Desde el 2026-10-12, `docs/modelo-datos.md` documenta también `message_reaction`, `feedback_suggestion` y `purchase_rating` (commit `3b2cd43`, SPEC-24). Esas tres tablas no forman parte de este criterio y no tienen modelo, adapter ni migración.

Rutas: los modelos están en `src/adapters/outbound/persistence/models/`, los adapters en `src/adapters/outbound/persistence/` y los tests en `tests/unit/`.

| # | Tabla | Modelo (bytes) | Adapter (bytes) | Test (cantidad de `def test`) |
|---|---|---|---|---|
| 1 | `conversation` | `conversation.py` (3733) | `conversation_postgres_adapter.py` (1732) | `test_conversation_adapter.py` (10) |
| 2 | `message` | `message.py` (2615) | `message_postgres_adapter.py` (1360) | `test_message_adapter.py` (5) |
| 3 | `local_phone_verification` | `local_phone_verification.py` (1661) | `local_phone_verification_postgres_adapter.py` (1930) | `test_local_phone_verification_adapter.py` (4) |
| 4 | `cart` | `cart.py` (4440) | `cart_postgres_adapter.py` (2057) | `test_cart_adapter.py` (12, compartido con `cart_item`) |
| 5 | `cart_item` | `cart_item.py` (2592) | `cart_item_postgres_adapter.py` (1780) | `test_cart_adapter.py` (`test_cart_item_columnas_y_nulabilidad`, `test_cart_item_pk_fk_y_checks`, `test_cart_item_agregar_mismo_sku_suma_en_caso_de_uso`) |
| 6 | `checkout` | `checkout.py` (3752) | `checkout_postgres_adapter.py` (2631) | `test_checkout_adapter.py` (9) |
| 7 | `payment_attempt` | `payment_attempt.py` (2798) | `payment_attempt_postgres_adapter.py` (1151) | `test_payment_attempt_adapter.py` (7) |
| 8 | `order_ref` | `order_ref.py` (2665) | `order_ref_postgres_adapter.py` (2636) | `test_order_ref_adapter.py` (8) |
| 9 | `notification` | `notification.py` (3142) | `notification_postgres_adapter.py` (2672) | `test_notification_adapter.py` (7) |
| 10 | `claim_ref` | `claim_ref.py` (1562) | `claim_ref_postgres_adapter.py` (1651) | `test_claim_ref_adapter.py` (6) |
| 11 | `return_ref` | `return_ref.py` (2063) | `return_ref_postgres_adapter.py` (2479) | `test_return_ref_adapter.py` (7) |
| 12 | `evidence` | `evidence.py` (1946) | `evidence_postgres_adapter.py` (2543) | `test_evidence_adapter.py` (5) |
| 13 | `attachment` | `attachment.py` (3661) | `attachment_postgres_adapter.py` (2061) | `test_attachment_adapter.py` (9) |
| 14 | `outbox` | `outbox.py` (3202) | `outbox_postgres_adapter.py` (2474) | `test_outbox_adapter.py` (9) |

Además:

- `models/__init__.py` importa los 14 modelos, así que autogenerate los detecta.
- `tests/unit/test_persistence_schema.py` (4 tests) verifica el esquema en conjunto.
- `tests/integration/test_h2_06_postgres.py` cubre `message` y `evidence` contra PostgreSQL. Se omite si falta `TEST_DATABASE_URL`.

Archivos que siguen vacíos o con nombre en español:

| Archivo | Bytes | Observación |
|---|---|---|
| `src/adapters/outbound/persistence/cliente_postgres_adapter.py` | 0 | Nombre en español. En `development` se renombró a `customer_postgres_adapter.py`, pero sigue vacío. No existe tabla `customer` (el cliente es el `sub` del token) |
| `src/adapters/outbound/persistence/producto_postgres_adapter.py` | 0 | Nombre en español. En `development` se renombró a `product_postgres_adapter.py`, pero sigue vacío. Productos es un módulo externo, sin tabla propia |
| `src/adapters/outbound/persistence/__init__.py` | 0 | Marcador de paquete; es normal que esté vacío |

Ningún modelo ni adapter de las 14 tablas está vacío ni tiene nombre en español.

### 2.2 Migración inicial

Archivo: `src/infrastructure/db/migrations/versions/0001_initial_schema.py`, del commit `7d12c68` (PR #33).

- Es la única migración en `versions/`, tanto en `main` como en `development`.
- Usa `revision = '0001'` y `down_revision = None`. `alembic heads` devuelve un solo head: `0001 (head)`.
- `alembic.ini` define `file_template = %%(rev)s_%%(slug)s`.
- Crea las 14 tablas con `op.create_table`.
- Crea las funciones `public.uuidv7()` y `public.set_updated_at()`. Según el comentario de la migración, Supabase corre PG17 sin `uuidv7()` nativo, por eso se define como función propia.
- Crea el trigger `trg_<tabla>_updated_at BEFORE UPDATE` en las 9 tablas con `updated_at`: `attachment`, `cart`, `cart_item`, `checkout`, `conversation`, `evidence`, `notification`, `order_ref` y `outbox`.
- `downgrade()` elimina los 9 triggers, las 14 tablas y las funciones `set_updated_at()` y `uuidv7()`.
- Prueba local del 2026-10-16 contra una base vacía en PostgreSQL 16.15, no Supabase:
  - `alembic upgrade head` creó 14 tablas y 9 triggers, con `alembic_version = 0001`.
  - `alembic downgrade base` dejó 0 tablas y 0 funciones.
  - No se probó contra el Supabase del equipo.

### 2.3 Enlaces del README

Estado: **pendiente**. Lo cubre otro PR.

- El README de specs tiene la fila "Diseño | Figma", pero sin enlace. No enlaza `docs/design-system.md`, que existe desde `2582579`, ni ninguna propuesta de UX.
- En `docs/` de specs no hay propuestas de UX.
- El frontend no tiene `README.md` en `main`. Su carpeta `docs/` solo contiene cinco capturas (`visual-*.png`).

## 3. Casos de prueba iniciales del Hito 2

Estos casos solo cubren los entregables del Hito 2. Los casos funcionales del Hito 3 corresponden a la tarea H3-16.

| ID | Criterio | Precondición | Pasos | Resultado esperado | Cómo se verifica |
|---|---|---|---|---|---|
| CP-H2-01 | Commit propio de David en `main` | Fetch de backend y frontend | `git log origin/main --author=Ankarmin --no-merges` en cada repo | Al menos un commit | Hash y PR en la sección 1 |
| CP-H2-02 | Commit propio de Sonny en `main` | Fetch de backend | `git log origin/main --author=Gabriel --no-merges` y comprobar el login `SOoOnny` en GitHub | Al menos un commit | Hash y PR en la sección 1 |
| CP-H2-03 | Commit propio de Diego en `main` | Fetch de frontend y specs | `git log origin/main --author=Diego-ArevaloM --no-merges` en cada repo | Al menos un commit | Hash y PR en la sección 1 |
| CP-H2-04 | Commit propio de Alonso en `main` | Fetch de backend | `git log origin/main --author=Lume03 --no-merges` | Al menos un commit | Hash y PR en la sección 1 |
| CP-H2-05 | Commits de Sebastian, Mathias y Nikol en `main` | Fetch de los tres repos | `git log origin/main --author=<autor> --no-merges` | Al menos un commit por integrante | Hash y PR en la sección 1. El de Nikol queda cumplido cuando se mergee este documento |
| CP-H2-06 | `conversation` con modelo, adapter y test | Backend en `main`, dependencias instaladas | Comprobar que los archivos no estén vacíos y ejecutar `python -m pytest tests/unit/test_conversation_adapter.py` | Archivos con contenido y tests en verde | Salida de pytest y `git ls-tree -l` |
| CP-H2-07 | `message` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_message_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-08 | `local_phone_verification` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_local_phone_verification_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-09 | `cart` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_cart_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-10 | `cart_item` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_cart_adapter.py -k cart_item` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-11 | `checkout` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_checkout_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-12 | `payment_attempt` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_payment_attempt_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-13 | `order_ref` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_order_ref_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-14 | `notification` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_notification_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-15 | `claim_ref` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_claim_ref_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-16 | `return_ref` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_return_ref_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-17 | `evidence` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_evidence_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-18 | `attachment` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_attachment_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-19 | `outbox` con modelo, adapter y test | Igual que CP-H2-06 | Igual, con `test_outbox_adapter.py` | Igual que CP-H2-06 | Igual que CP-H2-06 |
| CP-H2-20 | `alembic upgrade head` contra una base vacía | Base PostgreSQL vacía y `DATABASE_URL` apuntando a ella | `alembic upgrade head` y luego contar tablas y triggers con `psql` | 14 tablas, 9 triggers `trg_*_updated_at` y `alembic_version = 0001` | Salida de Alembic y de las consultas |
| CP-H2-21 | `alembic downgrade base` | Base de CP-H2-20 en `0001` | `alembic downgrade base` y luego contar tablas y funciones | 0 tablas del modelo, sin `set_updated_at()` ni `uuidv7()` | Salida de Alembic y de las consultas |
| CP-H2-22 | Un solo head de Alembic | Backend en `main` | `alembic heads` y listar `migrations/versions/` | Un solo head, `0001`, y un solo archivo `0001_*.py` | Salida del comando |
| CP-H2-23 | Identificadores en inglés | Migración `0001` | Revisar nombres de tablas, columnas, valores de los `CHECK ... IN`, constraints, índices y archivos de `models/` y `*_postgres_adapter.py` | Sin identificadores en español. Los valores de Ventas se guardan como `EXCHANGE`, `MONEY_REFUND` | Revisión del archivo de migración y `git ls-tree` de `persistence/` |
| CP-H2-24 | CI en verde en el backend | Último commit de `main` y de `development` | Consultar el check `test` del workflow `CI` en GitHub | `completed / success` | Pestaña Checks del commit o API `check-runs` |
| CP-H2-25 | CI en verde en el frontend | Último commit de `main` y de `development` | Consultar el check `check` del workflow de frontend en GitHub | `completed / success` | Pestaña Checks del commit o API `check-runs` |

### Resultado de la primera ejecución (2026-10-16)

| ID | Resultado | Detalle |
|---|---|---|
| CP-H2-01 a CP-H2-04 | Pasa | Sección 1 |
| CP-H2-05 | Parcial | Sebastian y Mathias pasan. Nikol pasa cuando se mergee este documento |
| CP-H2-06 a CP-H2-19 | Pasa | Tabla 2.1 y ejecución de pytest |
| CP-H2-20 y CP-H2-21 | Pasa en local | PostgreSQL 16.15 local, base vacía. No se ejecutó contra Supabase |
| CP-H2-22 | Pasa | `0001 (head)` |
| CP-H2-23 | Pasa en la migración | Quedan los dos archivos vacíos con nombre en español en `main` (sección 2.1) |
| CP-H2-24 | Pasa | Check `test` en `success` en `da03d62` (`main`) y `7a619b0` (`development`) |
| CP-H2-25 | Pasa | Check `check` en `success` en `ddfd565` (`main`) y `1794b10` (`development`) |

## 4. Ejecución de `python -m pytest tests/unit` en el backend

Se ejecutó el 2026-10-16 en un entorno virtual con Python 3.13.16 (el CI usa 3.12), con las dependencias de `requirements.txt` de cada rama y `PYTHONPATH=.`:

| Rama | Commit | Resultado |
|---|---|---|
| `main` | `da03d62` | 106 passed |
| `development` | `7a619b0` | 420 passed, 6 warnings |

Los tests de integración de `development` (`tests/integration`) se omitieron todos (34 skipped) porque no se definió `TEST_DATABASE_URL`.

## 5. Lo que no se pudo verificar

- La migración contra el Supabase del equipo: solo se probó en PostgreSQL 16 local.
- El commit propio de Nikol en `main`, hasta que se mergee este documento.
