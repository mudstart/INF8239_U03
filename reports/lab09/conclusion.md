# LAB09 · Cierre interpretativo

Estudiante: Jose Miguel Maduro Valenzuela · INF-8239 · Unidad 03 · 2026-10-06

Evidencia: `reports/lab09/` (12 corridas, `pareto.csv`, `model_comparison.csv`, `profiles_*.csv`,
`analisis_factorizacion.md`, `analisis_hibrido.md`) y `docs/SYSTEM_CARD.md`. Trabajé con un corte
temporal leave-one-out sobre MovieLens Latest Small (SHA-256 `696d65a3…e436`) y evalué 587 usuarios.

**Resultado de ratings:**
La factorización predice la última valoración de cada usuario con un RMSE de 1.021 a 1.032 según el
número de factores: al aumentar los factores el error baja levemente. Sin embargo, al compararla con
referencias simples encontré que mejora poco: predecir la media global da 1.116 y predecir la media
de cada usuario da 1.023, prácticamente lo mismo que el modelo con 20 factores (1.026). Concluyo que
el modelo aproxima ratings, pero no captura mucho más que el nivel promedio de cada persona.

**Resultado de ranking:**
Un RMSE menor no produjo mejores listas. El HitRate@10 del híbrido fue de 4.03 % con 10 factores,
3.52 % con 20 y 3.86 % con 40, sin seguir la tendencia del RMSE. El resultado que más me interesa
destacar es que el baseline de popularidad obtuvo el mayor HitRate (4.26 %, 25 de 587 usuarios), por
encima de todos los modelos personalizados, mientras que el contenido puro acertó en un solo usuario
(0.17 %). Las diferencias entre configuraciones equivalen a 1–3 aciertos y están dentro de la
variación entre semillas (desviación de 0.5 a 0.9 puntos), así que no las considero concluyentes.

**Cobertura del catálogo:**
La popularidad muestra las mismas películas a todos y cubre el 1.2 % del catálogo; los modelos
personalizados cubren entre 5.6 % y 10.2 %. Observé una tensión clara entre acierto y diversidad: la
configuración con más aciertos (10 factores) es la de menor cobertura, y al bajar alpha a 0.25 la
cobertura sube de 7.2 % a 10.2 %, pero se pierden aciertos en las tres semillas.

**Comportamiento del usuario frío:**
Para un usuario nuevo no existe señal colaborativa: `top_n` devuelve una lista vacía y el sistema usa
el fallback de popularidad (*Forrest Gump*, *Shawshank Redemption*, *Pulp Fiction*…), que siempre es
la misma y está marcada como no personalizada. Comprobé que el problema también aparece con poco
historial: el usuario 53, con 19 ratings, no conserva ningún título de su Top-10 entre las tres
semillas, mientras que el usuario 414, con 2 697 ratings, conserva 7 de 10. Con pocos datos, la
recomendación depende más de la inicialización aleatoria que del gusto del usuario. Además, en 23
usuarios la película retenida no existía en el entrenamiento (cold start de ítem) y no pude evaluarlos.

**Configuración seleccionada y evidencia:**
Seleccioné 10 factores, 12 épocas y alpha 0.75.
- *alpha 0.75 frente a 0.25*: con los mismos factores, épocas, corte y semilla, alpha 0.75 obtuvo más
  aciertos en las tres semillas (22 contra 19, 23 contra 15, 17 contra 13). Con alpha 0.75 domina la
  señal colaborativa; con 0.25 domina el contenido y las listas repiten los géneros del perfil.
- *10 factores*: es la única configuración óptima de Pareto. Obtiene el HitRate medio más alto
  (4.03 %) con 806 KB y 13.5 s de entrenamiento, frente a 3 222 KB y 16.0 s de la de 40 factores.
- *Limitaciones que reconozco*: la ventaja en HitRate no es estadísticamente sólida y es la
  configuración con menor cobertura. Si la diversidad fuera la prioridad, elegiría 40 factores con
  alpha 0.75 (9.7 % de cobertura).

**Costo computacional:**
Ejecuté todas las corridas en un equipo personal (AMD Ryzen 5 5600X, 6 núcleos / 12 hilos, 32 GB de
RAM, Windows 11 Pro). Cada corrida completa (entrenar, evaluar los cuatro modelos y generar perfiles)
tardó entre 27 y 35 s, y el entrenamiento entre 12 y 16 s. El tamaño del modelo crece de forma lineal
con los factores: 806 KB, 1 611 KB y 3 222 KB. Multiplicar por 4 los factores cuadruplica la memoria
y aumenta un 18 % el tiempo sin mejorar el ranking, por lo que, desde la perspectiva Green AI, no
justifico el modelo más grande. El costo menor de todos es el del baseline de popularidad, que no
requiere entrenamiento y obtiene el mejor HitRate, aunque no personaliza.

**Riesgo principal y mitigación:**
*Riesgo*: considero que el riesgo principal es la popularidad dominante, que lleva a una burbuja de
filtro. La métrica de acierto premia recomendar lo popular: el baseline no personalizado gana en
HitRate y la configuración con más aciertos es la que menos catálogo muestra. Si el sistema se
desplegara optimizando solo HitRate, concentraría la exposición en pocas películas y, por
retroalimentación, esas películas acumularían aún más interacciones en el siguiente entrenamiento.
*Mitigación*: propongo evaluar siempre con dos métricas (HitRate y cobertura) y elegir
configuraciones en la frontera de Pareto entre ambas; limitar la cantidad de títulos muy populares en
el Top-10 o reservar posiciones para exploración; dar más peso al contenido o a la popularidad cuando
el usuario tiene poco historial, en lugar de una señal colaborativa inestable; y, en un despliegue,
registrar lo recomendado y monitorear la concentración del catálogo en el tiempo. Además, no extiendo
ninguna conclusión a grupos poblacionales, porque el dataset no tiene datos demográficos.
