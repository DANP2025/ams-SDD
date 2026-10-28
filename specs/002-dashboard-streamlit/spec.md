# Spec 002 — Estructura del dashboard Streamlit

## Requisitos

- **REQ-001:** Cuando una persona autorizada abra el AMS, el sistema deberá mostrar Z-Score/Extrapolar como sección inicial.
- **REQ-002:** El dashboard deberá organizarse en una sola página, sin barra lateral de navegación.
- **REQ-003:** El dashboard deberá mostrar las secciones `Z-Score / Extrapolar`, `MBD Hopkins` y `SWC` como pestañas visibles.
- **REQ-004:** Mientras MBD Hopkins o SWC no estén implementados, al seleccionar esas pestañas el sistema deberá mostrar el aviso `Próximamente` y no presentar controles o resultados ficticios.
- **REQ-005:** Cuando no se pueda cargar el origen de datos, el dashboard deberá mostrar el mensaje de error y bloquear las funciones que dependen de esos datos.
- **REQ-006:** La interfaz deberá mantener etiquetas claras en español y no mostrar DNI como nombre visible de jugador.

## Fuera de alcance

- Implementar los cálculos MBD Hopkins o SWC.
- Añadir navegación lateral.
- Añadir una portada con indicadores o resultados agregados.
- Mostrar gráficos o tablas de análisis antes de validar los datos de entrada.

## Criterios de aceptación

- [ ] La primera sección que aparece es Z-Score / Extrapolar.
- [ ] No hay barra lateral de navegación.
- [ ] Las tres secciones acordadas son visibles en una sola página.
- [ ] MBD Hopkins y SWC muestran `Próximamente` mientras no estén implementadas.
- [ ] Los módulos pendientes no muestran resultados ficticios ni cálculos parciales.
- [ ] Los errores de carga impiden que el dashboard muestre análisis como si fueran válidos.
