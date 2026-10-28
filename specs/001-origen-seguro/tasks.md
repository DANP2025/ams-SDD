# Tareas — Spec 001: Origen seguro de datos

- [ ] Crear configuración de secretos para OIDC, lista de cuentas autorizadas, ID del Sheet y cuenta de servicio.
- [ ] Implementar inicio de sesión OIDC y bloquear cuentas que no estén autorizadas.
- [ ] Implementar lectura de las tres pestañas privadas con una cuenta de servicio de solo lectura.
- [ ] Normalizar encabezados y aplicar alias para jugador, fecha, categoría y demás campos estructurales.
- [ ] Conservar automáticamente las nuevas columnas de medición sin tratarlas como campos estructurales.
- [ ] Añadir asignación interactiva de campos estructurales desconocidos con estado limitado a la sesión.
- [ ] Validar pestañas y campos obligatorios antes de entregar datos al análisis.
- [ ] Excluir filas sin jugador o fecha y comunicar el conteo en la interfaz.
- [ ] Configurar una caché con duración máxima de cinco minutos y un modo de actualización controlado.
- [ ] Añadir pruebas unitarias con hojas ficticias para alias, columnas nuevas, campos faltantes y filas incompletas.
- [ ] Verificar que ninguna etiqueta visible use el DNI y que los secretos no estén versionados.
