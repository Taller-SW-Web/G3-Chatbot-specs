# Design System — Inka Athletics (Mockups)

> Fuente de verdad del frontend en `Mockups-Wireframes/app`.
> Tokens definidos en `app/globals.css` (`@theme` de Tailwind CSS v4), fuentes en
> `app/layout.tsx` (`next/font/google`), componentes en `app/page.tsx` y
> `app/components/`.
> Stack real: **Next.js 16.3.6 App Router + React 19.2.8 + TypeScript 5 + Tailwind CSS v4**
> (`@tailwindcss/postcss ^4`, sin `tailwind.config`, todo por CSS variables).
> Logos en `public/logos/inka-volt-sinfondo.png` y `inka-negro-sinfondo.png`.

Mapa de archivos:

| Archivo | Contiene |
|---|---|
| `app/globals.css` | Todos los tokens `@theme`, clases `.wf-*`, keyframes, `.wf-phone`, foco |
| `app/layout.tsx` | Carga `Inter` + `Oswald` con variables `--font-sans` / `--font-display`, `lang="es"` |
| `app/page.tsx` | Las 13 pantallas + `IconBtn`, `PlaceholderImg`, `SectionLabel`, `AttachmentPopup`, `ProductModal`, `AuthModal`, `Sidebar`, etc. |
| `app/components/StatusBadge.tsx` | Server Component de badges de estado + `STATUS_VARIANT_MAP` |
| `app/components/BrandLogo.tsx` | Client Component logo con fallback a wordmark en texto |
| `app/components/icons/*.tsx` | Set único de 22 iconos (estilo Tabler, `currentColor`) |

---

## 1. Marca

- **Nombre:** Inka Athletics.
- **Propósito:** Impulsar a más personas a vivir el deporte con confianza, encontrando equipamiento, ropa y accesorios adecuados para cada meta.
- **Personalidad:** Determinada · Cercana · Contemporánea · Confiable · Activa · Orgullosamente peruana, sin clichés.
- **Tono de voz (obligatorio en todos los copy):** Directo, motivador y humano. Con energía, sin gritar ni presionar.
  - Debe sonar: Claro ("Encuentra tu talla y entrena cómodo.") · Motivador ("Tu próxima meta empieza hoy.") · Cercano ("Todo listo para seguir avanzando.") · Seguro ("Compra productos verificados y recibe seguimiento de tu pedido.") · Deportivo ("Equípate para dar tu mejor paso.").
  - Evitar: exceso de inglés · frases agresivas ("sé el mejor", "no pares nunca") · juvenil forzado/informal · folklorismo superficial.
  - Descripciones de `ProductModal` (`descripcionPara()`): Runner = "Amortiguación ligera para tus rutas diarias…", Urban = "Pisada estable y diseño versátil…", Trail = "Agarre firme en tierra y piedra…", Court = "Clásica y cómoda para el uso diario…".
- **Logos (2 archivos reales + 1 fallback):**
  | Variante | Archivo / uso | Tamaño en mockups |
  |---|---|---|
  | `volt` | `/logos/inka-volt-sinfondo.png` (1334×406) — header sobre ink, sidebar | `h-11` header (botón a **nuevo chat**), `h-12` sidebar |
  | `negro` | `/logos/inka-negro-sinfondo.png` (1306×368) — `AuthModal` sobre blanco | `h-16` centrado en auth |
  | fallback texto | `INKA ATHLETICS` en `.font-heading` (`text-text-inverse` + `text-accent-volt`, o `text-text-primary` + `text-ember`) si la imagen falla | mismo tracking `0.08em` |
  | Tercera variante Figma `signal` (azul) | Solo referencia de marca, **no se usa en mockups** |

---

## 2. Colores (tokens `@theme` → clases Tailwind v4)

> En Tailwind v4 `--color-action-primary: #f76707` genera `bg-action-primary`, `text-action-primary`, `border-action-primary`, etc. **Nunca hardcodear hex en JSX** salvo `PlaceholderImg` y `body`.

### 2.1 Action — CTAs y acciones prioritarias (texto sobre naranja siempre `text-surface-ink`)

| Token (`@theme`) | Hex | Clase | Uso cerrado |
|---|---|---|---|
| `action/primary` | `#F76707` | `bg-action-primary` | CONFIRMAR COMPRA, IR A PAGAR, AGREGAR AL CARRITO, VER SEGUIMIENTO / EN HISTORIAL, ENTRAR COMO DEMO, REGISTRARSE, CONFIRMAR, botón `+` de tarjetas, VER OFERTAS del hero |
| `action/primary-hover` | `#C2410C` | `hover:bg-action-primary-hover` | Hover de todo lo anterior |
| `action/primary-soft` | `#FCE3D0` | `bg-action-primary-soft` | Solo fondo suave "Sin verificar" (cuenta) |
| `ember` / `ember-deep` (alias legacy tester) | `#F76707` / `#C2410C` | `text-ember`, `bg-ember-deep` | Fallback logo negro + texto `Sin verificar` (`text-ember-deep`). **Prohibido para estados** |

### 2.2 Accent — marca

| Token | Hex | Clase | Uso |
|---|---|---|---|
| `accent/volt` | `#C3E504` | `bg-accent-volt` / `text-accent-volt` | Badge contador carrito, esquina recortada de `PlaceholderImg` (`clip-path: polygon(100% 0,0 0,100% 100%)`), pill "OFERTAS DE LA SEMANA" (fondo es `volt-soft`), punto de sidebar recientes, avatar cuenta, hito actual en seguimiento |
| `accent/volt-soft` | `#EEF7B0` | `bg-accent-volt-soft` | Fondo badge DISPONIBLE, "Verificado", "Celular verificado", sombra `.wf-check` (`box-shadow: 0 0 0 5px volt-soft, 0 0 0 6.5px ink`) |
| `accent/volt-ink` | `#5C6B00` | `text-accent-volt-ink` | Texto sobre `volt-soft` |
| `accent/signal` | `#4361EE` | `text-accent-signal` / `border-accent-signal` | Foco `:focus-visible` (outline 3px), hover de chips (`hover:border-accent-signal`), icono `VerifyEmailModal` |
| `accent/signal-soft` | `#E1E6FB` | `bg-accent-signal-soft` | Fondo icono correo éxito, anillo de foco `.wf-input:focus` (`outline: 2px solid signal-soft`), gradiente de `PlaceholderImg` |
| `accent/signal-ink` | `#2839A8` | `text-accent-signal-ink` | Texto sobre `signal-soft` (reservado) |

### 2.3 Surfaces

| Token | Hex | Uso |
|---|---|---|
| `surface/ink` | `#1B1812` | Header, burbuja usuario, botones oscuros (`bg-surface-ink text-text-inverse`), fondo `body` (`--background`), hero, `Total a pagar`, tabs activos, tallas activas, dots paginación activos, overlay `bg-surface-ink/60` |
| `surface/ink-soft` | `#26221A` | `IconBtn` header, hover sidebar (`hover:bg-surface-ink-soft`), gradiente `PlaceholderImg`, hero "1 / 4", icono camión en seguimiento |
| `surface/cloud` | `#F7F5F0` | Fondo del teléfono y de todas las pantallas (`bg-surface-cloud`), hover filas buscar, steppers |
| `surface/cloud-subtle` | `#EDEAE2` | Divisores (`divide-surface-cloud-subtle`), tabs auth, dropzone evidencia punteada |

### 2.4 Texto

| Token | Hex | Uso |
|---|---|---|
| `text/primary` | `#1B1812` | Títulos, nombres producto, texto principal |
| `text/secondary` | `#495057` | Descripciones, tallas, precios **contenidos** (13–14px semibold), ayudas, placeholders (`placeholder:text-text-secondary`) |
| `text/disabled` | `#868E96` | Placeholders deshabilitados, swatch Gris `#868E96` |
| `text/inverse` | `#F7F5F0` | Sobre ink (header, burbuja usuario, `.font-heading` fallback volt) |
| `text/inverse-soft` | `#D8D3C8` | Subtítulo hero "Equípate…", subtítulo seguimiento |
| `text/muted-dark` | `#9C9788` | Etiqueta `RECIENTES`, previews sidebar, chevron cuenta |

### 2.5 Bordes

| Token | Hex | Uso |
|---|---|---|
| `border/default` | `#DEE2E6` | Tarjetas blancas, inputs, chips, modales (fondo claro) |
| `border/inverse` | `#3A362C` | `IconBtn`, filas sidebar, hero interno sobre ink |

### 2.6 Semánticos — únicos permitidos para badges de estado (nunca ember)

| Estado | Texto / Fondo | Clases | Uso acordado |
|---|---|---|---|
| `info` | `#1971C2` / `#E7F5FF` | `bg-info-background text-info-default` | **EN CAMINO** (progreso logístico) |
| `warning` | `#F08C00` / `#FFF9DB` | `bg-warning-background text-warning-default` | **EN REVISIÓN, EN PROCESO** (espera/gestión) |
| `success` | `#2F9E44` / `#EBFBEE`¹ | `bg-success-background text-success-default` | **ENTREGADO, APROBADO, RESUELTO, REEMBOLSADO**, cupón aplicado (`border-success-default/30`), stock "Disponible", check éxito |
| `error` | `#E03131` / `#FFF5F5` | `bg-error-background text-error-default` | **Solo error real: RECHAZADO, PAGO FALLIDO**, hover trash carrito, CERRAR SESIÓN |

¹ `globals.css` define `--color-success-background: #ebfbee` (sin la segunda `e` de Figma `#EBFBEE`). Tomar el valor del CSS como canónico en código.

Reglas: rojo/naranja ember **nunca** es estado. Todo badge = **icono + texto**, nunca solo color (`role="status" aria-live="polite"`).

### 2.7 Fondos y decorativos fuera de tokens

- `body`: `#14100B` + 2 radiales (halo volt `rgba(195,229,4,.08)` arriba + puntos `rgba(247,245,240,.07)` trama `22px`).
- `PlaceholderImg`: `linear-gradient(135deg, ink-soft, signal-soft, ink)` + esquina volt.
- Hero: `repeating-linear-gradient(115deg, transparent 0 40px, rgba(247,103,7,.14) 40px 42px, transparent 42px 90px, rgba(195,229,4,.10) 90px 92px)` + `.inka-energy-bar` (`linear-gradient(90deg, action-primary, volt, signal)`, `120×6px`, `radius-full`).
- `.wf-phone`: `border: 2px solid #000` + `box-shadow: 0 0 0 6px rgba(247,245,240,.06), 0 30px 80px rgba(0,0,0,.55)`.
- Blanco puro `#FFF`: tarjetas, burbuja bot, chips, inputs, footers.

---

## 3. Tipografía y fuentes

### 3.1 Carga (única forma permitida)

```tsx
// app/layout.tsx
import { Inter, Oswald } from "next/font/google";
const inter = Inter({ subsets: ["latin"], variable: "--font-sans", display: "swap" });
const oswald = Oswald({ subsets: ["latin"], weight: ["500", "700"], variable: "--font-display", display: "swap" });
<html lang="es" className={`h-full ${inter.variable} ${oswald.variable}`}>
```

- `--font-display: "Oswald", "Arial Narrow", sans-serif` · `--font-sans: "Inter", system-ui, sans-serif`.
- `body { font-family: var(--font-sans); -webkit-font-smoothing: antialiased; }`.
- `h1,h2,h3,.font-heading { font-family: display; weight 700; UPPERCASE; letter-spacing .02em; line-height 1.1; }`.
- `button { font-family: inherit; cursor: pointer; }`.
- `.wf-phone { font-variant-numeric: tabular-nums; }` (cantidades, precios y badges siempre tabulares).
- **Display Oswald 700 MAYÚSCULAS solo H1/H2/H3 + nombres de producto.** Todo lo demás Inter. Prohibido Oswald en body/labels/auxiliares.

### 3.2 Escala (Figma + ajuste real en mockups)

| Estilo | Spec Figma | Uso real en mockups | Clases |
|---|---|---|---|
| H1 | 32/40/700 Oswald | Hero "ENCUENTRA TU PRÓXIMA META" a **28/32** | `font-heading text-[28px] leading-[32px]`, palabra clave `text-action-primary` |
| H2 | 28/36/700 Oswald | "EQUIPAMIENTO DESTACADO" a **24/32**, "¡PEDIDO CONFIRMADO!" / "¡SE REGISTRÓ TU RECLAMO!" / "¡SOLICITUD ENVIADA!" a **24/32** | `font-heading text-[24px] leading-8` |
| H3 | 24/32/700 Oswald | "¡CONFIRMA TU CORREO!" a **20px** | `font-heading text-[20px]` |
| H4 (Inter) | 20/28/700 | Total carrito **20px** heading, nombre `ProductModal` **20px** | `font-heading text-[20px]` (totales) |
| Subtitle | 18/26/600 Inter | Total éxito `18px` heading | `font-heading text-[18px]` |
| Nombre producto | — | 15–20/tight/700 Oswald uppercase `text-primary` (home 17px, chat 15px, modal 20px, carrito 15px) | `font-heading text-[17px]/[15px]/[20px] uppercase leading-tight` |
| Precio contenido | — | **13–14/semibold Inter `text-secondary`, subordinado al nombre**. Nada de precio grande naranja | `text-[13px]/[14px] font-semibold text-text-secondary` |
| Total/Subtotal | — | Solo totales 20px (18px pagado en éxito) | `font-heading text-[20px]` |
| Body | 16/24/400 | Burbujas y descripciones a **14/20** (`leading-5`), modal desc **13/20** | `text-[14px] leading-5`, `text-[13px] leading-5` |
| Body/Small | 14/20/400 | Filas etiqueta/dato pedidos 14px | `text-[14px]` |
| Label | 14/20/600 | `SectionLabel`: **15px heading .06em uppercase** (no 14) | `font-heading text-[15px] tracking-[0.06em] uppercase` |
| Auxiliary | 12/16/400 `text-secondary` | Ayudas, vigencias, notas pago, cajas info 12px | `text-[12px] text-text-secondary` |
| Badge | 10–11/700 | `StatusBadge` 10px, DISPONIBLE/tabs 10–11px | `text-[10px]/[11px] font-bold tracking-wide` |
| Botón | 11–14/700 + `tracking-wide` | Primarios 12–14px, pedidos 11px | `text-[11px]/[12px]/text-sm font-bold tracking-wide` |
| Header ink | — | 16px heading `.08em`, pedidos 13px | `font-heading text-[16px] tracking-[0.08em]`, pedidos `text-[13px]` |

**Jerarquía precio (regla vigente):** el nombre manda (15–17px heading primary), el precio acompaña (13–14px semibold secondary). Solo subtotales/totales en 20px.

---

## 4. Espaciado, radios, sombras y grilla

### 4.1 Espaciado — escala 4px, prohibidos arbitrarios (7/13/19/27px)

| Token (`@theme`) | Valor | Clases generadas | Uso |
|---|---|---|---|
| `xs` | 4px | `p-xs gap-xs`… | Separación mínima, gaps iconos dots |
| `sm` | 8px | `gap-2`… | Icono-texto 8px, gaps internos |
| `md` | 16px | `p-4 gap-4`… | Padding estándar pantallas (`p-4`), gaps secciones (`gap-4`) |
| `lg` | 24px | `p-6 gap-6`… | Hero/éxito (`px-4 pt-5 pb-6`, `p-6`) |
| `xl` | 32px | — | Entre secciones |

Gaps reales más usados: `gap-1/1.5/2/3/4`, `px-3/py-2.5/py-3/py-3.5`, burbujas `px-3 py-2`.

### 4.2 Radios

| Token | Valor | Uso |
|---|---|---|
| `xs` | 4px | Controles compactos (`rounded-xs` en esquina burbuja propia `rounded-br-xs`) |
| `sm` | 8px | Botones `.wf-btn`, inputs `.wf-input` |
| `md` | 12px | Tarjetas `.wf-card`, `PlaceholderImg`, modales chicos (`rounded-md`) |
| `lg` | 16px | Modales/sheets grandes (`rounded-lg` hero, `rounded-t-lg` sheets) |
| `full` | 999px | Badges, chips, pills, steppers redondos, teléfono **36px** (`.wf-phone`) |

### 4.3 Sombras y bordes

- `.wf-card { box-shadow: 0 1px 0 rgba(27,24,18,.08); }` — única sombra de tarjetas.
- `.wf-check { box-shadow: 0 0 0 5px volt-soft, 0 0 0 6.5px ink; animation: pop .35s … }` — check circular éxito.
- `.wf-phone`: borde 2px negro + doble sombra exterior (ver §2.7).
- Divisores: `divide-surface-cloud-subtle`, `border-dashed border-border-default` en resúmenes.

### 4.4 Grilla responsive (12 columnas siempre)

| Breakpoint | Margen / Gutter / Máx | Mockups |
|---|---|---|
| Base <576px | 16 / 16 / fluido | **1 tarjeta/fila en listados, 2 col en grids de producto/chat** (`grid-cols-2`) |
| ≥576px | 20 / 16 / 540 | — |
| Tablet ≥768px | 24 / 20 / 720 | 2/fila |
| ≥992px | 32 / 24 / 960 | — |
| Desktop ≥1200px | 32 / 24 / 1140 | hasta 4/fila |
| ≥1408px | 40 / 24 / 1320 | — |

Teléfono fijo: `max-width 430px`, `height: max(600px, min(880px, 100dvh-2rem))`, `min-height 600px`, columna flex con `main` scroll interno (`overflow-y-auto no-scrollbar`) y footers `sticky bottom-0`.

---

## 5. Componentes base

### 5.1 `.wf-btn` (en `@layer components` para que utilities lo sobrescriban)

`radius-sm`, `font-weight 600`, `font-sans`, `letter-spacing .04em`, `transition transform/shadow/bg`, `:active scale(.96)`.
Variantes reales:

| Variante | Clases | Dónde |
|---|---|---|
| Primario naranja | `bg-action-primary text-surface-ink hover:bg-action-primary-hover` `py-2.5/3/3.5 text-[11px]/[12px]/sm font-bold tracking-wide` | Todos los CTA principales |
| Secundario oscuro | `bg-surface-ink text-text-inverse` | APLICAR cupón, secundarios éxito/reclamo, tabs activos, tallas activas, PREGUNTAR EN EL CHAT |
| Terciario blanco | `bg-white border border-border-default text-text-primary` | MIS PEDIDOS/RECLAMOS, RECLAMAR/DEVOLVER, GALERÍA/TOMAR FOTO |
| Peligro texto | `bg-white border text-error-default` | CERRAR SESIÓN |
| Deshabilitado | `disabled:opacity-45 disabled:cursor-not-allowed` | ENVIAR FOTO sin preview |

### 5.2 `.wf-input`

`border-default`, `radius-sm`, fondo blanco, `text-primary`. Foco: `border-signal + outline 2px signal-soft`. Usos: inputs checkout/auth/carrito/cupón, `select` distrito (10 opciones: Lima Cercado, Miraflores, San Isidro, Santiago de Surco, La Molina, San Miguel, Los Olivos, San Juan de Lurigancho, Villa El Salvador, Callao) y doc (DNI/RUC/CE/PASAPORTE), `textarea` reclamo, OTP 6 celdas (`grid-cols-6`, `maxLength 1`, `inputMode numeric`). Talla activa = excepción oscura (`bg-surface-ink text-inverse`), no `.wf-input`.

### 5.3 `.wf-chip`

`border-default`, `radius-full`, fondo blanco. Quick replies y filtros (`px-3 py-1.5 text-[12px] font-semibold`, `hover:border-accent-signal`). Talla en cards: `text-[11px] px-2 py-0.5`.

### 5.4 `.wf-card` + `PlaceholderImg` + `SectionLabel` + `IconBtn`

- `.wf-card`: solo sombra 1px (ver §4.3), siempre con `rounded-md bg-white border border-border-default`.
- `PlaceholderImg({label})`: `rounded-md`, degradado ink-soft→signal-soft→ink, esquina volt recortada, emoji 👟 32px (`text-[32px] p-2`). Alturas: `h-24` chat, `h-28` home, `h-56` modal, `w-20 h-20` carrito, `w-16 h-16` reembolso, `w-11 h-11` miniaturas pedido.
- `SectionLabel`: `font-heading 15px .06em uppercase primary`.
- `IconBtn({label, onClick})`: `w-10 h-10 wf-btn bg-surface-ink-soft text-inverse border-inverse hover:bg-surface-ink`, steppers `w-7 h-7 bg-cloud`, `+` cards `w-9 h-9 bg-action-primary` (`w-8 h-8` en chat), trash `w-8 h-8 bg-white hover:text-error hover:border-error`. **Todo icono suelto va en botón con `aria-label`.**

### 5.5 `StatusBadge` (`app/components/StatusBadge.tsx`, Server Component)

Props: `status: EN_CAMINO | EN_PROCESO | EN_REVISION | ENTREGADO | APROBADO | RESUELTO | REEMBOLSADO | RECHAZADO | PAGO_FALLIDO`, o `variant: info|warning|success|error`, más `icon` y `children`. Clases: `inline-flex items-center gap-1 rounded-full px-2 py-1 text-[10px] font-bold tracking-wide` + `role="status" aria-live="polite"`. Mapa: `EN_CAMINO→info`, `EN_PROCESO/EN_REVISION→warning`, `ENTREGADO/APROBADO/RESUELTO/REEMBOLSADO→success`, `RECHAZADO/PAGO_FALLIDO→error`. Iconos: `TruckIcon` EN_CAMINO, `CheckIcon` ENTREGADO/APROBADO, `RefreshIcon` EN_REVISION, `FileAlertIcon` EN_PROCESO.

### 5.6 `BrandLogo` (Client Component, `next/image` + `priority` en volt)

Ver §1 para variantes y tamaños. `alt="Inka Athletics"`.

---

## 6. Patrones por pantalla (13 pantallas en `page.tsx`)

| # | Pantalla (`Screen`) | Patrón visual cerrado |
|---|---|---|
| 1 | `home` | Hero ink clicable (pill volt-soft 11px + H1 28px + energy-bar + subtítulo inverse-soft 14px + botón naranja 13px + contador `1/4` + dots `w-6 ink` activo). Grid `grid-cols-2 gap-3` productos (imagen `h-28`, nombre 17px, detalle 12px, precio 14px, DISPONIBLE 11px volt, `+` 36px). Caja "Acciones rápidas" + nota "Toca + para elegir talla…". |
| 2 | `chat` | Burbujas (ver §7), `ProductCards` blancas (título 14px semibold + grid 2 col + chip talla + `+` 32px + "Ver más/menos" 12px underline), quick replies, typing, login-card. |
| 3 | `buscar` | Search pill (`wf-chip px-4 py-3` + `SearchIcon` 20 + input transparente), etiqueta "Recientes" 13px semibold, lista blanca con divisor `cloud-subtle` (título 14px bold + preview 12px + fecha + `ChevronRightIcon` 16). Vacío: `Sin resultados para "q"`. |
| 4 | `carrito` | Cards blancas (IMG 80px, nombre 15px, variante/detalle 12px, precio 13px semibold, trash + stepper max 10). Cupón: input + APLICAR ink, aplicado = caja success 13px bold `CUPÓN −20%` + Quitar underline. Footer blanco sticky: Subtotal 14px / Descuento success / Total heading 20px + IR A PAGAR. Vacío 14px centrado. |
| 5 | `checkout` | Cabecera ink (`Total a pagar:` 14px semibold + total heading 20px). Caja Dirección (4 inputs + grid doc 2 col + nota 12px "El documento…"). Caja tarjeta (número + MM/AA + CVV + nota "solo tarjeta · 15 min · 3 intentos"). CTA CONFIRMAR COMPRA. |
| 6 | `exito` | Check success 64px (`wf-check`), H2 24px, pedido `#A-1043` + correo enmascarado 14px, resumen blanco (subtotal/descuento/total 18px + items `nombre × qty` 13px + tarjeta `••••` + entrega + receptor, divisores dashed), VER MIS PEDIDOS + "Volver al inicio" underline. |
| 7 | `pedidos` (+ tabs) | Tabs `grid-cols-4` blancos (`rounded-sm py-2 text-[10px]`, activo ink). Cards: nº 13px secondary + `StatusBadge`, filas 14px etiqueta/dato, miniaturas 44px, CTAs 11px (VER SEGUIMIENTO naranja + PREGUNTAR ink / RECLAMAR+DEVOLVER blancos). 4 tabs: proceso `#A-1042` EN CAMINO, entregados `#A-0987` ENTREGADO, reembolso `#R-0312` EN_REVISION + `#DEV-2026-00045` APROBADO, reclamos `#REC-2026-0118` EN_PROCESO. |
| 8 | `seguimiento` | Cabecera ink (icono camión 40px + título 15px + subtítulo 12px inverse-soft). Timeline 4 hitos (nodo 24px: hechos ink+check, actual volt+camión, línea 2px). PREGUNTAR EN EL CHAT naranja + "Volver al historial" underline con flecha. |
| 9 | `reclamo` / `reclamo-exito` | Form: select motivo + textarea 4 filas + ENVIAR RECLAMO + caja info 12px "código + 15 días hábiles". Éxito: check + H2 + `#REC-2026-0119` + caja "chat o Historial→Reclamos" + VER EN HISTORIAL + SEGUIR POR EL CHAT ink. |
| 10 | `devolucion` / `devolucion-exito` | Toggle CAMBIO/DEVOLUCION (contenedor blanco + activo ink), dropzone dashed `h-24 cloud-subtle` (JPG/PNG/WEBP/PDF ≤5MB), motivo + ENVIAR SOLICITUD. Éxito: `DEV-2026-00046` + "Historial→Reembolso/Cambio". |
| 11 | `config` (Mi cuenta) | Lista blanca dividida 14px (Nombre / Correo+Verificado volt / Celular+verificado o `action-soft/ember-deep` "Sin verificar" / DNI). OTP 6 dígitos + VERIFICAR. Botones MIS PEDIDOS/RECLAMOS blancos + CERRAR SESIÓN error. Bloque "SE EDITA EN SEGURIDAD…" 11px `.18em` + filas con `LockIcon` 16. |
| 12 | Modales | `AuthModal` (tabs INGRESAR/REGISTRARME ink-activo + inputs + ENTRAR COMO DEMO/REGISTRARSE + nota demo), `VerifyEmailModal` (icono correo signal-soft 64px + H3 20px + CONFIRMAR + Reenviar), `ProductModal` bottom-sheet (ver §6.1), `AttachmentPopup` (GALERÍA/TOMAR FOTO + preview 64px + JPG/PNG/WEBP ≤5MB + ENVIAR FOTO). Todos: overlay `absolute inset-0 z-40 bg-ink/60 fade-in` + `sheet bg-white rounded-t-lg p-4`, cierre `IconBtn X`. |
| 13 | `Sidebar` + header/composer | Header ink sticky (`px-4 py-2 border-inverse`): menú/volver `IconBtn` + logo/`headerTitle` + carrito con badge volt (`min-w-5 h-5 text-[11px] border-ink`, `cartCount`). Sidebar `w-[85%] max-w-[340px] bg-ink side-in`: logo `h-12`, Nuevo chat/Buscar/Historial, RECIENTES 11px `.2em muted-dark` (punto volt 8px + título 14px bold + preview 12px muted), cuenta (avatar volt 36px + Settings 20). Composer sticky (`border-t px-3 py-3`): foto + input pill (`wf-chip px-4 py-2.5 text-sm`) + micro + enviar. |

### 6.1 `ProductModal` (detalle, bottom-sheet `max-h-[92%]` scroll sin barra)

Imagen `h-56` · nombre 20px · categoría 13px · descripción 13/20 motivadora · precio 14px secondary · DISPONIBLE 11px con check · Color (3 swatches 36px: Negro `#1B1812`, Blanco `#FFF`, Gris `#868E96`, activo `ring-2 ring-offset-2 ring-ink`) · Tallas 40–43 (`wf-chip px-4 py-2 text-[14px]`, activa ink) · Stock success · AGREGAR AL CARRITO. El `+` de tarjetas **abre el detalle, no agrega directo**.

---

## 7. Sistema de chat

- Burbuja usuario: `bg-surface-ink text-inverse`, derecha, `max-w-[80%]`, `rounded-md rounded-br-xs px-3 py-2 text-[14px] leading-5`, animación `msg-in`. Fotos: `PhotoIcon 16 + nombre`.
- Burbuja bot: blanca con borde, izquierda, `max-w-[85%]`, `rounded-bl-xs`.
- **Códigos y promos en negrita** (`renderWithBoldCodes`, regex `#[A-Z]-dddd | REC-2026-dddd | DEV-2026-ddddd | R-0312` + `-20%`, `2x1` en copy): `#A-1042`, `REC-2026-0118/0119`, `DEV-2026-00045/00046/00047`, `PED-2026-00891`, `#A-1043`, `#R-0312`.
- CTA contextual bajo bot según código: `VER MI DEVOLUCIÓN`→Reembolso/Cambio · `VER MI RECLAMO`→Reclamos · `RASTREAR PEDIDO`→Seguimiento.
- Quick replies globales (home + chat + vacíos): `Ver ofertas · Rastrear pedido · Ayuda con devolución` (chip blanco, `hover:border-signal`). Con login-gate: invitado → tarjeta `bot-login` (texto 14px + INICIAR SESIÓN naranja).
- `AttachmentPopup`: GALERÍA / TOMAR FOTO (cámara, `capture="environment"`), preview + `ENVIAR FOTO`; botón composer con icono foto.
- Typing: 3 `.tdot` 6px ink con delays 0/.15/.3s.
- Seeds de demo (`FLOW_SEEDS`, `RECENT_CHATS` 7 chats, `CHAT_INICIAL`) y deep-links `?s=&t=&c=&b=&demo=1/2&sb=1&auth=1&modal=A-D&q=&otp=1&tipo=&expand=1&verify=1&added=`.

---

## 8. Iconografía (set único, 22 iconos en `app/components/icons/`)

Estilo Tabler: lienzo 24×24, trazo 2px, `currentColor`, separación icono-texto **8px**. Tamaños: **16** controles/navegación (`Plus`, `Minus`, `Trash`, `Check`, `ChevronRight`, `Lock`, `Truck` en badges) · **20** botones/inputs/header (`Menu2`, `ArrowLeft`, `ShoppingCart`, `Microphone`, `ArrowUp`, `Photo`, `Camera`, `Search`, `X`, `MessagePlus`, `History`, `Settings`) · **24** énfasis (checks éxito, correo). Interactivos siempre en botón con `aria-label` ("Ver carrito", "Agregar imagen", "Quitar…", etc.). Inventario: `Menu2, ArrowLeft, ArrowUp, ShoppingCart, Plus, Minus, Microphone, X, Search, MessagePlus, History, ChevronRight, Trash, Check, Mail, Lock, Settings, Photo, Camera, Truck, Refresh, FileAlert`.

---

## 9. Motion, foco y accesibilidad

- Clases: `.msg-in` (fade-up .25s), `.sheet` (sheet-up .3s `cubic-bezier(.32,.72,0,1)`), `.side-in` (slide-in-left .22s), `.fade-in` (.2s), `.pop/.wf-check` (.35s `cubic-bezier(.34,1.56,.64,1)`), `.tdot` typing 1.2s, `.inka-energy-bar` estática.
- Keyframes: `fade-up` (6px), `fade-in`, `sheet-up` (48px), `pop` (.6→1), `typing-dot` (−4px), `slideInLeft` (−40px).
- `prefers-reduced-motion: reduce` desactiva todo.
- Foco visible global: `outline: 3px solid signal + offset 2px`; inputs usan anillo `signal-soft`.
- A11y: `lang="es"`, `aria-label` en todos los icon-buttons/inputs, `aria-pressed` en color/talla, `role="group"` + `aria-labelledby="talla-label"`, `role="status" aria-live="polite"` en badges, `role="img" aria-label` en placeholders, `alt` en logos e imágenes, `tabular-nums` en cifras, `scrollTo top` al cambiar de pantalla, overlay cierra con click fuera + `stopPropagation` dentro.
- Utilidad `.no-scrollbar` (scroll interno sin barra en `main` y sheets).

---

## 10. Frame móvil y fondo exterior

`.wf-phone`: `width 100% / max 430px` centrado, alto dispositivo (`max(600px, min(880px, 100dvh-2rem))`), `radius 36px`, `overflow hidden`, columna flex, `bg cloud`, borde 2px negro + doble sombra. `body` (`min-h-full flex flex-col items-center py-4 px-3 font-sans`): fondo `#14100B` con halo volt y trama de puntos. `main` scrollea por dentro; header (`sticky top-0 z-20`) y composer/subtotal (`sticky bottom-0`) siempre anclados.

---

## 11. Privacidad, moneda y formatos

- Enmascarado (solo últimos 3–4 visibles): celular `+51 *****777` (`maskCelular`), DNI `*****234`, correo `c****@dominio` (`maskEmail`: 1ª letra + `****@dominio`), tarjeta `•••• 1111` (últimos 4).
- Moneda: `S/ {precio}.00` siempre con 2 decimales; cupón mock **−20%** (`Math.round(subtotal*.2)`); stepper 1–10 (`Math.min(10)` / `Math.max(1)`).
- Fechas demo: entrega `18 sep 2026`, entregado `2 sep 2026`, solicitud `10 sep 2026`; plazos: reclamo 15 días hábiles, cambio 7 días naturales, pago 15 min / 3 intentos.
- Evidencia: JPG/PNG/WEBP (chat) + PDF (devolución), **≤ 5 MB**.

---

## 12. DO / DON'T y reglas Tailwind v4

**DO:** H1/H2/H3 Oswald Bold mayúsculas · tokens `spacing/*` y `radius/*` (nada arbitrario) · `StatusBadge` icono+texto · `aria-label` en icon-buttons · `bg-action-primary text-surface-ink` en primarios · Server Components por defecto (`'use client'` solo con hooks/animación: `page.tsx`, `BrandLogo`) · helpers `.wf-*` en `@layer components`.
**DON'T:** Oswald en body/labels/aux · valores 7/13/19/27px o radios 10px · estado solo con color o con ember/naranja · click en icono suelto · hex hardcodeado en JSX · instalar Tailwind extra o crear `tailwind.config` (v4 = CSS-first) · precio grande naranja · `+` que agregue directo sin talla/color.
