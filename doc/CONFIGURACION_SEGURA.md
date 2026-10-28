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
5. Abre el JSON en tu computadora. Comprueba que `"type"` sea
   `"service_account"`. No pegues el JSON completo con llaves `{}`, comas y dos
   puntos: Streamlit Secrets utiliza formato TOML.
6. Copia los campos del JSON a la sección `[gcp_service_account]` que se muestra
   en la guía de abajo. Conserva los nombres de campo y las comillas TOML.
7. Comparte el Google Sheet privado con el correo `client_email` de esa cuenta
   de servicio y dale permiso **Lector**. No cambies el acceso general del Sheet
   a público.

## 3. Crear el inicio de sesión de Google

1. En Google Cloud Console, configura la pantalla de consentimiento OAuth.
2. Crea un **ID de cliente OAuth** de tipo **Aplicación web**.
3. En **URI de redireccionamiento autorizados**, agrega la dirección que
   Streamlit Community Cloud muestre para esta app, terminada en
   `/oauth2callback`.
4. Copia el ID de cliente y el secreto de cliente directamente a la sección
   `[auth]` de los secretos de Streamlit. Son valores OAuth distintos del
   `client_id` que aparece dentro del JSON de la cuenta de servicio. Nunca los
   guardes en `app.py`.

El inicio de sesión Google no requiere una contraseña compartida dentro del AMS.
Cada persona usa su propia cuenta Google. Solo las cuentas incluidas en
`[app].authorized_emails` podrán acceder.

## 4. Configurar Streamlit Community Cloud

1. En Streamlit Community Cloud, abre la app creada desde
   `DANP2025/ams-SDD`, con `app.py` como archivo principal.
2. En la app, abre **Manage app → menú de tres puntos → Settings → Secrets**.
3. Completa los secretos con los valores de Google Cloud, el ID de la hoja y
   las cuentas autorizadas. La sección de formato más abajo muestra los campos.
4. Genera un valor secreto aleatorio para `cookie_secret`; no reutilices una
   contraseña personal ni la contraseña compartida en un chat.
5. En `[auth].redirect_uri`, usa exactamente la URL de la app más
   `/oauth2callback`.
6. En `[app].authorized_emails`, agrega solo las cuentas Google autorizadas.
7. Guarda los secretos y reinicia la aplicación.

Los secretos de la aplicación existen solo en la configuración privada de
Streamlit; la plantilla del repositorio contiene marcadores, no credenciales.

### Formato de los Secrets

Para preparar todos los secretos sin pegarlos en un chat, abre
[el convertidor local](../tools/convertir_json_secrets.html) desde la carpeta
del proyecto. Completa localmente el ID y el secreto OAuth de tipo Aplicación
web, pega el enlace del Sheet o su ID, escribe las cuentas autorizadas (una por
línea), pega el JSON de la cuenta de servicio y pulsa **Generar clave aleatoria**
para `cookie_secret`. Luego pulsa **Preparar Secrets completos**. El convertidor
trabaja en el navegador, sin llamadas de red, y genera un único documento TOML
con las secciones `[auth]`, `[app]` y `[gcp_service_account]`. Pulsa **Copiar
TOML** y reemplaza en Streamlit Secrets el documento anterior por el documento
completo generado. Después de guardar, vuelve al convertidor y pulsa **Borrar
los campos**; borra también el portapapeles copiando un texto inocuo.

En Streamlit Community Cloud, abre [share.streamlit.io](https://share.streamlit.io),
busca AMS en tu espacio de trabajo, pulsa el menú de tres puntos junto a la app,
elige **Settings** y abre la pestaña **Secrets**. Alternativamente, desde la app
pulsa **Manage app**, abre el menú de tres puntos del panel de registros y elige
**Settings → Secrets**. Secrets debe contener un solo documento TOML con las
tres secciones. No pegues el contenido real de credenciales en GitHub ni en
este chat.

Si decides no usar el convertidor, transforma los campos del JSON al formato
siguiente. En particular, el valor de `private_key` del JSON ya contiene los
saltos como `\n`. Para ese campo, copia solo lo que está entre las comillas del
valor JSON y pégalo entre las comillas de TOML; conserva cada `\n` tal como
aparece. No copies el nombre `"private_key"`, los dos puntos ni la coma final:

```toml
[gcp_service_account]
type = "service_account"
project_id = "VALOR project_id DEL JSON"
private_key_id = "VALOR private_key_id DEL JSON"
private_key = "-----BEGIN PRIVATE KEY-----\nVALOR COMPLETO private_key DEL JSON\n-----END PRIVATE KEY-----\n"
client_email = "VALOR client_email DEL JSON"
client_id = "VALOR client_id DEL JSON"
auth_uri = "VALOR auth_uri DEL JSON"
token_uri = "VALOR token_uri DEL JSON"
auth_provider_x509_cert_url = "VALOR auth_provider_x509_cert_url DEL JSON"
client_x509_cert_url = "VALOR client_x509_cert_url DEL JSON"
```

No agregues comillas extra alrededor del valor, no cambies `\n` por una barra
invertida adicional, y elimina la coma que aparece al final de una propiedad
JSON. La clave privada es secreta; reemplaza todo el valor de ejemplo por el
`private_key` completo del JSON. No dejes marcadores como `VALOR ... DEL JSON`.

El documento de Secrets también debe incluir estas secciones, completadas con
los datos OAuth de la **aplicación web** y con el ID de la hoja:

```toml
[auth]
redirect_uri = "https://danp2025-ams-sdd-app-jtgkoq.streamlit.app/oauth2callback"
cookie_secret = "VALOR ALEATORIO LARGO Y UNICO"
client_id = "ID DE CLIENTE OAUTH DE LA APLICACION WEB"
client_secret = "SECRETO OAUTH DE LA APLICACION WEB"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[app]
google_sheet_id = "ID DE LA HOJA ENTRE /d/ Y /edit"
authorized_emails = [
  "correo-google-1@example.com",
  "correo-google-2@example.com",
  "correo-google-3@example.com",
]
```

En `[auth]`, `client_id` y `client_secret` vienen del cliente OAuth de tipo
**Aplicación web**, no del JSON de la cuenta de servicio. En
`[gcp_service_account]`, `client_id` sí viene del JSON de la cuenta de servicio.
`cookie_secret` debe ser un valor aleatorio largo y único. No compartas estos
valores con nadie.

Al terminar, el editor de Secrets debe contener las tres secciones: `[auth]`,
`[app]` y `[gcp_service_account]`. Sustituye todos los textos de ejemplo por
valores reales válidos antes de guardar. Streamlit lee ese contenido como TOML:
usa `=` entre nombre y valor, comillas dobles para textos, y corchetes para
secciones y listas.

## 5. Comprobar la conexión

- Inicia sesión con una cuenta autorizada.
- Una cuenta que no esté en la lista debe recibir acceso denegado.
- La cuenta de servicio debe aparecer como lectora en el diálogo **Compartir**
  del Google Sheet.
- Si faltan secretos, la aplicación mostrará qué secciones de configuración
  deben completarse.
- Los datos se actualizan automáticamente cada cinco minutos.
