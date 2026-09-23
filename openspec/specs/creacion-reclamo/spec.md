# Creación de reclamo

> Origen: SPEC-19 · Grupo: Postventa · Requiere sesión: Sí · Depende de: [`inicio-sesion`](../inicio-sesion/spec.md) (SPEC-03), [`motor-conversacion`](../motor-conversacion/spec.md) (SPEC-05), [`consulta-estado-pedido`](../consulta-estado-pedido/spec.md) (SPEC-17), Ventas (F6)

## Purpose

Permitir al cliente reportar un problema con un pedido desde el chat, de forma guiada y con una confirmación explícita, y entregarle un código para hacer seguimiento.

## Contexto

Ventas y Postventa gestiona los reclamos según el Libro de Reclamaciones (Indecopi). Su `api-contract.md` (v1.3.0) define F6 completo, incluidos el registro, la consulta y el listado, y confirma el **plazo de respuesta de 15 días hábiles**.

Distingue:

- **Reclamo:** disconformidad con el producto o servicio.
- **Queja:** malestar con la atención.

El reclamo requiere un bloque `consumidor` con nombre completo, **documento**, correo y teléfono — el mismo dato que SPEC-12 ya captura en el checkout, así que se reutiliza del último pedido del cliente en lugar de pedirlo de nuevo.

✅ **Resuelto (23/09):** Ventas agregó `GET /api/v2/reclamos/{codigoSeguimiento}` y `GET /api/v2/reclamos?documento=&clienteId=&estado=` (acuerdo A10). Ya se puede detectar duplicados contra el listado real, y SPEC-20 puede consultar el estado sin limitaciones.

## Alcance

Incluye:
- Detección de la intención de reclamar ("me llegó dañado", "quiero hacer un reclamo").
- Recolección guiada: pedido, tipo (`RECLAMO` o `QUEJA`), motivo tipificado, descripción y pedido concreto del cliente (qué solución espera).
- Reutilización del documento del cliente capturado en su último pedido (SPEC-12), sin volver a pedirlo si ya existe.
- Formulario de revisión prellenado y editable, con confirmación explícita.
- Registro en Ventas con idempotencia y constancia en el chat.
- Aviso si ya existe un reclamo abierto para el mismo pedido y motivo, consultando el listado real de Ventas.

### Fuera de alcance

- Adjuntar fotos o evidencias al reclamo (si se necesita evidencia, corresponde a una devolución, SPEC-21).
- Solicitud formal de devolución o cambio (F3 de Ventas): es SPEC-21.
- Respuesta o gestión del reclamo: la hace el equipo de Ventas mediante `PATCH /reclamos/{id}/respuesta`.

## Requirements

### Requirement: Recolección guiada
El sistema DEBE (SHALL) reunir los datos del reclamo conversando, sin enviarlo hasta la confirmación, y presentar un formulario de revisión prellenado.

Motivos: alineados a los que usa Ventas en su ejemplo (`INCUMPLIMIENTO_PLAZO_ENTREGA`) y ampliados para cubrir los casos del canal: `PRODUCTO_DEFECTUOSO`, `PRODUCTO_EQUIVOCADO`, `PEDIDO_INCOMPLETO`, `INCUMPLIMIENTO_PLAZO_ENTREGA`, `NO_RECIBIDO`, `COBRO_INCORRECTO`, `ATENCION`, `OTRO`.

*Trazabilidad: SPEC-19 · Requisito 1.*

#### Scenario: Reclamo expresado en lenguaje natural
- **DADO** un cliente con el pedido PED-…891 `ENTREGADO`
- **CUANDO** escribe "las zapatillas que me llegaron tienen la suela despegada"
- **ENTONCES** el LLM invoca `preparar_reclamo {pedidoRef: "PED-…891", tipo: RECLAMO, motivo: PRODUCTO_DEFECTUOSO, descripcion: "..."}`, y el chat muestra el formulario prellenado con los campos editables, "¿Qué solución esperas?" y "Enviar reclamo"

#### Scenario: Falta el pedido
- **DADO** un cliente con varios pedidos
- **CUANDO** escribe "quiero reclamar"
- **ENTONCES** se muestra `OrderList` para elegir el pedido (el reclamo siempre se asocia a un pedido del cliente)

#### Scenario: Descripción insuficiente
- **DADO** una descripción de menos de 20 caracteres
- **CUANDO** se intenta enviar
- **ENTONCES** el formulario pide "Cuéntanos un poco más (mínimo 20 caracteres)"; el máximo es de 1000

### Requirement: Confirmación explícita y registro
El sistema DEBE (SHALL) registrar el reclamo en Ventas solo cuando el cliente pulsa "Enviar reclamo", con una `Idempotency-Key` (cabecera `X-Idempotency-Key`), y mostrar la constancia.

Payload real `POST {VEN}/api/v2/reclamos`:
```json
{
  "pedidoId": "PED-2026-00891",
  "tipo": "RECLAMO",
  "canal": "CHATBOT",
  "motivo": "PRODUCTO_DEFECTUOSO",
  "detalle": "La suela de la zapatilla derecha se despegó al primer uso.",
  "consumidor": {
    "nombreCompleto": "Juan Pérez",
    "documento": "72458912",
    "email": "juan.perez@example.com",
    "telefono": "+51999888777"
  }
}
```

*Trazabilidad: SPEC-19 · Requisito 2.*

#### Scenario: Reclamo registrado
- **DADO** un formulario confirmado, con el documento tomado del último pedido del cliente
- **CUANDO** Ventas responde `201 {reclamoId, codigoSeguimiento, estado: REGISTRADO, motivo, plazoDiasHabiles: 15, fechaLimiteSLA, respuestaVisibleCliente: null}`
- **ENTONCES** se guarda `reclamo_ref` y se muestra la constancia con el `codigoSeguimiento`, la fecha, el pedido, el motivo, "Recibirás respuesta antes del {fechaLimiteSLA}" y el texto "Guarda este código para consultar tu reclamo"

#### Scenario: Cliente sin documento registrado
- **DADO** un cliente cuyo único pedido previo no tiene documento guardado (caso raro, de datos migrados) o que nunca compró antes
- **CUANDO** intenta reclamar
- **ENTONCES** el formulario pide `tipoDocumento`/`numeroDocumento` en ese momento, con el mismo `DocumentoValidator` de SPEC-12

#### Scenario: Doble envío
- **DADO** dos envíos con la misma `Idempotency-Key`
- **CUANDO** se procesan
- **ENTONCES** se registra un solo reclamo y ambos reciben la misma constancia

#### Scenario: El cliente cancela
- **DADO** el formulario de reclamo abierto
- **CUANDO** el cliente pulsa "Cancelar" o escribe "mejor no"
- **ENTONCES** no se registra nada y el borrador se descarta

### Requirement: Reclamos duplicados
El sistema DEBE (SHALL) avisar si ya existe un reclamo abierto (no `ATENDIDO` ni `DERIVADO`) para el mismo pedido y motivo, consultando `GET /api/v2/reclamos?clienteId=&estado=` antes de mostrar el formulario de uno nuevo.

*Trazabilidad: SPEC-19 · Requisito 3.*

#### Scenario: Reclamo abierto existente
- **DADO** un reclamo `REGISTRADO` o `EN_PROCESO` para PED-…891 con motivo `PRODUCTO_DEFECTUOSO`
- **CUANDO** el cliente intenta registrar otro igual
- **ENTONCES** se informa el `codigoSeguimiento` existente y su estado, con "Ver estado" (SPEC-20), y no se crea uno nuevo sin que el cliente lo confirme explícitamente ("Registrar uno nuevo de todas formas")

#### Scenario: Reclamo previo ya atendido
- **DADO** que el único reclamo previo sobre ese pedido y motivo está `ATENDIDO` o `DERIVADO`
- **CUANDO** el cliente registra uno nuevo
- **ENTONCES** se permite sin aviso (no es un duplicado, es un caso ya cerrado)

### Requirement: Tolerancia a fallos
El sistema DEBE (SHALL) informar con claridad si el reclamo no pudo registrarse, sin simular un registro.

*Trazabilidad: SPEC-19 · Requisito 4.*

#### Scenario: Ventas no disponible
- **DADO** que Ventas no responde al registrar
- **CUANDO** se envía
- **ENTONCES** se muestra "No pudimos registrar tu reclamo en este momento. Guardamos tu borrador por 24 horas" con "Reintentar", y el borrador queda en `conversacion.contexto`

#### Scenario: Pedido no válido para reclamar
- **DADO** que Ventas rechaza con `400` (por ejemplo, datos incompletos)
- **CUANDO** se envía
- **ENTONCES** se muestra el mensaje de forma comprensible, mapeando `codigo` de Ventas a un `code` interno

## Requisitos no funcionales

- **Confirmación:** ningún reclamo se registra solo por la decisión del LLM (SPEC-05 Req. 6).
- **Privacidad:** la descripción del cliente se envía tal cual a Ventas, y en los logs se registra truncada a 50 caracteres. El documento reutilizado del checkout nunca se muestra completo en el chat.
- **Normativa:** el plazo de respuesta es de **15 días hábiles**, confirmado por Ventas; se muestra la `fechaLimiteSLA` que ella misma calcula, sin que el chatbot la recalcule.
- **Rendimiento:** el registro tarda p95 ≤ 1 s; la consulta de duplicados antes de mostrar el formulario, p95 ≤ 500 ms.

## Criterio de completitud

La capacidad se considera correctamente implementada cuando:
- Todos los requisitos están implementados.
- Todos los escenarios definidos se cumplen.
- Los requisitos no funcionales aplicables se cumplen.
- No se han incorporado funcionalidades fuera del alcance.
