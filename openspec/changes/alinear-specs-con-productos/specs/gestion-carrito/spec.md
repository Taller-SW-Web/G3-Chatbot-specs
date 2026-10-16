## MODIFIED Requirements

### Requirement: Ver el carrito con totales recalculados
El sistema DEBE (SHALL) mostrar el bloque `CARRITO` recalculando en cada lectura los precios (`GET /precios`, canal `CHATBOT`), el descuento (`POST /promociones/evaluar`, que devuelve un único `discount_amount` para toda la cesta) y la validez del cupón. Los totales son: `subtotal` (Σ precio regular vigente × cantidad), `descuento` (un solo importe), `costoEnvio` (si hay cotización) y `total`.

*Trazabilidad: SPEC-11 · Requisito 3.*

#### Scenario: Resumen del carrito
- **DADO** 2 líneas con una promoción aplicable
- **CUANDO** el cliente escribe "¿cuánto llevo?"
- **ENTONCES** se muestra el bloque `CARRITO` con las líneas (imagen, nombre, variante, cantidad y precio), el subtotal, una línea de descuento con el nombre de la promoción (se busca por `promotion_id` en `GET /promociones`, pero Productos no garantiza que figure ahí, y `promotion_id` puede ser nulo; si no se resuelve, "Descuento", comportamiento interino que no es contrato de Productos) y su importe, "Envío: se calcula al elegir la dirección" y el total

#### Scenario: El precio cambió
- **DADO** una línea agregada a S/ 239.90 cuyo precio vigente ahora es S/ 299.90
- **CUANDO** se muestra el carrito
- **ENTONCES** el total usa S/ 299.90 y aparece el aviso "El precio de X cambió de S/ 239.90 a S/ 299.90"

#### Scenario: Producto desactivado en el carrito
- **DADO** una línea cuyo SKU está `AGOTADO`, o cuyo precio o disponibilidad responden un error de identificación o elegibilidad (SKU inexistente, inactivo, no comercializable o sin precio vigente)
- **CUANDO** se muestra el carrito
- **ENTONCES** la línea se marca "Agotado" si el estado es `AGOTADO` y "Ya no disponible" si hubo error de identificación o elegibilidad (nunca se presenta un SKU inexistente o inactivo como agotado), no suma al total, queda excluida del checkout y se ofrece "Quitar"

#### Scenario: Disponibilidad indeterminada en el carrito
- **DADO** una línea con estado `INDETERMINADO`
- **CUANDO** se muestra el carrito
- **ENTONCES** la línea se mantiene y suma al total, con el aviso "No pudimos confirmar el stock" (comportamiento interino, no contrato de Productos)

#### Scenario: Carrito vacío
- **DADO** un carrito sin líneas
- **CUANDO** se pide verlo
- **ENTONCES** se responde "Tu carrito está vacío" con las acciones "Ver ofertas" y "Buscar productos"

#### Scenario: Evaluación de promociones no disponible
- **DADO** que `POST /promociones/evaluar` falla
- **CUANDO** se muestra el carrito
- **ENTONCES** se muestran el subtotal con precios vigentes y la nota "No pudimos calcular promociones en este momento", y el checkout queda bloqueado hasta que la evaluación responda (para no cobrar un total distinto)

#### Scenario: Límite de frecuencia en la evaluación
- **DADO** que `POST /promociones/evaluar` responde `429`
- **CUANDO** se muestra el carrito
- **ENTONCES** se respeta `Retry-After` si viene en la respuesta, no se reintenta antes, se aplica el mismo tratamiento que ante una falla de la evaluación y no se supone una cuota numérica
