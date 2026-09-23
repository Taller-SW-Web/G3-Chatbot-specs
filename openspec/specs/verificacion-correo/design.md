# Diseño: Verificación de correo

> Origen: SPEC-02 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Seguridad | `POST /auth/verificar-correo` | ✅ |
| Seguridad | `POST /auth/verificar-correo/reenviar` | ✅ |
| Seguridad | URL base del enlace del correo → `https://<front-chatbot>/verificar-correo` | 🟡 Acuerdo A1 |

## Frontend

| Componente | Responsabilidad |
|---|---|
| Ruta `/verificar-correo` (`VerificarCorreoPage`) | Lee el token, llama al BFF, limpia la URL y muestra los estados éxito, vencido, usado y sin token. |
| `ReenviarVerificacionForm` | Campo de correo y botón; mensaje neutro; manejo del 429. |
| Integración con `AppShell` | Parámetro `?abrirLogin=1` para que la app abra el formulario de login al volver desde el correo. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/sesion/verificar-correo` | Reenvía a Seguridad; propaga `204` y `410` con su `code`. |
| `POST /api/v1/sesion/verificar-correo/reenviar` | Reenvía a Seguridad; siempre `202` salvo `429`. |
| Herramienta LLM `reenviar_verificacion` | Devuelve el bloque `FORMULARIO` con el campo correo (el LLM no envía el correo por sí mismo). |

## Desglose para issues

- [ ] `[FE]` Crear `VerificarCorreoPage` con los 4 estados y la limpieza de URL
- [ ] `[FE]` Crear `ReenviarVerificacionForm` reutilizable (página, chat y login)
- [ ] `[FE]` Abrir `AuthModal` en el login mediante el parámetro de URL
- [ ] `[BE]` Endpoints proxy de verificación y reenvío
- [ ] `[BE]` Herramienta `reenviar_verificacion`
- [ ] `[INT]` Pruebas contra Prism (`204`, `410` con ejemplos `expirado` y `yaUsado`, `429`)
- [ ] `[INT]` Coordinar con Seguridad la URL del enlace (acuerdo A1)
- [ ] `[QA]` Pruebas de todos los escenarios y verificar que el token no aparece en logs
