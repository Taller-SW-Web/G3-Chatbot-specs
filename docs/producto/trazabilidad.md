# Trazabilidad — Canal Chatbot

> Une las historias (`HU`) con las specs, las reglas de negocio, los endpoints, los hitos y las prioridades. Las tablas de las secciones 2 a 4 se derivan de los archivos de [`historias/`](historias/) y de los `spec.md`; si se edita una historia, hay que regenerarlas o actualizarlas a mano.

## 1. Convenciones de identificadores

| ID | Formato | Ejemplo | Dónde se define |
|---|---|---|---|
| Épica | `EP-NN` (dos dígitos) | `EP-04` | [`epicas.md`](epicas.md) |
| Historia | `HU-<ÁREA>-NN`, con el área de 3 letras de su épica | `HU-CAR-05` | [`historias/`](historias/) |
| Regla de negocio | `RN-<ÁREA>-NN`, con la misma área | `RN-CAR-07` | [`reglas-negocio.md`](reglas-negocio.md) |
| Requisito de spec | `SPEC-NN · Req. N`: el N-ésimo `### Requirement:` del `spec.md` de la spec `SPEC-NN` (índice en el README §3). Un rango se escribe `Req. 2–3`. | `SPEC-11 · Req. 1` | `openspec/specs/<capacidad>/spec.md` |
| Escenario | `SPEC-NN · Req. N · Scenario: <nombre exacto>` | `SPEC-11 · Req. 1 · Scenario: Límite por línea` | ídem (`#### Scenario:`) |
| Tarea de desglose | `SPEC-NN · Tn`: la n-ésima tarea del "Desglose para issues" del `design.md` | `SPEC-14 · T5` | `openspec/specs/<capacidad>/design.md` |
| Acuerdo de integración | `A1` … `A14` (✅ resuelto, 🟡 abierto) | `A5` 🟡 | [`contratos-integracion.md` §6](../contratos-integracion.md#6-acuerdos-pendientes-llevar-a-la-sincronización-de-líderes) |

Áreas: `IDE` Identidad · `CNV` Conversación · `CAT` Catálogo y descubrimiento · `CAR` Carrito · `CHK` Checkout · `PED` Pedido · `SGT` Seguimiento · `RCL` Reclamos · `DEV` Devoluciones.

Módulos en la columna de endpoints consumidos: `SEG` Seguridad (`{SEG}/api/v1`), `PRO` Productos (`{PRO}/api/v1`, 🟡 provisional), `VEN` Ventas, `DES` Despacho (`{DES}/api/v1`). Los endpoints expuestos son del backend del chatbot, con prefijo `/api/v1`.

## 2. Matriz de trazabilidad

| HU | Título | SPEC / Req. | Reglas de negocio | Endpoint expuesto (chatbot) | Endpoint consumido | Hito | Prioridad | Pts |
|---|---|---|---|---|---|---|---|---|
| [HU-IDE-01](historias/EP-01-identidad-sesion.md#hu-ide-01--abrir-el-formulario-de-registro-desde-el-chat) | Abrir el formulario de registro desde el chat | `SPEC-01 · Req. 1` | RN-IDE-15 | `POST /chat/conversaciones/{id}/mensajes` (herramienta `solicitar_registro`) | — | Hito 3 | Must | 3 |
| [HU-IDE-02](historias/EP-01-identidad-sesion.md#hu-ide-02--crear-mi-cuenta-con-validación-inmediata) | Crear mi cuenta con validación inmediata | `SPEC-01 · Req. 2–3` | RN-IDE-01, RN-IDE-02, RN-IDE-03, RN-IDE-04, RN-IDE-05, RN-IDE-06 | `POST /sesion/registro`, `GET /sesion/politica-contrasena` | SEG `POST /auth/registro`, `GET /password/politica` | Hito 3 | Must | 5 |
| [HU-IDE-03](historias/EP-01-identidad-sesion.md#hu-ide-03--recibir-mensajes-claros-ante-errores-del-registro) | Recibir mensajes claros ante errores del registro | `SPEC-01 · Req. 4` | RN-IDE-07 | `POST /sesion/registro` | SEG `POST /auth/registro` | Hito 3 | Must | 3 |
| [HU-IDE-04](historias/EP-01-identidad-sesion.md#hu-ide-04--activar-mi-cuenta-desde-el-enlace-de-verificación) | Activar mi cuenta desde el enlace de verificación | `SPEC-02 · Req. 1` | RN-IDE-08 | `POST /sesion/verificar-correo` | SEG `POST /auth/verificar-correo` | Hito 3 | Must | 3 |
| [HU-IDE-05](historias/EP-01-identidad-sesion.md#hu-ide-05--pedir-un-nuevo-enlace-de-verificación) | Pedir un nuevo enlace de verificación | `SPEC-02 · Req. 2–3` | RN-IDE-07, RN-IDE-09, RN-IDE-10 | `POST /sesion/verificar-correo/reenviar` | SEG `POST /auth/verificar-correo/reenviar` | Hito 3 | Must | 3 |
| [HU-IDE-06](historias/EP-01-identidad-sesion.md#hu-ide-06--iniciar-sesión-con-correo-y-contraseña) | Iniciar sesión con correo y contraseña | `SPEC-03 · Req. 1` | RN-IDE-10, RN-IDE-11, RN-IDE-13, RN-IDE-18 | `POST /sesion/login`, `GET /sesion/perfil` | SEG `POST /auth/login`, `POST /auth/logout`, `GET /auth/me` | Hito 3 | Must | 5 |
| [HU-IDE-07](historias/EP-01-identidad-sesion.md#hu-ide-07--completar-el-inicio-de-sesión-con-segundo-factor) | Completar el inicio de sesión con segundo factor | `SPEC-03 · Req. 2` | RN-IDE-12 | `POST /sesion/mfa/solicitar`, `POST /sesion/mfa/verificar` | SEG `POST /auth/otp/solicitar`, `POST /auth/otp/verificar` | Hito 3 | Must | 5 |
| [HU-IDE-08](historias/EP-01-identidad-sesion.md#hu-ide-08--retomar-lo-que-estaba-haciendo-tras-iniciar-sesión) | Retomar lo que estaba haciendo tras iniciar sesión | `SPEC-03 · Req. 3` | RN-IDE-15 | `POST /sesion/login` (post-login) | — | Hito 3 | Must | 3 |
| [HU-IDE-09](historias/EP-01-identidad-sesion.md#hu-ide-09--conservar-mi-carrito-anónimo-al-iniciar-sesión) | Conservar mi carrito anónimo al iniciar sesión | `SPEC-03 · Req. 4` | RN-IDE-16, RN-CAR-01, RN-CAR-07 | `POST /sesion/login` (post-login), `GET /carrito` | PRO `GET /inventario/disponibilidad` 🟡 | Hito 3 | Must | 3 |
| [HU-IDE-10](historias/EP-01-identidad-sesion.md#hu-ide-10--mantener-mi-sesión-activa-de-forma-segura) | Mantener mi sesión activa de forma segura | `SPEC-03 · Req. 5` | RN-IDE-13, RN-IDE-14 | `POST /sesion/refresh` | SEG `POST /auth/refresh`, `GET /auth/.well-known/jwks.json` | Hito 3 | Must | 5 |
| [HU-IDE-11](historias/EP-01-identidad-sesion.md#hu-ide-11--cerrar-sesión) | Cerrar sesión | `SPEC-03 · Req. 6` | RN-IDE-17 | `POST /sesion/logout` | SEG `POST /auth/logout` | Hito 3 | Must | 2 |
| [HU-IDE-12](historias/EP-01-identidad-sesion.md#hu-ide-12--verificar-mi-celular-antes-del-primer-pago) | Verificar mi celular antes del primer pago | `SPEC-04 · Req. 1` | RN-IDE-19 | `POST /checkout` (`403 CELULAR_NO_VERIFICADO`) | SEG `GET /auth/me` | Hito 4 | Must | 3 |
| [HU-IDE-13](historias/EP-01-identidad-sesion.md#hu-ide-13--recibir-y-validar-el-código-de-mi-celular) | Recibir y validar el código de mi celular | `SPEC-04 · Req. 2` | RN-IDE-20 | `POST /contacto/celular/solicitar-otp`, `POST /contacto/celular/verificar-otp` | — (SMS simulado propio) | Hito 4 | Must | 5 |
| [HU-IDE-14](historias/EP-01-identidad-sesion.md#hu-ide-14--recibir-orientación-si-el-celular-no-es-el-mío-o-verificarlo-por-iniciativa-propia) | Recibir orientación si el celular no es el mío o verificarlo por iniciativa propia | `SPEC-04 · Req. 3` | RN-IDE-21 | `POST /chat/conversaciones/{id}/mensajes` (herramienta `verificar_celular`) | SEG `GET /auth/me` | Hito 4 | Should | 2 |
| [HU-CNV-01](historias/EP-02-conversacion.md#hu-cnv-01--iniciar-conversaciones-nuevas-y-retomar-las-anteriores) | Iniciar conversaciones nuevas y retomar las anteriores | `SPEC-05 · Req. 1` (escenarios 1, 2, 4 y 5) | RN-CNV-01, RN-CNV-02, RN-CNV-03 | `POST /chat/conversaciones`, `GET /chat/conversaciones`, `GET /chat/conversaciones/{id}/mensajes` | — | Hito 3 | Must | 5 |
| [HU-CNV-02](historias/EP-02-conversacion.md#hu-cnv-02--buscar-entre-mis-conversaciones) | Buscar entre mis conversaciones | `SPEC-05 · Req. 1` (escenario 3) | — | `GET /chat/conversaciones/buscar` | — | Hito 3 | Should | 2 |
| [HU-CNV-03](historias/EP-02-conversacion.md#hu-cnv-03--ver-ofertas-y-empezar-a-conversar-desde-la-pantalla-de-inicio) | Ver ofertas y empezar a conversar desde la pantalla de inicio | `SPEC-05 · Req. 2` | RN-CNV-04 | `POST /chat/conversaciones`, `GET /catalogo/promociones`, `GET /catalogo/productos?soloOfertas=true` | PRO `GET /promociones`, `GET /productos` 🟡 | Hito 3 | Must | 5 |
| [HU-CNV-04](historias/EP-02-conversacion.md#hu-cnv-04--pedir-lo-que-necesito-en-lenguaje-natural) | Pedir lo que necesito en lenguaje natural | `SPEC-05 · Req. 3` | RN-CNV-05, RN-CNV-06 | `POST /chat/conversaciones/{id}/mensajes` | Proveedor LLM | Hito 3 | Must | 8 |
| [HU-CNV-05](historias/EP-02-conversacion.md#hu-cnv-05--ver-la-respuesta-del-asistente-en-tiempo-real) | Ver la respuesta del asistente en tiempo real | `SPEC-05 · Req. 4` | RN-CNV-07 | `POST /chat/conversaciones/{id}/mensajes`, WS `/chat/ws`, `GET /chat/conversaciones/{id}/mensajes?desde=` | Proveedor LLM (streaming) | Hito 3 | Must | 8 |
| [HU-CNV-06](historias/EP-02-conversacion.md#hu-cnv-06--referirme-a-productos-mostrados-antes) | Referirme a productos mostrados antes | `SPEC-05 · Req. 5` | RN-CNV-08 | `POST /chat/conversaciones/{id}/mensajes` | Proveedor LLM | Hito 3 | Must | 3 |
| [HU-CNV-07](historias/EP-02-conversacion.md#hu-cnv-07--ejecutar-herramientas-de-forma-segura-habilitadora) | Ejecutar herramientas de forma segura (Habilitadora) | `SPEC-05 · Req. 6` | RN-CNV-09, RN-CNV-10, RN-CNV-11 | `POST /chat/conversaciones/{id}/mensajes` | Proveedor LLM | Hito 3 | Must | 5 |
| [HU-CNV-08](historias/EP-02-conversacion.md#hu-cnv-08--recibir-solo-datos-comerciales-verídicos) | Recibir solo datos comerciales verídicos | `SPEC-05 · Req. 7` | RN-CNV-12 | WS `/chat/ws` (evento `fin`) | Proveedor LLM | Hito 3 | Must | 5 |
| [HU-CNV-09](historias/EP-02-conversacion.md#hu-cnv-09--usar-botones-de-acción-rápida-sin-esperar-al-asistente) | Usar botones de acción rápida sin esperar al asistente | `SPEC-05 · Req. 8` | RN-CNV-13 | `POST /chat/conversaciones/{id}/mensajes` (`accion`) | — | Hito 3 | Must | 3 |
| [HU-CNV-10](historias/EP-02-conversacion.md#hu-cnv-10--proteger-mis-datos-sensibles-y-resistir-instrucciones-maliciosas) | Proteger mis datos sensibles y resistir instrucciones maliciosas | `SPEC-05 · Req. 9` | RN-CNV-14, RN-CNV-15 | `POST /chat/conversaciones/{id}/mensajes` | Proveedor LLM | Hito 3 | Must | 5 |
| [HU-CNV-11](historias/EP-02-conversacion.md#hu-cnv-11--seguir-comprando-aunque-el-asistente-falle) | Seguir comprando aunque el asistente falle | `SPEC-05 · Req. 10` | RN-CNV-16 | `POST /chat/conversaciones/{id}/mensajes` (respuesta REST) | PRO `GET /productos` 🟡 | Hito 3 | Should | 5 |
| [HU-CNV-12](historias/EP-02-conversacion.md#hu-cnv-12--limitar-el-uso-para-proteger-el-servicio-habilitadora) | Limitar el uso para proteger el servicio (Habilitadora) | `SPEC-05 · Req. 11` | RN-CNV-17, RN-CNV-18 | `POST /chat/conversaciones/{id}/mensajes`, `POST /chat/conversaciones` (`429`) | — | Hito 3 | Should | 3 |
| [HU-CNV-13](historias/EP-02-conversacion.md#hu-cnv-13--saber-que-converso-con-un-asistente-virtual-y-cómo-se-usan-mis-datos) | Saber que converso con un asistente virtual y cómo se usan mis datos | `SPEC-05 · Req. 12` | RN-CNV-19, RN-CNV-20, RN-CNV-21 | `POST /chat/conversaciones/{id}/mensajes` | Proveedor LLM | Hito 3 | Must | 3 |
| [HU-CAT-01](historias/EP-03-descubrimiento.md#hu-cat-01--buscar-productos-combinando-filtros) | Buscar productos combinando filtros | `SPEC-06 · Req. 1` | RN-CAT-01, RN-CAT-02, RN-CAT-05 | `GET /catalogo/productos` | PRO `GET /productos`, `GET /precios` 🟡 | Hito 3 | Must | 5 |
| [HU-CAT-02](historias/EP-03-descubrimiento.md#hu-cat-02--ser-entendido-aunque-use-sinónimos-o-escriba-mal-la-marca) | Ser entendido aunque use sinónimos o escriba mal la marca | `SPEC-06 · Req. 2` | RN-CAT-03, RN-CAT-04 | `GET /catalogo/productos` | PRO `GET /categorias`, `GET /marcas` 🟡 | Hito 3 | Must | 5 |
| [HU-CAT-03](historias/EP-03-descubrimiento.md#hu-cat-03--refinar-la-búsqueda-conversando-o-con-chips) | Refinar la búsqueda conversando o con chips | `SPEC-06 · Req. 3` | — | `GET /catalogo/productos` | PRO `GET /productos` 🟡 | Hito 3 | Should | 5 |
| [HU-CAT-04](historias/EP-03-descubrimiento.md#hu-cat-04--ver-más-resultados-o-sugerencias-si-no-hay-coincidencias) | Ver más resultados o sugerencias si no hay coincidencias | `SPEC-06 · Req. 4` | RN-CAT-05 | `GET /catalogo/productos` (`pagina`) | PRO `GET /productos` 🟡 | Hito 3 | Must | 3 |
| [HU-CAT-05](historias/EP-03-descubrimiento.md#hu-cat-05--saber-cuándo-el-catálogo-no-está-disponible) | Saber cuándo el catálogo no está disponible | `SPEC-06 · Req. 5` | RN-CAT-06, RN-CAT-07 | `GET /catalogo/productos` | PRO `GET /productos`, `GET /categorias`, `GET /marcas` 🟡 | Hito 3 | Must | 2 |
| [HU-CAT-06](historias/EP-03-descubrimiento.md#hu-cat-06--recibir-recomendaciones-según-mi-necesidad) | Recibir recomendaciones según mi necesidad | `SPEC-07 · Req. 1` | RN-CAT-08, RN-CAT-09 | `POST /chat/conversaciones/{id}/mensajes` (herramienta `recomendar_productos`) | PRO `GET /productos`, `GET /inventario/disponibilidad` 🟡 | Hito 4 | Must | 5 |
| [HU-CAT-07](historias/EP-03-descubrimiento.md#hu-cat-07--recibir-solo-recomendaciones-disponibles-y-veraces) | Recibir solo recomendaciones disponibles y veraces | `SPEC-07 · Req. 2` | RN-CAT-08 | `POST /chat/conversaciones/{id}/mensajes` | PRO `GET /inventario/disponibilidad` 🟡 | Hito 4 | Must | 3 |
| [HU-CAT-08](historias/EP-03-descubrimiento.md#hu-cat-08--recibir-sugerencias-de-complementos) | Recibir sugerencias de complementos | `SPEC-07 · Req. 3` | RN-CAT-10 | `POST /carrito/items` | PRO `GET /recomendaciones/candidatos` 🟡 | Hito 4 | Should | 5 |
| [HU-CAT-09](historias/EP-03-descubrimiento.md#hu-cat-09--consultar-las-promociones-vigentes-del-canal) | Consultar las promociones vigentes del canal | `SPEC-08 · Req. 1` | RN-CAT-11 | `GET /catalogo/promociones` | PRO `GET /promociones` 🟡 | Hito 4 | Must | 3 |
| [HU-CAT-10](historias/EP-03-descubrimiento.md#hu-cat-10--ver-el-precio-de-oferta-en-tarjetas-y-detalle) | Ver el precio de oferta en tarjetas y detalle | `SPEC-08 · Req. 2` | RN-CAT-12 | `GET /catalogo/productos/{productoId}` | PRO `GET /precios` 🟡 | Hito 4 | Must | 3 |
| [HU-CAT-11](historias/EP-03-descubrimiento.md#hu-cat-11--entender-los-descuentos-aplicados-en-mi-carrito) | Entender los descuentos aplicados en mi carrito | `SPEC-08 · Req. 3` | RN-CAT-13 | `GET /carrito` | PRO `POST /promociones/evaluar` 🟡 | Hito 4 | Must | 3 |
| [HU-CAT-12](historias/EP-03-descubrimiento.md#hu-cat-12--no-recibir-códigos-de-cupón-en-la-consulta-de-ofertas) | No recibir códigos de cupón en la consulta de ofertas | `SPEC-08 · Req. 4` | RN-CAT-14 | `GET /catalogo/promociones` | PRO `GET /promociones` 🟡 | Hito 4 | Should | 1 |
| [HU-CAT-13](historias/EP-03-descubrimiento.md#hu-cat-13--ver-productos-en-un-carrusel-de-tarjetas) | Ver productos en un carrusel de tarjetas | `SPEC-09 · Req. 1` | RN-CAT-15 | `GET /catalogo/productos` | PRO `GET /productos`, `GET /inventario/disponibilidad` 🟡 | Hito 3 | Must | 5 |
| [HU-CAT-14](historias/EP-03-descubrimiento.md#hu-cat-14--agregar-desde-la-tarjeta-eligiendo-la-variante) | Agregar desde la tarjeta eligiendo la variante | `SPEC-09 · Req. 2` | RN-CAT-16 | `POST /carrito/items`, `GET /catalogo/productos/{productoId}` | PRO `GET /productos/{id}` 🟡 | Hito 3 | Must | 3 |
| [HU-CAT-15](historias/EP-03-descubrimiento.md#hu-cat-15--ver-el-detalle-de-un-producto) | Ver el detalle de un producto | `SPEC-09 · Req. 3` | RN-CAT-17 | `GET /catalogo/productos/{productoId}` | PRO `GET /productos/{id}`, `GET /precios`, `GET /inventario/disponibilidad` 🟡 | Hito 3 | Must | 5 |
| [HU-CAT-16](historias/EP-03-descubrimiento.md#hu-cat-16--elegir-talla-y-color-escribiendo) | Elegir talla y color escribiendo | `SPEC-09 · Req. 4` | RN-CAT-16 | `POST /chat/conversaciones/{id}/mensajes` (herramienta `ver_detalle_producto`) | PRO `GET /productos/{id}`, `GET /inventario/disponibilidad` 🟡 | Hito 3 | Must | 5 |
| [HU-CAR-01](historias/EP-04-carrito.md#hu-car-01--agregar-solo-cantidades-disponibles) | Agregar solo cantidades disponibles | `SPEC-10 · Req. 1` | RN-CAR-01, RN-CAR-02 | `POST /carrito/items`, `GET /catalogo/disponibilidad` | PRO `GET /inventario/disponibilidad` 🟡 | Hito 3 | Must | 5 |
| [HU-CAR-02](historias/EP-04-carrito.md#hu-car-02--revalidar-el-stock-de-todo-el-carrito-antes-de-pagar) | Revalidar el stock de todo el carrito antes de pagar | `SPEC-10 · Req. 2` | RN-CAR-03, RN-CAR-06 | `POST /checkout` (`409 CARRITO_DESACTUALIZADO`) | PRO `GET /inventario/disponibilidad?skus=` 🟡; VEN `POST /api/v1/pedidos` (`409`) | Hito 3 | Must | 5 |
| [HU-CAR-03](historias/EP-04-carrito.md#hu-car-03--nunca-agregar-sin-confirmar-el-stock) | Nunca agregar sin confirmar el stock | `SPEC-10 · Req. 3` | RN-CAR-04 | `POST /carrito/items` (`503`) | PRO `GET /inventario/disponibilidad` 🟡 | Hito 3 | Must | 2 |
| [HU-CAR-04](historias/EP-04-carrito.md#hu-car-04--preguntar-por-la-disponibilidad-de-una-talla) | Preguntar por la disponibilidad de una talla | `SPEC-10 · Req. 4` | RN-CAR-05 | `GET /catalogo/disponibilidad` | PRO `GET /inventario/disponibilidad` 🟡 | Hito 3 | Should | 3 |
| [HU-CAR-05](historias/EP-04-carrito.md#hu-car-05--agregar-productos-al-carrito-conversando) | Agregar productos al carrito conversando | `SPEC-11 · Req. 1` | RN-CAR-07, RN-CAR-08, RN-CAR-09 | `POST /carrito/items`, `GET /carrito` | PRO `GET /inventario/disponibilidad` 🟡 | Hito 3 | Must | 5 |
| [HU-CAR-06](historias/EP-04-carrito.md#hu-car-06--cambiar-cantidades-y-quitar-productos) | Cambiar cantidades y quitar productos | `SPEC-11 · Req. 2` | RN-CAR-10, RN-CAR-11 | `PATCH /carrito/items/{itemId}`, `DELETE /carrito/items/{itemId}`, `DELETE /carrito` | — | Hito 3 | Must | 5 |
| [HU-CAR-07](historias/EP-04-carrito.md#hu-car-07--ver-mi-carrito-con-totales-actualizados) | Ver mi carrito con totales actualizados | `SPEC-11 · Req. 3` | RN-CAR-12, RN-CAR-13, RN-CAR-14 | `GET /carrito` | PRO `GET /precios`, `POST /promociones/evaluar` 🟡 | Hito 3 | Must | 8 |
| [HU-CAR-08](historias/EP-04-carrito.md#hu-car-08--recuperar-mi-carrito-en-otra-sesión-o-dispositivo) | Recuperar mi carrito en otra sesión o dispositivo | `SPEC-11 · Req. 4` | RN-CAR-15, RN-CAR-16 | `GET /carrito` | — | Hito 3 | Must | 3 |
| [HU-CHK-01](historias/EP-05-checkout-pago.md#hu-chk-01--ingresar-mi-documento-de-identidad-al-pagar) | Ingresar mi documento de identidad al pagar | `SPEC-12 · Req. 1` | RN-CHK-01, RN-CHK-02 | `POST /checkout` (snapshot `contacto`) | VEN `POST /api/v1/pedidos` (`400 DATO_INVALIDO`) | Hito 4 | Must | 5 |
| [HU-CHK-02](historias/EP-05-checkout-pago.md#hu-chk-02--ingresar-o-reutilizar-mi-dirección-de-entrega) | Ingresar o reutilizar mi dirección de entrega | `SPEC-12 · Req. 2` | RN-CHK-03 | `GET /direcciones` | SEG `GET /usuarios/{id}/direcciones` | Hito 4 | Must | 3 |
| [HU-CHK-03](historias/EP-05-checkout-pago.md#hu-chk-03--guardar-mi-dirección-para-la-próxima-compra) | Guardar mi dirección para la próxima compra | `SPEC-12 · Req. 3` | RN-CHK-04 | `POST /checkout` | SEG `POST /usuarios/{id}/direcciones` | Hito 4 | Should | 2 |
| [HU-CHK-04](historias/EP-05-checkout-pago.md#hu-chk-04--conocer-el-costo-y-el-plazo-del-envío-antes-de-pagar) | Conocer el costo y el plazo del envío antes de pagar | `SPEC-12 · Req. 4` | RN-CHK-05, RN-CHK-06, RN-CHK-07, RN-CHK-08 | `POST /envio/cotizar` | DES `POST /zonas/cotizar` (🟡 A12); PRO peso por SKU 🟡 (A6) | Hito 4 | Must | 8 |
| [HU-CHK-05](historias/EP-05-checkout-pago.md#hu-chk-05--mantener-vigente-la-cotización-de-envío) | Mantener vigente la cotización de envío | `SPEC-12 · Req. 5` | RN-CHK-09 | `POST /envio/cotizar`, `POST /checkout` | DES `POST /zonas/cotizar` | Hito 4 | Must | 3 |
| [HU-CHK-06](historias/EP-05-checkout-pago.md#hu-chk-06--aplicar-un-cupón-de-descuento) | Aplicar un cupón de descuento | `SPEC-13 · Req. 1` | RN-CHK-10, RN-CHK-11, RN-CHK-12 | `POST /carrito/cupon`, `DELETE /carrito/cupon` | PRO `POST /cupones/validar`, `POST /promociones/evaluar` 🟡 | Hito 4 | Must | 5 |
| [HU-CHK-07](historias/EP-05-checkout-pago.md#hu-chk-07--entender-por-qué-mi-cupón-fue-rechazado) | Entender por qué mi cupón fue rechazado | `SPEC-13 · Req. 2` | RN-CHK-13 | `POST /carrito/cupon` (`422 CUPON_INVALIDO`) | PRO `POST /cupones/validar` 🟡 | Hito 4 | Must | 3 |
| [HU-CHK-08](historias/EP-05-checkout-pago.md#hu-chk-08--aplicar-cupones-solo-con-sesión-iniciada) | Aplicar cupones solo con sesión iniciada | `SPEC-13 · Req. 3` | RN-CHK-14 | `POST /carrito/cupon` (`401 REQUIERE_SESION`) | — | Hito 4 | Must | 2 |
| [HU-CHK-09](historias/EP-05-checkout-pago.md#hu-chk-09--revalidar-el-cupón-cuando-cambia-el-carrito) | Revalidar el cupón cuando cambia el carrito | `SPEC-13 · Req. 4` | RN-CHK-15 | `GET /carrito`, `POST /checkout` | PRO `POST /cupones/validar` 🟡 | Hito 4 | Must | 3 |
| [HU-CHK-10](historias/EP-05-checkout-pago.md#hu-chk-10--proteger-los-cupones-contra-fuerza-bruta-habilitadora) | Proteger los cupones contra fuerza bruta (Habilitadora) | `SPEC-13 · Req. 5` | RN-CHK-16 | `POST /carrito/cupon` (`429`) | — | Hito 4 | Should | 2 |
| [HU-CHK-11](historias/EP-05-checkout-pago.md#hu-chk-11--iniciar-el-pago-con-las-precondiciones-resueltas) | Iniciar el pago con las precondiciones resueltas | `SPEC-14 · Req. 1` | RN-CHK-17 | `POST /checkout` (guardas), herramienta `iniciar_checkout` | — | Hito 4 | Must | 5 |
| [HU-CHK-12](historias/EP-05-checkout-pago.md#hu-chk-12--confirmar-el-resumen-y-registrar-mi-pedido) | Confirmar el resumen y registrar mi pedido | `SPEC-14 · Req. 2` | RN-CHK-18, RN-CHK-19 | `POST /checkout`, `GET /checkout/{checkoutId}` | VEN `POST /api/v1/pedidos`; PRO revalidación 🟡 | Hito 4 | Must | 5 |
| [HU-CHK-13](historias/EP-05-checkout-pago.md#hu-chk-13--ingresar-mi-tarjeta-en-un-formulario-seguro) | Ingresar mi tarjeta en un formulario seguro | `SPEC-14 · Req. 3` | RN-CHK-20, RN-CHK-21, RN-CHK-22 | `POST /checkout/{checkoutId}/pago` | — | Hito 4 | Must | 5 |
| [HU-CHK-14](historias/EP-05-checkout-pago.md#hu-chk-14--validar-mi-sesión-justo-antes-de-cobrar) | Validar mi sesión justo antes de cobrar | `SPEC-14 · Req. 4` | RN-CHK-23 | `POST /checkout/{checkoutId}/pago` | SEG `POST /auth/introspeccion`, `POST /auth/token` | Hito 4 | Must | 3 |
| [HU-CHK-15](historias/EP-05-checkout-pago.md#hu-chk-15--pagar-con-tarjeta-simulada) | Pagar con tarjeta simulada | `SPEC-14 · Req. 5` | RN-CHK-19, RN-CHK-24, RN-CHK-25 | `POST /checkout/{checkoutId}/pago` | — (simulador propio) | Hito 4 | Must | 8 |
| [HU-CHK-16](historias/EP-05-checkout-pago.md#hu-chk-16--expirar-el-checkout-no-pagado) | Expirar el checkout no pagado | `SPEC-14 · Req. 6` | RN-CHK-26 | `POST /checkout/{checkoutId}/pago` (`410`) | VEN `POST /api/v1/pedidos/{id}/anulaciones` | Hito 4 | Must | 3 |
| [HU-PED-01](historias/EP-06-pedido-confirmacion.md#hu-ped-01--registrar-mi-pedido-en-ventas) | Registrar mi pedido en Ventas | `SPEC-15 · Req. 1` | RN-PED-01, RN-PED-02, RN-PED-03 | `POST /checkout` | VEN `POST /api/v1/pedidos` | Hito 4 | Must | 8 |
| [HU-PED-02](historias/EP-06-pedido-confirmacion.md#hu-ped-02--confirmar-mi-pedido-pagado-aunque-ventas-falle-temporalmente) | Confirmar mi pedido pagado aunque Ventas falle temporalmente | `SPEC-15 · Req. 2` | RN-PED-04, RN-PED-05, RN-PED-06 | `GET /checkout/{checkoutId}` | VEN `POST /api/v1/pedidos/{id}/pagos/notificacion` | Hito 4 | Must | 8 |
| [HU-PED-03](historias/EP-06-pedido-confirmacion.md#hu-ped-03--liberar-los-pedidos-que-no-se-pagaron) | Liberar los pedidos que no se pagaron | `SPEC-15 · Req. 3` | RN-PED-06, RN-PED-07 | — (outbox) | VEN `POST /api/v1/pedidos/{id}/anulaciones` | Hito 4 | Must | 3 |
| [HU-PED-04](historias/EP-06-pedido-confirmacion.md#hu-ped-04--garantizar-que-se-registra-exactamente-lo-confirmado) | Garantizar que se registra exactamente lo confirmado | `SPEC-15 · Req. 4` | RN-PED-08, RN-PED-09 | `POST /checkout` | VEN `POST /api/v1/pedidos` | Hito 4 | Must | 2 |
| [HU-PED-05](historias/EP-06-pedido-confirmacion.md#hu-ped-05--recibir-el-correo-de-confirmación-de-mi-compra) | Recibir el correo de confirmación de mi compra | `SPEC-16 · Req. 1` | RN-PED-10, RN-PED-14 | — (outbox `ENVIAR_CORREO`) | SMTP | Hito 4 | Must | 5 |
| [HU-PED-06](historias/EP-06-pedido-confirmacion.md#hu-ped-06--recibir-un-único-correo-aunque-haya-fallos) | Recibir un único correo aunque haya fallos | `SPEC-16 · Req. 2` | RN-PED-10, RN-PED-11 | — (outbox `ENVIAR_CORREO`) | SMTP | Hito 4 | Must | 3 |
| [HU-PED-07](historias/EP-06-pedido-confirmacion.md#hu-ped-07--ver-mi-compra-confirmada-aunque-el-correo-se-demore) | Ver mi compra confirmada aunque el correo se demore | `SPEC-16 · Req. 3` (escenario 1) | RN-PED-12 | `GET /checkout/{checkoutId}` (bloque `CONFIRMACION_PEDIDO`) | — | Hito 4 | Must | 1 |
| [HU-PED-08](historias/EP-06-pedido-confirmacion.md#hu-ped-08--pedir-el-reenvío-del-correo-de-confirmación) | Pedir el reenvío del correo de confirmación | `SPEC-16 · Req. 3` (escenario 2) | RN-PED-13 | `POST /pedidos/{id}/reenviar-confirmacion` | SMTP | Hito 4 | Should | 2 |
| [HU-SGT-01](historias/EP-07-seguimiento.md#hu-sgt-01--encontrar-mi-pedido-rápidamente) | Encontrar mi pedido rápidamente | `SPEC-17 · Req. 1` | RN-SGT-02, RN-SGT-03, RN-SGT-04, RN-SGT-05 | `GET /pedidos`, `GET /pedidos/{pedidoId}` | VEN `GET /api/v1/pedidos`, `GET /api/v1/pedidos/{id}` | Hito 5–6 | Must | 5 |
| [HU-SGT-02](historias/EP-07-seguimiento.md#hu-sgt-02--ver-el-estado-y-la-línea-de-tiempo-de-mi-pedido) | Ver el estado y la línea de tiempo de mi pedido | `SPEC-17 · Req. 2` | RN-SGT-01, RN-SGT-06, RN-SGT-07 | `GET /pedidos/{pedidoId}` | VEN `GET /api/v1/pedidos/{id}`; DES seguimiento 🟡 | Hito 5–6 | Must | 5 |
| [HU-SGT-03](historias/EP-07-seguimiento.md#hu-sgt-03--obtener-respuestas-directas-sobre-mi-pedido) | Obtener respuestas directas sobre mi pedido | `SPEC-17 · Req. 3` | RN-SGT-08 | `GET /pedidos/{pedidoId}` | VEN `GET /api/v1/pedidos/{id}`; DES seguimiento 🟡 | Hito 5–6 | Should | 3 |
| [HU-SGT-04](historias/EP-07-seguimiento.md#hu-sgt-04--saber-cuándo-no-se-puede-consultar-mi-pedido) | Saber cuándo no se puede consultar mi pedido | `SPEC-17 · Req. 4` | RN-SGT-09 | `GET /pedidos`, `GET /pedidos/{pedidoId}` | VEN `GET /api/v1/pedidos/{id}` | Hito 5–6 | Must | 2 |
| [HU-SGT-05](historias/EP-07-seguimiento.md#hu-sgt-05--seguir-mi-paquete-en-ruta) | Seguir mi paquete en ruta | `SPEC-18 · Req. 1` | RN-SGT-10, RN-SGT-12 | `GET /pedidos/{pedidoId}/seguimiento` | DES `GET /seguimiento?idPedido=` 🟡 (propuesto) | Hito 5–6 | Should | 5 |
| [HU-SGT-06](historias/EP-07-seguimiento.md#hu-sgt-06--enterarme-de-entregas-fallidas-o-reprogramadas) | Enterarme de entregas fallidas o reprogramadas | `SPEC-18 · Req. 2` | RN-SGT-11 | `GET /pedidos/{pedidoId}/seguimiento` | DES `GET /seguimiento?idPedido=` 🟡 | Hito 5–6 | Should | 3 |
| [HU-SGT-07](historias/EP-07-seguimiento.md#hu-sgt-07--recibir-respuestas-honestas-sobre-la-ubicación-del-repartidor) | Recibir respuestas honestas sobre la ubicación del repartidor | `SPEC-18 · Req. 3` | RN-SGT-11 | `GET /pedidos/{pedidoId}/seguimiento` | DES `GET /seguimiento?idPedido=` 🟡 | Hito 5–6 | Should | 2 |
| [HU-SGT-08](historias/EP-07-seguimiento.md#hu-sgt-08--consultar-despacho-con-credenciales-de-servicio-y-degradar-ante-fallos-habilitadora) | Consultar Despacho con credenciales de servicio y degradar ante fallos (Habilitadora) | `SPEC-18 · Req. 4` | RN-SGT-13, RN-SGT-14 | `GET /pedidos/{pedidoId}/seguimiento` | SEG `POST /auth/token`; DES `GET /seguimiento?idPedido=` 🟡 | Hito 5–6 | Should | 3 |
| [HU-RCL-01](historias/EP-08-reclamos.md#hu-rcl-01--describir-mi-problema-y-revisar-el-reclamo-antes-de-enviarlo) | Describir mi problema y revisar el reclamo antes de enviarlo | `SPEC-19 · Req. 1` | RN-RCL-01, RN-RCL-02, RN-RCL-03 | `POST /chat/conversaciones/{id}/mensajes` (herramienta `preparar_reclamo`) | VEN `GET /api/v1/pedidos?clienteId=` | Hito 5–6 | Should | 5 |
| [HU-RCL-02](historias/EP-08-reclamos.md#hu-rcl-02--registrar-mi-reclamo-y-recibir-un-código) | Registrar mi reclamo y recibir un código | `SPEC-19 · Req. 2` | RN-RCL-04, RN-RCL-05, RN-RCL-06, RN-CHK-01 | `POST /reclamos` | VEN `POST /api/v2/reclamos` | Hito 5–6 | Should | 5 |
| [HU-RCL-03](historias/EP-08-reclamos.md#hu-rcl-03--evitar-reclamos-duplicados) | Evitar reclamos duplicados | `SPEC-19 · Req. 3` | RN-RCL-07 | `POST /reclamos` | VEN `GET /api/v2/reclamos?clienteId=&estado=` | Hito 5–6 | Should | 3 |
| [HU-RCL-04](historias/EP-08-reclamos.md#hu-rcl-04--conservar-mi-reclamo-si-falla-el-registro) | Conservar mi reclamo si falla el registro | `SPEC-19 · Req. 4` | RN-RCL-08 | `POST /reclamos` | VEN `POST /api/v2/reclamos` | Hito 5–6 | Should | 2 |
| [HU-RCL-05](historias/EP-08-reclamos.md#hu-rcl-05--listar-y-abrir-mis-reclamos) | Listar y abrir mis reclamos | `SPEC-20 · Req. 1` | RN-RCL-11 | `GET /reclamos`, `GET /reclamos/{codigoSeguimiento}` | VEN `GET /api/v2/reclamos`, `GET /api/v2/reclamos/{codigoSeguimiento}` | Hito 5–6 | Could | 3 |
| [HU-RCL-06](historias/EP-08-reclamos.md#hu-rcl-06--leer-el-estado-y-la-respuesta-de-mi-reclamo) | Leer el estado y la respuesta de mi reclamo | `SPEC-20 · Req. 2` | RN-RCL-09, RN-RCL-10 | `GET /reclamos/{codigoSeguimiento}` | VEN `GET /api/v2/reclamos/{codigoSeguimiento}` | Hito 5–6 | Could | 3 |
| [HU-RCL-07](historias/EP-08-reclamos.md#hu-rcl-07--saber-cuándo-no-se-pueden-consultar-mis-reclamos) | Saber cuándo no se pueden consultar mis reclamos | `SPEC-20 · Req. 3` | — | `GET /reclamos`, `GET /reclamos/{codigoSeguimiento}` | VEN `GET /api/v2/reclamos` | Hito 5–6 | Could | 1 |
| [HU-DEV-01](historias/EP-09-devoluciones.md#hu-dev-01--saber-si-mi-pedido-es-elegible-para-cambio-o-devolución) | Saber si mi pedido es elegible para cambio o devolución | `SPEC-21 · Req. 1` | RN-DEV-01, RN-DEV-02 | `GET /pedidos/{pedidoId}` | VEN `GET /api/v1/pedidos/{id}` | Hito 5–6 | Could | 3 |
| [HU-DEV-02](historias/EP-09-devoluciones.md#hu-dev-02--elegir-los-productos-el-tipo-y-el-motivo-de-la-solicitud) | Elegir los productos, el tipo y el motivo de la solicitud | `SPEC-21 · Req. 2` | RN-DEV-03, RN-DEV-04, RN-DEV-07 | `POST /chat/conversaciones/{id}/mensajes` (herramienta `preparar_devolucion`), `GET /catalogo/disponibilidad` | PRO `GET /inventario/disponibilidad` 🟡 | Hito 5–6 | Could | 5 |
| [HU-DEV-03](historias/EP-09-devoluciones.md#hu-dev-03--adjuntar-evidencia-fotográfica-o-en-pdf) | Adjuntar evidencia fotográfica o en PDF | `SPEC-21 · Req. 3` | RN-DEV-05, RN-DEV-06 | `POST /evidencias` | VEN `POST /api/v2/devoluciones/evidencias/upload` | Hito 5–6 | Could | 5 |
| [HU-DEV-04](historias/EP-09-devoluciones.md#hu-dev-04--registrar-mi-solicitud-y-recibir-un-código) | Registrar mi solicitud y recibir un código | `SPEC-21 · Req. 4` | RN-DEV-07, RN-DEV-08, RN-DEV-09 | `POST /devoluciones` | VEN `POST /api/v2/devoluciones` | Hito 5–6 | Could | 5 |
| [HU-DEV-05](historias/EP-09-devoluciones.md#hu-dev-05--evitar-solicitudes-duplicadas) | Evitar solicitudes duplicadas | `SPEC-21 · Req. 5` | RN-DEV-10 | `POST /devoluciones` | VEN `GET /api/v2/devoluciones?clienteId=` | Hito 5–6 | Could | 3 |
| [HU-DEV-06](historias/EP-09-devoluciones.md#hu-dev-06--ver-todas-mis-solicitudes-en-la-pestaña-reembolsos) | Ver todas mis solicitudes en la pestaña "Reembolsos" | `SPEC-22 · Req. 1` | RN-DEV-13 | `GET /devoluciones`, `GET /devoluciones/{devolucionId}` | VEN `GET /api/v2/devoluciones?clienteId=`, `GET /api/v2/devoluciones/{id}` | Hito 5–6 | Could | 3 |
| [HU-DEV-07](historias/EP-09-devoluciones.md#hu-dev-07--ver-el-estado-de-mi-solicitud) | Ver el estado de mi solicitud | `SPEC-22 · Req. 2` | RN-DEV-11, RN-DEV-12 | `GET /devoluciones/{devolucionId}` | VEN `GET /api/v2/devoluciones/{id}` | Hito 5–6 | Could | 3 |
| [HU-DEV-08](historias/EP-09-devoluciones.md#hu-dev-08--ver-el-estado-de-mi-reembolso) | Ver el estado de mi reembolso | `SPEC-22 · Req. 3` | RN-DEV-12, RN-DEV-14 | `GET /devoluciones/{devolucionId}` | VEN `GET /api/v2/devoluciones/{id}` | Hito 5–6 | Could | 3 |
| [HU-DEV-09](historias/EP-09-devoluciones.md#hu-dev-09--saber-cuándo-no-se-pueden-consultar-mis-devoluciones) | Saber cuándo no se pueden consultar mis devoluciones | `SPEC-22 · Req. 4` | — | `GET /devoluciones/{devolucionId}` | VEN `GET /api/v2/devoluciones/{id}` | Hito 5–6 | Could | 1 |

## 3. Verificación de cobertura de requisitos

Cada uno de los **99 requisitos** de las 22 specs está cubierto por al menos una historia.

| Requisito | Nombre | Historia(s) |
|---|---|---|
| `SPEC-01 · Req. 1` | Apertura del formulario de registro | HU-IDE-01 |
| `SPEC-01 · Req. 2` | Validación en cliente | HU-IDE-02 |
| `SPEC-01 · Req. 3` | Registro exitoso | HU-IDE-02 |
| `SPEC-01 · Req. 4` | Manejo de errores de Seguridad | HU-IDE-03 |
| `SPEC-02 · Req. 1` | Canje del enlace de verificación | HU-IDE-04 |
| `SPEC-02 · Req. 2` | Reenvío del enlace | HU-IDE-05 |
| `SPEC-02 · Req. 3` | Pista ante cualquier login fallido | HU-IDE-05 |
| `SPEC-03 · Req. 1` | Inicio de sesión con correo y contraseña | HU-IDE-06 |
| `SPEC-03 · Req. 2` | Segundo factor (MFA) | HU-IDE-07 |
| `SPEC-03 · Req. 3` | Retoma de la acción pendiente | HU-IDE-08 |
| `SPEC-03 · Req. 4` | Fusión del carrito anónimo | HU-IDE-09 |
| `SPEC-03 · Req. 5` | Renovación y validación de la sesión | HU-IDE-10 |
| `SPEC-03 · Req. 6` | Cierre de sesión | HU-IDE-11 |
| `SPEC-04 · Req. 1` | Exigir el celular verificado antes del checkout | HU-IDE-12 |
| `SPEC-04 · Req. 2` | Envío y verificación del código | HU-IDE-13 |
| `SPEC-04 · Req. 3` | El celular es incorrecto | HU-IDE-14 |
| `SPEC-05 · Req. 1` | Conversaciones múltiples | HU-CNV-01, HU-CNV-02 |
| `SPEC-05 · Req. 2` | Pantalla de inicio | HU-CNV-03 |
| `SPEC-05 · Req. 3` | Interpretación de la intención mediante herramientas | HU-CNV-04 |
| `SPEC-05 · Req. 4` | Transmisión de la respuesta por WebSocket | HU-CNV-05 |
| `SPEC-05 · Req. 5` | Referencias al contexto conversacional | HU-CNV-06 |
| `SPEC-05 · Req. 6` | Ejecución segura de herramientas | HU-CNV-07 |
| `SPEC-05 · Req. 7` | Veracidad de la respuesta | HU-CNV-08 |
| `SPEC-05 · Req. 8` | Acciones directas desde la UI | HU-CNV-09 |
| `SPEC-05 · Req. 9` | Protección de datos sensibles y ante prompt injection | HU-CNV-10 |
| `SPEC-05 · Req. 10` | Modo degradado | HU-CNV-11 |
| `SPEC-05 · Req. 11` | Límites de uso | HU-CNV-12 |
| `SPEC-05 · Req. 12` | Presentación del asistente y aviso de privacidad | HU-CNV-13 |
| `SPEC-06 · Req. 1` | Búsqueda con filtros combinados | HU-CAT-01 |
| `SPEC-06 · Req. 2` | Normalización de categoría y marca | HU-CAT-02 |
| `SPEC-06 · Req. 3` | Refinamiento conversacional | HU-CAT-03 |
| `SPEC-06 · Req. 4` | Paginación y resultados vacíos | HU-CAT-04 |
| `SPEC-06 · Req. 5` | Tolerancia a fallos de Productos | HU-CAT-05 |
| `SPEC-07 · Req. 1` | Recomendación a partir de una necesidad | HU-CAT-06 |
| `SPEC-07 · Req. 2` | Recomendaciones veraces y disponibles | HU-CAT-07 |
| `SPEC-07 · Req. 3` | Complementos (cross-sell) | HU-CAT-08 |
| `SPEC-08 · Req. 1` | Listar promociones vigentes del canal | HU-CAT-09 |
| `SPEC-08 · Req. 2` | Mostrar precio de oferta en tarjetas y detalle | HU-CAT-10 |
| `SPEC-08 · Req. 3` | Explicar los beneficios aplicados en el carrito | HU-CAT-11 |
| `SPEC-08 · Req. 4` | No revelar códigos de cupón | HU-CAT-12 |
| `SPEC-09 · Req. 1` | Tarjetas en carrusel | HU-CAT-13 |
| `SPEC-09 · Req. 2` | Agregar desde la tarjeta | HU-CAT-14 |
| `SPEC-09 · Req. 3` | Detalle del producto | HU-CAT-15 |
| `SPEC-09 · Req. 4` | Selección de variante por lenguaje natural | HU-CAT-16 |
| `SPEC-10 · Req. 1` | Validar antes de agregar o incrementar | HU-CAR-01 |
| `SPEC-10 · Req. 2` | Revalidar todo el carrito antes del checkout | HU-CAR-02 |
| `SPEC-10 · Req. 3` | Nunca asumir disponibilidad | HU-CAR-03 |
| `SPEC-10 · Req. 4` | Consulta explícita de disponibilidad | HU-CAR-04 |
| `SPEC-11 · Req. 1` | Agregar productos | HU-CAR-05 |
| `SPEC-11 · Req. 2` | Modificar y quitar | HU-CAR-06 |
| `SPEC-11 · Req. 3` | Ver el carrito con totales recalculados | HU-CAR-07 |
| `SPEC-11 · Req. 4` | Persistencia y ciclo de vida | HU-CAR-08 |
| `SPEC-12 · Req. 1` | Capturar el documento de identidad | HU-CHK-01 |
| `SPEC-12 · Req. 2` | Capturar la dirección en el checkout | HU-CHK-02 |
| `SPEC-12 · Req. 3` | Guardar la dirección para la próxima compra | HU-CHK-03 |
| `SPEC-12 · Req. 4` | Cotizar el envío | HU-CHK-04 |
| `SPEC-12 · Req. 5` | Mantener vigente la cotización | HU-CHK-05 |
| `SPEC-13 · Req. 1` | Aplicar un cupón válido | HU-CHK-06 |
| `SPEC-13 · Req. 2` | Rechazo con motivo claro | HU-CHK-07 |
| `SPEC-13 · Req. 3` | Requiere sesión | HU-CHK-08 |
| `SPEC-13 · Req. 4` | Revalidación | HU-CHK-09 |
| `SPEC-13 · Req. 5` | Protección contra fuerza bruta | HU-CHK-10 |
| `SPEC-14 · Req. 1` | Precondiciones del checkout | HU-CHK-11 |
| `SPEC-14 · Req. 2` | Confirmación del resumen y creación del checkout | HU-CHK-12 |
| `SPEC-14 · Req. 3` | Captura segura de la tarjeta | HU-CHK-13 |
| `SPEC-14 · Req. 4` | Introspección antes de procesar el pago | HU-CHK-14 |
| `SPEC-14 · Req. 5` | Simulación del pago | HU-CHK-15 |
| `SPEC-14 · Req. 6` | Vigencia del checkout | HU-CHK-16 |
| `SPEC-15 · Req. 1` | Crear el pedido en Ventas | HU-PED-01 |
| `SPEC-15 · Req. 2` | Notificar el pago aprobado | HU-PED-02 |
| `SPEC-15 · Req. 3` | Anular los pedidos no pagados | HU-PED-03 |
| `SPEC-15 · Req. 4` | Coherencia del snapshot | HU-PED-04 |
| `SPEC-16 · Req. 1` | Envío de la confirmación | HU-PED-05 |
| `SPEC-16 · Req. 2` | Idempotencia y reintentos | HU-PED-06 |
| `SPEC-16 · Req. 3` | El correo no bloquea la compra | HU-PED-07, HU-PED-08 |
| `SPEC-17 · Req. 1` | Identificar el pedido | HU-SGT-01 |
| `SPEC-17 · Req. 2` | Mostrar el estado y la línea de tiempo | HU-SGT-02 |
| `SPEC-17 · Req. 3` | Preguntas específicas | HU-SGT-03 |
| `SPEC-17 · Req. 4` | Tolerancia a fallos | HU-SGT-04 |
| `SPEC-18 · Req. 1` | Consultar el seguimiento de un pedido despachado | HU-SGT-05 |
| `SPEC-18 · Req. 2` | Entregas no exitosas | HU-SGT-06 |
| `SPEC-18 · Req. 3` | Límites de la información | HU-SGT-07 |
| `SPEC-18 · Req. 4` | Autenticación de servicio y fallos | HU-SGT-08 |
| `SPEC-19 · Req. 1` | Recolección guiada | HU-RCL-01 |
| `SPEC-19 · Req. 2` | Confirmación explícita y registro | HU-RCL-02 |
| `SPEC-19 · Req. 3` | Reclamos duplicados | HU-RCL-03 |
| `SPEC-19 · Req. 4` | Tolerancia a fallos | HU-RCL-04 |
| `SPEC-20 · Req. 1` | Listar e identificar reclamos | HU-RCL-05 |
| `SPEC-20 · Req. 2` | Mostrar el estado y la respuesta | HU-RCL-06 |
| `SPEC-20 · Req. 3` | Tolerancia a fallos | HU-RCL-07 |
| `SPEC-21 · Req. 1` | Verificar elegibilidad | HU-DEV-01 |
| `SPEC-21 · Req. 2` | Elegir línea, tipo y motivo | HU-DEV-02 |
| `SPEC-21 · Req. 3` | Cargar evidencia fotográfica o en PDF | HU-DEV-03 |
| `SPEC-21 · Req. 4` | Confirmación explícita y registro | HU-DEV-04 |
| `SPEC-21 · Req. 5` | Solicitud duplicada sobre el mismo pedido | HU-DEV-05 |
| `SPEC-22 · Req. 1` | Listar e identificar solicitudes | HU-DEV-06 |
| `SPEC-22 · Req. 2` | Mostrar el estado del expediente | HU-DEV-07 |
| `SPEC-22 · Req. 3` | Mostrar el estado del reembolso de dinero | HU-DEV-08 |
| `SPEC-22 · Req. 4` | Tolerancia a fallos | HU-DEV-09 |

**Resultado:** 99 de 99 requisitos cubiertos (100 %). Requisitos sin historia: ninguno.

Requisitos repartidos en más de una historia: `SPEC-05 · Req. 1` (HU-CNV-01 y HU-CNV-02) y `SPEC-16 · Req. 3` (HU-PED-07 y HU-PED-08). Historias que cubren más de un requisito: HU-IDE-02 (`SPEC-01 · Req. 2–3`) y HU-IDE-05 (`SPEC-02 · Req. 2–3`).

La cobertura a nivel de escenario también es completa: los **279 escenarios** de las specs están citados por nombre en los criterios de aceptación de alguna historia.

## 4. Totales

### 4.1 Por épica

| Épica | Historias | Puntos | Must | Should | Could | Hito 3 (pts) | Hito 4 (pts) | Hito 5–6 (pts) |
|---|---|---|---|---|---|---|---|---|
| EP-01 · Identidad y sesión | 14 | 50 | 13 | 1 | — | 40 | 10 | — |
| EP-02 · Motor de conversación | 13 | 60 | 10 | 3 | — | 60 | — | — |
| EP-03 · Descubrimiento de productos | 16 | 61 | 13 | 3 | — | 38 | 23 | — |
| EP-04 · Carrito y stock | 8 | 36 | 7 | 1 | — | 36 | — | — |
| EP-05 · Checkout y pago | 16 | 65 | 14 | 2 | — | — | 65 | — |
| EP-06 · Grabación y confirmación del pedido | 8 | 32 | 7 | 1 | — | — | 32 | — |
| EP-07 · Seguimiento de pedidos | 8 | 28 | 3 | 5 | — | — | — | 28 |
| EP-08 · Reclamos | 7 | 22 | — | 4 | 3 | — | — | 22 |
| EP-09 · Devoluciones y reembolsos | 9 | 31 | — | — | 9 | — | — | 31 |
| **Total** | **99** | **385** | **67** | **20** | **12** | **174** | **130** | **81** |

### 4.2 Por hito

| Hito | Specs (README) | Historias | Puntos | Must (pts) | Should (pts) | Could (pts) |
|---|---|---|---|---|---|---|
| Hito 3 | SPEC-01, 02, 03, 05, 06, 09, 10, 11 | 41 | 174 | 36 (156) | 5 (18) | 0 (0) |
| Hito 4 | SPEC-04, 07, 08, 12, 13, 14, 15, 16 | 34 | 130 | 28 (116) | 6 (14) | 0 (0) |
| Hito 5–6 | SPEC-17 a 22 | 24 | 81 | 3 (12) | 9 (31) | 12 (38) |
| **Total** | | **99** | **385** | **67 (284)** | **20 (63)** | **12 (38)** |

### 4.3 Distribución MoSCoW

| Prioridad | Historias | % historias | Puntos | % puntos |
|---|---|---|---|---|
| Must | 67 | 68 % | 284 | 74 % |
| Should | 20 | 20 % | 63 | 16 % |
| Could | 12 | 12 % | 38 | 10 % |
| Won't (este ciclo) | 0 | — | — | — |

Los puntos Won't no se cuentan: lo excluido del ciclo está en [`alcance.md` §5](alcance.md#5-fuera-de-alcance-consolidado) y no genera historias.

### 4.4 Reglas de negocio

| Área | IDE | CNV | CAT | CAR | CHK | PED | SGT | RCL | DEV | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| Reglas | 21 | 21 | 17 | 16 | 26 | 14 | 14 | 11 | 14 | **154** |

Todas las reglas del catálogo están citadas por al menos una historia, y todas las reglas citadas en las historias existen en el catálogo.
