import requests
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import concurrent.futures
import ssl
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from streamlit.components.v1 import html

# Custom adapter to force TLS version
class SslAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        context.set_ciphers('DEFAULT:@SECLEVEL=1')  # Lower security level if needed
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# Create session with custom adapter
session = requests.Session()
session.mount('https://', SslAdapter())

# Dictionary of major SF neighborhoods and additional areas with approximate centroid lat/long (based on public geographic data)
locations = {
    'Alamo Square': (37.776, -122.434),
    'Bayview': (37.726, -122.39),
    'Bernal Heights': (37.743, -122.415),
    'Castro': (37.761, -122.435),
    'Chinatown': (37.794, -122.408),
    'Excelsior': (37.724, -122.427),
    'Financial District': (37.794, -122.399),
    'Haight-Ashbury': (37.77, -122.447),
    'Mission': (37.76, -122.419),
    'Nob Hill': (37.793, -122.414),
    'Noe Valley': (37.751, -122.432),
    'North Beach': (37.801, -122.409),
    'Pacific Heights': (37.792, -122.435),
    'Potrero Hill': (37.76, -122.401),
    'Richmond': (37.78, -122.48),
    'SOMA': (37.778, -122.405),
    'Sunset': (37.76, -122.48),
    'Tenderloin': (37.783, -122.411),
    'Pier 39': (37.8087, -122.4098),
    'Golden Gate Park': (37.7694, -122.4762),
    'Baker Beach': (37.7936, -122.4837),
    'Ocean Beach': (37.7594, -122.5107),
    'Coit Tower': (37.8024, -122.4058),
    'Golden Gate Bridge Area': (37.8199, -122.4786),
    'Dolores Park': (37.7597, -122.4271),
    'Presidio': (37.7989, -122.4662),
    'Buena Vista Park': (37.7682, -122.4414),
    'Corona Heights Park': (37.7648, -122.4390),
    'Twin Peaks': (37.7544, -122.4474),
    'McLaren Park': (37.7178, -122.4193),
    'Lincoln Park': (37.7858, -122.5023),
    'Glen Canyon Park': (37.7390, -122.4430),
    'Sutro Heights Park': (37.7778, -122.5111),
    'Washington Square Park': (37.8008, -122.4101),
    'Crissy Field': (37.8030, -122.4650),
    'Lafayette Park': (37.7918, -122.4278),
    'Stern Grove': (37.7363, -122.4770),
    'Mountain Lake Park': (37.7875, -122.4678),
    'Duboce Park': (37.7695, -122.4330),
    'Union Square': (37.7879, -122.4075),
    'Salesforce Tower': (37.7899, -122.3969),
    'Lombard Street': (37.8021, -122.4187),
    'Transamerica Pyramid': (37.7952, -122.4029),
    'Ferry Building': (37.7956, -122.3933),
    'Palace of Fine Arts': (37.8034, -122.4487),
    'Exploratorium': (37.8010, -122.3978),
    'Cable Car Museum': (37.7947, -122.4116),
    'Alcatraz Island': (37.8267, -122.4228),
    'California Academy of Sciences': (37.7699, -122.4661),
    'de Young Museum': (37.7714, -122.4688),
    'Sutro Baths': (37.7833, -122.5136),
    'Lands End Trail': (37.7877, -122.5053),
    'Batteries to Bluffs Trail': (37.793, -122.483),
    'Mount Sutro Trail': (37.758, -122.456),
    "Philosopher's Way Trail": (37.717, -122.419),
    "Lovers' Lane Trail": (37.797, -122.457),
    'Strawberry Hill Trail': (37.7685, -122.4754),
    'China Beach': (37.7879851, -122.4910832),
    "Marshall's Beach": (37.801685, -122.479965),
    'Fort Funston Beach': (37.7195436, -122.5028052),
    'Aquatic Park Beach': (37.8064236, -122.4239802),
    'Mile Rock Beach': (37.7927536, -122.5103236),
    'India Basin Shoreline Park': (37.73421, -122.37605),
    'Alta Plaza Park': (37.7911417, -122.4376241),
    'Angelo J. Rossi Playground': (37.7787325, -122.4572683),
    'Aptos Playground': (37.728, -122.467),
    'Argonne Playground': (37.7793741, -122.4777496),
    'Balboa Park': (37.725353, -122.445496),
    'Billy Goat Hill Trail': (37.741382, -122.432971),
    'Cabrillo Playground': (37.77289, -122.49874),
    'Cayuga Playground': (37.713856, -122.450439),
    'Collis P. Huntington Park': (37.79217, -122.41218),
    'Conservatory of Flowers': (37.7723, -122.46),
    'Agua Vista Park': (37.7704, -122.3856),
    'Bayfront Park': (37.7725, -122.3855),
    'Bayview Gateway Park': (37.727, -122.386),
    'Brannan Street Park': (37.780, -122.391),
    'China Basin Park': (37.774, -122.389),
    'Crane Cove Park': (37.757, -122.383),
    'Cruise Terminal Plaza': (37.794, -122.387),
    'Fort Point Beach': (37.8105, -122.4770),
    'Asian Art Museum': (37.7803, -122.4166),
    'SFMOMA': (37.7857, -122.4012),
    'Beat Museum': (37.7976, -122.4059),
    'Museum of the African Diaspora': (37.7861, -122.4010),
    'Cartoon Art Museum': (37.7830, -122.4007),
    'Mission Dolores': (37.7641, -122.4264),
    "Old St. Mary's Church": (37.7926, -122.4059)
}

# Conversion factors
KMH_TO_MPH = 0.621371
C_TO_F = lambda c: (c * 9/5) + 32

# Thermal Neutral Zone range in °F (based on reliable sources)
TNZ_LOW = 68  # 20°C
TNZ_HIGH = 77  # 25°C

# Function to get current weather batch
def get_current_weather_batch(names, lats, lons):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={','.join(map(str, lats))}&longitude={','.join(map(str, lons))}&current=cloud_cover,wind_speed_10m,temperature_2m&timezone=America/Los_Angeles"
    response = session.get(url)
    if response.status_code == 200:
        data = response.json()
        if not isinstance(data, list):
            data = [data]
        results = []
        for i, d in enumerate(data):
            currents = d['current']
            name = names[i]
            cloud = currents['cloud_cover']
            wind = round(currents['wind_speed_10m'] * KMH_TO_MPH, 1)
            temp = round(C_TO_F(currents['temperature_2m']))
            sunny = cloud < 30
            results.append({'name': name, 'lat': lats[i], 'lon': lons[i], 'cloud': cloud, 'wind': wind, 'temp': temp, 'sunny': sunny})
        return results
    return []

# Function to get daily weather batch
def get_daily_weather_batch(names, lats, lons):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={','.join(map(str, lats))}&longitude={','.join(map(str, lons))}&daily=cloud_cover_mean,wind_speed_10m_max,temperature_2m_mean&forecast_days=1&timezone=America/Los_Angeles"
    response = session.get(url)
    if response.status_code == 200:
        data = response.json()
        if not isinstance(data, list):
            data = [data]
        results = []
        for i, d in enumerate(data):
            dailys = d['daily']
            name = names[i]
            cloud_mean = dailys['cloud_cover_mean'][0]
            wind_max = round(dailys['wind_speed_10m_max'][0] * KMH_TO_MPH, 2)
            temp_mean = round(C_TO_F(dailys['temperature_2m_mean'][0]))
            results.append({'name': name, 'cloud_mean': cloud_mean, 'wind_max': wind_max, 'temp_mean': temp_mean})
        return results
    return []

# Prepare lists
all_names = list(locations.keys())
all_lats = [lat for lat, lon in locations.values()]
all_lons = [lon for lat, lon in locations.values()]

batch_size = 20  # Adjust based on API limits; Open-Meteo can handle more, but safe

# Helper to fetch batches in parallel
def fetch_current_batch(batch):
    names, lats, lons = batch
    return get_current_weather_batch(names, lats, lons)

def fetch_daily_batch(batch):
    names, lats, lons = batch
    return get_daily_weather_batch(names, lats, lons)

# Inline CSS
css = """
/* General styling */
body {
    font-family: 'Arial', sans-serif;
    background-color: #f0f4f8;
    color: #333;
}

h1, h2 {
    color: #007bff;
}

/* Sidebar styling */
.sidebar .sidebar-content {
    background-color: #ffffff;
    border-right: 1px solid #ddd;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Dataframe styling */
.stDataFrame {
    width: 100%;
    overflow-x: auto;
}

/* Map container */
.stFolium {
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Buttons and alerts */
.stButton > button {
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.5rem 1rem;
}

.stAlert {
    border-radius: 4px;
}

/* Reduce spacing between elements */
div.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}

.stMarkdown, .stHeader {
    margin-top: 0.5rem !important;
    margin-bottom: 0.5rem !important;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .sidebar .sidebar-content {
        border-right: none;
        border-bottom: 1px solid #ddd;
    }

    h1 {
        font-size: 1.5rem;
    }

    h2 {
        font-size: 1.2rem;
    }

    .stDataFrame {
        font-size: 0.8rem;
    }
}

/* Increased width by another 20%... REM to check */
.main .block-container {
    max-width: 1051px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
"""
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Streamlit app layout
st.title("San Francisco Weather Tracker App")

# Fetch daily weather data early since it's needed for optimal location
with st.spinner('Fetching daily weather data...'):
    daily_data = []
    batches = []
    for i in range(0, len(all_names), batch_size):
        batches.append((
            all_names[i:i+batch_size],
            all_lats[i:i+batch_size],
            all_lons[i:i+batch_size]
        ))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_daily_batch, batch) for batch in batches]
        for future in concurrent.futures.as_completed(futures):
            daily_data.extend(future.result())

df_daily = None
optimal = None
optimal_lat = None
optimal_lon = None
optimal_cloud = None
optimal_wind = None
optimal_temp = None
if daily_data:
    df_daily = pd.DataFrame(daily_data)
    
    # Filter for TNZ
    df_tnz = df_daily[(df_daily['temp_mean'] >= TNZ_LOW) & (df_daily['temp_mean'] <= TNZ_HIGH)].copy()
    
    if not df_tnz.empty:
        # Sort: lowest cloud first, then lowest wind
        df_tnz.sort_values(by=['cloud_mean', 'wind_max'], inplace=True)
        optimal = df_tnz.iloc[0]
    else:
        # Fallback: overall optimal without TNZ filter, sorted by cloud, wind, then closest to TNZ center
        df_daily['temp_diff'] = abs(df_daily['temp_mean'] - (TNZ_LOW + TNZ_HIGH) / 2)
        df_daily.sort_values(by=['cloud_mean', 'wind_max', 'temp_diff'], inplace=True)
        optimal = df_daily.iloc[0]
    
    if optimal is not None:
        optimal_name = optimal['name']
        optimal_lat, optimal_lon = locations[optimal_name]
        optimal_cloud = optimal['cloud_mean']
        optimal_wind = optimal['wind_max']
        optimal_temp = optimal['temp_mean']

# Section 1: Current Sunny Areas Map
st.markdown('<div id="current-sunny"></div>', unsafe_allow_html=True)
st.header("Current Sunny Areas in San Francisco")
st.write("Green markers indicate sunny areas (cloud cover < 30%). Red indicates cloudy. Blue indicates optimal location for best weather today.")

with st.spinner('Fetching current weather data...'):
    current_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_current_batch, batch) for batch in batches]
        for future in concurrent.futures.as_completed(futures):
            current_data.extend(future.result())

if current_data:
    df_current = pd.DataFrame(current_data)

    # Create Folium map centered on SF
    m = folium.Map(location=[37.77, -122.42], zoom_start=12, tiles="CartoDB Positron")

    # Add markers
    for row in df_current.itertuples():
        color = 'green' if row.sunny else 'red'
        popup_html = f"""
        {row.name}<br>
        Cloud: {row.cloud}% <br>
        Wind: {row.wind} mph <br>
        Temp: {row.temp} °F <br>
        <a href="https://www.google.com/maps/dir/?api=1&destination={row.lat},{row.lon}" target="_blank">Navigate to {row.name}</a>
        """
        folium.CircleMarker(
            location=(row.lat, row.lon),
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)

    # Add blue marker for optimal location if available
    if optimal_lat and optimal_lon:
        popup_html_opt = f"""
        Optimal: {optimal['name']}<br>
        Avg Cloud: {optimal_cloud}% <br>
        Max Wind: {optimal_wind} mph <br>
        Avg Temp: {optimal_temp} °F <br>
        <a href="https://www.google.com/maps/dir/?api=1&destination={optimal_lat},{optimal_lon}" target="_blank">Navigate to {optimal['name']}</a>
        """
        folium.CircleMarker(
            location=(optimal_lat, optimal_lon),
            radius=12,
            color='blue',
            fill=True,
            fill_color='blue',
            popup=folium.Popup(popup_html_opt, max_width=300)
        ).add_to(m)

    # Display map in Streamlit
    folium_static(m)
else:
    st.error("Error fetching current weather data.")

# Section 2: Optimal Location for Today
st.markdown('<div id="optimal-location"></div>', unsafe_allow_html=True)
st.header("Optimal Location for Best Weather Today")
st.write("Based on temperature within the thermal neutral zone (68-77°F), then lowest average cloud cover (most sun), then lowest max wind speed (least wind).")

if optimal is not None:
    if 'temp_diff' in optimal:
        st.warning(f"No locations within the thermal neutral zone today. The closest optimal is **{optimal['name']}** with average cloud cover {optimal['cloud_mean']}%, max wind {optimal['wind_max']} mph, and average temp {optimal['temp_mean']} °F.")
    else:
        st.success(f"The optimal location today is **{optimal['name']}** with average cloud cover {optimal['cloud_mean']}%, max wind {optimal['wind_max']} mph, and average temp {optimal['temp_mean']} °F.")
else:
    st.error("Error determining optimal location.")

# Daily Weather Data
st.markdown('<div id="daily-weather"></div>', unsafe_allow_html=True)
st.header("Daily Weather Data")
if df_daily is not None:
    display_df = df_daily.copy()
    rename_dict = {'cloud_mean': 'Avg Cloud Cover (%)', 'wind_max': 'Max Wind Speed (mph)', 'temp_mean': 'Avg Temp (°F)', 'temp_diff': 'Temp Deviation from Comfort (°F)'}
    display_df.rename(columns=rename_dict, inplace=True)
    format_dict = {'Max Wind Speed (mph)': '{:.2f}'}
    if 'Temp Deviation from Comfort (°F)' in display_df.columns:
        format_dict['Temp Deviation from Comfort (°F)'] = '{:.2f}'
    styled_df = display_df.style.highlight_min(subset=['Avg Cloud Cover (%)', 'Max Wind Speed (mph)'], color='#4CBB17').highlight_max(subset=['Avg Temp (°F)'], color='#4CBB17').format(format_dict)
    st.dataframe(styled_df, hide_index=True)
else:
    st.error("No daily weather data available.")

# Thermal Neutral Zone Areas
st.markdown('<div id="tnz-areas"></div>', unsafe_allow_html=True)
st.header("Areas within Human Thermal Neutral Zone")
st.write("The thermal neutral zone for humans is the range of ambient temperatures, typically 68-77°F (20-25°C) for lightly clothed individuals at rest, where the body can maintain its core temperature without additional metabolic effort for heating or cooling.")

if df_daily is not None and not df_daily.empty:
    tnz_locations = df_daily[(df_daily['temp_mean'] >= TNZ_LOW) & (df_daily['temp_mean'] <= TNZ_HIGH)]['name'].tolist()
    if tnz_locations:
        st.markdown("Locations within the thermal neutral zone:\n" + "\n".join(f"- {loc}" for loc in sorted(tnz_locations)))
    else:
        st.write("No locations within the thermal neutral zone today.")
else:
    st.error("No data available for thermal neutral zone analysis.")