# Diseño: Gestión del carrito

> Origen: SPEC-11 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Productos | `GET /precios?skus=&canal=CHATBOT` | 🟡 A5 |
| Productos | `POST /promociones/evaluar {canal: CHATBOT, lineas[], cupon?}` | 🟡 A5 |
| Productos | Disponibilidad (SPEC-10) | 🟡 A5 |

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
| Tablas `carrito` e `item_carrito` | Ver `modelo-datos.md`. |
| Job de limpieza | Marca como `ABANDONADO` los carritos anónimos con más de 7 días de inactividad. |

## Desglose para issues

- [ ] `[BE]` Modelos `carrito` e `item_carrito` con migraciones y restricciones (1..10, SKU único por carrito)
- [ ] `[BE]` `CarritoService` (agregar, cambiar, quitar, vaciar) con bloqueo optimista
- [ ] `[BE]` `TotalesCalculator` con precios, evaluación y avisos de cambios
- [ ] `[BE]` Endpoints REST del carrito
- [ ] `[BE]` Herramientas LLM del carrito y `ResolverLineaCarrito`
- [ ] `[BE]` Job de limpieza de carritos anónimos
- [ ] `[FE]` `CartPage` (pantalla completa) y `CartBadge` global
- [ ] `[FE]` `CartBlock` embebido en el chat con enlace a `CartPage`, `UndoToast` y `ConfirmDialog`
- [ ] `[FE]` Hooks `useCart` y `useCartMutations` con manejo de `409`, `422` y `503`
- [ ] `[QA]` Pruebas de todos los escenarios, más una prueba de concurrencia de dos mutaciones simultáneas
