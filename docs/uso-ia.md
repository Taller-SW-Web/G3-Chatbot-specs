# Uso de IA y código generado

> Explica las dos formas en que el proyecto usa inteligencia artificial: como parte del producto (el asistente conversacional) y como apoyo para especificar, programar y revisar. Todo lo que se afirma aquí tiene respaldo en los repositorios; lo que falta completar está marcado como **[completar]**.

## 1. IA dentro del producto: el asistente Botleta

El Canal Chatbot es un asistente de compras en lenguaje natural. El backend interpreta cada mensaje con un LLM que elige herramientas del sistema (*tool calling*) y responde en streaming. La decisión está en [ADR-0005](arquitectura/adr/ADR-0005-llm-con-tool-calling-detras-de-llmprovider.md) y el comportamiento en [SPEC-05 `motor-conversacion`](../openspec/specs/motor-conversacion/spec.md).

### 1.1 Cómo funciona un turno

1. El cliente envía un mensaje: `POST /api/v1/chat/conversaciones/{id}/mensajes`.
2. El backend arma el contexto acotado (system prompt, resumen y últimos mensajes) y el catálogo de herramientas del hito, y llama al modelo a través del puerto `LLMProvider`.
3. Si el modelo pide una herramienta (buscar productos, ver el detalle, agregar al carrito, solicitar el registro), el backend valida los argumentos, la ejecuta y le devuelve el resultado. El bucle tiene un máximo de 5 iteraciones por turno.
4. La respuesta llega al navegador por SSE en la misma respuesta del `POST` ([ADR-0021](arquitectura/adr/ADR-0021-streaming-por-sse-en-la-respuesta-del-post.md)): eventos `token` con el texto y `bloque` con los datos estructurados (carrusel, carrito, formularios).

### 1.2 Proveedor y configuración

| Aspecto | Valor vigente | Fuente |
|---|---|---|
| Proveedor | OpenAI (`OpenAILLMProvider` en el código; `OpenAIProvider` en el ADR), detrás del puerto `LLMProvider`; `ClaudeProvider` previsto sin implementar | ADR-0005, enmienda del 2026-10-11 |
| Modelo | `gpt-6-luna` | ADR-0005 |
| API | Responses API, con `store=false` (el proveedor no guarda la conversación) | ADR-0005, enmienda del 2026-10-16 |
| Razonamiento | `LLM_REASONING_EFFORT=none` por defecto | ADR-0005, enmienda del 2026-10-16 |
| Temperatura | 0,6 por defecto (`LLM_TEMPERATURE`) | ADR-0005, enmienda del 2026-10-11 |
| Clave | Solo en el backend (`LLM_API_KEY`), nunca en el frontend | ADR-0005 |

Cambiar de proveedor o de modelo es configuración, no código: el motor de conversación solo conoce el puerto.

### 1.3 Controles para que la IA no invente ni actúe de más

| Riesgo | Control | Dónde |
|---|---|---|
| El modelo inventa precios, stock o descuentos | Los datos comerciales salen siempre de las herramientas y se muestran en bloques estructurados, no en el texto del LLM. `OutputValidator` compara los montos, porcentajes y descuentos del texto con los resultados; está implementado y entra al turno con H3-11 (PR #45 del backend, sin mergear al 2026-10-17) | ADR-0005; `src/domain/services/output_validator.py` (backend) |
| El modelo ejecuta acciones no deseadas | Argumentos validados, identidad tomada siempre del token (nunca de los argumentos del modelo) y confirmación en pantalla para acciones con efecto económico o irreversible | ADR-0005; SPEC-05 |
| *Prompt injection* desde los datos | Los resultados de las herramientas se envuelven en `<datos_herramienta>` y el system prompt indica tratarlos como datos, no como instrucciones | `src/application/prompts/system_prompt.py` (backend) |
| Datos sensibles hacia el proveedor | `SensitiveDataFilter` redacta contraseñas, tarjetas y documentos de identidad antes de enviar el texto al LLM | `src/domain/services/sensitive_data_filter.py` (backend); [`privacidad.md`](conversacion/privacidad.md) |
| El LLM no responde | Modo degradado: respuesta de respaldo con acciones rápidas; los botones siguen funcionando sin LLM | SPEC-05; ADR-0021 |
| Flujo transfronterizo de datos | El proveedor procesa fuera del Perú; se informa al cliente según la Ley 29733 | [`privacidad.md`](conversacion/privacidad.md) §3 |

### 1.4 Prueba con el modelo real

El 2026-10-16 se probó por primera vez contra la API real de OpenAI ([`odd/tasks/hito-3.md`](../odd/tasks/hito-3.md), séptimo tramo de H3-10). De esa prueba salieron decisiones concretas:

- Pasar de Chat Completions a la Responses API, porque `gpt-6-luna` rechazaba herramientas al razonar.
- Restringir la descripción de `solicitar_registro`, que el modelo usaba fuera de lugar.
- Asignar `id` a los bloques que llegaban sin él.

Resultado medido: turnos de 3 a 5 s; en el navegador, primer token a 1,19 s.

Pendiente: el conjunto de evaluación de intenciones (`evals/intenciones.jsonl`, al menos 120 frases con 90 % de acierto en CI, según ADR-0005) todavía no existe; `tests/evals/` está vacío.

## 2. IA en el desarrollo: cómo se especificó y programó

### 2.1 Primero la especificación (SDD con OpenSpec)

El equipo trabaja con desarrollo guiado por especificaciones (*Spec-Driven Development*). La fuente de verdad es este repositorio, gestionado con [OpenSpec](https://github.com/Fission-AI/OpenSpec) y el flujo SDD de gentle-ai ([README §6](../README.md#6-cómo-trabajar-con-openspec)):

1. **Specs base:** 24 capacidades en `openspec/specs/<capacidad>/`, cada una con `spec.md` (requisitos con escenarios Dado, Cuando y Entonces) y `design.md` (integraciones, frontend, backend y desglose en tareas).
2. **Cambios:** todo cambio de comportamiento se propone en `openspec/changes/<cambio>/` con propuesta, specs delta, diseño y tareas. Ningún requisito se edita a mano en la spec base.
3. **Validación:** `npx @fission-ai/openspec validate --strict` revisa el formato antes de integrar.
4. **Archivo:** al aprobarse, el cambio se fusiona en la spec base y queda en `openspec/changes/archive/` con su fecha. Ejemplo: `2026-10-16-ajustar-calificacion-compra-y-entrega`, que separó la calificación de la entrega y la valoración de la compra (SPEC-24).
5. **Trazabilidad:** cada requisito lleva su línea *Trazabilidad*. `docs/producto/trazabilidad.md` enlaza requisito, historia de usuario, regla de negocio y endpoint, y [`casos-prueba-hito-3.md`](casos-prueba-hito-3.md) tiene un caso por escenario (126 casos).

Con esto, la IA genera código a partir de requisitos escritos, versionados y revisados, no a partir de pedidos sueltos.

### 2.2 Herramientas de IA usadas por el equipo

| Integrante | Herramienta | Uso principal |
|---|---|---|
| Nikol | Claude Code | Documentación y specs (evidencia del Hito 2, propuestas de UX, correcciones de SPEC-24), verificación de commits y gestión de conversaciones (H3-15) |
| Mathias | [completar] | [completar] |
| Sebastian | [completar] | [completar] |
| Sonny | [completar] | [completar] |
| David | [completar] | [completar] |
| Alonso | Deska (Codex) | Apoyo en la implementación y revisión de H3-11: integración de herramientas y acciones rápidas en backend y frontend y ejecución de pruebas. |
| Diego | Gemini con Opencode | Implementación y revisión de frontend y backend: design system (tokens y componentes base, H2-08), páginas de carrito, checkout e historial, `ChatPage`/`Sidebar` y autenticación (login, MFA y sesión, H3-14) |

Además del asistente de código, el flujo usa:

- **gentle-ai:** orquesta el flujo SDD (exploración, propuesta, specs delta, diseño, tareas, aplicación, verificación y archivo).
- **Engram:** memoria persistente donde se replican los planes de `odd/tasks/` entre sesiones.

### 2.3 Cómo se genera el código: orquestador y roles delegados

Las tareas grandes se ejecutan con un agente orquestador que reparte el trabajo en roles delegados. La columna *Ruta* de [`odd/tasks/hito-3.md`](../odd/tasks/hito-3.md) registra cuál se usó en cada tramo:

- **Mapeador:** lee el código existente y resume dónde tocar, sin escribir.
- **Redactor:** escribe el código o la documentación de un tramo acotado.
- **Revisor:** revisa un PR en modo de solo lectura y reporta bloqueantes.
- **Orquestador:** lee el código central, vuelve a ejecutar las pruebas y aplica o pide correcciones antes de dar por cerrado el tramo.

Las decisiones de diseño no las toma la IA: quedan registradas con su responsable humano. Por ejemplo, Mathias decidió el transporte SSE (ADR-0021), el proveedor OpenAI y la temperatura (enmiendas del ADR-0005), y la PO decidió las correcciones de SPEC-24.

### 2.4 Cómo se controla el código generado

Ningún código generado entra sin pasar por los mismos controles que el código escrito a mano:

| Control | Cómo se aplica | Evidencia |
|---|---|---|
| Specs como contrato | El código implementa requisitos y escenarios ya escritos; las pruebas citan el escenario que cubren | `docs/casos-prueba-hito-3.md` |
| Pruebas | Backend: más de 420 pruebas unitarias y más de 30 de integración contra PostgreSQL 18. Frontend: pruebas unitarias con Vitest y E2E con Playwright; las E2E de humo del hito están en revisión (PR #20 del frontend) | `odd/tasks/hito-3.md` (cierres de H3-10 y H3-15); `tests/` de cada repo |
| CI obligatorio | `pytest` en el backend; `lint`, `typecheck`, `test` y `build` en el frontend | `.github/workflows/` de cada repo |
| Revisión humana | `main` y `development` protegidas: PR obligatorio con una aprobación, y se descartan aprobaciones si llegan commits nuevos | Cierre de H3-02 en `odd/tasks/hito-3.md` |
| Prueba manual | Los tramos con riesgo se verifican por HTTP o en el navegador contra una base migrada y, desde el 2026-10-16, contra el modelo real | Cierres de H3-10 y H3-15 |
| Reglas de estilo | Código del backend en inglés, sin referencias a hitos ni tareas; identificadores de base de datos en inglés | Restricciones de `odd/tasks/hito-3.md` |

### 2.5 Ejemplos de correcciones sobre código generado

La revisión humana encontró y corrigió fallas reales en código asistido por IA:

- **Filtro de datos sensibles (PR #35, H3-08):** la primera versión dejaba pasar contraseñas y tarjetas hacia el LLM. La revisión pidió cambios y el PR se aprobó tras la corrección (`d50a3c8`).
- **Clientes de Productos (PR #39, H3-06):** las respuestas 4xx llegaban como datos válidos y una prueba no ejercitaba el cliente. Se corrigió antes del merge (`8cc6e61`).
- **Herramienta fuera de lugar (H3-10, `d215350`):** el modelo mostraba el formulario de registro ante preguntas de producto. Se corrigió la descripción de la herramienta y se verificó contra OpenAI.

## 3. Límites y riesgos aceptados

- La salida del LLM no es determinista; cualquier cambio de prompt o de modelo debería pasar por la evaluación de intenciones, que aún no existe (sección 1.4).
- Costo y latencia por turno (riesgo R9 de `docs/producto/alcance.md`): se acotan con contexto limitado y un timeout de 15 s por llamada al modelo (`LLM_TIMEOUT_SECONDS`). El límite de mensajes por minuto (SPEC-05, límites de uso) está especificado, pero aún no está implementado en el backend.
- El código asistido por IA puede verse correcto y fallar en casos borde; por eso cada tramo se cierra con pruebas, CI y una aprobación humana, y los hallazgos se registran en `odd/tasks/`.
