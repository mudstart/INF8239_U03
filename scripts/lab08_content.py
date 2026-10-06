import pandas as pd

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.recommenders import ContentRecommender, weighted_popularity

# Tres consultas de géneros distintos: animación infantil, drama criminal y terror.
QUERIES = ["Toy Story (1995)", "Shawshank Redemption, The (1994)", "Shining, The (1980)"]

ratings, movies = load_movielens(MOVIELENS_DIR)
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
popular = weighted_popularity(ratings, movies).head(10)
popular[["title", "count", "mean", "weighted_score"]].to_csv(reports / "popular_top10.csv")
print("Popularidad:\n", popular[["title", "count", "mean", "weighted_score"]])

model = ContentRecommender().fit(movies)
results = []
for title in QUERIES:
    genres = movies.loc[movies["title"].eq(title), "genres"].iloc[0]
    recommendations = model.recommend(title, 10)
    recommendations.insert(0, "rank", range(1, len(recommendations) + 1))
    recommendations.insert(0, "query", title)
    results.append(recommendations)
    print(f"\nSimilares a {title} [{genres}]:\n", recommendations.drop(columns="query"))
pd.concat(results).to_csv(reports / "content_recommendations.csv", index=False)
