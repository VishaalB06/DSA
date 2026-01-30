"""
graph_builder.py
Build adjacency-list graph from airport data with airline-aware edges.
"""

from typing import Dict, List, Optional, Tuple

import pandas as pd

from airline_rules import airline_serves_city, get_hub, SUPPORTED_AIRLINES


# Edge: (neighbor_index, weight_km, airline_or_None)
Edge = Tuple[int, float, Optional[str]]


def build_graph(
    df: pd.DataFrame,
    airlines: List[str],
) -> Tuple[List[List[Edge]], Dict[str, int], Dict[int, str], pd.DataFrame]:
    """
    Build an adjacency-list graph where edges exist only if a selected
    airline operates that route (hub <-> city or hub <-> hub when multi-airline).

    Returns:
        - adjacency_list: adj[i] = [(j, weight_km, airline), ...]
        - city_to_index: map city name -> node index
        - index_to_city: map node index -> city name
        - df: same DataFrame (for lat/lon lookup)
    """
    for a in airlines:
        if a not in SUPPORTED_AIRLINES:
            raise ValueError(f"Unsupported airline: {a}. Use: {list(SUPPORTED_AIRLINES)}")

    cities = df["City"].tolist()
    city_to_index: Dict[str, int] = {c: i for i, c in enumerate(cities)}
    index_to_city: Dict[int, str] = {i: c for i, c in enumerate(cities)}
    n = len(cities)

    # Distance lookup: (city A, city B) -> km
    def dist(a: str, b: str) -> float:
        if a == b:
            return 0.0
        row_a = df[df["City"] == a].iloc[0]
        row_b = df[df["City"] == b].iloc[0]
        if a == "Doha":
            return float(row_b["Distance to Doha"])
        if a == "Dubai":
            return float(row_b["Distance to Dubai"])
        if a == "Abu Dhabi":
            return float(row_b["Distance to Abu Dhabi"])
        if b == "Doha":
            return float(row_a["Distance to Doha"])
        if b == "Dubai":
            return float(row_a["Distance to Dubai"])
        if b == "Abu Dhabi":
            return float(row_a["Distance to Abu Dhabi"])
        # Non-hub to non-hub: no direct edge in our model
        return float("inf")

    adjacency_list: List[List[Edge]] = [[] for _ in range(n)]

    for airline in airlines:
        hub = get_hub(airline)
        if hub not in city_to_index:
            continue
        hi = city_to_index[hub]
        for c in cities:
            if c == hub:
                continue
            if not airline_serves_city(airline, c):
                continue
            ci = city_to_index[c]
            d = dist(hub, c)
            if d == float("inf"):
                continue
            adjacency_list[hi].append((ci, d, airline))
            adjacency_list[ci].append((hi, d, airline))

    # Hub-to-hub routes come from per-airline hub <-> city (other hubs are cities).
    return adjacency_list, city_to_index, index_to_city, df
