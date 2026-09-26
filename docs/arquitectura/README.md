# Arquitectura — Canal Chatbot

Esta carpeta documenta la arquitectura del Canal Chatbot con dos herramientas complementarias: el **modelo C4**, que muestra *qué* piezas existen y cómo se comunican, y los **ADR**, que explican *por qué* se decidió así.

## Contenido

| Documento | Para qué sirve | Lectores principales |
|---|---|---|
| [`c4.md`](c4.md) | Diagramas C4 en Mermaid: contexto (nivel 1), contenedores (nivel 2), entorno de desarrollo y componentes del backend (nivel 3, en dos vistas). Cada diagrama trae una tabla de elementos con su spec de origen | Todo el equipo, docentes, otros módulos |
| [`adr/`](adr/README.md) | Registro de decisiones de arquitectura (formato de Michael Nygard): 18 aceptadas y 1 propuesta, con índice y [plantilla](adr/plantilla.md) | Tech lead, backend, frontend |

## Relación con el resto del repositorio

- **[README §1](../../README.md#1-arquitectura) sigue siendo la vista de entrada.** Tiene los diagramas hexagonales de frontend y backend, los principios, el stack y la decisión del token. Esta carpeta no los repite: el C4 los ubica en niveles y los ADR registran el contexto, las alternativas y las consecuencias de cada decisión.
- **Las specs son la fuente de verdad.** Los componentes y nombres del C4 salen de los `design.md` de [`openspec/specs/`](../../openspec/specs/), y los contratos de [`contratos-integracion.md`](../contratos-integracion.md). Si un diagrama o un ADR contradice a una spec, manda la spec y este documento se corrige.
- **Los ADR no crean decisiones.** Documentan las ya tomadas en las specs o en los documentos transversales. Un cambio de comportamiento se hace primero en las specs mediante un cambio de OpenSpec (`openspec/changes/`), igual que en la [capa de producto](../producto/README.md) y el [diseño conversacional](../conversacion/README.md).
- **Flujos dinámicos:** las secuencias (turno de texto, checkout y pago) están en [`flujos-conversacion.md`](../conversacion/flujos-conversacion.md) y no se duplican aquí.

## Cómo mantenerlo

1. Si un cambio de OpenSpec agrega, renombra o quita un componente de un `design.md`, actualiza la tabla y el diagrama correspondiente de `c4.md`.
2. Si cambia una decisión, crea un ADR nuevo con la [plantilla](adr/plantilla.md) y marca el anterior como **Reemplazada por ADR-NNNN**.
3. Antes de publicar, valida los diagramas: `npx -y @mermaid-js/mermaid-cli -i docs/arquitectura/c4.md -o /tmp/c4.md` renderiza todos los bloques `mermaid` del archivo.

## Preguntas abiertas

Consolidadas de [`c4.md`](c4.md#preguntas-abiertas) y del [ADR-0018](adr/ADR-0018-agrupacion-del-nucleo-en-ocho-casos-de-uso.md):

1. **Topología del worker:** ¿el `OutboxWorker` y los jobs corren como proceso separado o dentro de la API? Con varias réplicas de la API, un scheduler en cada una duplicaría los jobs.
2. **Despliegue:** ningún documento define dónde se despliegan frontend, backend y base de datos, por eso no hay vista de despliegue.
3. **Casos de uso de identidad:** la agrupación en 8 casos de uso (Propuesta) no cubre SPEC-01 a SPEC-04.
