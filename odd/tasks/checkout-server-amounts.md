# Importes del checkout calculados por el servidor

## Objetivo

Que `POST /checkout` calcule el costo de envío y el descuento solo en el servidor, según el contrato de `docs/contratos-integracion.md` §2.8, antes de la demo del Hito 4 (2026-11-07).

## Problema

Estado verificado el 2026-11-06 en `origin/development` (backend `776c04b`):

- El envío está fijo en `12.50` (`DEFAULT_SHIPPING_COST`, `manage_checkout_use_case.py:24` y `:178`); no se consulta a Despacho ni se valida cobertura.
- El descuento se lee de `cart.totals_snapshot`; si la copia está desactualizada se aplica `0` sin avisar, en lugar de `409 CARRITO_DESACTUALIZADO`.
- El router usa un `CreateCheckoutRequest` propio (`extra="ignore"`) que descarta en silencio líneas e importes; el contrato pide `400 VALIDACION`. El DTO del contrato (`commerce_contracts_dto.py`, `extra="forbid"`) no se usa.
- El frontend envía líneas e importes y genera una `Idempotency-Key` nueva en cada intento.

## Alcance

- Backend: recotizar el envío con el puerto de Despacho dentro del checkout (`422 SIN_COBERTURA`, `503 MODULO_NO_DISPONIBLE` sin costo o plazo), eliminar `12.50`, `409 CARRITO_DESACTUALIZADO` con `summary` cuando la copia del carrito está desactualizada, y usar el DTO del contrato (`400 VALIDACION` ante campos no admitidos).
- Frontend: enviar solo `direccion` y `contacto`, `Idempotency-Key` estable por intento y mostrar el `summary` del `409`.

Fuera de alcance: renombrar `orderId` a `pedidoId`, `conversacionId`, `guardarDireccion`, precios en vivo de Productos y validación de stock.

## Restricciones

- Backend y frontend se promueven juntos: con el DTO estricto, el frontend actual recibiría `400`.
- En la demo Despacho corre con `DISPATCH_MODE=fake`.
- Modo TDD: sin configurar. Verificaciones funcionales de cada repositorio.
- Commits solo con confirmación explícita del usuario.

## Tareas

| ID | Ruta | Repositorio | Tarea | Estado |
|---|---|---|---|---|
| T1 | Delegada (escritor; 4+ archivos) | backend | Recotización, `409`, DTO del contrato y pruebas | [x] `794f081`, PR #70 |
| T2 | Delegada (escritor; 3+ archivos) | frontend | Cuerpo reducido, `Idempotency-Key` estable, manejo del `409` y pruebas | [x] `ded36c5`, PR #42 |
| T3 | Directa | ambos | PR por repositorio hacia `development` y promoción a `main` | [x] backend #71 (`b666d58`), frontend #43 (`9014c8e`) |

## Criterios de aceptación

- El checkout con dirección cubierta usa el costo de la cotización de Despacho; sin cobertura responde `422 SIN_COBERTURA`.
- Un cuerpo con `lineas`, `subtotal`, `costoEnvio`, `descuento` o `total` responde `400 VALIDACION`.
- Una copia del carrito desactualizada responde `409 CARRITO_DESACTUALIZADO` con `summary`.
- El frontend no envía importes y reutiliza la misma `Idempotency-Key` al reintentar.

## Verificaciones aplicables

- Backend: `ruff check .`, `python -m pytest tests/unit`.
- Frontend: `pnpm lint`, `pnpm typecheck`, `pnpm test` (en local con Node 26: `NODE_OPTIONS=--no-experimental-webstorage`).

## Progreso

- 2026-11-06: mapeo del flujo de importes y alcance acordado con Mathias.
- 2026-11-06: T1 hecha (backend PR #70, `794f081`): `ruff` limpio y 851 pruebas unitarias en verde. T2 hecha (frontend PR #42, `ded36c5`): lint sin errores, typecheck y 340 pruebas en verde. CI en verde en ambos PR. Seguimiento: el DTO estricto descarta `contacto.celular`, por lo que la validación de celular verificado (SPEC-04) ya no se ejecuta en el checkout.

- 2026-11-06: T3 hecha. #70 y #42 mergeados con permisos de administrador; promoción a `main` con merge commit: backend #71 y frontend #43. Producción expone el `CreateCheckoutRequest` del contrato (`additionalProperties: false`) y Vercel completó el despliegue.

## Siguiente paso

Probar en producción el flujo con sesión: envío, pago, pedido y correo. Seguimiento: validación de celular verificado en el checkout (SPEC-04).
