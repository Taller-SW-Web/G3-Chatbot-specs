# ADR-0025: Monolito modular por capacidad en backend y frontend

## Estado

Aceptada

## Fecha

2026-11-21

## Contexto

El backend y el frontend ya seguían Clean Architecture + Hexagonal (ADR-0002), pero el corte primario era **por capa**: `domain/`, `application/`, `ports/` y `adapters/`. Cualquier funcionalidad tocaba los mismos archivos y carpetas que otra persona (`main.py`, el contenedor de DI, el adaptador HTTP del frontend y el registro de navegación), lo que producía PRs que se pisaban y rebases constantes.

El equipo ya tomó la decisión y la implementó en los dos repositorios de aplicación. El ADR canónico vive en `G3-Chatbot-backend/docs/adr/ADR-0024-modularizacion.md`; este ADR la **homologa** en el repositorio de especificaciones para que las specs, el C4 y el flujo de trabajo compartan el mismo vocabulario. No crea una decisión nueva.

> **Nota de numeración:** el ADR-0024 de **este** repositorio es el del pipeline de calidad y seguridad. El ADR-0024 del **backend** es el de modularización. Para evitar ambigüedad, en la documentación del canal se cita siempre como «ADR-0024 del backend».

## Decisión

El corte primario pasa a ser **por capacidad de negocio**: un monolito modular con **8 módulos con el mismo id** en backend y frontend:

`mod-auth`, `mod-catalog`, `mod-cart`, `mod-shipping`, `mod-checkout`, `mod-orders`, `mod-postventa` y `mod-chat`.

Dentro de cada módulo se conserva el corte hexagonal de ADR-0002 (`domain/`, `application/`, `ports/`, `adapters/`; en el frontend además `ui/`). `shared/` es el kernel: configuración, base de datos, DI, errores, autenticación de transporte, correlation id, outbox, persistencia compartida y primitivas de UI. **No contiene reglas de negocio.**

Reglas de dependencia:

1. Un módulo solo importa `shared/`, su propio árbol y el `public.py` / `public.ts` de los módulos declarados en `dependsOn`.
2. Está prohibido importar `domain/`, `application/` o `adapters/` de otro módulo.
3. El DAG es `catalog → cart → checkout → orders → postventa`; `shipping` alimenta a `checkout`; `chat` orquesta a todos; `auth` es transversal a través de `shared/infrastructure/auth`.
4. `chat` puede depender de todos; ningún módulo depende de `chat`.
5. Los routers conservan las rutas públicas; cada router declara `tags=[MODULE_ID]`.
6. Un PR toca un solo módulo. `shared/` exige la etiqueta `cross-modulo` y revisión del owner de plataforma.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Mantener el corte por capa | PRs grandes y acoplados; conflictos constantes en `main.py`, DI y registro de rutas |
| Microservicios por capacidad | Coste operativo y de red desproporcionado para el curso; el dominio sigue siendo un solo producto |
| Paquetes por capa con prefijos de módulo | No impide importar el interior de otro módulo; las fronteras no son verificables |
| Monolito modular con `public.py` / `public.ts` y gates | Aísla el cambio, permite PRs paralelos y verifica las fronteras en CI |

## Consecuencias

**Positivas**

- PRs pequeños y paralelos, con ownership claro por módulo.
- El contrato backend↔frontend se puede verificar por `tags` y manifiestos.
- Las fronteras dejan de ser una convención: `scripts/check_modules.py` y `scripts/check-modules.mjs` las bloquean.

**Negativas y riesgos aceptados**

- Hay que mover código una vez (estrategia *strangler* por módulo).
- `shared/` exige disciplina para no convertirse en un cajón de sastre.
- Next.js obliga a mantener archivos wrapper en `app/`.
- La verificación cruzada de OpenAPI entre repositorios todavía es manual; el manifiesto del frontend declara endpoints, pero el gate actual no compara cada endpoint contra `docs/openapi.json`.

**Neutras**

- No se introducen microservicios, repositorios nuevos ni cambios de URL pública.
- El despliegue sigue siendo un solo backend y un solo frontend.

## Referencias

- `G3-Chatbot-backend/docs/adr/ADR-0024-modularizacion.md` — decisión canónica y migración por fases.
- `G3-Chatbot-backend/modules.manifest.json` y `G3-Chatbot-frontend/modules.manifest.json` — manifiestos de módulos, owners y `dependsOn`.
- [`modularizacion.md`](../modularizacion.md) — mapa operativo, contrato y gates.
- [`c4.md`](../c4.md) — niveles 2 y 3 ajustados a los 8 módulos.
- [ADR-0002](ADR-0002-arquitectura-hexagonal.md) — hexagonal dentro de cada módulo.
- [ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md) — integración síncrona entre módulos del marketplace.
- [ADR-0011](ADR-0011-outbox-transaccional.md) — outbox en `shared/`.
