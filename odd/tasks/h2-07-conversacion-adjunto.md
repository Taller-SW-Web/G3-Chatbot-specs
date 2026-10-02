# H2-07: modelos y adapters de `conversation` y `attachment`, más CI

Feature de Mathias dentro del Hito 2 (ver `hito-2.md`). Repo: `G3-Chatbot-backend`, rama `feature/h2-07-conversacion-adjunto` creada desde `origin/development`.

## Objetivo

Dejar `conversation` y `attachment` (SPEC-23) con modelo SQLAlchemy, adapter y test, y un workflow de CI que ejecute pytest.

## Alcance y restricciones

- Fuente de verdad: `docs/modelo-datos.md` (secciones `conversation` y `attachment`) y SPEC-23 (`openspec/specs/adjuntos-imagenes-chat/`).
- Patrón de referencia: `celular_verificacion` de Sebastian (modelo `Mapped`/`mapped_column`, adapter clase simple con `AsyncSession` que hace `flush` sin `commit`, test offline sobre `Base.metadata`).
- IDs: `server_default=text("uuidv7()")`. Enums como `text + CHECK`. Timestamps `timestamptz`. Nombres de constraints `uq_<table>_<cols>` y `ck_<table>_<rule>`.
- `attachment` es la tabla 14 y no tiene archivos previos: se crean `models/adjunto.py` y `adjunto_postgres_adapter.py`.
- Sin migraciones (`alembic revision` es H2-10, de Sebastian).
- No se crean `pytest.ini` ni `conftest.py` (los configura H2-06, Alonso). El CI usa `PYTHONPATH=.` y `python -m pytest tests/unit`.
- Fuera de alcance: puerto `AttachmentStorage`, `AdjuntoService` y casos de uso.

## Configuración de implementación

- TDD: apagado (sin configuración de proyecto ni elección explícita; fuente: ausencia de config).
- Runner de pruebas: `python -m pytest tests/unit` con `PYTHONPATH=.`.
- Estrategia de entrega: `ask-on-risk`. Pronóstico: unas 400 líneas editadas, bajo o en el límite del presupuesto de un PR.

## Tareas

Ruta: escritor delegado único (dispara el trigger de 2+ archivos no triviales).

- [x] **T1** Modelos `conversation` y `attachment` con columnas, CHECKs e índices de `modelo-datos.md`, y registro en `models/__init__.py`.
- [x] **T2** Adapters `conversacion_postgres_adapter.py` y `adjunto_postgres_adapter.py`.
- [x] **T3** Tests unitarios offline para ambos adapters y modelos.
- [x] **T4** Workflow `.github/workflows/ci.yml` que instala `requirements.txt` y ejecuta pytest.

## Decisiones tomadas por defecto (a confirmar en revisión)

- `conversation.title_search_vector`: `TSVECTOR` con `Computed(..., persisted=True)` e índice GIN.
- `conversation.context`: se agrega `CHECK (jsonb_typeof(context) = 'object')` por la regla general de `modelo-datos.md` (sección Convenciones, fila `jsonb`).
- `created_at` y `updated_at`: `server_default=now()` en ambas tablas; sin trigger.
- `attachment.message_id` usa `ForeignKey("message.id")` como cadena; el test no resuelve esa FK hasta que H2-06 mergee `message`.
- El adapter de `conversation` es una clase simple (no implementa `conversacion_state_port`, que está vacío y pendiente de renombre).

## Criterios de aceptación

- `conversation` y `attachment` tienen modelo y adapter con contenido, registrados en `models/__init__.py`.
- Cada adapter tiene al menos un test que pasa con `PYTHONPATH=. python -m pytest tests/unit`.
- El workflow de CI existe y ejecuta pytest.
- No hay migraciones ni `pytest.ini`/`conftest.py` en el PR.

## Progreso

T1 a T4 implementadas por un escritor delegado y verificadas: `PYTHONPATH=. python -m pytest tests/unit` da 23 passed (re-ejecutado por el orquestador, Python 3.14 local; el CI usa 3.12). `Base.metadata` lista `attachment`, `local_phone_verification` y `conversation`. Cambios sin stagear en la rama. Commit: pendiente de confirmación del usuario. Espejo en Engram: pendiente (`ambiguous_project`).

## Siguiente paso

Confirmar el commit, abrir PR hacia `development` y marcar el avance en `hito-2.md`.
