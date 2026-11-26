# Arquitectura — Canal Chatbot

Esta carpeta documenta la arquitectura del Canal Chatbot con tres herramientas complementarias: el **modelo C4**, que muestra *qué* piezas existen y cómo se comunican; la **vista de modularización**, que explica cómo se corta el código por capacidad; y los **ADR**, que explican *por qué* se decidió así.

## Contenido

| Documento | Para qué sirve | Lectores principales |
|---|---|---|
| [`modularizacion.md`](modularizacion.md) | Monolito modular por capacidad: los 8 módulos, el DAG, `shared/`, el contrato backend↔frontend, auto-discovery y gates. Es la vista de entrada para trabajar en el código | Todo el equipo, backend, frontend |
| [`c4.md`](c4.md) | Diagramas C4 en Mermaid: contexto (nivel 1), contenedores (nivel 2 con los 8 módulos), entorno de desarrollo, despliegue y componentes (nivel 3: módulos y fronteras). Cada diagrama trae una tabla de elementos con su spec de origen | Todo el equipo, docentes, otros módulos |
| [`adr/`](adr/README.md) | Registro de decisiones de arquitectura (formato de Michael Nygard): 29 aceptadas, 1 reemplazada y 1 propuesta, con índice y [plantilla](adr/plantilla.md) | Tech lead, backend, frontend |

## Relación con el resto del repositorio

- **Las specs son la fuente de verdad del comportamiento.** Los componentes, rutas y estados del C4 y de la vista de modularización salen de los `design.md` de [`openspec/specs/`](../../openspec/specs/) y de los contratos de [`contratos-integracion.md`](../contratos-integracion.md). Si un diagrama o un ADR contradice una spec, manda la spec y este documento se corrige.
- **El corte primario es por capacidad.** El [ADR-0025](adr/ADR-0025-monolito-modular-por-capacidad.md) homologa el ADR-0024 del backend: 8 módulos con el mismo id en backend y frontend, `shared/` como kernel y hexagonal dentro de cada módulo ([ADR-0002](adr/ADR-0002-arquitectura-hexagonal.md)).
- **Los ADR no crean decisiones.** Documentan las ya tomadas en las specs o en los documentos transversales. Un cambio de comportamiento se hace primero en las specs mediante un cambio de OpenSpec (`openspec/changes/`), igual que en la [capa de producto](../producto/README.md) y el [diseño conversacional](../conversacion/README.md).
- **Flujos dinámicos:** las secuencias (turno de texto, checkout y pago) están en [`flujos-conversacion.md`](../conversacion/flujos-conversacion.md) y no se duplican aquí.
- **Cómo se trabaja:** el flujo paso a paso, la Definition of Done y la checklist de PR están en [`docs/flujo-de-trabajo.md`](../flujo-de-trabajo.md) y en [`AGENTS.md`](../../AGENTS.md).

## Cómo mantenerlo

1. Si un cambio de OpenSpec agrega, renombra o quita un módulo, una ruta o un componente, actualiza `modularizacion.md`, la tabla y el diagrama correspondiente de `c4.md`, y el `MODULE.md` del módulo.
2. Si cambia el DAG o una capacidad, actualiza `modules.manifest.json` en **ambos** repos y la tabla de §3 de `modularizacion.md`.
3. Si cambia una decisión, crea un ADR nuevo con la [plantilla](adr/plantilla.md) y marca el anterior como **Reemplazada por ADR-NNNN**.
4. Antes de publicar, valida los diagramas: `npx -y @mermaid-js/mermaid-cli -i docs/arquitectura/c4.md -o /tmp/c4.md` renderiza todos los bloques `mermaid` del archivo.
5. Las correcciones de drift de specs se registran en la auditoría vigente: [`auditoria-specs-2026-11.md`](../auditoria-specs-2026-11.md).

## Preguntas abiertas

1. **Verificación cruzada de OpenAPI.** El manifiesto del frontend declara endpoints y existe un gate de contrato por módulo, pero la cobertura es parcial. El test manual (`api-rutas-contrato.test.ts`) incluye `/contacto/celular/verificar-otp`, ya implementado y mergeado (D1). ¿Se convierte el gate en bloqueante para todos los endpoints antes del cierre?
2. ✅ **SPEC-04 y SPEC-23.** Resueltas e implementadas el 2026-11-21: OTP, `CheckoutGuard`, endpoints de adjuntos y `AttachmentStorage` están en `development` (backend #141 · `b75fbea6`, frontend #109 · `7432d463`). El detalle está en [`auditoria-specs-2026-11.md`](../auditoria-specs-2026-11.md) §5.
3. **`shared/` y el worker.** El worker de outbox vive en `shared/`; si crece con jobs de un módulo concreto, hay que decidir si se mueve al módulo dueño o se queda como kernel.
