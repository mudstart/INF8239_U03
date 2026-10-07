"""Resume las corridas de reports/lab09 y marca configuraciones dominadas (Pareto)."""
from __future__ import annotations

import json

import pandas as pd

from inf8239_u03.config import ROOT

run_dir = ROOT / "reports/lab09"
rows = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(run_dir.glob("metrics_*.json"))]
if not rows:
    raise SystemExit("No hay corridas en reports/lab09; ejecute primero scripts/lab09_hybrid.py")
runs = pd.DataFrame(rows)
runs["hit_rate_at_10"] = runs["models"].map(lambda models: models["hybrid"]["hit_rate_at_10"])
summary = (
    runs.groupby(["factors", "epochs", "alpha"])
    .agg(
        seeds=("seed", "nunique"),
        rmse_mean=("rmse", "mean"),
        rmse_std=("rmse", "std"),
        hit_rate_mean=("hit_rate_at_10", "mean"),
        hit_rate_std=("hit_rate_at_10", "std"),
        coverage_mean=("catalog_coverage", "mean"),
        train_seconds_mean=("train_seconds", "mean"),
        model_kb=("model_kb", "mean"),
    )
    .reset_index()
)


# Dominada: otra configuración tiene igual o mejor utilidad con igual o menor costo, y es estrictamente mejor en algo.
def dominated_by(index: int) -> str:
    row = summary.loc[index]
    for other_index, other in summary.iterrows():
        if other_index == index:
            continue
        no_worse = (
            other.hit_rate_mean >= row.hit_rate_mean
            and other.train_seconds_mean <= row.train_seconds_mean
            and other.model_kb <= row.model_kb
        )
        better = (
            other.hit_rate_mean > row.hit_rate_mean
            or other.train_seconds_mean < row.train_seconds_mean
            or other.model_kb < row.model_kb
        )
        if no_worse and better:
            return f"f{int(other.factors)}_e{int(other.epochs)}_a{other.alpha:.2f}"
    return ""


summary["dominated_by"] = [dominated_by(index) for index in summary.index]
summary["pareto_optimal"] = summary["dominated_by"].eq("")
summary.to_csv(run_dir / "pareto.csv", index=False)

models = pd.DataFrame(
    [
        {"model": name, "factors": run["factors"], "alpha": run["alpha"], "seed": run["seed"], **values}
        for run in rows
        for name, values in run["models"].items()
    ]
)
comparison = models.groupby(["model", "factors", "alpha"])[["hit_rate_at_10", "precision_at_10", "catalog_coverage"]].mean().reset_index()
comparison.to_csv(run_dir / "model_comparison.csv", index=False)

pd.set_option("display.width", None, "display.max_columns", None)
print("Tabla de Pareto (utilidad = HitRate@10 del híbrido; costo = segundos de entrenamiento y KB):\n")
print(summary.round(4).to_string(index=False))
print("\nComparación de modelos (promedio entre semillas):\n")
print(comparison.round(4).to_string(index=False))
print("\nGuardado en reports/lab09/pareto.csv y reports/lab09/model_comparison.csv")
