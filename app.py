import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson
import streamlit as st
from streamlit_folium import st_folium
import folium

# open a csv file as a dataframe
# gps_data = "Team_1_oyster-1f67 05-12-2022.csv"
gps_data = "/content/drive/MyDrive/Colab Notebooks/BSEN 892/Week3/Python_GPS_data_analysis/Team_1_oyster-1f67 05-12-2022.csv"

# opened dataframe
data_read = pd.read_csv(gps_data)

# Add GPS data to the base map
# The dataset contains a full day of GPS points
# Make the visualization flexible—allow toggling these points on/off
# Split the points into time intervals (e.g., 00:00–06:00, 06:00–12:00, 12:00–18:00, 18:00–24:00)

# preparation
df = data_read.copy()
bins = [0,6,12,18,24]
labels = ["00:00–06:00","06:00–12:00", "12:00–18:00", "18:00–24:00"]
time_col = "Date Logged (CT (-06:00))"
lat_col  = "Latitude"
lon_col  = "Longitude"

# Extract hour information
df["dt"] = pd.to_datetime(df[time_col], format="%m/%d/%Y %H:%M", errors="coerce")
df["date"] = df["dt"].dt.date
df["hour"] = df["dt"].dt.hour

# colors = {
#     "06:00–12:00": "red",
#     "12:00–18:00": "blue",
#     "18:00–24:00": "green",
#     "00:00–06:00": "purple",
# }

# Bucket each row into a 6-hour window
def time_window(h):
    if pd.isna(h):
        return None
    h = int(h)
    if 0  <= h < 6:  return "00:00–06:00"
    if 6  <= h < 12: return "06:00–12:00"
    if 12 <= h < 18: return "12:00–18:00"
    return "18:00–24:00"

# Apply function to each column or row
df["window"] = df["hour"].apply(time_window)

# Create one overlay layer per time window and add red markers
for w in labels:
  df_window = df[df["window"] == w]
  if df_window.empty: continue

  # FeatureGroup object will hold editable figures
  # Create layer for each points according to time window (00:00–06:00, 06:00–12:00, 12:00–18:00, 18:00–24:00)
  fg = folium.FeatureGroup(name=f"{w} (n={len(df_window)})", show=True)

  # Iterate over DataFrame rows and add each circle marker into fg
  for _, r in df_window.iterrows(): 
      # The tooltip shows time/lat/lon for each circle marker
      info = f"""
          Time: {r[time_col]}<br>
          Latitude: {r[lat_col]:.5f}<br>
          Longitude: {r[lon_col]:.5f}
          """
      # Create circle marker for each point (row)
      folium.CircleMarker(
          location=[r[lat_col], r[lon_col]],
          radius=8,
          color="red",
          fill=True,
          fill_color="red",
          fill_opacity=0.9,
          tooltip=folium.Tooltip(info, sticky = True) 
      ).add_to(fg)
  # Add each time window's layer into map
  fg.add_to(m)

# Add the tile layer with a custom display name
center_lat = data_read['Latitude'].mean()
center_lon = data_read['Longitude'].mean()

tile_url = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
attr = ("Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, "
        "Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community")

# Add another base map option
folium.TileLayer(
    tiles=tile_url,
    attr=attr,
    name="Satellite View",   # <<-- your friendly name here
    overlay=False,
    control=True
).add_to(m)

# Layer control - shows checkboxes for the 4 time windows and a radio for base maps
folium.LayerControl(collapsed=False).add_to(m)

# Create a list to hold the GeoJSON data for each time point
features = []

# Iterate over each row in the DataFrame
for index, row in data_read.iterrows():
    # Create a GeoJSON feature for each row https://geojson.org/
    feature = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [row['Longitude'], row['Latitude']]
        },
        'properties': {
            'time': row['Date Logged (CT (-06:00))'],  # Assuming 'Time' is the column name for time data
            'popup': row['Date Logged (CT (-06:00))']  # Adjust the popup content as needed
        }
    }
    # Append the feature to the list
    features.append(feature)

# Create a GeoJSON object containing all the features
geojson = {
    'type': 'FeatureCollection',
    'features': features
}

# Add TimestampedGeoJson plugin to the previous map
# It can show changing geospatial data over time
# here we can use this package to show the changes of GPS points over the day
TimestampedGeoJson(geojson,
          period='PT10M',  # Specify the time interval for each frame (e.g., PT10M represents 10 minute)
          duration='PT10M',  # Specify the duration of each frame
          add_last_point=True,  # Add the last data point for each time point
          auto_play=True,  # Automatically play the animation when the map is loaded
          loop=True,  # Loop the animation
          max_speed=10,  # Maximum speed of the animation
          # loop_button=True,  # Show loop button
          date_options='YYYY/MM/DD HH:mm:ss',  # Date format
          time_slider_drag_update=True  # Update the map as the time slider is dragged
        ).add_to(m)


# 📌 Display the map in Streamlit
st.title("Folium Map in Streamlit")
st_data = st_folium(m, width=1000, height=600)
