## MODIFIED Requirements

### Requirement: Adjuntar imágenes desde el compositor
El sistema DEBE (SHALL) permitir adjuntar hasta 3 imágenes por mensaje (`image/jpeg`, `image/png` o `image/webp`, máx. 5 MB cada una), elegir su origen entre Galería y Tomar foto, validarlas en el cliente antes de subirlas y mostrar una previsualización con la opción de quitar cada una.

*Trazabilidad: SPEC-23 · Requisito 1.*

#### Scenario: Adjuntar imágenes válidas
- **DADO** el compositor de una conversación
- **CUANDO** el cliente selecciona 2 imágenes `image/jpeg` de 2 MB cada una
- **ENTONCES** se muestra una miniatura de cada una con su progreso de carga y un botón "Quitar", y el botón de envío se habilita cuando terminan de subirse

#### Scenario: Más de 3 imágenes
- **DADO** un mensaje con 3 imágenes ya adjuntas
- **CUANDO** el cliente intenta agregar una cuarta
- **ENTONCES** el frontend no la sube y muestra "Puedes adjuntar hasta 3 imágenes por mensaje"

#### Scenario: Tipo o tamaño no permitido detectado en el cliente
- **DADO** un archivo `.gif`, un PDF o una imagen de 7 MB
- **CUANDO** el cliente lo selecciona desde Galería o Tomar foto
- **ENTONCES** el frontend lo rechaza antes de subirlo y muestra "Solo puedes adjuntar imágenes JPG, PNG o WebP de hasta 5 MB"

#### Scenario: Quitar una imagen antes de enviar
- **DADO** una imagen ya subida y aún no enviada
- **CUANDO** el cliente pulsa "Quitar"
- **ENTONCES** la imagen desaparece del compositor y el backend elimina el adjunto pendiente y su archivo

#### Scenario: Mensaje solo con imagen
- **DADO** una imagen adjunta y el campo de texto vacío
- **CUANDO** el cliente envía el mensaje
- **ENTONCES** el envío se permite (el texto es opcional cuando hay al menos un adjunto)

#### Scenario: Elegir el origen de la imagen
- **DADO** un cliente que ya confirmó el aviso de privacidad (Requisito 2)
- **CUANDO** pulsa el botón "Agregar imagen"
- **ENTONCES** se muestra una hoja con las opciones "Galería" y "Tomar foto" y el recordatorio de formatos y tamaño permitidos

#### Scenario: Tomar una foto con la cámara
- **DADO** la hoja de origen en un dispositivo con cámara
- **CUANDO** el cliente elige "Tomar foto" y captura una imagen
- **ENTONCES** la foto pasa las mismas validaciones de tipo y tamaño que una imagen de la galería, aparece como miniatura con "Quitar" y cuenta para el límite de 3 imágenes por mensaje

#### Scenario: Dispositivo sin cámara o permiso denegado
- **DADO** un dispositivo sin cámara, o un cliente que niega el permiso
- **CUANDO** elige "Tomar foto"
- **ENTONCES** no se adjunta nada, no se muestra un error bloqueante y la opción "Galería" y el envío de texto siguen funcionando

#### Scenario: Foto de cámara mayor de 5 MB
- **DADO** una foto de cámara que supera 5 MB
- **CUANDO** el cliente la captura o selecciona
- **ENTONCES** se rechaza con "Solo puedes adjuntar imágenes JPG, PNG o WebP de hasta 5 MB" sin comprimirla en el cliente

## MODIFIED Non-Functional Requirements

- **Privacidad:** la cámara se abre solo mediante el selector nativo del dispositivo; la aplicación no pide ni conserva un permiso de cámara propio. La limpieza de EXIF y ubicación del Requisito 3 aplica también a las fotos tomadas con la cámara.