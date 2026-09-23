# Diseño: Registro de cliente desde el chat

> Origen: SPEC-01 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Seguridad | `POST /auth/registro` | ✅ |
| Seguridad | `GET /password/politica` | ✅ |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `AuthModal` | Contenedor con pestañas "Crear cuenta" e "Iniciar sesión"; en móvil se muestra como hoja inferior. |
| `RegistroForm` | React Hook Form + Zod; normaliza el celular, muestra y oculta la contraseña, y enlaza a los términos y condiciones. |
| `PasswordPolicyChecklist` | Muestra las reglas de la política en tiempo real. |
| `ChatMessage` (bloque `FORMULARIO/REGISTRO`) | Renderiza el disparador del modal dentro del flujo de mensajes. |
| Servicio `authApi.registrar()` | Llama a `POST /api/v1/sesion/registro` y mapea `problem+json` a errores de campo. |

## Backend

| Componente | Responsabilidad |
|---|---|
| Router `sesion` → `POST /api/v1/sesion/registro` | Valida con Pydantic, aplica el rate limit y reenvía a Seguridad. |
| `SeguridadClient.registrar()` | Cliente httpx con timeout de 5 s y URL base parametrizada (mock/real). |
| `ErrorMapper` | Traduce los `code` de Seguridad a los `code` propios o los propaga. |
| Herramienta LLM `solicitar_registro` | No recibe argumentos y devuelve el bloque `FORMULARIO/REGISTRO`. |
| Filtro de logs | Redacta los campos `contrasena` y `confirmacion`. |

## Desglose para issues

- [ ] `[FE]` Crear `AuthModal` con pestañas y la variante de hoja inferior para móvil
- [ ] `[FE]` Implementar `RegistroForm` con esquema Zod, normalización del celular y confirmación de contraseña
- [ ] `[FE]` Implementar `PasswordPolicyChecklist` consumiendo `/sesion/politica-contrasena`
- [ ] `[FE]` Mapear los errores `problem+json` a errores de campo y mensajes genéricos
- [ ] `[BE]` Endpoint `POST /api/v1/sesion/registro` con rate limit por IP y antirrebote por correo
- [ ] `[BE]` Endpoint `GET /api/v1/sesion/politica-contrasena` con caché de 10 min
- [ ] `[INT]` `SeguridadClient.registrar` contra el mock Prism (`Prefer: code=409`, `code=400`, `code=422`)
- [ ] `[BE]` Herramienta `solicitar_registro` y guardado de `accionPendiente`
- [ ] `[BE]` Filtro de logs que redacte las contraseñas
- [ ] `[QA]` Pruebas de todos los escenarios (unitarias e integración con respx) y un E2E con Playwright del registro exitoso
