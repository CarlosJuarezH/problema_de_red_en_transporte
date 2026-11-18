# Vivienda y oferta de Airbnb: comparación global y caso de Ciudad de México

Este proyecto analiza diferencias entre renta mensual estimada y salario neto individual en distintas ciudades, y caracteriza la oferta de Airbnb en Ciudad de México por tipo de alojamiento, precio y estancia.

## Pregunta de investigación
¿Cómo varía la relación entre la renta mensual y el salario neto mensual estimado entre las ciudades de la base global, y cómo se distribuye la oferta de Airbnb en Ciudad de México?


## Estructura del repositorio:
```text
problema_de_red_en_transporte/
├── data/
│   ├── raw/                 # Respuestas JSON originales de INEGI
│   └── processed/           # Datos procesados en formato Parquet
├── src/
│   └── descargar_inegi.py   # Consulta la API y genera JSON y Parquet
├── .env.example             # Ejemplo de configuración, sin credenciales
├── .gitignore
├── CITATION.cff
├── LICENSE
├── README.md
└── requirements.txt         # Dependencias de Python con versiones fijadas
```


## Flujo de datos de INEGI

El flujo consulta la API del Banco de Indicadores del INEGI para Ciudad de México (clave geográfica `09`). Recupera la serie histórica de estos indicadores:

| Clave | Indicador | Unidad |
|---|---|---|
| `1002000001` | Población total | Personas |
| `6207019027` | Porcentaje de viviendas particulares habitadas alquiladas | Porcentaje |

La consulta cubre Ciudad de México como entidad federativa y sus 16 alcaldías. Se guarda una respuesta JSON por área geográfica en `data/raw/` y un archivo Parquet conjunto en `data/processed/`. El Parquet conserva el indicador, periodo, valor, código y nombre geográfico, nivel geográfico y metadatos de procedencia.

### Periodos disponibles

- **Ciudad de México como entidad:** población total de 1910 a 2025, en los periodos disponibles de la serie; viviendas alquiladas en 2015 y 2025.
- **Alcaldías:** población total en 1995, 2000, 2005, 2010 y 2020; viviendas alquiladas en 2015 y 2025.

A nivel de alcaldía, los periodos de ambos indicadores no coinciden. Por ello, no deben interpretarse como una comparación de los dos indicadores para un mismo año. 

La extracción validada contiene 130 observaciones, sin valores nulos en `value` ni duplicados por indicador, periodo y geografía.

##  Cómo reproducir el proyecto
Clonar el repositorio (git clone https://github.com/CarlosJuarezH/problema_de_red_en_transporte.git).

Se requiere Python y un token válido de INEGI. En GitHub Codespaces, configura el token como secreto llamado `INEGI_TOKEN` con acceso a este repositorio. No lo incluyas en el código ni en archivos versionados.

Instala las dependencias:

```bash
python -m pip install -r requirements.txt 
```

Ejecuta el flujo:
```bash
python src/descargar_inegi.py
```
## Validación de medidas con pandas

#### Anuncios Airbnb

- **DAX:** `DISTINCTCOUNT(Airbnb_CDMX[listing_id])`
- **Archivo usado:** `data/processed/Airbnb_CDMX.csv`
- **Comprobación en pandas:** conteo de `listing_id` únicos con `nunique(dropna=False)`.
- **Power BI:** 30,468
- **pandas:** 30,468
- **Diferencia:** 0
- **Resultado:** Coinciden; medida validada.

#### Precio mediano por noche MXN

- **DAX:** mediana de `precio_noche_mxn`, filtrando cotizaciones disponibles y no mensualizadas.
- **Archivo usado:** `data/processed/Airbnb_CDMX.csv`
- **Registros con precio considerados por pandas:** 28,063
- **Power BI:** $1,505.00 MXN
- **pandas:** $1,505.00 MXN
- **Diferencia:** $0.00
- **Resultado:** Coinciden; medida validada.

#### Carga 3 hab centro

- **DAX:** `DIVIDE([Renta 3 habitaciones centro USD], [Salario neto mensual en USD])`
- **Archivo usado:** `data/processed/Costo_de_vida_limpio.xlsx`, hoja `Datos_limpios`
- **Renta promedio según pandas:** 1,798.10 USD
- **Salario promedio según pandas:** 2,607.37 USD
- **Carga según pandas:** 68.96 %
- **Power BI:** 68.96 %
- **Resultado:** Coinciden al redondear a dos decimales; medida validada.
- **Contexto:** tabla completa, sin filtros ni segmentadores.

#### Porcentaje de viviendas alquiladas (INEGI)

- **DAX:** promedio de `INEGI[value]` para el indicador `6207019027`, dividido entre 100 y mostrado como porcentaje.
- **Archivo usado:** `data/processed/inegi_cdmx_20261117T025258Z.parquet`
- **Contexto comparado:** `geography_code = 09002`, periodo 2025.
- **Valor original de INEGI según pandas:** 27.966695
- **Power BI:** 27.97 %
- **pandas:** 27.97 %
- **Resultado:** Coinciden al redondear a dos decimales; medida validada.

## Buenas prácticas
- Mantener los datos originales en **data/** sin modificarlos directamente.
- Usar mensajes de commit claros y atómicos para reflejar el progreso.
- Documentar cambios relevantes en **docs/**.

## LICENSE
Este proyecto está bajo la **licencia MIT**.
La elegí porque permite que otros investigadores y estudiantes usen, modifiquen y distribuyan el proyecto libremente, manteniendo el reconocimiento al autor. Al ser un trabajo académico y de investigación se fomenta la colaboración y reutilización del trabajo en distintos contextos.

## Cómo citar
Si utilizas este repositorio en tu trabajo académico, por favor cita de la siguiente manera:
**Juárez Hernández, C. M. (2026). Problema de red en transporte [Repositorio en GitHub]. GitHub. https://github.com/CarlosJuarezH/problema_de_red_en_transporte**

Si utilizas este proyecto, por favor cita el repositorio.  
GitHub genera automáticamente la referencia desde el archivo [CITATION.cff](./CITATION.cff).  
Haz clic en el botón **Cite this repository** en la página principal del repositorio para obtener la cita en APA, BibTeX u otros estilos.
