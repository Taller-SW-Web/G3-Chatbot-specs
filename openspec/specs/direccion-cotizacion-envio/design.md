# Diseño: Dirección de entrega, documento del comprador y cotización de envío

> Origen: SPEC-12 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Seguridad | `GET /usuarios/{id}/direcciones` (para prellenar, token del titular) | ✅ |
| Seguridad | `POST /usuarios/{id}/direcciones` (guardado opcional) | ✅ |
| Despacho | `POST /api/v1/cotizaciones` con `Authorization: Bearer <service-token>`, scope `cotizaciones:calcular`, audience `api-despacho` | ✅ contrato real · 🟡 scope pendiente para `modulo-chatbot` |
| Productos | `POST /productos/datos-fisicos/consulta` (lo usa Despacho, no el chatbot) | 🟡 no consume el canal |
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
| `POST /api/v1/envio/cotizar {destinatario, direccion, distrito, referencia?}` | Reúne `destino` y `lineas` desde el carrito, consulta a Despacho y guarda el snapshot en el checkout. |
| `EnvioService` | Construye el payload real de Despacho a partir del carrito: `destino` + `lineas` con `sku` y `cantidad`; no calcula ni envía peso ni volumen. |
| `DespachoClient.cotizar()` | Timeout de 4 s; arma `POST /api/v1/cotizaciones` con los campos reales y normaliza los errores propios de Despacho. |
| `GuardarDireccionOpcional` | Se ejecuta junto a la creación del pedido (SPEC-15) solo si el checkbox estaba marcado; no bloquea el checkout si falla. |
| `DocumentoValidator` | Aplica las expresiones regulares confirmadas por Ventas por `tipoDocumento` (incluida la validación del prefijo del RUC); responde `code: DATO_INVALIDO` si no cumple, igual que Ventas. No persiste el documento fuera del snapshot del pedido. |

🧩 El contrato real de Despacho ya no acepta `pesoKg` ni `volumenM3`; el canal solo manda `destino` y, si hay productos, `lineas` con `sku` + `cantidad`. El cálculo físico queda en Despacho / Productos, no en la capa del chatbot.

### Mapeo de errores propios de Despacho

| Código de Despacho | Mapeo interno del chatbot |
|---|---|
| `DESP_ERROR_DESTINO_REQUERIDO` | `VALIDACION` / `destino requerido` |
| `DESP_ERROR_LINEAS_VACIAS` | `VALIDACION` / `lineas vacías` |
| `DESP_ERROR_CANTIDAD_INVALIDA` | `VALIDACION` / `cantidad inválida` |
| `DESP_ERROR_PRODUCTO_NO_ENCONTRADO` | `PRODUCTO_NO_DISPONIBLE` |
| `DESP_ERROR_DATOS_FISICOS_INCOMPLETOS` | `SERVICIO_NO_DISPONIBLE` o `VALIDACION` según el flujo |
| `DESP_ERROR_PRODUCTOS_NO_DISPONIBLE` | `SERVICIO_NO_DISPONIBLE` |
| `DESP_ERROR_LIMITE_COTIZACION` | `DEMASIADAS_SOLICITUDES` |

## Desglose para issues

- [ ] `[INT]` Cerrar A12 con Despacho y dejar el scope `cotizaciones:calcular` pendente para `modulo-chatbot`
- [ ] `[BE]` `DocumentoValidator` y el campo `BuyerDocumentSection` en el snapshot
- [ ] `[BE]` `EnvioService` y `DespachoClient` con el nuevo payload `destino + lineas` y el mapeo de errores
- [ ] `[BE]` Endpoint `envio/cotizar` con los nombres de campo alineados a Ventas
- [ ] `[BE]` `GuardarDireccionOpcional` integrado en la creación del pedido
- [ ] `[FE]` `BuyerDocumentSection` con prellenado del último documento usado
- [ ] `[FE]` `AddressSection` (campos libres + selector de distrito + checkbox de guardado)
- [ ] `[FE]` `ShippingQuote` embebido en `CheckoutPage`
- [ ] `[QA]` Pruebas de todos los escenarios (documento, cobertura, sin cobertura, timeout, recotización y guardado fallido no bloqueante)
