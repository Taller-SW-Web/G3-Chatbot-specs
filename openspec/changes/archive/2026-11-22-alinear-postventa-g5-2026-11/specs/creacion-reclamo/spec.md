## MODIFIED Requirements

### Requirement: Recolección guiada
El sistema DEBE (SHALL) reunir los datos del reclamo conversando, sin enviarlo hasta la confirmación, y presentar un formulario de revisión prellenado.

Motivos: el formulario, la herramienta `preparar_reclamo` y el backend DEBEN (SHALL) aceptar únicamente los cinco motivos del contrato de G5: `INCUMPLIMIENTO_PLAZO_ENTREGA`, `PRODUCTO_DEFECTUOSO_O_INCORRECTO`, `COBRO_INDEBIDO_O_NO_RECONOCIDO`, `ATENCION_INADECUADA` e `INCUMPLIMIENTO_GARANTIA`. G5 no expone `OTRO` ni alias: el cliente DEBE (SHALL) elegir el motivo más cercano y explicar el caso concreto en `detalle` (mínimo 20 y máximo 1000 caracteres).

*Trazabilidad: SPEC-19 · Requisito 1. Alineado con el contrato real de G5 (2026-11).*

#### Scenario: Reclamo expresado en lenguaje natural
- **DADO** un cliente con el pedido PED-…891 `ENTREGADO`
- **CUANDO** escribe "las zapatillas que me llegaron tienen la suela despegada"
- **ENTONCES** el LLM invoca `preparar_reclamo {pedidoRef: "PED-…891", tipo: RECLAMO, motivo: PRODUCTO_DEFECTUOSO_O_INCORRECTO, descripcion: "..."}`, y el chat muestra el formulario prellenado con los campos editables, "¿Qué solución esperas?" y "Enviar reclamo"

#### Scenario: Falta el pedido
- **DADO** un cliente con varios pedidos
- **CUANDO** escribe "quiero reclamar"
- **ENTONCES** se muestra `OrderList` para elegir el pedido (el reclamo siempre se asocia a un pedido del cliente)

#### Scenario: Descripción insuficiente
- **DADO** una descripción de menos de 20 caracteres
- **CUANDO** se intenta enviar
- **ENTONCES** el formulario pide "Cuéntanos un poco más (mínimo 20 caracteres)"; el máximo es de 1000

#### Scenario: Caso que no encaja exactamente en un motivo
- **DADO** un caso que no corresponde exactamente a ninguno de los cinco motivos, por ejemplo "el producto dejó de funcionar y la tienda no aplica la garantía"
- **CUANDO** el cliente lo describe en el chat
- **ENTONCES** el formulario propone el motivo más cercano de la lista (en el ejemplo, `INCUMPLIMIENTO_GARANTIA`), lo deja editable y exige que el detalle explique el caso concreto; no se ofrece ni se envía `OTRO`

#### Scenario: Motivo fuera de la lista del contrato
- **DADO** un envío con un `motivo` que no está entre los cinco de G5, por ejemplo `OTRO` o un valor de una versión anterior como `PRODUCTO_DEFECTUOSO`
- **CUANDO** llega a `POST /api/v1/reclamos`
- **ENTONCES** responde `400 VALIDACION` con `errores[{campo: "motivo", mensaje}]`, no se llama a Ventas, no se crea el reclamo y el formulario solo ofrece los cinco motivos del contrato

### Requirement: Confirmación explícita y registro
El sistema DEBE (SHALL) registrar el reclamo en Ventas solo cuando el cliente pulsa "Enviar reclamo", con una `Idempotency-Key` (cabecera `Idempotency-Key`, igual que el resto de operaciones que crean algo), y mostrar la constancia.

Payload real `POST {VEN}/api/v2/reclamos`:
```json
{
  "pedidoId": "PED-2026-00891",
  "tipo": "RECLAMO",
  "canal": "CHATBOT",
  "motivo": "PRODUCTO_DEFECTUOSO_O_INCORRECTO",
  "detalle": "La suela de la zapatilla derecha se despegó al primer uso.",
  "consumidor": {
    "nombreCompleto": "Juan Pérez",
    "documento": "72458912",
    "email": "juan.perez@example.com",
    "telefono": "+51999888777"
  }
}
```

El cuerpo de `POST /api/v1/reclamos` es ese payload más `forzar` (booleano, por defecto `false`); `forzar` es una decisión del chatbot y no se reenvía a Ventas. El `motivo` enviado por el frontend DEBE (SHALL) ser uno de los cinco de G5; el backend NO DEBE (SHALL NOT) traducir alias ni aceptar valores de versiones anteriores.

*Trazabilidad: SPEC-19 · Requisito 2.*

#### Scenario: Reclamo registrado
- **DADO** un formulario confirmado, con el documento tomado del último pedido del cliente
- **CUANDO** Ventas responde `201 {reclamoId, codigoSeguimiento, estado: REGISTRADO, motivo, plazoDiasHabiles: 15, fechaLimiteSLA, respuestaVisibleCliente: null}`
- **ENTONCES** se guarda `claim_ref` y se muestra la constancia con el `codigoSeguimiento`, la fecha, el pedido, el motivo, "Recibirás respuesta antes del {fechaLimiteSLA}" y el texto "Guarda este código para consultar tu reclamo"

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
El sistema DEBE (SHALL) detectar, antes de registrar, si ya existe un reclamo abierto (no `ATENDIDO` ni `DERIVADO`) para el mismo pedido y motivo, consultando `GET /api/v1/reclamos` (proxy a `GET /api/v2/reclamos/me?estado=` con el token del cliente). La detección DEBE (SHALL) repetirse en el `POST /api/v1/reclamos` como comprobación autoritativa, no solo en la pantalla previa. Si existe un duplicado y el cliente no envía `forzar: true`, el backend responde `409 RECLAMO_DUPLICADO` con el `codigoSeguimiento` y el estado del reclamo existente; con `forzar: true` registra uno nuevo. La `Idempotency-Key` sigue aplicando en ambos casos.

*Trazabilidad: SPEC-19 · Requisito 3.*

#### Scenario: Reclamo abierto existente
- **DADO** un reclamo `REGISTRADO` o `EN_PROCESO` para PED-…891 con motivo `PRODUCTO_DEFECTUOSO_O_INCORRECTO`
- **CUANDO** el cliente intenta registrar otro igual sin `forzar`
- **ENTONCES** se informa el `codigoSeguimiento` existente y su estado, con "Ver estado" (SPEC-20), y no se crea uno nuevo; si confirma "Registrar uno nuevo de todas formas", el formulario reenvía con `forzar: true`

#### Scenario: Reclamo previo ya atendido
- **DADO** que el único reclamo previo sobre ese pedido y motivo está `ATENDIDO` o `DERIVADO`
- **CUANDO** el cliente registra uno nuevo
- **ENTONCES** se permite sin aviso (no es un duplicado, es un caso ya cerrado)

#### Scenario: Registro forzado
- **DADO** un reclamo abierto para el mismo pedido y motivo y una confirmación explícita del cliente
- **CUANDO** se envía `POST /api/v1/reclamos` con `forzar: true`
- **ENTONCES** se registra el nuevo reclamo, se guarda su `claim_ref` y se muestra una constancia nueva con su propio `codigoSeguimiento`

#### Scenario: Doble envío con `forzar`
- **DADO** dos envíos con la misma `Idempotency-Key` y `forzar: true`
- **CUANDO** se procesan
- **ENTONCES** se registra un solo reclamo y ambos reciben la misma constancia

#### Scenario: No se puede consultar el listado de duplicados
- **DADO** que `GET /api/v1/reclamos` falla o excede el tiempo de espera al comprobar duplicados
- **CUANDO** el cliente envía un reclamo distinto
- **ENTONCES** el registro continúa (decisión de falibilidad: el reclamo es la operación principal), se registra un aviso en los logs y el cliente no ve un error de duplicados; si el equipo prefiere bloquear, se cambia a `503 SERVICIO_NO_DISPONIBLE` en una decisión posterior
