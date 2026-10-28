# Plan — Spec 001: Origen seguro de datos

## Diseño

1. **Identidad:** Streamlit OIDC con Google identifica a la persona que inició sesión.
2. **Autorización:** una lista de correos permitidos, cargada desde secretos de Streamlit, bloquea todas las cuentas no autorizadas antes de consultar el Sheet.
3. **Acceso a Sheets:** una cuenta de servicio, configurada en secretos y con permiso de lectura sobre la hoja privada, obtiene las tres pestañas requeridas.
4. **Normalización de encabezados:** una función común normaliza tildes, mayúsculas y separadores; un registro de alias transforma los campos estructurales conocidos a nombres canónicos.
5. **Columnas variables:** las columnas que no sean campos estructurales se conservan como variables de medición. Los campos estructurales desconocidos se asignan con selectores y la selección se guarda en `st.session_state`.
6. **Validación:** cada pestaña valida los campos mínimos antes de entregar datos al dashboard. Las filas sin jugador o fecha se excluyen y se cuentan.
7. **Caché:** los datos se almacenan en caché por un máximo de cinco minutos. Los errores se presentan al usuario con el nombre de la pestaña o campo afectado.

## Flujo de datos

`Inicio de sesión → lista autorizada → lectura privada de Sheets → normalización y validación → exclusión de filas incompletas → datos disponibles al dashboard`

## Protección de datos

- El acceso a datos se realiza después de autorizar la cuenta.
- El DNI sirve únicamente como clave interna de unión y no se presenta como etiqueta visible.
- Los secretos de OIDC y de la cuenta de servicio se mantienen fuera del repositorio.
- Las pruebas usan datos ficticios y no llaman al Sheet real.

## Manejo de errores

- **Cuenta no autorizada:** bloquear la carga y ofrecer cerrar sesión.
- **Credenciales o permisos inválidos:** indicar que deben revisarse los secretos y los permisos de la cuenta de servicio.
- **Pestaña inexistente:** detener la carga e indicar el nombre esperado.
- **Campo obligatorio ausente:** ofrecer asignación si es un campo estructural; si no se puede resolver, detener el análisis.
- **Fila incompleta:** excluirla y reportar el conteo, sin sustituir sus celdas por cero.
