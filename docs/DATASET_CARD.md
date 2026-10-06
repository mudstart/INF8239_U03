# Dataset Card · MovieLens

## Fuente, fecha, versión y hash
| Campo | Valor |
|---|---|
| Nombre | MovieLens Latest Small (`ml-latest-small`) |
| Publicador | GroupLens Research, University of Minnesota |
| URL | https://files.grouplens.org/datasets/movielens/ml-latest-small.zip |
| Versión | Generada por GroupLens el 2018-09-26 (versión de desarrollo, no archivada) |
| Fecha de descarga | 2026-10-06 |
| SHA-256 del ZIP | `696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436` |
| Tamaño | ~1 MB comprimido |

GroupLens advierte que esta es una versión de *desarrollo*: puede cambiar con el tiempo y no es
apropiada para resultados de investigación compartidos. Los resultados de este proyecto solo son
comparables con descargas que produzcan el mismo hash.

## Licencia y cita
Condiciones del `README.txt` oficial:
- Uso permitido para fines de investigación.
- Debe citarse el dataset en cualquier publicación derivada.
- No se puede declarar ni insinuar respaldo de la University of Minnesota ni de GroupLens.
- Puede redistribuirse, incluso transformado, solo bajo estas mismas condiciones.
- Prohibido el uso comercial o con fines de lucro sin permiso de GroupLens.
- Se entrega «tal cual», sin garantía de exactitud ni idoneidad.

Cita: Harper, F. M., & Konstan, J. A. (2015). The MovieLens datasets: History and context.
*ACM Transactions on Interactive Intelligent Systems, 5*(4), Article 19.
https://doi.org/10.1145/2827872

## Archivos y diccionario
CSV con encabezado, codificación UTF-8.

| Archivo | Filas | Columna | Descripción |
|---|---|---|---|
| `ratings.csv` | 100 836 | `userId` | Identificador anónimo del usuario |
| | | `movieId` | Identificador de película (igual que en movielens.org) |
| | | `rating` | Valoración explícita de 0.5 a 5.0 en pasos de 0.5 |
| | | `timestamp` | Segundos desde 1970-01-01 UTC |
| `movies.csv` | 9 742 | `movieId` | Clave de película |
| | | `title` | Título con año entre paréntesis |
| | | `genres` | Géneros separados por `\|` (20 valores, incluido `(no genres listed)`) |
| `tags.csv` | 3 683 | `userId`, `movieId`, `tag`, `timestamp` | Etiquetas de texto libre creadas por usuarios |
| `links.csv` | 9 742 | `movieId`, `imdbId`, `tmdbId` | Enlaces a IMDb y TMDb |

Este proyecto usa `ratings.csv` y `movies.csv`; `tags.csv` y `links.csv` no se utilizan.

## Procedimiento de descarga
```bash
uv run python scripts/download_data.py   # descarga, calcula SHA-256 y extrae en data/raw/
uv run python scripts/audit_data.py      # valida y resume
```
`download_zip` (`src/inf8239_u03/data.py`) calcula el hash sobre los bytes descargados y rechaza
rutas inseguras dentro del ZIP. `load_movielens` valida columnas obligatorias, que todo `movieId` de
ratings exista en movies (clave foránea) y que los ratings estén en [0.5, 5.0]. Los datos crudos
viven en `data/raw/` y no se editan ni se suben al repositorio (`.gitignore`).

## Población observada y exclusiones
Resultados de la auditoría (2026-10-06):

| Medida | Valor |
|---|---|
| Usuarios | 610 |
| Películas en catálogo / con al menos un rating | 9 742 / 9 724 (18 solo tienen tags) |
| Ratings | 100 836 |
| Rango temporal | 1996-03-29 a 2018-09-24 |
| Densidad usuario × película | 1.70 % |
| Ratings por usuario (mín / mediana / máx) | 20 / 70.5 / 2 698 |
| Ratings por película (mediana) | 3; 3 446 películas tienen un solo rating |
| Media de rating (desv. estándar) | 3.50 (1.04) |

- Usuarios elegidos al azar por GroupLens, **todos con al menos 20 películas valoradas**: no hay
  usuarios casuales ni nuevos, así que el cold start de usuario no está representado.
- Sin datos demográficos: no es posible auditar sesgos por edad, sexo o país.
- Solo se incluyen películas con al menos un rating o tag.

## Calidad, sesgos y usos prohibidos
**Calidad.** Sin valores nulos en `ratings`, `movies` ni `tags`; sin pares usuario–película
duplicados; todas las claves foráneas válidas. `links.csv` tiene 8 `tmdbId` faltantes. Hay 5 títulos
duplicados con distinto `movieId` y géneros (p. ej. *Emma (1996)*, *War of the Worlds (2005)*); una
búsqueda por título toma solo la primera coincidencia. 34 películas tienen `(no genres listed)`.

**Sesgos.**
- *Autoselección*: las personas valoran lo que eligieron ver. La distribución está cargada hacia
  valores altos (moda 4.0) y la ausencia de rating no significa rechazo.
- *Popularidad / cola larga*: pocas películas concentran muchos ratings y la mediana es 3; los
  modelos tienden a favorecer lo ya popular.
- *Usuarios muy activos*: un usuario aporta 2 698 ratings; pocos usuarios pesan mucho en las medias.
- *Géneros*: Drama (4 361) y Comedy (3 756) dominan; Film-Noir (87) y Western (167) son escasos.
  La etiqueta de género es gruesa y asignada por catálogo, no por el usuario.
- *Temporal*: datos de 1996–2018; no reflejan el catálogo ni los gustos actuales.

**Usos prohibidos o no apropiados.**
- Uso comercial sin permiso de GroupLens.
- Presentar resultados como representativos de la población general o de usuarios nuevos.
- Inferir atributos personales o reidentificar usuarios.
- Publicar resultados científicos comparables sin registrar el hash, porque la versión cambia.
