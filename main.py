import os
import pickle
import math
import numpy as np
import pandas as pd
import difflib
from sklearn.metrics.pairwise import cosine_similarity

# =========================================================
# LOAD
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

df           = pickle.load(open(os.path.join(DATA_DIR, "df.pkl"), "rb"))
indices      = pickle.load(open(os.path.join(DATA_DIR, "indices.pkl"), "rb"))
tfidf_matrix = pickle.load(open(os.path.join(DATA_DIR, "tfidf_matrix.pkl"), "rb"))

# embeddings optional (safe loading)
emb_path = os.path.join(DATA_DIR, "embeddings.pkl")
if os.path.exists(emb_path):
    embeddings = pickle.load(open(emb_path, "rb"))
else:
    embeddings = None

has_embeddings = embeddings is not None and embeddings.ndim == 2 and embeddings.shape[1] > 1

# feature flags
has_cast     = "cast_clean" in df.columns
has_keywords = "keywords_clean" in df.columns

# =========================================================
# UTIL
# =========================================================

def safe(v, default="N/A"):
    try:
        if pd.isna(v):
            return default
    except:
        pass
    return v if v not in ("", None) else default


def get_genres(row):
    return row.get("genres_clean", "N/A").title() or "N/A"


def get_poster(row):
    p = str(row.get("poster_path", "") or "")
    return f"https://image.tmdb.org/t/p/w500{p}" if p else None


# =========================================================
# TITLE MATCHING
# =========================================================

def find_title(name: str):
    name = name.lower().strip()

    if name in indices.index:
        return name

    partials = [t for t in indices.index if name in t]
    if partials:
        return min(partials, key=len)

    matches = difflib.get_close_matches(name, indices.index, n=3, cutoff=0.65)
    return matches[0] if matches else None


# =========================================================
# POPULARITY
# =========================================================

_MAX_LOG_POP = math.log1p(float(df["popularity"].max()))


def pop_score(pop):
    try:
        return math.log1p(float(pop)) / _MAX_LOG_POP if _MAX_LOG_POP else 0
    except:
        return 0


# =========================================================
# RECOMMENDATION ENGINE
# =========================================================

def recommend(movie_name: str, n: int = 10):
    if not movie_name.strip():
        return []

    title = find_title(movie_name)
    if not title:
        return []

    idx = indices[title]

    # TF-IDF similarity
    tfidf_sim = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()

    # Hybrid embedding similarity
    if has_embeddings:
        emb_sim = cosine_similarity(
            embeddings[idx].reshape(1, -1),
            embeddings
        ).flatten()
        sim = 0.6 * tfidf_sim + 0.4 * emb_sim
    else:
        sim = tfidf_sim

    base_row = df.iloc[idx]

    results = []

    for i in np.argsort(sim)[::-1]:

        if i == idx:
            continue

        row = df.iloc[i]

        if len(str(row.get("overview", ""))) < 30:
            continue

        rating = float(row.get("vote_average", 0) or 0)

        quality = 0.5 * (rating / 10) + 0.5 * pop_score(row.get("popularity", 0))

        final_score = 0.90 * sim[i] + 0.10 * quality

        results.append({
            "title": safe(row.get("title")),
            "overview": safe(row.get("overview")),
            "poster": get_poster(row),
            "rating": round(rating, 1),
            "year": str(row.get("release_date", ""))[:4] or "N/A",
            "popularity": safe(row.get("popularity")),
            "genres": get_genres(row),
            "similarity": round(float(sim[i]), 3),
            "score": round(float(final_score), 3),
        })

        if len(results) == n:
            break

    return results