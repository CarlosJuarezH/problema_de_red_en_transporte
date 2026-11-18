import pandas as pd
#################### Anuncios de Airbnb
airbnb = pd.read_csv("data/processed/Airbnb_CDMX.csv")

anuncios_pandas = airbnb["listing_id"].nunique(dropna=False)
ids_vacios = airbnb["listing_id"].isna().sum()

print(f"Filas en el archivo: {len(airbnb)}")
print(f"listing_id vacíos: {ids_vacios}")
print(f"Anuncios únicos según pandas: {anuncios_pandas}")

##################### Precio mediano por noche MXN
disponible = (
    airbnb["cotizacion_disponible"]
    .astype(str).str.strip().str.upper()
    .eq("TRUE")
)

no_mensualizada = (
    airbnb["cotizacion_mensualizada"]
    .astype(str).str.strip().str.upper()
    .eq("FALSE")
)

precios_validos = pd.to_numeric(
    airbnb.loc[
        disponible & no_mensualizada,
        "precio_noche_mxn"
    ],
    errors="coerce"
)

print(f"Precios considerados: {precios_validos.notna().sum()}")
print(f"Mediana según pandas: {precios_validos.median()}")

##### Carga 3 hab centro
