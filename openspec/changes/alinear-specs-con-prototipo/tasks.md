# Tasks

## 1. Contrato de navegación y cuenta

- [x] 1.1 Añadir el requisito 7 de "Mi cuenta" a la delta de SPEC-03.
- [x] 1.2 Modificar el requisito 3 de SPEC-04 para iniciar OTP desde `AccountPage` sin salir de la pantalla.
- [x] 1.3 Modificar el requisito 1 de SPEC-05 y añadir sus escenarios de `SearchChatsPage` e historial lateral.
- [x] 1.4 Actualizar diseño de SPEC-03, SPEC-05 y SPEC-17 con rutas y navegación pendientes.

## 2. Acciones y pantallas de consulta

- [x] 2.1 Modificar el requisito 2 de SPEC-05 para incluir las acciones rápidas fijas en Inicio.
- [x] 2.2 Añadir los requisitos 13 y 14 de SPEC-05 para "Preguntar en el chat" y acciones rápidas fijas.
- [x] 2.3 Actualizar los diseños de SPEC-17, SPEC-18, SPEC-20 y SPEC-22 con "Preguntar en el chat".

## 3. Cámara y checkout

- [x] 3.1 Modificar el requisito 1 de SPEC-23 con Galería/Tomar foto, selector nativo y validaciones compartidas.
- [x] 3.2 Modificar el requisito 1 de SPEC-12 con la nota fija sobre el documento del comprobante.
- [x] 3.3 Actualizar privacidad y diseño de adjuntos y checkout; conservar separación entre imágenes del chat y evidencia de Ventas.

## 4. Documentación transversal de producto

- [x] 4.1 Actualizar README §2 y referencias de navegación en alcance, flujos y diseños.
- [x] 4.2 Añadir historias de usuario para Mi cuenta, Preguntar en el chat y acciones rápidas; actualizar historias de búsqueda, cámara, documento y tarjetas relacionadas.
- [x] 4.3 Actualizar reglas, trazabilidad, intenciones y microcopy canónico.
- [x] 4.4 Actualizar contratos de `GET /sesion/perfil` y acciones directas; documentar en modelo de datos que no se requieren tablas nuevas.
- [x] 4.5 Recalcular requisitos, escenarios, historias, puntos y reglas desde los documentos resultantes.

## 5. Verificación

- [x] 5.1 Ejecutar `npx @fission-ai/openspec validate --specs --strict` y validar el change id.
- [ ] 5.2 Al archivar, aplicar los reemplazos a los diseños base que aún describen la búsqueda como campo de Sidebar, `SesionIndicator` en la cabecera y el botón como "Adjuntar".
- [x] 5.3 Revisar español neutro, trazabilidad de los nuevos requisitos y conteos publicados.