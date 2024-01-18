import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
import os


st.markdown("""
    <link href='https://api.mapbox.com/mapbox-gl-js/v2.3.1/mapbox-gl.css' rel='stylesheet' />
    """, unsafe_allow_html=True)

from functions import get_gcdata, show_dynamic_plot

def get_feature_info(alcaldia_name):
    # dummy data
    example_data = {
        'ALVARO OBREGON': {'Population': 727034, 'Area': '96.17 sq km', 'Description': 'Known for its cultural history and landmarks.'},
        'AZCAPOTZALCO': {'Population': 414711, 'Area': '33.66 sq km', 'Description': 'Industrial and commercial area.'},
        'BENITO JUAREZ': {'Population': 385439, 'Area': '26.63 sq km', 'Description': 'Densely populated and commercially vibrant.'},
        'COYOACAN': {'Population': 620416, 'Area': '54.40 sq km', 'Description': 'Cultural center, home to Frida Kahlo Museum.'},
        'CUAJIMALPA': {'Population': 186391, 'Area': '70.28 sq km', 'Description': 'Contains large expanses of rural areas and forests.'},
        'CUAUHTEMOC': {'Population': 531831, 'Area': '32.44 sq km', 'Description': 'Central borough, heart of the city.'},
        'GUSTAVO A. MADERO': {'Population': 1185772, 'Area': '94.07 sq km', 'Description': 'Largest borough by population.'},
        'IZTACALCO': {'Population': 384326, 'Area': '23.30 sq km', 'Description': 'Small in size but densely populated.'},
        'IZTAPALAPA': {'Population': 1815786, 'Area': '116.67 sq km', 'Description': 'Largest borough by area, diverse and populous.'},
        'MAGDALENA CONTRERAS': {'Population': 239086, 'Area': '74.58 sq km', 'Description': 'Known for its forested areas.'},
        'MIGUEL HIDALGO': {'Population': 372889, 'Area': '46.99 sq km', 'Description': 'Affluent area with many embassies.'},
        'MILPA ALTA': {'Population': 130582, 'Area': '228.41 sq km', 'Description': 'Rural borough with a strong indigenous presence.'},
        'TLAHUAC': {'Population': 360265, 'Area': '85.34 sq km', 'Description': 'Rural and urban mix, known for its chinampas.'},
        'TLALPAN': {'Population': 650567, 'Area': '312.00 sq km', 'Description': 'Largest borough by land, with many ecological reserves.'},
        'VENUSTIANO CARRANZA': {'Population': 430978, 'Area': '33.42 sq km', 'Description': 'Location of the Mexico City International Airport.'},
        'XOCHIMILCO': {'Population': 415007, 'Area': '118.00 sq km', 'Description': 'Famous for its canals and chinampas.'}
    }
    return example_data.get(alcaldia_name, {'Population': 'Unknown', 'Area': 'Unknown', 'Description': 'No data available.'})

# Información sobre las alcaldías
data = {
    'Alcaldía': ['ALVARO OBREGON', 'AZCAPOTZALCO', 'BENITO JUAREZ', 'COYOACAN', 'CUAJIMALPA', 'CUAUHTEMOC', 'GUSTAVO A. MADERO', 'IZTACALCO', 'IZTAPALAPA', 'MAGDALENA CONTRERAS', 'MIGUEL HIDALGO', 'MILPA ALTA', 'TLAHUAC', 'TLALPAN', 'VENUSTIANO CARRANZA', 'XOCHIMILCO'],
    'Latitud': [19.3587, 19.4869, 19.3620, 19.3139, 19.3584, 19.4326, 19.4814, 19.3951, 19.3558, 19.2966, 19.4329,
                19.1406, 19.2861, 19.1963, 19.4319, 19.2480],
    'Longitud': [-99.2536, -99.1840, -99.1626, -99.1622, -99.2974, -99.1332, -99.1037, -99.0970, -99.0759, -99.2847,
                 -99.1936, -99.0095, -99.0045, -99.1380, -99.1124, -99.1276]
}

df_alcaldias = pd.DataFrame(data)
df_alcaldias.set_index('Alcaldía', inplace=True)

# Cargar el archivo GeoJSON con los límites de las alcaldías
#geojson_path = 'geo/archivo.geojson' #whole city
geojson_path = 'archivo.geojson'#city by alcaldia
gdf_alcaldias = gpd.read_file(geojson_path)


# Página principal
def main():
    st.markdown("# Consola de Datos 911 CDMX")

    st.markdown('### Obten informacion detallada acerca de los incidentes reportados al 911')
    extended_alcaldia_list = [''] + list(df_alcaldias.index)

    # Mapa interactivo dividido por alcaldías
    alcaldia_seleccionada = st.selectbox("Selecciona una alcaldía:", extended_alcaldia_list, index=0)

    # locacion initial
    def_latitude= 19.4326 # Latitude for Mexico City center
    def_longitude=  -99.1332  # Longitude for Mexico City center
    def_zoom= 10  # Adjusted zoom level to see the whole city

    if alcaldia_seleccionada:
        # Fetch and display information about the selected alcaldía
        info = get_feature_info(alcaldia_seleccionada)
        st.write(f"Information about {alcaldia_seleccionada}:")
        st.json(info)

        # Update the map based on the selection
        latitud = df_alcaldias.loc[alcaldia_seleccionada, 'Latitud']
        longitud = df_alcaldias.loc[alcaldia_seleccionada, 'Longitud']
        zoom_level = 11
    else:
        # Default view when no selection is made
        latitud = def_latitude
        longitud = def_longitude
        zoom_level = def_zoom


    # Visualizar el mapa
    view_state = pdk.ViewState(
        latitude=latitud,
        longitude=longitud,
        zoom=zoom_level
    )



    layer_alcaldias = pdk.Layer(
                                    "GeoJsonLayer",
                                    data=gdf_alcaldias,
                                    get_fill_color=[200, 30, 0, 100],  # Red, semi-transparent
                                    get_line_color=[0, 0, 0, 100],  # Solid black lines
                                    get_line_width=60, #thicc so they can be seen
                                    pickable=True,
                                    auto_highlight=True,
                                    opacity=0.8,
                                    tooltip={
                                            "text": "{NOMGEO}"
                                            }
        )



    r = pdk.Deck(layers=[layer_alcaldias],
                 initial_view_state=view_state,
                 map_style=None
)

    # Mostrar el mapa en Streamlit
    st.pydeck_chart(r)

    if st.button("Desplegar informacion Alcaldía"):
        # Navegar a la página de información detallada
        st.session_state.ubicacion_seleccionada = alcaldia_seleccionada
        st.experimental_rerun()

    # Página de información detallada
def mostrar_informacion_detallada():
    st.title(f"Información de la Alcaldía {st.session_state.ubicacion_seleccionada}")

    # Get gc data
    data_alcaldia = get_gcdata(st.session_state.ubicacion_seleccionada)

    # Show plot
    show_dynamic_plot(data_alcaldia, st.session_state.ubicacion_seleccionada)



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
