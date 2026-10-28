# Spec 001 — Origen seguro de datos

## Requisitos

- **REQ-001:** Cuando una persona no haya iniciado sesión, el sistema deberá impedir el acceso a cualquier dato del AMS.
- **REQ-002:** Cuando una persona inicie sesión, el sistema deberá permitirle continuar únicamente si su correo está en la lista de personas autorizadas.
- **REQ-003:** Cuando la persona autorizada acceda, el sistema deberá leer las pestañas `Base de datos`, `Rendimiento` y `Plat de fuerza` desde el Google Sheet privado mediante una cuenta de servicio.
- **REQ-004:** Cuando el sistema cargue encabezados, deberá reconocer variantes de mayúsculas, tildes y separadores, además de los alias configurados para campos como jugador, fecha y categoría.
- **REQ-005:** Cuando se agregue una columna nueva de medición, el sistema deberá conservarla como una variable disponible sin exigir cambios de código.
- **REQ-006:** Cuando un nombre nuevo corresponda a un campo estructural obligatorio y no pueda identificarse, el sistema deberá solicitar una asignación con controles de la interfaz y conservarla durante la sesión actual.
- **REQ-007:** Cuando una pestaña o campo obligatorio no esté disponible, el sistema deberá detener el análisis y explicar claramente qué falta, sin presentar resultados parciales como válidos.
- **REQ-008:** Cuando una fila de medición no tenga jugador o fecha, el sistema deberá excluirla de los cálculos y mostrar cuántas filas se excluyeron.
- **REQ-009:** Cuando cambien los datos de la hoja, el sistema deberá refrescar la copia en caché como máximo cada cinco minutos.
- **REQ-010:** Cuando se produzca un error de acceso o de estructura, el sistema deberá mostrar una explicación accionable y no sustituir el error por datos vacíos o valores cero.
- **REQ-011:** El sistema no deberá mostrar DNI como etiqueta visible de jugador ni incluir credenciales en el código fuente.

## Fuera de alcance

- Publicar o compartir el Google Sheet con datos reales de manera abierta.
- Editar datos de jugadores desde el dashboard.
- Recordar asignaciones de columnas entre sesiones o entre usuarios.
- Calcular Z-Score, MBD o SWC; esos cálculos pertenecen a sus especificaciones respectivas.
- Guardar datos personales fuera del Google Sheet de origen.

## Criterios de aceptación

- [ ] Una cuenta que no figure en la lista autorizada no puede ver ni cargar datos. (Pendiente de comprobar con una cuenta real no autorizada.)
- [x] El sistema accede únicamente a la hoja privada configurada y a las tres pestañas esperadas.
- [x] Variaciones de mayúsculas, tildes y separadores no impiden reconocer encabezados conocidos.
- [x] Una métrica nueva se conserva como columna disponible.
- [x] Un campo estructural desconocido presenta una asignación seleccionable y esta dura solo la sesión actual.
- [x] Una pestaña o campo obligatorio faltante bloquea el análisis y produce un mensaje claro.
- [x] Las filas sin jugador o fecha quedan fuera del cálculo y se informa su cantidad.
- [x] Los cambios de datos se reflejan en un plazo máximo de cinco minutos.
- [x] Los errores de acceso o esquema no se convierten en resultados vacíos o en ceros.
- [x] El DNI no se muestra en tablas, filtros o etiquetas visibles del dashboard.
