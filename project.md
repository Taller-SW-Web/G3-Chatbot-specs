# Project.md — Marketplace Multicanal de Productos Deportivos

## Contexto general
Proyecto del curso Taller de Construcción de Software Web (UNMSM, Ciclo 2026-II). Consiste en desarrollar un **Marketplace Multicanal** para una empresa de productos deportivos (camisetas, accesorios para distintos deportes), construido como un **sistema modular integrado por APIs**, con arquitectura de microservicios y desarrollo asistido por IA (SDD).

Este documento cubre el **Canal Chatbot** (atención al cliente vía conversación en lenguaje natural), uno de los 7 módulos del proyecto general:
- a. Canal Marketplace (cliente, web)
- b. **Canal Chatbot (cliente, conversacional)** ← módulo cubierto por estas specs
- c. Canal Retail (vendedor, en tienda)
- d. Módulo de ventas y postventa
- e. Módulo de despacho y entrega a domicilio
- f. Módulo de productos y ofertas
- g. Módulo de seguridad y autenticación de usuarios

## Requisitos técnicos y arquitectónicos del curso
- Arquitectura de microservicios; cada módulo tiene su propio frontend y backend.
- Integración entre módulos **únicamente vía APIs asíncronas** — sin acceso directo a bases de datos ajenas.
- Diseño de interfaz en Figma; frontend en React; backend en Java SpringBoot, .NET Core o Node.js; base de datos relacional (MySQL/PostgreSQL).
- Autenticación y desarrollo seguro obligatorios en todos los componentes.
- Despliegue en nube, con CI/CD e pruebas unitarias/integración/performance en hitos posteriores del curso.

## Propiedad de entidades (dueños de datos)
El Canal Chatbot **no es dueño de ninguna entidad de negocio**; siempre consume APIs de los módulos dueños:

| Entidad | Módulo dueño |
|---|---|
| Usuario (cliente/vendedor) | Módulo de seguridad y autenticación de usuarios |
| Pedido | Módulo de ventas y postventa |
| Producto (incluye stock) | Módulo de productos y ofertas |
| Despacho | Módulo de despacho y entrega |

## Matriz de integración del Canal Chatbot
El Chatbot Cliente tiene permitido integrarse (vía API asíncrona) con:
- Módulo de ventas y postventa (Sí)
- Módulo de despacho y entrega (Sí)
- Módulo de productos y ofertas (Sí)
- Módulo de seguridad y usuarios (Sí)

No tiene integración directa con Marketplace Cliente ni con Retail Vendedor (no aplica).

## Capacidades del Canal Chatbot (mapeadas a specs/)
1. `consulta-recomendacion-conversacional` — búsqueda conversacional, filtros, recomendaciones, ofertas.
2. `gestion-carrito-checkout-conversacional` — carrito, validación de formato de contacto, pago simulado.
3. `seguimiento-notificaciones-pedido` — notificación de confirmación por correo, consulta de estado de pedido.
4. `validacion-identidad-usuario` — verificación de existencia del cliente contra el sistema central de Seguridad.
5. `validacion-disponibilidad-stock` — verificación de stock en tiempo real antes de agregar al carrito.

## Reglas de diseño transversales
- Toda comunicación con otros módulos es **asíncrona, vía API**, nunca acceso directo a BD.
- Todo dato de tarjeta/contacto viaja encriptado (desarrollo seguro por defecto).
- El Chatbot puede registrar clientes temporalmente como "invitados" cuando aún no existen en Seguridad, pero la verificación final de identidad siempre es responsabilidad del Módulo de Seguridad.
- Las specs de este módulo no gestionan roles, contraseñas, devoluciones, reembolsos, ni actualización de catálogo/stock — esas responsabilidades pertenecen a otros módulos y están explícitamente fuera de alcance en cada spec.
