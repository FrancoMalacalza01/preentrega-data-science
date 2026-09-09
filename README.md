# Diseño de completación y productividad de pozos no convencionales en Vaca Muerta

Proyecto final — **EnergIA Digital, Data Science** (Tutora Belén).
Estado: **Pre-entrega 2 (Análisis Exploratorio de Datos)**.

**Integrantes:** Franco Malacalza · Martín Gerbaldo · Carolina

---

## El dataset

Los datos salen del portal de datos abiertos de la **Secretaría de Energía de la Nación**. La tabla
base es *Datos de fractura de pozos de hidrocarburos (Adjunto IV)*: 4.890 registros y 30 columnas,
con un registro por operación de fractura hidráulica declarada por las operadoras, desde 2009 hasta
hoy. Se complementa —de forma opcional— con *Producción de petróleo y gas por pozo (Capítulo IV)*,
que tiene grano mensual por pozo y se vincula con la anterior por el identificador `idpozo`.

- Fractura: http://datos.energia.gob.ar/dataset/datos-de-fractura-de-pozos-adjunto-iv
- Producción: http://datos.energia.gob.ar/dataset/produccion-de-petroleo-y-gas-por-pozo

## Resumen del proyecto

Cada pozo horizontal no convencional se termina con un diseño de fractura hidráulica: una longitud de
rama lateral, una cantidad de etapas, y un volumen de arena y agua bombeados a determinada presión.
Ese diseño concentra buena parte del costo de la terminación, y las operadoras deciden cuánto
invertir en él sin certeza de cuánto va a producir el pozo después. El proyecto analiza cómo se
diseñan hoy esos pozos en Vaca Muerta, cómo cambió ese diseño en la última década, y cuánto de la
productividad se explica por esas decisiones.

## Objetivo

Construir un modelo supervisado que estime la **producción acumulada de petróleo en los primeros 12
meses** de un pozo (`prod_pet_acum_12m`, en m³) a partir de las características de su completación y
su ubicación geológica —un problema de regresión, con una variante de clasificación que predice si el
pozo cae en el cuartil superior de productividad de su formación. En paralelo, aplicar clustering
sobre las variables de completación para identificar arquetipos de diseño de pozo y comparar el
rendimiento entre grupos.

## Qué se descubrió en el análisis exploratorio

El hallazgo que condiciona todo lo demás es que **el dataset mezcla dos poblaciones incomparables**:
2.054 de los 4.890 registros (42%) tienen longitud de rama cero, y no son datos faltantes sino pozos
verticales convencionales —un vertical mediano bombea 0 toneladas de arena contra 8.576 del
horizontal mediano—. El segundo es que **el grano no es un pozo por fila**: hay 244 registros
excedentes que resultaron ser cargas parciales de una misma operación, no refracturas, y hubo que
consolidarlos. El tercero es que **el problema de calidad son los ceros, no los nulos**: aparecen
como valor centinela en longitud de rama (el valor 3,0 m se repite 63 veces), presión, potencia y
agua. Tras la limpieza quedaron **2.603 pozos horizontales**, 97% de ellos en Vaca Muerta.

Sobre el negocio, el diseño de pozo cambió radicalmente: entre 2016 y 2025 la arena por pozo se
triplicó, pero **la intensidad de fractura se amesetó** —la arena por metro de rama subió apenas 9%
desde 2019—. El crecimiento vino de alargar el pozo y apretar el espaciamiento entre etapas (de 78 m
en 2018 a 59 m en 2026), no de bombear más arena por metro, lo que sugiere rendimientos decrecientes
en intensidad. Además, cada operadora tiene una estrategia identificable: Vista Energy usa la rama
más larga y la mayor intensidad de forma muy estandarizada, mientras que Total Austral está en el
extremo opuesto y con mucha más dispersión.

## Modelos ajustados

_(Pre-entrega 3 y 4 — pendientes.)_ El EDA ya dejó identificados dos problemas a resolver antes de
modelar: **multicolinealidad severa** entre las variables crudas (`cantidad_fracturas` y
`arena_total_tn` correlacionan 0,95), que obliga a quedarse con una variable de escala más las de
intensidad; y la **confusión entre operadora, área y diseño**, que amenaza la interpretación causal
de cualquier modelo que use la empresa como predictor.

## Limitaciones y sesgos

- **Concentración en un operador:** YPF representa el 53% de los pozos, así que el modelo aprenderá
  sobre todo su forma de completar.
- **Concentración geológica:** el 97% de los pozos son de Vaca Muerta; las conclusiones no se
  extrapolan a otras formaciones.
- **No hay contrafactual:** el dataset solo contiene pozos efectivamente fracturados.
- **Datos preliminares:** la Secretaría los publica como sujetos a revisión, y el año en curso está
  incompleto.
- **Sesgo de supervivencia temporal:** exigir 12 meses completos de producción excluye a los pozos
  más recientes, que son los de diseño más moderno.

---

## Estructura del repositorio

```
.
├── README.md
├── requirements.txt
├── 01_EDA_preentrega2.ipynb        # Pre-entrega 2 — este notebook
├── data/
│   ├── datos-de-fractura-...csv    # dataset base
│   └── processed/                  # salidas del notebook
└── figs/                           # gráficos exportados
```

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
jupyter notebook 01_EDA_preentrega2.ipynb
```

El notebook **corre completo solo con el CSV de fractura**. La sección 11, que construye la variable
objetivo cruzando con la tabla de producción, se activa sola si encuentra los archivos del Capítulo
IV en `data/`; si no están, lo informa y sigue sin fallar.

> Para activarla hay que descargar dos o tres años de producción y dejarlos en `data/`. Buscá los
> archivos que dicen **"con identificador"**: son los únicos que traen `idpozo`. Los de "DDJJ
> abiertas y cerradas" no sirven para el join.

En Google Colab, la celda de carga busca el archivo en `.`, `data/`, `/content/` y Google Drive, y
ofrece subida interactiva si no lo encuentra.
