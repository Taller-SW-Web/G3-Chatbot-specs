# Diseño: Dirección de entrega, documento del comprador y cotización de envío

> Origen: SPEC-12 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Seguridad | `GET /usuarios/{id}/direcciones` (para prellenar, token del titular) | ✅ |
| Seguridad | `POST /usuarios/{id}/direcciones` (guardado opcional) | ✅ |
| Despacho | `POST /zonas/cotizar {distrito, codigoPostal?, pesoKg, volumenM3?}` | ✅ contrato publicado · 🟡 autenticación (A12) |
| Productos | Peso y volumen por SKU, o quién los agrega | 🟡 A6 (replanteado, ver `contratos-integracion.md`) |
| Ventas | Nombres de campo de `contacto` y `envio` usados por esta spec | ✅ `api-contract.md` §1.1 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `BuyerDocumentSection` (dentro de `CheckoutPage`) | Selector `tipoDocumento` (`DNI`, `RUC`, `CE`, `PASAPORTE`) y campo `numeroDocumento`; valida en vivo contra la expresión regular de cada tipo (Requisito 1) y muestra la regla esperada bajo el campo. |
| `AddressSection` (dentro de `CheckoutPage`) | Campos `destinatario`, `direccion` con selector de distrito embebido, `referencia` y el checkbox "Guardar esta dirección"; prellenado desde la dirección predeterminada si existe. |
| `ShippingQuote` | Costo, plazo y zona dentro de la misma pantalla; estado sin cobertura; reintentar. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `GET /api/v1/direcciones` | Proxy a Seguridad con el token del cliente, usado solo para prellenar. |
| `POST /api/v1/envio/cotizar {destinatario, direccion, distrito, referencia?}` | Calcula el peso y volumen, cotiza y guarda el snapshot en el checkout. |
| `EnvioService` | Cálculo de peso y volumen (SKU → Productos → valor por defecto), cotización y vigencia de 30 min. |
| `DespachoClient.cotizar()` | Timeout de 4 s; arma el payload con `modalidad: DELIVERY`. |
| `GuardarDireccionOpcional` | Se ejecuta junto a la creación del pedido (SPEC-15) solo si el checkbox estaba marcado; no bloquea el checkout si falla. |
| `DocumentoValidator` | Aplica las expresiones regulares confirmadas por Ventas por `tipoDocumento` (incluida la validación del prefijo del RUC); responde `code: DATO_INVALIDO` si no cumple, igual que Ventas. No persiste el documento fuera del snapshot del pedido. |

## Desglose para issues

- [ ] `[INT]` Cerrar A6 con Productos y Despacho (quién agrega el peso del carrito) y A12 con Despacho (autenticación del cotizador)
- [ ] `[BE]` `DocumentoValidator` y el campo `BuyerDocumentSection` en el snapshot
- [ ] `[BE]` `EnvioService`, `DespachoClient` y `pesos_por_categoria.yaml`
- [ ] `[BE]` Endpoint `envio/cotizar` con los nombres de campo alineados a Ventas
- [ ] `[BE]` `GuardarDireccionOpcional` integrado en la creación del pedido
- [ ] `[FE]` `BuyerDocumentSection` con prellenado del último documento usado
- [ ] `[FE]` `AddressSection` (campos libres + selector de distrito + checkbox de guardado)
- [ ] `[FE]` `ShippingQuote` embebido en `CheckoutPage`
- [ ] `[QA]` Pruebas de todos los escenarios (documento, cobertura, sin cobertura, timeout, recotización y guardado fallido no bloqueante)
