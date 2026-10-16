# ADR-0022: Módulos simulados en proceso para los entornos desplegados

## Estado

Aceptada. Enmienda al [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) sin reemplazarlo.

## Fecha

2026-10-16

## Contexto

- El [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) simula Seguridad con **Prism** (local, puerto `4010`) y Productos, Ventas y Despacho con **respx**, que solo existe dentro de las pruebas.
- En los entornos desplegados en Railway (*staging* y producción, [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md)) ningún servidor responde en esas URLs base: cualquier búsqueda en el catálogo fallaría.
- El equipo evaluó Prism como la herramienta prevista, pero no es utilizable en el entorno desplegado.
- La demo del Hito 3 exige el frontend conectado al backend desplegado, con datos de los módulos.

## Decisión

Mathias (líder del equipo) decidió el 2026-10-16 que **los entornos desplegados simulan los módulos dentro del propio proceso del backend, mediante adaptadores falsos en memoria.**

- **Configuración:** una variable de entorno `MODULES_MODE` con valor `fake` o `http`, definida por entorno. Mientras no existan los módulos reales (hasta el Hito 4), *staging* y producción usan `fake`, porque la demo del Hito 3 corre en producción (H3-20). Cada entorno pasa a `http` cuando su módulo real y sus credenciales estén disponibles.
- **Con `fake`:** el contenedor de dependencias conecta adaptadores falsos en memoria que implementan los **mismos puertos de salida** que los clientes HTTP y reutilizan los datos semilla de las pruebas (`tests/helpers`).
- **Con `http`:** se usan los clientes HTTP reales (subclases de `BaseModuleClient`) contra las URLs base configuradas.
- **Paso a los módulos reales:** es un cambio de configuración, coherente con el [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) y la arquitectura hexagonal ([ADR-0002](ADR-0002-arquitectura-hexagonal.md)).
- **Prism** queda solo para las pruebas `[INT]` locales.
- **Requisito previo:** todo cliente de módulo debe estar detrás de un puerto de salida. Seguridad aún no tiene puerto (pendiente de H3-07); se resuelve primero en H3-09.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Servicio de mocks aparte en Railway (Prism para Seguridad y una aplicación FastAPI pequeña con datos semilla para el resto, por la red privada `*.railway.internal`) | Añade servicios que mantener y pagar y una aplicación más que versionar; además, Prism no es viable en el entorno desplegado |
| Esperar a los módulos reales | Bloquea la demo del Hito 3 (ya descartada en el [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md)) |

## Consecuencias

**Positivas**
- Sin servicios ni costo adicionales.
- Datos de demostración deterministas.
- El paso a los módulos reales es un cambio de configuración.

**Negativas y riesgos aceptados**
- Los clientes HTTP no se ejercitan en los entornos desplegados; solo los cubren las pruebas unitarias con respx.
- Los adaptadores falsos pueden divergir de los contratos reales (mismo riesgo R1 del [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md)).
- Los datos falsos no deben habilitarse nunca en producción una vez que existan los módulos reales.

## Referencias

- [ADR-0017](ADR-0017-mocks-y-urls-base-parametrizadas.md) (decisión que se enmienda)
- [ADR-0020](ADR-0020-despliegue-en-railway-vercel-y-supabase.md) (despliegue)
- [ADR-0002](ADR-0002-arquitectura-hexagonal.md) (puertos y adaptadores)
- `odd/tasks/hito-3.md` (tareas H3-03, H3-07, H3-09 y H3-18)
- [`c4.md`](../c4.md#vista-de-despliegue) (vista de despliegue)
