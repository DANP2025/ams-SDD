# Aclaraciones — Spec 003

| Tema | Pregunta | Respuesta |
|---|---|---|
| Periodo | ¿Cómo seleccionar las mediciones? | Por mes y año. |
| Jugadores | ¿Cómo elegir deportistas para comparar? | Elegir una categoría de jugadores y uno o varios jugadores. |
| Referencia | ¿Contra qué población comparar? | Elegir una categoría de referencia para el mismo periodo. |
| Evaluaciones repetidas | ¿Qué hacer si un jugador tiene varias evaluaciones en el mes? | Usar la evaluación más reciente del mes. |
| Colores | ¿Cómo explicar los colores cuando la dirección deseable depende de la variable? | Mantener colores según el signo del Z-Score y mostrar una nota de que no representan beneficio deportivo universal. |
| Presentación | ¿Qué visualizaciones incluir? | Tabla de resultados y gráfico radar. |
| Referencia insuficiente | ¿Qué hacer si no hay suficiente dispersión o datos? | Mostrar resultado vacío/no disponible, nunca cero. |

## Fórmula y clasificación confirmadas

- `Z = (valor del jugador - media de referencia) / desviación estándar de referencia`.
- Desviación estándar muestral (`ddof = 1`).
- Se excluyen ceros de la población de referencia y se requieren al menos dos observaciones válidas.
- La desviación estándar de referencia debe ser distinta de cero.
- Los intervalos de clasificación están definidos en `spec.md`.
