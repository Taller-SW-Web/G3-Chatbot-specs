# EP-04 · Carrito y stock — Historias de usuario

> Specs: [SPEC-10](../../../openspec/specs/validacion-stock/spec.md), [SPEC-11](../../../openspec/specs/gestion-carrito/spec.md) · Área `CAR` · 8 historias · 36 puntos
>
> Los criterios de aceptación **remiten** a los escenarios de la spec, que son la única fuente de verdad del comportamiento. Aquí solo se resume cada uno en una línea.

---

## HU-CAR-01 · Agregar solo cantidades disponibles

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Must | 5 | Hito 3 | `SPEC-10 · Req. 1` | RN-CAR-01, RN-CAR-02 | Productos 🟡 (A5: `/inventario/disponibilidad`) |

**Como** cliente, **quiero** que el chat me avise si pido más unidades de las que hay y me proponga alternativas, **para** no llegar al pago con un carrito imposible de cumplir.

**Criterios de aceptación**
- `SPEC-10 · Req. 1 · Scenario: Stock suficiente` — con stock suficiente la adición se acepta.
- `SPEC-10 · Req. 1 · Scenario: Stock parcial` — se responde `409 STOCK_INSUFICIENTE` y se ofrece agregar solo lo disponible.
- `SPEC-10 · Req. 1 · Scenario: SKU agotado` — se ofrecen otras variantes o hasta 3 productos similares con stock.

**Prioridad:** Must: la validación de stock es parte del lineamiento "agregar productos al carrito".

---

## HU-CAR-02 · Revalidar el stock de todo el carrito antes de pagar

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Must | 5 | Hito 3 | `SPEC-10 · Req. 2` | RN-CAR-03, RN-CAR-06 | Productos 🟡 (A5); Ventas ✅ (`409` al crear el pedido) |

**Como** cliente, **quiero** enterarme antes de pagar si algo de mi carrito se agotó mientras elegía, **para** ajustar mi compra sin que se me cobre algo que no se puede entregar.

**Criterios de aceptación**
- `SPEC-10 · Req. 2 · Scenario: El stock cambió desde que se agregó` — se responde `409 CARRITO_DESACTUALIZADO` con detalle por línea y las acciones "Ajustar a N" y "Quitar del carrito".
- `SPEC-10 · Req. 2 · Scenario: Todas las líneas disponibles` — la validación pasa y el checkout continúa.
- `SPEC-10 · Req. 2 · Scenario: Ventas rechaza por stock al crear el pedido` — se vuelve al carrito con la revalidación completa y sin cobrar.

**Prioridad:** Must: evita cobrar pedidos que no se pueden cumplir.

**Notas:** la validación masiva se construye en Hito 3 (README), pero sus escenarios 2 y 3 solo se pueden probar de punta a punta con el checkout de Hito 4 (HU-CHK-12, HU-PED-01). RNF: hasta 20 SKUs en una sola llamada con p95 ≤ 500 ms.

---

## HU-CAR-03 · Nunca agregar sin confirmar el stock

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Must | 2 | Hito 3 | `SPEC-10 · Req. 3` | RN-CAR-04 | Productos 🟡 (A5) |

**Como** cliente, **quiero** que si el inventario no responde el chat me lo diga en lugar de agregar a ciegas, **para** no descubrir en el pago que el producto no estaba disponible.

**Criterios de aceptación**
- `SPEC-10 · Req. 3 · Scenario: Inventario no disponible al agregar` — tras 3 s sin respuesta, no se agrega, se responde `503` y se ofrece "Reintentar".
- `SPEC-10 · Req. 3 · Scenario: Disponibilidad no disponible solo para mostrar` — las tarjetas se muestran sin badge y la validación se hace al agregar.

**Prioridad:** Must, por el principio "nunca se asume disponibilidad".

---

## HU-CAR-04 · Preguntar por la disponibilidad de una talla

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Should | 3 | Hito 3 | `SPEC-10 · Req. 4` | RN-CAR-05 | Productos 🟡 (A5) |

**Como** cliente, **quiero** preguntar "¿tienen las Ultraboost en 40?" y obtener una respuesta directa, **para** decidir sin abrir el detalle del producto.

**Criterios de aceptación**
- `SPEC-10 · Req. 4 · Scenario: Consulta de talla` — se responde si hay disponibilidad (o "Quedan pocas unidades" si son ≤ 5) con el botón "Agregar".
- `SPEC-10 · Req. 4 · Scenario: Consulta de una variante inexistente` — se informan las tallas que maneja el producto.

**Prioridad:** Should: mejora la conversación; la disponibilidad ya se ve en la tarjeta y en el detalle.

---

## HU-CAR-05 · Agregar productos al carrito conversando

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Must | 5 | Hito 3 | `SPEC-11 · Req. 1` | RN-CAR-07, RN-CAR-08, RN-CAR-09 | Productos 🟡 (A5, vía HU-CAR-01) |

**Como** cliente, **quiero** decir "agrega las primeras en talla 41" y recibir un resumen de mi carrito, **para** armar mi compra sin salir de la conversación.

**Criterios de aceptación**
- `SPEC-11 · Req. 1 · Scenario: Agregar por conversación` — se resuelve el SKU, se valida el stock, se crea la línea y se responde con el resumen y los botones "Ver carrito", "Seguir comprando" y "Pagar".
- `SPEC-11 · Req. 1 · Scenario: Agregar un SKU ya existente` — la línea suma la cantidad y no se duplica.
- `SPEC-11 · Req. 1 · Scenario: Límite por línea` — superar 10 unidades responde `422 LIMITE_CANTIDAD` y ofrece agregar solo lo permitido.
- `SPEC-11 · Req. 1 · Scenario: Límite de líneas` — con 20 líneas se rechaza un SKU nuevo.

**Prioridad:** Must: es literalmente el lineamiento "agregar productos al carrito mediante conversación".

**Notas:** incluye la persistencia del carrito (tablas `carrito` e `item_carrito`), los endpoints REST y los hooks del frontend.

---

## HU-CAR-06 · Cambiar cantidades y quitar productos

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Must | 5 | Hito 3 | `SPEC-11 · Req. 2` | RN-CAR-10, RN-CAR-11 | — |

**Como** cliente, **quiero** cambiar cantidades, quitar productos o vaciar el carrito por texto o con botones, **para** ajustar mi compra con facilidad y poder deshacer un error.

**Criterios de aceptación**
- `SPEC-11 · Req. 2 · Scenario: Cambiar la cantidad por texto` — "pon 3 de las medias" resuelve la línea por nombre, valida el stock y fija la cantidad.
- `SPEC-11 · Req. 2 · Scenario: Referencia ambigua dentro del carrito` — ante dos coincidencias se pregunta "¿Cuáles?" con las opciones.
- `SPEC-11 · Req. 2 · Scenario: Cantidad cero` — la línea se elimina y se puede deshacer durante 10 s.
- `SPEC-11 · Req. 2 · Scenario: Vaciar el carrito` — se exige confirmación y el carrito queda sin líneas, cupón ni envío.

**Prioridad:** Must: sin edición, el carrito no es usable.

---

## HU-CAR-07 · Ver mi carrito con totales actualizados

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Must | 8 | Hito 3 | `SPEC-11 · Req. 3` | RN-CAR-12, RN-CAR-13, RN-CAR-14 | Productos 🟡 (A5: `/precios`, `/promociones/evaluar`) |

**Como** cliente, **quiero** ver mi carrito con precios, descuentos y total recalculados cada vez, **para** saber exactamente cuánto voy a pagar y enterarme de cualquier cambio.

**Criterios de aceptación**
- `SPEC-11 · Req. 3 · Scenario: Resumen del carrito` — el bloque `CARRITO` muestra líneas, subtotal, descuentos, nota de envío y total.
- `SPEC-11 · Req. 3 · Scenario: El precio cambió` — el total usa el precio vigente y se avisa el cambio.
- `SPEC-11 · Req. 3 · Scenario: Producto desactivado en el carrito` — la línea queda "Ya no disponible", no suma y se excluye del checkout.
- `SPEC-11 · Req. 3 · Scenario: Carrito vacío` — se informa y se ofrecen "Ver ofertas" y "Buscar productos".
- `SPEC-11 · Req. 3 · Scenario: Evaluación de promociones no disponible` — se muestra el subtotal con la nota correspondiente y el checkout queda bloqueado.

**Prioridad:** Must: el total del carrito es la base del total a cobrar.

**Notas:** incluye `CartPage` (pantalla completa), `CartBadge` y `TotalesCalculator`. RNF: lectura con recálculo p95 ≤ 900 ms. En 8 puntos está en el límite; si crece, separar `CartPage` en su propia historia.

---

## HU-CAR-08 · Recuperar mi carrito en otra sesión o dispositivo

| Épica | Prioridad (MoSCoW) | Estimación | Hito | Specs/Requisitos | Reglas de negocio | Dependencias externas |
|---|---|---|---|---|---|---|
| EP-04 | Must | 3 | Hito 3 | `SPEC-11 · Req. 4` | RN-CAR-15, RN-CAR-16 | — |

**Como** cliente autenticado, **quiero** encontrar mi carrito al volver otro día o desde otro dispositivo, y empezar uno nuevo después de comprar, **para** no perder productos ni mezclar compras.

**Criterios de aceptación**
- `SPEC-11 · Req. 4 · Scenario: Volver otro día con sesión` — al iniciar sesión se recupera el carrito con los totales recalculados.
- `SPEC-11 · Req. 4 · Scenario: Carrito convertido` — tras el pago confirmado el carrito queda `CONVERTIDO` y el cliente empieza con uno vacío.

**Prioridad:** Must: el carrito persistente es parte del ciclo de compra.

**Notas:** el escenario "Carrito convertido" se prueba de punta a punta en Hito 4 (HU-PED-02). Incluye el job que marca `ABANDONADO` los carritos anónimos con más de 7 días de inactividad.

---

## Asignación del desglose (`design.md`) a historias

Tareas numeradas `T1…Tn` en el orden del "Desglose para issues" de cada `design.md`. Las tareas `[QA]` se replican como una sub-issue por historia de esa spec.

| Spec | Tarea → Historia |
|---|---|
| SPEC-10 | T1 `[INT]` consulta masiva de disponibilidad (A5) → HU-CAR-01 · T2 `[BE]` InventarioClient y StockValidator → HU-CAR-01 (relacionadas: HU-CAR-02, HU-CAR-03) · T3 `[BE]` SimilaresService y `consultar_disponibilidad` → HU-CAR-04 (relacionada: HU-CAR-01) · T4 `[FE]` StockConflictNotice y AvailabilityBadge → HU-CAR-01 · T5 `[QA]` → HU-CAR-01 a HU-CAR-04 |
| SPEC-11 | T1 `[BE]` modelos `carrito` e `item_carrito` → HU-CAR-05 · T2 `[BE]` CarritoService → HU-CAR-05 · T3 `[BE]` TotalesCalculator → HU-CAR-07 · T4 `[BE]` endpoints REST → HU-CAR-05 · T5 `[BE]` herramientas y ResolverLineaCarrito → HU-CAR-06 · T6 `[BE]` job de limpieza → HU-CAR-08 · T7 `[FE]` CartPage y CartBadge → HU-CAR-07 · T8 `[FE]` CartBlock, UndoToast, ConfirmDialog → HU-CAR-06 · T9 `[FE]` hooks `useCart`/`useCartMutations` → HU-CAR-05 · T10 `[QA]` → HU-CAR-05 a HU-CAR-08 |
