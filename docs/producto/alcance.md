# Alcance del producto — Canal Chatbot

> Capa de producto sobre las specs de `openspec/specs/`. Todo lo que se afirma aquí proviene de las specs, de [`contratos-integracion.md`](../contratos-integracion.md) o del [README](../../README.md); cuando algo es una propuesta de este documento, se indica y se lleva a [Preguntas abiertas](#preguntas-abiertas).

## 1. Visión

El Canal Chatbot es el canal de venta conversacional del Marketplace Multicanal de productos deportivos: una aplicación web propia, de pantalla completa y pensada primero para el móvil, en la que el cliente busca, compara, recibe recomendaciones, arma su carrito, paga con tarjeta (simulada) y hace seguimiento y postventa de sus pedidos conversando en lenguaje natural o con botones. El canal no es dueño del catálogo, del stock, de los usuarios, de los pedidos ni de los despachos: los consulta por API a los módulos de Seguridad y Usuarios, Productos y Ofertas, Ventas y Postventa y Despacho y Entrega, y garantiza que el asistente nunca invente precios, stock ni estados.

## 2. Usuarios y roles

| Rol | Cómo se identifica | Qué puede hacer | Fuente |
|---|---|---|---|
| **Visitante anónimo** | Sin token; conversaciones ligadas a la cookie `chat_sid` | Conversar, buscar, ver recomendaciones y ofertas, ver detalle, armar un carrito anónimo (expira a los 7 días de inactividad), registrarse e iniciar sesión | SPEC-05, SPEC-06 a 11 (Requiere sesión: No) |
| **Cliente registrado sin verificar** | Cuenta `PENDIENTE_VERIFICACION` en Seguridad | Verificar el correo y pedir reenvío del enlace; no puede iniciar sesión | SPEC-01 · Req. 3, SPEC-02 |
| **Cliente autenticado** | Token con rol `CLIENTE` (`sub` = `cliente_id`) | Todo lo anterior, más: carrito persistente, dirección y cotización, cupones, consulta de pedidos, reclamos, devoluciones y reembolsos | SPEC-03, SPEC-05 · Req. 6 |
| **Cliente autenticado con celular verificado** | Verificación local vigente para el celular actual del perfil | Iniciar el checkout y pagar | SPEC-04 · Req. 1, SPEC-14 · Req. 1 |
| **Usuario sin rol `CLIENTE`** (p. ej., vendedor) | Token sin `CLIENTE` | Nada: se cierra su sesión con "Esta cuenta no puede comprar desde este canal" | SPEC-03 · Req. 1 |

Actores externos que **no** usan el canal pero deciden sobre sus datos: el Gestor de Ventas (responde reclamos y resuelve devoluciones) y el Gestor Comercial de Productos (crea promociones y cupones).

## 3. Canal

- **Incluido:** aplicación **web**, mobile-first, de pantalla completa (patrón tipo ChatGPT/WhatsApp Web), con frontend Next.js (App Router, solo como frontend) + React + TypeScript y backend FastAPI propio (BFF). Pantallas: Inicio, Barra lateral, Conversación, Carrito, Checkout e Historial de pedidos (README §2).
- **Excluido explícitamente:**
  - WhatsApp y otros canales de mensajería (SPEC-05 · Fuera de alcance).
  - Voz / speech-to-text (SPEC-05 · Fuera de alcance).
  - Aplicaciones móviles nativas: el README define el canal como "solo web" (README, encabezado).
  - Widget embebido en otro módulo: es una aplicación propia (README, encabezado).
  - Notificaciones push y SMS al cliente (SPEC-08, SPEC-16 · Fuera de alcance).

## 4. Capacidades incluidas

Agrupadas por épica (ver [`epicas.md`](epicas.md)). Una línea por capacidad.

**EP-01 · Identidad y sesión**
- Registro con formulario seguro dentro del chat, con validación de política de contraseña y celular `+51` ([SPEC-01](../../openspec/specs/registro-cliente/spec.md)).
- Verificación de correo por enlace de un solo uso (24 h) y reenvío limitado a 3 por hora ([SPEC-02](../../openspec/specs/verificacion-correo/spec.md)).
- Login con MFA opcional, renovación silenciosa del token (15 min), retoma de la acción pendiente, fusión del carrito y logout ([SPEC-03](../../openspec/specs/inicio-sesion/spec.md)).
- Verificación local del celular por OTP simulado (6 dígitos, 5 min, 3 intentos) antes del primer pago ([SPEC-04](../../openspec/specs/validacion-celular/spec.md)).

**EP-02 · Motor de conversación**
- Conversaciones múltiples (crear, listar, buscar, retomar), pantalla de inicio, interpretación con herramientas, streaming por WebSocket con *fallback* a *polling*, acciones directas, guardarraíles, modo degradado y límites de uso ([SPEC-05](../../openspec/specs/motor-conversacion/spec.md)).

**EP-03 · Descubrimiento de productos**
- Búsqueda con filtros combinados, sinónimos locales, refinamiento y paginación de 10 en 10 ([SPEC-06](../../openspec/specs/busqueda-filtrado/spec.md)).
- Recomendación de 3 a 5 productos según la necesidad, con hasta 2 preguntas aclaratorias y complementos ([SPEC-07](../../openspec/specs/recomendacion/spec.md)).
- Consulta de promociones vigentes del canal y precios de oferta ([SPEC-08](../../openspec/specs/ofertas-promociones/spec.md)).
- Carrusel de tarjetas, detalle y selección de variante por UI o por texto ([SPEC-09](../../openspec/specs/tarjetas-detalle-producto/spec.md)).

**EP-04 · Carrito y stock**
- Validación de stock en vivo al agregar y revalidación masiva al pagar ([SPEC-10](../../openspec/specs/validacion-stock/spec.md)).
- Carrito conversacional con límites de 10 unidades por línea y 20 líneas, totales recalculados y persistencia ([SPEC-11](../../openspec/specs/gestion-carrito/spec.md)).

**EP-05 · Checkout y pago**
- Documento del comprador (DNI, RUC, CE, PASAPORTE), dirección con campos libres y cotización de envío con Despacho ([SPEC-12](../../openspec/specs/direccion-cotizacion-envio/spec.md)).
- Un cupón por carrito, validado sin consumir y revalidado ante cambios ([SPEC-13](../../openspec/specs/cupones/spec.md)).
- Checkout de 15 minutos, introspección de sesión y pago simulado con tarjeta, con hasta 3 intentos ([SPEC-14](../../openspec/specs/checkout-pago/spec.md)).

**EP-06 · Grabación y confirmación del pedido**
- Creación del pedido en Ventas, notificación de pago por outbox y anulación de pedidos no pagados ([SPEC-15](../../openspec/specs/grabacion-pedido/spec.md)).
- Correo de confirmación único por pedido, con reintentos y reenvío manual ([SPEC-16](../../openspec/specs/notificacion-confirmacion/spec.md)).

**EP-07 · Seguimiento de pedidos**
- Consulta del estado y línea de tiempo de los pedidos del cliente (de cualquier canal) ([SPEC-17](../../openspec/specs/consulta-estado-pedido/spec.md)).
- Seguimiento del despacho por etapas, sin GPS ni datos del repartidor ([SPEC-18](../../openspec/specs/seguimiento-despacho/spec.md)).

**EP-08 · Reclamos** (extensión)
- Registro guiado de reclamos o quejas sobre un pedido, con detección de duplicados ([SPEC-19](../../openspec/specs/creacion-reclamo/spec.md)).
- Consulta del estado y de la respuesta textual de Ventas ([SPEC-20](../../openspec/specs/consulta-reclamo/spec.md)).

**EP-09 · Devoluciones y reembolsos** (extensión)
- Solicitud de cambio o devolución dentro de 7 días naturales, con evidencia de hasta 3 archivos de 5 MB ([SPEC-21](../../openspec/specs/solicitud-devolucion-cambio/spec.md)).
- Consulta de solicitudes de todos los canales y del estado del reembolso ([SPEC-22](../../openspec/specs/consulta-devolucion-reembolso/spec.md)).

## 5. Fuera de alcance (consolidado)

Recopilado de la sección *Fuera de alcance* de las 22 specs, sin duplicados. Cuando un mismo punto aparece en varias specs, se citan todas.

### Canal e interacción
| Excluido | Fuente |
|---|---|
| WhatsApp y otros canales de mensajería | SPEC-05 |
| Voz (speech-to-text) | SPEC-05 |
| Atención con agente humano (handoff) | SPEC-05 |
| Personalización o recomendación basada en el historial de compras o en el comportamiento de otros usuarios | SPEC-05, SPEC-07 |
| Entrenamiento o *fine-tuning* de modelos propios | SPEC-05 |
| Edición o borrado de conversaciones desde la UI (solo archivado automático) | SPEC-05 |
| Notificaciones push o SMS al cliente | SPEC-08, SPEC-16 |

### Identidad y cuenta
| Excluido | Fuente |
|---|---|
| Registro o inicio de sesión con redes sociales | SPEC-01, SPEC-03 |
| Registro de vendedores o administradores | SPEC-01 |
| Edición del perfil, cambio de correo y cambio de celular (son de Seguridad o del Marketplace) | SPEC-01, SPEC-02, SPEC-04 |
| Verificación del correo por OTP (se usa enlace) | SPEC-02, SPEC-04 |
| Plantilla y envío del correo de verificación (los gestiona Seguridad) | SPEC-02 |
| Recuperación de contraseña dentro del chat (solo enlace al flujo externo) | SPEC-03 |
| Activación o desactivación de MFA | SPEC-03 |
| Proveedor SMS real (se simula) | SPEC-04 |
| Compartir la verificación local del celular con otros canales | SPEC-04 |

### Catálogo y descubrimiento
| Excluido | Fuente |
|---|---|
| Búsqueda por imagen | SPEC-06 |
| Filtros por características técnicas avanzadas mientras Productos no las exponga | SPEC-06 |
| Búsqueda semántica con embeddings propios | SPEC-06 |
| Configuración de reglas de cross-sell (es de Productos) | SPEC-07 |
| Recomendación de tallas por medidas corporales; guía de tallas interactiva (solo enlace si Productos provee la URL) | SPEC-07, SPEC-09 |
| Crear o editar promociones (es del Gestor Comercial) | SPEC-08 |
| Combos como unidad vendible, salvo que Productos los exponga como producto | SPEC-08 |
| Reseñas y calificaciones | SPEC-09 |
| Zoom avanzado o vista 360° | SPEC-09 |

### Carrito y stock
| Excluido | Fuente |
|---|---|
| Reserva de stock al agregar al carrito | SPEC-10 |
| Stock por tienda física y retiro en tienda | SPEC-10, SPEC-12 |
| Aviso de reposición de stock | SPEC-10 |
| Lista de deseos o favoritos | SPEC-11 |
| Guardar para después o varios carritos | SPEC-11 |
| Compartir el carrito | SPEC-11 |

### Checkout, pago y envío
| Excluido | Fuente |
|---|---|
| Editar o eliminar direcciones guardadas | SPEC-12 |
| Validar el documento contra RENIEC o SUNAT (solo formato) | SPEC-12 |
| Paso separado para elegir entre varias direcciones guardadas | SPEC-12 |
| Elegir fecha o franja de entrega | SPEC-12 |
| Validación de la dirección con geocodificación o mapa | SPEC-12 |
| Consumo del uso del cupón (lo hacen Ventas y Productos) | SPEC-13 |
| Varios cupones simultáneos | SPEC-13 |
| Generación o distribución de cupones | SPEC-13 |
| Pasarela de pago real (Niubiz, Culqi, Mercado Pago) y 3-D Secure | SPEC-14 |
| Yape, PagoEfectivo, pago contra entrega y cuotas | SPEC-14 |
| Guardar tarjetas | SPEC-14 |
| Emisión de comprobante electrónico (boleta o factura) y su descarga | SPEC-14, SPEC-15, SPEC-17 |

### Pedido, seguimiento y notificaciones
| Excluido | Fuente |
|---|---|
| Consumo de stock y solicitud de despacho (los desencadena Ventas) | SPEC-15 |
| Anulación de un pedido a pedido del cliente (F2 de Ventas) | SPEC-15, SPEC-17, SPEC-21 |
| Correos por cambios de estado posteriores (despachado, entregado) | SPEC-16 |
| Encuesta de satisfacción (F5 de Ventas) | SPEC-16 |
| Mapa o rastreo GPS en tiempo real | SPEC-18 |
| Reprogramar la entrega o cambiar la dirección desde el chat | SPEC-18 |
| Contacto directo con el repartidor | SPEC-18 |

### Postventa
| Excluido | Fuente |
|---|---|
| Adjuntar evidencias a un reclamo (la evidencia corresponde a una devolución) | SPEC-19 |
| Responder, gestionar, reabrir, apelar o cerrar reclamos desde el chat | SPEC-19, SPEC-20 |
| Notificación por correo de la respuesta al reclamo (es de Ventas) | SPEC-20 |
| Evaluación y decisión de solicitudes de devolución (es del Gestor) | SPEC-21 |
| Coordinación del recojo o del nuevo despacho | SPEC-21 |
| Ejecución o reintento del reembolso o extorno (F4 de Ventas) | SPEC-14, SPEC-21, SPEC-22 |
| Variante deseada como campo estructurado hacia Ventas (se envía en `descripcion`) | SPEC-21 |
| Apelar una solicitud rechazada o cancelar una en curso | SPEC-22 |

> **Nota:** las devoluciones y los cambios están **dentro** del canal (EP-09, Could), cubiertos por SPEC-21 y SPEC-22. SPEC-17 solo los excluye de su propio alcance (ver la [pregunta abierta 1](#preguntas-abiertas), resuelta).

## 6. Dependencias externas

| Módulo | Estado | Endpoints | Acuerdos | Impacto |
|---|---|---|---|---|
| **Seguridad y Usuarios** | ✅ Contrato publicado | JWKS, `client_credentials`, registro, política de contraseña, verificación de correo, login, OTP, refresh, logout, `me`, direcciones, introspección | A1 ✅ (acción pendiente: informar la URL de `/verificar-correo`); A2 ✅ decidido fuera de alcance de Seguridad; A3 ✅ (credenciales reales desde Hito 4); A4 🟡 (rol `SERVICIO_INTEGRACION`) | EP-01, EP-05 (introspección), EP-07 (token de servicio) |
| **Productos y Ofertas** | 🟡 Provisional: las specs de Productos definen las capacidades, pero las rutas son una propuesta del chatbot | Búsqueda, detalle, categorías, marcas, precios por canal, disponibilidad, promociones, evaluación, cupones, candidatos | A5 🟡 (rutas y payloads), A6 🟡 (quién agrega peso y volumen), A7 🟡 (búsqueda por texto libre) | EP-02 (grid de inicio), EP-03, EP-04, EP-05 (cupones y revalidación), EP-09 (variante deseada) |
| **Ventas y Postventa** | ✅ Contrato publicado (v1.3.0) | Pedidos (crear, notificar pago, anular, detalle, listado), reclamos (crear, detalle, listado), devoluciones (evidencia, crear, detalle, listado) | A8, A9, A10, A13, A14 ✅ | EP-04 (409 por stock), EP-05, EP-06, EP-07, EP-08, EP-09 |
| **Despacho y Entrega** | Cotización ✅ publicada · Seguimiento 🟡 | `POST /zonas/cotizar`; seguimiento por pedido (propuesto `GET /seguimiento?idPedido=`) | A11 🟡 (seguimiento por `idPedido`, con token de servicio y sin coordenadas); A12 🟡 (autenticación de la cotización); A4 🟡 | EP-05 (cotización), EP-07 (seguimiento) |
| **Proveedor LLM** | Definido por configuración | Claude u OpenAI detrás de `LLMProvider` | — | EP-02 y todas las épicas conversacionales |
| **SMTP** | Configurable (Mailtrap en desarrollo) | Envío de correo | — | EP-06 |

## 7. Restricciones

**Tecnología (README §1.5)**
- Frontend: Next.js (App Router, solo como frontend, sin Route Handlers ni Server Actions hacia el backend), React, TypeScript, arquitectura hexagonal, TanStack Query, Zustand, React Hook Form + Zod, Tailwind CSS.
- Backend: Python 3.12, FastAPI, arquitectura hexagonal, Pydantic v2, SQLAlchemy 2 + Alembic, httpx async, PyJWT (JWKS), APScheduler; PostgreSQL propio.
- Pruebas: pytest, respx, Prism (mock de Seguridad), Vitest + Testing Library, Playwright. Cada escenario DADO/CUANDO/ENTONCES debe tener al menos una prueba automatizada que lo referencie por nombre (README §5).
- El stack de backend (Python/FastAPI) fue **aprobado por el profesor**, aunque los lineamientos del curso listan Java Spring Boot, .NET Core o Node.js (README §1.5).

**Hitos (README §3)**
- Hito 3 (demo 1): SPEC-05, 06, 09, 10, 11, 01, 02 y 03.
- Hito 4 (integración): SPEC-04, 07, 08, 12, 13, 14, 15 y 16.
- Hito 5–6: SPEC-17 a 22, endurecimiento de RNF y pruebas de performance.

**Negocio y seguridad**
- Único método de pago: **tarjeta simulada** con un simulador determinista; no hay pasarela real ni pago contra entrega (SPEC-14).
- El SMS del OTP de celular es simulado (SPEC-04).
- Sin acceso a bases de datos de otros módulos; toda integración es por API (README §1.3).
- Datos sensibles (contraseña, OTP, tarjeta) nunca pasan por el LLM ni se persisten; de la tarjeta solo se guardan marca y últimos 4 dígitos (SPEC-05 · Req. 9, SPEC-14 · Req. 3).
- Access token en LocalStorage con vida de 15 min (riesgo XSS aceptado por el equipo) y refresh token solo en cookie `httpOnly` (README §1.4).
- Moneda PEN con 2 decimales; fechas en UTC en la API y en hora de Lima en la UI (README §5).

**Límites y tiempos medibles**

| Aspecto | Valor | Fuente |
|---|---|---|
| Unidades por línea / líneas por carrito | 10 / 20 | SPEC-11 · Req. 1 |
| Vigencia del checkout | 15 min | SPEC-14 · Req. 6 |
| Intentos de pago por checkout | 3 | SPEC-14 · Req. 5 |
| Vigencia de la cotización de envío | 30 min | SPEC-12 · Req. 5 |
| OTP (MFA y celular) | 6 dígitos, 5 min, 3 intentos, 3 envíos / 15 min | SPEC-03 · Req. 2; SPEC-04 · Req. 2 |
| Mensajes por cliente o IP | 20 por minuto | SPEC-05 · Req. 11 |
| Cupones inválidos | 5 en 10 min | SPEC-13 · Req. 5 |
| Registros por IP | 5 cada 10 min | SPEC-01 · RNF |
| Plazo de devolución / de respuesta a reclamo | 7 días naturales / 15 días hábiles | SPEC-21 · Req. 1; SPEC-19 · Req. 2 |
| Evidencia de devolución | hasta 3 archivos de 5 MB | SPEC-21 · Req. 3 |
| Timeouts de integración | Seguridad 5 s (registro), 3 s (introspección); Productos 4 s (catálogo), 3 s (inventario); Despacho 4 s; Ventas 5 s; LLM 15 s | SPEC-01, 14, 06, 10, 12, 18, 15, 05 |
| Rendimiento del chat | primer fragmento p95 ≤ 2 s; turno completo p95 ≤ 6 s; acción directa p95 ≤ 1,5 s | SPEC-05 · RNF |
| Rendimiento de compra | búsqueda p95 ≤ 800 ms; carrito p95 ≤ 900 ms; cotización p95 ≤ 600 ms; pago p95 ≤ 1 s; creación de pedido p95 ≤ 1,5 s | SPEC-06, 11, 12, 14, 15 · RNF |
| Calidad del LLM | ≥ 120 frases etiquetadas; precisión de intención ≥ 90 % en CI | SPEC-05 · RNF |
| Correo de confirmación | enviado en ≤ 60 s en el 95 % de los casos | SPEC-16 · RNF |

## 8. Supuestos

1. Productos y Ofertas implementará endpoints equivalentes a los propuestos en `contratos-integracion.md` §3.2; mientras tanto se desarrolla contra mocks con datos semilla (A5).
2. Seguridad entrega las credenciales reales de `modulo-chatbot` en Hito 4; hasta entonces se prueba con `client_secret=secreto-de-prueba` contra Prism (SPEC-14 · RNF).
3. Despacho cubre al menos Lima y Callao; el selector de distrito se limita a esas zonas si Despacho no amplía la cobertura (SPEC-12 · RNF).
4. La agrupación de las 22 specs en 8 casos de uso del backend es una propuesta pendiente de confirmar contra el código (README §1.2).
5. Mientras A6 siga abierto, el peso del carrito se calcula con `config/pesos_por_categoria.yaml` (SPEC-12 · Req. 4).
6. El seguimiento de Despacho se implementa según el overview de Despacho (consulta por `idPedido` con token de servicio, sin coordenadas), no según su `api-contract.md` (SPEC-18 · Contexto, A11).
7. Las estimaciones en puntos de este documento son relativas al equipo y se recalibran tras el primer ciclo.

## 9. Riesgos abiertos

| # | Riesgo | Probabilidad / impacto | Mitigación | Épicas |
|---|---|---|---|---|
| R1 | **A5 🟡:** las rutas de Productos son una propuesta; el contrato real puede diferir y obligar a rehacer clientes y DTOs justo antes de la demo de Hito 3. | Alta / Alto | Aislar `ProductosClient` detrás de un puerto; mock respx con datos semilla; issue de coordinación con Productos bloqueando las historias `contrato:provisional`. | EP-02, 03, 04, 05, 09 |
| R2 | **A6 🟡:** sin definir quién agrega peso y volumen, la cotización usa pesos por categoría que pueden no coincidir con el costo real. | Media / Medio | Registrar cada uso del valor por defecto; revisar al cerrar A6. | EP-05 |
| R3 | **A11 🟡 / A4 🟡:** el seguimiento de Despacho no tiene endpoint unificado ni rol de servicio emitido; SPEC-18 podría no ser demostrable en Hito 5–6. | Alta / Medio | Historias de SPEC-18 en Should; degradación al estado de Ventas (SPEC-18 · Req. 4). | EP-07 |
| R4 | **A12 🟡:** la autenticación del cotizador (pública o con API key) no está definida. | Media / Medio | `DespachoClient` con autenticación configurable. | EP-05 |
| R5 | **A7 🟡:** la búsqueda por texto libre `q` en Productos no está confirmada; afecta la búsqueda y el modo degradado. | Media / Alto | Normalizar a categoría y marca como camino principal. | EP-02, 03 |
| R6 | ✅ **Cerrado (24/09/2026).** Stack no aprobado: el profesor aceptó Python/FastAPI. | — | — | Todas |
| R7 | **Token en LocalStorage (riesgo aceptado):** un XSS permitiría robar hasta 15 min de sesión. | Media / Alto | CSP estricta, sanitización del contenido del LLM y de otros módulos, token de 15 min (README §1.4). | EP-01, 02 |
| R8 | **Credenciales reales de Seguridad solo en Hito 4:** la introspección y el token de servicio no se prueban contra el servicio real hasta ese hito. | Media / Medio | Pruebas contra Prism desde Hito 3. | EP-05, 06 |
| R9 | **Costo y latencia del LLM:** el turno completo debe cumplir p95 ≤ 6 s y la precisión ≥ 90 %. | Media / Medio | Rate limit, contexto acotado (12 mensajes, 10 productos), modo degradado, evaluación en CI. | EP-02 |
| R10 | **Dependencias entre hitos:** varias historias de Hito 3 solo se prueban de punta a punta con piezas de Hito 4 (grid de ofertas, revalidación de stock, carrito convertido) y el token de servicio de SPEC-18 se necesita en Hito 4. | Alta / Medio | Ver preguntas abiertas 2 y 3. | EP-02, 04, 05, 07 |

## Preguntas abiertas

Cada pregunta trae una **propuesta** aplicada provisionalmente en este paquete de producto y el archivo y línea que la motivó.

1. ✅ **Resuelta (24/09/2026). ¿Devoluciones y cambios están dentro o fuera del canal?** `openspec/specs/consulta-estado-pedido/spec.md:34` decía "Devoluciones o cambios: no se incluyen en este canal", lo que contradecía a SPEC-21 y SPEC-22.
   *Decisión:* están **dentro** del canal (EP-09, Could). Se corrigió la línea de SPEC-17 para que solo los excluya de su propio alcance y remita a SPEC-21 y SPEC-22.

2. ✅ **Resuelta (24/09/2026). ¿Cómo se alimenta el grid de ofertas de la pantalla de inicio en Hito 3?** `openspec/specs/motor-conversacion/spec.md:90` usa `GET /catalogo/promociones` (SPEC-08), que según `README.md:197` es de Hito 4, mientras SPEC-05 es de Hito 3 (`README.md:196`).
   *Decisión:* el grid usa `soloOfertas=true` de SPEC-06 desde Hito 3; el banner se alimenta de SPEC-08 y se oculta mientras no esté disponible (Hito 3), falle o no haya promociones. Se corrigió SPEC-05 · Req. 2 y se agregó el escenario "Promociones no disponibles".

3. ✅ **Resuelta (24/09/2026). ¿Se adelanta el `ServiceTokenProvider` a Hito 4?** Está en el desglose de SPEC-18 (`openspec/specs/seguimiento-despacho/design.md:34`, Hito 5–6), pero lo necesitan la introspección de SPEC-14 (`openspec/specs/checkout-pago/design.md:32`) y el worker de SPEC-15 (`openspec/specs/grabacion-pedido/design.md:12`), ambos de Hito 4.
   *Decisión:* el `ServiceTokenProvider` se construye en Hito 4 dentro de HU-CHK-14; SPEC-18 lo reutiliza. Se actualizó el desglose de `seguimiento-despacho/design.md`.

4. ✅ **Resuelta (24/09/2026). ¿Qué significa "el chat lo guía a elegir la dirección" si la dirección se captura en `CheckoutPage`?** `openspec/specs/checkout-pago/spec.md:54-57` (escenario "Falta una precondición") describe un paso conversacional, mientras SPEC-12 fija la captura en campos libres dentro de `CheckoutPage` y excluye un paso separado de selección de direcciones.
   *Decisión:* cuando falta la dirección, se navega a `CheckoutPage` con la sección de dirección enfocada. Se corrigió SPEC-14 · Req. 1 (texto del requisito y escenario "Falta una precondición").

5. ✅ **Resuelta (24/09/2026). ¿Cómo conviven el reenvío del correo (`REENVIO_CONFIRMACION`) y la clave única de `notificacion`?** `openspec/specs/notificacion-confirmacion/spec.md:74` crea reenvíos de tipo `REENVIO_CONFIRMACION` (máx. 2), pero `docs/modelo-datos.md:137-138` define `tipo` solo como `CONFIRMACION_PEDIDO` y la unicidad `pedido_id + tipo` impediría un segundo reenvío.
   *Decisión (provisional, se refinará con el modelo de datos):* se agregó `REENVIO_CONFIRMACION` al enum de `notificacion.tipo` y un campo `numero_reenvio` (0–2) que forma parte de la clave única; `intentos` sigue contando solo reintentos SMTP.

6. ✅ **Resuelta (24/09/2026). ¿El listado de devoluciones de Ventas acepta el filtro `pedidoId`?** `openspec/specs/solicitud-devolucion-cambio/spec.md:151` consulta `GET /api/v2/devoluciones?clienteId=&pedidoId=&estado=`, pero el contrato confirmado (`docs/contratos-integracion.md:199` y A10 en la línea 264) solo publica `clienteId`, `estado` y `tipo`.
   *Decisión:* se consulta por `clienteId` y se filtra por `pedidoId` en el backend del chatbot hasta que Ventas publique el filtro. Se corrigió SPEC-21.

7. ✅ **Resuelta (24/09/2026). ¿Se admite PDF como evidencia en el modelo local?** SPEC-21 · Req. 3 permite `application/pdf`, pero `docs/modelo-datos.md:176` define `evidencia.tipo` solo como `IMAGEN`.
   *Decisión (provisional, se refinará con el modelo de datos):* `evidencia.tipo` guarda el valor que devuelva Ventas sin `CHECK` local. Queda pendiente confirmar con Ventas el valor para PDF.

8. **¿Qué zonas cubre Despacho?** `openspec/specs/direccion-cotizacion-envio/spec.md:167` limita el ubigeo a Lima y Callao "si Despacho solo cubre esas zonas", sin confirmarlo.
   *Propuesta:* arrancar con Lima y Callao y ampliar cuando Despacho publique su cobertura.

9. ✅ **Resuelta (24/09/2026). Prioridad de las extensiones.** `README.md:215-217` marca como extensión el registro/login, los reclamos y las devoluciones.
   *Decisión:* registro y login como **Must** (son prerrequisito del checkout, SPEC-14 · Req. 1); creación de reclamo como **Should** (lo enlazan SPEC-17 y SPEC-18, y responde al Libro de Reclamaciones); consulta de reclamos y todo EP-09 como **Could**.

10. ✅ **Resuelta (24/09/2026). Prioridad del seguimiento de Despacho (SPEC-18).** El curso traza la consulta de estado a SPEC-17 y SPEC-18 (`README.md` §4), pero SPEC-18 depende de A4 y A11, ambos abiertos (`openspec/specs/seguimiento-despacho/design.md:9-11`).
    *Decisión:* SPEC-17 en **Must** (salvo HU-SGT-03, preguntas específicas, en **Should**) y SPEC-18 en **Should**, con la degradación al estado de Ventas como comportamiento mínimo.

11. **URL de verificación del canal (A1).** `openspec/specs/verificacion-correo/design.md:11` aún marca la URL como 🟡, aunque A1 figura resuelto con una acción pendiente (`docs/contratos-integracion.md:255`).
    *Propuesta:* crear una issue `[INT]` para informar a Seguridad la URL exacta de `/verificar-correo` antes de la demo de Hito 3; sin ella, HU-IDE-04 no es demostrable de punta a punta.

12. ✅ **Resuelta (24/09/2026). Aprobación del stack.** `README.md:144` pedía validar Python/FastAPI con el profesor.
    *Decisión:* el profesor aprobó Python/FastAPI. El riesgo R6 queda cerrado.
