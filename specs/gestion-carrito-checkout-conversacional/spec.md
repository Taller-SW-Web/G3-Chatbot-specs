# Especificación: Gestión de Carrito y Checkout Conversacional

## 1. Contexto
Una vez que el chatbot presenta los productos, el cliente debe poder concretar su compra directamente en la interfaz del chat, garantizando que el sistema obtenga la información de contacto y valide el pago de forma segura.

## 2. Propósito
Facilitar la agregación de productos, validación de formato de contacto del cliente y simulación de pago con tarjeta para generar un pedido oficial en el sistema.

## 3. Alcance
Incluye:
- Agregar productos al carrito mediante conversación.
- Validación de formato del número celular y correo del cliente (la verificación de existencia contra el sistema central corresponde a la especificación "Validación de Identidad e Integración de Usuario").
- Grabación del pedido y pago con tarjeta.

## 4. Requisitos

### Requisito 1: Gestión del carrito de compras
El sistema DEBE permitir al usuario añadir los productos sugeridos a un carrito virtual manteniendo el contexto de la conversación.

#### Escenario: Agregar producto al carrito exitosamente
- DADO que el chatbot ha mostrado un producto disponible
- CUANDO el cliente indica en lenguaje natural su intención de comprarlo o agregarlo
- ENTONCES el sistema añade el producto al carrito del usuario e informa el subtotal actualizado

#### Escenario: Agregar una unidad adicional de un producto ya presente en el carrito
- DADO que el cliente ya tiene un producto agregado en su carrito
- CUANDO el cliente solicita nuevamente el mismo producto en la conversación
- ENTONCES el sistema incrementa la cantidad de esa línea en lugar de duplicarla, y actualiza el subtotal

### Requisito 2: Validación de formato de datos de contacto
El sistema DEBE exigir y validar el formato de los datos de contacto antes de proceder al pago.

#### Escenario: Validación de contacto correcta
- DADO que el cliente tiene productos en su carrito y desea pagar
- CUANDO el sistema le solicita su número celular y correo, y el cliente los ingresa con formato válido
- ENTONCES el sistema aprueba la validación de formato y continúa el flujo hacia la verificación de identidad

#### Escenario: Formato de contacto inválido
- DADO que el sistema solicita datos de contacto
- CUANDO el cliente ingresa un número de celular o correo con formato incorrecto
- ENTONCES el sistema rechaza la entrada y solicita al usuario que ingrese la información nuevamente

### Requisito 3: Simulación de pago y grabación
El sistema DEBE procesar la transacción de pago simulada y registrar oficialmente el pedido.

#### Escenario: Pago exitoso y grabación
- DADO que los datos de contacto están validados y el cliente ingresa su tarjeta
- CUANDO la simulación de pago con tarjeta es aprobada
- ENTONCES el sistema realiza la grabación del pedido

#### Escenario: Pago rechazado
- DADO que los datos de contacto están validados y el cliente ingresa su tarjeta
- CUANDO la simulación de pago con tarjeta es rechazada
- ENTONCES el sistema informa al cliente del rechazo, no graba el pedido y permite reintentar el pago

## 5. Requisitos no funcionales
- Seguridad: La información de la tarjeta y datos del cliente deben ser manejados bajo criterios de desarrollo seguro.
- Integración: El microservicio del chatbot debe interactuar por API asíncrona con el "Módulo de ventas y postventa", ya que este es el dueño de la entidad "pedido", y con el "Módulo de seguridad y autenticación de usuarios" para la verificación de identidad (ver especificación "Validación de Identidad e Integración de Usuario").

## 6. Fuera de alcance
- Autenticación de usuarios mediante OTP o contraseñas — Es responsabilidad del Módulo de Seguridad y autenticación de usuarios.
- Verificación de existencia del cliente contra el sistema central de usuarios — Corresponde a la especificación "Validación de Identidad e Integración de Usuario".
- Anulación o devoluciones de pedidos — Le corresponde al módulo de ventas y postventa.

## Criterio de completitud
La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
