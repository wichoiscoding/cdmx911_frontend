import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import geopandas as gpd
import pydeck as pdk
from google.cloud import storage
from io import BytesIO
import plotly.express as px
import os
import requests

def get_feature_info(alcaldia_name=None):
    alcaldias_info = {
        'Alvaro Obregon': {
            'Population': 759137,
            'Area': 96.17,
            'Population Density': 7893.70
        },
        'Azcapotzalco': {
            'Population': 432205,
            'Area': 33.66,
            'Population Density': 12840.31
        },
        'Benito Juarez': {
            'Population': 434153,
            'Area': 26.63,
            'Population Density': 16303.15
        },
        'Coyoacan': {
            'Population': 614447,
            'Area': 54.40,
            'Population Density': 11294.98
        },
        'Cuajimalpa de Morelos': {
            'Population': 217686,
            'Area': 70.28,
            'Population Density': 3097.41
        },
        'Cuauhtemoc': {
            'Population': 545884,
            'Area': 32.44,
            'Population Density': 16827.50
        },
        'Gustavo A. Madero': {
            'Population': 1173351,
            'Area': 94.07,
            'Population Density': 12473.17
        },
        'Iztacalco': {
            'Population': 404695,
            'Area': 23.30,
            'Population Density': 17368.88
        },
        'Iztapalapa': {
            'Population': 1835486,
            'Area': 116.67,
            'Population Density': 15732.29
        },
        'La Magdalena Contreras': {
            'Population': 247622,
            'Area': 74.58,
            'Population Density': 3320.22
        },
        'Miguel Hidalgo': {
            'Population': 414470,
            'Area': 46.99,
            'Population Density': 8820.39
        },
        'Milpa Alta': {
            'Population': 152685,
            'Area': 228.41,
            'Population Density': 668.47
        },
        'Tlahuac': {
            'Population': 392313,
            'Area': 85.34,
            'Population Density': 4597.06
        },
        'Tlalpan': {
            'Population': 699928,
            'Area': 312.00,
            'Population Density': 2243.36
        },
        'Venustiano Carranza': {
            'Population': 443704,
            'Area': 33.42,
            'Population Density': 13276.60
        },
        'Xochimilco': {
            'Population': 442178,
            'Area': 118.00,
            'Population Density': 3747.27
        }
    }
    if alcaldia_name is None:
        return list(alcaldias_info.keys())
    else:
        return alcaldias_info.get(alcaldia_name, {'Population': 'Unknown', 'Area': 'Unknown', 'Description': 'No data available.'})

API_HOST_LOCAL = os.getenv('SERVICE_URL')


def show_dynamic_plot(name_alcaldia):

    # Get dynamic data
    params = {'name_alcaldia': name_alcaldia}
    response = requests.get(API_HOST_LOCAL + '/dynamic-data', params=params).json()
    data_grouped = pd.DataFrame(response['data'])
    data_grouped = data_grouped[data_grouped['year'] != 2013]

    # Ordena la lista de meses de enero a diciembre
    sorted_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    sorted_months_2023 = ['January', 'February', 'March', 'April', 'May', 'June', 'July']

    # Sidebar para la selección de año y mes
    selected_year = st.sidebar.selectbox('Seleccionar Año:', data_grouped['year'].unique(), index=len(data_grouped['year'].unique()) - 1)
    if selected_year == 2023:
        selected_month = st.sidebar.selectbox('Seleccionar Mes:', sorted_months_2023, index=len(sorted_months_2023) - 1)
    else:
        selected_month = st.sidebar.selectbox('Seleccionar Mes:', sorted_months, index=len(sorted_months) - 1)

    # Filtra datos según la selección
    filtered_data = data_grouped[(data_grouped['year'] == selected_year) & (data_grouped['month'] == selected_month)]

    # Total incidentes por mes
    st.markdown(f'## Total de Incidentes: {len(filtered_data)}')


    # Gráfico de barras
    st.plotly_chart(px.bar(filtered_data, x='incidente_c4', y='count', color='incidente_c4',
                        labels={'count': 'Numero de Incidentes'},
                        title=f'Numero de Incidentes por Tipo en {name_alcaldia} ({selected_year} - {selected_month})')
                )

    # Gráfico de pastel
    st.plotly_chart(px.pie(filtered_data, names='incidente_c4', values='count',
                        title=f'Distribución de Incidentes en {name_alcaldia} ({selected_year} - {selected_month})')
                )

    # Grafico distribucion por hora
    # Gráfico de distribución por hora del día
    st.plotly_chart(px.bar(filtered_data, x='hora_creacion', y='count',
                                labels={'count': 'Total de Incidentes'},
                                title=f'Total de Incidentes por Hora del Día en el mes de {selected_month} de {selected_year}',
                                color_discrete_sequence=['green']))



def show_historic_tvsf():

    cuenta_historica_binaria = pd.Series(data=[816864, 407711], index=[1, 0])

    # Show pie chart
    st.plotly_chart(px.pie(
    cuenta_historica_binaria,
    labels=cuenta_historica_binaria.index.map({1: 'True Case Calls', 0: 'False Case Calls'}),
    values=cuenta_historica_binaria.values,
    #title='Histórico llamadas Verdaderas vs Incongruentes(2014-2023)',
    names=cuenta_historica_binaria.index.map({1: 'Casos Verdaderos', 0: 'Casos Incongruentes'}),
    color_discrete_sequence=['blue', 'red']),
    use_container_width=True
    )


def show_predicted_incidents(alcaldia_seleccionada):
    """
    plot predicted incident data in line and area charts

    :param model_data: Dictionary containing month names as keys and predicted incident counts as values.
    """


    alcaldia_info = get_feature_info(alcaldia_seleccionada.title())
    population = alcaldia_info.get('Population', 1)  # Default to 1 to avoid division by zero



    params = {'name_alcaldia': alcaldia_seleccionada}
    response = requests.get(API_HOST_LOCAL + '/model-data', params=params).json()
    model_data = pd.DataFrame.from_dict(response)


    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    model_data.index = pd.Categorical(model_data.index, categories=months_order, ordered=True)
    df = model_data.sort_index(inplace=True)


    # Line chart
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(x=model_data.index, y=model_data['data'], mode='lines+markers', name='Predicted Incidents', line=dict(color='blue', width=2)))
    line_chart.update_layout(title='Monthly Predicted Incident Trends', xaxis_title='Month', yaxis_title='Number of Incidents', template='seaborn')

    # Area chart
    area_chart = go.Figure()
    area_chart.add_trace(go.Scatter(x=model_data.index, y=model_data['data'], fill='tozeroy', name='Incident Area', line=dict(color='cyan', width=2)))
    area_chart.update_layout(title='Area Chart of Predicted Incidents', xaxis_title='Month', yaxis_title='Number of Incidents', template='seaborn')

    print("modeldata : ", type(model_data), model_data)
    print("pop variable : ", type(population), population)
    model_data['crashes_per_capita'] = model_data['data'] / population


    # Pie chart
    pie_chart = go.Figure()
    pie_chart.add_trace(go.Pie(labels=model_data.index, values=model_data['crashes_per_capita'], name='Crashes per Capita'))
    pie_chart.update_layout(title='Predicted Crashes per Capita by Month', template='seaborn')

    return line_chart, pie_chart
    # Display charts in Streamlit
    #st.plotly_chart(line_chart)
    #st.plotly_chart(area_chart)
    #st.plotly_chart(pie_chart)


def show_aggregated_predictions():
    # List of all alcaldías
    print("test test")
    alcaldias = get_feature_info()
    total_predictions = {}
    predictions_per_thousand = {}


    for alcaldia in alcaldias:
        params = {'name_alcaldia': alcaldia.upper()}
        response = requests.get(API_HOST_LOCAL + '/model-data', params=params)
        if response.status_code == 200:
            model_data = pd.DataFrame.from_dict(response.json())
            total = model_data['data'].sum()
            total_predictions[alcaldia] = total

            # Get population for the alcaldía
            population_info = get_feature_info(alcaldia)
            population = population_info.get('Population', 1)  # Default to 1 to avoid division by zero

            # Calculate predicted incidents per 1000 people
            predictions_per_thousand[alcaldia] = (total / population) * 1000
        else:
            print(f"Error fetching data for {alcaldia}: {response.status_code}")

    total_prediction_df = pd.DataFrame(list(total_predictions.items()), columns=['Alcaldía', 'Total Predictions'])
    predictions_per_thousand_df = pd.DataFrame(list(predictions_per_thousand.items()), columns=['Alcaldía', 'Predictions per 1000 People'])

    # Sort the DataFrames
    total_prediction_df = total_prediction_df.sort_values(by='Total Predictions', ascending=False)
    predictions_per_thousand_df = predictions_per_thousand_df.sort_values(by='Predictions per 1000 People', ascending=False)

    # Create and display the bar charts
    total_bar_chart = px.bar(total_prediction_df, x='Alcaldía', y='Total Predictions',
                             title='Total Predicted Incidents Distribution Among Alcaldías')
    per_thousand_bar_chart = px.bar(predictions_per_thousand_df, x='Alcaldía', y='Predictions per 1000 People',
                                    title='Predicted Incidents per 1000 People Among Alcaldías')

    #st.plotly_chart(total_bar_chart, use_container_width=True)
    #st.plotly_chart(per_thousand_bar_chart, use_container_width=True)

    return total_bar_chart, per_thousand_bar_chart
