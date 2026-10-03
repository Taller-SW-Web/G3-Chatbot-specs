## MODIFIED Requirements

### Requirement: El celular es incorrecto
El sistema DEBE (SHALL) orientar al cliente si el celular registrado no es el suyo, sin permitir cambiarlo desde el chat (ese cambio es responsabilidad de Seguridad y queda fuera de este canal).

*Trazabilidad: SPEC-04 · Requisito 3.*

#### Scenario: El cliente indica que el número no es el suyo
- **DADO** el paso de verificación
- **CUANDO** el cliente pulsa "Ese no es mi número" o lo escribe
- **ENTONCES** el chat explica que el cambio de celular se hace desde su perfil fuera del chatbot y conserva el carrito
- **Y** muestra un enlace al perfil solo si hay una URL externa configurada

#### Scenario: Verificación iniciada por el cliente
- **DADO** un cliente autenticado
- **CUANDO** escribe "quiero verificar mi celular"
- **ENTONCES** se muestra el estado actual ("Tu celular ya está verificado") o se inicia el flujo del Requisito 2

#### Scenario: Verificación iniciada desde "Mi cuenta"
- **DADO** un cliente autenticado cuyo celular vigente no tiene una verificación local
- **CUANDO** pulsa "Verificar celular" en `AccountPage`
- **ENTONCES** se inicia el flujo del Requisito 2 dentro de la misma pantalla (envío del código, `OtpInput`, temporizador y reenvío, con las mismas reglas de vigencia, intentos y límite de envíos)
- **Y** al verificar, la etiqueta pasa a "Celular verificado" sin salir de la pantalla