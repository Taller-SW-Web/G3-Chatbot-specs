# ADR-0013: Solo referencias locales a agregados de otros módulos

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; la parte de evidencias se simplificó con el acuerdo A13, resuelto el 2026-09-23)

## Contexto

- El canal no es dueño de usuarios, productos, pedidos, reclamos, devoluciones ni despachos (`alcance.md` §1); la matriz del curso prohíbe leer bases ajenas (README §1.3.6).
- Aun así necesita recordar qué creó (pedido, reclamo, devolución) para controlar la pertenencia, detectar duplicados, reintentar operaciones y mostrar confirmaciones.
- Ventas hostea las evidencias de devolución y devuelve su URL (A13).

## Decisión

- La base PostgreSQL del chatbot guarda **solo sus propios agregados**: conversaciones, mensajes, carrito, checkout, intentos de pago simulados, verificación local del celular, notificaciones y outbox.
- De otros módulos guarda **identificadores (referencias)**, no copias de sus datos maestros:
  - `pedido_ref` (`pedido_id` de Ventas y un `estado_local` propio de la integración: `PAGO_PENDIENTE_NOTIFICAR`, `ANULACION_SOLICITADA`…);
  - `reclamo_ref` y `devolucion_ref`, con el código visible y la clave de idempotencia;
  - `producto_id` y `sku` en `item_carrito`;
  - `cliente_id` = `sub` del token;
  - `evidencia.url` tal como la devuelve Ventas (sin bucket propio).
- Los **snapshots** mínimos se permiten solo para mostrar información o reintentar: `checkout.resumen` (enviado a Ventas), `item_carrito` (nombre, variante, imagen) y `carrito.envio_snapshot`.
- El estado vigente siempre se consulta al módulo dueño; `devolucion_ref` sirve de respaldo solo si Ventas no responde (SPEC-22).

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Replicar pedidos, reclamos o productos en la base local (*alternativa estándar, no documentada*) | Duplicaría datos cuyo dueño es otro módulo y obligaría a sincronizarlos sin eventos ([ADR-0010](ADR-0010-integracion-sincrona-por-api-sin-eventos.md)) |
| Almacenamiento propio (bucket) para las evidencias | Innecesario desde A13: Ventas hostea el archivo |

## Consecuencias

**Positivas**
- No hay datos desincronizados: el cliente ve el estado real, incluidas las solicitudes creadas en otros canales (SPEC-22).
- Menos datos personales bajo responsabilidad del canal (`privacidad.md` §2).

**Negativas y riesgos aceptados**
- Casi toda consulta depende de la disponibilidad del módulo dueño.
- Los snapshots (sobre todo `checkout.resumen`, con documento y dirección) no tienen plazo de retención definido (`conversacion/README.md`, pregunta 10).
- `carrito.direccion_id` se describe como referencia a una dirección de Seguridad, aunque la dirección ahora se captura en campos libres ([ADR-0016](ADR-0016-direccion-en-checkoutpage-fuera-del-chat.md)); conviene revisar ese campo al refinar el modelo de datos.

## Referencias

- `docs/modelo-datos.md` introducción (líneas 5-8) y tablas `pedido_ref`, `reclamo_ref`, `devolucion_ref`, `evidencia`, `carrito`
- `README.md` §1.3, principio 6 (línea 123)
- `docs/contratos-integracion.md` §6, acuerdo A13 (línea 267)
- `openspec/specs/consulta-devolucion-reembolso/design.md` (`DevolucionConsultaService`)
- `docs/conversacion/privacidad.md` §2
