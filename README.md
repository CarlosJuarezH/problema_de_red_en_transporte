# Vivienda y oferta de Airbnb: comparación global y caso de Ciudad de México

Este proyecto analiza diferencias entre renta mensual estimada y salario neto individual en distintas ciudades, y caracteriza la oferta de Airbnb en Ciudad de México por tipo de alojamiento, precio y estancia.

## Pregunta de investigación
¿Cómo varía la relación entre la renta mensual y el salario neto mensual estimado entre las ciudades de la base global, y cómo se distribuye la oferta de Airbnb en Ciudad de México?


## Estructura del repositorio:
problema_de_red_en_transporte/
|-- codigo/        # Scripts de modelado y simulación (Python, R).
|-- datos/         # Dataset de rutas de transporte urbano.
|-- docs/    # Reportes técnicos y artículos en LaTex.
|-- .gitignore
|-- CITATION.cff
|-- LICENSE
|-- README.md      # Descripción general del proyecto.


## Flujo de datos de INEGI

El flujo consulta la API del Banco de Indicadores del INEGI para Ciudad de México (clave geográfica `09`). Recupera la serie histórica de estos indicadores:

| Clave | Indicador | Unidad |
|---|---|---|
| `1002000001` | Población total | Personas |
| `6207019027` | Porcentaje de viviendas particulares habitadas alquiladas | Porcentaje |

El porcentaje de viviendas alquiladas describe la tenencia de las viviendas habitadas; no es una medida del monto de la renta ni identifica viviendas anunciadas en Airbnb.

### Requisitos y ejecución

Se requiere Python y un token válido de INEGI. En GitHub Codespaces, configura el token como secreto llamado `INEGI_TOKEN` con acceso a este repositorio. No lo incluyas en el código ni en archivos versionados.

Instala las dependencias:

```bash
python -m pip install -r requirements.txt 
```

Ejecuta el flujo:
```bash
python src/descargar_inegi.py
```
Archivos generados:
- data/raw/: respuesta JSON original de la API.
- data/processed/: tabla Parquet.
Los nombres de archivo incluyen la fecha y hora de descarga. El Parquet conserva metadatos de procedencia.

##  Cómo reproducir el proyecto
1. Clonar el repositorio (git clone https://github.com/CarlosJuarezH/problema_de_red_en_transporte.git).
2. Abrir los scripts en la carpeta **codigo/** y ejecutarlos en Python o Colab.
3. Los datos de entrada se encuentran en **datos/**.
4. Los resultados y gráficas se guardan en **docs/**.

## Buenas prácticas
- Mantener los datos originales en **datos/** sin modificarlos directamente.
- Usar mensajes de commit claros y atómicos para reflejar el progreso.
- Documentar cambios relevantes en docs/.

## LICENSE
Este proyecto está bajo la **licencia MIT**.
La elegí porque permite que otros investigadores y estudiantes usen, modifiquen y distribuyan el modelo de red tronco-alimentadora libremente, manteniendo el reconocimiento al autor. Al ser un trabajo académico y de investigación se fomenta la colaboración y reutilización del trabajo en distintos contextos.

## Cómo citar
Si utilizas este repositorio en tu trabajo académico, por favor cita de la siguiente manera:
**Juárez Hernández, C. M. (2026). Problema de red en transporte [Repositorio en GitHub]. GitHub. https://github.com/CarlosJuarezH/problema_de_red_en_transporte**

Si utilizas este proyecto, por favor cita el repositorio.  
GitHub genera automáticamente la referencia desde el archivo [CITATION.cff](./CITATION.cff).  
Haz clic en el botón **Cite this repository** en la página principal del repositorio para obtener la cita en APA, BibTeX u otros estilos.
