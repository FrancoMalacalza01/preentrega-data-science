# Diseño de completación y productividad de pozos no convencionales en Vaca Muerta

Proyecto final del curso de Ciencia de Datos — **EnergIA Digital 2026**.

**Integrantes:** Franco Malacalza · Martín Gerbaldo · Carolina Bailón

## El problema

Un pozo no convencional no produce por sí solo: la roca de Vaca Muerta tiene el petróleo
atrapado adentro y hay que agrietarla. Para eso se perfora un tramo horizontal de varios
kilómetros y se bombea agua con arena a alta presión, en decenas de etapas sucesivas. La arena
queda trabando las fracturas para que no se cierren.

Ese conjunto de decisiones —cuán largo es el tramo horizontal, cuántas etapas, cuánta arena y
cuánta agua por etapa— es el **diseño de completación**, y concentra buena parte del costo de
terminar el pozo. La operadora lo define antes de saber cuánto va a producir: una vez bombeada,
la arena no se recupera. Sobreinvertir es plata enterrada; subinvertir deja petróleo en el
subsuelo.

## Objetivo

Entender **cómo se diseña hoy un pozo no convencional en Vaca Muerta y cómo cambió ese diseño en
la última década**, y dejar construido un dataset limpio que permita estimar la producción
esperada de un pozo a partir de su diseño.

## Datos

| Fuente | Contenido | Período | Registros |
|---|---|---|---|
| Secretaría de Energía — **Datos de fractura de pozos (Adjunto IV)** | Una fila por operación de fractura: longitud de rama, etapas, arena nacional e importada, agua, presión máxima, potencia de equipos, operadora y formación | 2009 → 2026, actualización diaria | 4.890 |

https://datos.energia.gob.ar/dataset/datos-de-fractura-de-pozos-adjunto-iv

El archivo está incluido en el repositorio, en `data/fractura_adjunto_iv.csv`.

## Alcance elegido

**Pozos horizontales con rama de al menos 500 m.** El dataset original mezcla dos poblaciones que
no son comparables: 2.054 de los 4.890 registros (42%) son pozos verticales convencionales, con
una escala de operación completamente distinta. Además, en un pozo vertical las variables de
intensidad por metro serían indefinidas.

Tras la limpieza quedan **2.603 pozos**: 2.590 en Cuenca Neuquina y 2.517 con Vaca Muerta como
formación productiva.

## Estructura del repositorio

```
preentrega-data-science/
├── README.md
├── requirements.txt
├── data/
│   └── fractura_adjunto_iv.csv     # dataset original del portal, sin modificar
└── notebooks/
    └── 01_eda_preentrega2.ipynb    # análisis exploratorio completo
```

Al ejecutar el notebook se crea `data/processed/` con el dataset limpio. No está versionado
porque se regenera solo.

## Cómo reproducir

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_eda_preentrega2.ipynb
```

El notebook corre de punta a punta con el CSV que ya está en el repositorio: no hace falta
descargar nada. Está ejecutado, así que los resultados y los gráficos se ven directamente en
GitHub sin correr nada.

## Qué hace el notebook

Sigue la estructura de la guía de la cursada, en tres partes:

| Parte | Puntos | Contenido |
|---|---|---|
| **1 — Análisis exploratorio** | 1 a 12 | Conocer el dataset, identificar las variables, completitud, duplicados, categóricas, unicidad de escritura, distribuciones, atípicos y su comportamiento, relación entre variables, comparación de grupos y variable objetivo |
| **2 — Transformación y limpieza** | 13 a 17 | Conversión de fechas, normalización de categorías, faltantes, validación de errores y definición del alcance, consolidación de cargas parciales |
| **3 — Feature engineering** | 18 | Creación de las variables de intensidad, control de plausibilidad y encoding |

La Parte 1 explora el dataset completo sin modificarlo. El filtro a pozos horizontales es una
decisión documentada de la Parte 2, no un supuesto de partida.

## Principales hallazgos del EDA

- **El dataset mezcla pozos verticales y horizontales.** Un vertical mediano bombea 0 tn de arena
  y 430 m³ de agua en 3 etapas; uno horizontal, 8.576 tn y 54.314 m³ en 38 etapas. El cruce con
  `tipo_reservorio` lo confirma: los verticales son convencionales y los horizontales no.

- **El grano no es un pozo por fila.** Hay 4.890 filas para 4.646 pozos. Los 244 registros
  excedentes comparten pozo *y* fecha de fractura y reparten las etapas entre varias filas: son
  cargas parciales de una misma operación, no refracturas. Se consolidan sumando las magnitudes
  aditivas y tomando el máximo de las propiedades del pozo.

- **Los ceros son el problema de calidad, no los nulos.** Solo tres columnas tienen nulos, pero
  hay ceros centinela en longitud de rama (el valor 3,0 m aparece 63 veces), presión, potencia y
  agua. Un equipo de fractura no opera a cero psi.

- **`co2_inyectado_m3` no aporta nada, pero no por lo obvio.** Tiene 159 registros con valor
  positivo, y los 159 son pozos verticales. Dentro de la población analizada es idénticamente
  cero. Mirando solo el porcentaje de ceros global la conclusión habría sido otra.

- **La intensidad de fractura se amesetó.** Entre 2016 y 2025 la arena por pozo se triplicó, pero
  eso es efecto de escala: la rama se duplicó. La arena *por metro* creció 29% hasta 2019 y
  apenas 9% en los seis años siguientes, mientras el espaciamiento entre etapas se apretaba de
  78 m a 59 m. La industria dejó de mejorar bombeando más arena por metro.

- **Cada operadora tiene una estrategia identificable.** Vista Energy usa la rama más larga
  (2.911 m), la mayor intensidad (4,17 tn/m) y el espaciamiento más apretado (58 m), y lo repite
  de forma muy estandarizada. Total Austral está en el extremo opuesto (1.970 m y 2,48 tn/m) y
  con mucha más dispersión.

- **Hay multicolinealidad severa.** `cantidad_fracturas` y `arena_total_tn` correlacionan 0,95, y
  ambas con la longitud de rama cerca de 0,89. Para modelar hay que quedarse con una variable de
  escala más las de intensidad, que son casi ortogonales entre sí.

## Limitaciones y sesgos

- **Concentración en un operador.** YPF representa el 53% de los pozos, así que cualquier
  conclusión refleja sobre todo su forma de completar.
- **Concentración geológica.** El 97% de los pozos son de Vaca Muerta; las conclusiones no se
  extrapolan a otras formaciones no convencionales.
- **Diseño confundido con geología.** Cada operadora trabaja en áreas de calidad de roca distinta,
  así que el efecto del diseño está mezclado con el de la roca. El análisis describe asociaciones,
  no efectos causales.
- **No hay contrafactual.** El dataset solo contiene pozos efectivamente fracturados: no se puede
  saber qué habría producido un pozo con otro diseño.
- **Datos preliminares.** La Secretaría de Energía los publica como sujetos a revisión, y el año
  en curso está incompleto.
