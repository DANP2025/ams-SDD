# Spec 002 — Estructura del dashboard Streamlit

## Requisitos

- **REQ-001:** Cuando una persona autorizada abra el AMS, el sistema deberá mostrar Z-Score/Extrapolar como sección inicial.
- **REQ-002:** El dashboard deberá organizarse en una sola página, sin barra lateral de navegación.
- **REQ-003:** El dashboard deberá mostrar las secciones `Z-Score / Extrapolar`, `MBD Hopkins` y `SWC` como pestañas visibles.
- **REQ-004:** Las pestañas MBD Hopkins y SWC deberán presentar sus análisis implementados y no mostrar controles ni resultados ficticios.
- **REQ-005:** Cuando no se pueda cargar el origen de datos, el dashboard deberá mostrar el mensaje de error y bloquear las funciones que dependen de esos datos.
- **REQ-006:** La interfaz deberá mantener etiquetas claras en español y no mostrar DNI como nombre visible de jugador.

## Fuera de alcance

- Añadir módulos de análisis distintos de Z-Score, MBD Hopkins y SWC.
- Añadir navegación lateral.
- Añadir una portada con indicadores o resultados agregados.
- Mostrar gráficos o tablas de análisis antes de validar los datos de entrada.

## Criterios de aceptación

- [x] La primera sección que aparece es Z-Score / Extrapolar.
- [x] No hay barra lateral de navegación.
- [x] Las tres secciones acordadas son visibles en una sola página.
- [x] MBD Hopkins y SWC muestran sus análisis implementados en lugar de `Próximamente`.
- [x] No se muestran resultados ficticios ni cálculos parciales.
- [x] Los errores de carga impiden que el dashboard muestre análisis como si fueran válidos.
