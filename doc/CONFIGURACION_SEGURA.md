# Configuración segura del AMS

La aplicación inicia sesión con Google, permite el acceso solo a las cuentas de
la lista autorizada y lee el Google Sheet privado mediante una cuenta de
servicio. No compartas contraseñas, claves privadas ni archivos de credenciales
en el chat o en el repositorio.

## 1. Publicar el código de forma privada

Streamlit Community Cloud despliega aplicaciones desde GitHub. El código puede
estar en un repositorio público o privado. Un repositorio privado sigue siendo
visible para su propietario al iniciar sesión en GitHub; la visibilidad del
código no determina quién puede abrir la aplicación.

En VS Code, usa el panel **Control de código fuente** para publicar el proyecto
en el repositorio de GitHub elegido. Si el repositorio es público, revisa que
solo contenga código, pruebas y documentación: nunca incluyas
`.streamlit/secrets.toml`, claves OAuth, archivos JSON de cuentas de servicio ni
filas reales del Google Sheet.

## 2. Crear el acceso de lectura para el Google Sheet

1. En Google Cloud Console, crea o selecciona un proyecto.
2. Habilita **Google Sheets API** para ese proyecto.
3. En **IAM y administración → Cuentas de servicio**, crea una cuenta de servicio.
4. Crea una clave JSON y guárdala localmente en un lugar privado. No la subas a
   GitHub ni la envíes por chat.
5. Abre el JSON y copia los valores de sus campos en la sección
   `[gcp_service_account]` de la plantilla de secretos.
6. Comparte el Google Sheet privado con el correo `client_email` de esa cuenta
   de servicio y dale permiso **Lector**. No cambies el acceso general del Sheet
   a público.

## 3. Crear el inicio de sesión de Google

1. En Google Cloud Console, configura la pantalla de consentimiento OAuth.
2. Crea un **ID de cliente OAuth** de tipo **Aplicación web**.
3. En **URI de redireccionamiento autorizados**, agrega la dirección que
   Streamlit Community Cloud muestre para esta app, terminada en
   `/oauth2callback`.
4. Copia el ID de cliente y el secreto de cliente directamente a la sección
   `[auth]` de los secretos de Streamlit. Nunca los guardes en `app.py`.

El inicio de sesión Google no requiere una contraseña compartida dentro del AMS.
Cada persona usa su propia cuenta Google. Solo las cuentas incluidas en
`[app].authorized_emails` podrán acceder.

## 4. Configurar Streamlit Community Cloud

1. En Streamlit Community Cloud, crea la app desde el repositorio privado de
   GitHub y selecciona `app.py` como archivo principal.
2. Abre la app en Streamlit y entra en **Settings → Secrets**.
3. Copia el contenido de `.streamlit/secrets.example.toml` en el editor de
   secretos de Streamlit. Completa los marcadores con los valores de Google
   Cloud, el ID de la hoja y las cuentas autorizadas.
4. Genera un valor secreto aleatorio para `cookie_secret`; no reutilices una
   contraseña personal ni la contraseña compartida en un chat.
5. En `[auth].redirect_uri`, usa exactamente la URL de la app más
   `/oauth2callback`.
6. En `[app].authorized_emails`, agrega solo las cuentas Google autorizadas.
7. Guarda los secretos y reinicia la aplicación.

Los secretos de la aplicación existen solo en la configuración privada de
Streamlit; la plantilla del repositorio contiene marcadores, no credenciales.

## 5. Comprobar la conexión

- Inicia sesión con una cuenta autorizada.
- Una cuenta que no esté en la lista debe recibir acceso denegado.
- La cuenta de servicio debe aparecer como lectora en el diálogo **Compartir**
  del Google Sheet.
- Si faltan secretos, la aplicación mostrará qué secciones de configuración
  deben completarse.
- Los datos se actualizan automáticamente cada cinco minutos.
