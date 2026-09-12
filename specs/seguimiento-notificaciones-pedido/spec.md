# Especificación: Seguimiento y Notificaciones

## 1. Contexto
Después de realizar la compra, el cliente necesita confirmación de su transacción y la capacidad de rastrear en qué estado se encuentra su entrega interactuando con el mismo canal.

## 2. Propósito
Mantener al cliente informado sobre la confirmación de su compra y permitirle consultar el estado actualizado de su pedido en cualquier momento.

## 3. Alcance
Incluye:
- Notificaciones por correo del pedido al cliente.
- Consulta del estado de un pedido.

## 4. Requisitos

### Requisito 1: Notificación de confirmación
El sistema DEBE enviar un correo electrónico automático al cliente una vez que su pedido se haya grabado exitosamente.

#### Escenario: Envío de correo de pedido
- DADO que el pago con tarjeta se ha simulado y el pedido se ha grabado
- CUANDO el proceso de checkout finaliza exitosamente
- ENTONCES el sistema dispara una notificación por correo al cliente con el resumen de su compra

#### Escenario: Fallo temporal en el envío de la notificación
- DADO que el pedido se ha grabado exitosamente
- CUANDO el servicio de envío de correo no está disponible en ese momento
- ENTONCES el sistema reintenta el envío de forma asíncrona sin bloquear la confirmación del pedido al cliente en el chat

### Requisito 2: Consulta de estado
El sistema DEBE permitir al usuario preguntar por el estado de su orden utilizando el chatbot.

#### Escenario: Seguimiento de pedido existente
- DADO que el cliente tiene un pedido registrado previamente
- CUANDO el cliente consulta el estado de su pedido proporcionando su código u orden
- ENTONCES el sistema devuelve el estado actual del pedido

#### Escenario: Consulta con código de pedido inexistente o inválido
- DADO que el cliente solicita el estado de un pedido
- CUANDO el código proporcionado no corresponde a ningún pedido registrado
- ENTONCES el sistema informa que no encontró el pedido y solicita al cliente verificar el código ingresado

## 5. Requisitos no funcionales
- Integración: El sistema debe consultar el estado del pedido comunicándose a través de APIs con el "Módulo de ventas y postventa" o el "Módulo de despacho y entrega".
- Disponibilidad: Las notificaciones deben procesarse de forma asíncrona para no bloquear el flujo de la aplicación.

## 6. Fuera de alcance
- Gestión de estados del despacho en ruta — Es función del Módulo de despacho y entrega a domicilio.
- Gestión de entregas fallidas — Le corresponde al operador/repartidor en su módulo respectivo.

## Criterio de completitud
La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
