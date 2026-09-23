# Diseño: Inicio de sesión, MFA y gestión de sesión

> Origen: SPEC-03 · Especificación de comportamiento: [`spec.md`](spec.md)

## Integraciones

| Módulo | Endpoint | Estado |
|---|---|---|
| Seguridad | `POST /auth/login` | ✅ |
| Seguridad | `POST /auth/otp/solicitar` · `POST /auth/otp/verificar` | ✅ |
| Seguridad | `POST /auth/refresh` · `POST /auth/logout` · `GET /auth/me` | ✅ |
| Seguridad | `GET /auth/.well-known/jwks.json` | ✅ |

## Frontend

| Componente | Responsabilidad |
|---|---|
| `LoginForm` | Correo y contraseña; errores genéricos; enlaces a registro y a reenvío de verificación. |
| `MfaStep` + `OtpInput` | 6 casillas numéricas con pegado automático, cuenta regresiva, reenvío con temporizador y cambio de canal. |
| `chatStore` (Zustand, slice de sesión) | Guarda `accessToken`, `expiraEn` y `usuario` persistidos en LocalStorage, y expone `login`, `logout` y `refresh`. El logout borra la entrada de LocalStorage. |
| `apiClient` (interceptor) | Agrega el Bearer, hace refresh previo al vencimiento, mantiene una única promesa de refresh concurrente y reintenta una vez ante `401`. |
| `SesionIndicator` | Avatar o nombre en la cabecera de `AppShell`, con el menú "Mis pedidos", "Mis reclamos" y "Cerrar sesión". |
| Restauración al cargar | Lee el token de LocalStorage al montar la aplicación; si expiró o no existe, llama a `POST /sesion/refresh`. |

## Backend

| Componente | Responsabilidad |
|---|---|
| `POST /api/v1/sesion/login` | Proxy del login; maneja `mfaRequerido`; fija las cookies `chat_rt` y `chat_chg`. |
| `POST /api/v1/sesion/mfa/solicitar` · `/verificar` | Usa el `challengeToken` de la cookie; al verificar, abre la sesión igual que el login. |
| `POST /api/v1/sesion/refresh` · `/logout` | Rotación y borrado de las cookies. |
| `GET /api/v1/sesion/perfil` | Proxy de `/auth/me` (incluye `celularVerificado`, que usa SPEC-04). |
| `JwtValidator` (dependencia FastAPI `get_cliente_actual`) | JWKS cacheado; exige el rol `CLIENTE`; expone `cliente_id = sub`. |
| `SesionService.post_login()` | Liga la conversación, fusiona los carritos y ejecuta la `accionPendiente`. |
| Herramientas LLM `solicitar_login` y `cerrar_sesion` | Devuelven el bloque `FORMULARIO/LOGIN` o ejecutan el logout. |

## Desglose para issues

- [ ] `[FE]` `LoginForm` con manejo de errores genéricos y enlaces
- [ ] `[FE]` `MfaStep` y `OtpInput` (pegado, temporizador, reenvío, canal SMS)
- [ ] `[FE]` Slice de sesión en `chatStore` con el token persistido en LocalStorage y restauración al cargar
- [ ] `[FE]` Interceptor `apiClient` con refresh único concurrente
- [ ] `[FE]` `SesionIndicator` y menú de usuario
- [ ] `[BE]` Endpoints de login, MFA, refresh, logout y perfil con cookies seguras y CSRF
- [ ] `[BE]` `JwtValidator` con caché del JWKS y tolerancia a caídas
- [ ] `[BE]` `SesionService.post_login`: ligar la conversación, fusionar carritos y ejecutar la acción pendiente
- [ ] `[BE]` Herramientas `solicitar_login` y `cerrar_sesion`
- [ ] `[INT]` Pruebas contra Prism (`Prefer: example=conMfa`, `code=401`, `REFRESCO_INVALIDO`)
- [ ] `[QA]` Pruebas de todos los escenarios; E2E de login con MFA y retoma del checkout
