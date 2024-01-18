import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import os
import requests

from functions import show_dynamic_plot, show_historic_tvsf

API_HOST_LOCAL = os.getenv('API_HOST_LOCAL')


# Get main map
response = requests.get(API_HOST_LOCAL + '/main-map')
mapa = gpd.read_file(response.text, driver='GeoJSON')

# Página principal
def main():
    st.markdown("# Consola de Datos 911 CDMX")

    st.markdown('### Obten informacion detallada acerca de los incidentes reportados al 911')

    # name-alcaldia api call
    response = requests.get(API_HOST_LOCAL + '/name-alcaldia')
    names_alcaldias = response.json()['alcaldias']

    # Select box alcaldia
    alcaldia_seleccionada = st.selectbox("Selecciona una alcaldía:", names_alcaldias)

    # Get alcaldia lat & lon
    params = {'name_alcaldia': alcaldia_seleccionada}
    response = requests.get(API_HOST_LOCAL + '/latlon', params=params).json()
    latitud, longitud = response['Latitud'], response['Longitud']

    # Visualizar el mapa
    view_state = pdk.ViewState(
        latitude=latitud,
        longitude=longitud,
        zoom=12
    )

    layer_alcaldias = pdk.Layer(
        "GeoJsonLayer",
        data=mapa,
        get_fill_color=[255, 0, 0, 100],
        get_line_color=[0, 255, 0, 200],
        get_line_width=60, #thicc so they can be seen
        pickable=True,
        auto_highlight=True,
        opacity=0.8,
        tooltip={
                "text": "{NOMGEO}"
        }
    )

    r = pdk.Deck(layers=[layer_alcaldias], initial_view_state=view_state, map_style=None)

    # Mostrar el mapa en Streamlit
    st.pydeck_chart(r)

    if st.button("Desplegar informacion Alcaldía mensual"):
        # Navegar a la página de información detallada
        st.session_state.ubicacion_seleccionada = alcaldia_seleccionada
        st.experimental_rerun()

    # Historic True vs False case calls
    show_historic_tvsf()


    # Página de información detallada
def mostrar_informacion_detallada():
    st.title(f"Información de la Alcaldía {st.session_state.ubicacion_seleccionada}")

    st.markdown('##### *Datos actualizados hasta Julio de 2023')

    # Show plot
    show_dynamic_plot(st.session_state.ubicacion_seleccionada)


# Manejo de la navegación entre páginas
if 'ubicacion_seleccionada' not in st.session_state:
    st.session_state.ubicacion_seleccionada = None

if st.session_state.ubicacion_seleccionada is not None:
    mostrar_informacion_detallada()
    if st.button("Regresar al mapa"):
        # Regresar a la página principal
        st.session_state.ubicacion_seleccionada = None
        st.experimental_rerun()
else:
    main()
