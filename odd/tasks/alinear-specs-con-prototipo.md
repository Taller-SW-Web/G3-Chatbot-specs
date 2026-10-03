# Alinear specs con el prototipo — seis elementos UX

## Objetivo

Documentar en el flujo OpenSpec los seis elementos acordados del prototipo, sin editar las specs vigentes directamente ni añadir código de aplicación.

## Alcance

- Pantalla `AccountPage` de solo lectura y verificación local del celular desde la misma pantalla.
- Botón "Preguntar en el chat" en tarjetas de pedidos, seguimiento, reclamos y devoluciones/cambios.
- `SearchChatsPage` y acceso "Historial de pedidos" desde `Sidebar`.
- Acciones rápidas fijas en Inicio y Conversación.
- Adjuntar imágenes desde Galería o cámara con las mismas validaciones.
- Nota informativa del documento en checkout.

## Tareas

- [x] Crear `openspec/changes/alinear-specs-con-prototipo/` con propuesta, diseño, tareas y deltas de SPEC-03, 04, 05, 12 y 23.
- [x] Registrar las once preguntas abiertas y sus defaults en la propuesta.
- [x] Actualizar el inventario de pantallas, alcance, épicas e historias de usuario.
- [x] Actualizar la matriz de trazabilidad y cubrir los 112 requisitos.
- [x] Actualizar las reglas de negocio, intenciones, flujos, microcopy, privacidad, contratos de integración y modelo de datos.
- [x] Recalcular requisitos, escenarios, historias, puntos y reglas.
- [x] Ejecutar `npx @fission-ai/openspec validate --specs --strict` y validar el change id con `--strict`.
- [x] Revisar los documentos transversales y documentar las referencias de diseño base que se sustituyen al archivar.

## Totales recalculados

| Métrica | Base | Propuesta |
|---|---:|---:|
| Specs | 23 | 23 |
| Requisitos | 109 | 112 |
| Escenarios | 325 | 352 |
| Historias | 105 | 111 |
| Puntos | 419 | 438 |
| Reglas de negocio | 162 | 168 |

## Decisiones pendientes de confirmación

Ver `openspec/changes/alinear-specs-con-prototipo/proposal.md`, sección "Questions to Confirm". Entre ellas: fuente del documento de cuenta y texto de checkout, correo completo, destino de "Mis reclamos", acciones principales, tipos directos y retoma de `/pedidos` tras login.

## Límites

- No editar `openspec/specs/` hasta archivar las deltas.
- Los diseños base conservan descripciones antiguas mientras el change está abierto; su reemplazo queda para el paso de aplicación/archivo.
- Las modificaciones del perfil permanecen a cargo de Seguridad/Marketplace; este cambio no incluye pestaña "Reclamos", pantallas completas de postventa, rastreo por descripción ni cambios en el formato de códigos.
- No usar fotos del chat como evidencia y no añadir voz.
- No hacer commit ni push sin confirmación explícita.
