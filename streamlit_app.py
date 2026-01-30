import streamlit as st
import streamlit.components.v1 as components

from data_loader import load_airport_data
from graph_builder import build_graph
from dijkstra import dijkstra_airline_aware, dijkstra_standard
from airline_rules import SUPPORTED_AIRLINES, get_hub
from web_map import build_map_html

st.set_page_config(page_title="Flight Route Optimizer", layout="wide")

st.title("Flight Route Optimizer — Streamlit Demo")
st.markdown("Use the controls in the sidebar to pick origin, destination, and airlines.")

# Load data
@st.cache_data
def load_data():
    df = load_airport_data()
    return df

df = load_data()
cities = df["City"].tolist()

# Sidebar controls
with st.sidebar.form("route_form"):
    source = st.selectbox("Origin city", options=[""] + cities, index=0)
    destination = st.selectbox("Destination city", options=[""] + cities, index=0)
    airlines = st.multiselect("Preferred airlines", options=list(SUPPORTED_AIRLINES))
    submit = st.form_submit_button("Compute Optimal Route")

if submit:
    if not source or not destination:
        st.error("Please select both origin and destination.")
    elif source == destination:
        st.error("Origin and destination must differ.")
    else:
        try:
            # Build graph and run airline-aware Dijkstra
            adj, c2i, i2c, _ = build_graph(df, airlines if airlines else list(SUPPORTED_AIRLINES))
            result = dijkstra_airline_aware(adj, c2i, i2c, source, destination, airlines if airlines else list(SUPPORTED_AIRLINES))
            if result is None:
                st.warning("No feasible route with selected airlines.")
            else:
                total_km, path_cities, segments = result
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.metric("Total Distance (km)", f"{round(total_km,2)}")
                    st.write("**Route:** " + " → ".join(path_cities))
                    st.write("**Segments:**")
                    for a, b, air in segments:
                        st.write(f"- {a} → {b} ({air or 'transfer'})")
                with col2:
                    st.write("**Hubs in use:**")
                    hubs = sorted({get_hub(a) for a in (airlines if airlines else list(SUPPORTED_AIRLINES))})
                    st.write(", ".join(hubs))

                # Build folium map via web_map helper and render HTML
                try:
                    map_html = build_map_html(df, path_cities, segments, airlines if airlines else list(SUPPORTED_AIRLINES))
                    st.write("#### Route Map")
                    components.html(map_html, height=500)
                except Exception as e:
                    st.error(f"Map rendering failed: {e}")

        except Exception as e:
            st.exception(e)

else:
    st.info("Configure a route in the sidebar and press 'Compute Optimal Route'.")

# Footer / deploy note
st.markdown("---")
st.caption("This Streamlit wrapper uses your existing routing modules. Deploy to Streamlit Community Cloud by pushing this repo to GitHub and connecting it.")
