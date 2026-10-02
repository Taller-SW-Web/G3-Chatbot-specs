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
- Snapshots de módulos externos: se guardan en `jsonb` con los nombres reales del contrato (`product_id`, `precio_regular`, `channel_id`), según `docs/modelo-datos.md`. Aplica a `item_carrito`, `pedido_ref`, `reclamo_ref` y `devolucion_ref`.
- Buena práctica de versionado de migraciones: los identificadores de revisión son secuenciales y de cuatro dígitos. La primera es `0001` y cada migración siguiente suma uno (`0002`, `0003`, ...), generada con `--rev-id` explícito. Los archivos se nombran `NNNN_descripcion_corta.py` (`file_template = %%(rev)s_%%(slug)s` en `alembic.ini`, que hoy está vacío). Nunca se editan ni se renumeran migraciones ya mergeadas en `main`; un cambio nuevo es siempre una migración nueva.
- Fuera de alcance: integración real con Productos y Despacho (scopes pendientes en Seguridad, Hito 4) y actualización de mocks (Hito 3).

## Tareas

### Fase 1: desbloqueo (Sebastian)

- [ ] **H2-01** Confirmar la versión de PostgreSQL en el Supabase del equipo (`SELECT version();`) y decidir la generación de IDs: `server_default=text("uuidv7()")` si es PG18; si no, UUID v7 en la aplicación (por ejemplo `uuid6` o `uuid_utils`) o una función SQL propia. Luego dejar en `main` la `Base` declarativa, el engine/sesión y `env.py` de Alembic (incluye `alembic.ini` con `file_template = %%(rev)s_%%(slug)s` para el versionado `0001`, `0002`, ...), y documentar la decisión de IDs, la convención de `models/__init__.py` y la regla del snapshot `jsonb`.

### Fase 2: en paralelo (modelo + adapter + test, sin migración)

- [ ] **H2-02** Sebastian: `celular_verificacion_local` (modelo + adapter; no existe tabla `cliente`, `cliente_id` es el `sub` del token); revisión técnica de los PR, empezando por los que tienen FKs entre sí (`carrito` → `item_carrito`, `checkout` → `intento_pago`).
- [ ] **H2-03** Sonny: `carrito`, `item_carrito`, `pedido_ref`, `outbox` (SPEC-10, 11, 15).
- [ ] **H2-04** David (BD): `checkout`, `intento_pago`, `reclamo_ref`, `devolucion_ref`, `notificacion` (SPEC-12, 14, 16, 19 a 22).
- [ ] **H2-05** David (frontend): `MessageBubble` y `ProductCard` estáticos con datos mock, usando los tokens de Diego.
- [ ] **H2-06** Alonso: `mensaje` y `evidencia`; configuración de pytest con un test por adapter.
- [ ] **H2-07** Mathias: `conversacion` y `adjunto` (SPEC-23) con sus adapters; CI que ejecute pytest.
- [ ] **H2-08** Diego: tokens y tema Tailwind, componentes base (Button, Input, Card), enlace al Figma en el README y 3 propuestas de UX en `docs/`.
- [ ] **H2-09** Nikol: checklist de evidencia del hito, casos de prueba iniciales y verificación de commits por integrante.

### Fase 3: cierre (Sebastian)

- [ ] **H2-10** Generar la migración inicial con `alembic revision --autogenerate --rev-id 0001 -m "initial schema"`, probarla contra Supabase (`alembic upgrade head` y `alembic downgrade base`) y hacer push.

## Criterios de aceptación

- Los cuatro integrantes sin commits (David, Sonny, Diego, Alonso) tienen al menos un commit propio mergeado en `main`.
- Las 14 tablas de `docs/modelo-datos.md` tienen modelo y adapter con contenido, y cada adapter tiene al menos un test.
- Existe una sola migración inicial, con revisión `0001`, que crea todas las tablas del modelo y se puede revertir con `alembic downgrade base`.
- El README enlaza los mockups, el sistema de diseño y las 3 propuestas de UX.

## Riesgos

- **PostgreSQL 18 sin confirmar en Supabase:** de ello depende `uuidv7()`; se resuelve en H2-01 antes de que los demás escriban modelos.
- **Cuello de botella en Sebastian:** si tarda en la Fase 1 se bloquean los modelos; si tarda en la Fase 3 el entregable de BD queda sin migración.
- **Carga:** David y Sonny son los más cargados; esta división no la aumenta porque el diseño de tablas ya existe.
- **Dependencia de David con Diego:** H2-05 necesita los tokens de H2-08; si se retrasan, David empieza con estilos provisionales.

## Progreso

Ninguna tarea iniciada. Commits: pendiente de confirmación del usuario cuando corresponda.

## Siguiente paso

Sebastian ejecuta H2-01.
