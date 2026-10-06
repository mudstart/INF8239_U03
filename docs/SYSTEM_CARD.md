# System Card · Recomendador

## Usuarios y propósito
Sistema académico para el curso INF-8239 (LAB08). Ordena películas de MovieLens para ilustrar dos
políticas de recomendación y sus límites. Usuarios previstos: estudiantes y docentes que evalúan el
método. No está pensado para producción ni para decisiones sobre personas reales.

Una lista recomendada significa «puntúa alto según esta función y estos datos», no «al usuario le
gustará».

## Catálogo y candidatos
- Catálogo: 9 742 películas de `movies.csv` (MovieLens Latest Small, SHA-256 en la Dataset Card).
- **Popularidad**: solo son candidatas las películas con un número de ratings mayor o igual al
  percentil 80 (`count >= 12`), es decir 1 967 películas. El resto nunca puede aparecer.
- **Contenido**: todas las películas son candidatas, excepto la película consultada, que se excluye
  de su propio Top-k.
- No se filtran películas ya vistas por el usuario, porque el modelo por contenido no usa historial
  de usuario.

## Señales utilizadas
| Señal | Origen | Modelo |
|---|---|---|
| Rating explícito (0.5–5) | `ratings.csv` | Popularidad |
| Número de ratings por película | `ratings.csv` | Popularidad |
| Géneros | `movies.csv` | Contenido |

No se usan tags, timestamps, datos demográficos ni texto de sinopsis.

## Modelos y fallback
**1. Baseline de popularidad suavizada** (`weighted_popularity`). Promedio bayesiano:

`score = n / (n + m) · media_película + m / (n + m) · media_global`

con `m = 12` (percentil 80 de conteos) y media global 3.50. Una película con pocas valoraciones se
acerca a la media global, así que una sola valoración de 5 no domina el ranking. Es igual para todos
los usuarios. Top-10 actual: *Shawshank Redemption* (4.40), *The Godfather* (4.24),
*Fight Club* (4.23)… (`reports/popular_top10.csv`).

**2. Recomendador por contenido** (`ContentRecommender`). Representa los géneros con TF-IDF y
ordena por similitud coseno con la película consultada. Es ítem-a-ítem: parte de una película, no de
un perfil de usuario.

**Fallback.** Para un usuario sin historial se usa la lista de popularidad. Si el título consultado no
existe, el modelo por contenido lanza `KeyError` y la aplicación debe mostrar el error en lugar de
inventar una lista.

## Métricas offline
En LAB08 no hay evaluación offline con un conjunto de prueba; la validación es cualitativa: revisar
que la película consultada no se recomiende a sí misma, explicar los géneros compartidos y
detectar empates. Las pruebas automáticas (`tests/test_content.py`, `tests/test_data.py`) verifican
contratos de datos y comportamiento. HitRate@10 y cobertura de catálogo con partición temporal
leave-one-out se calculan en LAB09 (`scripts/lab09_hybrid.py`).

## Cold start, cobertura y diversidad
**Cold start.**
- *Usuario nuevo*: no hay historial; la popularidad sirve como respuesta por defecto, pero no está
  personalizada. Los datos no contienen usuarios con menos de 20 ratings, así que este caso no se
  puede medir.
- *Película nueva*: no tiene ratings, por lo que nunca entra en la lista de popularidad
  (`count >= 12`). El modelo por contenido sí puede recomendarla en cuanto tiene géneros.
- *Película sin géneros*: las 34 películas con `(no genres listed)` solo se parecen entre sí.

**Cobertura.** La popularidad muestra las mismas 10 películas a todos: 10 / 9 742 ≈ 0.1 % del
catálogo. El modelo por contenido cubre más catálogo según la película consultada, pero sin
personalización.

**Diversidad y sobre-especialización.** Con *Toy Story (1995)* las 10 recomendaciones son de
animación infantil y todas tienen `content_score = 1.0`, porque comparten exactamente los mismos
cinco géneros. Solo hay 951 combinaciones distintas de géneros en 9 742 películas, así que los
empates son frecuentes y el orden dentro de un empate es arbitrario. Una secuela y una película
poco conocida reciben la misma puntuación.

## Riesgos y monitoreo
| Riesgo | Efecto | Mitigación o monitoreo |
|---|---|---|
| Sesgo de popularidad | Refuerza lo ya conocido; la cola larga queda invisible | Medir cobertura de catálogo; combinar con contenido o factorización (LAB09) |
| Sobre-especialización | Listas homogéneas que repiten géneros | Medir diversidad de géneros en el Top-k; desempatar con popularidad |
| Empates de similitud | Orden arbitrario y poco informativo | Reportar empates; añadir señales (tags, año) |
| Títulos duplicados | La búsqueda por título toma la primera coincidencia | Consultar por `movieId` |
| Datos antiguos y no representativos | Conclusiones que no generalizan | Declarar límites; no extrapolar a usuarios nuevos |
| Versión cambiante del dataset | Resultados no reproducibles | Registrar fecha, URL y SHA-256 |
| Interpretación como verdad | Uso indebido del Top-10 | La interfaz muestra fuente, método y limitaciones |
