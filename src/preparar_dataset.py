"""Construye el dataset analítico de pozos a partir de la tabla de fracturas.

Es el mismo pipeline que documenta el notebook 01, empaquetado como script para
poder regenerar los datos procesados sin abrir Jupyter. El notebook explica y
justifica cada decisión; acá están solamente ejecutadas.

Uso:
    python src/preparar_dataset.py

Entrada : data/raw/fractura_adjunto_iv.csv
Salidas : data/processed/pozos_analitico.csv   (legible, categóricas como texto)
          data/processed/pozos_encoded.csv     (lista para alimentar un modelo)
"""

from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "raw" / "fractura_adjunto_iv.csv"
SALIDA = RAIZ / "data" / "processed"

# Por debajo de este largo la rama horizontal no es confiable: aparecen valores
# centinela (3,0 m repetido decenas de veces) e intensidades imposibles.
UMBRAL_RAMA_M = 500

CATEGORICAS = [
    "cuenca", "formacion_productiva", "tipo_reservorio", "subtipo_reservorio",
    "tipo_terminacion", "empresa_informante", "yacimiento", "areapermisoconcesion",
]

# Propiedades del pozo (no se suman) frente a magnitudes de la operación (sí).
AGREGACIONES = {
    "longitud_rama_horizontal_m": "max",
    "presion_maxima_psi": "max",
    "potencia_equipos_fractura_hp": "max",
    "cantidad_fracturas": "sum",
    "arena_bombeada_nacional_tn": "sum",
    "arena_bombeada_importada_tn": "sum",
    "agua_inyectada_m3": "sum",
    "fecha_inicio_fractura": "min",
    "fecha_fin_fractura": "max",
    "sigla": "first",
    "cuenca": "first",
    "areapermisoconcesion": "first",
    "yacimiento": "first",
    "formacion_productiva": "first",
    "tipo_reservorio": "first",
    "subtipo_reservorio": "first",
    "tipo_terminacion": "first",
    "empresa_informante": "first",
}


def cargar(ruta=ENTRADA):
    if not ruta.exists():
        raise FileNotFoundError(
            f"Falta {ruta}. Corré antes: python src/descargar_fractura.py"
        )
    return pd.read_csv(ruta, low_memory=False)


def limpiar(frac, hoy=None):
    """Filtra a pozos horizontales, corrige fechas y consolida por pozo."""
    hoy = hoy or pd.Timestamp.today().normalize()

    df = frac[frac["longitud_rama_horizontal_m"] >= UMBRAL_RAMA_M].copy()

    for col in ["fecha_inicio_fractura", "fecha_fin_fractura"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df.loc[df["fecha_fin_fractura"] < df["fecha_inicio_fractura"], "fecha_fin_fractura"] = pd.NaT
    df.loc[df["fecha_inicio_fractura"] > hoy, "fecha_inicio_fractura"] = pd.NaT

    # Los registros repetidos son cargas parciales de una misma operación.
    df = (df.groupby("idpozo")
            .agg(**{col: (col, func) for col, func in AGREGACIONES.items()})
            .reset_index())

    # Ceros que son faltantes disfrazados: un equipo no opera a cero psi.
    for col in ["presion_maxima_psi", "potencia_equipos_fractura_hp", "agua_inyectada_m3"]:
        df[col] = df[col].replace(0, np.nan)
        df[col] = (df[col]
                   .fillna(df.groupby("formacion_productiva")[col].transform("median"))
                   .fillna(df[col].median()))

    # Extremos físicamente implausibles: se recortan en vez de borrar el pozo.
    for col in ["presion_maxima_psi", "potencia_equipos_fractura_hp"]:
        inferior, superior = df[col].quantile([0.01, 0.99])
        df[col] = df[col].clip(inferior, superior)

    for col in CATEGORICAS:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].replace({"nan": "sin dato", "": "sin dato"})

    # co2_inyectado_m3 es idénticamente cero en la población horizontal.
    return df.drop(columns=["co2_inyectado_m3"], errors="ignore")


def agregar_derivadas(df):
    """Variables de intensidad: permiten comparar pozos de distinto tamaño."""
    df = df.copy()
    df["es_vaca_muerta"] = df["formacion_productiva"] == "vaca muerta"

    df["arena_total_tn"] = (df["arena_bombeada_nacional_tn"]
                            + df["arena_bombeada_importada_tn"])
    df["arena_por_metro"] = df["arena_total_tn"] / df["longitud_rama_horizontal_m"]
    df["agua_por_metro"] = df["agua_inyectada_m3"] / df["longitud_rama_horizontal_m"]
    df["arena_por_etapa"] = df["arena_total_tn"] / df["cantidad_fracturas"]
    df["agua_por_etapa"] = df["agua_inyectada_m3"] / df["cantidad_fracturas"]
    df["espaciamiento_etapas_m"] = (df["longitud_rama_horizontal_m"]
                                    / df["cantidad_fracturas"])

    df["ratio_arena_importada"] = (df["arena_bombeada_importada_tn"]
                                   / df["arena_total_tn"].replace(0, np.nan)).fillna(0)
    df["ratio_agua_arena"] = df["agua_inyectada_m3"] / df["arena_total_tn"].replace(0, np.nan)
    df["usa_arena_importada"] = (df["arena_bombeada_importada_tn"] > 0).astype(int)

    df["duracion_fractura_dias"] = (df["fecha_fin_fractura"]
                                    - df["fecha_inicio_fractura"]).dt.days
    df["anio_fractura"] = df["fecha_inicio_fractura"].dt.year

    # Una o dos etapas para más de 500 m de rama es una carga incompleta.
    df["carga_sospechosa"] = ((df["espaciamiento_etapas_m"] > 200)
                              | (df["cantidad_fracturas"] <= 2)).astype(int)
    return df


def codificar(df):
    """One-hot para baja cardinalidad, frequency encoding para alta.

    Se evita target encoding a propósito: filtraría información de la variable
    objetivo hacia los predictores.
    """
    cardinalidad = df[CATEGORICAS].nunique()
    baja = cardinalidad[cardinalidad <= 15].index.tolist()
    alta = cardinalidad[cardinalidad > 15].index.tolist()

    codificado = pd.concat(
        [df, pd.get_dummies(df[baja], prefix=baja, drop_first=True)], axis=1)
    for col in alta:
        frecuencias = codificado[col].value_counts(normalize=True)
        codificado[f"{col}_freq"] = codificado[col].map(frecuencias)
    return codificado


def main():
    frac = cargar()
    print(f"Registros crudos: {len(frac):,}")

    df = agregar_derivadas(limpiar(frac))
    codificado = codificar(df)

    SALIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA / "pozos_analitico.csv", index=False)
    codificado.to_csv(SALIDA / "pozos_encoded.csv", index=False)

    print(f"pozos_analitico.csv -> {df.shape[0]:,} pozos x {df.shape[1]} columnas")
    print(f"pozos_encoded.csv   -> {codificado.shape[0]:,} pozos x {codificado.shape[1]} columnas")
    print(f"Guardado en {SALIDA}")


if __name__ == "__main__":
    main()
