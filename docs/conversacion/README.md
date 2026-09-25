# Diseño conversacional — Canal Chatbot

Esta carpeta define **cómo conversa** el asistente del canal: su persona y tono, las intenciones que atiende, diálogos de ejemplo, flujos, indicadores y el tratamiento de datos personales.

## Relación con las specs

- **Las specs son el contrato de comportamiento.** Qué hace el sistema, con qué herramientas, límites, códigos de error y textos obligatorios se define solo en `openspec/specs/<capacidad>/spec.md`, sobre todo en [SPEC-05 `motor-conversacion`](../../openspec/specs/motor-conversacion/spec.md).
- **Estos documentos son diseño conversacional** sobre ese contrato: tono, microcopy, ejemplos, métricas y criterios de privacidad. **No pueden contradecir a las specs.** Si un texto de aquí difiere de uno fijado en una spec, manda la spec y este documento se corrige.
- Cuando un documento necesita una decisión que las specs no toman, la deja como **propuesta** y la registra en [Preguntas abiertas](#preguntas-abiertas). Si una propuesta cambia comportamiento, se lleva a las specs mediante un cambio de OpenSpec (`openspec/changes/`), igual que en la [capa de producto](../producto/README.md).
- El único cambio de comportamiento que acompañó a esta carpeta es **SPEC-05 · Req. 12** (*Presentación del asistente y aviso de privacidad*) y la línea *Idioma* de los RNF de SPEC-05, reflejados en la historia HU-CNV-13 y las reglas RN-CNV-19 a RN-CNV-21.

## Contenido

| Documento | Para qué sirve | Lectores principales |
|---|---|---|
| [`persona-tono.md`](persona-tono.md) | Identidad de "Botleta", personalidad, voz, política de emojis, longitud en móvil, patrones de mensaje, tono en contextos sensibles y **microcopy canónico** | Todo el equipo, redacción del prompt |
| [`intenciones.md`](intenciones.md) | **56 intenciones** (46 de negocio y 10 de sistema) con herramienta, slots, sesión, confirmación y spec; catálogo de entidades; **281 frases** de ejemplo y formato de `evals/intenciones.jsonl` | Backend (prompt y `ToolRegistry`), QA |
| [`dialogos-ejemplo.md`](dialogos-ejemplo.md) | **15 diálogos** de ejemplo con herramientas, bloques y referencias a escenarios | Todo el equipo, QA, demo |
| [`flujos-conversacion.md`](flujos-conversacion.md) | **5 diagramas** Mermaid: estados globales, descubrimiento → carrito, checkout y pago, postventa y secuencia de un turno | Tech lead, frontend, backend |
| [`kpis.md`](kpis.md) | **19 KPIs** de negocio y calidad conversacional (con fórmula, fuente, estado de medición y meta), métricas técnicas de las specs e instrumentación nueva necesaria | PO, tech lead |
| [`privacidad.md`](privacidad.md) | Inventario de datos, qué recibe el LLM, regla de tarjetas, aviso y consentimiento, ARCO, logs y OWASP LLM Top 10 2025 (no es asesoría legal) | PO, backend, QA |

## Cómo usarlo

1. Antes de escribir o cambiar el **prompt del sistema** (`prompts/sistema.md`), revisa la [checklist de la guía de persona](persona-tono.md#9-checklist-para-el-prompt-del-sistema).
2. Al agregar o renombrar una **herramienta**, actualiza primero SPEC-05 · Req. 3 y 6, luego [`intenciones.md`](intenciones.md) y el conjunto de evaluación.
3. Usa los **diálogos** como guion de la demo y como base de pruebas E2E; cada uno indica los escenarios que ejercita.
4. Mantén los IDs `INT-XXX-NN` estables: el conjunto de evaluación los usa como etiqueta.

## Preguntas abiertas

Cada pregunta trae una **propuesta** aplicada provisionalmente en estos documentos.

1. **Nombre de la tienda y del asistente.** La tienda aún no tiene nombre y "Botleta" es provisional.
   *Propuesta:* usar "la tienda" y el marcador `STORE_NAME` en textos y prompt; el nombre del asistente sale de `ASSISTANT_NAME` (SPEC-05 · Req. 12). Si se agrega `STORE_NAME` como variable de entorno, registrarlo en SPEC-05 · RNF *Configuración*.

2. **¿Existe un canal de contacto de la tienda (teléfono, correo, formulario)?** La atención humana está fuera de alcance (SPEC-05), y SPEC-05 · Req. 12 solo muestra el canal de contacto "si está configurado".
   *Propuesta:* mientras no exista, ante "quiero hablar con una persona" se ofrecen solo "Crear un reclamo" y "Mis pedidos". Definir quién es dueño de ese canal (¿Ventas?).
   *Estado (24/09/2026):* probablemente sea un **correo** de atención, aún sin verificar. **Revisar al implementar SPEC-05 · Req. 12 (HU-CNV-13):** confirmar el correo y configurarlo; hasta entonces aplica la propuesta anterior.

3. **Política de privacidad completa.** SPEC-05 · Req. 12 enlaza a una "Política de privacidad" que no existe.
   *Propuesta:* redactarla con el contenido mínimo de [`privacidad.md` §5](privacidad.md#5-aviso-de-privacidad-y-consentimiento) y definir quién es el responsable del tratamiento (la tienda, el Marketplace o cada canal) y quién inscribe el banco de datos.

4. **Derechos ARCO desde el chat.**
   *Propuesta:* fuera de alcance del chat; el asistente redirige al canal de privacidad de la tienda (pendiente, ligado a la pregunta 2). El equipo del canal debe poder ubicar y borrar sus datos propios por `cliente_id`.

5. **Transferencia internacional al proveedor LLM.**
   *Propuesta:* elegir el proveedor y su configuración (sin uso para entrenamiento, retención mínima), informarlo en la política y validarlo con asesoría (ver [`privacidad.md` §3](privacidad.md#3-qué-recibe-el-proveedor-llm)).

6. ✅ **Resuelta (24/09/2026). Herramientas `elegir_direccion` y `cotizar_envio` frente a la dirección en `CheckoutPage`.** SPEC-05 · Req. 3 las lista como herramientas del LLM, pero SPEC-12 captura la dirección solo en `CheckoutPage`, SPEC-12 · RNF prohíbe enviar la dirección al LLM y SPEC-14 · Req. 1 resuelve dirección y cotización fuera del chat.
   *Decisión:* se retiraron `elegir_direccion` y `cotizar_envio` de SPEC-05 · Req. 3. La intención de envío invoca `iniciar_checkout`, que lleva a `CheckoutPage` con la sección de dirección enfocada; si ya hay cotización vigente, `ver_carrito` la muestra.

7. **Reenvío del correo de confirmación sin herramienta.** SPEC-16 · Req. 3 ofrece "Reenviar", pero SPEC-05 · Req. 3 no tiene herramienta para eso, y el endpoint `POST /pedidos/{id}/reenviar-confirmacion` que cita [`trazabilidad.md`](../producto/trazabilidad.md) (HU-PED-08) no está en [`contratos-integracion.md` §2.5](../contratos-integracion.md#25-checkout-pago-y-pedidos-spec-14-a-spec-18).
   *Propuesta:* tratar "Reenviar" como acción directa (sin LLM) y agregar el endpoint a los contratos.

8. **Confirmación antes de cada acción con escritura.** Se esperaba confirmar toda escritura (agregar, quitar, cupón), pero SPEC-05 · Req. 6 marca agregar, cambiar cantidad, quitar y aplicar cupón **sin** confirmación en la UI (son reversibles); solo vaciar el carrito, reemplazar un cupón, pagar, reclamar y devolver la exigen.
   *Propuesta:* seguir la spec (menos fricción; los cambios se informan y se pueden deshacer). Cambiarlo requeriría modificar SPEC-05 · Req. 6.

9. **CSAT con 👍/👎.** No está en las specs.
   *Propuesta:* una pregunta opcional al final de una compra, reclamo o devolución ([`kpis.md` §3](kpis.md#csat-propuesta-no-está-en-las-specs)); si se aprueba, cambio en SPEC-05.

10. **Retención de datos incompleta.** Solo están definidos: archivado de conversaciones a los 90 días (sin borrado), expiración de anónimas a los 7 días y purga de borradores de evidencia a las 24 h. Faltan plazos para mensajes archivados, `checkout.resumen` (con documento), `celular_verificacion_local`, `intento_pago`, `notificacion`, `outbox` y logs.
    *Propuesta:* definir un plazo por tabla en `modelo-datos.md` mediante un cambio de OpenSpec ([`privacidad.md` §2](privacidad.md#2-inventario-de-datos-personales)).

11. ✅ **Resuelta (24/09/2026). Texto de confirmación del correo inconsistente.** SPEC-15 · Req. 2 dice "Te enviamos la confirmación a m****a@…" y SPEC-16 · Req. 3 dice "Te enviaremos la confirmación a m****a@…, sin prometer que ya llegó".
    *Decisión:* se unificó en "Te enviaremos la confirmación a m****a@…" (criterio de SPEC-16: no prometer que ya llegó). Se corrigió SPEC-15.

12. **Mensajes de rechazo de pago incompletos.** SPEC-14 · Req. 5 fija solo el texto de `FONDOS_INSUFICIENTES`.
    *Propuesta:* `DENEGADA_POR_EMISOR` → "Tu tarjeta fue rechazada por el banco emisor. Puedes intentar con otra tarjeta"; `ERROR_PROCESAMIENTO` → "No pudimos procesar el pago por un error temporal. Puedes intentarlo de nuevo". Agregarlos a SPEC-14.

13. ✅ **Resuelta (24/09/2026). Formato del código de devolución.** SPEC-21 usa `DEV-2026-0042` (4 dígitos) y `modelo-datos.md` usa `DEV-2026-00045` (5 dígitos).
    *Decisión:* el formato lo define Ventas; se alineó el ejemplo de `modelo-datos.md` a `DEV-2026-0042`.

14. **Revelación del prompt del sistema (OWASP LLM07).** SPEC-05 · Req. 9 cubre la inyección, pero no la petición de revelar las instrucciones.
    *Propuesta:* el asistente no revela su prompt y el prompt no contiene secretos; agregar un escenario a SPEC-05 · Req. 9.

15. **Burbuja del cliente con un número de tarjeta.** SPEC-05 · Req. 9 redacta antes de persistir y de llamar al LLM, pero no dice qué ve el cliente en su propia burbuja.
    *Propuesta:* el frontend reemplaza la burbuja por el texto redactado que devuelve el backend, para que el número no quede en pantalla ni en el historial.

16. **Instrumentación para KPIs.** Faltan la etiqueta de intención por turno, marcas de fallback y de modo degradado, latencia del primer fragmento y la conversación del checkout.
    *Propuesta:* agregarlas al log por turno que ya exige SPEC-05 · RNF *Observabilidad* ([`kpis.md` §5](kpis.md#5-instrumentación-nueva-necesaria-resumen)).

17. ✅ **Resuelta (24/09/2026). Datos personales escritos en el chat que sí llegan al LLM.** `SensitiveDataFilter` no redacta documentos ni direcciones, y SPEC-18 permite enviar `recibidoPor` al LLM.
    *Decisión:* SPEC-05 · Req. 9 redacta ahora el documento de identidad precedido por una palabra que lo identifique (nuevo escenario, `[documento oculto]`); `recibidoPor` llega solo al frontend (SPEC-18 · RNF). La dirección escrita libremente no se detecta de forma fiable y queda como riesgo aceptado ([`privacidad.md`](privacidad.md)).

18. **Verificación legal del D.S. 016-2024-JUS.** No se pudo contrastar su texto artículo por artículo (plazos ARCO, incidentes, Oficial de Datos Personales, requisitos del consentimiento).
    *Propuesta:* revisión por una persona con formación legal antes de operar con datos reales; hasta entonces, los puntos marcados "a verificar" en [`privacidad.md`](privacidad.md) no son requisitos.

19. **¿Presentación en cada conversación o una sola vez por cliente?** SPEC-05 · Req. 12 presenta al asistente en la primera respuesta de **cada** conversación nueva.
    *Propuesta:* mantenerlo así (una línea, sin repetir en la misma conversación); revisarlo si las pruebas con usuarios lo perciben como repetitivo.
