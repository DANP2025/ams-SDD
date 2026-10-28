# Tareas — Spec 005: SWC

- [x] Añadir selección explícita de categoría, variable, periodo Pre y periodo Post; representar a todos los jugadores de la categoría.
- [x] Preparar las mediciones Pre válidas del grupo de referencia seleccionado.
- [x] Calcular la desviación estándar muestral del grupo Pre.
- [x] Calcular cambio, SWC y tamaño estandarizado con las fórmulas acordadas.
- [x] Implementar la clasificación de magnitud por valor absoluto con límites 0.2, 0.6 y 1.2.
- [x] Mantener el signo del cambio visible junto a la etiqueta de magnitud.
- [x] Presentar un gráfico de dispersión por variable con un punto por jugador, Pre/Post, cambio, SWC, tamaño estandarizado y magnitud en el detalle.
- [x] Añadir franjas verdes para cambios positivos, rojas para negativos y grises para triviales, sin inferir beneficio o perjuicio.
- [x] Aumentar la tipografía, evitar etiquetas de magnitud superpuestas y habilitar zoom y desplazamiento del gráfico.
- [x] Limitar el eje estandarizado a ±6.5 SD e indicar valores exteriores con triángulos y su valor real en el detalle.
- [x] Evitar el solapamiento de etiquetas de puntos fuera de escala; mantener el nombre y el valor real en la información emergente.
- [x] Excluir edad y peso del selector de variables y del constructor del gráfico.
- [x] Mostrar un estado no disponible cuando falten datos, haya muestra insuficiente o SD sea cero.
- [x] Añadir la advertencia de interpretación contextual y de que magnitud no equivale a beneficio.
- [x] Añadir pruebas para valores límite, signos opuestos, datos faltantes y selección del SD de Pre.

## Validación de datos pendiente

- [ ] Confirmar con la fuente y el equipo de AMS la unidad y el protocolo de
  `Altura Salto`: en la aplicación publicada, los puntos observados para esta
  variable quedaron fuera del rango gráfico de ±6.5 SD. No cambiar los datos ni
  las unidades hasta verificar su significado.
