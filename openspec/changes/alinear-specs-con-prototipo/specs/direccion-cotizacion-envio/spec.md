## MODIFIED Requirements

### Requirement: Capturar el documento de identidad
El sistema DEBE (SHALL) pedir el tipo y número de documento del comprador dentro de `CheckoutPage`, ya que Ventas lo exige para crear el pedido y ningún otro flujo lo captura. 🧩 **Reglas confirmadas por Ventas (23/09/2026)** para su `DocumentoValidator`: el bloque `contacto` exige **siempre** `tipoDocumento` y `numeroDocumento` — nunca es opcional, se usa tanto para emitir el comprobante como para validar la entrega. El frontend valida con exactamente estas expresiones, para que nunca lleguen a Ventas datos que su propio validador vaya a rechazar:

| `tipoDocumento` | Regla | Expresión regular |
|---|---|---|
| `DNI` | Exactamente 8 dígitos numéricos | `^[0-9]{8}$` |
| `RUC` | Exactamente 11 dígitos numéricos, empezando por `10`, `15`, `17` o `20` | `^[0-9]{11}$` (más la validación del prefijo) |
| `CE` (Carné de Extranjería) | De 8 a 12 caracteres alfanuméricos | `^[a-zA-Z0-9]{8,12}$` |
| `PASAPORTE` | De 6 a 12 caracteres alfanuméricos | `^[a-zA-Z0-9]{6,12}$` |

Si el formato no corresponde al tipo elegido, Ventas rechaza con `400 Bad Request {codigo: DATO_INVALIDO}`. Esto reemplaza el rango genérico de "6 a 12 caracteres" para `CE` que se había asumido antes, y agrega `PASAPORTE` como cuarto tipo (no contemplado en el diseño anterior). La sección muestra bajo los campos la nota fija "El documento del comprobante puede ser distinto al de tu cuenta." El documento capturado se usa solo para ese pedido y no modifica el perfil del cliente.

*Trazabilidad: SPEC-12 · Requisito 1.*

#### Scenario: DNI válido
- **DADO** un cliente que completa `tipoDocumento: DNI` y `numeroDocumento: 72458912`
- **CUANDO** valida el formulario
- **ENTONCES** se acepta, porque cumple `^[0-9]{8}$`

#### Scenario: RUC con prefijo inválido
- **DADO** `tipoDocumento: RUC` y `numeroDocumento: 30458912345`
- **CUANDO** valida el formulario
- **ENTONCES** se rechaza en el cliente antes de enviarlo, porque el RUC no empieza por `10`, `15`, `17` o `20`, aunque tenga 11 dígitos

#### Scenario: CE fuera de rango
- **DADO** `tipoDocumento: CE` y `numeroDocumento: 1234567` (7 caracteres)
- **CUANDO** valida el formulario
- **ENTONCES** se rechaza, porque el CE exige de 8 a 12 caracteres, no de 6 a 12 como se pensaba antes

#### Scenario: Pasaporte válido
- **DADO** `tipoDocumento: PASAPORTE` y `numeroDocumento: A1234567`
- **CUANDO** valida el formulario
- **ENTONCES** se acepta, porque cumple `^[a-zA-Z0-9]{6,12}$`

#### Scenario: Documento inválido o vacío
- **DADO** un `numeroDocumento` vacío o con un formato que no corresponde al `tipoDocumento` elegido
- **CUANDO** el cliente intenta pagar
- **ENTONCES** se muestra el error junto al campo y no se habilita el pago (el frontend nunca deja llegar esto a Ventas, pero si ocurriera, Ventas también lo rechaza con `400 DATO_INVALIDO`)

#### Scenario: Cliente recurrente
- **DADO** un cliente que ya completó su documento en una compra anterior en este canal
- **CUANDO** vuelve a comprar
- **ENTONCES** el campo se prellena con el último documento usado (guardado en `checkout.summary` de su pedido anterior, nunca en el perfil de Seguridad, que no lo modela) y queda editable

#### Scenario: Nota sobre el documento del comprobante
- **DADO** la sección de documento de `CheckoutPage`
- **CUANDO** se muestra
- **ENTONCES** bajo los campos aparece la nota "El documento del comprobante puede ser distinto al de tu cuenta."
- **Y** el documento ingresado se usa solo para ese pedido (`checkout.summary.contacto`) y no modifica ningún dato del perfil del cliente