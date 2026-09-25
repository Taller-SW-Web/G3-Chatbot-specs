# ADR-0001: Backend en Python 3.12 con FastAPI

## Estado

Aceptada

## Fecha

2026-09-24 (aprobación del profesor; cierra el riesgo R6 de `alcance.md`)

## Contexto

- Los lineamientos del curso listan Java Spring Boot, .NET Core o Node.js como tecnologías de backend.
- El núcleo del canal es un orquestador de LLM con tool calling y streaming (SPEC-05), que hace muchas llamadas HTTP concurrentes a los cuatro módulos y al proveedor LLM.
- El equipo ya había diseñado el backend en Python/FastAPI (`chatbot_router.py`, `chatbot_ws_adapter.py`) y el stack no estaba aprobado: era el riesgo R6 del producto.

## Decisión

El backend del Canal Chatbot se implementa en **Python 3.12 con FastAPI**, con este stack (README §1.5):

- Pydantic v2 para los contratos de la API y los esquemas de las herramientas del LLM.
- SQLAlchemy 2 + Alembic para PostgreSQL.
- httpx async para los clientes de los módulos y PyJWT para validar tokens con el JWKS de Seguridad.
- APScheduler para el worker de outbox y los jobs programados.
- pytest + respx para las pruebas.

El profesor aprobó esta elección el 2026-09-24.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Java Spring Boot, .NET Core o Node.js (lineamientos del curso) | El equipo optó por Python/FastAPI y el profesor lo aceptó. Los documentos no registran una comparación detallada |

## Consecuencias

**Positivas**
- FastAPI soporta REST y WebSocket en la misma aplicación, que es justo lo que pide el doble protocolo ([ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md)).
- Los esquemas Pydantic sirven a la vez para validar la API y los argumentos de las herramientas del LLM (SPEC-05 · Req. 6).
- Las llamadas async con httpx encajan con la integración síncrona por API hacia cuatro módulos ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)).

**Negativas y riesgos aceptados**
- El stack difiere del que listan los lineamientos del curso; otros módulos pueden usar otro lenguaje, lo que no afecta porque la integración es solo por API (README §1.3.6).

## Referencias

- `README.md` §1.5 (líneas 137-149)
- `docs/producto/alcance.md` §7 (línea 184), riesgo R6 (línea 238) y pregunta abierta 12 (líneas 281-282)
- `openspec/config.yaml` (contexto: "Backend … Python 3.12, FastAPI, hexagonal")
