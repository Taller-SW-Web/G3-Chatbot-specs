# Cupones de descuento

> Origen: SPEC-13 · Grupo: Checkout · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03), [`gestion-carrito`](../gestion-carrito/spec.md) (SPEC-11), Productos (SPEC-005 y SPEC-006 de Productos), Ventas (F1)

## Purpose

Permitir al cliente aplicar un código de descuento a su carrito desde el chat y ver su efecto real en el total antes de pagar.

## Contexto

Productos y Ofertas gestiona cupones asociados a promociones de modalidad `CUPON`. Su SPEC-005 fija las reglas:

- Los canales **validan** un código por API **sin consumirlo**. La respuesta indica si es válido, el motivo de rechazo, el descuento y el importe resultante.
- El uso se **consume** cuando Ventas confirma el pedido tras el pago, y solo si el cupón forma parte del beneficio finalmente seleccionado.
- Si el cupón tiene límite por cliente, la validación exige un `customerRef`.
- La combinación con promociones automáticas y ofertas la resuelve el motor de Productos.

## Alcance

Incluye:
- Ingreso del código por texto ("tengo el cupón RUN10") o en el campo del carrito.
- Validación contra Productos con las líneas del carrito, el canal `CHATBOT` y el `customerRef` del cliente.
- Presentación del descuento o del motivo de rechazo.
- Un solo cupón por carrito; quitar o reemplazar el cupón.
- Revalidación del cupón al cambiar el carrito y al iniciar el checkout.
- Envío del código a Ventas en el snapshot del pedido, para su consumo al confirmar.

### Fuera de alcance

- Consumo del uso del cupón: lo hacen Ventas y Productos al confirmar el pedido.
- Varios cupones simultáneos.
- Generación o distribución de cupones.

## Requirements

### Requirement: Aplicar un cupón válido
El sistema DEBE (SHALL) validar el código con Productos y, si es válido, guardarlo en el carrito y reflejar el descuento en los totales.

*Trazabilidad: SPEC-13 · Requisito 1.*

#### Scenario: Cupón válido por texto
- **DADO** un cliente autenticado con un carrito de S/ 300 elegible
- **CUANDO** escribe "aplica el cupón RUN10"
- **ENTONCES** se invoca `aplicar_cupon {codigo: "RUN10"}`, Productos responde `valido: true, descuento: 30.00` y el carrito muestra "Cupón RUN10: -S/ 30.00" con el total actualizado

#### Scenario: Código con espacios o minúsculas
- **DADO** el código " run10 "
- **CUANDO** se aplica
- **ENTONCES** se normaliza (trim y mayúsculas) antes de validar

#### Scenario: Reemplazar un cupón
- **DADO** un carrito con el cupón A
- **CUANDO** el cliente aplica el cupón B y este es válido
- **ENTONCES** se pregunta "¿Reemplazo el cupón A por B?" y, al confirmar, queda solo B

### Requirement: Rechazo con motivo claro
El sistema DEBE (SHALL) mostrar el motivo de rechazo que devuelve Productos, traducido a un mensaje comprensible, sin aplicar el cupón.

| Motivo (Productos) | Mensaje |
|---|---|
| `INEXISTENTE` | "Ese cupón no existe. Revisa que esté bien escrito." |
| `EXPIRADO` / `NO_VIGENTE` | "Ese cupón ya no está vigente." |
| `AGOTADO` | "Ese cupón ya alcanzó su límite de usos." |
| `LIMITE_CLIENTE` | "Ya usaste este cupón el máximo de veces permitido." |
| `MONTO_MINIMO` | "Este cupón aplica para compras desde S/ X. Te faltan S/ Y." |
| `NO_APLICA_PRODUCTOS` | "Este cupón no aplica a los productos de tu carrito." |
| `NO_APLICA_CANAL` | "Este cupón no es válido en este canal." |
| `NO_COMBINABLE` | "Tu carrito ya tiene un beneficio mejor que no se combina con este cupón." |

*Trazabilidad: SPEC-13 · Requisito 2.*

#### Scenario: Monto mínimo no alcanzado
- **DADO** un cupón con un mínimo de S/ 200 y un carrito de S/ 150
- **CUANDO** se aplica
- **ENTONCES** se responde `422 CUPON_INVALIDO {motivo: MONTO_MINIMO}` y se muestra "Te faltan S/ 50.00", con el botón "Ver productos"

#### Scenario: Cupón no combinable
- **DADO** que Productos determina que la mejor alternativa para la cesta no incluye el cupón
- **CUANDO** se valida
- **ENTONCES** se informa que ya se aplica un beneficio mayor y el cupón no queda aplicado

### Requirement: Requiere sesión
El sistema DEBE (SHALL) exigir la sesión para aplicar cupones, porque los límites por cliente requieren `customerRef`.

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
El sistema DEBE (SHALL) revalidar el cupón cuando cambia el carrito y justo antes de crear el pedido, y retirarlo con aviso si dejó de ser válido.

*Trazabilidad: SPEC-13 · Requisito 4.*

#### Scenario: Quitar productos invalida el cupón
- **DADO** un cupón con mínimo de S/ 200 aplicado a un carrito de S/ 250
- **CUANDO** el cliente quita productos y el carrito baja a S/ 180
- **ENTONCES** el cupón se retira y se informa "Quitamos el cupón RUN10 porque tu compra ya no alcanza el mínimo"

#### Scenario: El cupón se agota antes de pagar
- **DADO** un cupón válido al aplicarlo
- **CUANDO** al iniciar el checkout Productos responde `AGOTADO`
- **ENTONCES** el checkout se detiene con `409 CARRITO_DESACTUALIZADO`, el cupón se retira y se muestra el nuevo total antes de continuar

### Requirement: Protección contra fuerza bruta
El sistema DEBE (SHALL) limitar los intentos fallidos de cupones.

*Trazabilidad: SPEC-13 · Requisito 5.*

#### Scenario: Demasiados intentos inválidos
- **DADO** un cliente con 5 cupones inválidos en 10 minutos
- **CUANDO** intenta otro
- **ENTONCES** se responde `429` y el mensaje "Demasiados intentos, espera unos minutos"

#### Scenario: Contador tras un cupón válido
- **DADO** un cliente con 3 intentos inválidos
- **CUANDO** aplica un cupón válido
- **ENTONCES** el contador de intentos fallidos se reinicia

## Requisitos no funcionales

- **Consistencia:** el chatbot no calcula el descuento del cupón; usa el que devuelve Productos. El total enviado a Ventas coincide con la última evaluación.
- **Idempotencia:** validar varias veces no consume usos (garantía de Productos); el chatbot nunca llama a una API de consumo.
- **Seguridad:** los códigos se registran en los logs parcialmente enmascarados (`RU***`).

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
