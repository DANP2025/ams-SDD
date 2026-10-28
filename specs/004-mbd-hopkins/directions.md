# Direcciones de lectura MBD

Este catálogo define la dirección usada para traducir una variación numérica a
probabilidades de beneficio o perjuicio. No convierte un resultado en
diagnóstico ni reemplaza la interpretación del protocolo.

## Variables configuradas

| Dirección | Alias normalizados admitidos | Criterio |
|---|---|---|
| Mayor | VO2 max, VO2max, 30-15 IFT, 30-15 VIFT, VIFT | Se interpreta como una mayor capacidad aeróbica o velocidad final del test. |
| Mayor | Alt. Salto, Altura de salto, Jump Height, CMJ Height | Se interpreta como mayor altura de salto, si el campo mide altura y no tiempo de vuelo u otra variable derivada. |
| Mayor | Fuerza CMJ, CMJ Peak Force, Peak Force CMJ | Se interpreta como mayor fuerza pico de CMJ, con el mismo protocolo, unidades y criterio de normalización. |
| Mayor | Pot Pico, Potencia Pico, Peak Power | Se interpreta como mayor potencia pico; debe corresponder al mismo test y método de cálculo. |
| Mayor | Fuerza IMTP, IMTP Peak Force, Peak Force IMTP | Se interpreta como mayor fuerza pico del IMTP, manteniendo posición y protocolo. |
| Mayor | F0, V0, Vmax, Pmax, RF | Capacidades del perfil mecánico de sprint. La dirección positiva no significa que todas deban maximizarse de forma aislada: la interpretación del perfil depende del atleta y la distancia objetivo. |
| Mayor | RFD 100, RFD 150, RFD 250 | Se interpreta como mayor tasa de desarrollo de fuerza en esa ventana temporal y bajo el mismo protocolo. |

Solo se activan los alias escritos en el catálogo, comparados sin distinguir
mayúsculas, acentos o separadores. Se admite un sufijo de unidad o protocolo
después del alias (por ejemplo, `F0 (N/kg)`). Una variable no reconocida
—incluidas `DRF` y `RFD Dec`— permanece neutral. No se asigna dirección por
coincidencia parcial dentro del nombre.

## Alcance e interpretación

- Los rótulos `Beneficioso` y `Perjudicial` son lecturas probabilísticas con
  respecto a la dirección configurada, no conclusiones sobre salud o
  prescripciones de entrenamiento.
- Los parámetros del perfil fuerza-velocidad de sprint no describen un óptimo
  universal. La potencia máxima y el perfil fuerza-velocidad deben interpretarse
  según el atleta y la distancia de aceleración prevista.
- La dirección de las métricas de salto, fuerza y RFD supone que el nombre y la
  unidad reflejan realmente el indicador descrito. Si la columna corresponde a
  una fórmula distinta, no debe heredar automáticamente esa interpretación.
- Los colores verdes y rojos resaltan la dirección de la clasificación; `NO
  CLARO` se muestra en un tono más suave para no aparentar certeza.
- `CLARO`/`NO CLARO` y las etiquetas de certeza usan los umbrales de la
  especificación MBD y los supuestos del modelo (incluido ICC fijo de 0.90).

## Referencias verificadas

1. Hopkins WG, Marshall SW, Batterham AM, Hanin J. *Progressive statistics for
   studies in sports medicine and exercise science*. Med Sci Sports Exerc.
   2009;41(1):3-13. doi:
   [10.1249/MSS.0b013e31818cb278](https://doi.org/10.1249/MSS.0b013e31818cb278).
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/19092709/).
2. Samozino P, Peyrot N, Edouard P, et al. *Optimal mechanical force-velocity
   profile for sprint acceleration performance*. Scand J Med Sci Sports.
   2022;32(3):559-575. doi:
   [10.1111/sms.14097](https://doi.org/10.1111/sms.14097). El artículo describe
   un perfil óptimo individual dependiente de la potencia y la distancia, no
   una regla universal para maximizar cada componente.
3. Buchheit M. *The 30-15 Intermittent Fitness Test: Accuracy for Individualizing
   Interval Training of Young Intermittent Sport Players*. J Strength Cond Res.
   2008;22(2):365-374. doi:
   [10.1519/JSC.0b013e3181635b2e](https://doi.org/10.1519/JSC.0b013e3181635b2e).

La literatura respalda el significado general de estas pruebas, pero no
confirma por sí sola el protocolo, las unidades o la fórmula de cada columna
particular de AMS. Mantener `DRF`, `RFD Dec` y todo alias no listado como neutral
es intencional hasta verificar esos detalles.
