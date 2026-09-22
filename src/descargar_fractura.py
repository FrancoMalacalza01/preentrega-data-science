"""Descarga la tabla de fracturas (Adjunto IV) del portal de datos abiertos.

La Secretaría de Energía publica el Adjunto IV con actualización diaria, así que
el archivo cambia con el tiempo: este script deja siempre la versión más nueva en
data/raw/fractura_adjunto_iv.csv.

Uso:
    python src/descargar_fractura.py

El portal corre sobre CKAN, así que en vez de hardcodear la URL del CSV —que
cambia cuando republican el recurso— se consulta la API del dataset y se toma el
recurso de actualización diaria.
"""

from pathlib import Path
import sys
import urllib.request

API_DATASET = (
    "http://datos.energia.gob.ar/api/3/action/package_show"
    "?id=datos-de-fractura-de-pozos-adjunto-iv"
)

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "data" / "raw" / "fractura_adjunto_iv.csv"


def url_del_recurso():
    """Devuelve la URL del CSV de actualización diaria según la API de CKAN."""
    import json

    with urllib.request.urlopen(API_DATASET, timeout=60) as respuesta:
        paquete = json.load(respuesta)["result"]

    candidatos = [
        recurso for recurso in paquete["resources"]
        if recurso.get("format", "").upper() == "CSV"
    ]
    if not candidatos:
        raise RuntimeError("El dataset no expone ningún recurso CSV.")

    # Preferimos la versión de actualización diaria, que es la más completa.
    for recurso in candidatos:
        if "diaria" in recurso.get("name", "").lower():
            return recurso["url"]
    return candidatos[0]["url"]


def main():
    DESTINO.parent.mkdir(parents=True, exist_ok=True)

    try:
        url = url_del_recurso()
    except Exception as error:  # noqa: BLE001 - queremos un mensaje legible
        print(f"No se pudo consultar la API del portal: {error}", file=sys.stderr)
        print(
            "Descargá el CSV a mano desde\n"
            "  http://datos.energia.gob.ar/dataset/datos-de-fractura-de-pozos-adjunto-iv\n"
            f"y guardalo como {DESTINO}",
            file=sys.stderr,
        )
        return 1

    print(f"Descargando {url}")
    urllib.request.urlretrieve(url, DESTINO)
    print(f"Guardado en {DESTINO} ({DESTINO.stat().st_size / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
