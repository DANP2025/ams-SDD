# Spec 004 — MBD Hopkins

## Requisitos

- **REQ-001:** Cuando la persona seleccione categoría, uno o varios jugadores y periodos Pre y Post, el sistema deberá comparar las mediciones de esos periodos.
- **REQ-002:** Para cada variable, el sistema deberá calcular `Cambio = Post - Pre` y obtener la desviación estándar muestral de la categoría de referencia en Pre.
- **REQ-003:** El sistema deberá calcular `SWC = 0.2 × SD de Pre` y `tamaño del efecto = Cambio / SD de Pre`.
- **REQ-004:** El sistema deberá mantener el ICC fijo en `0.90`, calcular `TE = SD de Pre × sqrt(1 - ICC)`, `SE del cambio = TE × sqrt(2)` y el intervalo del 95% como `Cambio ± 1.96 × SE del cambio`.
- **REQ-005:** El sistema deberá estimar las probabilidades de beneficio, perjuicio y cambio trivial con la distribución normal y los umbrales `+SWC` y `-SWC`.
- **REQ-006:** Antes de asignar etiquetas beneficiosas o perjudiciales, el sistema deberá usar una dirección deseable por variable respaldada por una revisión de literatura y aprobada para el AMS.
- **REQ-007:** Cuando no haya una dirección deseable documentada para una variable, el sistema deberá mostrar el cambio y su incertidumbre sin etiquetarlo como beneficio o perjuicio.
- **REQ-008:** Cuando haya datos faltantes, menos de dos observaciones válidas en Pre o desviación estándar cero, el sistema deberá marcar el resultado como no disponible.
- **REQ-009:** El gráfico deberá usar los mismos límites del intervalo del 95% que la tabla y representar las zonas perjudicial, trivial y beneficiosa según la dirección documentada.
- **REQ-010:** El sistema deberá clasificar la certeza con los umbrales acordados: Casi Seguro (>99.5%), Muy Probable (>95%), Probable (>75%), Posible (>25%) y Trivial cuando ninguna probabilidad de beneficio o perjuicio supere 25%.
- **REQ-011:** El sistema deberá marcar `NO CLARO` cuando las probabilidades de beneficio y perjuicio superen ambas el 5%; en caso contrario, marcar `CLARO`.
- **REQ-012:** El sistema deberá explicar que las probabilidades dependen de los supuestos del modelo y no reemplazan el criterio profesional.

## Fuera de alcance

- Diagnosticar lesiones o indicar tratamientos.
- Inferir automáticamente que un cambio es beneficioso basándose únicamente en una palabra del nombre de la variable.
- Usar un ICC distinto de `0.90` en la primera versión MBD.
- Presentar barras de error diferentes del intervalo calculado en la tabla.

## Criterios de aceptación

- [ ] Cambio, SWC, tamaño del efecto, TE, error estándar e intervalo del 95% coinciden con las fórmulas de esta especificación.
- [ ] Las probabilidades de beneficio, perjuicio y trivialidad se calculan alrededor de los umbrales SWC.
- [ ] Las etiquetas de dirección se muestran solo para variables con dirección aprobada y documentada.
- [ ] Variables sin dirección documentada presentan resultados neutrales sin etiquetado de beneficio/perjuicio.
- [ ] Tabla y gráfico muestran el mismo intervalo del 95%.
- [ ] Se aplica correctamente `CLARO`/`NO CLARO` y los umbrales de certeza.
- [ ] Datos ausentes, muestra insuficiente o desviación estándar cero no generan resultados ficticios.
- [ ] La interfaz presenta los supuestos del modelo y no comunica un diagnóstico.
