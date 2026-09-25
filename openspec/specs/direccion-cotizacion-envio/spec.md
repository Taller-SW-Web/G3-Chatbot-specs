# Dirección de entrega, documento del comprador y cotización de envío

> Origen: SPEC-12 · Grupo: Checkout · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03), [`gestion-carrito`](../gestion-carrito/spec.md) (SPEC-11), Seguridad, Ventas (F1), Despacho (F-01)

## Purpose

Que el cliente indique su dirección de entrega y su documento de identidad dentro del checkout, y conozca, antes de pagar, si hay cobertura, cuánto cuesta el envío y en cuántos días llega.

## Contexto

Tres módulos intervienen en este paso, y su contrato real (revisado en `contratos-integracion.md`) fija los nombres de campo que hay que usar:

- **Ventas** exige, para crear el pedido (`api-contract.md` §1.1): un bloque `contacto` con `nombreCompleto`, `tipoDocumento`, `numeroDocumento`, `telefono` y `email`; y un bloque `envio` con `modalidad`, `costo`, `destinatario`, `departamento`, `provincia`, `distrito`, `direccion` y `referencia`.
- **Seguridad** es dueño de las direcciones guardadas del cliente: `GET/POST /usuarios/{id}/direcciones`, con etiqueta, departamento, provincia, distrito, dirección, referencia y predeterminada.
- **Despacho** ofrece a los canales Marketplace y Chatbot la cotización de envío (`POST /zonas/cotizar`), que indica si hay cobertura, el costo y el plazo estimado. Todos los envíos salen de un único centro de despacho.

🧩 El wireframe de `CheckoutPage` captura la dirección con **campos libres en la misma pantalla de pago**, no con un selector de direcciones guardadas. Esta spec se ajusta a ese flujo, usando los nombres de campo que Ventas espera.

🧩 **Acuerdo A14, resuelto (23/09/2026):** Ventas exige `tipoDocumento` y `numeroDocumento` del comprador, siempre obligatorios, y confirmó por escrito las reglas de formato de cada tipo (Requisito 1). Ni el registro (Seguridad no lo pide) ni ningún otro punto del flujo lo capturan hoy; esta spec agrega ese campo al checkout — es la única oportunidad razonable de pedirlo.

El peso y el volumen del paquete son insumos de la cotización; quién los calcula sigue en discusión con Productos y Despacho (acuerdo A6, ver `contratos-integracion.md`).

## Alcance

Incluye:
- Sección "Datos de entrega" dentro de `CheckoutPage`, con los campos `destinatario` (nombre completo de quien recibe), `tipoDocumento`, `numeroDocumento`, `direccion` (texto libre), `distrito` (selector), `departamento`/`provincia` (derivados del distrito) y `referencia` (opcional).
- Si el cliente tiene direcciones guardadas en Seguridad, una opción para autocompletar con la predeterminada (sin obligar a usarla).
- Casilla opcional "Guardar esta dirección para la próxima vez", que registra la dirección en Seguridad.
- Cotización del envío con el distrito y el peso y volumen estimados del carrito, mostrada dentro de la misma pantalla.
- Rechazo de direcciones sin cobertura y ofrecimiento de corregir el distrito.
- Recotización cuando cambia el distrito o el contenido del carrito.

### Fuera de alcance

- Editar o eliminar direcciones existentes: se hace en el perfil del cliente (Seguridad o Marketplace).
- Validar el documento contra RENIEC o SUNAT: se valida solo el formato.
- Un paso de checkout separado para elegir entre varias direcciones guardadas.
- Elegir la fecha o franja de entrega, o retiro en tienda.
- Validación de la dirección con geocodificación o mapa.

## Requirements

### Requirement: Capturar el documento de identidad
El sistema DEBE (SHALL) pedir el tipo y número de documento del comprador dentro de `CheckoutPage`, ya que Ventas lo exige para crear el pedido y ningún otro flujo lo captura. 🧩 **Reglas confirmadas por Ventas (23/09/2026)** para su `DocumentoValidator`: el bloque `contacto` exige **siempre** `tipoDocumento` y `numeroDocumento` — nunca es opcional, se usa tanto para emitir el comprobante como para validar la entrega. El frontend valida con exactamente estas expresiones, para que nunca lleguen a Ventas datos que su propio validador vaya a rechazar:

| `tipoDocumento` | Regla | Expresión regular |
|---|---|---|
| `DNI` | Exactamente 8 dígitos numéricos | `^[0-9]{8}$` |
| `RUC` | Exactamente 11 dígitos numéricos, empezando por `10`, `15`, `17` o `20` | `^[0-9]{11}$` (más la validación del prefijo) |
| `CE` (Carné de Extranjería) | De 8 a 12 caracteres alfanuméricos | `^[a-zA-Z0-9]{8,12}$` |
| `PASAPORTE` | De 6 a 12 caracteres alfanuméricos | `^[a-zA-Z0-9]{6,12}$` |

Si el formato no corresponde al tipo elegido, Ventas rechaza con `400 Bad Request {codigo: DATO_INVALIDO}`. Esto reemplaza el rango genérico de "6 a 12 caracteres" para `CE` que se había asumido antes, y agrega `PASAPORTE` como cuarto tipo (no contemplado en el diseño anterior).

*Trazabilidad: SPEC-12 · Requisito 1.*

#### Scenario: DNI válido
- **DADO** un cliente que completa `tipoDocumento: DNI` y `numeroDocumento: 72458912`
- **CUANDO** valida el formulario
- **ENTONCES** se acepta, porque cumple `^[0-9]{8}$`

#### Scenario: RUC con prefijo inválido
- **DADO** `tipoDocumento: RUC` y `numeroDocumento: 30458912345`
- **CUANDO** valida el formulario
- **ENTONCES** se rechaza en el cliente antes de enviarlo, porque el RUC no empieza por `10`, `15`, `17` o `20`, aunque tenga 11 dígitos

#### Scenario: CE fuera de rango
- **DADO** `tipoDocumento: CE` y `numeroDocumento: 1234567` (7 caracteres)
- **CUANDO** valida el formulario
- **ENTONCES** se rechaza, porque el CE exige de 8 a 12 caracteres, no de 6 a 12 como se pensaba antes

#### Scenario: Pasaporte válido
- **DADO** `tipoDocumento: PASAPORTE` y `numeroDocumento: A1234567`
- **CUANDO** valida el formulario
- **ENTONCES** se acepta, porque cumple `^[a-zA-Z0-9]{6,12}$`

#### Scenario: Documento inválido o vacío
- **DADO** un `numeroDocumento` vacío o con un formato que no corresponde al `tipoDocumento` elegido
- **CUANDO** el cliente intenta pagar
- **ENTONCES** se muestra el error junto al campo y no se habilita el pago (el frontend nunca deja llegar esto a Ventas, pero si ocurriera, Ventas también lo rechaza con `400 DATO_INVALIDO`)

#### Scenario: Cliente recurrente
- **DADO** un cliente que ya completó su documento en una compra anterior en este canal
- **CUANDO** vuelve a comprar
- **ENTONCES** el campo se prellena con el último documento usado (guardado en `checkout.resumen` de su pedido anterior, nunca en el perfil de Seguridad, que no lo modela) y queda editable

### Requirement: Capturar la dirección en el checkout
El sistema DEBE (SHALL) mostrar los campos de dirección dentro de `CheckoutPage`, prellenados con la dirección predeterminada del cliente si existe y editable, usando los nombres de campo que espera Ventas.

*Trazabilidad: SPEC-12 · Requisito 2.*

#### Scenario: Cliente con dirección guardada
- **DADO** un cliente con la dirección predeterminada "Av. Larco 1234, dpto. 502, Miraflores"
- **CUANDO** abre `CheckoutPage`
- **ENTONCES** los campos `destinatario`, `direccion` (con su `distrito`) y `referencia` vienen prellenados y editables, con la nota "Usando tu dirección guardada · Cambiar"

#### Scenario: Cliente sin direcciones guardadas
- **DADO** un cliente sin direcciones en Seguridad
- **CUANDO** abre `CheckoutPage`
- **ENTONCES** los campos aparecen vacíos, con `distrito` como un selector obligatorio (ubigeo, que también resuelve `departamento` y `provincia`)

#### Scenario: Validación de los campos
- **DADO** un `destinatario` vacío o una `direccion` de menos de 5 caracteres
- **CUANDO** el cliente intenta cotizar o pagar
- **ENTONCES** se muestran los errores por campo y no se cotiza ni se habilita el pago

### Requirement: Guardar la dirección para la próxima compra
El sistema DEBE (SHALL) ofrecer guardar la dirección ingresada en Seguridad, sin que sea obligatorio.

*Trazabilidad: SPEC-12 · Requisito 3.*

#### Scenario: Cliente marca "Guardar esta dirección"
- **DADO** el checkbox marcado y los campos válidos
- **CUANDO** el cliente confirma el pedido (SPEC-14)
- **ENTONCES** el backend llama a `POST /usuarios/{id}/direcciones` con el token del cliente antes o junto con la creación del pedido; si Seguridad falla al guardarla, el checkout **continúa igual** y se informa "No pudimos guardar tu dirección para la próxima vez"

#### Scenario: Cliente no marca la casilla
- **DADO** el checkbox sin marcar
- **CUANDO** se confirma el pedido
- **ENTONCES** la dirección se usa solo para ese pedido y no se llama a Seguridad para guardarla

### Requirement: Cotizar el envío
El sistema DEBE (SHALL) cotizar con Despacho enviando el distrito resuelto de la dirección, el `pesoKg` total y el `volumenM3` total del carrito, y mostrar el resultado dentro de `CheckoutPage` antes de habilitar el pago. `modalidad` se envía siempre como `DELIVERY` (no hay retiro en tienda en este canal).

*Trazabilidad: SPEC-12 · Requisito 4.*

#### Scenario: Destino con cobertura
- **DADO** una dirección en Miraflores y un carrito de 1,2 kg
- **CUANDO** Despacho responde `coberturaDisponible: true, costoEnvio: 12.50, plazoEstimadoDias: 1`
- **ENTONCES** `CheckoutPage` muestra "Envío a Miraflores: S/ 12.50 · llega en 1 día hábil aprox." y el total a pagar lo incluye

#### Scenario: Destino sin cobertura
- **DADO** un distrito fuera de cobertura
- **CUANDO** Despacho responde `coberturaDisponible: false`
- **ENTONCES** se informa "Aún no llegamos a {distrito}" bajo el campo de dirección, se bloquea el botón de pago (`422 SIN_COBERTURA`) y se pide corregir el distrito

#### Scenario: Peso de producto no disponible
- **DADO** que Productos no informa el peso de un SKU
- **CUANDO** se calcula el peso total
- **ENTONCES** se usa el peso por defecto de su categoría (`config/pesos_por_categoria.yaml`) como parche mientras se resuelve el acuerdo A6, y se registra el uso del valor por defecto

#### Scenario: Despacho no disponible
- **DADO** que el cotizador no responde en 4 s
- **CUANDO** se cotiza
- **ENTONCES** no se asume ningún costo; se muestra "No pude calcular el envío ahora" con el botón "Reintentar" y el pago queda deshabilitado

### Requirement: Mantener vigente la cotización
El sistema DEBE (SHALL) invalidar y recalcular la cotización cuando cambian la dirección o el contenido del carrito, o cuando la cotización tiene más de 30 minutos.

*Trazabilidad: SPEC-12 · Requisito 5.*

#### Scenario: El carrito cambia después de cotizar
- **DADO** una cotización vigente en `CheckoutPage`
- **CUANDO** el cliente vuelve al carrito y agrega otro producto
- **ENTONCES** la cotización se invalida y se recalcula automáticamente al reabrir `CheckoutPage`

#### Scenario: Cotización vencida
- **DADO** una cotización con más de 30 minutos
- **CUANDO** el cliente confirma el pago
- **ENTONCES** se recotiza antes de crear el pedido y, si el costo cambió, se muestra el nuevo total antes de continuar

## Requisitos no funcionales

- **Privacidad:** la dirección y el documento no se solicitan ni se envían al LLM; si el cliente los menciona por chat, se le redirige a completarlos en `CheckoutPage`. El documento escrito en el chat se redacta (SPEC-05 · Req. 9); una dirección escrita libremente no se puede detectar de forma fiable y queda como riesgo aceptado (ver `docs/conversacion/privacidad.md`).
- **Seguridad:** el guardado de direcciones se hace con el token del cliente (el titular). El número de documento se guarda solo en el snapshot del pedido (`checkout.resumen.contacto`), nunca en una tabla propia de datos de identidad.
- **Rendimiento:** la cotización tarda p95 ≤ 600 ms (es síncrona según F-01 de Despacho).
- **Datos de ubigeo:** el selector de distrito usa un JSON estático (INEI), limitado a Lima y Callao si Despacho solo cubre esas zonas.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
