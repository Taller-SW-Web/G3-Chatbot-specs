# Catálogo de herramientas sin ambigüedades para el motor de conversación

## Why

La tabla de herramientas de SPEC-05 (`motor-conversacion`) no coincide con lo que el backend
expone y no alcanza para implementar el catálogo completo:

1. **Drift de nombres.** La spec publica `listar_pedidos` y `consultar_pedido`, pero el
   `ToolRegistry` registra una sola herramienta consolidada, `consultar_pedidos`
   (`mod_catalog/application/tools.py`), y `ActionDispatcher` mapea `MIS_PEDIDOS`,
   `CONSULTAR_PEDIDOS` y `VER_PEDIDO` a ella. Ninguna implementación puede cumplir la spec
   tal como está escrita sin inventar una segunda herramienta o un alias no documentado.
2. **Herramienta no documentada.** `silenciar_complementos` está implementada
   (`mod_catalog/application/tools.py`, `mod_catalog/application/discovery.py`) y el prompt
   del sistema la usa, pero no aparece en la tabla de intenciones ni en las reglas de sesión
   y confirmación.
3. **Contrato de resultados incompleto.** Para seguimiento, reclamos y devoluciones la spec
   nombra las herramientas pero no dice qué bloque devuelve cada una, con qué claves ni qué
   renderiza el frontend. `MessageBubble.renderBloque` descarta
   `LISTA_PEDIDOS`, `ESTADO_PEDIDO`, `CONSTANCIA_RECLAMO`, `ESTADO_RECLAMO`,
   `CONSTANCIA_DEVOLUCION` y `ESTADO_DEVOLUCION`; los componentes existen en `mod-orders` y
   `mod-postventa` pero no están cableados.
4. **Dos herramientas describen efectos que el backend no puede ejecutar.** `iniciar_checkout`
   parece crear el checkout y `cerrar_sesion` parece borrar cookies `httpOnly`; en realidad
   el checkout se crea en `CheckoutPage` y las cookies solo las borra el BFF en
   `POST /api/v1/sesion/logout`.

Sin este delta, cada implementador elige un nombre, un bloque o un efecto distinto y el
catálogo queda incompleto o contradictorio.

## What Changes

- **BREAKING (contrato de la spec, no del código):** se consolida el catálogo en
  `consultar_pedidos {pedidoId?, estado?}`. `listar_pedidos` y `consultar_pedido` dejan de ser
  nombres de herramienta y no se publican como alias al LLM. Las acciones directas
  `MIS_PEDIDOS`, `CONSULTAR_PEDIDOS` y `VER_PEDIDO` siguen existiendo y apuntan a la misma
  herramienta. Se documenta la razón y el impacto en `design.md`.
- Se incorpora `silenciar_complementos` a la tabla de intenciones (SPEC-05 · Req. 3) y al
  catálogo, con su efecto real: fija `contexto.crossSellSilenciado = true`, devuelve texto y
  ningún bloque, y no exige sesión ni confirmación.
- Se agrega el **contrato del catálogo**: 29 herramientas con argumentos, sesión,
  confirmación, bloque o acción resultante y spec dueña.
- Se agrega el **contrato de bloques** de pedidos, seguimiento, reclamos y devoluciones con las
  claves mínimas de `datos`, y se declaran dos tipos de bloque nuevos: `LISTA_RECLAMOS` y
  `LISTA_DEVOLUCIONES` (los componentes ya existen; el enum no los tenía).
- Se agrega el contrato de **acciones de cliente**: `IR_A_CHECKOUT`, `CERRAR_SESION`,
  `NUEVO_CHAT` y `BUSCAR_CHATS` las ejecuta el frontend; el backend solo las devuelve en un
  bloque `ACCIONES_RAPIDAS`.
- `iniciar_checkout` queda definido como acción `IR_A_CHECKOUT`: no crea el checkout, no
  cotiza, no pide dirección ni datos de tarjeta. El checkout y el pago solo ocurren en
  `CheckoutPage` (SPEC-14).
- `cerrar_sesion` queda definido como acción `CERRAR_SESION`: el frontend llama a
  `POST /api/v1/sesion/logout` (el BFF borra `chat_rt` y `chat_chg`) y limpia el token local;
  la herramienta nunca lee ni borra cookies.
- Se actualizan `docs/conversacion/intenciones.md` y los documentos de conversación que usaban
  los nombres anteriores, para que la tabla canónica no quede desalineada.
- Se documenta la brecha del renderizador frontend como **tarea de implementación**, no como
  comportamiento existente.

## Capabilities

- **Modified Capabilities:**
  - `motor-conversacion` (SPEC-05): se modifican los requisitos «Interpretación de la
    intención mediante herramientas», «Ejecución segura de herramientas» y «Consultar en el
    chat desde una tarjeta»; se agregan «Contrato del catálogo de herramientas», «Bloques de
    pedidos, seguimiento, reclamos y devoluciones» y «Acciones de cliente del chat».

## Impact

- **Backend (`mod_chat`, `mod_catalog`, `mod_orders`):** `ToolRegistry` debe publicar el
  catálogo completo (hoy faltan seguimiento, reclamos, devoluciones, cupones, login, reenvío,
  logout, checkout y navegación); `ActionDispatcher` gana las acciones `CONFIRMAR_RECLAMO` y
  `CONFIRMAR_DEVOLUCION`; `mod_postventa` expone los handlers de sus tres herramientas.
- **Backend (`shared/domain/block.py`):** dos valores nuevos en `BlockType`
  (`LISTA_RECLAMOS`, `LISTA_DEVOLUCIONES`).
- **Frontend (`mod-chat`):** `MessageBubble.renderBloque` debe renderizar los ocho bloques de
  pedidos y postventa; `ChatPage.ejecutarAccionRapida` debe interceptar las cuatro acciones de
  cliente. `mod-orders` y `mod-postventa` deben adaptar las props de sus componentes al
  contrato de `datos` (hoy son prototipos con datos de wireframe).
- **Contrato:** `docs/contratos-integracion.md` §2.1 lista los dos bloques nuevos y las
  acciones de cliente. No hay endpoints nuevos ni cambios de `docs/openapi.json`.
- **Datos:** sin migraciones ni tablas nuevas. `claim_ref` y `return_ref` no cambian.
- **Compatibilidad:** ninguna herramienta implementada se renombra en código; el único cambio
  de nombre es de la spec al código ya mergeado. Los clientes del BFF no se ven afectados.

## Rollback

El cambio es documental y de contrato. Si se revierte, se vuelve a la versión anterior de
SPEC-05 y de `intenciones.md`; el backend conserva `consultar_pedidos`, que ya está en `main`.
No hay datos, migraciones ni endpoints que deshacer. La única precaución es no reintroducir
`listar_pedidos`/`consultar_pedido` como herramientas del LLM: dos herramientas con la misma
intención degradan la precisión del catálogo y vuelven a abrir el drift.

## Preguntas abiertas

Ninguna de producto. Las tres decisiones de contrato (consolidar en `consultar_pedidos`, dos
bloques de lista para postventa y cuatro acciones de cliente) se justifican en `design.md` con
la evidencia del código actual y se pueden revertir por separado.
