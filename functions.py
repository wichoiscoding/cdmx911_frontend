import streamlit as st
import pandas as pd
import geopandas as gpd
import pydeck as pdk
from google.cloud import storage
from io import BytesIO
import plotly.express as px
import os


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


def get_gcdata(name_alcaldia):
    #gc info
    bucket_name = 'cdmx911'
    file_name = f'completa-alcaldia/{name_alcaldia}_data.csv'
    project_id = 'lewagon-bootcamp-404323'

    # Verificar si el archivo ya existe localmente
    local_file_path = file_name

    if os.path.exists(local_file_path):
        data_alcaldia = pd.read_csv(local_file_path)

    else:
        # Configura la conexión a gc
        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)

        # Descarga el archivo CSV como BytesIO
        blob = bucket.blob(file_name)
        content = blob.download_as_text()
        csv_data = BytesIO(content.encode('utf-8'))

        data_alcaldia = pd.read_csv(csv_data)
    return data_alcaldia


def show_dynamic_plot(data_alcaldia, name_alcaldia):

    # Convierte la columna 'fecha_creacion' a tipo datetime
    data_alcaldia['fecha_creacion'] = pd.to_datetime(data_alcaldia['fecha_creacion'])

    # Extrae el año y el mes de la fecha de creación
    data_alcaldia['year'] = data_alcaldia['fecha_creacion'].dt.year
    data_alcaldia['month'] = data_alcaldia['fecha_creacion'].dt.month_name()

    # Ordena la lista de meses de enero a diciembre
    sorted_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    # Agrupa por año, mes y tipo de incidente y cuenta la frecuencia
    data_grouped = data_alcaldia.groupby(['year', 'month', 'incidente_c4']).size().reset_index(name='count')

    # Sidebar para la selección de año y mes
    selected_year = st.sidebar.selectbox('Select Year:', data_grouped['year'].unique(), index=len(data_grouped['year'].unique()) - 1)
    selected_month = st.sidebar.selectbox('Select Month:', sorted_months, index=len(sorted_months) - 1)

    # Filtra datos según la selección
    filtered_data = data_grouped[(data_grouped['year'] == selected_year) & (data_grouped['month'] == selected_month)]

    # Gráfico de barras
    st.plotly_chart(px.bar(filtered_data, x='incidente_c4', y='count', color='incidente_c4',
                        labels={'count': 'Number of Incidents'},
                        title=f'Number of Incidents by Type in {name_alcaldia} ({selected_year} - {selected_month})')
                )

    # Gráfico de pastel
    st.plotly_chart(px.pie(filtered_data, names='incidente_c4', values='count',
                        title=f'Incident Distribution in {name_alcaldia} ({selected_year} - {selected_month})')
                )
