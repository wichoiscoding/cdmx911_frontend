import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import os
import requests

from functions import show_dynamic_plot, show_historic_tvsf, show_predicted_incidents, get_feature_info, show_aggregated_predictions

API_HOST_LOCAL = os.getenv('SERVICE_URL')
st.set_page_config(layout="wide")


# Get main map
response = requests.get(API_HOST_LOCAL + '/main-map')
mapa = gpd.read_file(response.text, driver='GeoJSON')


# Página principal
def main():
    github_url = "https://github.com/wichoiscoding/"
    badge_url = "https://img.shields.io/badge/-wichoiscoding-black?style=flat-square&logo=github"

    st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center;">
            <h1 style="margin-right: 10px;">Consola de datos 911 CDMX</h1>
            <a href="{github_url}">
                <img src="{badge_url}" alt="GitHub Badge" style="height: 40px;">
            </a>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Obten informacion detallada acerca de los incidentes reportados al 911</h3>", unsafe_allow_html=True)

    #st.markdown('### Obten informacion detallada acerca de los incidentes reportados al 911')

    # name-alcaldia api call
    response = requests.get(API_HOST_LOCAL + '/name-alcaldia')
    names_alcaldias = response.json()['alcaldias']

    # Select box alcaldia
    alcaldia_seleccionada = st.selectbox("Selecciona una alcaldía:", names_alcaldias)
    col1, col2 = st.columns(2)
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

    #response = requests.get(API_HOST_LOCAL + '/model-data', params=params).json()


    with col1:
        st.markdown('## Mapa de CMDX')

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
        st.pydeck_chart(r,use_container_width=True)

        if st.button("Desplegar informacion Alcaldía mensual"):
            # Navegar a la página de información detallada
            st.session_state.ubicacion_seleccionada = alcaldia_seleccionada
            st.experimental_rerun()

    line_chart, pie_chart = show_predicted_incidents(alcaldia_seleccionada)
    #pie_chart = show_aggregated_predictions()
    with col2:
        st.markdown('## Predicciones de Incidentes')
        st.plotly_chart(line_chart,use_container_width=True)

    col3, col4 = st.columns(2)
    total_prediction, per_pop = show_aggregated_predictions()
    with col3:
        st.markdown('## Total incidentes por alcaldía')
        st.plotly_chart(total_prediction,use_container_width=True)

    with col4:
        # Historic True vs False case calls
        st.markdown('## Total incidentes por poblacion')
        st.plotly_chart(per_pop,use_container_width=True)


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
