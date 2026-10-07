# LAB09 · Híbrido, perfiles y costo frente a utilidad

Evidencia: `reports/lab09/metrics_*.json`, `profiles_*.csv`, `pareto.csv` y `model_comparison.csv`.
Ejecuté 12 corridas: 4 configuraciones × 3 semillas (42, 7, 123), todas con 12 épocas y el mismo
corte temporal. Evalué 587 usuarios; un acierto equivale a 0.17 puntos de HitRate.

## 1. Comparación de los cuatro modelos

Promedio de las 3 semillas con 20 factores y alpha 0.75:

| Modelo | HitRate@10 | Precision@10 | Cobertura | Personalizado |
|---|---|---|---|---|
| Popularidad | **4.26 %** (25 aciertos) | 0.43 % | 1.2 % | No |
| Contenido (perfil de géneros) | 0.17 % (1 acierto) | 0.02 % | 7.8 % | Sí |
| Colaborativo (factorización) | 3.52 % | 0.35 % | 7.0 % | Sí |
| Híbrido | 3.52 % | 0.35 % | 7.2 % | Sí |

Con una sola película retenida por usuario, Precision@10 es siempre HitRate@10 / 10.

**Ningún modelo personalizado supera al baseline de popularidad en aciertos.** Mi interpretación es
que la popularidad acierta más porque la película que un usuario ve a continuación suele ser popular,
pero muestra
las mismas 10 películas a todos y cubre el 1.2 % del catálogo. Los modelos personalizados aciertan
algo menos y cubren entre 6 y 8 veces más catálogo. El contenido puro casi no acierta: los
géneros por sí solos no predicen qué verá cada persona.

## 2. Paso 5 · Híbrido: alpha 0.25 frente a 0.75

`hybrid_score = alpha × colaborativo + (1 − alpha) × contenido`. Ambas señales se normalizan a [0, 1].
El híbrido reordena las 100 mejores candidatas del colaborativo, así que alpha cambia el orden pero
no puede traer películas fuera de esas 100. Para que la comparación fuera controlada, mantuve iguales
semilla, corte, factores (20) y épocas (12), y solo cambié alpha.

| Semilla | Aciertos alpha 0.25 | Aciertos alpha 0.75 | Cobertura 0.25 | Cobertura 0.75 |
|---|---|---|---|---|
| 42 | 19 | 22 | 10.6 % | 7.8 % |
| 7 | 15 | 23 | 10.1 % | 7.0 % |
| 123 | 13 | 17 | 9.7 % | 7.0 % |
| **Media** | **2.67 % ± 0.52** | **3.52 % ± 0.55** | **10.2 %** | **7.2 %** |

El RMSE es idéntico en ambas (1.026), porque alpha no cambia la factorización, solo el ranking.

**Qué señal domina.**
- *alpha 0.75*: domina el colaborativo. Para el usuario con historial amplio, la señal colaborativa
  media en el Top-10 sube de 0.42 a 0.63 respecto de alpha 0.25, y el contenido baja de 0.92 a 0.69.
  Entran películas que no encajan en los géneros del usuario pero que usuarios parecidos valoraron,
  como *Psycho* (contenido 0.20) para el usuario con historial amplio. Con alpha 0.75 el híbrido
  acierta exactamente lo mismo que el colaborativo puro en cada semilla: el 25 % de contenido solo
  reordena dentro de la lista.
- *alpha 0.25*: domina el contenido. La lista se llena de
  películas con géneros idénticos al perfil (*Modern Times*, *City Lights*, *Manhattan* para el
  mismo usuario). Solo 4 de los 10 títulos coinciden con los de alpha 0.75.

**Selección: alpha 0.75.** Elijo alpha 0.75 porque en las tres semillas obtiene más aciertos que
alpha 0.25 (22 contra 19, 23 contra 15 y 17 contra 13), de modo que la ventaja no depende de una
semilla particular. Reconozco que el costo es cobertura: alpha 0.25 cubre unos 3 puntos más del
catálogo. Si el objetivo fuera diversidad y no acierto, alpha 0.25 sería defendible; en este
laboratorio, donde la métrica principal de ranking es HitRate@10, la evidencia favorece 0.75.

## 3. Paso 6 · Tres perfiles

Revisé los archivos `profiles_*.csv`. Como medida de estabilidad conté los títulos que aparecen en el
Top-10 en las tres semillas.

| Perfil | Usuario | Historial | Excluye vistos | Estabilidad (f20, a0.75) | Señal dominante |
|---|---|---|---|---|---|
| Historial amplio | 414 | 2 697 películas | Sí, en las 12 corridas | 7 de 10 | Mixta (colab. 0.63, contenido 0.69) |
| Historial pequeño | 53 | 19 películas | Sí, en las 12 corridas | **0 de 10** | Colaborativa (0.70), contenido más débil (0.58) |
| Usuario nuevo | — | 0 | No aplica | 10 de 10 (siempre la misma) | Ninguna: fallback |

**Historial amplio.** Verifiqué que la lista excluye todo lo visto (`already_seen = False` en todas
las corridas) y que es estable: 7 de 10 títulos se repiten con cualquier semilla (*12 Angry Men*, *Life Is Beautiful*,
*Intouchables*…). Con 2 697 ratings, los factores del usuario quedan bien determinados.

**Historial pequeño.** La lista también excluye lo visto, pero encontré que es inestable: ningún título aparece
en las tres semillas. Con 20 factores y semilla 42 recibe clásicos populares (*The Godfather*,
*Goodfellas*, *Apocalypse Now*); con 10 factores y la misma semilla recibe películas muy distintas
(*Broken Arrow*, *Inspector Gadget*, *RoboCop 3*). Con 19 ratings hay muy poca información para
estimar sus factores, y el resultado depende de la inicialización aleatoria. Al bajar alpha a 0.25
la lista pasa a depender del contenido (0.89), lo que la vuelve más coherente con sus géneros, pero
tampoco estable entre semillas.

**Usuario nuevo.** `top_n` no tiene vector para él y devuelve una lista vacía; el sistema usa el
fallback de popularidad por cantidad y media: *Forrest Gump*, *Shawshank Redemption*, *Pulp
Fiction*, *The Matrix*… (`reports/cold_start_fallback.csv`). La lista siempre se produce y está
marcada `personalized = False`: es igual para cualquier usuario nuevo y debe presentarse como
«populares», no como «recomendado para ti». Comprobé que el fallback produce una lista en todas
las corridas.

## 4. Paso 7 · Costo frente a utilidad (Pareto)

Definí la utilidad como el HitRate@10 del híbrido, y el costo como los segundos de entrenamiento y
el tamaño del modelo. Una configuración está dominada si otra tiene igual o mejor utilidad con igual
o menor costo.

| Configuración | HitRate@10 | Cobertura | RMSE | Entrenamiento | Tamaño | Estado |
|---|---|---|---|---|---|---|
| 10 factores, alpha 0.75 | **4.03 % ± 0.94** | 5.6 % | 1.032 | 13.5 s | 806 KB | **Óptima de Pareto** |
| 20 factores, alpha 0.75 | 3.52 % ± 0.55 | 7.2 % | 1.026 | 14.7 s | 1 611 KB | Dominada por 10 factores |
| 40 factores, alpha 0.75 | 3.86 % ± 0.60 | 9.7 % | 1.021 | 16.0 s | 3 222 KB | Dominada por 10 factores |
| 20 factores, alpha 0.25 | 2.67 % ± 0.52 | 10.2 % | 1.026 | 13.6 s | 1 611 KB | Dominada por 10 factores |

En mi equipo (AMD Ryzen 5 5600X, 32 GB de RAM), la corrida completa (entrenar, evaluar los cuatro
modelos y generar perfiles) tardó entre 27 y 35 s.

**Lectura.** La configuración de 10 factores domina a las demás: obtiene el HitRate medio más alto
con la mitad o la cuarta parte del tamaño y menos tiempo. Más factores reducen el RMSE pero no
mejoran el ranking. Desde la perspectiva Green AI, no encuentro justificación para pagar 4 veces más
memoria por la configuración de 40 factores.

**Límites que reconozco en esta conclusión.**
- La ventaja de 10 factores es de unos 1 a 3 aciertos en promedio y su variación entre semillas es la
  mayor (18 a 29 aciertos). La dominancia se basa en medias y no es estadísticamente sólida.
- La cobertura no forma parte de la utilidad en esta tabla. Si se incluyera, 40 factores (9.7 %)
  dejaría de estar dominada, porque 10 factores tiene la menor cobertura (5.6 %).
- Los tiempos varían entre corridas de la misma configuración (hasta 3 s), así que las diferencias
  de tiempo de 1 a 2 s no son concluyentes; las diferencias de tamaño sí son exactas.

**Configuración seleccionada: 10 factores, 12 épocas, alpha 0.75.** La elijo porque es la óptima de
Pareto en acierto y costo, y la de menor huella computacional. Declaro su principal desventaja: es la
que menos catálogo cubre. Si la diversidad fuera prioritaria, elegiría 40 factores con alpha 0.75,
que casi duplica la cobertura a cambio de 4 veces el tamaño.
