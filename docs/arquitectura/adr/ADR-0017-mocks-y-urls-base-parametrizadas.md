# ADR-0017: Integración contra mocks con URLs base parametrizadas

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; práctica de los `design.md` y de la Definición de Listo, sin fecha)

## Contexto

- Los contratos externos maduran a distinto ritmo:
  - Seguridad publicó su `openapi.yaml`, pero las credenciales reales llegan en el Hito 4 (A3);
  - las rutas de Productos son una propuesta del chatbot (A5);
  - el seguimiento de Despacho está abierto (A11).
- La demo del Hito 3 incluye historias que dependen de Productos y Seguridad.
- Cada escenario de las specs necesita al menos una prueba automatizada (README §5).

## Decisión

- Cada cliente de módulo toma su **URL base de la configuración** (mock o real), sin cambiar código. Ejemplo: `SeguridadClient` con "URL base parametrizada (mock/real)".
- **Seguridad** se simula con **Prism** sobre su `openapi.yaml` publicado (puerto `4010`, sin prefijo `/api/v1`), con ejemplos elegidos por la cabecera `Prefer` y `client_secret=secreto-de-prueba`.
- **Productos, Ventas y Despacho** se simulan en las pruebas con **respx** y datos semilla; cada cliente (`ProductosClient`, `VentasClient`…) se entrega con su mock.
- El proveedor LLM y el WebSocket se mockean en las pruebas del motor; el correo se revisa en **Mailtrap**.
- Definición de Listo (R3): una historia puede empezar si su contrato está confirmado **o** existe un mock utilizable.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Esperar a que los módulos publiquen APIs reales (*alternativa estándar, no documentada*) | Bloquearía la demo del Hito 3 y el desarrollo de las historias con contratos provisionales |
| Prism también para Productos, Ventas y Despacho (*alternativa estándar, no documentada*) | Productos no tiene OpenAPI publicado; los documentos fijan respx para estos tres módulos |

## Consecuencias

**Positivas**
- El equipo desarrolla y prueba sin depender de la disponibilidad de otros módulos.
- Pasar de mock a real es un cambio de configuración, combinado con la arquitectura hexagonal ([ADR-0002](ADR-0002-arquitectura-hexagonal.md)).

**Negativas y riesgos aceptados**
- Un mock puede divergir del contrato real: si Productos cambia sus rutas, hay que rehacer clientes y DTOs (riesgo R1).
- La introspección y el token de servicio no se prueban contra el servicio real hasta el Hito 4 (riesgo R8).

## Referencias

- `README.md` §1.5, fila *Pruebas* (línea 146)
- `docs/contratos-integracion.md` §3.1 (encabezado, mock Prism en `:4010`)
- `openspec/specs/registro-cliente/design.md` (`SeguridadClient`, pruebas `[INT]` contra Prism)
- `openspec/specs/inicio-sesion/design.md` y `verificacion-correo/design.md` (pruebas contra Prism)
- `openspec/specs/busqueda-filtrado/design.md`, `creacion-reclamo/design.md`, `solicitud-devolucion-cambio/design.md` (mocks por cliente)
- `docs/producto/definicion-listo-terminado.md` R3 y D2.1
- `docs/producto/alcance.md` §8, supuestos 1 y 2; §9, riesgos R1 y R8
