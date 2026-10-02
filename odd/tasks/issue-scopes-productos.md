# Issue de seguridad — scopes faltantes de Productos para `modulo-chatbot`

## Resumen

Se requiere abrir una solicitud formal a `Modulo-de-Seguridad` para registrar y conceder los scopes necesarios del módulo de Productos y Ofertas para el canal Chatbot. El objetivo es habilitar la integración real del chatbot con el catálogo, precios, promociones, cupones, recomendaciones, inventario y datos físicos, sin depender de mocks ni de rutas provisionales.

## Contexto

La integración de Productos ya está resuelta en contenido, pero los scopes siguen marcados como `pending-security-registration` y no están concedidos a `modulo-chatbot`.

Este bloqueo afecta las capacidades del chatbot que usan:

- `catalogo:leer` para `GET /productos`, `GET /productos/{productoId}`, `GET /categorias`, `GET /marcas`
- `precios:leer` para `GET /precios` y `GET /precios/skus/{sku}`
- `promociones:leer` para `GET /promociones`
- `promociones:evaluar` para `POST /promociones/evaluar`
- `cupones:validar` para `POST /cupones/validar`
- `recomendaciones:leer` para `GET /recomendaciones`
- `inventario:disponibilidad:leer` para `GET /inventario/disponibilidad`
- `productos:fisicos:leer` para `POST /productos/datos-fisicos/consulta`

## Alcance solicitado

Se pide registrar los scopes con la audiencia `api-productos` y otorgarlos a `modulo-chatbot` con el mismo trato que se está gestionando para Despacho.

## Requerimientos funcionales y de integración

- El chatbot debe poder consultar catálogo, detalle, marcas, categorías y filtros reales del módulo de Productos.
- El chatbot debe poder consultar precios y promociones por canal, con la semántica real del contrato (`precio_regular`, `precio_oferta`, `channel_id`, `lines`, `quantity`, `coupon_code`, `customer_ref`).
- El chatbot debe poder validar cupones sin consumirlos y evaluar promociones sobre una cesta real.
- El chatbot debe poder consultar disponibilidad por SKU para validar stock y evitar checkout con líneas no disponibles.
- El chatbot debe poder consultar recomendaciones y datos físicos si el flujo de negocio los requiere.

## Hito sugerido

- Hito: integración con Productos y Ofertas
- Etapa: preproducción / habilitación de capacidades
- Dependencia: cierre previo de `Modulo-de-Seguridad` para registrar scopes y audiencia

## Criterio de cierre

La integración se considera lista cuando:

1. todos los scopes anteriores estén registrados en Seguridad,
2. la audiencia `api-productos` quede definida y autorizada para `modulo-chatbot`,
3. el chatbot pueda invocar las rutas reales de Productos sin depender de mocks ni de payloads provisionales.

## Impacto

- `busqueda-filtrado`
- `recomendacion`
- `ofertas-promociones`
- `tarjetas-detalle-producto`
- `validacion-stock`
- `gestion-carrito`
- `cupones`
- `direccion-cotizacion-envio` (solo por compatibilidad con los datos físicos que Despacho consulta)

## Nota

Este documento es un borrador formal para entrega a Seguridad; no se ejecuta ni se abre un issue externo en el repositorio del módulo de Seguridad dentro de esta tarea.
