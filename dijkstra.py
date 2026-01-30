"""
dijkstra.py
Modified Dijkstra's algorithm: shortest path with airline-aware edge pruning.
Uses a min-heap (priority queue) for greedy expansion.
"""

import heapq
from typing import Dict, List, Optional, Tuple

from airline_rules import get_hub
from graph_builder import Edge


# Result: (total_km, path_as_city_names, segments as (from_city, to_city, airline))
PathResult = Tuple[float, List[str], List[Tuple[str, str, Optional[str]]]]


def dijkstra_airline_aware(
    adjacency_list: List[List[Edge]],
    city_to_index: Dict[str, int],
    index_to_city: Dict[int, str],
    source: str,
    dest: str,
    airlines: List[str],
) -> Optional[PathResult]:
    """
    Run Dijkstra on the airline-pruned graph from source to dest.
    Edges are only those added by graph_builder (hub <-> city for selected airlines).
    Uses a min-heap to always expand the shortest valid path first (greedy).

    Returns:
        (total_distance_km, [city0, city1, ...], [(from, to, airline), ...])
        or None if no feasible route.
    """
    if source not in city_to_index or dest not in city_to_index:
        return None
    src = city_to_index[source]
    dst = city_to_index[dest]
    n = len(adjacency_list)

    # dist[i] = shortest distance from source to node i
    dist: List[float] = [float("inf")] * n
    dist[src] = 0.0

    # prev[i] = (predecessor_index, airline_on_edge_from_pred_to_i)
    prev: List[Optional[Tuple[int, Optional[str]]]] = [None] * n

    # Min-heap: (distance, node_index). Ties broken by insertion order.
    heap: List[Tuple[float, int]] = [(0.0, src)]
    heapq.heapify(heap)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == dst:
            break
        for v, w, airline in adjacency_list[u]:
            new_d = d + w
            if new_d < dist[v]:
                dist[v] = new_d
                prev[v] = (u, airline)
                heapq.heappush(heap, (new_d, v))

    if dist[dst] == float("inf"):
        return None

    path_indices: List[int] = []
    cur = dst
    while cur is not None:
        path_indices.append(cur)
        pr = prev[cur]
        if pr is None:
            break
        cur = pr[0]
    path_indices.reverse()

    path_cities = [index_to_city[i] for i in path_indices]
    segments: List[Tuple[str, str, Optional[str]]] = []
    for k in range(len(path_indices) - 1):
        u, v = path_indices[k], path_indices[k + 1]
        _, airline = prev[v]
        segments.append((index_to_city[u], index_to_city[v], airline))

    return (dist[dst], path_cities, segments)


def dijkstra_standard(
    adjacency_list: List[List[Edge]],
    city_to_index: Dict[str, int],
    index_to_city: Dict[int, str],
    source: str,
    dest: str,
) -> Optional[Tuple[float, List[str]]]:
    """
    Standard Dijkstra ignoring airlines (uses same graph;
    assumes graph has been built with all airlines so any edge is valid).
    Returns (total_km, path_cities) or None.
    """
    if source not in city_to_index or dest not in city_to_index:
        return None
    src = city_to_index[source]
    dst = city_to_index[dest]
    n = len(adjacency_list)

    dist = [float("inf")] * n
    dist[src] = 0.0
    prev: List[Optional[int]] = [None] * n
    heap: List[Tuple[float, int]] = [(0.0, src)]
    heapq.heapify(heap)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == dst:
            break
        for v, w, _ in adjacency_list[u]:
            new_d = d + w
            if new_d < dist[v]:
                dist[v] = new_d
                prev[v] = u
                heapq.heappush(heap, (new_d, v))

    if dist[dst] == float("inf"):
        return None

    path_indices = []
    cur = dst
    while cur is not None:
        path_indices.append(cur)
        cur = prev[cur]
    path_indices.reverse()
    path_cities = [index_to_city[i] for i in path_indices]
    return (dist[dst], path_cities)
