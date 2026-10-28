# Tareas — Spec 001: Origen seguro de datos

- [x] Crear configuración de secretos para OIDC, lista de cuentas autorizadas, ID del Sheet y cuenta de servicio.
- [x] Implementar inicio de sesión OIDC y bloquear cuentas que no estén autorizadas.
- [x] Implementar lectura de las tres pestañas privadas con una cuenta de servicio de solo lectura.
- [x] Normalizar encabezados y aplicar alias para jugador, fecha, categoría y demás campos estructurales.
- [x] Conservar automáticamente las nuevas columnas de medición sin tratarlas como campos estructurales.
- [x] Añadir asignación interactiva de campos estructurales desconocidos con estado limitado a la sesión.
- [x] Validar pestañas y campos obligatorios antes de entregar datos al análisis.
- [x] Excluir filas sin jugador o fecha y comunicar el conteo en la interfaz.
- [x] Configurar una caché con duración máxima de cinco minutos y un modo de actualización controlado.
- [x] Añadir pruebas unitarias con hojas ficticias para alias, columnas nuevas, campos faltantes y filas incompletas.
- [x] Verificar que ninguna etiqueta visible use el DNI y que los secretos no estén versionados.

La implementación y la configuración del repositorio están verificadas. La
prueba en producción confirma el acceso autorizado y la carga actual de datos;
queda pendiente comprobar el rechazo con una cuenta real que no figure en la
lista autorizada, sin modificar la lista de acceso de AMS.
