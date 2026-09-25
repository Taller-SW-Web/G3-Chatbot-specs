# ADR-0005: LLM con tool calling detrás del puerto `LLMProvider`; datos comerciales solo desde herramientas

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; decisión de SPEC-05, sin fecha)

## Contexto

- El curso pide consulta conversacional de productos en lenguaje natural (README §4).
- El catálogo de intenciones es amplio: 56 intenciones con variantes peruanas (`intenciones.md`), con referencias al contexto ("agrega el segundo en talla 42") y extracción de parámetros.
- Un LLM puede inventar precios, stock o estados, ejecutar acciones no deseadas y ser objeto de prompt injection (SPEC-05 · Contexto).
- El proveedor debe poder cambiarse (Claude u OpenAI) y la clave nunca va al frontend.

## Decisión

- La interpretación usa un **LLM con tool calling**: el backend envía el mensaje, el contexto acotado (resumen y últimos 12 mensajes) y el catálogo de herramientas, y ejecuta la herramienta que el LLM elige (`InterpretarYResponderUseCase`, `ToolRegistry`; máx. 5 iteraciones).
- El proveedor queda detrás del puerto outbound **`LLMProvider`**, con las implementaciones `ClaudeProvider` y `OpenAIProvider`. Proveedor, modelo, temperatura (≤ 0,3), `max_tokens` y timeouts se configuran por variables de entorno.
- **Veracidad:** precios, stock, descuentos, totales y estados provienen siempre de las herramientas y se renderizan en bloques estructurados, no con el texto del LLM. `OutputValidator` compara los montos del texto con los resultados y corrige en el evento `fin`.
- **Ejecución segura:** argumentos validados con Pydantic, identidad tomada siempre del token, sesión exigida en herramientas protegidas y confirmación en la UI para acciones con efecto económico o irreversible. El pago, los reclamos y las devoluciones solo se envían con botón.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| NLU clásico con clasificador de intenciones y extracción de entidades (*alternativa estándar, no documentada*) | Exigiría entrenar y mantener un modelo propio, y el entrenamiento o *fine-tuning* está fuera de alcance (SPEC-05). Resuelve peor las referencias al contexto y la redacción natural |
| Acoplar el backend al SDK de un solo proveedor (*alternativa estándar, no documentada*) | Impediría cambiar de proveedor por configuración, como exige SPEC-05 · RNF *Configuración* |

## Consecuencias

**Positivas**
- Un mismo motor cubre las 56 intenciones sin reglas por intención; la precisión se controla con `evals/intenciones.jsonl` (≥ 120 frases, ≥ 90 % en CI).
- Si el LLM falla, las acciones directas por botón y el modo degradado siguen funcionando ([ADR-0007](ADR-0007-rest-para-acciones-y-websocket-para-streaming.md)).

**Negativas y riesgos aceptados**
- Costo y latencia por turno (riesgo R9): se acotan con rate limit (20 mensajes/min), contexto limitado y timeout de 15 s.
- Los proveedores procesan datos fuera del Perú, un flujo transfronterizo que debe informarse (`privacidad.md` §3).
- La salida del LLM es no determinista: cualquier cambio de prompt o modelo debe pasar la evaluación en CI.

## Referencias

- `openspec/specs/motor-conversacion/spec.md` Contexto (líneas 19-24), Req. 3, 6, 7 (líneas 107-228) y RNF (líneas 321-328)
- `openspec/specs/motor-conversacion/design.md` (Backend)
- `README.md` §1.3.4 (línea 121) y §1.5 (línea 143)
- `docs/conversacion/privacidad.md` §3 y §8
- `docs/producto/alcance.md` §9, riesgo R9
