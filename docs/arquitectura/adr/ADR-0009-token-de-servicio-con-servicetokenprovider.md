# ADR-0009: Token de servicio `client_credentials` con `ServiceTokenProvider` desde el Hito 4

## Estado

Aceptada

## Fecha

2026-09-24 (se adelanta el `ServiceTokenProvider` al Hito 4)

## Contexto

- Varias llamadas del chatbot no tienen un token de cliente disponible o no deben usarlo:
  - el `OutboxWorker` notifica pagos y solicita anulaciones a Ventas en segundo plano (SPEC-15);
  - la introspección previa al pago se hace con credenciales del módulo (SPEC-14, acuerdo A3);
  - el seguimiento de Despacho exige token de servicio (SPEC-18, A4 y A11 abiertos).
- El `ServiceTokenProvider` figuraba en el desglose de SPEC-18 (Hito 5–6), pero SPEC-14 y SPEC-15, del Hito 4, ya lo necesitaban.
- La validación del token del cliente se hace en local con el JWKS de Seguridad.

## Decisión

- El backend obtiene un **token de servicio** con `POST /auth/token` (`grant_type=client_credentials`, `client_id=modulo-chatbot`) mediante un componente único, **`ServiceTokenProvider`**, que lo **cachea hasta 60 s antes de su `exp`** y lo renueva ante `401`.
- Se construye en el **Hito 4** dentro de HU-CHK-14 (SPEC-14); SPEC-15 y SPEC-18 lo reutilizan.
- Reglas de autenticación entre componentes:
  - Token del cliente → validación local con JWKS cacheado (`iss=auth-service`, `tipo=acceso`, rol `CLIENTE`).
  - Recurso del titular (p. ej. direcciones) → se reenvía el token del cliente.
  - Operación a nombre del sistema → token de servicio.
  - Antes de cada pago → `POST /auth/introspeccion` con scope `tokens:introspeccion`, sin caché y con timeout de 3 s.
- Hasta el Hito 4 se prueba contra Prism con `client_secret=secreto-de-prueba`.

## Alternativas consideradas

| Alternativa | Por qué se descartó |
|---|---|
| Construir el `ServiceTokenProvider` en el Hito 5–6 con SPEC-18 (plan original) | La introspección de SPEC-14 y el worker de SPEC-15, ambos del Hito 4, lo necesitan antes (`alcance.md`, pregunta 3) |
| Reutilizar el token del cliente en las tareas en segundo plano (*alternativa estándar, no documentada*) | El worker no tiene sesión de cliente y el token de 15 min puede haber expirado cuando se reintenta |

## Consecuencias

**Positivas**
- Una sola implementación de caché y renovación para todos los clientes de módulos.
- Los tokens de servicio nunca llegan al navegador ([ADR-0004](ADR-0004-backend-como-bff-y-nextjs-solo-frontend.md)).

**Negativas y riesgos aceptados**
- Las credenciales reales llegan recién en el Hito 4 (riesgo R8); hasta entonces solo se prueba contra el mock.
- El rol `SERVICIO_INTEGRACION` para consultar Despacho sigue sin emitirse (A4, riesgo R3).

## Referencias

- `docs/contratos-integracion.md` §1 (líneas 19-27), §3.1 (líneas 151-160) y §6, acuerdos A3 y A4
- `openspec/specs/seguimiento-despacho/design.md` (líneas 26 y 34)
- `openspec/specs/checkout-pago/design.md` (`IntrospeccionClient`, línea 32) y `spec.md` RNF *Seguridad (autorización)* (línea 176)
- `openspec/specs/grabacion-pedido/design.md` (Integraciones)
- `docs/producto/alcance.md` pregunta 3 (líneas 254-255), riesgos R3 y R8
