# LAB08 · Análisis de popularidad y recomendación por contenido

Evidencia: `reports/popular_top10.csv` y `reports/content_recommendations.csv`, generados con
`uv run python scripts/lab08_content.py` sobre MovieLens Latest Small
(SHA-256 `696d65a3…e436`, descargado el 2026-10-06).

## 1. Baseline de popularidad suavizada

| # | Película | count | mean | weighted_score |
|---|---|---|---|---|
| 1 | Shawshank Redemption, The (1994) | 317 | 4.429 | 4.395 |
| 2 | Godfather, The (1972) | 192 | 4.289 | 4.243 |
| 3 | Fight Club (1999) | 218 | 4.273 | 4.233 |
| 4 | Star Wars: Episode IV (1977) | 251 | 4.231 | 4.198 |
| 5 | Usual Suspects, The (1995) | 204 | 4.238 | 4.197 |
| 6 | Godfather: Part II, The (1974) | 129 | 4.260 | 4.195 |
| 7 | Schindler's List (1993) | 220 | 4.225 | 4.188 |
| 8 | Goodfellas (1990) | 126 | 4.250 | 4.185 |
| 9 | Dr. Strangelove (1964) | 97 | 4.268 | 4.184 |
| 10 | Dark Knight, The (2008) | 149 | 4.238 | 4.183 |

El puntaje suavizado combina la media de cada película con la media global (3.50), con peso
`m = 12` (percentil 80 de conteos). Solo compiten las 1 967 películas con al menos 12 ratings.

- **La evidencia cambia el orden.** *Godfather: Part II* tiene una media mayor que *Star Wars*
  (4.260 contra 4.231), pero con 129 ratings frente a 251; al suavizar queda por debajo
  (4.195 contra 4.198). Lo mismo ocurre con *Dr. Strangelove* (media 4.268, solo 97 ratings), que
  baja al puesto 9 detrás de películas con media menor.
- **Una sola valoración alta no domina.** *Asterix and the Vikings* tiene media 5.0 con un único
  rating y ni siquiera es candidata.
- **Limitaciones.** La lista es idéntica para todos los usuarios y cubre 10 de 9 742 películas
  (≈ 0.1 % del catálogo). Favorece dramas y clásicos muy valorados por los 610 usuarios observados.

## 2. Consultas por contenido

El modelo representa los géneros de cada película con TF-IDF y ordena por similitud coseno.
Se consultaron tres películas de géneros distintos:

| Consulta | Géneros | Películas con géneros idénticos | Puesto en popularidad |
|---|---|---|---|
| Toy Story (1995) | Adventure, Animation, Children, Comedy, Fantasy | 12 | 187 |
| Shawshank Redemption, The (1994) | Crime, Drama | 133 | 1 |
| Shining, The (1980) | Horror | 166 | 66 |

En las tres consultas, las 10 recomendaciones tienen `content_score = 1.0`.

### 2.1 Toy Story (1995)
Turbo · Emperor's New Groove · Adventures of Rocky and Bullwinkle · **Toy Story 2** · Asterix and
the Vikings · Antz · The Wild · Shrek the Third · The Good Dinosaur · **Monsters, Inc.**

- La película consultada no aparece en su propio Top-10.
- Los cinco géneros de *Toy Story* explican todas las posiciones: las diez comparten exactamente
  la misma combinación.
- La secuela *Toy Story 2* (97 ratings, media 3.86) aparece en el puesto 4, por debajo de *Turbo*
  (1 rating, media 2.50) y *Rocky and Bullwinkle* (media 2.22). El modelo no distingue calidad ni
  relación de franquicia.

### 2.2 Shawshank Redemption, The (1994)
Short Film About Killing · Tattooed Life · Gomorrah · The Infiltrator · Felon · Donnie Brasco ·
United 93 · Freedomland · Lights in the Dusk · Once Upon a Time in America

- La película consultada no aparece en su propio Top-10.
- `Crime|Drama` es una combinación muy común: 133 películas empatan con 1.0 y el Top-10 es solo
  una muestra de ellas.
- *Shawshank* es la número 1 en popularidad, pero sus recomendaciones son en su mayoría películas
  con 1 o 2 ratings. Similitud de contenido y calidad percibida son cosas distintas.
- *United 93* (drama sobre el 11-S) aparece al mismo nivel que *Donnie Brasco* (drama de mafia):
  la etiqueta «Crime|Drama» agrupa temas muy diferentes.

### 2.3 Shining, The (1980)
Hellraiser III · Southbound · Hostel · Michael Jackson's Thriller · Witchfinder General ·
Halloween (2007) · Spirit Camp · The Human Centipede · The Awakening · The Last Winter

- La película consultada no aparece en su propio Top-10.
- `Horror` es un único género, así que cualquier película etiquetada solo como terror es idéntica
  para el modelo: 166 empates.
- *Michael Jackson's Thriller* es un videoclip, no un largometraje, y queda igual de cerca que
  cualquier película de terror.
- *The Human Centipede* (1 rating de 0.5) se recomienda con el mismo puntaje que el resto. El
  terror psicológico de *The Shining* y el gore de *Hostel* no se distinguen.

## 3. Interpretación

**Qué representa la similitud.** `content_score = 1.0` significa «tiene exactamente los mismos
géneros registrados en el catálogo», no «le gustará al usuario» ni «es una buena película». El
modelo no usa ratings, sinopsis, director, año ni tags.

**Por qué hay empates.** Hay 9 742 películas pero solo 951 combinaciones distintas de géneros. Cuando
varias películas comparten la combinación de la consulta, todas obtienen 1.0 y el orden entre
ellas depende solo de cómo el algoritmo de ordenamiento resuelve los empates. Ese orden es
arbitrario y no se debe interpretar: el puesto 1 no es «más parecido» que el puesto 10.

**Sobre-especialización.** En las tres consultas, el 100 % de las recomendaciones repite los géneros
de la película consultada. Quien consulta *Toy Story* nunca verá una comedia para adultos ni un
drama, aunque el historial real de quienes valoraron *Toy Story* incluya esos géneros.

**Cold start.**
- *Película nueva*: el modelo por contenido sí puede recomendarla en cuanto tiene géneros. Por eso
  aparecen títulos con 1 rating, que la popularidad nunca mostraría (exige al menos 12).
- *Usuario nuevo*: el modelo por contenido necesita una película de referencia; sin ella, la
  única respuesta disponible es el Top-10 de popularidad.

**Posibles mejoras.** Desempatar con `weighted_score` para que entre películas igual de
similares se prefieran las mejor valoradas; agregar señales más finas (tags, año, director);
medir la diversidad de géneros del Top-10; y combinar contenido con filtrado colaborativo, que es
el objetivo del LAB09.
