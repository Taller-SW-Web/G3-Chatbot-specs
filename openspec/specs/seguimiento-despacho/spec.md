# Seguimiento del despacho en ruta

> Origen: SPEC-18 · Grupo: Seguimiento · Requiere sesión: Sí · Depende de: [`consulta-estado-pedido`](../consulta-estado-pedido/spec.md) (SPEC-17), Despacho (RT-04), Seguridad (token de servicio)

## Purpose

Mostrar al cliente en qué punto del traslado está su paquete, con los hitos del despacho, sin exponer datos operativos ni personales.

## Contexto

Despacho es dueño de la entidad despacho y define 7 estados: `PENDIENTE_ASIGNACION`, `ASIGNADO`, `EN_CAMINO`, `ENTREGADO`, `FALLIDO`, `DEVUELTO_A_ORIGEN` y `CANCELADO`. Cada uno tiene una etiqueta pensada para el cliente.

Su requisito transversal RT-04 define el seguimiento para canales:

- Los canales consultan por código de rastreo o por identificador de pedido, con un token de servicio.
- Reciben la etiqueta del estado, la fecha programada, el distrito de destino y los hitos con fecha.
- La respuesta no incluye coordenadas, teléfono, dirección completa ni datos del repartidor.
- Los hitos de un fallo no exponen el motivo.
- **No hay rastreo GPS**: el seguimiento se basa en los cambios de estado.

Hay una discrepancia: el `api-contract.md` de Despacho publica `GET /tracking/{codigoRastreo}` público y con coordenadas. Aplicamos lo que dice su overview, que es la fuente que su propio repositorio declara como vigente (acuerdo A11).

## Alcance

Incluye:
- Consulta del seguimiento por `idPedido` con el token de servicio del chatbot.
- Presentación de la etiqueta, la fecha programada, el distrito y los hitos.
- Casos de entrega fallida, reprogramación, devolución a origen y cancelación.
- Respuesta a "¿ya viene?", "¿quién me lo trae?" y "¿dónde está el repartidor?" dentro de los límites de la información disponible.

### Fuera de alcance

- Mapa o rastreo GPS en tiempo real: Despacho lo excluye.
- Reprogramar la entrega o cambiar la dirección desde el chat: lo gestiona Despacho (F-04).
- Contacto directo con el repartidor.

## Requirements

### Requirement: Consultar el seguimiento de un pedido despachado
El sistema DEBE (SHALL) consultar a Despacho el seguimiento del pedido (solo si pertenece al cliente, SPEC-17) y mostrar la etiqueta del estado, la fecha programada, el distrito de destino y los hitos con fecha y hora de Lima.

*Trazabilidad: SPEC-18 · Requisito 1.*

#### Scenario: En camino
- **DADO** un pedido `DESPACHADO` cuyo despacho está `EN_CAMINO`
- **CUANDO** el cliente pregunta "¿dónde está mi pedido?"
- **ENTONCES** se muestra "En camino · Entrega programada para hoy · Destino: Miraflores" con los hitos "Recibido en centro de despacho 10:00", "Asignado a repartidor 14:30" y "En camino 16:00"

#### Scenario: Aún sin despacho
- **DADO** un pedido `PAGADO` o `EN_PREPARACION` para el que Despacho responde `404`
- **CUANDO** se consulta el seguimiento
- **ENTONCES** se responde "Tu pedido aún se está preparando; te mostraremos el seguimiento cuando salga del centro de despacho" (no es un error)

#### Scenario: Entregado
- **DADO** un despacho `ENTREGADO`
- **CUANDO** se consulta
- **ENTONCES** se muestra "Entregado el {fecha} {hora}" y, si Despacho lo informa, el nombre de quien recibió

### Requirement: Entregas no exitosas
El sistema DEBE (SHALL) comunicar los fallos, las reprogramaciones y las devoluciones con las etiquetas de Despacho, sin mostrar el motivo interno.

*Trazabilidad: SPEC-18 · Requisito 2.*

#### Scenario: Entrega fallida
- **DADO** un despacho `FALLIDO`
- **CUANDO** se consulta
- **ENTONCES** se muestra "No entregado, regresando al centro" y "Te informaremos la nueva fecha de entrega", sin motivo ni comentario del repartidor

#### Scenario: Reprogramado
- **DADO** un despacho reprogramado (`PENDIENTE_ASIGNACION` tras un `FALLIDO`)
- **CUANDO** se consulta
- **ENTONCES** los hitos muestran "No entregado, regresando al centro" y "Entrega reprogramada para {fecha}"

#### Scenario: Devuelto a origen
- **DADO** un despacho `DEVUELTO_A_ORIGEN`
- **CUANDO** se consulta
- **ENTONCES** se muestra "Tu paquete volvió a nuestro centro de despacho. El equipo de ventas se comunicará contigo" con "Reportar un problema" (SPEC-19)

### Requirement: Límites de la información
El sistema DEBE (SHALL) responder con honestidad las preguntas que la información disponible no cubre.

*Trazabilidad: SPEC-18 · Requisito 3.*

#### Scenario: El cliente pide la ubicación exacta
- **DADO** un pedido en camino
- **CUANDO** el cliente pregunta "¿dónde está el repartidor exactamente?" o "¿me pasas su número?"
- **ENTONCES** se responde que el seguimiento se actualiza por etapas y no incluye la ubicación en tiempo real ni los datos del repartidor, y se muestra la última etapa con su hora

#### Scenario: Respuesta con campos no permitidos
- **DADO** que Despacho devuelve por error coordenadas, dirección completa o datos del repartidor
- **CUANDO** el backend mapea la respuesta
- **ENTONCES** descarta esos campos (lista blanca) antes de enviar el bloque al frontend o al LLM

### Requirement: Autenticación de servicio y fallos
El sistema DEBE (SHALL) usar un token de servicio vigente para consultar a Despacho y degradar con elegancia ante fallos.

*Trazabilidad: SPEC-18 · Requisito 4.*

#### Scenario: Token de servicio vencido
- **DADO** un token de servicio en caché a punto de vencer
- **CUANDO** se consulta
- **ENTONCES** se renueva con `POST /auth/token` (`client_credentials`) antes de llamar; si Despacho responde `401`, se renueva una vez y se reintenta

#### Scenario: Despacho no disponible
- **DADO** que Despacho no responde en 4 s
- **CUANDO** se consulta
- **ENTONCES** se muestra el estado según Ventas con "El detalle del envío no está disponible ahora" y "Reintentar"

## Requisitos no funcionales

- **Privacidad:** lista blanca de campos: `estadoEtiqueta`, `estado`, `fechaProgramada`, `distrito` e `hitos[{titulo, fecha, completado}]` llegan al frontend y al LLM; `recibidoPor?` (nombre de un tercero) llega **solo** al bloque del frontend, nunca al LLM. Nada más llega a ninguno de los dos.
- **Seguridad:** el token de servicio se obtiene y cachea en el backend; nunca llega al frontend.
- **Rendimiento:** la consulta tarda p95 ≤ 600 ms; caché de 30 s por pedido para evitar golpear a Despacho con consultas repetidas.
- **Coherencia:** el estado del pedido lo decide Ventas; si Ventas dice `ENTREGADO` y Despacho aún no, se muestra "Entregado".
- **Manejo de `SCOPE_INSUFICIENTE`:** si el token de servicio del chatbot no tiene el rol `SERVICIO_INTEGRACION` que exige Despacho (acuerdo A4, aún abierto), la llamada falla con `403 SCOPE_INSUFICIENTE`; el sistema no reintenta (pedir el scope no es un error transitorio) y muestra el mismo aviso de "no disponible" del Requisito 4.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
