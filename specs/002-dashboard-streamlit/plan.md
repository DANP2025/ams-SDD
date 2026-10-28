# Plan — Spec 002: Estructura del dashboard

## Diseño lógico

1. Validar autenticación y autorización antes de mostrar los datos o los módulos.
2. Construir una sola página Streamlit sin navegación lateral.
3. Presentar las secciones acordadas en una fila de pestañas.
4. Seleccionar Z-Score / Extrapolar como vista inicial y alojar allí los filtros y resultados de la primera versión.
5. Mantener MBD Hopkins y SWC como pestañas informativas `Próximamente`; no cargar datos ni simular resultados desde ellas.
6. Mostrar los errores de origen de datos de forma explícita y no renderizar análisis dependientes de una carga fallida.

## Criterios de presentación

- Los encabezados y controles visibles estarán en español.
- Las etiquetas de jugador no usarán el DNI.
- El panel lateral no se utilizará para navegación o selección de análisis.
- El dashboard no mostrará valores de ejemplo en producción.
