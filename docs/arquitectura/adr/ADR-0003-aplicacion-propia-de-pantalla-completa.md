# ADR-0003: Aplicación web propia de pantalla completa, no un widget embebido

## Estado

Aceptada

## Fecha

2026-09-24 (fecha de registro; la decisión sale de los wireframes mobile del equipo, sin fecha)

## Contexto

- El Canal Chatbot es un canal de venta del Marketplace Multicanal, al mismo nivel que los demás canales, y el curso le asigna su propio frontend y backend.
- Los wireframes mobile del equipo muestran una navegación de cliente de chat (barra lateral, pantalla de inicio con ofertas, conversación, carrito, checkout e historial de pedidos).
- SPEC-05 exige conversaciones múltiples (crear, listar, buscar, retomar), lo que no cabe en un widget flotante de conversación única.

## Decisión

El canal es una **aplicación web propia, solo web, de uso mobile-first y de pantalla completa**, con el patrón de ChatGPT o WhatsApp Web. No es un widget embebido en otro módulo. Todas las pantallas (`HomePage`, `Sidebar`, `ChatPage`, `CartPage`, `CheckoutPage`, `OrderHistoryPage`) son de pantalla completa, no superposiciones.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Widget flotante embebido en la web de otro módulo | Excluido de forma explícita (README, encabezado; `alcance.md` §3). No soporta conversaciones múltiples ni pantallas propias de carrito, checkout e historial |
| WhatsApp u otros canales de mensajería | Fuera de alcance (SPEC-05 · *Fuera de alcance*) |
| Aplicación móvil nativa | Fuera de alcance: el canal es "solo web" (`alcance.md` §3) |

## Consecuencias

**Positivas**
- El modelo de datos soporta varias conversaciones por cliente, cada una con su memoria de trabajo (`conversacion.contexto`).
- Carrito, checkout e historial tienen pantallas completas donde se capturan datos sensibles fuera del chat ([ADR-0006](ADR-0006-datos-sensibles-fuera-del-llm.md), [ADR-0016](ADR-0016-direccion-en-checkoutpage-fuera-del-chat.md)).
- El canal controla sus cabeceras de seguridad (CSP) porque no se ejecuta dentro de una página ajena.

**Negativas y riesgos aceptados**
- El equipo construye y mantiene un frontend completo (enrutamiento, estado, sesión), no solo un componente.
- Sin canales de mensajería ni app nativa, el alcance depende del navegador del cliente.

## Referencias

- `README.md` encabezado (línea 5) y §2 (líneas 153-168)
- `openspec/specs/motor-conversacion/spec.md` Contexto (líneas 9-17) y Requisito 1
- `docs/producto/alcance.md` §3 (líneas 21-29)
