# Diseño: Gestión del carrito

> Origen: SPEC-11 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /precios?skus=&canal=CHATBOT` y, para una sola línea, `GET /precios/skus/{sku}?canal=CHATBOT` (sin `canal` Pricing devuelve el precio global, no el del canal) | 🟡 A5 · scope `precios:leer` pendiente |
| Productos | `POST /promociones/evaluar {channel_id, at, lines[], coupon_code, customer_ref}` → un único `discount_amount` para toda la cesta (sin desglose por línea), con `promotion_id` y `reason`; ante `429` se respeta `Retry-After` | 🟡 A5 · scope `promociones:evaluar` pendiente |
| Productos | Disponibilidad comercial y verificación por cantidad (SPEC-10) | 🟡 A5 |

🧩 El carrito ya no debe armar `canal`, `lineas` ni `cupon`; el payload del contrato real usa `channel_id`, `lines`, `quantity`, `coupon_code` y `customer_ref`. El nombre del descuento se resuelve por `promotion_id` contra `GET /promociones`; si no se encuentra o es nulo, la línea dice "Descuento" (comportamiento interino, no es contrato de Productos).

## Frontend

| Componente | Responsabilidad |
|---|---|
| `CartPage` (pantalla completa) | Vista principal del carrito, accedida desde `CartBadge`: líneas, controles +/−, quitar, `CartDiscountLines`, envío, total, avisos de cambios y el botón "Pagar" (navega a `CheckoutPage`, SPEC-14) y "Seguir comprando" (vuelve a `HomePage` o a la conversación). |
| `CartBlock` (bloque `CARRITO`, dentro del chat) | Versión resumida embebida en la conversación cuando el cliente pregunta "¿cuánto llevo?" o tras agregar un producto; incluye el enlace "Ver carrito completo" que navega a `CartPage`. |
| `CartBadge` | Ícono con contador de unidades, visible en la cabecera de `HomePage`, `ChatPage` y demás pantallas; abre `CartPage`. |
| `UndoToast` | Deshacer una eliminación durante 10 s. |
| `ConfirmDialog` | Confirmación para vaciar el carrito. |
| Hooks `useCart` y `useCartMutations` | TanStack Query con invalidación tras cada mutación; comparten estado entre `CartPage` y `CartBlock`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Endpoints `GET/DELETE /carrito`, `POST /carrito/items`, `PATCH/DELETE /carrito/items/{id}` | Operaciones del carrito desde la UI. |
| `CarritoService` | Agregar, cambiar cantidad, quitar, vaciar, obtener con recálculo y fusionar (SPEC-03). |
| `TotalesCalculator` | Precios vigentes, evaluación de promociones, cupón, envío y avisos de cambios. |
| `ResolverLineaCarrito` | Resuelve referencias por nombre u ordinal dentro del carrito. |
| Herramientas LLM `agregar_al_carrito`, `ver_carrito`, `cambiar_cantidad`, `quitar_del_carrito` y `vaciar_carrito` | Mismos handlers que los endpoints. |
| Tablas `cart` e `cart_item` | Ver `modelo-datos.md`. |
| Job de limpieza | Marca como `ABANDONED` los carritos anónimos con más de 7 días de inactividad. |

## Desglose para issues

- [ ] `[BE]` Modelos `cart` e `cart_item` con migraciones y restricciones (1..10, SKU único por carrito)
- [ ] `[BE]` `CarritoService` (agregar, cambiar, quitar, vaciar) con bloqueo optimista
- [ ] `[BE]` `TotalesCalculator` con precios, evaluación y avisos de cambios
- [ ] `[BE]` Endpoints REST del carrito
- [ ] `[BE]` Herramientas LLM del carrito y `ResolverLineaCarrito`
- [ ] `[BE]` Job de limpieza de carritos anónimos
- [ ] `[FE]` `CartPage` (pantalla completa) y `CartBadge` global
- [ ] `[FE]` `CartBlock` embebido en el chat con enlace a `CartPage`, `UndoToast` y `ConfirmDialog`
- [ ] `[FE]` Hooks `useCart` y `useCartMutations` con manejo de `409`, `422` y `503`
- [ ] `[QA]` Pruebas de todos los escenarios, más una prueba de concurrencia de dos mutaciones simultáneas
