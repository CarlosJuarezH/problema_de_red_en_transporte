import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests


# La raíz del proyecto es la carpeta que contiene src/ y data/.
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# Claves y nombres descriptivos de los indicadores seleccionados.
INDICATORS = {
    "6207019027": "porcentaje_viviendas_alquiladas",
    "1002000001": "poblacion_total",
}

GEOGRAPHY_CODE = "09"
GEOGRAPHY_NAME = "Ciudad de México"


def main():
    token = os.getenv("INEGI_TOKEN")

    if not token:
        sys.exit(
            "No se encontró INEGI_TOKEN. "
            "Revisa el secreto de Codespaces y reinicia el entorno."
        )

    indicator_ids = ",".join(INDICATORS.keys())

    # La URL incluye el token para autenticar la consulta.
    # No la imprimimos para evitar exponerlo en la terminal.
    url = (
        "https://www.inegi.org.mx/app/api/indicadores/"
        "desarrolladores/jsonxml/INDICATOR/"
        f"{indicator_ids}/es/{GEOGRAPHY_CODE}/false/BISE/2.0/"
        f"{token}?type=json"
    )

    try:
        response = requests.get(url, timeout=60)
    except requests.RequestException:
        sys.exit(
            "No se pudo conectar con la API del INEGI. "
            "Revisa la conexión e inténtalo de nuevo."
        )

    if response.status_code != 200:
        sys.exit(
            "La API respondió con el código HTTP "
            f"{response.status_code}. Revisa el token y vuelve a intentarlo."
        )

    try:
        payload = response.json()
    except ValueError:
        sys.exit("La respuesta de la API no se pudo interpretar como JSON.")

    series = payload.get("Series")

    if not isinstance(series, list):
        sys.exit(
            "La respuesta no contiene una lista 'Series'. "
            "No se generaron archivos."
        )

    received_ids = {
        str(serie.get("INDICADOR"))
        for serie in series
    }
    missing_ids = set(INDICATORS) - received_ids

    if missing_ids:
        sys.exit(
            "No llegaron todos los indicadores solicitados. "
            f"Faltan: {', '.join(sorted(missing_ids))}. "
            "No se generaron archivos."
        )

    rows = []

    for serie in series:
        indicator_id = str(serie.get("INDICADOR"))
        indicator_name = INDICATORS[indicator_id]

        for observation in serie.get("OBSERVATIONS", []):
            rows.append({
                "indicator_id": indicator_id,
                "indicator_name": indicator_name,
                "period": observation.get("TIME_PERIOD"),
                "value_raw": observation.get("OBS_VALUE"),
                "unit_code": serie.get("UNIT"),
                "frequency_code": serie.get("FREQ"),
                "topic_code": serie.get("TOPIC"),
                "geography_code": observation.get("COBER_GEO"),
                "series_source_code": serie.get("SOURCE"),
                "series_last_update": serie.get("LASTUPDATE"),
                "series_note_code": serie.get("NOTE"),
                "observation_status": observation.get("OBS_STATUS"),
                "observation_exception": observation.get("OBS_EXCEPTION"),
                "observation_source": observation.get("OBS_SOURCE"),
                "observation_note": observation.get("OBS_NOTE"),
            })

    table_df = pd.DataFrame(rows)

    if table_df.empty:
        sys.exit("Los indicadores llegaron, pero no contienen observaciones.")

    # Conservamos el valor original y añadimos una columna numérica para analizar.
    table_df["period"] = pd.to_numeric(
        table_df["period"], errors="coerce"
    ).astype("Int64")

    table_df["value"] = pd.to_numeric(
        table_df["value_raw"], errors="coerce"
    )

    if table_df["value"].isna().all():
        sys.exit("No se encontraron valores numéricos para procesar.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    extraction_time = datetime.now(timezone.utc)
    timestamp = extraction_time.strftime("%Y%m%dT%H%M%SZ")

    raw_path = RAW_DIR / f"inegi_cdmx_{timestamp}.json"
    parquet_path = PROCESSED_DIR / f"inegi_cdmx_{timestamp}.parquet"

    # Guardamos exactamente el contenido JSON recibido.
    raw_path.write_bytes(response.content)

    # Convertimos la tabla y añadimos procedencia al esquema Parquet.
    arrow_table = pa.Table.from_pandas(table_df, preserve_index=False)
    metadata = dict(arrow_table.schema.metadata or {})

    metadata.update({
        b"source": b"INEGI - API del Banco de Indicadores",
        b"indicator_ids": indicator_ids.encode("utf-8"),
        b"geography_code": GEOGRAPHY_CODE.encode("utf-8"),
        b"geography_name": GEOGRAPHY_NAME.encode("utf-8"),
        b"language": b"es",
        b"historical_series": b"true",
        b"format": b"json",
        b"extracted_at_utc": extraction_time.isoformat().encode("utf-8"),
        b"api_endpoint_template": (
            b"https://www.inegi.org.mx/app/api/indicadores/"
            b"desarrolladores/jsonxml/INDICATOR/{indicator_ids}/"
            b"es/{geography_code}/false/BISE/2.0/{TOKEN}?type=json"
        ),
    })

    arrow_table = arrow_table.replace_schema_metadata(metadata)
    pq.write_table(arrow_table, parquet_path)

    # Mostramos las ubicaciones, pero nunca la URL ni el token.
    print("Consulta completada.")
    print(f"Observaciones guardadas: {len(table_df)}")
    print(f"JSON: {raw_path.relative_to(ROOT)}")
    print(f"Parquet: {parquet_path.relative_to(ROOT)}")
    print("Indicadores recibidos:", ", ".join(sorted(received_ids)))


if __name__ == "__main__":
    main()