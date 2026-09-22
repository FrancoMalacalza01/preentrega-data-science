# Cómo funciona este proyecto

Documento técnico interno. El `README.md` cuenta **qué** hace el proyecto; este archivo
explica **cómo** está armado, por qué cada pieza está donde está, y qué decisiones hay
detrás. Sirve para retomar el trabajo, para que cualquiera del grupo pueda modificarlo, y
para defenderlo oralmente.

---

## 1. El recorrido de los datos

Todo el proyecto es una cadena de cuatro pasos:

```
   PORTAL                  data/raw/            data/processed/        reports/figures/
Secretaría de   ──────>  fractura_        ──>  pozos_analitico.csv  ──>  8 gráficos
  Energía                adjunto_iv.csv        pozos_encoded.csv          .png
  (CKAN)
             descargar_          limpieza y            visualización
           fractura.py       transformación
                          (notebook o script)
```

Regla que ordena todo: **el dato crudo nunca se modifica**. Todo lo que se toca queda en
`data/processed/`, que es descartable y regenerable. Si mañana descubrimos un error en la
limpieza, corregimos el pipeline y volvemos a correrlo sobre `raw`; el original sigue
intacto. Por eso hay dos carpetas y no una.

---

## 2. Los archivos, uno por uno

### `src/descargar_fractura.py`

Baja el dataset del portal de datos abiertos y lo deja en `data/raw/fractura_adjunto_iv.csv`.

Lo que no es obvio: **no tiene la URL del CSV escrita en el código**. El portal corre sobre
CKAN, así que el script le pregunta a la API qué recursos tiene el dataset y elige el de
actualización diaria.

¿Por qué esa vuelta? Porque cuando la Secretaría republica el archivo, la URL directa
cambia y un script con la URL fija se rompe en silencio. Preguntando por la API, sigue
funcionando. Y si la API falla, imprime la dirección del portal para bajarlo a mano en vez
de cortar con un error críptico.

No hace falta correrlo para trabajar: el CSV ya está versionado en el repo.

### `src/preparar_dataset.py`

El pipeline de limpieza como script ejecutable. Cuatro funciones en orden:

| Función | Qué hace |
|---|---|
| `cargar()` | Lee el CSV crudo y avisa si falta |
| `limpiar()` | Filtra a horizontales, corrige fechas, consolida por pozo, imputa y recorta |
| `agregar_derivadas()` | Calcula las 11 variables de intensidad |
| `codificar()` | One-hot y frequency encoding de las categóricas |

**Produce exactamente los mismos dos CSV que el notebook.** Está verificado: mismas
dimensiones (2.603 × 32 y 2.603 × 49) y cero diferencias numéricas columna por columna. Es
importante que sea así, porque si el script y el notebook divergieran el repo se estaría
contradiciendo a sí mismo.

La división del trabajo entre ambos es deliberada:

- El **notebook explica y justifica** cada decisión, con los chequeos que la respaldan.
- El **script ejecuta**. Si alguien solo quiere los datos limpios, corre el script en
  segundos sin abrir Jupyter.

### `notebooks/01_eda_preentrega2.ipynb`

El documento principal de la entrega. 87 celdas, 43 de código, ejecutado de punta a punta
sin errores. La sección 5 explica su recorrido.

### `data/raw/fractura_adjunto_iv.csv`

El Adjunto IV tal como lo publica la Secretaría: 4.890 filas, 30 columnas, una fila por
operación de fractura declarada. No se modifica nunca.

### `data/processed/`

Las dos salidas del pipeline:

- **`pozos_analitico.csv`** — 2.603 pozos × 32 columnas, con las categóricas como texto
  legible. Es el que se usa para explorar y graficar.
- **`pozos_encoded.csv`** — los mismos pozos × 49 columnas, con las categóricas ya
  convertidas a números. Es el que va a alimentar el modelo de la Pre-entrega 3.

### `reports/figures/`

Los 8 gráficos que **el notebook exporta solo**, mediante un helper `guardar_figura(nombre)`.
El prefijo `01_` indica qué notebook los generó: cuando exista el notebook 02 del modelo, sus
figuras serán `02_*` y no se pisarán. Los nombres son descriptivos
(`01_correlacion_spearman.png`) y no `fig05.png`, así se encuentran por el nombre cuando haga
falta una para la presentación.

### `.gitignore`

Ignora `data/raw/*` **con una excepción explícita** para el CSV de fractura:

```
data/raw/*
!data/raw/fractura_adjunto_iv.csv
```

Lo normal en un proyecto de datos es no versionar los datos crudos, porque son pesados y
regenerables. Acá hacemos la excepción porque la guía del curso pide entregar el dataset
dentro del repositorio, y el archivo pesa 1,2 MB.

También ignora `data/raw/produccion/`, donde van a ir los CSV del Capítulo IV: son cientos
de megabytes por año y esos sí no entran a git.

---

## 3. Cómo se resuelven las rutas

Este es el único punto técnicamente delicado del repo.

El notebook vive en `notebooks/`, pero los datos están en `data/` **de la raíz**. Si usara
rutas relativas simples (`data/raw/...`), andaría al abrirlo desde Jupyter y se rompería al
correrlo desde la raíz o desde Colab.

La solución es la función `raiz_del_proyecto()`, en la celda de configuración: sube por el
árbol de directorios buscando `requirements.txt`. Donde lo encuentra, esa es la raíz, y
todas las rutas se arman contra ella:

```python
RAIZ = raiz_del_proyecto()
DATA_DIR = RAIZ / "data"
RAW_DIR  = DATA_DIR / "raw"
PROC_DIR = DATA_DIR / "processed"
FIG_DIR  = RAIZ / "reports" / "figures"
```

Si no encuentra la marca —caso Colab, donde no hay repo clonado— se queda con el directorio
actual y el notebook sigue funcionando igual.

El CSV, además, se busca por patrón y no por nombre exacto:

```python
PATRON_FRACTURA = "*fractura*adjunto*iv*.csv"
```

Así acepta tanto el nombre corto del repo (`fractura_adjunto_iv.csv`) como el nombre largo
con el que el portal entrega la descarga
(`datos-de-fractura-de-pozos-de-hidrocarburos-adjunto-iv-actualizacin-diaria.csv`). Si no
encuentra nada y estamos en Colab, ofrece subirlo a mano.

---

## 4. Por qué el notebook pesa medio mega

**GitHub no renderiza archivos de más de 1 MB.** Con los 8 gráficos embebidos, el notebook
pesaba 1,12 MB: quien lo abriera en GitHub habría visto un cartel de "no podemos mostrar
archivos tan grandes" en lugar del análisis.

La solución fue recomprimir los PNG embebidos a paleta de 256 colores. En gráficos de color
plano —que es lo que son todos— el resultado es visualmente idéntico, y baja las imágenes de
0,72 MB a 0,26 MB. El notebook quedó en 0,51 MB, con margen de sobra.

Si en el futuro se agregan gráficos y el archivo vuelve a pasar el megabyte, hay que repetir
ese paso antes de subirlo.

---

## 5. El recorrido del notebook

Las 13 secciones, y qué aporta cada una:

| Sección | Contenido | Por qué está |
|---|---|---|
| **1. Objetivo** | Pregunta de negocio, alcance, fuentes | Define qué se responde y qué no |
| **2. Configuración** | Librerías, rutas, helper de figuras | Hace el notebook portable |
| **3. Carga** | Búsqueda del CSV y diccionario de las 30 columnas | Deja claro qué significa cada variable |
| **4. Estructura y grano** | Qué representa una fila y si la clave es única | **Descubre que el grano no es un pozo por fila** |
| **5. Perfilado** | Tipo, nulos, ceros, cardinalidad por columna | **Descubre que el problema son los ceros, no los nulos** |
| **6. Calidad** | Reglas de negocio, valores centinela, outliers | Justifica cada filtro con evidencia |
| **7. Limpieza** | Filtrado, consolidación, imputación, recorte | Produce los 2.603 pozos |
| **8. Variables derivadas** | 11 features de intensidad + control de plausibilidad | Hace comparables pozos de distinto tamaño |
| **9. Encoding** | One-hot y frequency encoding | Prepara los datos para modelar |
| **10. Visualización** | 6 bloques de gráficos | Responde una pregunta concreta cada uno |
| **11. Variable objetivo** | Cruce con producción (opcional) | Queda listo para la Pre-entrega 3 |
| **12. Conclusiones** | Calidad, variables, negocio, sesgos | Cierra con los números reales |
| **13. Guardado** | Exporta los CSV procesados | Conecta con el resto del repo |

La sección 11 **está desactivada a propósito**. Detecta sola si los archivos del Capítulo IV
están en `data/`; si no están, lo informa y el notebook sigue sin fallar. Así la entrega
corre completa con lo que hay hoy, y el día que bajemos la producción se activa sin tocar una
línea de código.

---

## 6. Las decisiones que hay que saber defender

### Restringir a pozos horizontales

No es un filtro de conveniencia. Un vertical mediano bombea **0 tn de arena en 3 etapas**;
uno horizontal, **8.576 tn en 38 etapas**. Mezclarlos produciría un modelo que aprende a
distinguir vertical de horizontal en lugar de aprender el efecto del diseño. Además, las
variables de intensidad por metro serían indefinidas en un pozo vertical: división por cero.
El cruce con `tipo_reservorio` lo respalda: los verticales son convencionales y los
horizontales, no convencionales.

### Umbral de 500 m, elegido con análisis de sensibilidad

No se eligió a ojo. Se probaron 0, 100, 300, 500, 800 y 1.000 m mirando dos cosas: cuántos
pozos sobreviven y si el espaciamiento típico entre etapas se mantiene estable —es un buen
testigo porque es una decisión de ingeniería con rango físico acotado—.

El espaciamiento se estabiliza en 63 m a partir de los 100 m de rama. Sin filtro aparece una
intensidad máxima de **102 tn de arena por metro**, unas 25 veces el valor típico y
físicamente imposible. Se eligió 500 m porque conserva casi los mismos pozos que 100 m
(92,2% contra 92,9%) descartando con más margen la zona donde la longitud reportada no es
confiable.

### Consolidar en vez de deduplicar

Hay 4.890 filas para 4.646 pozos. Los 244 registros excedentes comparten pozo **y fecha de
fractura**, y reparten las etapas entre varias filas. No son refracturas: son cargas
parciales de una misma operación. Por eso se **suman** las magnitudes aditivas (etapas,
arena, agua) y se toma el **máximo** de las propiedades del pozo (longitud, presión). Borrar
duplicados habría perdido etapas reales.

### Recortar los outliers en vez de eliminar el pozo

Presiones de 209.640 psi y potencias de 232.159 hp son errores de carga: una fractura real
opera entre 5.000 y 15.000 psi. Pero el resto de las variables de esos pozos son válidas, así
que se recortan por percentil 1 y 99 en lugar de borrar la fila. Eliminar el pozo entero
sería tirar información buena por un error en una sola columna.

### Frequency encoding y no target encoding

Para las categóricas de alta cardinalidad (operadora, yacimiento, área) se usa la frecuencia
de cada categoría. El target encoding daría mejores resultados aparentes, pero **filtra
información de la variable objetivo hacia los predictores** y produce métricas infladas que
no se sostienen fuera de la muestra.

### El caso del CO₂

`co2_inyectado_m3` vale cero en el 96,7% de los registros, lo que invita a descartarla por
constante. Pero mirando el 3,3% restante: los 159 registros con valor positivo son **todos
pozos verticales**. Dentro de la población que analizamos es idénticamente cero.

Por eso la columna se elimina **después** de filtrar y no antes. Y sirve como ejemplo
metodológico: mirando solo el porcentaje de ceros global, la conclusión habría sido otra.

---

## 7. Qué hay que saber para la Pre-entrega 3

El EDA dejó dos problemas identificados que hay que resolver **antes** de modelar:

**Multicolinealidad severa.** `cantidad_fracturas` y `arena_total_tn` correlacionan 0,95, y
ambas con la longitud de rama cerca de 0,89. Tiene sentido físico —un pozo más largo lleva
más etapas y cada etapa consume arena— pero rompe los modelos: los coeficientes salen
inestables y SHAP reparte el crédito arbitrariamente entre variables correlacionadas,
generando explicaciones confiadas y falsas.

La solución es quedarse con **una sola variable de escala** (la longitud de rama) más las de
**intensidad** (arena por metro, agua por metro, espaciamiento), que son casi ortogonales
entre sí.

**El diseño está confundido con la geología.** Cada operadora trabaja en áreas de calidad de
roca distinta, así que el efecto del diseño se mezcla con el de la roca. Hay que controlar
por formación y área, y declarar que el proyecto estima asociaciones y no efectos causales.

Además, dos precauciones para cuando se construya la variable objetivo:

1. El mes de vida de un pozo **no** se calcula con `cumcount()`. Si un pozo tiene meses sin
   reportar, el conteo posicional los saltea y comprime la ventana de 12 meses. Se calcula
   por diferencia de períodos contra el primer mes con producción efectiva.
2. Hay que descartar los pozos cuyo primer mes de producción coincide con el inicio del
   período descargado: no se sabe si es realmente su primer mes o si venían produciendo desde
   antes (**truncamiento a izquierda**).

Ambas ya están implementadas en la sección 11 del notebook.

---

## 8. Comandos útiles

```bash
# Preparar el entorno
pip install -r requirements.txt

# Bajar la última versión del dataset (opcional, ya está en el repo)
python src/descargar_fractura.py

# Regenerar data/processed/ sin abrir Jupyter
python src/preparar_dataset.py

# Abrir el análisis
jupyter notebook notebooks/01_eda_preentrega2.ipynb
```

---

## 9. Estado actual

| Ítem | Estado |
|---|---|
| Notebook de EDA ejecutado y sin errores | Listo |
| Dataset original incluido en el repo | Listo |
| Datos procesados y figuras exportadas | Listo |
| README con dataset, objetivo, hallazgos y sesgos | Listo |
| Scripts de descarga y preparación | Listo |
| Link compartido en el foro del aula virtual | **Pendiente** |
| CSV de producción del Capítulo IV descargados | **Pendiente — bloquea la Pre-entrega 3** |

Bajar la tabla de producción es el camino crítico del proyecto: sin ella no hay variable
objetivo, y sin variable objetivo no hay modelo supervisado, ni interpretación, ni API.
