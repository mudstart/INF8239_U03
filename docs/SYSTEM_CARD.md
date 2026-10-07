# System Card · Recomendador

## Usuarios y propósito
Sistema académico para el curso INF-8239 (LAB08 y LAB09). Ordena películas de MovieLens para comparar
cuatro políticas de recomendación (popularidad, contenido, colaborativa e híbrida) y sus límites.
Usuarios previstos: estudiantes y docentes que evalúan el método. No está pensado para producción ni
para decisiones sobre personas reales.

Una lista recomendada significa «puntúa alto según esta función y estos datos», no «al usuario le
gustará».

## Catálogo y candidatos
- Catálogo: 9 742 películas de `movies.csv` (MovieLens Latest Small, SHA-256 en la Dataset Card).
- **Popularidad suavizada (LAB08)**: solo son candidatas las películas con al menos 12 ratings
  (percentil 80 de conteos), es decir 1 967 películas.
- **Contenido ítem-a-ítem (LAB08)**: todas las películas, excepto la consultada.
- **Modelos por usuario (LAB09)**: las 9 701 películas con al menos un rating en entrenamiento,
  excluyendo las que el usuario ya valoró. El colaborativo propone sus 100 mejores candidatas y el
  híbrido las reordena; el híbrido no puede recomendar fuera de esas 100.
- Fallback de usuario nuevo: las 10 películas con más ratings en entrenamiento (desempate por media).

## Señales utilizadas
| Señal | Origen | Modelos |
|---|---|---|
| Rating explícito (0.5–5) | `ratings.csv` | Popularidad, colaborativo, perfil de contenido |
| Número de ratings por película | `ratings.csv` | Popularidad, fallback |
| Géneros (TF-IDF) | `movies.csv` | Contenido, híbrido |
| Timestamp | `ratings.csv` | Solo para el corte temporal de evaluación |

No se usan tags, sinopsis ni datos demográficos (el dataset no los tiene).

## Modelos y fallback
**1. Popularidad suavizada** (`weighted_popularity`). Promedio bayesiano
`n / (n + m) · media_película + m / (n + m) · media_global`, con `m = 12` y media global 3.50. Igual
para todos los usuarios. Top-10: *Shawshank Redemption*, *The Godfather*, *Fight Club*…
(`reports/popular_top10.csv`).

**2. Contenido** (`ContentRecommender`). TF-IDF de géneros y similitud coseno. En LAB08 parte de una
película; en LAB09 parte de un perfil de usuario: promedio de los géneros de su historial, ponderado
por `rating − 2.5` (mínimo 0.1).

**3. Colaborativo** (`MatrixFactorization`). Factorización por descenso de gradiente estocástico:
`rating ≈ media_global + usuario · película`, con vectores latentes, tasa de aprendizaje 0.01 y
regularización 0.05. Los factores latentes no tienen un significado humano garantizado.

**4. Híbrido.** `hybrid = alpha · colaborativo + (1 − alpha) · contenido`, ambas señales
normalizadas a [0, 1] dentro de las 100 candidatas del colaborativo.

**Configuración seleccionada: 10 factores, 12 épocas, alpha 0.75.** Es la única óptima de Pareto en
HitRate@10 frente a tiempo y tamaño, y alpha 0.75 supera a 0.25 en las tres semillas evaluadas
(`reports/lab09/analisis_hibrido.md`). Su desventaja declarada es la menor cobertura de catálogo.

**Fallback.** Si el usuario no está en el entrenamiento, `top_n` devuelve una lista vacía y se usa la
lista de popularidad (`reports/cold_start_fallback.csv`), marcada `personalized = False`. Debe
presentarse como «populares», no como «recomendado para ti». En la aplicación, un título inexistente
produce `KeyError` en lugar de una lista inventada.

## Métricas offline
**Protocolo.** Corte temporal leave-one-out: se reserva la última valoración de cada usuario y se
entrena con las anteriores (sin usar interacciones futuras). Se evalúan 587 de 610 usuarios; en los
otros 23 la película retenida no aparece en entrenamiento (cold start de ítem). Tres semillas por
configuración (42, 7, 123). Un acierto equivale a 0.17 puntos de HitRate.

**Comparación de modelos** (20 factores, alpha 0.75, media de 3 semillas):

| Modelo | HitRate@10 | Precision@10 | Cobertura |
|---|---|---|---|
| Popularidad | 4.26 % | 0.43 % | 1.2 % |
| Contenido | 0.17 % | 0.02 % | 7.8 % |
| Colaborativo | 3.52 % | 0.35 % | 7.0 % |
| Híbrido | 3.52 % | 0.35 % | 7.2 % |

**Configuraciones del híbrido** (media ± desviación de 3 semillas):

| Factores | alpha | RMSE | HitRate@10 | Cobertura | Entrenamiento | Tamaño |
|---|---|---|---|---|---|---|
| 10 | 0.75 | 1.032 | 4.03 % ± 0.94 | 5.6 % | 13.5 s | 806 KB |
| 20 | 0.75 | 1.026 | 3.52 % ± 0.55 | 7.2 % | 14.7 s | 1 611 KB |
| 40 | 0.75 | 1.021 | 3.86 % ± 0.60 | 9.7 % | 16.0 s | 3 222 KB |
| 20 | 0.25 | 1.026 | 2.67 % ± 0.52 | 10.2 % | 13.6 s | 1 611 KB |

Referencias de RMSE: predecir la media global da 1.116; predecir la media de cada usuario, 1.023.

**Lectura.** Ningún modelo personalizado supera a la popularidad en aciertos, pero esta cubre solo el
1.2 % del catálogo. Más factores bajan el RMSE sin mejorar el ranking. Las diferencias de HitRate
entre configuraciones son del mismo orden que la variación entre semillas: no son concluyentes.

Pruebas automáticas: `tests/test_data.py`, `tests/test_content.py`,
`tests/test_matrix_factorization.py` y `tests/test_metrics.py` (7 de 7 aprobadas).

## Cold start, cobertura y diversidad
**Cold start.**
- *Usuario nuevo*: sin señal colaborativa; recibe el fallback de popularidad, no personalizado. Los
  datos no tienen usuarios con menos de 20 ratings, así que se simula.
- *Usuario con poco historial*: el usuario 53 (19 ratings) recibe listas sin ningún título en común
  entre las tres semillas; sus factores dependen de la inicialización aleatoria. El usuario 414
  (2 697 ratings) mantiene 7 de 10 títulos.
- *Película nueva*: no tiene vector colaborativo ni entra en la popularidad (`count >= 12`); solo el
  contenido puede recomendarla. En el corte temporal afecta a 23 usuarios.
- *Película sin géneros*: las 34 películas con `(no genres listed)` solo se parecen entre sí.

**Cobertura.** Popularidad 1.2 %; híbrido entre 5.6 % y 10.2 % según la configuración. Bajar alpha a
0.25 o subir a 40 factores aumenta la cobertura; la configuración seleccionada es la de menor
cobertura entre las personalizadas.

**Diversidad y sobre-especialización.** En el LAB08, el 100 % de las recomendaciones por contenido
repetía exactamente los géneros consultados, con empates en `content_score = 1.0` (hay 951
combinaciones de géneros para 9 742 películas). Con alpha 0.25 el híbrido hereda esta tendencia: la
señal de contenido media en el Top-10 llega a 0.92.

## Riesgos y monitoreo
| Riesgo | Efecto | Mitigación o monitoreo |
|---|---|---|
| Popularidad dominante | Los mismos títulos para muchas personas; el baseline popular gana en aciertos con 1.2 % de cobertura | Reportar cobertura junto al HitRate; limitar ítems muy populares en el Top-10 |
| Burbuja de filtro | Poca exposición a categorías distintas; contenido puro 100 % del mismo género | Medir diversidad de géneros del Top-10; reservar posiciones para exploración |
| Sesgo de selección | Solo se observan ratings de lo consumido; ausencia ≠ rechazo | Interpretar métricas como relativas a lo observado |
| Ausencia de demografía | No se puede afirmar desempeño por grupos ni auditar equidad | Declarar el límite; no extrapolar a poblaciones |
| Retroalimentación | Las recomendaciones cambiarían las interacciones que luego entrenan el modelo; la evaluación offline no lo mide | Registrar lo recomendado; monitorear concentración del catálogo en el tiempo |
| Inestabilidad con poco historial | Listas que cambian con la semilla | Dar más peso al contenido o a la popularidad cuando el historial es pequeño |
| Incertidumbre de la métrica | Diferencias de 1–3 aciertos dentro del ruido | Reportar media y desviación de varias semillas |
| Empates y títulos duplicados | Orden arbitrario; búsqueda por título ambigua | Desempatar con popularidad; consultar por `movieId` |
| Versión cambiante del dataset y dependencias | Resultados no reproducibles; el código base falló con scikit-learn reciente (`np.matrix`) | Registrar SHA-256; fijar dependencias con `uv.lock` |
| Interpretación como verdad | Uso indebido del Top-10 | La interfaz muestra método y limitaciones; documentar fallback no personalizado |
