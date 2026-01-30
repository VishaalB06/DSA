"""
airline_rules.py
Airline route constraints: hub cities and which routes each airline operates.
"""

from typing import Dict, FrozenSet, List, Optional, Set, Tuple

AIRLINE_HUBS: Dict[str, str] = {
    "Qatar Airways": "Doha",
    "Emirates": "Dubai",
    "Etihad": "Abu Dhabi",
}

AIRLINE_COLORS: Dict[str, str] = {
    "Qatar Airways": "#800020",
    "Emirates": "#E41B17",
    "Etihad": "#F4C430",
}

SUPPORTED_AIRLINES: FrozenSet[str] = frozenset(AIRLINE_HUBS.keys())

AIRLINE_EXCLUDED_CITIES: Dict[str, Set[str]] = {
    "Qatar Airways": {
        "Vancouver", "Adelaide", "Wellington", "Perth", "Brisbane",
        "Denver", "Phoenix", "Orlando", "Detroit", "Minneapolis",
        "Cleveland", "St. Louis", "Tampa", "Baltimore", "Pittsburgh",
        "Charlotte", "Austin", "San Diego", "Portland", "Sacramento",
        "Bogota", "Lima", "Santiago", "Mexico City", "Lagos",
    },
    "Emirates": {
        "Vancouver", "Adelaide", "Wellington", "Perth", "Brisbane",
        "Denver", "Phoenix", "Orlando", "Detroit", "Minneapolis",
        "Cleveland", "St. Louis", "Tampa", "Baltimore", "Pittsburgh",
        "Charlotte", "Austin", "San Diego", "Portland", "Sacramento",
        "Zanzibar", "Kampala", "Lusaka", "Harare",
        "Bogota", "Lima", "Santiago", "Mexico City",
    },
    "Etihad": {
        "Vancouver", "Adelaide", "Wellington", "Perth", "Brisbane",
        "Denver", "Phoenix", "Orlando", "Detroit", "Minneapolis",
        "Cleveland", "St. Louis", "Tampa", "Baltimore", "Pittsburgh",
        "Charlotte", "Austin", "San Diego", "Portland", "Sacramento",
        "Mexico City", "Bogota", "Lima", "Santiago",
        "Rio de Janeiro", "Sao Paulo", "Buenos Aires",
        "Lagos", "Accra", "Cape Town", "Zanzibar",
    },
}

def airline_serves_city(airline: str, city: str) -> bool:
    hubs = {"Doha", "Dubai", "Abu Dhabi"}
    if city in hubs:
        return True
    excluded = AIRLINE_EXCLUDED_CITIES.get(airline, set())
    return city not in excluded

def get_hub(airline: str) -> str:
    if airline not in AIRLINE_HUBS:
        raise ValueError(f"Unknown airline: {airline}")
    return AIRLINE_HUBS[airline]

def get_hubs_for_airlines(airlines: List[str]) -> Set[str]:
    return {get_hub(a) for a in airlines}

def is_hub(city: str, airlines: List[str]) -> bool:
    return city in get_hubs_for_airlines(airlines)

def operates_route(airline: str, origin: str, dest: str, cities: Set[str]) -> bool:
    hub = get_hub(airline)
    if origin not in cities or dest not in cities:
        return False
    if origin == hub:
        return airline_serves_city(airline, dest)
    if dest == hub:
        return airline_serves_city(airline, origin)
    return False

def get_route_airline(origin: str, dest: str, airlines: List[str], hubs: Set[str]) -> Optional[str]:
    for air in airlines:
        h = get_hub(air)
        if origin == h and dest != h and airline_serves_city(air, dest):
            return air
        if dest == h and origin != h and airline_serves_city(air, origin):
            return air
    return None
