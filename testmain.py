import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk

# Información sobre las alcaldías
data = {
    'Alcaldía': ['Álvaro Obregón', 'Azcapotzalco', 'Benito Juárez', 'Coyoacán', 'Cuajimalpa', 'Cuauhtémoc',
                 'Gustavo A. Madero', 'Iztacalco', 'Iztapalapa', 'Magdalena Contreras', 'Miguel Hidalgo',
                 'Milpa Alta', 'Tláhuac', 'Tlalpan', 'Venustiano Carranza', 'Xochimilco'],
    'Latitud': [19.3587, 19.4869, 19.3620, 19.3139, 19.3584, 19.4326, 19.4814, 19.3951, 19.3558, 19.2966, 19.4329,
                19.1406, 19.2861, 19.1963, 19.4319, 19.2480],
    'Longitud': [-99.2536, -99.1840, -99.1626, -99.1622, -99.2974, -99.1332, -99.1037, -99.0970, -99.0759, -99.2847,
                 -99.1936, -99.0095, -99.0045, -99.1380, -99.1124, -99.1276]
}

df_alcaldias = pd.DataFrame(data)
df_alcaldias.set_index('Alcaldía', inplace=True)

# Cargar el archivo GeoJSON con los límites de las alcaldías
geojson_path = 'archivo.geojson'
gdf_alcaldias = gpd.read_file(geojson_path)

# Página principal
def main():
    st.title("Mapa Interactivo de la Ciudad de México")

    # Mapa interactivo dividido por alcaldías
    alcaldia_seleccionada = st.selectbox("Selecciona una alcaldía:", df_alcaldias.index)

    # Obtener las coordenadas de la alcaldía seleccionada
    latitud = df_alcaldias.loc[alcaldia_seleccionada, 'Latitud']
    longitud = df_alcaldias.loc[alcaldia_seleccionada, 'Longitud']

    # Visualizar el mapa
    view_state = pdk.ViewState(
        latitude=latitud,
        longitude=longitud,
        zoom=12
    )

    layer_alcaldias = pdk.Layer(
        "GeoJsonLayer",
        data=gdf_alcaldias,
        get_fill_color=[255, 0, 0, 100],
        get_line_color=[0, 255, 0, 200],
    )


    r = pdk.Deck(layers=[layer_alcaldias], initial_view_state=view_state, map_style=None)

    # Mostrar el mapa en Streamlit
    st.pydeck_chart(r)

    if st.button("Ver más información"):
        # Navegar a la página de información detallada
        st.session_state.ubicacion_seleccionada = alcaldia_seleccionada
        st.experimental_rerun()

# Página de información detallada
def mostrar_informacion_detallada():
    st.title(f"Información de la Alcaldía {st.session_state.ubicacion_seleccionada}")
    st.write(f"Detalles de la Alcaldía {st.session_state.ubicacion_seleccionada}")

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
