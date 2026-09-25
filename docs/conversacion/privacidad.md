# Privacidad y protección de datos en el chatbot

> **Aviso:** este documento es una guía de diseño para un proyecto universitario. **No es asesoría legal.** Antes de operar con clientes reales, el tratamiento debe revisarlo una persona con formación en protección de datos personales, contrastándolo con el texto oficial de la ley y su reglamento.

## 1. Marco de referencia

| Fuente | Uso en este documento |
|---|---|
| **Ley N.° 29733**, Ley de Protección de Datos Personales (Perú) | Principios (consentimiento, finalidad, proporcionalidad, calidad, seguridad), deber de información al titular, flujo transfronterizo y derechos de acceso, rectificación, cancelación y oposición (ARCO) |
| **Reglamento aprobado por el D.S. N.° 016-2024-JUS**, vigente desde el 31/03/2025 | Reemplaza al reglamento anterior. Texto de referencia: [lpderecho.pe](https://lpderecho.pe/reglamento-ley-proteccion-datos-personales-decreto-supremo-016-2024-jus/) |
| **OWASP Top 10 for LLM Applications 2025** | Riesgos propios del LLM: [owasp.org](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |
| Specs del canal | SPEC-05 · Req. 9, 12 y RNF *Privacidad*; SPEC-01, 03, 04, 12, 14, 16, 18, 19, 21 (RNF de privacidad y seguridad) |

> ⚠️ **Pendiente de verificación:** no fue posible contrastar aquí el texto del D.S. 016-2024-JUS artículo por artículo. Los puntos que dependen de su redacción exacta (plazos de respuesta a derechos ARCO, notificación de incidentes, Oficial de Datos Personales, requisitos del consentimiento y de la política de privacidad) se marcan como **"a verificar"** y se listan en las [preguntas abiertas](README.md#preguntas-abiertas).

## 2. Inventario de datos personales

"Dónde se guarda" remite a [`modelo-datos.md`](../modelo-datos.md). El chatbot no replica los datos maestros de otros módulos: guarda identificadores y snapshots mínimos.

| Dato | Origen | Dónde se guarda | Retención definida | ¿Llega al LLM? |
|---|---|---|---|---|
| Texto de los mensajes del cliente (puede contener datos personales que el cliente escriba) | Chat | `mensaje.texto` (redactado si hay tarjeta, OTP o contraseña), `conversacion.titulo`, `conversacion.resumen`, `conversacion.busqueda` | Anónimas: expiran a los 7 días de inactividad. Autenticadas: se **archivan** (no se borran) a los 90 días sin actividad. **Sin plazo de borrado** ⚠️ | Sí: últimos 12 mensajes + resumen de la conversación activa (SPEC-05 · RNF *Contexto*) |
| Nombre de pila | Seguridad (`GET /auth/me`) | No se persiste aparte | — | **Sí, es el único dato de identidad permitido** (SPEC-05 · RNF *Privacidad*) |
| Identificador del cliente (`sub`) | Token | `cliente_id` en varias tablas | Ligado a cada tabla ⚠️ | No (la identidad sale del token, SPEC-05 · Req. 6) |
| Cookie de sesión anónima `chat_sid` | Navegador | `conversacion.sid_anonimo` (hash) | 7 días de inactividad | No |
| Access token | Seguridad | LocalStorage del navegador (riesgo XSS aceptado) | 15 min | No |
| Refresh token | Seguridad | Cookie `httpOnly` | Rotación de Seguridad | No |
| Correo | Seguridad | `notificacion.destinatario`; enmascarado en el chat | **No definida** ⚠️ | No |
| Celular | Seguridad | `celular_verificacion_local.celular` (completo); enmascarado en el chat | **No definida** ⚠️ | No |
| Contraseña, OTP | Formularios | **Nunca** (van directo al endpoint) | — | **Nunca** (SPEC-05 · Req. 9; SPEC-01 y SPEC-04 · RNF) |
| Datos de tarjeta (PAN, CVV, vencimiento) | `FORMULARIO/PAGO` | **Nunca**; solo `intento_pago.marca` y `ultimos4` | `intento_pago`: **no definida** ⚠️ | **Nunca** (SPEC-14 · RNF) |
| Documento de identidad, teléfono y correo del comprador | `CheckoutPage` | `checkout.resumen.contacto` (snapshot enviado a Ventas) | **No definida** ⚠️ | No (SPEC-12 · RNF *Privacidad*) |
| Dirección de entrega y destinatario | `CheckoutPage` | `checkout.resumen`, `carrito.envio_snapshot` (solo distrito), bloque `CONFIRMACION_PEDIDO` en `mensaje.bloques` | **No definida** ⚠️ | No (SPEC-12 · RNF) |
| Nombre de quien recibió el pedido (`recibidoPor`) | Despacho | Bloque `ESTADO_PEDIDO` | Como el mensaje | **No**: llega solo al bloque del frontend (SPEC-18 · RNF *Privacidad*) |
| Descripción de reclamo o devolución | Chat / formulario | Borrador en `conversacion.contexto`; se envía a Ventas | Borrador: 24 h si Ventas falla (SPEC-19 · Req. 4; SPEC-21 · Req. 4) | Sí, si el cliente la escribe en el chat (la extrae `preparar_reclamo`) |
| Evidencia (fotos o PDF) | Formulario | Solo la URL en `evidencia`; el archivo lo hospeda Ventas | Referencias de borradores: 24 h (SPEC-21 · Req. 3) | **No** (SPEC-21 · RNF) |
| Métricas por turno (tokens, latencia, herramienta) | Backend | `mensaje`, logs | **No definida** ⚠️ | No |
| Outbox (payloads de notificación de pago y correo) | Backend | `outbox.payload` | **No definida** ⚠️ | No |

**Retenciones faltantes (⚠️):** mensajes de conversaciones autenticadas y archivadas, `checkout.resumen` (con el documento), `celular_verificacion_local`, `intento_pago`, `notificacion`, `outbox` y logs. **Propuesta:** definir un plazo por tabla con el criterio "lo necesario para la finalidad" (p. ej., borrar mensajes de conversaciones archivadas al cumplir un plazo; conservar los snapshots de compra solo mientras se necesiten para postventa) y documentarlo en `modelo-datos.md` mediante un cambio de OpenSpec. Ver [pregunta abierta 10](README.md#preguntas-abiertas).

## 3. Qué recibe el proveedor LLM

**Regla de la spec:** al LLM se envía el nombre de pila del cliente (si hay sesión) y nunca el correo, el celular, la dirección completa ni el documento (SPEC-05 · RNF *Privacidad*). Los resultados de herramientas se truncan a lo necesario (SPEC-05 · RNF *Contexto*).

| Se envía | No se envía |
|---|---|
| Prompt del sistema, resumen de la conversación activa y sus últimos 12 mensajes (ya redactados) | Mensajes de otras conversaciones |
| Nombre de pila | Correo, celular, documento, dirección completa |
| Resultados de herramientas truncados (máx. 10 productos; campos de Despacho en lista blanca) | Contraseñas, OTP, datos de tarjeta (redactados antes, SPEC-05 · Req. 9) |
| | URL de la evidencia (SPEC-21 · RNF) |

**Brechas detectadas (a decidir):**
1. ✅ Resuelta: `SensitiveDataFilter` redacta también el documento de identidad cuando va precedido por una palabra que lo identifica (SPEC-05 · Req. 9, escenario "El cliente escribe su documento de identidad en el chat"). **Riesgo aceptado:** una dirección escrita libremente en el chat no se puede detectar de forma fiable; se mitiga con el aviso de privacidad (SPEC-05 · Req. 12) y redirigiendo a `CheckoutPage` (SPEC-12 · RNF).
2. ✅ Resuelta: `recibidoPor` (nombre de un tercero) llega solo al bloque del frontend, nunca al LLM (SPEC-18 · RNF *Privacidad*).

**Transferencia internacional.** Los proveedores previstos (Claude u OpenAI detrás de `LLMProvider`) procesan los datos fuera del Perú, lo que constituye un flujo transfronterizo de datos personales en el sentido de la Ley 29733. Consideraciones de diseño (a validar con asesoría):
- Informarlo en la política de privacidad (destinatario, país, finalidad).
- Minimizar lo que se envía (ya lo exige SPEC-05) y ampliar la redacción (brecha 1).
- Usar la API con las opciones del proveedor que excluyen el uso de los datos para entrenamiento y reducen la retención, según sus términos vigentes; conservar la referencia contractual.
- El proveedor elegido y su configuración se registran en la configuración del backend (proveedor y modelo ya van por variables de entorno, SPEC-05 · RNF *Configuración*).

## 4. Datos de tarjeta (regla tipo PCI)

El pago es **simulado** (SPEC-14), pero el diseño aplica igual las reglas de un canal real:

- **Nunca se acepta el número de tarjeta (PAN) en el chat.** Toda secuencia de 13 a 19 dígitos que pase Luhn se reemplaza por `[tarjeta oculta]` **antes** de persistir el mensaje o enviarlo al LLM, y el asistente responde "Por tu seguridad, ingresa los datos de tu tarjeta solo en la pantalla de pago" (SPEC-05 · Req. 9; [diálogo D-12](dialogos-ejemplo.md#d-12--número-de-tarjeta-pegado-en-el-chat)).
- La tarjeta se captura solo en `FORMULARIO/PAGO` y se envía directo a `POST /checkout/{id}/pago`; el PAN, el CVV y el vencimiento no se escriben en BD, logs, trazas ni prompts, y el body del endpoint se excluye del logging (SPEC-14 · Req. 3 y RNF).
- Solo persisten la marca y los últimos 4 dígitos (`intento_pago`).
- El formulario avisa "Pago simulado – entorno académico. No uses tarjetas reales" (SPEC-14 · RNF).
- Pendiente: si la burbuja del cliente en su propia pantalla debe mostrarse ya redactada ([pregunta abierta 15](README.md#preguntas-abiertas)).

## 5. Aviso de privacidad y consentimiento

### Aviso breve (en la app)
Definido en SPEC-05 · Req. 12: junto al campo de chat de `HomePage` y de toda conversación sin mensajes se muestra "Conversas con un asistente virtual con IA. No compartas contraseñas ni datos de tarjeta en el chat." con el enlace "Política de privacidad". No bloquea la navegación ni el primer mensaje.

### Contenido mínimo propuesto de la política completa
Basado en el deber de información de la Ley 29733 (contenido exacto **a verificar** con el reglamento):

| Sección | Contenido para este canal |
|---|---|
| Responsable | Nombre y domicilio de la tienda (`STORE_NAME`, pendiente) y medio de contacto para privacidad |
| Datos que se tratan | Los del inventario (§2), en lenguaje simple |
| Finalidades | Atender consultas y compras por chat; gestionar el carrito, el pago simulado y el pedido; enviar el correo de confirmación; atender reclamos, cambios y devoluciones; medir la calidad del servicio con métricas sin datos personales |
| Destinatarios | Módulos del Marketplace: Seguridad y Usuarios, Productos y Ofertas, Ventas y Postventa, Despacho y Entrega; el proveedor LLM; el proveedor de correo (SMTP) |
| Transferencia internacional | Proveedor LLM (país y finalidad) |
| Uso de IA | Que las respuestas las genera un asistente virtual con IA y que precios, stock y estados provienen de los sistemas de la tienda |
| Conservación | Plazos por tipo de dato (hoy parcialmente definidos, §2) |
| Derechos del titular | ARCO y cómo ejercerlos (§6); derecho a acudir a la Autoridad Nacional de Protección de Datos Personales |
| Banco de datos | Inscripción del banco de datos en el registro correspondiente (**a verificar** si aplica y quién la hace) |
| Almacenamiento en el navegador | Token en LocalStorage y cookies `chat_sid` y de refresh |
| Consecuencia de no dar los datos | Sin sesión se puede explorar y armar el carrito; para pagar se necesitan cuenta, celular verificado, documento y dirección |

### Enfoque de consentimiento (propuesta)
- **Aviso informado al inicio**, visible antes del primer mensaje, sin casillas premarcadas (SPEC-05 · Req. 12).
- El tratamiento necesario para atender la compra y la postventa se apoya en la relación con el cliente; el registro ya incluye `aceptaTerminos` (SPEC-01), cuyo texto gestiona Seguridad. Si la base jurídica exacta de cada finalidad requiere consentimiento expreso, se define con asesoría (**a verificar**).
- **Marketing:** requiere un consentimiento separado, libre y no premarcado. El canal **no envía comunicaciones comerciales** (SPEC-08 y SPEC-16 excluyen push y correos posteriores), así que queda **fuera de alcance**.

## 6. Derechos ARCO y otras solicitudes

**Propuesta:** el ejercicio de derechos ARCO **no se atiende dentro del chat** (el canal no tiene flujo de verificación de identidad para ello y SPEC-05 excluye editar o borrar conversaciones desde la UI). Si el cliente escribe "borra mis datos", "qué datos tienen de mí" o "elimina mi historial", Botleta:

1. Explica en una frase que esas solicitudes se atienden por el canal de privacidad de la tienda.
2. Muestra el enlace o correo de ese canal (**pendiente**: no existe aún, [pregunta abierta 4](README.md#preguntas-abiertas)).
3. No promete plazos ni borra nada por su cuenta.

Los plazos de respuesta y el procedimiento los fija el reglamento (**a verificar**). Como el chatbot guarda datos propios (conversaciones, snapshots de checkout, verificación de celular), el equipo del canal debe poder ubicarlos y borrarlos por `cliente_id` cuando la tienda lo solicite.

## 7. Enmascaramiento en logs

| Regla | Estado | Fuente |
|---|---|---|
| El log por turno no lleva datos personales en el texto | ✅ Spec | SPEC-05 · RNF *Observabilidad* |
| La contraseña nunca va a logs, `mensaje` ni contexto del LLM | ✅ Spec | SPEC-01 · RNF |
| El token de verificación de correo no se registra | ✅ Spec | SPEC-02 · RNF |
| El body del pago se excluye del logging | ✅ Spec | SPEC-14 · RNF |
| Cupones enmascarados (`RU***`) | ✅ Spec | SPEC-13 · RNF |
| Descripción de reclamo truncada a 50 caracteres | ✅ Spec (⚠️ 50 caracteres aún pueden incluir datos personales) | SPEC-19 · RNF |
| Correo y celular enmascarados en el chat | ✅ Spec | SPEC-01, SPEC-04 · RNF |
| El correo de confirmación no incluye documento ni celular completo | ✅ Spec | SPEC-16 · RNF |
| Correos, celulares y documentos enmascarados también en logs técnicos y de errores (`ultimo_error`, `outbox`) | 🟠 Propuesta | — |
| Registrar `cliente_id` y `correlationId`, nunca nombres ni correos | 🟠 Propuesta | — |

## 8. Riesgos del LLM (OWASP Top 10 LLM 2025)

| Riesgo | Control en las specs | Estado |
|---|---|---|
| LLM01 Prompt Injection | Resultados de herramientas delimitados como datos; descuentos solo de Productos | ✅ SPEC-05 · Req. 9 |
| LLM02 Sensitive Information Disclosure | Redacción de tarjeta, OTP y contraseña; nombre de pila como único dato; lista blanca de Despacho | ✅ SPEC-05 · Req. 9 y RNF; SPEC-18 · RNF · ⚠️ brechas del §3 |
| LLM03 Supply Chain | Proveedor detrás de `LLMProvider`; SDK del proveedor | 🟠 Propuesta: fijar versiones y revisar dependencias |
| LLM04 Data and Model Poisoning | No hay entrenamiento ni *fine-tuning* propio | ✅ Fuera de alcance (SPEC-05) |
| LLM05 Improper Output Handling | Sanitización de todo contenido del LLM antes de renderizar; CSP; `OutputValidator` | ✅ README §1.4; SPEC-03 · RNF; SPEC-05 · Req. 7 |
| LLM06 Excessive Agency | Esquemas Pydantic, identidad desde el token, sesión y confirmación en la UI; pago, reclamos y devoluciones solo con botón | ✅ SPEC-05 · Req. 6; SPEC-19, SPEC-21 · RNF |
| LLM07 System Prompt Leakage | El asistente no revela sus instrucciones; el prompt no contiene secretos | 🟠 Propuesta ([pregunta abierta 14](README.md#preguntas-abiertas)) |
| LLM08 Vector and Embedding Weaknesses | No se usan embeddings propios | ✅ No aplica (SPEC-06 · Fuera de alcance) |
| LLM09 Misinformation | Precios, stock, descuentos y estados solo desde herramientas | ✅ SPEC-05 · Req. 7; SPEC-07 · RNF |
| LLM10 Unbounded Consumption | 20 mensajes/min, máx. 5 iteraciones de herramientas, `max_tokens`, timeout de 15 s | ✅ SPEC-05 · Req. 11, RNF y `design.md` |

## 9. Incidentes de seguridad

El reglamento establece obligaciones ante incidentes que afecten datos personales, incluida la comunicación a la Autoridad y, cuando corresponda, a los titulares (**plazos y alcance a verificar**). Propuesta mínima para el canal: registrar el incidente con `correlationId`, avisar a la tienda y al equipo de Seguridad del Marketplace, y rotar credenciales afectadas (tokens de servicio, clave del LLM).
