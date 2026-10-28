# Plan — Spec 005: SWC

## Flujo de usuario

1. Seleccionar categoría, variable y periodos Pre/Post.
2. Ver un punto por cada jugador válido de la categoría, con el resultado Post en X y el cambio estandarizado en Y.
3. Consultar en el detalle del punto los valores Pre/Post, cambio, SD Pre, SWC y magnitud.
4. Interpretar el signo como positivo o negativo, con la advertencia visible de que no equivale automáticamente a beneficio o perjuicio.

## Cálculo

Para cada variable, reunir las mediciones válidas de la categoría seleccionada en Pre. Calcular su desviación estándar muestral. Si existen al menos dos observaciones y la desviación es distinta de cero:

- `Cambio = Post - Pre`
- `SWC = 0.2 × SD_Pre`
- `Tamaño estandarizado = Cambio / SD_Pre`
- Clasificar `abs(Tamaño estandarizado)` con los límites `0.2`, `0.6` y `1.2`.

No usar la desviación de los cambios como denominador para este diseño Pre/Post. No convertir datos faltantes en cero.

## Presentación

- Presentar Pre, Post, cambio, tamaño estandarizado, SWC y magnitud en el detalle interactivo de cada punto.
- Mantener visible el signo aunque la categoría de magnitud se base en el valor absoluto.
- Mostrar franjas neutrales simétricas en ±0.2, ±0.6 y ±1.2 SD.
- Incluir una nota sobre la interpretación contextual y los límites convencionales de la escala.
- Evitar etiquetas de beneficio/perjuicio automáticas.

## Validación

- Probar valores alrededor de `0.2`, `0.6` y `1.2`, incluidos los límites exactos.
- Probar cambios positivos y negativos de igual magnitud.
- Probar datos faltantes, grupo Pre con menos de dos valores y desviación estándar cero.
- Verificar que se usa el SD de Pre del grupo de referencia y no el SD del cambio.
