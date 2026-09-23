# Diseño: Checkout y simulación de pago con tarjeta

> Origen: SPEC-14 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | Creación del pedido y notificación del pago: ver SPEC-15 | 🟡 A8 |
| Ventas | Anulación por pago no completado: ver SPEC-15 | 🟡 A9 |
| Seguridad | `POST /auth/introspeccion` (scope `tokens:introspeccion` **concedido**; credenciales reales desde Hito 4) | ✅ A3 |
| Productos, Despacho | Revalidación: disponibilidad, precios, evaluación, cupón y cotización | 🟡 A5 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `CheckoutPage` (pantalla completa) | Líneas, importes, `AddressSection` (SPEC-12), "Editar carrito" y "Confirmar y pagar". |
| `CheckoutDiffNotice` | Resalta los cambios de total cuando llega un `409`. |
| `PaymentForm` (sección "Método de pago" de `CheckoutPage`, solo tarjeta) | Campos de tarjeta con máscara, detección de marca, Luhn, vencimiento, CVV, aviso de simulación, temporizador de 15 min e intentos restantes. |
| `PaymentProcessing` | Estado "Procesando…" que bloquea la interfaz. |
| Seguridad del formulario | Los datos viven solo en el estado local del componente, se limpian al desmontar y no se guardan en el store ni en `sessionStorage`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/checkout` | Guardas de precondición, revalidación completa, creación del checkout y del pedido (SPEC-15). |
| `GET /api/v1/checkout/{id}` | Estado del checkout. |
| `POST /api/v1/checkout/{id}/pago` | Validación, simulación, registro del intento y disparo de la notificación. |
| `CheckoutService` | Orquesta las precondiciones, la revalidación, la vigencia y los intentos. |
| `IntrospeccionClient` | Llama a `POST /auth/introspeccion` con el token de servicio de `modulo-chatbot`; timeout de 3 s, sin caché (la sesión se valida en el momento exacto del pago). |
| `CardValidator` | Luhn, BIN, vencimiento y CVV. |
| `PaymentSimulator` (interfaz `PaymentGateway`) | Tabla de tarjetas de prueba; reemplazable por una pasarela real a futuro. |
| Job `ExpirarCheckouts` | Cada minuto; encola las anulaciones. |
| Middleware de logging | Excluye el body de `/pago`. |
| Herramienta `iniciar_checkout` | Solo prepara el resumen; **nunca paga**. |

## Desglose para issues

- [ ] `[BE]` Modelos `checkout` e `intento_pago` con claves de idempotencia
- [ ] `[BE]` `CheckoutService`: guardas de precondición y revalidación completa
- [ ] `[BE]` `IntrospeccionClient` y el paso obligatorio de introspección antes del pago
- [ ] `[BE]` Endpoint `POST /checkout` (crea el checkout y llama a SPEC-15)
- [ ] `[BE]` `CardValidator` y `PaymentSimulator` con la tabla de tarjetas de prueba
- [ ] `[BE]` Endpoint `POST /checkout/{id}/pago` con límite de intentos
- [ ] `[BE]` Job de expiración y exclusión del body de pago en los logs
- [ ] `[BE]` Herramienta `iniciar_checkout`
- [ ] `[FE]` `CheckoutPage` (pantalla completa) y `CheckoutDiffNotice`
- [ ] `[FE]` `PaymentForm` con máscaras, validación, temporizador e intentos
- [ ] `[QA]` Pruebas de todos los escenarios; prueba de que no hay PAN en la BD ni en los logs (grep sobre los logs de la prueba); E2E del pago aprobado y del rechazado 3 veces
