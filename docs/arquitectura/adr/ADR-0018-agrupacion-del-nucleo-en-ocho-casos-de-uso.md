# ADR-0018: Agrupación del núcleo del backend en 8 casos de uso

## Estado

Propuesta

## Fecha

2026-09-24 (fecha de registro)

## Contexto

- El diagrama hexagonal del backend (README §1.2) muestra "8 casos de uso" en la capa `application/`.
- Las 22 specs definen capacidades, no casos de uso de código, y sus `design.md` nombran servicios (`CheckoutService`, `PedidoService`, `SesionService`…) sin decir a qué caso de uso pertenecen.
- El README marca la agrupación con 🧩: es una propuesta para alinear specs y diagrama, que el equipo debe confirmar contra el código o ajustar (README línea 111; `alcance.md` §8, supuesto 4).

## Decisión (propuesta)

El núcleo del backend se organiza en estos 8 casos de uso:

| Caso de uso | Agrupa |
|---|---|
| `GestionarConversacionUseCase` | SPEC-05 (crear, listar, buscar, historial) |
| `InterpretarYResponderUseCase` | SPEC-05 (tool calling, streaming) |
| `GestionarCatalogoUseCase` | SPEC-06 a SPEC-09 |
| `GestionarCarritoUseCase` | SPEC-10, 11, 13 |
| `GestionarCheckoutUseCase` | SPEC-12, 14 |
| `GestionarPedidoUseCase` | SPEC-15, 16, 17 |
| `GestionarSeguimientoUseCase` | SPEC-18 |
| `GestionarPostventaUseCase` | SPEC-19 a SPEC-22 |

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Un caso de uso por spec (*alternativa estándar, no documentada*) | No descartada formalmente; daría 22 o más casos de uso frente a los 8 del diagrama del equipo |

## Consecuencias

**Positivas**
- Alinea el diagrama del README con las specs y da un mapa para el `ToolRegistry` (cada herramienta apunta a un caso de uso).

**Negativas y riesgos aceptados**
- **Hueco detectado:** el README dice que los 8 casos de uso agrupan "las 22 specs", pero la tabla no incluye SPEC-01 a SPEC-04 (identidad). Sus componentes (`SesionService`, `JwtValidator`, `CheckoutGuard`, endpoints `/sesion/*` y `/contacto/celular/*`) quedan fuera de la agrupación.
- Mientras no se confirme contra el código, los nombres pueden cambiar.

## Preguntas abiertas

1. ¿Se agrega un noveno caso de uso de identidad (p. ej. `GestionarSesionUseCase`, SPEC-01 a 04) o la identidad se trata como servicios transversales fuera de los casos de uso?
2. ¿Los nombres coinciden con el código del repositorio `G3-Chatbot-backend`? Al confirmarlo, este ADR pasa a **Aceptada** (o se reemplaza).

## Referencias

- `README.md` §1.2 (líneas 70-114)
- `docs/producto/alcance.md` §8, supuesto 4 (línea 224)
- [Modelo C4, nivel 3](../c4.md#nivel-3--componentes-del-backend)
