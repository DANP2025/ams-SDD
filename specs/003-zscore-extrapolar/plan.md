# Plan — Spec 003: Z-Score / Extrapolar

## Flujo de usuario

1. Seleccionar mes y año con datos.
2. Seleccionar la categoría de los jugadores a consultar.
3. Elegir uno o varios jugadores de esa categoría.
4. Seleccionar la categoría de referencia.
5. Consultar tabla y radar con resultados disponibles y celdas vacías/no disponibles cuando falte información suficiente.

## Cálculo

Para cada variable, formar el grupo de referencia con mediciones válidas de la categoría de referencia en el periodo elegido. Excluir ceros de referencia. Calcular media y desviación estándar muestral; si hay menos de dos valores o la desviación estándar es cero, no calcular Z-Score para esa variable.

Para un jugador con evaluaciones repetidas en el mes, usar la fila de la fecha más reciente. Aplicar la fórmula confirmada y conservar el signo del resultado.

## Presentación

- Mostrar los valores de la tabla y el radar con la misma clasificación.
- Aplicar los intervalos y colores de la descripción funcional del proyecto.
- Mostrar una nota visible: los colores sitúan el valor frente a la referencia; no determinan por sí mismos si el cambio es beneficioso.
- Usar nombre/apellido o una etiqueta segura de jugador, nunca DNI.
- Distinguir “sin datos suficientes” de un valor igual a cero.

## Validación

- Probar límites exactos de cada intervalo.
- Probar ausencia de datos, cero en referencia, una sola observación y desviación estándar cero.
- Probar varias evaluaciones del mismo jugador dentro del mes.
- Probar selección de varios jugadores y consistencia tabla/radar.
