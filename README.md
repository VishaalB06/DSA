# Airline-Aware Shortest Flight Path System

A **Data Structures & Algorithms** project that computes the shortest valid flight path between two cities while respecting **airline route constraints**. Supports **Qatar Airways** (hub: Doha), **Emirates** (hub: Dubai), and **Etihad** (hub: Abu Dhabi). Uses **Dijkstra's algorithm** with a **min-heap** priority queue on an **adjacency-list** graph.

## Features

- **Graph**: Adjacency list; city-to-index **dictionary** (hash map).
- **Dijkstra**: **Priority queue (min-heap)** for greedy shortest-path expansion.
- **Airline-aware**: Edges only exist where a selected airline operates (hub <-> city). Multi-airline routing via hubs (e.g. Chennai -> Doha -> Zanzibar).
- **Visualization**: Real-world map (lat/lon), flight path with airline-specific colors, **animated** aircraft along the route.
- **Optional**: Compare standard vs airline-aware Dijkstra distances.

## Project Structure

```
DSA/
├── data/
│   ├── airport_data.csv    # Generated city/hub distance data (100+ cities)
│   └── airport_data.xlsx   # Optional; generated if openpyxl installed
├── data_loader.py          # Load and clean Excel/CSV data
├── graph_builder.py        # Build adjacency-list graph with airline-aware edges
├── airline_rules.py        # Airline hub and route constraints
├── dijkstra.py             # Modified Dijkstra (airline-aware) + standard
├── visualization.py        # Map plot + aircraft animation
├── main.py                 # User input and orchestration
├── generate_airport_data.py # One-time script to create airport_data CSV/Excel
├── requirements.txt
└── README.md
```

## Setup

1. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate    # Windows
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   For **visualization** you need `matplotlib` and `numpy`. For a **real-world map**, `cartopy` is used; on Windows, if `pip install cartopy` fails, try **conda**: `conda install -c conda-forge cartopy`. If Cartopy is missing, a simple lat/lon plot is used instead.

3. **Generate airport data** (if `data/airport_data.csv` is missing):

   ```bash
   python generate_airport_data.py
   ```

   This creates `data/airport_data.csv` (and `airport_data.xlsx` if `openpyxl` is installed).

## Usage

### Interactive

```bash
python main.py
```

You will be prompted for:

- **Source city**
- **Destination city**
- **Airline(s)** (1–3): Qatar Airways, Emirates, Etihad

The program prints the **path**, **total distance (km)**, and **legs** with airlines, then opens the **map + animation** (unless visualization is skipped).

### Command-line

```bash
python main.py --source Chennai --dest Zanzibar --airlines "Qatar Airways" --no-viz
python main.py -s London -d Tokyo -a "Emirates,Etihad" --no-compare
```

- `--source` / `-s`: Source city  
- `--dest` / `-d`: Destination city  
- `--airlines` / `-a`: Comma-separated airlines (e.g. `"Qatar Airways,Emirates"`)  
- `--no-viz`: Skip map and animation  
- `--no-compare`: Skip standard Dijkstra comparison  
- `--data`: Path to custom `airport_data.xlsx` or `.csv`

## Output

- **Selected airline(s)**
- **Path**: e.g. `Chennai -> Doha -> Zanzibar`
- **Total distance (km)**
- **Legs**: each segment with operating airline
- **Comparison** (optional): standard Dijkstra with *all* airlines vs airline-aware with *selected* airlines
- **Map**: flight path with **Qatar Airways = Burgundy**, **Emirates = Red**, **Etihad = Gold**; **animated** aircraft along the route

If no valid route exists with the chosen airlines:

```
No feasible route with selected airlines.
```

## Data

- **Columns**: City, Country, Latitude, Longitude, Distance to Doha, Distance to Dubai, Distance to Abu Dhabi  
- **Scope**: 100+ major global cities  
- **Format**: Excel (`.xlsx`) or CSV (`.csv`). The loader prefers Excel and falls back to CSV.

## Route restrictions

Each airline serves **hub <-> city** only for cities it actually flies to. Exclusions are defined in `airline_rules.py` via `AIRLINE_EXCLUDED_CITIES` (e.g. Etihad does not serve Zanzibar). To add more exclusions, add city names to the appropriate airline's set:

```python
AIRLINE_EXCLUDED_CITIES["Etihad"] = {"Zanzibar", "Dar es Salaam", ...}
```

## Algorithms & Data Structures

| Requirement        | Implementation                                      |
|--------------------|-----------------------------------------------------|
| Graph              | Adjacency list `adj[i] = [(j, weight_km, airline), ...]` |
| City mapping       | Dictionary `city -> index`                          |
| Priority queue     | `heapq` min-heap                                    |
| Shortest path      | Dijkstra's algorithm                                |
| Airline pruning    | Graph built only with edges for selected airlines   |

**Greedy logic**: The heap always expands the current shortest path; edges are only those allowed by the selected airlines (airline-aware pruning).

## License

Academic / educational use.
"# decentralized-app" 
"# DSA" 
