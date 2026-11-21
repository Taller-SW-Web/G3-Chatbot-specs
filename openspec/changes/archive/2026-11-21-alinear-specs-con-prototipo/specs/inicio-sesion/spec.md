## ADDED Requirements

### Requirement: Pantalla "Mi cuenta"
El sistema DEBE (SHALL) ofrecer al cliente autenticado una pantalla "Mi cuenta" (`AccountPage`, ruta `/cuenta`) de solo lectura con sus datos de perfil, el estado de verificación de su celular y los accesos a sus pedidos, sus reclamos y el cierre de sesión, y NO DEBE (SHALL NOT) permitir editar el perfil desde este canal.

*Trazabilidad: SPEC-03 · Requisito 7.*

#### Scenario: Abrir "Mi cuenta" con sesión
- **DADO** un cliente autenticado
- **CUANDO** pulsa su nombre en el pie de la barra lateral
- **ENTONCES** se navega a `AccountPage`, que muestra el nombre completo, el correo completo con la etiqueta "Verificado", el celular enmascarado (`+51 9****4321`) con la etiqueta "Celular verificado" o "Sin verificar" según la verificación local de SPEC-04, y los accesos "Mis pedidos", "Mis reclamos" y "Cerrar sesión"

#### Scenario: Visitante sin sesión
- **DADO** un visitante sin sesión
- **CUANDO** pulsa "Iniciar sesión" en el pie de la barra lateral
- **ENTONCES** se abre `AuthModal` en la pestaña de login y no se muestra `AccountPage`

#### Scenario: Documento del último pedido
- **DADO** un cliente que ya completó su documento en una compra anterior en este canal
- **CUANDO** abre `AccountPage`
- **ENTONCES** se muestra la fila "Documento" con el tipo y el número enmascarado, dejando visibles solo los últimos 3 caracteres (por ejemplo, `DNI *****912`), tomado del último `checkout.summary.contacto` del cliente y nunca del perfil de Seguridad

#### Scenario: Cliente sin documento registrado
- **DADO** un cliente que nunca completó una compra en este canal
- **CUANDO** abre `AccountPage`
- **ENTONCES** la fila "Documento" no se muestra

#### Scenario: Datos que se editan fuera del canal
- **DADO** `AccountPage`
- **CUANDO** se muestra la sección "Se edita en Seguridad / Marketplace"
- **ENTONCES** lista "Nombre o correo", "Cambiar celular", "Contraseña y MFA" y "Direcciones guardadas" como elementos informativos no editables
- **Y** ninguno abre un formulario dentro del chatbot; solo se ofrece un enlace externo si hay una URL de perfil configurada

#### Scenario: Accesos desde "Mi cuenta"
- **DADO** `AccountPage`
- **CUANDO** el cliente pulsa "Mis pedidos", "Mis reclamos" o "Cerrar sesión"
- **ENTONCES** se navega a `OrderHistoryPage` (SPEC-17), se listan los reclamos del cliente (SPEC-20) o se cierra la sesión (Requisito 6), respectivamente

#### Scenario: Perfil no disponible
- **DADO** que Seguridad no responde al consultar el perfil
- **CUANDO** carga `AccountPage`
- **ENTONCES** se muestra "No pudimos cargar tus datos en este momento" con "Reintentar", y "Cerrar sesión" sigue disponible

## ADDED Non-Functional Requirements

- **Privacidad:** el backend entrega el documento ya enmascarado; el número completo nunca llega al frontend desde `AccountPage`. Ningún dato de "Mi cuenta" se envía al LLM.