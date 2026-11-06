# H4-A1: correcciones de los contratos de APIs

## Objetivo

Corregir los bloqueantes de la revisión de los PR backend #60 y specs #26 (contratos de cupones, envío, checkout y pedidos, SPEC-12 a 18) para que el contrato acordado sea seguro y sirva de guía a las correcciones de #59 y #33.

## Problema

La revisión del 2026-11-06 (Codex, verificada por el orquestador) encontró que el contrato de `POST /api/v1/checkout` acepta del cliente líneas con precio, `subtotal`, `descuento`, `costoEnvio` y `total` (`commerce_contracts_dto.py:312-326`, `contratos-integracion.md:157-187`). Esto contradice SPEC-14 y la regla del hito: precios, descuentos y costos de envío provienen siempre del servidor.

## Alcance

- Backend, rama `feature/h4-a1-contratos-apis` (PR #60).
- Specs, rama `feature/h4-a1-contratos-apis` (PR #26).
- Fuera de alcance: implementar checkout, envío o pedidos; montar routers nuevos; corregir #59 y #33.

## Restricciones

- Commits solo con confirmación explícita del usuario. Sin atribución de IA.
- Código en inglés; documentación de specs en español neutro (sin voseo).
- Modo TDD: sin configurar. Verificaciones funcionales del repositorio.

## Tareas

Ruta: delegada a un worker de Codex (2 repositorios, varios archivos); revisión del orquestador.

- [x] C1 Checkout sin importes del cliente: el cuerpo acepta solo `cartId` opcional (carrito propio), `conversacionId`, `guardarDireccion`, `direccion` y `contacto`; líneas e importes se resuelven en el servidor. Backend y specs.
- [x] C2 `contacto` validado con `BuyerContactDTO`, con 400 `DATO_INVALIDO` mapeado. Backend y specs.
- [x] C3 `Idempotency-Key` obligatoria en `POST` reenviar-confirmación, con deduplicación por cliente, pedido y clave. Backend y specs.
- [x] C4 Cotización de envío: si Despacho no devuelve `costoEnvio` o el plazo, responder 503 en lugar de asumir cero o un día. Backend y specs.
- [x] C5 Specs: definir el 409 `CARRITO_DESACTUALIZADO` (con resumen actualizado del servidor) y el 400 `DATO_INVALIDO`; corregir `odd/tasks/hito-4.md` si declara implementados endpoints que solo son contrato.

## Criterios de aceptación

- Ningún DTO ni ejemplo de contrato acepta precios, descuentos, costos de envío o totales del cliente.
- `ruff check .` y `python -m pytest tests/unit` pasan en el backend.

## Progreso

- 2026-11-06: documento creado; tareas delegadas a Codex.
- 2026-11-06: C1 a C5 hechas por un worker de Codex y revisadas por el orquestador. Verificación: `ruff check .` sin errores y `pytest tests/unit` con 681 pruebas aprobadas; sin campos de importes en el esquema ni en el ejemplo del checkout. Commits: backend #60 `2048556`, specs #26 `f120332` y merge de `main` `4ae00a1` (conflicto en `odd/tasks/hito-4.md` resuelto conservando ambos lados).
- Seguimiento: el código 400 `DATO_INVALIDO` se decide en el manejador global por la ruta `/checkout`; conviene moverlo al router de checkout cuando se implemente. El frontend #33 recibirá 400 mientras envíe importes (`extra="forbid"`).
