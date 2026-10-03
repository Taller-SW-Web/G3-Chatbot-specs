# Diseño: alineación de specs con el prototipo

## Objetivo y alcance

Este cambio documenta seis elementos de UX ya decididos para el frontend existente. No cambia la arquitectura de módulos, no añade tablas y no implementa código. Los requisitos de comportamiento viven en las deltas de SPEC-03, SPEC-04, SPEC-05, SPEC-12 y SPEC-23; este archivo registra la composición y los contratos necesarios.

## Frontend

### Sesión y navegación

- `Sidebar` ofrece, en orden, "Nuevo chat", "Buscar chats", "Historial de pedidos", la lista "Recientes" y el pie con `SesionIndicator`.
- El pie muestra inicial y nombre. Con sesión abre `AccountPage` (`/cuenta`); sin sesión abre `AuthModal` en login.
- `AccountPage` es de solo lectura: muestra nombre, correo completo, celular enmascarado y verificación local, además del documento del último checkout enmascarado. Los accesos "Mis pedidos", "Mis reclamos" y "Cerrar sesión" navegan/ejecutan sus capacidades existentes. Los datos editables fuera del canal no abren formularios.
- `SearchChatsPage` (`/buscar`) muestra el campo "Buscar conversaciones" enfocado, recientes con título, vista previa y fecha, resultados resaltados y estado sin resultados.
- Si se pulsa "Historial de pedidos" sin sesión, el login conserva como destino pendiente `/pedidos`. Default propuesto: `chatStore.pendingNavigation`, separado de `conversation.context.accionPendiente`, se consume después de autenticarse y se limpia al navegar.

### Conversación y acciones

- `OrderCard`, `OrderStatusCard`, `ShipmentTracking`, `ClaimList` y `ReturnHistoryTab` incorporan "Preguntar en el chat". Por defecto abre una conversación nueva y envía el mensaje contextual como primer mensaje de cliente; la respuesta sigue las herramientas de SPEC-17/18/20/22 y no puede estar prearmada.
- Un nuevo `FixedQuickActions` vive debajo del grid de Inicio y al final de la lista de mensajes en Conversación. Contiene "Ver ofertas", "Rastrear pedido" y "Ayuda con devolución". `QuickReplies` conserva las acciones contextuales de cada respuesta.
- Default de integración: cada acción fija es una acción directa REST registrada en historial, no un turno de texto al LLM. Tipos propuestos: `VER_OFERTAS`, `RASTREAR_PEDIDO` y `AYUDA_DEVOLUCION`; reutilizan `consultar_promociones`, `listar_pedidos`/`consultar_pedido`/`consultar_seguimiento` y `preparar_devolucion` respectivamente. Requieren sesión las dos últimas y retoman tras login.

## Backend y privacidad

- `GET /api/v1/sesion/perfil` conserva el proxy a `GET /auth/me` y agrega el estado de verificación local del celular y `ultimoDocumento: {tipo, numeroEnmascarado} | null`.
- El documento se lee del `summary.contacto` del checkout más reciente del `customer_id` actual; no se agrega persistencia ni se consulta un documento en Seguridad. El BFF enmascara antes de responder y nunca envía datos de cuenta al LLM.
- El acceso al perfil y al último documento respeta pertenencia autenticada. Si Seguridad no responde, `AccountPage` conserva disponible el cierre de sesión y permite reintentar la lectura.

## Cámara y checkout

- `AttachmentButton` se etiqueta "Agregar imagen" y abre `AttachmentSourceSheet` con "Galería" y "Tomar foto". La cámara usa el selector nativo con `capture="environment"`; no se solicita ni persiste un permiso propio de cámara.
- Ambos orígenes pasan por la misma validación de MIME, tamaño y límite de adjuntos, limpieza EXIF/ubicación y carga del backend. Fotos mayores de 5 MB se rechazan con el mensaje existente; no se comprimen.
- `BuyerDocumentSection` muestra la nota "El documento del comprobante puede ser distinto al de tu cuenta.". El documento se usa para el pedido actual y no modifica el perfil.
- El prototipo actualmente muestra un texto que sugiere reutilizar una foto como evidencia de devolución. Se mantiene la decisión explícita del brief: no reutilizarla; `SPEC-23 · Req. 10` y el contrato con Ventas siguen separados.

## Persistencia

No se crean tablas ni columnas. `checkout.summary.contacto` ya conserva `tipoDocumento` y `numeroDocumento`; `AccountPage` obtiene una proyección enmascarada desde el checkout más reciente. El estado local del celular ya existe en la persistencia propia de SPEC-04.

## Riesgos y decisiones por confirmar

- Confirmar los once puntos registrados en `proposal.md`, en especial el texto del documento "de tu cuenta", el destino de `Mis reclamos`, los tipos de acción directa y el estado de navegación sin conversación.
- La carga de una imagen tomada por cámara puede superar 5 MB; el default es rechazo con el mensaje actual.
- No modificar los escenarios ni requisitos de voz, uso de imágenes como evidencia, pestaña de reclamos ni pantallas completas no incluidas en el brief.

## Aplicación al archivar

El validador de merge estricto exige mantener el identificador del escenario existente `Buscar chats`; su cuerpo se redefine para abrir `SearchChatsPage`, y se añaden aparte los escenarios de búsqueda por texto, sin resultados e historial lateral.

Las deltas sustituyen los diseños base que todavía describen el campo "Buscar chats" dentro de `Sidebar`, `SesionIndicator` en la cabecera y el botón de adjuntos como "Adjuntar". Esas fuentes (`motor-conversacion/design.md`, `inicio-sesion/design.md` y `adjuntos-imagenes-chat/design.md`) permanecen intactas mientras el cambio está abierto, conforme a README §6; hay que incorporar sus nuevas responsabilidades al aplicar/archivar el cambio.