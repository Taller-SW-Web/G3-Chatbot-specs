# Seguimiento del issue de scopes de Productos — Seguridad #33

## Resumen

La solicitud formal ya fue abierta en [Modulo-de-Seguridad #33](https://github.com/Taller-SW-Web/Modulo-de-Seguridad/issues/33) para registrar y conceder los scopes necesarios del módulo de Productos y Ofertas al canal Chatbot.

## Contexto

Actualizado el 2026-10-02: Seguridad respondió que la solicitud se acepta bajo la condición de que el PO de Productos confirme que los scopes de `x-required-scope` en `api/openapi.yaml` son su lista oficial. Cuando lo confirme, Seguridad los añadirá al catálogo con audiencia `api-productos` y los concederá a `modulo-chatbot`. El issue #33 continúa abierto; por ahora los scopes no están concedidos.

Este bloqueo afecta las capacidades del chatbot que usan:

- `catalogo:leer` para `GET /productos`, `GET /productos/{id}`, `GET /categorias`, `GET /marcas`
- `precios:leer` para `GET /precios` y `GET /precios/skus/{sku}`
- `promociones:leer` para `GET /promociones`
- `promociones:evaluar` para `POST /promociones/evaluar`
- `cupones:validar` para `POST /cupones/validar`
- `recomendaciones:leer` para `GET /recomendaciones`
- `inventario:disponibilidad:leer` para `GET /inventario/disponibilidad`

`productos:fisicos:leer` no se solicita para el chatbot: ese endpoint lo consume Despacho al calcular el peso y el volumen.

## Alcance solicitado

La petición solicita registrar los siete scopes con la audiencia `api-productos` y otorgarlos a `modulo-chatbot`, una vez que el PO de Productos confirme la lista.

## Requerimientos funcionales y de integración

- El chatbot debe poder consultar catálogo, detalle, marcas, categorías y filtros reales del módulo de Productos.
- El chatbot debe poder consultar precios y promociones por canal, con la semántica real del contrato (`precio_regular`, `precio_oferta`, `channel_id`, `lines`, `quantity`, `coupon_code`, `customer_ref`).
- El chatbot debe poder validar cupones sin consumirlos y evaluar promociones sobre una cesta real.
- El chatbot debe poder consultar disponibilidad por SKU para validar stock y evitar checkout con líneas no disponibles.
- El chatbot debe poder consultar recomendaciones; no consulta directamente los datos físicos usados por Despacho.

## Hito sugerido

- Hito: integración con Productos y Ofertas
- Etapa: preproducción / habilitación de capacidades
- Dependencia: cierre previo de `Modulo-de-Seguridad` para registrar scopes y audiencia

## Criterio de cierre

La integración se considera lista cuando:

1. el PO de Productos confirme que los siete scopes coinciden con `x-required-scope` en `api/openapi.yaml`,
2. todos esos scopes estén registrados y concedidos en Seguridad,
3. la audiencia `api-productos` quede autorizada para `modulo-chatbot`,
4. el chatbot pueda invocar las rutas reales de Productos sin depender de mocks ni de payloads provisionales.

## Impacto

- `busqueda-filtrado`
- `recomendacion`
- `ofertas-promociones`
- `tarjetas-detalle-producto`
- `validacion-stock`
- `gestion-carrito`
- `cupones`

## Estado del issue

Issue #33 abierto, con respuesta de Seguridad: aceptado condicionalmente a la confirmación del PO de Productos. No hay scopes concedidos todavía. La solicitud solo cubre los siete scopes de uso directo de Chatbot.
