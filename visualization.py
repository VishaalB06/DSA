"""
visualization.py
Plot flight path on a real-world map and animate aircraft movement.
"""

from typing import Dict, List, Optional, Tuple

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from airline_rules import AIRLINE_COLORS, get_hubs_for_airlines

# Try cartopy for real-world map; fall back to plain lat/lon if unavailable
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_CARTOPY = True
except ImportError:
    HAS_CARTOPY = False


def _get_coords(df: pd.DataFrame, city: str) -> Tuple[float, float]:
    """Return (lat, lon) for city."""
    row = df[df["City"] == city]
    if row.empty:
        return (0.0, 0.0)
    return (float(row["Latitude"].iloc[0]), float(row["Longitude"].iloc[0]))


def _interpolate_path(
    df: pd.DataFrame,
    segments: List[Tuple[str, str, Optional[str]]],
) -> Tuple[np.ndarray, np.ndarray, List[Optional[str]]]:
    """
    Build arrays of (lats, lons) and per-point airline for path.
    Each segment is interpolated into small steps for smooth animation.
    """
    lats, lons, airlines = [], [], []
    n_steps = 20  # points per segment
    for from_city, to_city, airline in segments:
        lat_a, lon_a = _get_coords(df, from_city)
        lat_b, lon_b = _get_coords(df, to_city)
        for i in range(n_steps + 1):
            t = i / n_steps
            lat = lat_a + t * (lat_b - lat_a)
            lon = lon_a + t * (lon_b - lon_a)
            lats.append(lat)
            lons.append(lon)
            airlines.append(airline)
    return np.array(lats), np.array(lons), airlines


def _setup_axes(use_cartopy: bool):
    """Create figure and axes (cartopy or plain)."""
    fig = plt.figure(figsize=(12, 8))
    if use_cartopy:
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.set_global()
        ax.coastlines(resolution="110m")
        ax.add_feature(cfeature.OCEAN, facecolor="#b5d0e8")
        ax.add_feature(cfeature.LAND, facecolor="#e8e4d9")
        ax.gridlines(draw_labels=True, linestyle="--", alpha=0.6)
        return fig, ax
    else:
        ax = fig.add_subplot(1, 1, 1)
        ax.set_facecolor("#b5d0e8")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.set_aspect("equal")
        return fig, ax


def plot_and_animate(
    df: pd.DataFrame,
    path_cities: List[str],
    segments: List[Tuple[str, str, Optional[str]]],
    airlines: List[str],
    output_path: Optional[str] = None,
) -> None:
    """
    Plot the flight path on a map and animate the aircraft.

    - path_cities: ordered list of cities on the route
    - segments: (from, to, airline) for each leg
    - airlines: selected airlines (for hub styling)
    """
    use_cartopy = HAS_CARTOPY
    fig, ax = _setup_axes(use_cartopy)
    transform = ccrs.PlateCarree() if use_cartopy else None

    hubs = get_hubs_for_airlines(airlines)

    # Collect all (lat, lon) for path cities
    path_lats = []
    path_lons = []
    for c in path_cities:
        lat, lon = _get_coords(df, c)
        path_lats.append(lat)
        path_lons.append(lon)

    # Draw path segments with airline-specific colors
    for from_city, to_city, airline in segments:
        lat_a, lon_a = _get_coords(df, from_city)
        lat_b, lon_b = _get_coords(df, to_city)
        color = AIRLINE_COLORS.get(airline or "", "#333333")
        if airline is None:
            color = "#666666"
        kwargs = {"color": color, "linewidth": 2, "zorder": 2}
        if use_cartopy:
            ax.plot([lon_a, lon_b], [lat_a, lat_b], transform=transform, **kwargs)
        else:
            ax.plot([lon_a, lon_b], [lat_a, lat_b], **kwargs)

    # Plot and label cities
    for i, city in enumerate(path_cities):
        lat, lon = _get_coords(df, city)
        is_hub = city in hubs
        kwargs = {"zorder": 4, "s": 120 if is_hub else 60}
        if is_hub:
            kwargs["color"] = "#ffcc00"
            kwargs["edgecolors"] = "black"
            kwargs["linewidths"] = 2
        else:
            kwargs["color"] = "#2d5a27"
            kwargs["edgecolors"] = "white"
            kwargs["linewidths"] = 1
        if use_cartopy:
            ax.scatter(lon, lat, transform=transform, **kwargs)
        else:
            ax.scatter(lon, lat, **kwargs)
        ax.annotate(
            city,
            (lon, lat),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
            fontweight="bold" if is_hub else "normal",
            zorder=5,
        )

    # Interpolated path for animation
    lats, lons, _ = _interpolate_path(df, segments)
    if len(lats) == 0:
        plt.suptitle("Flight path (no segments)")
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.show()
        return

    # Aircraft marker (moving point)
    if use_cartopy:
        ac, = ax.plot([], [], "o", color="#c00", markersize=14, markeredgecolor="white",
                      markeredgewidth=2, zorder=10, transform=transform)
    else:
        ac, = ax.plot([], [], "o", color="#c00", markersize=14, markeredgecolor="white",
                      markeredgewidth=2, zorder=10)

    def init():
        ac.set_data([], [])
        return (ac,)

    def animate_frame(k):
        if k < len(lons):
            ac.set_data([lons[k]], [lats[k]])
        return (ac,)

    n_frames = len(lats)
    # blit=False works reliably with Cartopy
    anim = animation.FuncAnimation(
        fig,
        animate_frame,
        init_func=init,
        frames=n_frames,
        interval=50,
        blit=False,
        repeat=True,
    )

    # Fit axes to path with padding (plain axes only)
    if not use_cartopy:
        pad = 5
        ax.set_xlim(min(path_lons) - pad, max(path_lons) + pad)
        ax.set_ylim(min(path_lats) - pad, max(path_lats) + pad)

    plt.suptitle("Airline-aware shortest flight path", fontsize=14)
    plt.tight_layout()

    if output_path:
        if str(output_path).lower().endswith(".gif"):
            try:
                from matplotlib.animation import PillowWriter
                anim.save(output_path, writer=PillowWriter(fps=15), dpi=100)
            except Exception:
                plt.savefig(output_path.replace(".gif", "_static.png"), dpi=150, bbox_inches="tight")
        else:
            plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
