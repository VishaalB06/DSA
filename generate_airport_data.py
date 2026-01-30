"""
One-time script to generate airport/city Excel data.
Run: python generate_airport_data.py
Output: data/airport_data.xlsx
"""

import math
import pandas as pd
from pathlib import Path

# Hub coordinates (lat, long)
HUBS = {
    "Doha": (25.2854, 51.5310),
    "Dubai": (25.2048, 55.2708),
    "Abu Dhabi": (24.4539, 54.3773),
}

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance in km between two (lat, lon) points."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return round(R * c, 2)

# 100+ major global cities: (City, Country, Lat, Lon)
CITIES = [
    ("London", "United Kingdom", 51.5074, -0.1278),
    ("Paris", "France", 48.8566, 2.3522),
    ("New York", "United States", 40.7128, -74.0060),
    ("Tokyo", "Japan", 35.6762, 139.6503),
    ("Sydney", "Australia", -33.8688, 151.2093),
    ("Singapore", "Singapore", 1.3521, 103.8198),
    ("Hong Kong", "China", 22.3193, 114.1694),
    ("Dubai", "United Arab Emirates", 25.2048, 55.2708),
    ("Doha", "Qatar", 25.2854, 51.5310),
    ("Abu Dhabi", "United Arab Emirates", 24.4539, 54.3773),
    ("Mumbai", "India", 19.0760, 72.8777),
    ("Delhi", "India", 28.7041, 77.1025),
    ("Chennai", "India", 13.0827, 80.2707),
    ("Bangalore", "India", 12.9716, 77.5946),
    ("Kolkata", "India", 22.5726, 88.3639),
    ("Hyderabad", "India", 17.3850, 78.4867),
    ("Los Angeles", "United States", 34.0522, -118.2437),
    ("Chicago", "United States", 41.8781, -87.6298),
    ("San Francisco", "United States", 37.7749, -122.4194),
    ("Miami", "United States", 25.7617, -80.1918),
    ("Toronto", "Canada", 43.6532, -79.3832),
    ("Vancouver", "Canada", 49.2827, -123.1207),
    ("Montreal", "Canada", 45.5017, -73.5673),
    ("Mexico City", "Mexico", 19.4326, -99.1332),
    ("São Paulo", "Brazil", -23.5505, -46.6333),
    ("Rio de Janeiro", "Brazil", -22.9068, -43.1729),
    ("Buenos Aires", "Argentina", -34.6037, -58.3816),
    ("Bogotá", "Colombia", 4.7110, -74.0721),
    ("Lima", "Peru", -12.0464, -77.0428),
    ("Santiago", "Chile", -33.4489, -70.6693),
    ("Madrid", "Spain", 40.4168, -3.7038),
    ("Barcelona", "Spain", 41.3851, 2.1734),
    ("Rome", "Italy", 41.9028, 12.4964),
    ("Milan", "Italy", 45.4642, 9.1900),
    ("Berlin", "Germany", 52.5200, 13.4050),
    ("Frankfurt", "Germany", 50.1109, 8.6821),
    ("Munich", "Germany", 48.1351, 11.5820),
    ("Amsterdam", "Netherlands", 52.3676, 4.9041),
    ("Brussels", "Belgium", 50.8503, 4.3517),
    ("Vienna", "Austria", 48.2082, 16.3738),
    ("Zurich", "Switzerland", 47.3769, 8.5417),
    ("Stockholm", "Sweden", 59.3293, 18.0686),
    ("Copenhagen", "Denmark", 55.6761, 12.5683),
    ("Oslo", "Norway", 59.9139, 10.7522),
    ("Helsinki", "Finland", 60.1695, 24.9354),
    ("Moscow", "Russia", 55.7558, 37.6173),
    ("Istanbul", "Turkey", 41.0082, 28.9784),
    ("Athens", "Greece", 37.9838, 23.7275),
    ("Lisbon", "Portugal", 38.7223, -9.1393),
    ("Dublin", "Ireland", 53.3498, -6.2603),
    ("Warsaw", "Poland", 52.2297, 21.0122),
    ("Prague", "Czech Republic", 50.0755, 14.4378),
    ("Budapest", "Hungary", 47.4979, 19.0402),
    ("Bucharest", "Romania", 44.4268, 26.1025),
    ("Cairo", "Egypt", 30.0444, 31.2357),
    ("Johannesburg", "South Africa", -26.2041, 28.0473),
    ("Cape Town", "South Africa", -33.9249, 18.4241),
    ("Nairobi", "Kenya", -1.2921, 36.8219),
    ("Lagos", "Nigeria", 6.5244, 3.3792),
    ("Casablanca", "Morocco", 33.5731, -7.5898),
    ("Tunis", "Tunisia", 36.8065, 10.1815),
    ("Dar es Salaam", "Tanzania", -6.7924, 39.2083),
    ("Zanzibar", "Tanzania", -6.1659, 39.2026),
    ("Addis Ababa", "Ethiopia", 9.0320, 38.7469),
    ("Accra", "Ghana", 5.6037, -0.1870),
    ("Tehran", "Iran", 35.6892, 51.3890),
    ("Riyadh", "Saudi Arabia", 24.7136, 46.6753),
    ("Jeddah", "Saudi Arabia", 21.5433, 39.1728),
    ("Kuwait City", "Kuwait", 29.3759, 47.9774),
    ("Baghdad", "Iraq", 33.3152, 44.3661),
    ("Amman", "Jordan", 31.9454, 35.9284),
    ("Beirut", "Lebanon", 33.8938, 35.5018),
    ("Karachi", "Pakistan", 24.8607, 67.0011),
    ("Lahore", "Pakistan", 31.5204, 74.3587),
    ("Dhaka", "Bangladesh", 23.8103, 90.4125),
    ("Colombo", "Sri Lanka", 6.9271, 79.8612),
    ("Kabul", "Afghanistan", 34.5553, 69.2075),
    ("Kathmandu", "Nepal", 27.7172, 85.3240),
    ("Bangkok", "Thailand", 13.7563, 100.5018),
    ("Kuala Lumpur", "Malaysia", 3.1390, 101.6869),
    ("Jakarta", "Indonesia", -6.2088, 106.8456),
    ("Manila", "Philippines", 14.5995, 120.9842),
    ("Ho Chi Minh City", "Vietnam", 10.8231, 106.6297),
    ("Hanoi", "Vietnam", 21.0285, 105.8542),
    ("Seoul", "South Korea", 37.5665, 126.9780),
    ("Beijing", "China", 39.9042, 116.4074),
    ("Shanghai", "China", 31.2304, 121.4737),
    ("Guangzhou", "China", 23.1291, 113.2644),
    ("Shenzhen", "China", 22.5431, 114.0579),
    ("Chengdu", "China", 30.5728, 104.0668),
    ("Taipei", "Taiwan", 25.0330, 121.5654),
    ("Auckland", "New Zealand", -36.8509, 174.7645),
    ("Wellington", "New Zealand", -41.2866, 174.7756),
    ("Melbourne", "Australia", -37.8136, 144.9631),
    ("Perth", "Australia", -31.9505, 115.8605),
    ("Brisbane", "Australia", -27.4698, 153.0251),
    ("Adelaide", "Australia", -34.9285, 138.6007),
    ("Houston", "United States", 29.7604, -95.3698),
    ("Dallas", "United States", 32.7767, -96.7970),
    ("Atlanta", "United States", 33.7490, -84.3880),
    ("Washington D.C.", "United States", 38.9072, -77.0369),
    ("Boston", "United States", 42.3601, -71.0589),
    ("Seattle", "United States", 47.6062, -122.3321),
    ("Denver", "United States", 39.7392, -104.9903),
    ("Phoenix", "United States", 33.4484, -112.0740),
    ("Las Vegas", "United States", 36.1699, -115.1398),
    ("Orlando", "United States", 28.5383, -81.3792),
    ("Philadelphia", "United States", 39.9526, -75.1652),
    ("Detroit", "United States", 42.3314, -83.0458),
    ("Minneapolis", "United States", 44.9778, -93.2650),
    ("Cleveland", "United States", 41.4993, -81.6944),
    ("St. Louis", "United States", 38.6270, -90.1994),
    ("Tampa", "United States", 27.9506, -82.4572),
    ("Baltimore", "United States", 39.2904, -76.6122),
    ("Pittsburgh", "United States", 40.4406, -79.9959),
    ("Charlotte", "United States", 35.2271, -80.8431),
    ("Austin", "United States", 30.2672, -97.7431),
    ("San Diego", "United States", 32.7157, -117.1611),
    ("Portland", "United States", 45.5152, -122.6784),
    ("Sacramento", "United States", 38.5816, -121.4944),
    ("Manchester", "United Kingdom", 53.4808, -2.2426),
    ("Birmingham", "United Kingdom", 52.4862, -1.8904),
    ("Glasgow", "United Kingdom", 55.8642, -4.2518),
    ("Edinburgh", "United Kingdom", 55.9533, -3.1883),
    ("Lyon", "France", 45.7640, 4.8357),
    ("Marseille", "France", 43.2965, 5.3698),
    ("Nice", "France", 43.7102, 7.2620),
    ("Hamburg", "Germany", 53.5511, 9.9937),
    ("Cologne", "Germany", 50.9375, 6.9603),
    ("Stuttgart", "Germany", 48.7758, 9.1829),
    ("Düsseldorf", "Germany", 51.2277, 6.7735),
    ("Rotterdam", "Netherlands", 51.9225, 4.4792),
    ("Antwerp", "Belgium", 51.2213, 4.4051),
    ("Geneva", "Switzerland", 46.2044, 6.1432),
    ("Luxembourg", "Luxembourg", 49.6116, 6.1319),
    ("Bratislava", "Slovakia", 48.1486, 17.1077),
    ("Ljubljana", "Slovenia", 46.0569, 14.5058),
    ("Zagreb", "Croatia", 45.8150, 15.9819),
    ("Belgrade", "Serbia", 44.7866, 20.4489),
    ("Sofia", "Bulgaria", 42.6977, 23.3219),
    ("Kiev", "Ukraine", 50.4501, 30.5234),
    ("Minsk", "Belarus", 53.9045, 27.5615),
    ("Tallinn", "Estonia", 59.4370, 24.7536),
    ("Riga", "Latvia", 56.9496, 24.1052),
    ("Vilnius", "Lithuania", 54.6872, 25.2797),
    ("Almaty", "Kazakhstan", 43.2389, 76.9455),
    ("Tashkent", "Uzbekistan", 41.2995, 69.2401),
    ("Baku", "Azerbaijan", 40.4093, 49.8671),
    ("Tbilisi", "Georgia", 41.7151, 44.8271),
    ("Yerevan", "Armenia", 40.1872, 44.5152),
    ("Tel Aviv", "Israel", 32.0853, 34.7818),
    ("Doha", "Qatar", 25.2854, 51.5310),
]

# Deduplicate by (City, Country) and ensure 100+ unique cities
seen = set()
final = []
for c in CITIES:
    key = (c[0].strip(), c[1])
    if key in seen:
        continue
    seen.add(key)
    final.append((c[0].strip(), c[1], c[2], c[3]))

# Add more cities to exceed 100
extra = [
    ("Abidjan", "Ivory Coast", 5.3600, -4.0083),
    ("Dakar", "Senegal", 14.7167, -17.4677),
    ("Algiers", "Algeria", 36.7538, 3.0588),
    ("Kampala", "Uganda", 0.3476, 32.5825),
    ("Lusaka", "Zambia", -15.3875, 28.3228),
    ("Harare", "Zimbabwe", -17.8292, 31.0522),
    ("Maputo", "Mozambique", -25.9692, 32.5732),
    ("Kigali", "Rwanda", -1.9536, 30.0606),
    ("Malé", "Maldives", 4.1755, 73.5093),
    ("Victoria", "Seychelles", -4.6200, 55.4550),
    ("Port Louis", "Mauritius", -20.1609, 57.5012),
    ("Muscat", "Oman", 23.5880, 58.3829),
    ("Manama", "Bahrain", 26.0667, 50.5577),
    ("Dammam", "Saudi Arabia", 26.4207, 50.0888),
]
for e in extra:
    k = (e[0], e[1])
    if k not in seen:
        seen.add(k)
        final.append(e)

def main():
    rows = []
    for city, country, lat, lon in final:
        d_doha = haversine_km(lat, lon, *HUBS["Doha"])
        d_dubai = haversine_km(lat, lon, *HUBS["Dubai"])
        d_abu = haversine_km(lat, lon, *HUBS["Abu Dhabi"])
        rows.append({
            "City": city,
            "Country": country,
            "Latitude": lat,
            "Longitude": lon,
            "Distance to Doha": d_doha,
            "Distance to Dubai": d_dubai,
            "Distance to Abu Dhabi": d_abu,
        })
    df = pd.DataFrame(rows)
    out_dir = Path(__file__).resolve().parent / "data"
    out_dir.mkdir(exist_ok=True)
    csv_path = out_dir / "airport_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"Wrote {len(df)} cities to {csv_path}")
    try:
        import openpyxl  # noqa: F401
        xlsx_path = out_dir / "airport_data.xlsx"
        df.to_excel(xlsx_path, index=False, sheet_name="Airports")
        print(f"Also wrote {xlsx_path}")
    except ImportError:
        print("Install openpyxl to also generate airport_data.xlsx")

if __name__ == "__main__":
    main()
