"""
web_map.py
Helper module for building interactive Folium maps with airline-aware routes.
"""

from typing import List, Optional, Tuple

import folium
import pandas as pd

from airline_rules import AIRLINE_COLORS, get_hubs_for_airlines


def _coords(df: pd.DataFrame, city: str) -> Tuple[float, float]:
    """
    Return (latitude, longitude) for a city from the airport DataFrame.
    
    Args:
        df: DataFrame with City, Latitude, Longitude columns
        city: City name to lookup
        
    Returns:
        Tuple of (lat, lon)
    """
    row = df[df["City"] == city]
    if row.empty:
        raise ValueError(f"City not found in DataFrame: {city}")
    return float(row.iloc[0]["Latitude"]), float(row.iloc[0]["Longitude"])


def build_map_html(
    df: pd.DataFrame,
    path_cities: List[str],
    segments: List[Tuple[str, str, Optional[str]]],
    airlines: List[str],
) -> str:
    """
    Build an interactive Folium map showing the route with airline-colored segments.
    
    Args:
        df: Airport data with coordinates
        path_cities: List of cities in the route (e.g., ["London", "Doha", "Dubai"])
        segments: List of (from_city, to_city, airline) tuples
        airlines: List of selected airlines (for hub identification)
        
    Returns:
        HTML string representation of the map for embedding in templates
    """
    if not path_cities:
        return ""

    # Get hub cities for color coding
    hubs = get_hubs_for_airlines(airlines)

    # Calculate center of map (average of all cities)
    coords = [_coords(df, city) for city in path_cities]
    avg_lat = sum(c[0] for c in coords) / len(coords)
    avg_lon = sum(c[1] for c in coords) / len(coords)

    # Create base map
    m = folium.Map(
        location=(avg_lat, avg_lon),
        zoom_start=4,
        tiles="OpenStreetMap"
    )

    # Add polylines for each segment (colored by airline)
    for from_city, to_city, airline in segments:
        from_coords = _coords(df, from_city)
        to_coords = _coords(df, to_city)

        # Get color for airline (default to gray if transfer or unknown)
        color = AIRLINE_COLORS.get(airline, "#808080") if airline else "#808080"

        # Create line with airline color
        folium.PolyLine(
            locations=[from_coords, to_coords],
            color=color,
            weight=3,
            opacity=0.8,
            popup=f"{from_city} → {to_city} ({airline or 'Transfer'})"
        ).add_to(m)

    # Track cities already marked (prevent duplicates)
    marked_cities = set()

    # Add circle markers for each city
    for city in path_cities:
        if city in marked_cities:
            continue
        marked_cities.add(city)

        lat, lon = _coords(df, city)

        # Color: gold for hubs, green for non-hubs
        is_hub = city in hubs
        color = "gold" if is_hub else "green"

        folium.CircleMarker(
            location=(lat, lon),
            radius=8,
            popup=f"<b>{city}</b><br/>{'(Hub)' if is_hub else '(City)'}",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(m)

    # Return HTML representation for embedding
    return m._repr_html_()
