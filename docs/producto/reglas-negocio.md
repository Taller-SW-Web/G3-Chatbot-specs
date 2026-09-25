# Catálogo de reglas de negocio — Canal Chatbot

> Capa de producto. Este catálogo **no reemplaza** a las specs: cada regla se extrajo de un requisito (o de la sección indicada) de `openspec/specs/<capacidad>/spec.md` y la spec sigue siendo la fuente de verdad. Si una regla cambia, se cambia primero la spec (flujo `openspec/changes/`) y después este catálogo.

## Cómo leer este catálogo

- **ID:** `RN-<ÁREA>-NN`. El área coincide con el código de la épica (ver [`epicas.md`](epicas.md)).
- **Fuente:** `SPEC-NN · Req. N` es el N-ésimo `### Requirement:` de la spec. Cuando la regla está en otra sección se indica (`RNF`, `Contexto`, `Alcance`).
- **Dueño de la regla:** quién la define y quién puede cambiarla. "Chatbot" significa que la decide este equipo. Cuando la define otro módulo (Seguridad, Productos, Ventas o Despacho), el chatbot solo la **aplica** y no puede modificarla por su cuenta.
- Solo se listan reglas presentes en las specs; no se agregaron reglas nuevas.

| Área | Épica | Reglas |
|---|---|---|
| `IDE` | Identidad y sesión | 21 |
| `CNV` | Motor de conversación | 21 |
| `CAT` | Descubrimiento de productos | 17 |
| `CAR` | Carrito y stock | 16 |
| `CHK` | Checkout y pago | 26 |
| `PED` | Grabación y confirmación del pedido | 14 |
| `SGT` | Seguimiento de pedidos | 14 |
| `RCL` | Reclamos | 11 |
| `DEV` | Devoluciones y reembolsos | 14 |
| **Total** | | **154** |

---

## RN-IDE — Identidad y sesión

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-IDE-01 | El celular del registro se acepta solo con el formato `+51` seguido de 9 dígitos que empiezan por 9. Si el cliente ingresa exactamente 9 dígitos que empiezan por 9, se normaliza agregando `+51`; cualquier otro formato bloquea el envío. | SPEC-01 · Req. 2 | Chatbot |
| RN-IDE-02 | La contraseña debe cumplir la política publicada por Seguridad (`GET /password/politica`), que el frontend valida en tiempo real antes de enviar. El rechazo definitivo (`422 POLITICA_INCUMPLIDA`) lo decide Seguridad. | SPEC-01 · Req. 2 y Req. 4 | Seguridad (el chatbot solo aplica la política) |
| RN-IDE-03 | Todo registro enviado desde el canal lleva `canalOrigen: "CHATBOT"` (lista cerrada `WEB`, `CHATBOT`, `RETAIL`, `MARKETPLACE`). | SPEC-01 · Req. 3 | Seguridad (define la lista); Chatbot (envía el valor) |
| RN-IDE-04 | Una cuenta recién creada queda en `PENDIENTE_VERIFICACION` y no abre sesión hasta verificar el correo. | SPEC-01 · Req. 3 | Seguridad |
| RN-IDE-05 | Un mismo correo no puede generar más de una petición de registro hacia Seguridad dentro de una ventana de 10 s (botón deshabilitado más bloqueo en el BFF). | SPEC-01 · Req. 3 | Chatbot |
| RN-IDE-06 | Se admiten como máximo 5 registros por IP cada 10 minutos. | SPEC-01 · RNF (Seguridad) | Chatbot |
| RN-IDE-07 | Ningún mensaje del canal permite deducir si un correo está registrado: el `409 CORREO_NO_DISPONIBLE` del registro y el reenvío de verificación (siempre `202`) se comunican con un texto neutro. | SPEC-01 · Req. 4; SPEC-02 · Req. 2 | Chatbot (Seguridad aplica la misma política en su API) |
| RN-IDE-08 | El enlace de verificación de correo es de un solo uso y vence a las 24 horas. | SPEC-02 · Req. 1 | Seguridad |
| RN-IDE-09 | El reenvío del enlace de verificación admite como máximo 3 solicitudes por hora por correo; la cuarta recibe `429 DEMASIADAS_SOLICITUDES`. | SPEC-02 · Req. 2 | Seguridad |
| RN-IDE-10 | Ante cualquier login rechazado con `401 CREDENCIALES_INVALIDAS` se muestra "Correo o contraseña incorrectos" y se ofrece siempre el reenvío de verificación, sin afirmar la causa (Seguridad no distingue contraseña incorrecta de cuenta bloqueada, inactiva o sin verificar). | SPEC-02 · Req. 3; SPEC-03 · Req. 1 | Seguridad (no distingue la causa); Chatbot (mensaje y pista) |
| RN-IDE-11 | Solo pueden operar en el canal los usuarios cuyo token incluye el rol `CLIENTE`; con otro rol se descartan los tokens y se cierra la sesión. | SPEC-03 · Req. 1 | Chatbot |
| RN-IDE-12 | El OTP de MFA tiene 6 dígitos, vence a los 5 minutos, admite 3 intentos y como máximo 3 solicitudes cada 15 minutos. | SPEC-03 · Req. 2 | Seguridad |
| RN-IDE-13 | El `accessToken` dura 15 minutos y el `refreshToken` es de un solo uso: reutilizar uno anterior cierra todas las sesiones del usuario. | SPEC-03 · Contexto y Req. 5 | Seguridad |
| RN-IDE-14 | El frontend renueva el token cuando faltan menos de 60 s para su vencimiento o ante un `401 TOKEN_INVALIDO`, con una única renovación simultánea; el backend valida cada token en local con el JWKS y, si el JWKS no responde, usa la copia en caché que contiene el `kid`. | SPEC-03 · Req. 5 | Chatbot |
| RN-IDE-15 | La acción que el cliente intentaba antes de autenticarse (`accionPendiente`) se ejecuta automáticamente tras el login o la verificación y luego se limpia. | SPEC-03 · Req. 3; SPEC-01 · Req. 1 | Chatbot |
| RN-IDE-16 | Al iniciar sesión, el carrito anónimo se fusiona con el carrito activo del cliente sumando cantidades por SKU, sujeto al stock disponible y al tope de 10 unidades por línea; el carrito anónimo queda `FUSIONADO`. | SPEC-03 · Req. 4 | Chatbot |
| RN-IDE-17 | Al cerrar sesión, la conversación continúa como anónima con un carrito vacío; el cierre local (cookie y token) se realiza aunque Seguridad no responda. | SPEC-03 · Req. 6 | Chatbot |
| RN-IDE-18 | Los bloqueos por intentos fallidos de login los aplica Seguridad; el chatbot no mantiene un contador propio. | SPEC-03 · RNF (Bloqueos) | Seguridad |
| RN-IDE-19 | No se puede iniciar el checkout si el celular vigente del perfil (`GET /auth/me`) no tiene una verificación local registrada para ese número exacto; un cambio de número invalida la verificación previa. | SPEC-04 · Req. 1 | Chatbot |
| RN-IDE-20 | El OTP de celular tiene 6 dígitos, vence a los 5 minutos, admite 3 intentos y como máximo 3 envíos cada 15 minutos; el envío es simulado por un adaptador propio. | SPEC-04 · Req. 2 | Chatbot |
| RN-IDE-21 | El número celular no se puede cambiar desde el chat; el cambio se hace en el perfil de cuenta, fuera del canal. | SPEC-04 · Req. 3 | Seguridad |

## RN-CNV — Motor de conversación

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-CNV-01 | Una conversación sin mensajes no aparece en el listado; su título se deriva del primer mensaje del cliente con un máximo de 40 caracteres. | SPEC-05 · Req. 1 | Chatbot |
| RN-CNV-02 | El listado de conversaciones se ordena por último mensaje en orden descendente; al retomar una conversación se cargan sus últimos 50 mensajes. | SPEC-05 · Req. 1 | Chatbot |
| RN-CNV-03 | Las conversaciones anónimas (cookie `chat_sid`) quedan ligadas al `cliente_id` al iniciar sesión. | SPEC-05 · Req. 1 | Chatbot |
| RN-CNV-04 | La pantalla de inicio muestra un grid de hasta 4 productos en oferta y no requiere sesión; la conversación se crea al enviar el primer mensaje, no antes. | SPEC-05 · Req. 2 | Chatbot |
| RN-CNV-05 | Ante un mensaje ambiguo, el asistente hace una sola pregunta aclaratoria y no invoca herramientas. | SPEC-05 · Req. 3 | Chatbot |
| RN-CNV-06 | El asistente solo atiende compras en la tienda deportiva; los pedidos fuera de ese dominio se rechazan amablemente con las acciones rápidas principales. | SPEC-05 · Req. 3 | Chatbot |
| RN-CNV-07 | El WebSocket se usa solo para transmitir la respuesta del asistente. Si no conecta o se cae, se reintenta 2 veces con backoff y luego se consulta por *polling* cada 2 s. | SPEC-05 · Req. 4 | Chatbot |
| RN-CNV-08 | La memoria de trabajo (último carrusel, filtros, acción pendiente, borradores) no se comparte entre conversaciones. | SPEC-05 · Req. 5 | Chatbot |
| RN-CNV-09 | La identidad del cliente se toma siempre del token (`sub`); cualquier identificador de cliente en los argumentos del LLM se ignora. | SPEC-05 · Req. 6 | Chatbot |
| RN-CNV-10 | Requieren sesión: dirección, cotización, cupón, checkout, reclamos, devoluciones y consultas de pedidos. Requieren confirmación explícita en la UI: `vaciar_carrito`, `iniciar_checkout` (el pago solo se ejecuta en `CheckoutPage`), `preparar_reclamo` y `preparar_devolucion`. | SPEC-05 · Req. 6 | Chatbot |
| RN-CNV-11 | Si el LLM invoca una herramienta con argumentos inválidos, se le devuelve el error como máximo 1 vez; si persiste, se pide el dato al cliente. | SPEC-05 · Req. 6 | Chatbot |
| RN-CNV-12 | Precios, stock, descuentos, totales y estados se presentan únicamente a partir de los resultados de las herramientas; un precio en el texto transmitido que no coincida se corrige antes de cerrar el turno. | SPEC-05 · Req. 7 | Chatbot |
| RN-CNV-13 | Las acciones de botones se ejecutan directamente sobre el caso de uso, sin pasar por el LLM ni por el WebSocket, y quedan registradas en el historial. | SPEC-05 · Req. 8 | Chatbot |
| RN-CNV-14 | Toda secuencia de 13 a 19 dígitos que pase la validación Luhn se reemplaza por `[tarjeta oculta]`, y todo número de documento precedido por "DNI", "RUC", "documento", "carné", "CE" o "pasaporte" se reemplaza por `[documento oculto]`, antes de persistirse o enviarse al LLM; contraseñas, OTP, datos de tarjeta y documentos nunca llegan al LLM ni a la base de datos. | SPEC-05 · Req. 9 | Chatbot |
| RN-CNV-15 | El contenido devuelto por las herramientas se trata como dato, nunca como instrucción; los descuentos solo provienen de Productos. | SPEC-05 · Req. 9 | Chatbot |
| RN-CNV-16 | Si el proveedor LLM excede 15 s o devuelve error, se activa el modo degradado con menú de acciones rápidas y búsqueda por palabra clave. | SPEC-05 · Req. 10 | Chatbot |
| RN-CNV-17 | Un cliente o IP que envía más de 20 mensajes en 1 minuto (sumando todas sus conversaciones) recibe `429 DEMASIADAS_SOLICITUDES`. | SPEC-05 · Req. 11 | Chatbot |
| RN-CNV-18 | Con más de 50 conversaciones, crear una nueva está permitido, pero el listado archiva automáticamente (sin borrar) las que llevan más de 90 días sin actividad. | SPEC-05 · Req. 11 | Chatbot |
| RN-CNV-19 | El asistente se identifica siempre como asistente virtual, con el nombre configurado en `ASSISTANT_NAME`: se presenta en una línea en la primera respuesta de cada conversación (sin repetirlo después) y lo aclara cada vez que el cliente pregunta si habla con una persona. Nunca afirma ni sugiere ser humano. | SPEC-05 · Req. 12 | Chatbot |
| RN-CNV-20 | Antes de la primera interacción se muestra, junto al campo de chat, un aviso breve de privacidad con enlace a la política completa; el aviso no bloquea la navegación ni el envío de mensajes y no usa casillas de aceptación premarcadas. | SPEC-05 · Req. 12 | Chatbot |
| RN-CNV-21 | El canal no ofrece atención con agente humano: ante ese pedido, el asistente lo explica y ofrece "Crear un reclamo", "Mis pedidos" y, solo si está configurado, el canal de contacto de la tienda, sin prometer una derivación ni tiempos de respuesta. | SPEC-05 · Req. 12 y Fuera de alcance | Chatbot |

## RN-CAT — Descubrimiento de productos

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-CAT-01 | Solo se muestran productos en estado `ACTIVO`; `BORRADOR` e `INACTIVO` nunca aparecen en resultados. | SPEC-06 · Req. 1 | Productos |
| RN-CAT-02 | El precio mostrado es el de Pricing para el canal `CHATBOT`; un SKU sin precio se muestra como "Precio no disponible" y no se puede agregar. | SPEC-06 · RNF (Consistencia) | Productos (precio); Chatbot (bloqueo de agregado) |
| RN-CAT-03 | Una marca escrita por el cliente se normaliza si la similitud con una marca del catálogo es ≥ 0,8; si hay dos candidatas cercanas, se pregunta cuál. | SPEC-06 · Req. 2 | Chatbot |
| RN-CAT-04 | Si la marca no existe en el catálogo, se informa y se ofrecen como máximo 6 marcas disponibles de la categoría. | SPEC-06 · Req. 2 | Chatbot |
| RN-CAT-05 | Cada carrusel de búsqueda muestra como máximo 10 productos; el resto se obtiene con "Ver más". | SPEC-06 · Req. 4 | Chatbot |
| RN-CAT-06 | Si Productos no responde en 4 s o devuelve `5xx`, se informa la indisponibilidad del catálogo y no se muestran datos obsoletos como vigentes. | SPEC-06 · Req. 5 | Chatbot |
| RN-CAT-07 | Si falla la carga de categorías o marcas, se usa la caché si tiene menos de 24 h; sin caché, se busca solo por texto libre `q`. | SPEC-06 · Req. 5 | Chatbot |
| RN-CAT-08 | Una recomendación muestra entre 3 y 5 productos activos con stock (se excluye cualquier candidato con `available = 0` en todas sus variantes), cada uno con una razón basada solo en atributos devueltos por Productos. | SPEC-07 · Req. 1 y Req. 2 | Chatbot |
| RN-CAT-09 | Antes de recomendar se hacen como máximo 2 preguntas aclaratorias, de una en una. | SPEC-07 · Req. 1 | Chatbot |
| RN-CAT-10 | Los complementos (cross-sell) se sugieren como máximo una vez por producto agregado, con hasta 3 candidatos con stock; si el cliente los rechaza, no se vuelven a sugerir en esa conversación salvo que los pida. | SPEC-07 · Req. 3 | Chatbot (candidatos definidos por Productos) |
| RN-CAT-11 | Se listan solo promociones de modalidad `AUTOMATICA`, activas, vigentes y habilitadas para `CHATBOT`; una lista de canales vacía significa todos los canales. | SPEC-08 · Req. 1 | Productos |
| RN-CAT-12 | Con `precioOferta` vigente se muestran el precio regular tachado, el precio de oferta y el porcentaje de ahorro redondeado; si la oferta vence, se vuelve al precio regular y se avisa si el producto estaba en el carrito. | SPEC-08 · Req. 2 | Productos (oferta); Chatbot (presentación) |
| RN-CAT-13 | El chatbot no calcula reglas de promoción: el descuento del carrito y el motivo de no aplicación provienen de la evaluación de Productos (`POST /promociones/evaluar`). | SPEC-08 · Req. 3 | Productos |
| RN-CAT-14 | La consulta de ofertas nunca lista códigos de cupón y excluye las promociones de modalidad `CUPON`. | SPEC-08 · Req. 4 | Chatbot |
| RN-CAT-15 | La disponibilidad en tarjeta es `DISPONIBLE`, `POCAS_UNIDADES` (≤ 5 unidades) o `AGOTADO`; la descripción breve tiene como máximo 90 caracteres y un carrusel, como máximo 10 tarjetas. | SPEC-09 · Req. 1 | Chatbot |
| RN-CAT-16 | Un producto con variantes no se agrega sin elegir la variante (SKU); las variantes agotadas se muestran deshabilitadas y solo se pregunta el atributo que falte. | SPEC-09 · Req. 2 y Req. 4 | Productos (el stock es por SKU); Chatbot (flujo) |
| RN-CAT-17 | La cantidad seleccionable en el detalle del producto va de 1 a 10. | SPEC-09 · Req. 3 | Chatbot |

## RN-CAR — Carrito y stock

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-CAR-01 | Una adición o incremento se acepta solo si `cantidadEnCarrito + cantidadSolicitada ≤ available` del SKU, consultado en vivo; si no, se responde `409 STOCK_INSUFICIENTE` con el disponible. | SPEC-10 · Req. 1 | Chatbot (stock propiedad de Productos) |
| RN-CAR-02 | Si el SKU está agotado, se ofrecen las variantes disponibles del mismo producto o, si no hay, hasta 3 productos similares con stock. | SPEC-10 · Req. 1 | Chatbot |
| RN-CAR-03 | Al iniciar el checkout se revalida todo el carrito en una sola consulta masiva; si alguna línea no se puede cumplir, el checkout se bloquea con `409 CARRITO_DESACTUALIZADO` y el detalle por línea. | SPEC-10 · Req. 2 | Chatbot |
| RN-CAR-04 | Nunca se asume disponibilidad: si el inventario no responde en 3 s, la adición o el checkout se rechazan con `503 SERVICIO_NO_DISPONIBLE`. | SPEC-10 · Req. 3 | Chatbot |
| RN-CAR-05 | No se revelan cantidades exactas de stock mayores a 5; con 5 o menos se indica "Quedan pocas unidades". | SPEC-10 · Req. 4 | Chatbot |
| RN-CAR-06 | La consulta de disponibilidad no es una reserva: el stock se consume cuando Ventas confirma el pedido, y Ventas vuelve a validarlo al crearlo (`409`). | SPEC-10 · Contexto y Req. 2 | Productos y Ventas |
| RN-CAR-07 | Una línea del carrito admite como máximo 10 unidades (`422 LIMITE_CANTIDAD`). | SPEC-11 · Req. 1 | Chatbot |
| RN-CAR-08 | El carrito admite como máximo 20 líneas (SKU distintos). | SPEC-11 · Req. 1 | Chatbot |
| RN-CAR-09 | Agregar un SKU que ya está en el carrito suma la cantidad a la línea existente; no se duplica la línea. | SPEC-11 · Req. 1 | Chatbot |
| RN-CAR-10 | Bajar a 0 la cantidad de una línea la elimina; la eliminación se puede deshacer durante 10 s. | SPEC-11 · Req. 2 | Chatbot |
| RN-CAR-11 | Vaciar el carrito exige confirmación en la UI; al confirmar, el carrito queda sin líneas, sin cupón y sin envío. | SPEC-11 · Req. 2 | Chatbot |
| RN-CAR-12 | Los totales se recalculan en cada lectura: `subtotal` = Σ (precio regular vigente × cantidad), `descuentos[]` según la evaluación de Productos, `costoEnvio` si hay cotización, y `total`. | SPEC-11 · Req. 3 | Chatbot (descuentos de Productos) |
| RN-CAR-13 | Una línea cuyo SKU pasó a `INACTIVO` se marca "Ya no disponible", no suma al total y queda excluida del checkout. | SPEC-11 · Req. 3 | Chatbot |
| RN-CAR-14 | Si la evaluación de promociones no responde, el carrito muestra el subtotal con precios vigentes y el checkout queda bloqueado hasta que la evaluación responda. | SPEC-11 · Req. 3 | Chatbot |
| RN-CAR-15 | El carrito anónimo vive ligado a la conversación y expira a los 7 días de inactividad; el cliente tiene un único carrito `ACTIVO`, que se conserva entre sesiones y dispositivos. | SPEC-11 · Req. 4 | Chatbot |
| RN-CAR-16 | Cuando el pedido pagado se confirma, el carrito pasa a `CONVERTIDO` y el cliente empieza con uno vacío. | SPEC-11 · Req. 4 | Chatbot |

## RN-CHK — Checkout y pago

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-CHK-01 | El documento del comprador es siempre obligatorio: `DNI` = 8 dígitos (`^[0-9]{8}$`); `RUC` = 11 dígitos que empiezan por 10, 15, 17 o 20; `CE` = 8 a 12 alfanuméricos (`^[a-zA-Z0-9]{8,12}$`); `PASAPORTE` = 6 a 12 alfanuméricos (`^[a-zA-Z0-9]{6,12}$`). Un formato que no corresponde al tipo se rechaza con `400 DATO_INVALIDO`. | SPEC-12 · Req. 1 | Ventas (acuerdo A14) |
| RN-CHK-02 | El documento se prellena con el último usado en una compra del canal (guardado en `checkout.resumen`), nunca desde el perfil de Seguridad, y queda editable. | SPEC-12 · Req. 1 | Chatbot |
| RN-CHK-03 | Para cotizar o pagar, `destinatario` es obligatorio, `direccion` tiene al menos 5 caracteres y `distrito` se elige de un selector de ubigeo obligatorio (resuelve `departamento` y `provincia`). | SPEC-12 · Req. 2 | Chatbot |
| RN-CHK-04 | Guardar la dirección en Seguridad es opcional; si el guardado falla, el checkout continúa y se informa al cliente. | SPEC-12 · Req. 3 | Chatbot |
| RN-CHK-05 | La modalidad de envío es siempre `DELIVERY`; no hay retiro en tienda en este canal. | SPEC-12 · Req. 4 | Chatbot |
| RN-CHK-06 | Un destino sin cobertura (`coberturaDisponible: false`) bloquea el pago (`422 SIN_COBERTURA`) hasta corregir el distrito. | SPEC-12 · Req. 4 | Despacho (cobertura) |
| RN-CHK-07 | Si Productos no informa el peso de un SKU, se usa el peso por defecto de su categoría (`config/pesos_por_categoria.yaml`) y se registra su uso, mientras el acuerdo A6 siga abierto. | SPEC-12 · Req. 4 | Chatbot (regla provisional) |
| RN-CHK-08 | Si el cotizador no responde en 4 s, no se asume ningún costo y el pago queda deshabilitado. | SPEC-12 · Req. 4 | Chatbot |
| RN-CHK-09 | Una cotización vence a los 30 minutos y se invalida cuando cambian la dirección o el contenido del carrito; si vence antes de confirmar, se recotiza y se muestra el nuevo total. | SPEC-12 · Req. 5 | Chatbot |
| RN-CHK-10 | El cupón se valida sin consumirse; el uso lo consumen Ventas y Productos al confirmar el pedido, y solo si el cupón forma parte del beneficio seleccionado. El chatbot nunca llama a una API de consumo. | SPEC-13 · Contexto y Req. 1 | Productos |
| RN-CHK-11 | El código de cupón se normaliza (sin espacios y en mayúsculas) antes de validarlo. | SPEC-13 · Req. 1 | Chatbot |
| RN-CHK-12 | Se admite un solo cupón por carrito; reemplazarlo por otro válido requiere confirmación del cliente. | SPEC-13 · Req. 1 | Chatbot |
| RN-CHK-13 | Los motivos de rechazo de un cupón son `INEXISTENTE`, `EXPIRADO`/`NO_VIGENTE`, `AGOTADO`, `LIMITE_CLIENTE`, `MONTO_MINIMO`, `NO_APLICA_PRODUCTOS`, `NO_APLICA_CANAL` y `NO_COMBINABLE`; un cupón rechazado no queda aplicado. | SPEC-13 · Req. 2 | Productos |
| RN-CHK-14 | Aplicar un cupón requiere sesión (por el `customerRef`); al cerrar sesión, el cupón no se conserva en el carrito anónimo. | SPEC-13 · Req. 3 | Productos (límite por cliente); Chatbot (flujo) |
| RN-CHK-15 | El cupón se revalida cuando cambia el carrito y justo antes de crear el pedido; si dejó de ser válido, se retira con aviso (en el checkout, con `409 CARRITO_DESACTUALIZADO`). | SPEC-13 · Req. 4 | Chatbot |
| RN-CHK-16 | Con 5 cupones inválidos en 10 minutos, el siguiente intento recibe `429`; un cupón válido reinicia el contador. | SPEC-13 · Req. 5 | Chatbot |
| RN-CHK-17 | Las precondiciones del checkout se verifican en este orden: sesión → celular verificado → carrito válido → dirección y cotización → cupón vigente. | SPEC-14 · Req. 1 | Chatbot |
| RN-CHK-18 | El checkout y el pedido en Ventas se crean solo cuando el cliente pulsa "Confirmar y pagar", revalidando stock, precios, promociones, cupón y envío; si el total cambió, se exige una nueva confirmación. | SPEC-14 · Req. 2 | Chatbot |
| RN-CHK-19 | `POST /checkout` y cada intento de pago llevan `Idempotency-Key`: la misma clave devuelve el mismo checkout o el mismo resultado de pago, sin duplicar pedido ni cobro. | SPEC-14 · Req. 2 y Req. 5 | Chatbot |
| RN-CHK-20 | El único método de pago del canal es la tarjeta (simulada). Los datos se capturan solo en el formulario `PAGO` y se descartan tras la simulación; solo se persisten la marca y los últimos 4 dígitos. | SPEC-14 · Alcance y Req. 3 | Chatbot |
| RN-CHK-21 | La tarjeta se valida con: marca por BIN (Visa 4…, Mastercard 51–55 y 2221–2720, Amex 34/37), algoritmo Luhn, vencimiento en el mes actual o posterior y CVV de 3 dígitos (4 en Amex). | SPEC-14 · Req. 3 | Chatbot |
| RN-CHK-22 | Una petición de pago con datos inválidos detectada en el servidor responde `400 VALIDACION`, no cuenta como intento y no se simula. | SPEC-14 · Req. 3 | Chatbot |
| RN-CHK-23 | Antes de cada pago se introspecciona el token del cliente (`POST /auth/introspeccion`); con `activo: false` o sin respuesta en 3 s el pago no se procesa y nunca se asume `activo: true`. | SPEC-14 · Req. 4 | Seguridad ("si la operación mueve dinero, introspeccionen"; acuerdo A3) |
| RN-CHK-24 | El simulador es determinista: `4111 1111 1111 1111`, `5555 5555 5555 4444` y `3782 822463 10005` aprueban; `…0002` rechaza por `FONDOS_INSUFICIENTES`; `…0069` rechaza por `DENEGADA_POR_EMISOR`; `…0119` devuelve `ERROR_PROCESAMIENTO` (reintentable); `…3220` aprueba con 5 s de latencia; cualquier otra tarjeta válida por Luhn aprueba. | SPEC-14 · Req. 5 | Chatbot |
| RN-CHK-25 | Cada checkout admite como máximo 3 intentos de pago; al tercer fallo pasa a `FALLIDO`, se solicita la anulación del pedido y el carrito vuelve a `ACTIVO`. | SPEC-14 · Req. 5 | Chatbot |
| RN-CHK-26 | Un checkout no pagado expira a los 15 minutos (`410 CHECKOUT_EXPIRADO`); un job revisa cada minuto, marca `EXPIRADO` y encola la anulación del pedido. | SPEC-14 · Req. 6 | Chatbot |

## RN-PED — Grabación y confirmación del pedido

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-PED-01 | El pedido se crea en Ventas en estado `CREADO`, con `canal: "CHATBOT"` y el snapshot completo (`contacto`, `items`, `cupon`, `envio`, `pago`). | SPEC-15 · Req. 1 | Ventas |
| RN-PED-02 | La `Idempotency-Key` de la creación es la del checkout; un reintento con la misma clave devuelve el mismo `pedidoId` sin duplicar el pedido. | SPEC-15 · Req. 1 y RNF (Idempotencia) | Chatbot |
| RN-PED-03 | Si Ventas no responde en 5 s al crear el pedido, no se piden los datos de la tarjeta y no se realiza ningún cobro. | SPEC-15 · Req. 1 | Chatbot |
| RN-PED-04 | La notificación del pago aprobado se registra en el outbox en la misma transacción que el intento de pago; la transición `CREADO → PAGADO` la decide Ventas. | SPEC-15 · Req. 2 | Ventas (transición); Chatbot (entrega) |
| RN-PED-05 | La notificación de pago se reintenta con backoff exponencial en 5 intentos (5 s, 15 s, 45 s, 2 min y 5 min); agotados, el registro queda `FALLIDO` para revisión manual. | SPEC-15 · Req. 2 | Chatbot |
| RN-PED-06 | Las respuestas `400` y `409` de Ventas a la notificación o a la anulación no se reintentan; se registran para revisión manual. | SPEC-15 · Req. 2 y Req. 3 | Chatbot |
| RN-PED-07 | Un pedido `CREADO` o `PAGADO` cuyo checkout terminó `FALLIDO` o `EXPIRADO` se anula con el motivo `PAGO_NO_COMPLETADO`, sin autorización del Gestor (respuesta `200`). | SPEC-15 · Req. 3 | Ventas (acuerdo A9) |
| RN-PED-08 | El snapshot debe cumplir `pago.subtotal − pago.descuentoCupon + pago.costoEnvio = pago.total` con tolerancia de 0,01; si no cuadra, no se crea el pedido. | SPEC-15 · Req. 4 | Chatbot |
| RN-PED-09 | Las líneas marcadas "Ya no disponible" se excluyen del arreglo `items` del pedido. | SPEC-15 · Req. 4 | Chatbot |
| RN-PED-10 | El correo de confirmación se envía cuando el pedido pasa a `PAGADO_NOTIFICADO`, al correo de la cuenta, y como máximo una vez por pedido (clave única `pedido_id + tipo`). | SPEC-16 · Req. 1 y Req. 2 | Chatbot |
| RN-PED-11 | Si el proveedor SMTP falla, el correo se reintenta hasta 3 veces (1 min, 5 min y 15 min); luego queda `FALLIDA` sin afectar el pedido ni el chat. | SPEC-16 · Req. 2 | Chatbot |
| RN-PED-12 | La confirmación de la compra en el chat no depende del correo; el mensaje no promete que el correo ya llegó. | SPEC-16 · Req. 3 | Chatbot |
| RN-PED-13 | El cliente puede pedir el reenvío del correo de confirmación como máximo 2 veces por pedido. | SPEC-16 · Req. 3 | Chatbot |
| RN-PED-14 | El correo no incluye el documento ni el celular completo del cliente. | SPEC-16 · RNF (Privacidad) | Chatbot |

## RN-SGT — Seguimiento de pedidos

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-SGT-01 | El estado del pedido lo decide Ventas: `CREADO → PAGADO → EN_PREPARACION → DESPACHADO → ENTREGADO`, con la rama `ANULADO`. | SPEC-17 · Contexto y Req. 2 | Ventas |
| RN-SGT-02 | Si el cliente tiene un solo pedido no finalizado, se muestra directamente; si tiene varios, se listan para elegir; si indica un número, se busca ese pedido. | SPEC-17 · Req. 1 | Chatbot |
| RN-SGT-03 | Un pedido inexistente y uno de otro cliente reciben la misma respuesta ("No encontré ese pedido en tu cuenta"). | SPEC-17 · Req. 1 | Chatbot |
| RN-SGT-04 | El listado de pedidos siempre filtra por `clienteId = sub` del token, y el detalle verifica la pertenencia antes de mostrarse. | SPEC-17 · Req. 1 y RNF (Seguridad) | Chatbot (Ventas también lo valida) |
| RN-SGT-05 | El listado conversacional muestra los 5 pedidos más recientes, con "Ver más". | SPEC-17 · Alcance | Chatbot |
| RN-SGT-06 | Las fechas y horas de la línea de tiempo se muestran en hora de Lima. | SPEC-17 · Req. 2 | Chatbot |
| RN-SGT-07 | En un pedido `ANULADO` con pago se informa "Si corresponde un reembolso, se procesará al medio de pago original", sin detalles internos. | SPEC-17 · Req. 2 | Chatbot |
| RN-SGT-08 | La fecha estimada de entrega se calcula con el plazo de la cotización (snapshot) o, si ya existe, con la fecha programada de Despacho. | SPEC-17 · Req. 3 | Chatbot |
| RN-SGT-09 | Si Ventas no responde, solo se puede mostrar el último estado conocido de pedidos creados en este canal, marcado como "último estado conocido". | SPEC-17 · Req. 4 | Chatbot |
| RN-SGT-10 | El seguimiento se consulta solo para pedidos del cliente; un `404` de Despacho en un pedido `PAGADO` o `EN_PREPARACION` no es un error. | SPEC-18 · Req. 1 | Chatbot |
| RN-SGT-11 | Solo llegan al frontend y al LLM los campos `estadoEtiqueta`, `estado`, `fechaProgramada`, `distrito` e `hitos[{titulo, fecha, completado}]`; `recibidoPor?` llega solo al frontend, nunca al LLM; nunca el motivo de un fallo, el comentario o los datos del repartidor, ni coordenadas. | SPEC-18 · Req. 2, Req. 3 y RNF (Privacidad) | Despacho (RT-04); Chatbot (lista blanca) |
| RN-SGT-12 | Si Ventas indica `ENTREGADO` y Despacho aún no, prevalece Ventas. | SPEC-18 · RNF (Coherencia) | Ventas |
| RN-SGT-13 | La consulta a Despacho usa un token de servicio vigente; ante `401` se renueva una vez y se reintenta; ante `403 SCOPE_INSUFICIENTE` no se reintenta. | SPEC-18 · Req. 4 y RNF | Seguridad / Despacho (acuerdo A4) |
| RN-SGT-14 | Si Despacho no responde en 4 s, se muestra el estado según Ventas con el aviso de detalle no disponible. | SPEC-18 · Req. 4 | Chatbot |

## RN-RCL — Reclamos

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-RCL-01 | Todo reclamo se asocia a un pedido del cliente. | SPEC-19 · Req. 1 | Chatbot |
| RN-RCL-02 | El tipo es `RECLAMO` o `QUEJA`, y el motivo uno de: `PRODUCTO_DEFECTUOSO`, `PRODUCTO_EQUIVOCADO`, `PEDIDO_INCOMPLETO`, `INCUMPLIMIENTO_PLAZO_ENTREGA`, `NO_RECIBIDO`, `COBRO_INCORRECTO`, `ATENCION`, `OTRO`. | SPEC-19 · Req. 1 | Ventas (Libro de Reclamaciones); motivos ampliados por Chatbot |
| RN-RCL-03 | La descripción del reclamo tiene entre 20 y 1000 caracteres. | SPEC-19 · Req. 1 | Chatbot |
| RN-RCL-04 | El reclamo se registra solo cuando el cliente pulsa "Enviar reclamo", con `Idempotency-Key`; el mismo envío repetido genera un solo reclamo. | SPEC-19 · Req. 2 | Chatbot |
| RN-RCL-05 | El documento del consumidor se reutiliza del último pedido del cliente; si no existe, se pide en el formulario con las reglas de RN-CHK-01. | SPEC-19 · Req. 2 | Chatbot (reglas de formato de Ventas) |
| RN-RCL-06 | El plazo de respuesta es de 15 días hábiles; se muestra la `fechaLimiteSLA` que calcula Ventas, sin recalcularla. | SPEC-19 · Req. 2 y RNF (Normativa) | Ventas |
| RN-RCL-07 | Si existe un reclamo abierto (ni `ATENDIDO` ni `DERIVADO`) para el mismo pedido y motivo, se informa su código y no se crea otro sin confirmación explícita. | SPEC-19 · Req. 3 | Chatbot |
| RN-RCL-08 | Si Ventas no responde al registrar, el borrador del reclamo se conserva 24 horas. | SPEC-19 · Req. 4 | Chatbot |
| RN-RCL-09 | Estados y etiquetas: `REGISTRADO` = "Recibido", `EN_PROCESO` = "En revisión", `ATENDIDO` = "Respondido", `DERIVADO` = "Derivado a otro equipo". | SPEC-20 · Req. 2 | Ventas (estados); Chatbot (etiquetas) |
| RN-RCL-10 | La respuesta de Ventas (`respuestaVisibleCliente`) se muestra textual; el LLM puede introducirla, pero no resumirla ni modificarla. | SPEC-20 · Req. 2 y RNF (Fidelidad) | Chatbot |
| RN-RCL-11 | Un código de reclamo inexistente y uno de otro cliente reciben la misma respuesta. | SPEC-20 · Req. 1 | Ventas (responde `404` en ambos casos) |

## RN-DEV — Devoluciones y reembolsos

| ID | Regla | Fuente | Dueño de la regla |
|---|---|---|---|
| RN-DEV-01 | Solo se puede solicitar un cambio o una devolución sobre un pedido `ENTREGADO` (si no, `409`). | SPEC-21 · Req. 1 y Req. 4 | Ventas |
| RN-DEV-02 | El plazo para solicitar es de 7 días naturales desde la entrega (fuera de plazo, `400`). | SPEC-21 · Req. 1 y Req. 4 | Ventas |
| RN-DEV-03 | El tipo es `CAMBIO` o `DEVOLUCION_DINERO`, y el motivo uno de: `TALLA_INCORRECTA`, `NO_ERA_LO_QUE_ESPERABA`, `PRODUCTO_DEFECTUOSO`, `PRODUCTO_EQUIVOCADO_ENVIADO`, `YA_NO_LO_QUIERO`, `OTRO`. | SPEC-21 · Req. 2 | Ventas (F3) |
| RN-DEV-04 | El motivo `PRODUCTO_DEFECTUOSO` exige al menos 1 archivo de evidencia válido para habilitar el envío. | SPEC-21 · Req. 2 | Ventas |
| RN-DEV-05 | La evidencia admite hasta 3 archivos `image/jpeg`, `image/png`, `image/webp` o `application/pdf`, de 5 MB como máximo cada uno, y se sube al almacenamiento de Ventas. | SPEC-21 · Req. 3 | Ventas (acuerdo A13) |
| RN-DEV-06 | Las referencias locales a evidencia de borradores no enviados se borran a las 24 horas; el archivo lo retiene Ventas. | SPEC-21 · Req. 3 | Chatbot |
| RN-DEV-07 | En un `CAMBIO`, la variante deseada se elige con disponibilidad validada y se envía en `descripcion`, porque el contrato no tiene un campo dedicado. | SPEC-21 · Req. 2 y Req. 4 | Chatbot (hasta que Ventas modele el campo) |
| RN-DEV-08 | La solicitud se registra solo cuando el cliente pulsa "Enviar solicitud", con `Idempotency-Key`. | SPEC-21 · Req. 4 | Chatbot |
| RN-DEV-09 | Si Ventas no responde al registrar, el borrador (incluidas las referencias a la evidencia subida) se conserva 24 horas. | SPEC-21 · Req. 4 | Chatbot |
| RN-DEV-10 | Si ya existe una solicitud abierta para el mismo pedido, se informa su código y no se crea otra sin confirmación explícita; las solicitudes `RECHAZADA` o `COMPLETADA` no cuentan como duplicado. | SPEC-21 · Req. 5 | Chatbot |
| RN-DEV-11 | Estados y etiquetas: `SOLICITADA` = "Recibida", `EN_EVALUACION` = "En revisión", `APROBADA` = "Aprobada", `RECHAZADA` = "Rechazada", `COMPLETADA` = "Completada". | SPEC-22 · Req. 2 | Ventas (estados); Chatbot (etiquetas) |
| RN-DEV-12 | El fundamento de un rechazo y el detalle del reembolso se muestran tal como los registra Ventas, sin reformular. | SPEC-22 · Req. 2, Req. 3 y RNF (Fidelidad) | Chatbot |
| RN-DEV-13 | El listado de solicitudes incluye todas las del cliente, registradas desde cualquier canal. | SPEC-22 · Req. 1 | Ventas (listado por `clienteId`) |
| RN-DEV-14 | Con una solicitud `APROBADA` de tipo `DEVOLUCION_DINERO` sin bloque `resolucion.reembolso`, se informa "Tu reembolso está en proceso" sin inventar monto ni fecha. | SPEC-22 · Req. 3 | Chatbot |
