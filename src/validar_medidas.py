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

######################## Carga 3 hab centro

archivo = "data/processed/Costo_de_vida_limpio.xlsx"
datos = pd.read_excel(archivo, sheet_name="Datos_limpios")

#print("Columnas de Datos_limpios:", [repr(columna) for columna in datos.columns])

renta_promedio = pd.to_numeric(
    datos["Renta 3 hab centro USD"],
    errors="coerce"
).mean()

salario_promedio = pd.to_numeric(
    datos["Salario neto mensual promedio USD"],
    errors="coerce"
).mean()

carga_decimal = renta_promedio / salario_promedio

print(f"Renta promedio según pandas: {renta_promedio}")
print(f"Salario promedio según pandas: {salario_promedio}")
print(f"Carga decimal según pandas: {carga_decimal:.6f}")
print(f"Carga porcentual según pandas: {carga_decimal * 100:.2f}%")

############## INEGI
base_inegi = pd.read_parquet(
    "data/processed/inegi_cdmx_20261117T025258Z.parquet"
)

observacion = base_inegi.loc[
    (base_inegi["indicator_id"].astype(str).str.strip() == "6207019027")
    & (base_inegi["geography_code"].astype(str).str.strip() == "09002")
    & (pd.to_numeric(base_inegi["period"], errors="coerce") == 2025),
    "value"
]

print(f"Observaciones encontradas: {len(observacion)}")

if len(observacion) == 1:
    valor_inegi = float(observacion.iloc[0])
    print(f"Valor original de INEGI: {valor_inegi}")
    print(f"Porcentaje esperado en Power BI: {valor_inegi:.2f}%")
