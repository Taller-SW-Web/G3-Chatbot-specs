# Gestión del carrito

> Origen: SPEC-11 · Grupo: Carrito · Requiere sesión: No · Depende de: [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`ofertas-promociones`](../ofertas-promociones/spec.md) (SPEC-08), [`tarjetas-detalle-producto`](../tarjetas-detalle-producto/spec.md) (SPEC-09), [`validacion-stock`](../validacion-stock/spec.md) (SPEC-10), [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03) (fusión)

## Purpose

Permitir al cliente agregar, modificar, quitar y revisar productos en su carrito por conversación o por la UI, con totales correctos y actualizados.

## Contexto

El carrito es responsabilidad de cada canal: Ventas lo deja fuera del alcance de F1. En el chatbot el cliente arma su compra conversando ("agrega dos", "quita las medias", "¿cuánto llevo?") o con botones.

El carrito vive en la base de datos propia del chatbot. Puede ser anónimo (ligado a la conversación) o del cliente (persistente entre sesiones), y los precios y descuentos se recalculan siempre contra Productos.

## Alcance

Incluye:
- Agregar un SKU con cantidad (validando el stock, SPEC-10).
- Incrementar, disminuir o fijar la cantidad; quitar una línea; vaciar el carrito (con confirmación).
- Ver el carrito: líneas, subtotal, descuentos (evaluación de Productos, SPEC-08), cupón (SPEC-13), envío (SPEC-12) y total.
- Persistencia: carrito anónimo por conversación y carrito de cliente único y activo.
- Recalcular precios y avisar los cambios cada vez que se muestra el carrito.
- Límites: 10 unidades por línea y 20 líneas.
- Productos desactivados dentro del carrito.

### Fuera de alcance

- Lista de deseos o favoritos: es una funcionalidad del Marketplace.
- Guardar para después o tener varios carritos.
- Compartir el carrito.

## Requirements

### Requirement: Agregar productos
El sistema DEBE (SHALL) agregar un SKU validado al carrito o sumar la cantidad si el SKU ya existe, y confirmar con un resumen breve.

*Trazabilidad: SPEC-11 · Requisito 1.*

#### Scenario: Agregar por conversación
- **DADO** un carrusel previo con zapatillas
- **CUANDO** el cliente escribe "agrega las primeras en talla 41"
- **ENTONCES** se resuelve el SKU (SPEC-09), se valida el stock (SPEC-10), se crea la línea y se responde "Agregué Zapatillas X talla 41 (S/ 289.90). Tu carrito: 1 producto · S/ 289.90" con los botones "Ver carrito", "Seguir comprando" y "Pagar"

#### Scenario: Agregar un SKU ya existente
- **DADO** 1 × SKU-A en el carrito
- **CUANDO** se agrega 1 × SKU-A
- **ENTONCES** la línea queda con cantidad 2 (no se duplica)

#### Scenario: Límite por línea
- **DADO** 9 × SKU-A en el carrito
- **CUANDO** se intentan agregar 3
- **ENTONCES** se responde `422 LIMITE_CANTIDAD` con el mensaje "El máximo por producto es 10 unidades" y se ofrece "Agregar 1"

#### Scenario: Límite de líneas
- **DADO** 20 líneas en el carrito
- **CUANDO** se intenta agregar un SKU nuevo
- **ENTONCES** se rechaza con el mensaje "Tu carrito llegó al máximo de 20 productos distintos"

### Requirement: Modificar y quitar
El sistema DEBE (SHALL) permitir cambiar cantidades y quitar líneas por texto o por controles de la UI, validando el stock en los incrementos.

*Trazabilidad: SPEC-11 · Requisito 2.*

#### Scenario: Cambiar la cantidad por texto
- **DADO** 1 × "Medias running" en el carrito
- **CUANDO** el cliente escribe "pon 3 de las medias"
- **ENTONCES** se resuelve la línea por nombre dentro del carrito, se valida el stock y la cantidad queda en 3

#### Scenario: Referencia ambigua dentro del carrito
- **DADO** dos líneas de zapatillas en el carrito
- **CUANDO** el cliente escribe "quita las zapatillas"
- **ENTONCES** se pregunta "¿Cuáles?" y se muestran las dos líneas como opciones

#### Scenario: Cantidad cero
- **DADO** una línea con cantidad 1
- **CUANDO** se pulsa "−"
- **ENTONCES** la línea se elimina y el cambio se puede deshacer durante 10 s con el botón "Deshacer"

#### Scenario: Vaciar el carrito
- **DADO** un carrito con líneas
- **CUANDO** el cliente pide vaciarlo
- **ENTONCES** se exige confirmación en la UI (SPEC-05 Req. 4) y, al confirmar, el carrito queda vacío (sin cupón ni envío)

### Requirement: Ver el carrito con totales recalculados
El sistema DEBE (SHALL) mostrar el bloque `CARRITO` recalculando en cada lectura los precios (Pricing, canal `CHATBOT`), los descuentos (`POST /promociones/evaluar`) y la validez del cupón. Los totales son: `subtotal` (Σ precio regular vigente × cantidad), `descuentos[]`, `costoEnvio` (si hay cotización) y `total`.

*Trazabilidad: SPEC-11 · Requisito 3.*

#### Scenario: Resumen del carrito
- **DADO** 2 líneas con una promoción aplicable
- **CUANDO** el cliente escribe "¿cuánto llevo?"
- **ENTONCES** se muestra el bloque `CARRITO` con las líneas (imagen, nombre, variante, cantidad y precio), el subtotal, las líneas de descuento con su nombre, "Envío: se calcula al elegir la dirección" y el total

#### Scenario: El precio cambió
- **DADO** una línea agregada a S/ 239.90 cuyo precio vigente ahora es S/ 299.90
- **CUANDO** se muestra el carrito
- **ENTONCES** el total usa S/ 299.90 y aparece el aviso "El precio de X cambió de S/ 239.90 a S/ 299.90"

#### Scenario: Producto desactivado en el carrito
- **DADO** una línea cuyo SKU pasó a `INACTIVO`
- **CUANDO** se muestra el carrito
- **ENTONCES** la línea aparece marcada como "Ya no disponible", no suma al total, queda excluida del checkout y se ofrece "Quitar"

#### Scenario: Carrito vacío
- **DADO** un carrito sin líneas
- **CUANDO** se pide verlo
- **ENTONCES** se responde "Tu carrito está vacío" con las acciones "Ver ofertas" y "Buscar productos"

#### Scenario: Evaluación de promociones no disponible
- **DADO** que `POST /promociones/evaluar` falla
- **CUANDO** se muestra el carrito
- **ENTONCES** se muestran el subtotal con precios vigentes y la nota "No pudimos calcular promociones en este momento", y el checkout queda bloqueado hasta que la evaluación responda (para no cobrar un total distinto)

### Requirement: Persistencia y ciclo de vida
El sistema DEBE (SHALL) persistir el carrito: el anónimo por conversación (expira a los 7 días de inactividad) y el de cliente como único carrito `ACTIVO` por cliente, conservándose entre sesiones y dispositivos.

*Trazabilidad: SPEC-11 · Requisito 4.*

#### Scenario: Volver otro día con sesión
- **DADO** un cliente que dejó productos en su carrito ayer
- **CUANDO** abre el chat e inicia sesión
- **ENTONCES** recupera su carrito, con los totales recalculados

#### Scenario: Carrito convertido
- **DADO** un pedido pagado (SPEC-15)
- **CUANDO** se confirma
- **ENTONCES** el carrito queda `CONVERTIDO` y el cliente empieza con uno vacío

## Requisitos no funcionales

- **Concurrencia:** bloqueo optimista (`version`) en el carrito; dos operaciones simultáneas no pierden cambios (una reintenta).
- **Rendimiento:** la lectura del carrito con recálculo (hasta 20 líneas) tarda p95 ≤ 900 ms; las operaciones de agregar o modificar, p95 ≤ 700 ms sin LLM.
- **Precisión:** cálculos con `Decimal` y redondeo a 2 decimales solo al presentar, igual que Productos.
- **Auditoría:** cada cambio del carrito queda como mensaje de tipo `HERRAMIENTA` en la conversación.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
