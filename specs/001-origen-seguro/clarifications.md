# Aclaraciones — Spec 001

| Tema | Pregunta | Respuesta |
|---|---|---|
| Fuente | ¿La fuente principal será Google Sheets, Excel o ambas? | Google Sheets; pestañas `Base de datos`, `Rendimiento` y `Plat de fuerza`. |
| Seguridad | ¿Qué modalidad de acceso se usará? | Acceso restringido al equipo de tres personas; hoja y aplicación privadas. |
| Alojamiento | ¿Dónde se alojará la aplicación? | Streamlit Community Cloud. |
| Inicio de sesión | ¿Cómo se autenticará el equipo? | Inicio de sesión de Google (OIDC) con una lista de cuentas autorizadas; no se usarán credenciales compartidas o escritas en el código. |
| Permisos de la hoja | ¿Quién necesita acceso lector al Google Sheet privado? | La cuenta de servicio configurada para la aplicación Streamlit; la IA no necesita acceso lector. |
| Variación de encabezados | ¿Qué hacer si un encabezado no coincide con los alias conocidos? | Incorporar automáticamente nuevas columnas de medición; para campos estructurales desconocidos, permitir asignación mediante la interfaz. |
| Persistencia de asignaciones | ¿Cómo recordar una asignación nueva? | Solo durante la sesión actual; no se guardará entre sesiones. |
| Actualización | ¿Cada cuánto refrescar los datos? | Automáticamente cada cinco minutos. |
| Esquema incompleto | ¿Qué hacer si falta una pestaña o un campo obligatorio? | Detener el análisis y explicar claramente qué falta. |
| Filas incompletas | ¿Qué hacer si una medición no tiene jugador o fecha? | Excluirla del cálculo e informar la cantidad excluida. |

## Decisiones de privacidad

- El enlace del Sheet no se incluye en el código ni en esta documentación.
- La hoja con datos reales deberá tener acceso restringido.
- Las credenciales y correos autorizados se configurarán en los secretos del alojamiento, nunca en el repositorio.
- No se solicitarán contraseñas de usuarios en el chat ni se reutilizarán contraseñas compartidas que se hayan expuesto.
