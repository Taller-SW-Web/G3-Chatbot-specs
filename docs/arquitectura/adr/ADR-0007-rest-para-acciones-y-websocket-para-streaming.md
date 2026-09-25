# ADR-0007: REST para acciones y WebSocket solo para el streaming, con *fallback* y modo degradado

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; decisión de SPEC-05 y del README, sin fecha)

## Contexto

- La experiencia esperada es la de un chat que "escribe en vivo" (SPEC-05 · RNF: primer fragmento p95 ≤ 2 s; turno completo p95 ≤ 6 s).
- Las acciones con efecto (agregar al carrito, pagar, reclamar) deben ser idempotentes, auditables y aplicar la sesión y la confirmación de la UI.
- El WebSocket puede no conectar (redes móviles, proxies) y el LLM puede fallar o exceder su tiempo.
- El backend debe poder correr con varias réplicas.

## Decisión

- **REST** (`chatbot_router.py` y routers por recurso, prefijo `/api/v1`) atiende todo lo que crea o modifica estado y las lecturas puntuales. Enviar un mensaje responde `202 {mensajeId}` de inmediato.
- **WebSocket** (`chatbot_ws_adapter.py`, `wss://<host>/api/v1/chat/ws?conversacionId=<id>`, autenticado con el mismo `accessToken`) se usa **únicamente** para transmitir la respuesta del asistente con los eventos `token`, `bloque`, `fin` y `error`. El cliente nunca envía mensajes por este canal y ninguna acción con efecto se ejecuta por él.
- **Una sola lógica:** texto libre (el LLM elige la herramienta) y botones (`ActionDispatcher`, sin LLM ni WebSocket) ejecutan el mismo caso de uso.
- **Fallback:** si el WebSocket no conecta, el frontend reintenta 2 veces con backoff y luego hace *polling* de `GET /chat/conversaciones/{id}/mensajes?desde=` cada 2 s. Al reconectar, el backend reenvía solo lo que falta del turno.
- **Modo degradado:** si el LLM excede 15 s, falla o no está configurado, `DegradedMode` responde por REST con un menú de acciones rápidas y un intérprete de palabras clave.
- El estado de la conversación vive en PostgreSQL, no en memoria, para permitir varias réplicas y varias pestañas por conversación.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Todo por WebSocket, incluidas las acciones (*alternativa estándar, no documentada*) | Descartado por el principio 2 del README: las acciones con efecto no viajan por WebSocket |
| Solo REST con *polling*, sin streaming (*alternativa estándar, no documentada*) | No da el efecto "escribiendo en vivo" ni el primer fragmento en ≤ 2 s. Se conserva como *fallback* |
| Server-Sent Events (*alternativa estándar, no documentada*) | Los documentos no la evalúan; la arquitectura del equipo fijó WebSocket |

## Consecuencias

**Positivas**
- Las operaciones con efecto conservan idempotencia, códigos `problem+json` y control de sesión propios de REST.
- El canal sigue siendo útil sin WebSocket y sin LLM.

**Negativas y riesgos aceptados**
- Dos protocolos que probar, incluido el caso de reconexión sin duplicar texto.
- El token viaja en el *handshake* del WebSocket (query param o subprotocolo), con la exposición que eso implique en logs de infraestructura.

## Referencias

- `README.md` §1.3, principios 2 y 3 (líneas 119-120)
- `openspec/specs/motor-conversacion/spec.md` Contexto (líneas 19-22), Req. 4, 8 y 10, RNF *Rendimiento* y *Escalabilidad del WebSocket* (líneas 321 y 327)
- `docs/contratos-integracion.md` §2.1 (líneas 35-57)
- `docs/conversacion/flujos-conversacion.md` (a) y (e)
