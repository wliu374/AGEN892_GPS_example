import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson
import streamlit as st
from streamlit_folium import st_folium
import folium
with open("./map.html", "r", encoding="utf-8") as f:
    map_html = f.read()
st.title("Folium Map in Streamlit")
st.components.v1.html(map_html, height=600, width=0,scrolling=True)
