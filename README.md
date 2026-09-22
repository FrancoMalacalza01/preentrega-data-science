# Diseño de completación y productividad de pozos no convencionales en Vaca Muerta

Proyecto final del curso de Ciencia de Datos — **EnergIA Digital 2026**.

**Integrantes:** Franco Malacalza · Martín Gerbaldo · Carolina Bailon

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

**Objetivo del modelo:** estimar la producción acumulada de petróleo de un pozo en sus primeros
12 meses (m³) a partir de su diseño de completación y su ubicación geológica, para poder comparar
escenarios de diseño antes de perforar.

## Datos

| Fuente | Contenido | Período | Uso |
|---|---|---|---|
| Secretaría de Energía — **Datos de fractura de pozos (Adjunto IV)** | Una fila por operación de fractura: longitud de rama, etapas, arena nacional e importada, agua, presión máxima, potencia de equipos, operadora, formación | 2009 → 2026, actualización diaria | Base del análisis |
| Secretaría de Energía — **Producción de petróleo y gas por pozo (Capítulo IV)** | Producción mensual de petróleo y gas por pozo | 2006 → 2026 | Variable objetivo (Pre-entrega 3) |

Ambas tablas se vinculan por el identificador de pozo `idpozo`. Del Capítulo IV solo sirven los
archivos que dicen *"con identificador"*: los de *"DDJJ abiertas y cerradas"* no traen `idpozo` y
no permiten el cruce.

- https://datos.energia.gob.ar/dataset/datos-de-fractura-de-pozos-adjunto-iv
- https://datos.energia.gob.ar/dataset/produccion-de-petroleo-y-gas-por-pozo

## Alcance elegido

**Pozos horizontales con rama de al menos 500 m.** El dataset original mezcla dos poblaciones que
no son comparables: 2.054 de los 4.890 registros (42%) son pozos verticales convencionales, con
una escala de operación completamente distinta. Además, en un pozo vertical las variables de
intensidad por metro serían indefinidas.

Tras la limpieza quedan **2.603 pozos**: 2.590 en Cuenca Neuquina y 2.517 con Vaca Muerta como
formación productiva. Es coherente con la realidad de la industria argentina, donde el desarrollo
no convencional es prácticamente sinónimo de Vaca Muerta.

## Estructura del repositorio

```
preentrega-data-science/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/                            # dataset original del portal, sin modificar
│   │   └── fractura_adjunto_iv.csv
│   └── processed/                      # generados por el notebook y por src/
│       ├── pozos_analitico.csv         # 2.603 pozos, categóricas como texto
│       └── pozos_encoded.csv           # mismo dataset, listo para modelar
├── notebooks/
│   └── 01_eda_preentrega2.ipynb        # Pre-entrega 2: el EDA completo
├── reports/
│   └── figures/                        # gráficos exportados por el notebook
└── src/
    ├── descargar_fractura.py           # baja el Adjunto IV vía la API del portal
    └── preparar_dataset.py             # pipeline de limpieza → data/processed/
```

El notebook es el documento principal: explica y justifica cada decisión. `src/preparar_dataset.py`
ejecuta ese mismo pipeline como script, y produce exactamente los mismos dos archivos.

Para el detalle técnico de cómo está armado todo —el recorrido de los datos, qué hace cada
archivo, cómo se resuelven las rutas y las decisiones metodológicas— ver
[`docs/COMO_FUNCIONA.md`](docs/COMO_FUNCIONA.md).

## Cómo reproducir

```bash
pip install -r requirements.txt

python src/descargar_fractura.py     # opcional: el CSV ya está versionado
python src/preparar_dataset.py       # regenera data/processed/

jupyter notebook notebooks/01_eda_preentrega2.ipynb
```

El notebook corre de punta a punta solo con el CSV de fractura. La sección 11, que construye la
variable objetivo cruzando con la producción, se activa sola si encuentra los archivos del
Capítulo IV en `data/`; si no están, lo informa y sigue sin fallar.

## Avance por pre-entregas

- [x] **Pre-entrega 2 — Exploración, transformación y visualización.** Perfilado de las 30
  columnas, reglas de calidad contra el dominio, análisis de sensibilidad del umbral de corte,
  consolidación por pozo, imputación, 11 variables derivadas de intensidad, encoding y 8
  visualizaciones. Ver `notebooks/01_eda_preentrega2.ipynb`.
- [ ] **Pre-entrega 3 — Modelo supervisado.** Regresión multi-horizonte (3, 6 y 12 meses) con
  partición temporal, línea base por formación y optimización de hiperparámetros.
- [ ] **Modelo no supervisado.** Clustering de arquetipos de diseño (K-Means y DBSCAN) usando
  solo variables de completación, y comparación de productividad entre grupos.
- [ ] **Entrega final.** API de predicción con explicación de los resultados, documentación y
  defensa oral.

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
  78 m a 59 m. La industria dejó de mejorar bombeando más arena por metro. Es la hipótesis
  central que el modelo de la Pre-entrega 3 tiene que contrastar.

- **Cada operadora tiene una estrategia identificable.** Vista Energy usa la rama más larga
  (2.911 m), la mayor intensidad (4,17 tn/m) y el espaciamiento más apretado (58 m), y lo repite
  de forma muy estandarizada. Total Austral está en el extremo opuesto (1.970 m y 2,48 tn/m) y
  con mucha más dispersión.

- **Hay multicolinealidad severa.** `cantidad_fracturas` y `arena_total_tn` correlacionan 0,95, y
  ambas con la longitud de rama cerca de 0,89. Para modelar hay que quedarse con una variable de
  escala más las de intensidad, que son casi ortogonales entre sí.

## Limitaciones y sesgos

- **Concentración en un operador.** YPF representa el 53% de los pozos, así que el modelo va a
  aprender sobre todo su forma de completar y será menos confiable para operadoras chicas.
- **Concentración geológica.** El 97% de los pozos son de Vaca Muerta; las conclusiones no se
  extrapolan a otras formaciones no convencionales.
- **Diseño confundido con geología.** Cada operadora trabaja en áreas de calidad de roca distinta,
  así que el efecto del diseño está mezclado con el de la roca. El proyecto estima asociaciones,
  no efectos causales.
- **No hay contrafactual.** El dataset solo contiene pozos efectivamente fracturados: no se puede
  saber qué habría producido un pozo con otro diseño.
- **Datos preliminares.** La Secretaría de Energía los publica como sujetos a revisión, y el año
  en curso está incompleto.
- **Sesgo de supervivencia temporal.** Exigir 12 meses completos de producción excluirá a los
  pozos más recientes, que son los de diseño más moderno.
