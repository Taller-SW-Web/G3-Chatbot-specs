# Definición de Listo y de Terminado — Canal Chatbot

> Aplica a las historias `HU-XXX-NN` de [`historias/`](historias/). Se alinea con la sección *Criterio de completitud* de cada `spec.md` y con las convenciones y el stack de pruebas del [README](../../README.md#5-convenciones).
>
> Roles que validan (sin nombres): **PO** (Product Owner), **QA**, **Tech lead**.

## Definición de Listo (DoR)

Una historia pasa a `Ready` solo si cumple **todos** los puntos:

| # | Criterio | Cómo se verifica | Valida |
|---|---|---|---|
| R1 | La historia cumple INVEST: es independiente o sus dependencias están listadas, negociable, aporta valor visible (o está marcada como **Habilitadora** con su justificación), estimable, pequeña (≤ 8 puntos) y verificable. | Revisión en el refinamiento. | PO |
| R2 | Cada requisito citado existe en `openspec/specs/<capacidad>/spec.md` con al menos un escenario, y cada criterio de aceptación referencia un escenario existente por su nombre exacto (`SPEC-NN · Req. N · Scenario: …`). | Comparación con la spec; la trazabilidad está en [`trazabilidad.md`](trazabilidad.md). | PO |
| R3 | Los contratos externos que consume están en ✅ **o** existe un mock utilizable: Prism para Seguridad, respx con datos semilla para Productos, Ventas y Despacho. | Columna "Dependencias externas" de la historia y [`contratos-integracion.md`](../contratos-integracion.md). | Tech lead |
| R4 | Las reglas de negocio aplicables están identificadas con su ID `RN-XXX-NN` y existen en [`reglas-negocio.md`](reglas-negocio.md). | Columna "Reglas de negocio". | PO |
| R5 | Está estimada en puntos Fibonacci (1, 2, 3, 5, 8) por el equipo. Si supera 8, se divide antes de entrar al ciclo. | Campo Estimate en Linear. | Tech lead |
| R6 | Las dependencias internas (otras historias) y los acuerdos abiertos (`A4`, `A5`, `A6`, `A7`, `A11`, `A12`) están listados y enlazados en Linear como *blocked by* cuando corresponda. | Relaciones en la issue. | Tech lead |
| R7 | La pantalla o el bloque de UI afectado está identificado (`HomePage`, `ChatPage`, `CartPage`, `CheckoutPage`, `OrderHistoryPage`, `Sidebar`, o el `Bloque.tipo` correspondiente) y, si existe, se enlaza el wireframe de Figma. | Descripción de la issue. | PO |
| R8 | Las tareas `[FE]`, `[BE]`, `[INT]` y `[QA]` del desglose de `design.md` están creadas como sub-issues, según la tabla "Asignación del desglose" del archivo de la épica. | Sub-issues en Linear. | Tech lead |
| R9 | Los requisitos no funcionales aplicables de la spec (rendimiento, privacidad, accesibilidad) están anotados en la historia o en sus sub-issues. | Sección *Requisitos no funcionales* de la spec. | QA |

## Definición de Terminado (DoD)

Una historia pasa a `Done` solo si cumple **todos** los niveles aplicables. Los niveles reproducen el *Criterio de completitud* de las specs ("todos los requisitos implementados; todos los escenarios se cumplen y tienen prueba automatizada; RNF aplicables cumplidos; sin funcionalidades fuera del alcance") y lo detallan.

### 1. Funcional y BDD

| # | Criterio | Valida |
|---|---|---|
| D1.1 | Todos los escenarios citados en los criterios de aceptación se cumplen. | QA |
| D1.2 | Cada escenario tiene **al menos una prueba automatizada que lo referencia por su nombre** (README §5): pytest en backend, Vitest + Testing Library en frontend, y Playwright cuando la spec pide E2E (por ejemplo, registro exitoso, login con MFA y retoma del checkout, pago aprobado y pago rechazado 3 veces). | QA |
| D1.3 | Las reglas de negocio citadas se cumplen con sus valores exactos (límites, plazos, reintentos), verificados por prueba. | QA |
| D1.4 | No se incorporó funcionalidad fuera del alcance de la spec ni de [`alcance.md`](alcance.md#5-fuera-de-alcance-consolidado). | PO |
| D1.5 | El PO aceptó la historia en la demo o la revisión del ciclo. | PO |

### 2. Integración y contratos

| # | Criterio | Valida |
|---|---|---|
| D2.1 | Las llamadas a otros módulos pasan pruebas de integración con respx (Productos, Ventas, Despacho) o contra Prism (Seguridad), incluidos los códigos de error que la spec menciona (`4xx`, `5xx`, timeouts). | QA |
| D2.2 | Los timeouts configurados coinciden con la spec (p. ej., Seguridad 5 s, Productos 4 s y 3 s, Despacho 4 s, Ventas 5 s, introspección 3 s, LLM 15 s). | Tech lead |
| D2.3 | Toda operación que crea algo en otro módulo o mueve dinero envía `Idempotency-Key`, y hay prueba de doble envío. | QA |
| D2.4 | Los errores propios se devuelven como `application/problem+json` con `code`, y los errores de Ventas (`codigo`) se normalizan a `code`. | Tech lead |
| D2.5 | Si la historia consume un endpoint 🟡, el cliente está aislado detrás de un puerto y la issue mantiene la etiqueta `contrato:provisional` hasta homologarlo. | Tech lead |
| D2.6 | Ningún camino de fallo asume disponibilidad: si un módulo no responde, la operación se rechaza de forma controlada y se informa al cliente (README §1.3, principio 7). | QA |

### 3. Seguridad y datos personales

| # | Criterio | Valida |
|---|---|---|
| D3.1 | La identidad del cliente se toma siempre del token (`sub`); las lecturas de recursos ajenos devuelven la misma respuesta que un recurso inexistente. | Tech lead |
| D3.2 | Contraseñas, OTP y datos de tarjeta no aparecen en la BD, en los logs, en las trazas ni en el contexto del LLM (verificado por prueba cuando la spec lo exige: SPEC-01, SPEC-04, SPEC-05, SPEC-14). | QA |
| D3.3 | Correo, celular y documento se muestran enmascarados donde la spec lo indica, y no se envían al LLM. | QA |
| D3.4 | Todo contenido que proviene del LLM o de otros módulos se sanitiza antes de renderizarse (sin `dangerouslySetInnerHTML` con texto no controlado). | Tech lead |
| D3.5 | Las acciones con efecto económico o irreversible exigen confirmación explícita en la UI (SPEC-05 · Req. 6). | QA |

### 4. UX/UI

| # | Criterio | Valida |
|---|---|---|
| D4.1 | La pantalla o el bloque coincide con el wireframe mobile-first y funciona en móvil y escritorio. | PO |
| D4.2 | Accesibilidad: navegación por teclado, `label` asociados, errores anunciados con `aria-live`, contraste AA y objetivos táctiles de al menos 44×44 px cuando la spec lo pide; revisión con axe sin errores críticos. | QA |
| D4.3 | Los textos visibles coinciden con los de la spec (mensajes de error, confirmaciones), en español neutro, con moneda "S/" y fechas en hora de Lima. | PO |
| D4.4 | Los estados de carga, vacío, error y "no disponible" están implementados. | QA |

### 5. Código y CI

| # | Criterio | Valida |
|---|---|---|
| D5.1 | El código sigue la arquitectura hexagonal (dominio y casos de uso sin dependencias de framework; adaptadores en `outbound/`/`adapters/`). | Tech lead |
| D5.2 | La revisión de código está aprobada por al menos una persona distinta del autor. | Tech lead |
| D5.3 | El pipeline de CI está en verde: linters, tipado, pruebas unitarias y de integración, y E2E cuando aplique. | Tech lead |
| D5.4 | Si la historia toca el prompt, el modelo o las herramientas del LLM, el conjunto de evaluación (`evals/intenciones.jsonl`, ≥ 120 frases) mantiene una precisión de intención ≥ 90 % en CI (SPEC-05 · RNF). | QA |
| D5.5 | Los RNF de rendimiento aplicables se midieron (p95) y cumplen el umbral de la spec; en Hito 5–6 se incluyen en las pruebas de performance. | QA |
| D5.6 | Las migraciones de base de datos (Alembic) son reversibles y están incluidas. | Tech lead |

### 6. Documentación

| # | Criterio | Valida |
|---|---|---|
| D6.1 | Si el comportamiento implementado difiere de la spec, se abrió un cambio en `openspec/changes/<cambio>/` (flujo SDD); la spec no se edita a mano. | Tech lead |
| D6.2 | Si cambió un contrato o se resolvió un acuerdo, se actualizó [`contratos-integracion.md`](../contratos-integracion.md) (estado ✅/🟡 y tabla de acuerdos). | Tech lead |
| D6.3 | Si cambió una regla de negocio en la spec, se actualizó [`reglas-negocio.md`](reglas-negocio.md) y, si aplica, [`trazabilidad.md`](trazabilidad.md). | PO |
| D6.4 | Las nuevas variables de entorno o configuraciones (`config/*.yaml`, timeouts) están documentadas en el repositorio correspondiente. | Tech lead |
