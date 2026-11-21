# Alinear las specs con el prototipo

## Why

El prototipo web ya contiene seis elementos de navegación e interacción que no están descritos de forma completa en las specs vigentes. El equipo decidió conservarlos; este cambio registra su comportamiento para que el prototipo y la fuente de verdad funcional no diverjan.

## What Changes

- Añadir `AccountPage` de solo lectura en SPEC-03 y permitir iniciar desde allí la verificación local del celular (SPEC-04).
- Añadir el botón "Preguntar en el chat" para pedidos, seguimientos, reclamos y solicitudes de devolución o cambio.
- Convertir "Buscar chats" en una pantalla propia, añadir "Historial de pedidos" a la barra lateral y documentar ambas rutas.
- Añadir las tres acciones rápidas fijas en Inicio y Conversación.
- Permitir elegir Galería o Tomar foto al adjuntar imágenes, conservando los límites y controles de privacidad.
- Mostrar en el checkout la nota sobre el documento del comprobante.
- Actualizar los diseños y documentos transversales afectados, sin modificar el comportamiento de voz ni reutilizar imágenes del chat como evidencia.

## Capabilities

- `inicio-sesion`: ADDED requisito 7, pantalla "Mi cuenta".
- `validacion-celular`: MODIFIED requisito 3, entrada a la verificación desde `AccountPage`.
- `motor-conversacion`: MODIFIED requisitos 1 y 2; ADDED requisitos 13 y 14.
- `adjuntos-imagenes-chat`: MODIFIED requisito 1 para cámara y selector de origen.
- `direccion-cotizacion-envio`: MODIFIED requisito 1 para la nota del documento.
- Diseños afectados: `consulta-estado-pedido`, `seguimiento-despacho`, `consulta-reclamo` y `consulta-devolucion-reembolso`.

## Questions to Confirm

Decisiones confirmadas con el equipo:

1. **Ubicación de "Mi cuenta":** requisito 7 de SPEC-03; no se crea una capacidad nueva y se mantienen 23 specs.
2. **Origen del documento en "Mi cuenta":** primero consultar el perfil de Seguridad (si tiene documento, aunque sea enmascarado, se muestra eso).
3. **Visibilidad del correo:** se muestra completo en `AccountPage`; el enmascaramiento sigue aplicando a mensajes del chat.
4. **Enlace al perfil externo:** los cuatro datos editables fuera del canal son informativos; solo enlazan al perfil externo si existe una URL configurada.
5. **Destino de "Mis reclamos":** la lista de SPEC-20. Si se aprueba una pestaña "Reclamos" en el historial, se ajustará el destino.
6. **"Preguntar en el chat":** siempre crea una conversación nueva, con la referencia del pedido, reclamo o solicitud de devolución o cambio ya incluida en el primer mensaje del cliente.
7. **Acciones rápidas fijas:** son acciones directas de la UI, registradas en el historial; no se envían como texto al LLM aunque el prototipo visual las presente como acciones del cliente.
8. **Acciones rápidas principales:** se consideran las tres acciones fijas. Las sugerencias contextuales que devuelve una respuesta siguen siendo `QuickReplies` separados.
9. **Retoma de navegación sin conversación:** se guarda `pendingNavigation = /pedidos` en estado transitorio de aplicación, fuera de `conversation.context.accionPendiente`, y se limpia tras el login y la navegación.
10. **Fotos mayores de 5 MB:** se rechazan con el mensaje de tamaño existente; no se comprimen en el cliente.
11. **Nombre del botón de adjuntar:** "Agregar imagen", como en el prototipo.

## Out of Scope

- No se añade código de aplicación ni una nueva spec.
- Voz permanece fuera de alcance; el botón "Voz" del prototipo se retirará.
- Las imágenes del chat no se usan como evidencia de devolución ni de reclamo (SPEC-23 · Req. 10).
- No se permite editar el perfil desde el chatbot.
- No se decide la pestaña "Reclamos" del historial ni se crean pantallas completas de seguimiento, reclamo o devolución.
- No se añade rastreo de pedidos por descripción ni se define el formato de códigos.

## Acceptance Criteria

- Las seis decisiones quedan reflejadas en las specs delta y en sus líneas de trazabilidad.
- `npx @fission-ai/openspec validate --specs --strict` pasa.
- README §2 y documentos transversales reflejan navegación, microcopy, contratos y privacidad actuales.
- Se recalculan requisitos, escenarios, historias, puntos y reglas de negocio.
- No quedan contradicciones sobre la búsqueda como pantalla, la ubicación de `SesionIndicator`, el menú "Mi cuenta", voz fuera de alcance o imágenes usadas como evidencia.