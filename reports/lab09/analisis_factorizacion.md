# LAB09 · Interpretación de la factorización y riesgos

Evidencia: `reports/lab09/metrics_*.json` y `reports/lab09/pareto.csv`, que generé con
`scripts/lab09_hybrid.py` (12 épocas, alpha 0.75, semillas 42, 7 y 123) y `scripts/lab09_pareto.py`.
Usé un corte temporal leave-one-out: reservé la última valoración de cada usuario y evalué 587 de
610 usuarios.

## 1. Resultados de la factorización

| Factores | RMSE (media ± desv.) | HitRate@10 híbrido | Cobertura | Entrenamiento | Tamaño |
|---|---|---|---|---|---|
| 10 | 1.032 ± 0.005 | 4.03 % ± 0.94 | 5.6 % | 13.5 s | 806 KB |
| 20 | 1.026 ± 0.000 | 3.52 % ± 0.55 | 7.2 % | 14.7 s | 1 611 KB |
| 40 | 1.021 ± 0.003 | 3.86 % ± 0.60 | 9.7 % | 16.0 s | 3 222 KB |

Para tener un punto de comparación, calculé dos referencias simples sobre los mismos 587 usuarios:

| Referencia | RMSE |
|---|---|
| Predecir la media global (3.50) | 1.116 |
| Predecir la media de cada usuario | 1.023 |

Con 587 usuarios evaluados, un acierto adicional equivale a 0.17 puntos de HitRate.

## 2. Interpretación prudente

**RMSE disminuye.** Al pasar de 10 a 40 factores el RMSE baja de 1.032 a 1.021: el modelo aproxima
algo mejor los ratings retenidos. Sin embargo, la mejora es pequeña y me llamó la atención que la
factorización con 20 factores (1.026) no supera a la regla trivial de predecir el promedio de cada
usuario (1.023). Además, el HitRate no sigue la misma tendencia que el RMSE. *No puedo concluir* que
un RMSE menor produzca mejores listas: predecir ratings y ordenar ítems son tareas distintas.

**HitRate sube y cobertura baja.** La configuración con mayor HitRate (10 factores, 4.03 %) es la de
menor cobertura (5.6 %), y el baseline de popularidad, con el HitRate más alto de todos (4.26 %),
cubre solo el 1.2 % del catálogo. Interpreto que los aciertos se obtienen concentrando las
recomendaciones en películas populares. *No puedo concluir* que el modelo con más aciertos sea el más
útil: también es el que muestra menos variedad.

**Más factores sin mejora.** Cuadruplicar los factores (de 10 a 40) multiplica por 4 el tamaño del
modelo y aumenta un 18 % el tiempo de entrenamiento, pero el HitRate no mejora (4.03 % → 3.86 %).
Las diferencias entre configuraciones (0.5 puntos) son del mismo orden que la variación entre
semillas (0.5–0.9 puntos), es decir, unos 3 usuarios. *No tengo evidencia suficiente* para afirmar
que alguna configuración es mejor en ranking; sí la tengo de que las más grandes cuestan más.

**Usuario fuera del entrenamiento.** Como todos los usuarios tienen al menos 20 ratings, los 610
aparecen en el entrenamiento y el cold start de usuario no ocurre en este corte. Lo que sí encontré
es cold start de ítem: en 23 usuarios la película retenida no fue vista por nadie durante el
entrenamiento, el modelo no tiene vector para ella y esos casos quedan fuera de la evaluación. Para un usuario
nuevo, `top_n` devuelve una lista vacía; el sistema usa entonces el fallback de popularidad
(*Forrest Gump*, *Shawshank Redemption*, *Pulp Fiction*…), registrado en `profiles_*.csv` con
`personalized = False`. Esa lista es igual para todos y no debe presentarse como personalizada.

## 3. Riesgos

Identifiqué los siguientes riesgos a partir de la evidencia de ambos laboratorios. Considero que el
principal es la popularidad dominante.

| Riesgo | Evidencia en este laboratorio | Mitigación |
|---|---|---|
| **Popularidad dominante** | La popularidad obtiene el mejor HitRate (4.26 %) con 1.2 % de cobertura; el fallback de usuario nuevo y varias recomendaciones del usuario con poco historial (*The Godfather*, *Goodfellas*) son títulos del Top de popularidad | Reportar cobertura junto al HitRate; penalizar o limitar ítems muy populares en el Top-10 |
| **Burbuja de filtro** | En el LAB08, el 100 % de las recomendaciones por contenido repetía los géneros consultados; en el híbrido, la cobertura total no supera el 10.7 % del catálogo | Medir la diversidad de géneros del Top-10; reservar posiciones para exploración |
| **Sesgo de selección** | Solo se observan ratings de películas que cada persona eligió ver; la media es 3.50 y la moda 4.0. Un rating ausente no significa rechazo | No interpretar la ausencia como desinterés; tratar los resultados como relativos a lo observado |
| **Ausencia de demografía** | El dataset no tiene edad, sexo ni país | No afirmar que el sistema funciona igual para distintos grupos; no es posible auditar equidad con estos datos |
| **Retroalimentación** | La evaluación es offline: no mide cómo las recomendaciones cambiarían lo que la gente ve y valora después | Si se desplegara, monitorear la concentración del catálogo en el tiempo y reentrenar con cuidado; registrar qué se recomendó |
| **Incertidumbre de la métrica** | Diferencias de HitRate de 0.5 puntos equivalen a unos 3 usuarios y están dentro de la variación entre semillas | Reportar media y desviación sobre varias semillas; no elegir configuraciones por diferencias menores que el ruido |
