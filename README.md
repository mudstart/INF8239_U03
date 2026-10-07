# INF-8239 · Unidad 03 · Sistemas recomendadores

Autor académico (proyecto base): Edwin Ramón José Nolasco
Estudiante: Jose Miguel Maduro Valenzuela

Proyecto inicial de LAB08 y LAB09. El dataset de muestra prueba el código; la evidencia final usa MovieLens.

## Dataset y licencia

Este proyecto usa **MovieLens Latest Small** (`ml-latest-small`), publicado por
[GroupLens Research](https://grouplens.org/datasets/movielens/), University of Minnesota.

- Fuente: https://files.grouplens.org/datasets/movielens/ml-latest-small.zip
- Fecha de descarga: 2026-10-06
- Versión: generada por GroupLens el 2018-09-26
- SHA-256 del ZIP: `696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436`
- Contenido: 100 836 ratings y 3 683 tags de 610 usuarios sobre 9 742 películas (1996-03-29 a 2018-09-24)

El dataset no se incluye en este repositorio; se descarga con `scripts/download_data.py`
para garantizar reproducibilidad y verificar el hash.
Su uso está sujeto a la licencia oficial de GroupLens: uso para investigación, citando a
Harper y Konstan (2015); sin fines comerciales sin permiso de GroupLens; sin implicar
respaldo de la University of Minnesota ni de GroupLens; y cualquier redistribución debe
mantener estas mismas condiciones. Los datos se ofrecen sin garantía.
`ml-latest-small` es una versión de desarrollo que puede cambiar, por lo que los resultados
dependen del hash registrado.

### Cita

Harper, F. M., & Konstan, J. A. (2015). The MovieLens datasets: History and context.
*ACM Transactions on Interactive Intelligent Systems, 5*(4), Article 19.
https://doi.org/10.1145/2827872

## Inicio
```bash
uv python install 3.12
uv sync
uv run pytest -q
uv run python scripts/download_data.py
uv run python scripts/audit_data.py
```

## LAB08 · Popularidad y contenido
```bash
uv run python scripts/lab08_content.py
uv run streamlit run app/streamlit_app.py
```
`lab08_content.py` genera el Top-10 de popularidad y tres consultas por contenido en `reports/`.

## LAB09 · Colaborativo e híbrido
En Windows (Git Bash) anteponga `PYTHONIOENCODING=utf-8` a los comandos `uv run python`.

```bash
# Experimento base
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75 --seed 42

# Comparación de alpha (mismos factores, épocas y semilla)
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25 --seed 42

# Tres semillas por configuración
for f in 10 20 40; do for s in 42 7 123; do uv run python scripts/lab09_hybrid.py --factors $f --epochs 12 --alpha 0.75 --seed $s; done; done
for s in 42 7 123; do uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25 --seed $s; done

# Tabla de Pareto y comparación de modelos
uv run python scripts/lab09_pareto.py
```

| Parámetro | Significado |
|---|---|
| `--factors` | Número de factores latentes de la factorización |
| `--epochs` | Pasadas de entrenamiento |
| `--alpha` | Peso de la señal colaborativa en el híbrido (el resto es contenido) |
| `--seed` | Semilla de inicialización del modelo |

Cada corrida (~30 s) guarda en `reports/lab09/`:
- `metrics_f{factores}_e{épocas}_a{alpha}_s{semilla}.json`: RMSE, tiempo, tamaño del modelo y
  HitRate@10, Precision@10 y cobertura de popularidad, contenido, colaborativo e híbrido.
- `profiles_*.csv`: Top-10 de un usuario con historial amplio, uno con historial pequeño y un
  usuario nuevo (fallback no personalizado).

`lab09_pareto.py` genera `pareto.csv` y `model_comparison.csv`. Además, `reports/hybrid_metrics.json`
y `reports/cold_start_fallback.csv` se sobrescriben con la última corrida.

Configuración seleccionada: 10 factores, 12 épocas, alpha 0.75. Análisis en
`reports/lab09/analisis_factorizacion.md` y `reports/lab09/analisis_hibrido.md`.

## Ejercicio 05 · Notebook ejecutado
`notebooks/recomendador_e05.ipynb` consolida LAB08 y LAB09 usando el código de `src/`: auditoría,
popularidad, contenido, factorización con corte temporal, comparación de modelos, Pareto y perfiles.
Reproduce la configuración seleccionada y verifica que coincide con las métricas del script.
Requiere los datos descargados y las corridas de `reports/lab09/`.

## Dependencias
`uv.lock` fija las versiones. `requirements.txt` se genera con
`uv export --format requirements.txt --output-file requirements.txt` para entornos sin uv.

## Pruebas
```bash
uv run pytest -q
```

## Interpretación
No presente una recomendación como verdad. Documente datos, candidatos, puntuación, métricas, fallback y límites.
