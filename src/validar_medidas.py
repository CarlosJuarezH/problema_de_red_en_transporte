import pandas as pd

airbnb = pd.read_csv("data/processed/Airbnb_CDMX.csv")

anuncios_pandas = airbnb["listing_id"].nunique(dropna=False)
ids_vacios = airbnb["listing_id"].isna().sum()

print(f"Filas en el archivo: {len(airbnb)}")
print(f"listing_id vacíos: {ids_vacios}")
print(f"Anuncios únicos según pandas: {anuncios_pandas}")
