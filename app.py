"""
app.py
Flask web application for airline-aware shortest flight path system.
Mirrors main.run() logic but uses HTML forms instead of CLI.
"""

from flask import Flask, render_template, request

from data_loader import load_airport_data
from graph_builder import build_graph
from dijkstra import dijkstra_airline_aware, dijkstra_standard
from airline_rules import SUPPORTED_AIRLINES
from web_map import build_map_html

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    GET: Render form with city and airline options.
    POST: Process form, compute route, and display results.
    """
    # Load airport data once per request
    df = load_airport_data()
    cities = sorted(df["City"].tolist())
    airlines = list(SUPPORTED_AIRLINES)

    if request.method == "GET":
        # Render empty form
        return render_template(
            "index.html",
            cities=cities,
            airlines=airlines,
        )

    # -------- POST: handle form submission --------
    source = request.form.get("source", "").strip()
    destination = request.form.get("destination", "").strip()
    selected_airlines = request.form.getlist("airlines")

    # Validate input
    error = None
    if not source or not destination:
        error = "Source and destination are required."
    elif source == destination:
        error = "Source and destination must be different."
    elif not selected_airlines:
        error = "Select at least one airline."
    elif source not in cities:
        error = f"Source city '{source}' not found in dataset."
    elif destination not in cities:
        error = f"Destination city '{destination}' not found in dataset."

    if error:
        return render_template(
            "index.html",
            cities=cities,
            airlines=airlines,
            error=error,
            source=source,
            destination=destination,
            selected_airlines=selected_airlines,
        )

    # -------- Build graph and run airline-aware Dijkstra --------
    # Mirror main.run() control flow exactly
    adj, city_to_idx, idx_to_city, _ = build_graph(df, selected_airlines)

    result = dijkstra_airline_aware(
        adjacency_list=adj,
        city_to_index=city_to_idx,
        index_to_city=idx_to_city,
        source=source,
        dest=destination,
        airlines=selected_airlines,
    )

    if result is None:
        # No feasible route found
        return render_template(
            "result.html",
            no_path=True,
            source=source,
            destination=destination,
            airlines=" → ".join(selected_airlines),
        )

    # Unpack result: (total_km, path_cities, segments)
    total_km, path_cities, segments = result

    # Optional: compare with standard Dijkstra (all airlines)
    comparison = None
    if set(selected_airlines) != SUPPORTED_AIRLINES:
        adj_full, c2i, i2c, _ = build_graph(df, list(SUPPORTED_AIRLINES))
        std_result = dijkstra_standard(
            adjacency_list=adj_full,
            city_to_index=c2i,
            index_to_city=i2c,
            source=source,
            dest=destination,
        )
        if std_result is not None:
            std_km, std_path = std_result
            comparison = {
                "std_km": round(std_km, 2),
                "std_path": std_path,
                "difference": round(std_km - total_km, 2),
            }

    # Build Folium map
    map_html = build_map_html(
        df=df,
        path_cities=path_cities,
        segments=segments,
        airlines=selected_airlines,
    )

    return render_template(
        "result.html",
        no_path=False,
        source=source,
        destination=destination,
        airlines=selected_airlines,
        path=path_cities,
        total_km=round(total_km, 2),
        segments=segments,
        comparison=comparison,
        map_html=map_html,
    )


if __name__ == "__main__":
    app.run(debug=True)
