import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

INDICATORS = {
    "6207019027": "porcentaje_viviendas_alquiladas",
    "1002000001": "poblacion_total",
}

ALCALDIAS_CDMX = {
    "09002": "Azcapotzalco",
    "09003": "Coyoacán",
    "09004": "Cuajimalpa de Morelos",
    "09005": "Gustavo A. Madero",
    "09006": "Iztacalco",
    "09007": "Iztapalapa",
    "09008": "La Magdalena Contreras",
    "09009": "Milpa Alta",
    "09010": "Álvaro Obregón",
    "09011": "Tláhuac",
    "09012": "Tlalpan",
    "09013": "Xochimilco",
    "09014": "Benito Juárez",
    "09015": "Cuauhtémoc",
    "09016": "Miguel Hidalgo",
    "09017": "Venustiano Carranza",
}

# Incluimos también la consulta estatal que ya funcionaba.
GEOGRAPHIES = {
    "09": {
        "name": "Ciudad de México",
        "level": "entidad_federativa",
    },
    **{
        code: {
            "name": name,
            "level": "alcaldia",
        }
        for code, name in ALCALDIAS_CDMX.items()
    },
}


def build_api_url(indicator_ids, geography_code, token):
    return (
        "https://www.inegi.org.mx/app/api/indicadores/"
        "desarrolladores/jsonxml/INDICATOR/"
        f"{indicator_ids}/es/{geography_code}/false/BISE/2.0/"
        f"{token}?type=json"
    )


def main():
    token = os.getenv("INEGI_TOKEN")

    if not token:
        sys.exit(
            "No se encontró INEGI_TOKEN. "
            "Revisa el secreto de Codespaces."
        )

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    indicator_ids = ",".join(INDICATORS)
    extraction_time = datetime.now(timezone.utc)
    timestamp = extraction_time.strftime("%Y%m%dT%H%M%SZ")

    rows = []
    issues = []

    for geography_code, geography in GEOGRAPHIES.items():
        print(
            "Consultando:",
            geography["name"],
            f"({geography_code})",
        )

        url = build_api_url(
            indicator_ids,
            geography_code,
            token,
        )

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
        except requests.RequestException as error:
            issues.append(
                f"{geography['name']} ({geography_code}): "
                f"falló la consulta ({type(error).__name__})."
            )
            continue

        raw_path = (
            RAW_DIR
            / f"inegi_cdmx_{timestamp}_{geography_code}.json"
        )
        raw_path.write_bytes(response.content)

        try:
            payload = response.json()
        except ValueError:
            issues.append(
                f"{geography['name']} ({geography_code}): "
                "la respuesta no se pudo interpretar como JSON."
            )
            continue

        series = payload.get("Series")

        if not isinstance(series, list):
            issues.append(
                f"{geography['name']} ({geography_code}): "
                "la respuesta no contiene la lista 'Series'."
            )
            continue

        received_ids = {
            str(item.get("INDICADOR"))
            for item in series
            if item.get("INDICADOR") is not None
        }

        missing_ids = set(INDICATORS) - received_ids
        if missing_ids:
            names = [
                INDICATORS[indicator_id]
                for indicator_id in sorted(missing_ids)
            ]
            issues.append(
                f"{geography['name']} ({geography_code}): "
                f"no llegaron estos indicadores: {', '.join(names)}."
            )

        for item in series:
            indicator_id = str(item.get("INDICADOR"))

            # Ignoramos cualquier indicador que no se haya solicitado.
            if indicator_id not in INDICATORS:
                continue

            observations = item.get("OBSERVATIONS") or []

            for observation in observations:
                returned_code = str(
                    observation.get("COBER_GEO") or geography_code
                )

                rows.append({
                    "indicator_id": indicator_id,
                    "indicator_name": INDICATORS[indicator_id],
                    "period": observation.get("TIME_PERIOD"),
                    "value_raw": observation.get("OBS_VALUE"),
                    "unit_code": item.get("UNIT"),
                    "frequency_code": item.get("FREQ"),
                    "topic_code": item.get("TOPIC"),
                    "geography_code": returned_code,
                    "geography_name": GEOGRAPHIES.get(
                        returned_code,
                        geography,
                    )["name"],
                    "geography_level": GEOGRAPHIES.get(
                        returned_code,
                        geography,
                    )["level"],
                    "requested_geography_code": geography_code,
                    "series_source_code": item.get("SOURCE"),
                    "series_last_update": item.get("LASTUPDATE"),
                    "series_note_code": item.get("NOTE"),
                    "observation_status": observation.get("OBS_STATUS"),
                    "observation_exception": observation.get(
                        "OBS_EXCEPTION"
                    ),
                    "observation_source": observation.get("OBS_SOURCE"),
                    "observation_note": observation.get("OBS_NOTE"),
                })

    if not rows:
        sys.exit(
            "No se obtuvieron observaciones. "
            "Revisa los JSON guardados y el token."
        )

    table_df = pd.DataFrame(rows)

    table_df["period"] = pd.to_numeric(
        table_df["period"],
        errors="coerce",
    ).astype("Int64")

    table_df["value"] = pd.to_numeric(
        table_df["value_raw"],
        errors="coerce",
    )

    parquet_path = (
        PROCESSED_DIR / f"inegi_cdmx_{timestamp}.parquet"
    )

    arrow_table = pa.Table.from_pandas(
        table_df,
        preserve_index=False,
    )
    metadata = dict(arrow_table.schema.metadata or {})

    metadata.update({
        b"source": b"INEGI - API del Banco de Indicadores",
        b"indicator_ids": indicator_ids.encode("utf-8"),
        b"geography_codes": ",".join(GEOGRAPHIES).encode("utf-8"),
        b"geography_names": json.dumps(
            {
                code: item["name"]
                for code, item in GEOGRAPHIES.items()
            },
            ensure_ascii=False,
        ).encode("utf-8"),
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

    print("\nConsulta terminada.")
    print(f"JSON guardados: {len(list(RAW_DIR.glob(f'inegi_cdmx_{timestamp}_*.json')))}")
    print(f"Observaciones en Parquet: {len(table_df)}")
    print(f"Parquet: {parquet_path.relative_to(ROOT)}")

    print("\nResumen por área e indicador:")
    resumen = (
        table_df.groupby(
            [
                "geography_level",
                "geography_name",
                "indicator_id",
                "indicator_name",
            ],
            dropna=False,
        )
        .size()
        .rename("observaciones")
    )
    print(resumen.to_string())

    if issues:
        print("\nAvisos:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("\nNo se detectaron indicadores faltantes.")


if __name__ == "__main__":
    main()