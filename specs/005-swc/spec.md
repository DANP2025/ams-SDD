# Spec 005 — SWC (Smallest Worthwhile Change)

## Requisitos

- **REQ-001:** Cuando la persona seleccione categoría, variable y periodos Pre y Post, el sistema deberá comparar los periodos para todos los jugadores de esa categoría y mostrar un punto por jugador válido.
- **REQ-002:** Para el diseño Pre/Post, el sistema deberá usar como referencia la desviación estándar muestral de la categoría seleccionada en el periodo Pre, no la desviación de los cambios ni la desviación individual del jugador.
- **REQ-003:** El sistema deberá calcular `Cambio = Post - Pre`, `SWC = 0.2 × SD de Pre` y `tamaño estandarizado = Cambio / SD de Pre`.
- **REQ-004:** El sistema deberá clasificar la magnitud absoluta del tamaño estandarizado con los límites de Hopkins: Trivial (`|efecto| < 0.2`), Small (`0.2 <= |efecto| < 0.6`), Moderate (`0.6 <= |efecto| < 1.2`) y Large (`|efecto| >= 1.2`).
- **REQ-005:** El sistema deberá conservar y mostrar el signo del cambio por separado de la etiqueta de magnitud.
- **REQ-006:** El sistema deberá explicar que las etiquetas describen magnitud estandarizada y no implican por sí mismas beneficio o perjuicio deportivo.
- **REQ-007:** Cuando falte Pre o Post, haya menos de dos mediciones válidas en el grupo Pre o su desviación estándar sea cero, el sistema deberá marcar el resultado como no disponible, nunca como cero.
- **REQ-008:** El sistema deberá mostrar un gráfico de dispersión por variable con el resultado Post en el eje X, el cambio estandarizado en el eje Y y un punto por jugador; el detalle interactivo deberá distinguir Pre, Post, cambio absoluto, SD de referencia, SWC y magnitud.
- **REQ-009:** El sistema deberá advertir que los umbrales de Hopkins son referencias convencionales que requieren revisión en el contexto de la población, variable y protocolo.

## Fuera de alcance

- Interpretar automáticamente que una magnitud positiva es beneficiosa o que una negativa es perjudicial.
- Estimar probabilidades de beneficio/perjuicio o incertidumbre del cambio; pertenece al módulo MBD Hopkins.
- Diagnosticar lesiones o prescribir entrenamiento.
- Usar una desviación estándar individual o la desviación de los cambios como sustituto silencioso de la desviación estándar de Pre del grupo.

## Criterios de aceptación

- [x] La categoría, variable y periodos Pre/Post se seleccionan explícitamente y el gráfico incluye los jugadores con resultados válidos de esa categoría.
- [x] La desviación de referencia procede de la categoría seleccionada en Pre y es muestral (`ddof = 1`).
- [x] El cambio, SWC y tamaño estandarizado coinciden con las fórmulas especificadas.
- [x] Las fronteras `0.2`, `0.6` y `1.2` producen, respectivamente, Small, Moderate y Large al alcanzar el umbral.
- [x] La clasificación usa la magnitud absoluta, mientras el signo permanece visible por separado.
- [x] Valores faltantes, muestra insuficiente o desviación cero se muestran como no disponibles.
- [x] La interfaz muestra el gráfico SWC por variable y distingue el signo del cambio de una interpretación de beneficio/perjuicio.
- [x] Las franjas de magnitud son simétricas y usan los umbrales estandarizados 0.2, 0.6 y 1.2.
