# ADR-0019: Imágenes como entrada del LLM, con almacenamiento propio privado detrás de `AttachmentStorage`

## Estado

Aceptada

## Fecha

2026-09-26 (decisión del equipo registrada en SPEC-23)

## Contexto

- Hasta esta decisión el LLM solo recibía texto: `motor-conversacion` dejaba la voz fuera de alcance, `busqueda-filtrado` dejaba fuera la búsqueda por imagen y `privacidad.md` indicaba que la evidencia de devolución nunca llegaba al LLM.
- El equipo decidió (2026-09-26) que el cliente pueda adjuntar imágenes al chat y que el LLM las interprete (por ejemplo "busco zapatillas como estas" o "este es el defecto"). El audio sigue fuera de alcance.
- El modelo elegido es `gpt-6-luna` (OpenAI), detrás del puerto `LLMProvider` ([ADR-0005](ADR-0005-llm-con-tool-calling-detras-de-llmprovider.md)). ⚠️ Su soporte de visión y su costo en tokens por imagen **no están verificados**.
- La base de datos es Supabase (plan gratuito). ⚠️ No está confirmado que ofrezca PostgreSQL 18, del que depende `uuidv7()` nativo del modelo de datos.
- OpenAI conserva las entradas de la API durante 30 días para monitoreo de abuso: el proveedor del modelo no sirve como almacenamiento ni como política de retención propia.
- Las evidencias de devolución (SPEC-21) las hostea Ventas y el chatbot no necesita bucket para ellas ([ADR-0013](ADR-0013-solo-referencias-locales-a-agregados-externos.md)); las imágenes del chat son otro caso: no son evidencia y Ventas no debe recibirlas.
- El historial debe poder mostrar las imágenes, y `SensitiveDataFilter` ([ADR-0006](ADR-0006-datos-sensibles-fuera-del-llm.md)) solo actúa sobre texto.

## Decisión

- **Imágenes como partes de contenido.** `LLMProvider` admite mensajes multimodales (partes de texto e imagen). El backend lee la imagen de su almacenamiento y la envía al LLM **en base64**; nunca una URL, ni pública ni firmada.
- **Almacenamiento propio y privado.** Las imágenes se guardan en un bucket privado de Supabase Storage detrás de un nuevo puerto outbound **`AttachmentStorage`** (`guardar`, `leer`, `eliminar`, `url_firmada`), con `SupabaseAttachmentStorage` como adaptador. La base de datos guarda solo referencias en la tabla `adjunto` (claves de almacenamiento, tipo, tamaño y dimensiones), nunca los bytes.
- **Carga previa por el backend.** El cliente sube cada imagen a un endpoint del backend, que valida el tipo por su firma binaria, elimina EXIF y ubicación, acota las dimensiones y genera una miniatura. El mensaje se envía después con `adjuntoIds`.
- **Miniaturas por URL firmada.** El historial muestra las miniaturas mediante URLs firmadas de corta vida (5 minutos por defecto) emitidas por el backend con pertenencia verificada.
- **Mismo contexto que el texto.** Las imágenes comparten la ventana de los últimos 12 mensajes, con un máximo de imágenes por turno para acotar el costo.
- **Imagen a criterios de texto.** El LLM traduce la imagen a criterios para las herramientas existentes (`buscar_productos`, SPEC-06). No hay búsqueda por similitud visual.
- **Degradación.** Si el modelo no admite visión (`LLM_VISION_ENABLED=false`), el LLM falla o el archivo no se puede leer, `DegradedMode` avisa que la imagen no pudo analizarse y el flujo de texto sigue activo.
- **Sin redacción automática de imágenes.** Se muestra un aviso antes de la primera carga y el riesgo residual se documenta en `privacidad.md`.
- **Límites de la decisión.** No cubre audio, PDF en el chat ni el envío de estas imágenes a Ventas. La evidencia de SPEC-21 sigue subiéndose a Ventas desde su formulario. El plazo de retención de los adjuntos no está decidido.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| API de archivos del proveedor: subir la imagen y referenciarla por identificador (*alternativa estándar, no documentada*) | La API de archivos deja la imagen guardada en el proveedor bajo su propia retención y acopla el backend a un solo proveedor, contra [ADR-0005](ADR-0005-llm-con-tool-calling-detras-de-llmprovider.md). El base64 en línea (elegido) es portable entre proveedores, aunque aumenta el tamaño de cada petición |
| Enviar al LLM una URL pública o firmada de la imagen (*alternativa estándar, no documentada*) | Expondría un enlace de una imagen privada a un tercero y obligaría a que el proveedor pueda descargarla; una URL pública no tiene control de acceso y una firmada puede filtrarse en registros del proveedor |
| No almacenar las imágenes: enviarlas al LLM y descartarlas (*alternativa estándar, no documentada*) | Sin almacenamiento no hay miniaturas en el historial ni se pueden reenviar las imágenes de los turnos siguientes dentro de la ventana de 12 mensajes: el LLM las perdería en el turno siguiente |
| Usar al proveedor del modelo como almacenamiento (*alternativa estándar, no documentada*) | Su retención es de 30 días y está pensada para monitoreo de abuso, no como política de retención del canal; no permite borrar ni servir miniaturas |
| Reutilizar el almacenamiento de Ventas de la evidencia (SPEC-21) | Ventas hostea evidencia de devoluciones, no imágenes de conversación; mezclarlas enviaría a otro módulo imágenes que el cliente no presentó como evidencia |
| Mantener el chat solo con texto (*statu quo*) | No cumple lo decidido por el equipo; el cliente debe describir con palabras lo que ya puede mostrar en una foto |
| Búsqueda por similitud visual con embeddings de imagen | Requiere un índice de imágenes de Productos y modelos propios, fuera de alcance; el LLM convierte la imagen en criterios de texto y reutiliza SPEC-06 |

## Consecuencias

**Positivas**
- El cliente puede mostrar lo que busca o el defecto de un producto sin describirlo.
- Se reutilizan las herramientas y los guardarraíles existentes: veracidad de precios, sesión, confirmación y modo degradado.
- El puerto `AttachmentStorage` permite cambiar de Supabase Storage a otro almacenamiento sin tocar los casos de uso.
- Las imágenes del chat no se mezclan con la evidencia que Ventas hostea.

**Negativas y riesgos aceptados**
- El canal pasa a ser responsable de guardar imágenes de clientes: un bucket privado, URLs firmadas, limpieza de adjuntos huérfanos y una política de retención que aún no está definida (pregunta abierta de SPEC-23).
- Cada imagen viaja fuera del Perú al proveedor del modelo y este la conserva 30 días; debe informarse en `privacidad.md` (flujo transfronterizo, [ADR-0005](ADR-0005-llm-con-tool-calling-detras-de-llmprovider.md)).
- Las imágenes pueden mostrar rostros, documentos, tarjetas o direcciones y no se redactan automáticamente: riesgo residual aceptado, mitigado con el aviso previo, la instrucción al asistente de no transcribir esos datos y los registros sin contenido de imagen.
- El texto dentro de una imagen puede intentar una inyección de instrucciones; se trata como dato ([ADR-0006](ADR-0006-datos-sensibles-fuera-del-llm.md), SPEC-05 · Req. 9), sin garantía absoluta.
- Mayor costo y latencia por turno con imágenes; los objetivos de SPEC-23 son provisionales hasta medirlos con el modelo real.
- Dependencia del plan gratuito de Supabase (almacenamiento y ancho de banda) y de que el modelo elegido admita visión, que aún no se verificó.

## Impacto en la privacidad

- **Datos nuevos:** imágenes que el cliente elige compartir, potencialmente con datos personales; se guardan en un bucket privado y solo se acceden por URLs firmadas de corta vida emitidas tras verificar la pertenencia de la conversación.
- **Minimización:** se eliminan EXIF y ubicación antes de guardar; los registros no contienen imágenes, base64, URLs firmadas ni nombres de archivo; las claves de almacenamiento son aleatorias.
- **Proveedor del modelo:** recibe las imágenes del contexto vigente en base64; no recibe URLs ni metadatos EXIF.
- **Transparencia:** aviso antes de la primera carga y enlace a la política de privacidad, sin casillas premarcadas.
- **Retención:** sin plazo definido; se propone alinearlo con el archivado de 90 días de las conversaciones, pendiente de decisión.

## Referencias

- `openspec/specs/adjuntos-imagenes-chat/spec.md` y `design.md` (SPEC-23)
- `openspec/specs/motor-conversacion/spec.md` Req. 3, 4, 10, 11 y RNF *Contexto* y *Privacidad*
- `openspec/specs/busqueda-filtrado/spec.md` (*Fuera de alcance*)
- `openspec/specs/solicitud-devolucion-cambio/spec.md` (evidencia hospedada en Ventas)
- `docs/conversacion/privacidad.md` §3
- [ADR-0005](ADR-0005-llm-con-tool-calling-detras-de-llmprovider.md), [ADR-0006](ADR-0006-datos-sensibles-fuera-del-llm.md), [ADR-0013](ADR-0013-solo-referencias-locales-a-agregados-externos.md)
