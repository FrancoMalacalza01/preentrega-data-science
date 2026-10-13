# Diseño de completación y productividad de pozos no convencionales en Vaca Muerta

Proyecto final del curso de Ciencia de Datos — **EnergIA Digital 2026**.

**Integrantes:** Carolina Bailón · Martín Gerbaldo · Franco Malacalza

Trabajo grupal. Las decisiones de alcance, criterio y metodología las discutimos y acordamos
entre los tres; nos apoyamos en herramientas de IA como copiloto, y lo documentamos al final
de este README.

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

Estimar **cuánto petróleo va a producir un pozo en su primer año a partir de las decisiones de
diseño que se toman antes de fracturarlo**, y entender cómo cambió ese diseño en la última década.

Es un problema de regresión supervisada: la variable a predecir son los metros cúbicos de petróleo
acumulados en los primeros 12 meses de producción.

## Datos

Tres datasets abiertos de la Secretaría de Energía, todos incluidos en el repositorio:

| Fuente | Contenido | Período | Registros |
|---|---|---|---|
| **Datos de fractura de pozos (Adjunto IV)** | Una fila por operación de fractura: longitud de rama, etapas, arena nacional e importada, agua, presión máxima, potencia de equipos, operadora y formación | 2009 → 2026 | 4.890 |
| **Producción de pozos de gas y petróleo** | Una fila por pozo y mes: producción de petróleo y gas | 2006 → 2026 | 136.380 |
| **Listado de pozos** | Coordenadas, cota y profundidad de cada pozo | — | 2.282 |

- https://datos.energia.gob.ar/dataset/datos-de-fractura-de-pozos-adjunto-iv
- https://datos.energia.gob.ar/dataset/produccion-de-pozos-de-gas-y-petroleo-por-pozo-y-mes
- https://datos.energia.gob.ar/dataset/listado-de-pozos-cargados-por-empresas-operadoras

El dataset de producción original pesa **1,4 GB** repartido en archivos anuales que cubren todos los
pozos del país. Lo que está en el repositorio es un recorte propio a los pozos de nuestro alcance y
a las cinco columnas que usamos: **1,3 MB** con la misma información útil. El código del recorte
está documentado en el anexo del notebook de modelado.

## Alcance elegido

**Pozos horizontales con rama de al menos 500 m.** El dataset original mezcla dos poblaciones que
no son comparables: 2.054 de los 4.890 registros (42%) son pozos verticales convencionales, con una
escala de operación completamente distinta. Además, en un pozo vertical las variables de intensidad
por metro serían indefinidas, porque habría que dividir por cero.

Tras la limpieza nos quedamos con **2.603 pozos**: 2.590 en Cuenca Neuquina y 2.517 con Vaca Muerta
como formación productiva.

## Estructura del repositorio

```
preentrega-data-science/
├── README.md
├── requirements.txt
├── data/
│   ├── fractura_adjunto_iv.csv       # dataset original del portal, sin modificar
│   ├── produccion_filtrada.csv.gz    # producción mensual, recortada a nuestro alcance
│   └── pozos_ubicacion.csv           # coordenadas y cota de los pozos
└── notebooks/
    ├── 01_eda_preentrega2.ipynb      # análisis exploratorio y limpieza
    └── 02_modelado_preentrega3.ipynb # modelos supervisados, evaluación y métricas
```

Al ejecutar el primer notebook se crea `data/processed/pozos_analitico.csv` con el dataset limpio y
enriquecido. No lo versionamos porque se regenera solo.

## Cómo reproducir

```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_eda_preentrega2.ipynb
jupyter notebook notebooks/02_modelado_preentrega3.ipynb
```

Los dos notebooks corren de punta a punta con los archivos que ya están en el repositorio: no hace
falta descargar nada. El segundo es autocontenido —vuelve a aplicar el pipeline de limpieza del
primero— así que puede correrse solo. Ambos están ejecutados, así que los resultados y los gráficos
se ven directamente en GitHub.

**Las versiones están fijadas con `==`**, y ejecutado así el resultado es idéntico al que está
guardado: los mismos números y los mismos gráficos, hasta el píxel. Hacen falta las dos cosas para
que eso valga. La semilla (`SEMILLA = 42`) fija los resultados numéricos, pero no el renderizado:
entre versiones de `matplotlib` cambia el antialiasing y hasta el ancho en píxeles de una figura.
Y ninguna fecha sale del reloj de la máquina —la referencia para descartar fechas imposibles es la
fecha de publicación del propio archivo—, así que correrlo mañana da lo mismo que correrlo hoy.

Está verificado con **Python 3.13.16**. Si tu versión de Python no tiene ruedas para alguno de los
paquetes, cambiá el `==` por `>=` en esa línea: el análisis no cambia, solo se re-renderizan los
gráficos.

## Qué hace cada notebook

### `01_eda_preentrega2.ipynb` — exploración y limpieza

Sigue la estructura de la guía de la cursada, en tres partes:

| Parte | Puntos | Contenido |
|---|---|---|
| **1 — Análisis exploratorio** | 1 a 12 | Conocer el dataset, identificar las variables, completitud, duplicados, categóricas, unicidad de escritura, distribuciones, atípicos y su comportamiento, relación entre variables, comparación de grupos y variable objetivo |
| **2 — Transformación y limpieza** | 13 a 17 | Conversión de fechas, normalización de categorías, faltantes, validación de errores y definición del alcance, consolidación de cargas parciales |
| **3 — Feature engineering** | 18 | Creación de las variables de intensidad y control de plausibilidad |

En la Parte 1 exploramos el dataset completo sin modificarlo. El filtro a pozos horizontales es una
decisión que tomamos y documentamos en la Parte 2, no un supuesto de partida.

### `02_modelado_preentrega3.ipynb` — modelos, evaluación y métricas

| Parte | Puntos | Contenido |
|---|---|---|
| **1** | 1 a 5 | Cruce con la producción, construcción de la variable objetivo con guardas de truncamiento, caracterización del objetivo y separación de los pozos de gas |
| **2** | 6 y 7 | Selección de variables: varianza nula, disponibilidad al momento de decidir, multicolinealidad medida con VIF |
| **3** | 8 a 11 | Partición temporal, preprocesamiento dentro del pipeline, métricas y modelo de referencia, encoding de la variable categórica |
| **4** | 12 a 14 | Regresión lineal, Ridge, Random Forest y Gradient Boosting; comparación |
| **5** | 15 a 19 | Validación cruzada con `TimeSeriesSplit`, optimización de hiperparámetros con `GridSearchCV`, sobreajuste, partición temporal contra aleatoria, validación expansiva y variantes descartadas |
| **6** | 20 a 22 | Importancia por permutación, coeficientes, diagnóstico de error por quintil y conclusiones |

## Resultados del modelado

**Modelo elegido: Random Forest.** Evaluado sobre los 619 pozos fracturados en 2024-2025, con
entrenamiento exclusivo en pozos anteriores:

| Modelo | MAE (m³) | RMSE (m³) | R² | Mejora de MAE vs. referencia |
|---|---|---|---|---|
| Referencia (mediana de train) | 14.138 | 18.782 | −0,18 | — |
| Regresión lineal | 10.776 | 15.019 | 0,244 | 24% |
| Ridge | 10.814 | 15.059 | 0,240 | 23% |
| **Random Forest** | **10.596** | **14.829** | **0,263** | **25%** |
| Gradient Boosting | 10.878 | 14.965 | 0,249 | 23% |

### El hallazgo central: la partición importa más que el modelo

El mismo modelo, con las mismas variables y los mismos hiperparámetros, evaluado con una **partición
aleatoria** da **R² 0,52** (promedio de 10 semillas) en lugar de 0,263. Exactamente el doble, y el
factor se repite en los tres modelos.

La diferencia es que la partición aleatoria le deja ver al modelo pozos del mismo período que
después usa para evaluarlo. Como el diseño de completación en Vaca Muerta cambió muchísimo —la rama
mediana pasó de 1.411 m en 2016 a 2.996 m en 2025— eso no refleja cómo se va a usar el modelo: en
la práctica se entrena con lo que ya produjo y se aplica a pozos que todavía no se fracturaron.

**La métrica no mide solo al modelo: mide al esquema de validación.**

### Validación cruzada: el mismo hallazgo sin tocar el test

El resultado anterior compara la partición temporal contra la aleatoria usando el conjunto de test.
Se puede comprobar lo mismo **sin que el test participe**, con validación cruzada sobre los 1.298
pozos de entrenamiento:

| Esquema de validación cruzada | R² medio | Desvío entre folds | Rango |
|---|---|---|---|
| `TimeSeriesSplit(5)` — temporal | **0,171** | 0,116 | 0,017 – 0,335 |
| `KFold(5, shuffle=True)` — aleatoria | **0,546** | 0,044 | 0,473 – 0,610 |

La validación aleatoria infla el resultado **3,2 veces**, y los pozos de 2024-2025 no intervinieron
en la medición. El desvío entre folds temporales es casi el triple que el de los aleatorios: cuando
el R² depende tanto de qué año toque predecir, reportar un número sin su dispersión da una falsa
sensación de precisión.

### Optimización de hiperparámetros: no había nada que ganar

Sobre esa validación temporal corrimos la búsqueda de hiperparámetros del Random Forest:

| | MAE de validación cruzada | MAE en test | R² en test |
|---|---|---|---|
| Hiperparámetros elegidos a mano | 11.765 | **10.596** | **0,263** |
| `GridSearchCV` — 120 combinaciones | **11.432** | 10.659 | 0,256 |
| `RandomizedSearchCV` — 60 sorteos | 11.517 | 10.554 | 0,255 |

**La optimización mejora la validación cruzada un 2,9% y no mejora el test.** Para saber si esas
diferencias significan algo, entrenamos el mismo modelo cambiando solo la semilla del bosque: el R²
de test se mueve con un desvío de **0,003**, en un rango de 0,252 a 0,264. El R² del modelo
optimizado —0,256— **cae dentro de ese rango**, a 1,9 desvíos del modelo a mano. Y reentrenar ese
mismo modelo optimizado con las filas ordenadas por año en lugar del orden original lo mueve otros
0,004, sin que cambie ningún hiperparámetro. La optimización movió la métrica en el mismo orden en
que la mueven detalles sin significado.

`RandomizedSearchCV` lo deja más claro todavía: es el **mejor MAE de los tres** (42 m³ por debajo del
modelo a mano) y a la vez el **peor R²**. Cuando el ordenamiento se da vuelta según qué métrica se
mire, ese ordenamiento no es información.

El óptimo es una meseta y no un pico: las cinco mejores combinaciones de la grilla están dentro de
40 m³ entre sí, con un desvío entre folds de unos 1.000 m³. Y el mejor de la grilla apunta a
`min_samples_leaf=2`, o sea hojas de dos pozos: más capacidad de memorizar, en un problema que ya
tiene una brecha train-test de 0,45. **Mantenemos los hiperparámetros elegidos a mano.** Lo que
aporta la búsqueda no es un modelo mejor, es la verificación de que no había uno mejor por encontrar.

### Encoding de la variable categórica

`operadora` es la única categórica del modelo: 10 categorías tras agrupar en `"otras"` las
operadoras con menos de 40 pozos. Comparados los esquemas sobre la misma partición temporal:

| Esquema | R² (Random Forest) | R² (Ridge) |
|---|---|---|
| Sin la categórica | 0,123 | 0,062 |
| **One-hot — el elegido** | **0,263** | **0,240** |
| Ordinal (códigos enteros) | 0,221 | **0,042** |
| Target encoding (CV interna) | 0,260 | 0,240 |

El encoding ordinal le cuesta poco al árbol, que puede partir la variable varias veces y reconstruir
los grupos, y **le rompe el modelo al lineal** (0,240 → 0,042), que queda obligado a tratar códigos
arbitrarios como si fueran una escala. El target encoding empata con one-hot usando una columna en
lugar de diez: con 10 categorías no vale el riesgo de filtración, pero es el camino para `yacimiento`
y sus 63 categorías.

Mirando la variable apareció además un defecto del dato: **Vista figura como dos operadoras
distintas** (`vista oil & gas argentina sau` y `vista energy argentina sau`) porque cambió de razón
social, y el corte es temporal —62 pozos en train y 0 en test la primera, 33 y 88 la segunda—, así
que esas dos columnas del one-hot funcionan como un marcador de época más que como la identidad de
la operadora. Unificarlas no cambia el resultado (R² 0,263 → 0,262), así que lo dejamos documentado
sin adoptarlo.

### Dónde falla el modelo

El error no está repartido parejo. Por quintil de producción real:

| Quintil | Real (mediana) | Predicho (mediana) | MAE |
|---|---|---|---|
| q1 — menos productivos | 15.507 | 28.560 | 15.655 |
| q3 — centro | 35.681 | 40.239 | **7.108** |
| q5 — más productivos | 57.521 | 46.060 | 15.444 |

En el rango central el MAE baja a 5.675-7.108 m³ (14-18% de la producción típica). En los extremos
se triplica, y con sesgo de signo opuesto: el modelo comprime sus predicciones hacia el centro.
Sirve para estimar un pozo de diseño típico; **no sirve para identificar de antemano los pozos
excepcionales ni los fracasos**, que son justamente los que no se explican por el diseño.

## Principales hallazgos del EDA

- **El dataset mezcla pozos verticales y horizontales.** Un vertical mediano bombea 0 tn de arena
  nacional y 430 m³ de agua en 3 etapas; uno horizontal, 8.576 tn y 54.314 m³ en 38 etapas. El cruce con
  `tipo_reservorio` lo confirma: los verticales son convencionales y los horizontales no.

- **El grano no es un pozo por fila.** Hay 4.890 filas para 4.646 pozos. Los 244 registros
  excedentes comparten pozo *y* fecha de fractura y reparten las etapas entre varias filas: son
  cargas parciales de una misma operación, no refracturas. Las consolidamos sumando las magnitudes
  aditivas y tomando el máximo de las propiedades del pozo.

- **Los ceros son el problema de calidad, no los nulos.** Solo tres columnas tienen nulos, pero
  hay ceros centinela en longitud de rama (el valor 3,0 m aparece 63 veces), presión, potencia y
  agua. Un equipo de fractura no opera a cero psi.

- **`co2_inyectado_m3` no aporta nada, pero no por lo obvio.** Tiene 159 registros con valor
  positivo, y los 159 son pozos verticales. Dentro de la población que analizamos es idénticamente
  cero. Si hubiéramos mirado solo el porcentaje de ceros global, la conclusión habría sido otra.

- **La intensidad de fractura se amesetó.** Entre 2016 y 2025 la arena por pozo se triplicó, pero
  eso es efecto de escala: la rama se duplicó. La arena *por metro* creció 29% hasta 2019 y
  apenas 9% en los seis años siguientes, mientras el espaciamiento entre etapas se apretaba de
  78 m a 59 m. La industria dejó de mejorar bombeando más arena por metro.

- **Cada operadora tiene una estrategia identificable, y se puede medir.** Vista usa la rama más
  larga (2.911 m), la mayor intensidad (4,17 tn/m) y el espaciamiento más apretado (58 m), y lo
  repite de forma muy estandarizada: su dispersión relativa de rama es 0,17, la más baja de las
  seis. Total Austral está en el extremo opuesto en todo —1.970 m, 2,48 tn/m, etapas a 83,6 m— con
  una dispersión de 0,42, dos veces y media la de Vista. La diferencia de intensidad entre las dos
  es de 1,7 veces, ya normalizada por metro de rama: es criterio de diseño, no escala.

- **Las variables de diseño están muy correlacionadas entre sí.** La longitud de rama correlaciona
  0,91 con la arena y 0,91 con las etapas, porque todas crecen con el tamaño del pozo. En el
  modelado conservamos una sola variable de escala más las de intensidad: con eso los VIF bajan de
  7,57 a menos de 5.

## Limitaciones y sesgos

- **Concentración en un operador.** YPF representa el 53% de los pozos, así que cualquier
  conclusión refleja sobre todo su forma de completar.
- **Concentración geológica.** El 97% de los pozos son de Vaca Muerta; las conclusiones no se
  extrapolan a otras formaciones no convencionales.
- **Diseño confundido con geología.** Cada operadora trabaja en áreas de calidad de roca distinta,
  así que el efecto del diseño está mezclado con el de la roca. Describimos asociaciones, no
  efectos causales.
- **No hay contrafactual.** El dataset solo contiene pozos efectivamente fracturados: no se puede
  saber qué habría producido un pozo con otro diseño.
- **Datos preliminares.** La Secretaría de Energía los publica como sujetos a revisión, y el año
  en curso está incompleto.
- **Falta la geología, que es el factor dominante.** Probamos agregar coordenadas, cota y área de
  concesión: el R² de test no se movió de 0,26 y el de entrenamiento subió de 0,71 a 0,81, es decir
  que solo agregan capacidad de memorizar. La posición en superficie no es la calidad de la roca a
  tres kilómetros de profundidad, y eso no está en datos abiertos. Es el techo del modelo.
- **La operadora pesa tanto como la mejor variable de diseño**, y no es causal: refleja la calidad
  del área que cada empresa tiene en concesión. No se puede usar para comparar operadoras.
- **El modelo es de petróleo.** Los 191 pozos cuyo objetivo es el gas quedan excluidos: medirlos con
  "petróleo acumulado a 12 meses" sería evaluarlos con la métrica equivocada.
- **Validez temporal acotada.** Está validado sobre pozos de 2024-2025. Si el diseño sigue
  cambiando, hay que reentrenar.

## Qué sigue

| Línea | Qué esperamos |
|---|---|
| **Encoding de alta cardinalidad** | `yacimiento` tiene 63 categorías y es un proxy geológico más fino que la operadora. Ya medimos que el target encoding empata con one-hot usando una columna en lugar de diez, así que es el camino; falta la validación cruzada anidada para no filtrar información |
| **Hiperparámetros del boosting** | La búsqueda sobre el Random Forest ya está hecha y no dio nada. Queda abierta para Gradient Boosting, que tiene más parámetros sensibles (`learning_rate`, `max_iter`, `l2_regularization`) y donde la meseta puede ser menos plana |
| **Predecir productividad por peso invertido** | La pregunta de negocio no es qué diseño produce más, sino cuál produce más por unidad de costo. El dataset tiene las cantidades de arena y agua, que son el grueso del costo |
| **Intervalos de predicción** | Dado el error en los extremos, un rango es más honesto que un número |
| **Modelo de gas** | Los 191 pozos excluidos, con la producción de gas como objetivo |

## Uso de herramientas de IA

Usamos un asistente de IA como **copiloto** durante las tres pre-entregas. Lo documentamos porque
la cursada lo pide y porque es parte honesta de cómo trabajamos.

### En qué nos ayudó y qué decidimos nosotros

| Nos apoyamos en la IA para | Lo resolvimos nosotros |
|---|---|
| Sintaxis y API de `pandas` y `scikit-learn` que no conocíamos (`ColumnTransformer`, `Pipeline`, `permutation_importance`) | La elección del tema, la pregunta de negocio y por qué vale la pena responderla |
| Proponer enfoques ante un problema planteado: cómo calcular el mes de vida de un pozo, cómo detectar el truncamiento de la ventana | La definición del alcance (pozos horizontales con rama ≥ 500 m) y su justificación técnica |
| Revisar nuestro código buscando errores y señalar casos borde que no habíamos previsto | La elección de la variable objetivo y de la ventana de 12 meses |
| Sugerir qué gráfico comunica mejor un hallazgo | La interpretación de los resultados y el criterio físico de qué tiene sentido en un pozo |
| Mejorar la redacción de las explicaciones para que se entiendan sin ser del rubro | Las decisiones metodológicas, incluida la de rechazar variantes que mejoraban la métrica |

### Cómo nos aseguramos de entender lo que entregamos

El criterio que seguimos fue que **ninguna afirmación entra si no la podemos sostener con la salida
del código**. Todos los números de los notebooks salen de celdas ejecutadas y visibles: si un
resultado del texto no coincidía con lo que imprimía la celda, corregíamos el texto, no el número.

Tres casos concretos donde revisar en lugar de aceptar nos cambió la conclusión:

- **La columna `co2_inyectado_m3`.** La primera lectura fue que era constante y no aportaba nada.
  Al mirar la salida, tenía 159 registros con valor positivo. Verificamos uno por uno: los 159 son
  pozos verticales, así que dentro de nuestro alcance es idénticamente cero. El hallazgo correcto
  es más fuerte que el inicial, y solo apareció por desconfiar del primero.

- **La transformación logarítmica de la variable objetivo.** La habíamos dado por necesaria al
  plantear el proyecto, porque es lo habitual en producción de hidrocarburos. Al medirla, la
  asimetría original era 0,57 y `log1p` la llevaba a −2,44: la empeoraba. Dejamos la verificación
  a la vista en el notebook en lugar de borrar el supuesto equivocado.

- **Agregar el año de fractura como variable.** Mejoraba el R² de 0,263 a 0,285. En vez de quedarnos
  con la mejora, la probamos en los otros cortes temporales: ahí cambiaba de signo. La descartamos
  y explicamos por qué, aunque el número fuera peor.

### Revisión entre nosotros

Cada entrega la revisó otro integrante del grupo antes de darla por cerrada, y de ahí salieron
cambios concretos: reemplazar el recorte de atípicos por imputación con la mediana del grupo —porque
el *winsorizing* no era una técnica vista en la cursada— y reescribir una sección entera de
comparación entre operadoras que no se entendía como estaba redactada.
