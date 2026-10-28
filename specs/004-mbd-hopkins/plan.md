# Plan — Spec 004: MBD Hopkins

## Flujo de usuario

1. Seleccionar categoría y uno o varios jugadores.
2. Seleccionar periodos Pre y Post.
3. Revisar cambios, incertidumbre, magnitudes estandarizadas y probabilidades disponibles.
4. Consultar etiquetas de beneficio/perjuicio solo para variables con dirección revisada, referenciada y aprobada.

## Modelo estadístico

- Usar el grupo de la categoría seleccionada en Pre como referencia.
- Calcular cambio `Post - Pre`, desviación estándar muestral de Pre, `SWC = 0.2 × SD` y tamaño del efecto.
- Mantener `ICC = 0.90`; calcular TE, error estándar e intervalo del 95% con las fórmulas de `spec.md`.
- Calcular probabilidades alrededor de `-SWC` y `+SWC` bajo el supuesto de distribución normal.
- Aplicar umbrales de certeza y sufijos `CLARO`/`NO CLARO` según la especificación.

## Dirección de las variables

Mantener un catálogo explícito por variable con: nombre reconocido, dirección deseable (`mayor`, `menor` o `sin dirección definida`), referencias científicas, población/protocolo de referencia y estado de validación. No inferir una dirección solo por el nombre. Si falta evidencia o aprobación, mostrar resultados descriptivos sin etiqueta direccional.

## Gráfico y mensajes

- Representar el intervalo calculado del 95% tanto en la tabla como en el Forest Plot.
- Mantener coherentes los umbrales `-SWC` y `+SWC`.
- Mostrar los supuestos ICC, normalidad y calidad de datos junto a la interpretación.
- Presentar resultados como apoyo al análisis profesional, no como decisiones automáticas.

## Validación

- Probar cálculos con ejemplos conocidos y casos límite.
- Verificar variables con dirección mayor, menor y sin dirección.
- Comprobar que intervalos de tabla y gráfico son idénticos.
- Revisar la evidencia científica y obtener validación profesional para el catálogo de direcciones.
