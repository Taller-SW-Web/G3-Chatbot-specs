# Diseño: Consulta de estado y respuesta del reclamo

> Origen: SPEC-20 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Ventas | `GET /api/v2/reclamos?clienteId=&estado=&pagina=&tamano=` | ✅ `api-contract.md` §2.8 |
| Ventas | `GET /api/v2/reclamos/{codigoSeguimiento}` | ✅ §2.7 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `ClaimList` | Lista de reclamos con badge de estado. |
| `ClaimStatusCard` (bloque `ESTADO_RECLAMO`) | Estado, `fechaLimiteSLA` y respuesta diferenciada. |
| Menú de usuario → "Mis reclamos" | Acción directa `LISTAR_RECLAMOS`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `GET /api/v1/reclamos` · `GET /api/v1/reclamos/{codigoSeguimiento}` | Proxy con control de pertenencia (`clienteId` del token, nunca del cliente). |
| `ReclamoConsultaService` | Mapea los cuatro estados reales y arma el mensaje del plazo o la respuesta. |
| Herramientas `listar_reclamos` y `consultar_reclamo` (`{codigoSeguimiento?}`) | Uso desde el chat. |

## Desglose para issues

- [ ] `[BE]` Endpoints de consulta y listado, proxy directo a Ventas
- [ ] `[BE]` `ReclamoConsultaService` con el mapeo de los 4 estados
- [ ] `[BE]` Herramientas `listar_reclamos` y `consultar_reclamo`
- [ ] `[FE]` `ClaimList` y `ClaimStatusCard`, más la entrada en el menú
- [ ] `[QA]` Pruebas de todos los escenarios, incluida la fidelidad textual de la respuesta
