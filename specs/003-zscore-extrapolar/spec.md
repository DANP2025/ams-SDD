# Spec 003 — Z-Score / Extrapolar

## Requisitos

- **REQ-001:** Cuando la persona seleccione un mes y año, el sistema deberá limitar el análisis a mediciones de ese periodo.
- **REQ-002:** Cuando la persona seleccione una categoría de jugadores, el sistema deberá permitir elegir uno o varios jugadores de esa categoría.
- **REQ-003:** Cuando la persona seleccione una categoría de referencia, el sistema deberá calcular cada Z-Score con la distribución de esa categoría en el mismo mes y año.
- **REQ-004:** Cuando un jugador tenga varias evaluaciones en el mes, el sistema deberá usar la evaluación más reciente de ese mes.
- **REQ-005:** Para cada variable, el sistema deberá calcular `Z = (valor del jugador - media de referencia) / desviación estándar de referencia`.
- **REQ-006:** El sistema deberá calcular la desviación estándar de referencia con la convención muestral (`ddof = 1`), excluir valores de referencia iguales a cero y requerir al menos dos observaciones válidas con desviación estándar distinta de cero.
- **REQ-007:** Cuando no se pueda calcular un resultado por falta de datos o dispersión, el sistema deberá dejar la celda vacía o indicar que no está disponible; nunca deberá presentar el resultado como cero.
- **REQ-008:** El sistema deberá presentar los resultados en una tabla y un gráfico tipo radar.
- **REQ-009:** El sistema deberá clasificar los resultados con los intervalos acordados: Excelente (`Z > 2`), Muy Bueno (`1 < Z <= 2`), Bueno (`0.5 < Z <= 1`), Promedio/Estable (`-0.5 <= Z <= 0.5`), Debajo del Promedio (`-1 <= Z < -0.5`), Pobre (`-2 <= Z < -1`), Muy Pobre (`-3 <= Z < -2`) y Extremadamente Pobre (`Z < -3`).
- **REQ-010:** El sistema deberá explicar que los colores representan la posición estadística respecto a la media, no un beneficio deportivo universal.
- **REQ-011:** Cuando haya más de un jugador seleccionado, el sistema deberá mantener identificadores legibles de jugador sin mostrar el DNI.

## Fuera de alcance

- Predecir resultados futuros; “Extrapolar” solo significa comparar con una población de referencia observada.
- Interpretar automáticamente si un valor alto o bajo es beneficioso para cada variable.
- Calcular MBD Hopkins o SWC.
- Sustituir la evaluación de profesionales del deporte o realizar diagnósticos médicos.

## Criterios de aceptación

- [x] Los filtros de mes, año, categoría de jugadores, jugadores y categoría de referencia controlan el conjunto de datos usado.
- [x] Para mediciones repetidas de un jugador en el mismo mes se usa la fecha más reciente.
- [x] La media y la desviación de referencia usan observaciones válidas del mismo mes y categoría.
- [x] Los ceros de la referencia no participan y se requieren al menos dos observaciones válidas.
- [x] Una desviación estándar igual a cero o datos insuficientes producen un resultado no disponible, nunca cero.
- [x] Tabla y radar coinciden en los valores y clasificación de Z-Score.
- [x] Los límites de clasificación se aplican correctamente, incluidos `Z = 2`, `Z = -0.5` y `Z = -1`.
- [x] La interfaz advierte que “por encima de la media” no significa automáticamente “mejor”.
- [x] El DNI no se muestra en etiquetas ni resultados visibles.
