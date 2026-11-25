# Catálogo de tools de `motor-conversacion` (M5)

Delta de especificación para implementar el catálogo completo de herramientas del canal sin
ambigüedades: consolida la consulta de pedidos en `consultar_pedidos`, incorpora
`silenciar_complementos`, fija el contrato de bloques de pedidos, seguimiento, reclamos y
devoluciones, y separa las acciones que ejecuta el frontend (`IR_A_CHECKOUT`, `CERRAR_SESION`,
`NUEVO_CHAT`, `BUSCAR_CHATS`) de las herramientas del backend.

- Propuesta: [`proposal.md`](proposal.md)
- Delta de la spec: [`specs/motor-conversacion/spec.md`](specs/motor-conversacion/spec.md)
- Diseño y decisiones: [`design.md`](design.md)
- Tareas de implementación: [`tasks.md`](tasks.md)
