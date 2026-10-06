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

## Laboratorios
```bash
uv run python scripts/lab08_content.py
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75
uv run streamlit run app/streamlit_app.py
```

## Interpretación
No presente una recomendación como verdad. Documente datos, candidatos, puntuación, métricas, fallback y límites.
