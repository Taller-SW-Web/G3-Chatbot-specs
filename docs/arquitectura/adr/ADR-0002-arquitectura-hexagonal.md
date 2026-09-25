# ADR-0002: Arquitectura hexagonal en frontend y backend

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; el README la incorpora como arquitectura definida por el equipo, sin fecha)

## Contexto

- El canal depende de cuatro módulos externos cuyos contratos están en distinto grado de madurez: Productos sigue provisional (A5) y el seguimiento de Despacho está abierto (A11).
- El proveedor LLM debe poder cambiarse por configuración (Claude u OpenAI, SPEC-05 · RNF *Configuración*).
- Hay piezas simuladas que se quieren reemplazar más adelante: el pago (SPEC-14) y el SMS del OTP (SPEC-04).
- Cada escenario DADO/CUANDO/ENTONCES debe tener al menos una prueba automatizada (README §5).

## Decisión

El frontend y el backend se organizan en **arquitectura hexagonal (puertos y adaptadores)**, cada uno con su núcleo de dominio y casos de uso independientes del framework (README §1):

- **Backend:** `domain/` (entidades, servicios, value objects), `application/` (casos de uso), `adapters/inbound/` (REST `chatbot_router.py`, WebSocket `chatbot_ws_adapter.py`, ambos detrás de `ChatbotServicePort`) y `adapters/outbound/`. Los puertos outbound incluyen `LLMProvider`, `PaymentGateway`, `SmsSender` y `EmailSender`, más los clientes de módulos y la persistencia `conversacion_postgres_adapter`.
- **Frontend:** `inbound/` (AppShell, App Router), `application/` (casos de uso como `enviarMensaje`), `domain/` (entidades y puertos `ChatbotApiPort`, `WebSocketPort`), `outbound/` (adaptadores Axios y WebSocket) e `infrastructure/` (`container.ts`, `apiConfig.ts`).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Arquitectura en capas acoplada al framework (*alternativa estándar, no documentada*) | Ataría los casos de uso a FastAPI o Next.js y dificultaría cambiar el LLM, el simulador de pago o los contratos provisionales sin tocar el núcleo |

## Consecuencias

**Positivas**
- Un contrato provisional que cambia solo afecta a su adaptador; el riesgo R1 (A5) se mitiga aislando `ProductosClient` detrás de un puerto (`alcance.md` §9).
- Las dos vías de entrada (texto con LLM y botón directo) llegan al mismo caso de uso (README §1.3.3).
- Los casos de uso se prueban con adaptadores falsos (respx, `EmailSender` falso, LLM mockeado).

**Negativas y riesgos aceptados**
- Más archivos e indirección que una aplicación en capas simple.
- La agrupación concreta en casos de uso sigue siendo una propuesta ([ADR-0018](ADR-0018-agrupacion-del-nucleo-en-ocho-casos-de-uso.md)).

## Referencias

- `README.md` §1 (líneas 32-114), §1.5 (líneas 141-142) y nota de la línea 28
- `openspec/specs/motor-conversacion/design.md` (Frontend y Backend)
- `docs/producto/alcance.md` §9, riesgo R1
- [Modelo C4, nivel 3](../c4.md#nivel-3--componentes-del-backend)
