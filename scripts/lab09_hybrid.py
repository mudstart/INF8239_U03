from __future__ import annotations

import argparse
import json
from time import perf_counter

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.metrics import catalog_coverage, hit_rate_at_k
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

parser = argparse.ArgumentParser()
parser.add_argument("--factors", type=int, default=20)
parser.add_argument("--epochs", type=int, default=12)
parser.add_argument("--alpha", type=float, default=0.75)
parser.add_argument("--seed", type=int, default=42)
args = parser.parse_args()
run_name = f"f{args.factors}_e{args.epochs}_a{args.alpha:.2f}_s{args.seed}"
run_dir = ROOT / "reports/lab09"
run_dir.mkdir(parents=True, exist_ok=True)

run_start = perf_counter()
ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
start = perf_counter()
model = MatrixFactorization(factors=args.factors, seed=args.seed).fit(train, epochs=args.epochs)
train_seconds = perf_counter() - start
model_kb = (model.user_factors.nbytes + model.item_factors.nbytes) / 1024
evaluable = test[test["userId"].isin(model.user_index) & test["movieId"].isin(model.item_index)]
predictions = [model.predict(row.userId, row.movieId) for row in evaluable.itertuples()]
rmse = root_mean_squared_error(evaluable["rating"], predictions)
popular = train.groupby("movieId")["rating"].agg(["mean", "count"]).sort_values(["count", "mean"], ascending=False)
popular_items = popular.index.tolist()
movie_table = movies.reset_index(drop=True).copy()
movie_table["genres_text"] = movie_table["genres"].str.replace("|", " ", regex=False)
genre_matrix = TfidfVectorizer().fit_transform(movie_table["genres_text"])
movie_row = {int(movie_id): index for index, movie_id in enumerate(movie_table["movieId"])}
row_movie = movie_table["movieId"].to_numpy()

# Los cuatro modelos se evalúan sobre los mismos usuarios, el mismo corte y excluyendo lo ya visto.
recommendations = {"popularity": {}, "content": {}, "collaborative": {}, "hybrid": {}}
details = {}
for user_id in evaluable["userId"].unique():
    seen = set(train.loc[train["userId"].eq(user_id), "movieId"])
    recommendations["popularity"][int(user_id)] = [item for item in popular_items if item not in seen][:10]
    collaborative = model.top_n(user_id, seen, 100)
    recommendations["collaborative"][int(user_id)] = collaborative["movieId"].head(10).astype(int).tolist()
    collaborative["normalized"] = (collaborative["collaborative_score"] - collaborative["collaborative_score"].min()) / max(collaborative["collaborative_score"].max() - collaborative["collaborative_score"].min(), 1e-9)
    history = train.loc[train["userId"].eq(user_id) & train["movieId"].isin(movie_row), ["movieId", "rating"]]
    history_rows = [movie_row[int(item)] for item in history["movieId"]]
    weights = np.clip(history["rating"].to_numpy() - 2.5, 0.1, None)
    profile = np.asarray(genre_matrix[history_rows].multiply(weights[:, None]).sum(axis=0)) / weights.sum()
    all_content = cosine_similarity(profile, genre_matrix).ravel()
    all_content[[movie_row[int(item)] for item in seen if int(item) in movie_row]] = -1
    recommendations["content"][int(user_id)] = row_movie[np.argsort(-all_content, kind="stable")[:10]].astype(int).tolist()
    candidate_rows = [movie_row[int(item)] for item in collaborative["movieId"]]
    content_scores = cosine_similarity(profile, genre_matrix[candidate_rows]).ravel()
    content_min, content_max = content_scores.min(), content_scores.max()
    collaborative["content_score"] = (content_scores - content_min) / max(content_max - content_min, 1e-9)
    collaborative["hybrid_score"] = args.alpha * collaborative["normalized"] + (1 - args.alpha) * collaborative["content_score"]
    top = collaborative.nlargest(10, "hybrid_score")
    recommendations["hybrid"][int(user_id)] = top["movieId"].astype(int).tolist()
    details[int(user_id)] = (top, len(seen))

comparison = {
    name: {
        "hit_rate_at_10": hit_rate_at_k(recs, evaluable, 10),
        "precision_at_10": hit_rate_at_k(recs, evaluable, 10) / 10,
        "catalog_coverage": catalog_coverage(recs, len(model.items)),
    }
    for name, recs in recommendations.items()
}
metrics = {
    "rmse": float(rmse),
    "hit_rate_at_10": comparison["hybrid"]["hit_rate_at_10"],
    "catalog_coverage": comparison["hybrid"]["catalog_coverage"],
    "train_seconds": train_seconds,
    "total_seconds": perf_counter() - run_start,
    "model_kb": model_kb,
    "parameters": int(model.user_factors.size + model.item_factors.size),
    "factors": args.factors,
    "epochs": args.epochs,
    "alpha": args.alpha,
    "seed": args.seed,
    "evaluated_users": int(evaluable["userId"].nunique()),
    "models": comparison,
    "cold_start_policy": "popularidad por cantidad y media; no personalizada",
}

# Perfiles: el usuario con más y con menos historial, y un usuario nuevo que recibe el fallback.
history_size = {user: size for user, (_, size) in details.items()}
heldout = dict(zip(evaluable["userId"].astype(int), evaluable["movieId"].astype(int)))
profiles = []
for label, user_id in [("historial_amplio", max(history_size, key=history_size.get)), ("historial_pequeno", min(history_size, key=history_size.get))]:
    top, size = details[user_id]
    seen = set(train.loc[train["userId"].eq(user_id), "movieId"])
    frame = top.merge(movies, on="movieId")[["movieId", "title", "genres", "normalized", "content_score", "hybrid_score"]]
    frame.insert(0, "rank", range(1, len(frame) + 1))
    frame.insert(0, "history_size", size)
    frame.insert(0, "userId", user_id)
    frame.insert(0, "profile", label)
    frame["already_seen"] = frame["movieId"].isin(seen)
    frame["is_heldout_item"] = frame["movieId"].eq(heldout[user_id])
    frame["personalized"] = True
    profiles.append(frame)
cold_start_items = popular_items[:10]
fallback = movies.set_index("movieId").loc[cold_start_items].reset_index()
cold = fallback[["movieId", "title", "genres"]].copy()
cold.insert(0, "rank", range(1, len(cold) + 1))
cold.insert(0, "history_size", 0)
cold.insert(0, "userId", "nuevo")
cold.insert(0, "profile", "usuario_nuevo")
cold["personalized"] = False
profiles.append(cold)
pd.concat(profiles).to_csv(run_dir / f"profiles_{run_name}.csv", index=False)

(run_dir / f"metrics_{run_name}.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
(ROOT / "reports/hybrid_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
fallback.to_csv(ROOT / "reports/cold_start_fallback.csv", index=False)
print(json.dumps(metrics, indent=2))
print(f"\nGuardado en reports/lab09/metrics_{run_name}.json y profiles_{run_name}.csv")
