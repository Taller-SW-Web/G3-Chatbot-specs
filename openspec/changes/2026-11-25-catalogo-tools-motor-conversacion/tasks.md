# Tasks

## 1. Specs y documentos (este PR)

- [x] 1.1 `motor-conversacion`: consolidar el catálogo en `consultar_pedidos {pedidoId?, estado?}` y retirar `listar_pedidos`/`consultar_pedido` como nombres de herramienta (Req. 3, Req. 6 y Req. 13).
- [x] 1.2 `motor-conversacion`: agregar `silenciar_complementos` a la tabla de intenciones y a las reglas de sesión/confirmación.
- [x] 1.3 `motor-conversacion`: agregar el requisito «Contrato del catálogo de herramientas» con las 29 herramientas, argumentos, sesión, confirmación y resultado.
- [x] 1.4 `motor-conversacion`: agregar el requisito «Bloques de pedidos, seguimiento, reclamos y devoluciones» con las claves mínimas de cada bloque y los dos tipos nuevos (`LISTA_RECLAMOS`, `LISTA_DEVOLUCIONES`).
- [x] 1.5 `motor-conversacion`: agregar el requisito «Acciones de cliente del chat» (`IR_A_CHECKOUT`, `CERRAR_SESION`, `NUEVO_CHAT`, `BUSCAR_CHATS`).
- [x] 1.6 `docs/conversacion/intenciones.md`: nombres canónicos en EP-03, EP-07 y EP-05; nota de acciones de cliente.
- [x] 1.7 `docs/conversacion/flujos-conversacion.md`, `dialogos-ejemplo.md` y `kpis.md`: reemplazar `listar_pedidos`/`consultar_pedido` por `consultar_pedidos`.
- [x] 1.8 `docs/contratos-integracion.md` §2.1: documentar los bloques `LISTA_RECLAMOS`/`LISTA_DEVOLUCIONES` y las cuatro acciones de cliente.
- [x] 1.9 `consulta-estado-pedido`, `inicio-sesion` y `checkout-pago` (`design.md`): alinear los nombres y el efecto de las herramientas.
- [x] 1.10 `docs/producto/historias/EP-02-conversacion.md`: actualizar la trazabilidad del escenario «Desde una tarjeta de pedido».
- [x] 1.11 Validar con `python scripts/check_links.py` y `npx --yes @fission-ai/openspec validate --specs`.

## 2. Backend — catálogo y acciones (`mod_chat`, `mod_catalog`, `mod_orders`)

- [x] 2.1 `shared/domain/block.py`: agregar `LISTA_RECLAMOS` y `LISTA_DEVOLUCIONES` a `BlockType` (el frontend ya los declara con TODO en `BloqueTipo.ts`; quitarlo al cablearlos).
- [x] 2.2 `mod_chat`/`ActionDispatcher`: agregar `CONFIRMAR_RECLAMO` y `CONFIRMAR_DEVOLUCION`; verificar que las cuatro acciones de cliente no estén en `QUICK_ACTIONS` (deben caer en `ACCION_DESCONOCIDA` si llegan).
- [x] 2.3 `mod_orders`/`order_handlers.py`: aplicar la regla D7 — `consultar_pedidos` sin argumentos muestra `ESTADO_PEDIDO` solo si hay exactamente un pedido no finalizado; con un único pedido finalizado devuelve `LISTA_PEDIDOS`.
- [x] 2.4 `mod_chat`: implementar el handler de `consultar_seguimiento` con `SeguimientoPedido` → `ESTADO_PEDIDO.datos.seguimiento` y sus hitos; tolerar `404` de Despacho como «aún se está preparando» (SPEC-18).
- [x] 2.5 `mod_chat`: implementar `iniciar_checkout` como devolución de la acción `IR_A_CHECKOUT` (sin llamar a `POST /checkout`), con `REQUIERE_SESION` y `accionPendiente = INICIAR_CHECKOUT` cuando falte sesión.
- [x] 2.6 `mod_chat`: implementar `cerrar_sesion`, `nueva_conversacion` y `buscar_conversaciones` como devolución de sus acciones de cliente; ninguna debe tocar cookies ni crear conversaciones.
- [x] 2.7 `mod_chat`: implementar `solicitar_login`, `reenviar_verificacion` (formulario `REENVIO_VERIFICACION`), `aplicar_cupon` y `quitar_cupon`; registrar sus contratos en `tool_contracts.py`.
- [x] 2.8 `mod_chat`: registrar en `tool_contracts.py` y en el `ToolRegistry` las seis herramientas de postventa (`preparar_reclamo`, `listar_reclamos`, `consultar_reclamo`, `preparar_devolucion`, `listar_devoluciones`, `consultar_devolucion`).
- [x] 2.9 `mod_postventa`: handlers de las seis herramientas, con pertenencia por `sub` y bloques según el contrato de `datos`; `CONFIRMAR_RECLAMO`/`CONFIRMAR_DEVOLUCION` registran, persisten el mensaje y devuelven la constancia.
- [x] 2.10 Pruebas unitarias por herramienta: argumentos inválidos (`extra="forbid"`), `REQUIERE_SESION`, pertenencia ajena, bloque esperado y ausencia de alias.

## 3. Frontend — renderer y acciones (`mod-chat`, `mod-orders`, `mod-postventa`)

- [x] 3.1 `MessageBubble.renderBloque`: agregar los casos `LISTA_PEDIDOS`, `ESTADO_PEDIDO`, `LISTA_RECLAMOS`, `ESTADO_RECLAMO`, `CONSTANCIA_RECLAMO`, `LISTA_DEVOLUCIONES`, `ESTADO_DEVOLUCION` y `CONSTANCIA_DEVOLUCION` importando por `public.ts`.
- [x] 3.2 `Bloque.ts`/`BloqueTipo.ts`: uniones discriminadas para los ocho bloques, con `datos` según el contrato del delta.
- [x] 3.3 `mod-orders`: adaptar `ListaPedidos` a `{pedidoId, fecha, total, estado, estadoEtiqueta, canal}` y `EstadoPedido` a `datos.hitos` + `datos.seguimiento`; agregar la acción "Ver seguimiento" cuando `detalleDisponible` sea verdadero.
- [x] 3.4 `mod-postventa`: adaptar `ListaReclamos`, `EstadoReclamo`, `ConstanciaReclamo`, `ListaDevoluciones`, `EstadoDevolucion` y `ConstanciaDevolucion` al contrato de `datos`; mostrar `respuestaVisibleCliente` y `resolucion.fundamento` sin reformular.
- [x] 3.5 `ChatPage.ejecutarAccionRapida`: interceptar `IR_A_CHECKOUT`, `CERRAR_SESION`, `NUEVO_CHAT` y `BUSCAR_CHATS` antes de `ejecutarAccionChatUseCase`; ejecutarlas una sola vez por turno y no al rehidratar el historial.
- [x] 3.6 `CERRAR_SESION`: reutilizar el logout de `mod-auth` (`POST /sesion/logout` + limpieza de `chatStore`), sin duplicar la lógica.
- [x] 3.7 `IR_A_CHECKOUT`: navegar a `/checkout` con la sección de dirección enfocada; sin sesión, abrir el login y conservar `INICIAR_CHECKOUT`.
- [x] 3.8 Pruebas de renderer: un caso por bloque con el `datos` real del backend; probar que un bloque desconocido sigue sin renderizarse y que los ocho nuevos sí.
- [x] 3.9 Cablear `FORMULARIO/LOGIN` y `FORMULARIO/REENVIO_VERIFICACION` en el chat (hoy `MessageBubble` solo pinta `OTP_CELULAR` y `REGISTRO`), reutilizando `LoginForm`/`ReenviarVerificacionForm` o abriendo `AuthModal`.

## 4. Evaluación y QA

- [ ] 4.1 Actualizar `evals/intenciones.jsonl`: las frases de EP-07 apuntan a `consultar_pedidos` (con y sin `pedidoId`) y las de INT-CAT-11 a `silenciar_complementos`.
- [ ] 4.2 Verificar precisión de intención ≥ 90 % con el catálogo nuevo.
- [ ] 4.3 Prueba E2E: "mis pedidos" → lista; elegir uno → estado; "¿ya viene?" → seguimiento; "mis reclamos" → lista; abrir uno → estado; enviar reclamo → constancia.
- [ ] 4.4 Prueba de contrato: `CERRAR_SESION` enviada al BFF responde `ACCION_DESCONOCIDA` y no borra cookies; `IR_A_CHECKOUT` no crea checkout.
- [ ] 4.5 Revisar que ningún documento operativo (fuera de los históricos) siga citando `listar_pedidos` o `consultar_pedido`.

## 5. Archivo

- [ ] 5.1 Aplicar el delta a `openspec/specs/motor-conversacion/spec.md` y mover el cambio a `openspec/changes/archive/` cuando las tareas 2.x y 3.x estén mergeadas.

> Implementado en backend #166 y frontend #141 (2026-11-25). Quedan las tareas 4.x (evals/E2E/QA) y 5.1 (archivar el delta).
