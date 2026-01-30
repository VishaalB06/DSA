"""
main.py
User input, orchestration, and execution for the airline-aware shortest flight path system.
"""

from pathlib import Path
from typing import List, Optional

from airline_rules import SUPPORTED_AIRLINES
from data_loader import load_airport_data
from dijkstra import dijkstra_airline_aware, dijkstra_standard
from graph_builder import build_graph


def _normalize_city(s: str) -> str:
    return s.strip()


def _select_airlines() -> List[str]:
    """Prompt user to select one or more airlines. Returns list of names."""
    print("\nSelect airline(s). Enter numbers separated by commas (e.g. 1,2):")
    options = list(SUPPORTED_AIRLINES)
    for i, name in enumerate(options, 1):
        print(f"  {i}) {name}")
    while True:
        raw = input("Your choice: ").strip()
        indices = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                idx = int(part)
                if 1 <= idx <= len(options):
                    indices.append(idx - 1)
            except ValueError:
                pass
        if indices:
            return [options[i] for i in sorted(set(indices))]
        print("Invalid input. Try e.g. 1 or 1,2 or 1,2,3.")


def _pick_city(prompt: str, cities: List[str]) -> str:
    """Let user type a city name; match against available cities."""
    while True:
        name = _normalize_city(input(prompt))
        if not name:
            continue
        matches = [c for c in cities if c.lower() == name.lower()]
        if len(matches) == 1:
            return matches[0]
        if matches:
            return matches[0]
        prefix = [c for c in cities if c.lower().startswith(name.lower())]
        if len(prefix) == 1:
            return prefix[0]
        if prefix:
            print(f"  Possible matches: {', '.join(prefix[:8])}{'...' if len(prefix) > 8 else ''}")
        else:
            print(f"  City not found. Ensure it's in the dataset (e.g. London, Mumbai, Doha).")


def run(
    source: Optional[str] = None,
    dest: Optional[str] = None,
    airlines: Optional[List[str]] = None,
    data_path: Optional[Path] = None,
    skip_viz: bool = False,
    compare_standard: bool = True,
) -> None:
    """
    Load data, build graph, run airline-aware Dijkstra, print results, and optionally visualize.

    If source, dest, or airlines are None, prompt interactively.
    """
    df = load_airport_data(data_path)
    cities = df["City"].tolist()

    if source is None:
        source = _pick_city("Source city: ", cities)
    else:
        source = _normalize_city(source)
        if source not in cities:
            print(f"Source city '{source}' not in dataset.")
            return

    if dest is None:
        dest = _pick_city("Destination city: ", cities)
    else:
        dest = _normalize_city(dest)
        if dest not in cities:
            print(f"Destination city '{dest}' not in dataset.")
            return

    if airlines is None:
        airlines = _select_airlines()
    else:
        invalid = [a for a in airlines if a not in SUPPORTED_AIRLINES]
        if invalid:
            print(f"Unsupported airline(s): {invalid}. Use: {list(SUPPORTED_AIRLINES)}")
            return

    # Build airline-aware graph and run modified Dijkstra
    adj, city_to_idx, idx_to_city, _ = build_graph(df, airlines)
    result = dijkstra_airline_aware(adj, city_to_idx, idx_to_city, source, dest, airlines)

    print("\n" + "=" * 60)
    print("SELECTED AIRLINE(S):", ", ".join(airlines))
    print("=" * 60)

    if result is None:
        print("No feasible route with selected airlines.")
        if not skip_viz:
            print("Skipping visualization.")
        return

    total_km, path_cities, segments = result
    print("PATH:", " -> ".join(path_cities))
    print("TOTAL DISTANCE (km):", round(total_km, 2))
    print("\nLegs:")
    for from_c, to_c, air in segments:
        air_str = air or "(transfer)"
        print(f"  {from_c} -> {to_c}  [{air_str}]")

    # Optional: compare with standard Dijkstra (all airlines)
    if compare_standard and set(airlines) != SUPPORTED_AIRLINES:
        adj_full, c2i, i2c, _ = build_graph(df, list(SUPPORTED_AIRLINES))
        std = dijkstra_standard(adj_full, c2i, i2c, source, dest)
        if std is not None:
            std_km, std_path = std
            print("\n--- Comparison (standard Dijkstra, all airlines) ---")
            print("Path:", " -> ".join(std_path))
            print("Total distance (km):", round(std_km, 2))
            diff = round(std_km - total_km, 2)
            if diff < 0:
                print("Standard (all airlines) is", abs(diff), "km shorter.")
            elif diff > 0:
                print("Airline-aware is", diff, "km shorter (restricting airlines).")
            else:
                print("Same distance.")

    if not skip_viz:
        try:
            from visualization import plot_and_animate
            plot_and_animate(df, path_cities, segments, airlines)
        except ImportError as e:
            print("Visualization skipped (install matplotlib, numpy; optional: cartopy):", e)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Airline-aware shortest flight path")
    ap.add_argument("--source", "-s", type=str, help="Source city")
    ap.add_argument("--dest", "-d", type=str, help="Destination city")
    ap.add_argument("--airlines", "-a", type=str, help='Airlines, comma-separated (e.g. "Qatar Airways,Emirates")')
    ap.add_argument("--no-viz", action="store_true", help="Skip map visualization")
    ap.add_argument("--no-compare", action="store_true", help="Skip standard Dijkstra comparison")
    ap.add_argument("--data", type=Path, help="Path to airport Excel/CSV")
    args = ap.parse_args()

    airlines_list = None
    if args.airlines:
        airlines_list = [a.strip() for a in args.airlines.split(",") if a.strip()]
        valid = [a for a in airlines_list if a in SUPPORTED_AIRLINES]
        if len(valid) != len(airlines_list):
            print("Unknown airline(s) in --airlines. Use: Qatar Airways, Emirates, Etihad")
            raise SystemExit(1)
        airlines_list = valid

    run(
        source=args.source or None,
        dest=args.dest or None,
        airlines=airlines_list,
        data_path=args.data,
        skip_viz=args.no_viz,
        compare_standard=not args.no_compare,
    )
