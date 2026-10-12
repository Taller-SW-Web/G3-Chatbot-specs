## MODIFIED Requirements

### Requirement: Aplicar un cupón válido
El sistema DEBE (SHALL) validar el código con Productos (`POST /api/v1/cupones/validar` con `coupon_code`, `channel_id`, `lines` y `customer_ref`) y, si `valid = true`, guardarlo en el carrito y reflejar el descuento en los totales.

*Trazabilidad: SPEC-13 · Requisito 1.*

#### Scenario: Cupón válido por texto
- **DADO** un cliente autenticado con un carrito de S/ 300 elegible
- **CUANDO** escribe "aplica el cupón RUN10"
- **ENTONCES** se invoca `aplicar_cupon {codigo: "RUN10"}`, Productos responde `valid: true, discount_amount: 30.00` y el carrito muestra "Cupón RUN10: -S/ 30.00" con el total actualizado

#### Scenario: Código con espacios o minúsculas
- **DADO** el código " run10 "
- **CUANDO** se aplica
- **ENTONCES** se normaliza (trim y mayúsculas) antes de validar

#### Scenario: Reemplazar un cupón
- **DADO** un carrito con el cupón A
- **CUANDO** el cliente aplica el cupón B y este es válido
- **ENTONCES** se pregunta "¿Reemplazo el cupón A por B?" y, al confirmar, queda solo B

### Requirement: Rechazo con motivo claro
El sistema DEBE (SHALL) traducir el campo `code` de la respuesta de Productos (lista cerrada) a un mensaje comprensible, sin aplicar el cupón. El sistema NO DEBE (SHALL NOT) ramificar por `rejection_reason`, que es solo texto humano.

| `code` (Productos) | Mensaje |
|---|---|
| `CUPON_NO_ENCONTRADO` | "Ese cupón no existe. Revisa que esté bien escrito." |
| `CUPON_INACTIVO` / `CUPON_FUERA_DE_VIGENCIA` | "Ese cupón ya no está vigente." |
| `CUPON_AGOTADO` | "Ese cupón ya alcanzó su límite de usos." |
| `LIMITE_CUPON_CLIENTE_ALCANZADO` | "Ya usaste este cupón el máximo de veces permitido." |
| `MONTO_MINIMO_NO_ALCANZADO` | "Este cupón aplica para compras con un mínimo mayor al de tu carrito." |
| `CUSTOMER_REF_REQUERIDO` | "Inicia sesión para usar este cupón." |
| `CUPON_NO_COMBINABLE` | "Tu carrito ya tiene un beneficio mejor que no se combina con este cupón." |

*Trazabilidad: SPEC-13 · Requisito 2.*

#### Scenario: Monto mínimo no alcanzado
- **DADO** un cupón con monto mínimo no alcanzado por el carrito
- **CUANDO** se aplica
- **ENTONCES** Productos responde `valid: false, code: MONTO_MINIMO_NO_ALCANZADO`, el chatbot responde `422 CUPON_INVALIDO` y muestra el mensaje de la tabla con el botón "Ver productos" (el monto exacto del mínimo no viene en la respuesta)

#### Scenario: Cupón no combinable
- **DADO** que Productos responde `code: CUPON_NO_COMBINABLE`
- **CUANDO** se valida
- **ENTONCES** se informa que ya se aplica un beneficio mayor y el cupón no queda aplicado

#### Scenario: Cupón que exige cliente identificado
- **DADO** un cupón con límite por cliente y un `customer_ref` ausente
- **CUANDO** Productos responde `code: CUSTOMER_REF_REQUERIDO`
- **ENTONCES** se pide iniciar sesión y se conserva la acción pendiente (Requisito "Requiere sesión")

### Requirement: Requiere sesión
El sistema DEBE (SHALL) exigir la sesión para aplicar cupones y enviar `customer_ref` igual al `sub` del token del **cliente** (nunca el `sub` del token de servicio), porque Productos aplica límites por cliente.

*Trazabilidad: SPEC-13 · Requisito 3.*

#### Scenario: Visitante anónimo con cupón
- **DADO** un visitante sin sesión
- **CUANDO** intenta aplicar un cupón
- **ENTONCES** se pide iniciar sesión y se guarda `accionPendiente = APLICAR_CUPON{codigo}` para aplicarlo automáticamente después

#### Scenario: Cupón aplicado y cierre de sesión
- **DADO** un cliente con cupón que cierra sesión
- **CUANDO** el carrito vuelve a ser anónimo
- **ENTONCES** el cupón no se conserva en el carrito anónimo

### Requirement: Revalidación
El sistema DEBE (SHALL) revalidar el cupón cuando cambia el carrito y justo antes de crear el pedido, y retirarlo con aviso si `valid` pasó a `false`.

*Trazabilidad: SPEC-13 · Requisito 4.*

#### Scenario: Quitar productos invalida el cupón
- **DADO** un cupón con monto mínimo aplicado a un carrito que lo alcanzaba
- **CUANDO** el cliente quita productos y el carrito baja del mínimo
- **ENTONCES** el cupón se retira y se informa "Quitamos el cupón RUN10 porque tu compra ya no alcanza el mínimo"

#### Scenario: El cupón se agota antes de pagar
- **DADO** un cupón válido al aplicarlo
- **CUANDO** al iniciar el checkout Productos responde `code: CUPON_AGOTADO`
- **ENTONCES** el checkout se detiene con `409 CARRITO_DESACTUALIZADO`, el cupón se retira y se muestra el nuevo total antes de continuar
