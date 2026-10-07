# LAB08 · Cierre interpretativo

Estudiante: Jose Miguel Maduro Valenzuela · INF-8239 · Unidad 03 · 2026-10-06

**Resultado principal:**
Construí dos políticas de recomendación sobre MovieLens Latest Small. El baseline de popularidad
suavizada produce un Top-10 estable y dominado por clásicos muy valorados (*Shawshank Redemption*,
*The Godfather*, *Fight Club*), pero es idéntico para todos y cubre solo 10 de 9 742 películas
(≈ 0.1 % del catálogo). El recomendador por contenido (TF-IDF de géneros + coseno) sí cambia según la
película consultada, pero en las tres consultas que hice devolvió diez películas con
`content_score = 1.0`: todas comparten exactamente los géneros de la consulta, de modo que el modelo
no puede distinguirlas y el orden dentro del Top-10 es arbitrario.

**Evidencia utilizada:**
- Dataset que descargué el 2026-10-06, con SHA-256
  `696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436` (`docs/DATASET_CARD.md`).
- Auditoría: 610 usuarios, 9 742 películas, 100 836 ratings, densidad 1.70 % (`reports/audit.txt`).
- Top-10 de popularidad (`reports/popular_top10.csv`).
- Tres consultas por contenido que elegí de géneros distintos: *Toy Story* (animación infantil),
  *Shawshank Redemption* (drama criminal) y *The Shining* (terror)
  (`reports/content_recommendations.csv`, `reports/analisis_contenido.md`).
- Capturas que tomé de la aplicación Streamlit con las mismas tres consultas (`reports/streamlit_*.png`).
- Pruebas automáticas: 7 de 7 aprobadas (`uv run pytest -q`).

**Qué representa la similitud:**
Un `content_score` de 1.0 significa que la película tiene exactamente los mismos géneros registrados
en el catálogo, no que el usuario la vaya a disfrutar ni que sea buena. Lo comprobé en los
resultados: *Toy Story 2*
(97 ratings, media 3.86) aparece detrás de *Turbo* (1 rating, media 2.50), y *Michael Jackson's
Thriller*, un videoclip, queda igual de cerca de *The Shining* que cualquier película de terror. Con
solo 951 combinaciones de géneros para 9 742 películas, los empates son la norma: 12 películas
empatan con *Toy Story*, 133 con *Shawshank* y 166 con *The Shining*, y el Top-10 muestra apenas
una parte de ellas.

**Problema de cold start observado:**
- *Película nueva*: la popularidad exige al menos 12 ratings, así que una película nueva nunca
  aparece en esa lista. El modelo por contenido sí la puede recomendar en cuanto tiene géneros: de
  hecho, observé que varias de sus recomendaciones tienen un solo rating.
- *Usuario nuevo*: el modelo por contenido necesita una película de referencia; sin ella, la única
  respuesta es el Top-10 de popularidad, que no está personalizado.
- No pude medir este problema directamente, porque en el dataset todos los usuarios tienen al menos
  20 ratings.

**Riesgo de sobre-especialización:**
En las tres consultas, el 100 % de las recomendaciones repite los géneros de la película consultada.
Quien consulta *Toy Story* solo ve animación infantil; quien consulta *The Shining* solo ve terror,
sin distinguir terror psicológico de gore (*Hostel*, *The Human Centipede*). En mi opinión, el
sistema refuerza lo ya conocido y no ofrece descubrimiento. A esto se suma que la etiqueta de género
es gruesa: «Crime|Drama» agrupa una película sobre el 11-S (*United 93*) con una de mafia
(*Donnie Brasco*).

**Decisión o siguiente experimento:**
Concluyo que ninguna de las dos políticas es suficiente por sí sola. Como siguiente paso propongo:
1. Desempatar el modelo por contenido con `weighted_score`, para que entre películas igual de
   similares se prefieran las mejor valoradas. Así *Toy Story 2* quedaría por delante de *Turbo*.
2. Combinar el contenido con filtrado colaborativo (factorización de matrices) en un modelo híbrido,
   y evaluarlo con HitRate@10 en una partición temporal. Este experimento lo desarrollo en el LAB09.
