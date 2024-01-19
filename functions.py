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


API_HOST_LOCAL = os.getenv('API_HOST_LOCAL')


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
    title='Histórico llamadas Verdaderas vs Incongruentes(2014-2023)',
    names=cuenta_historica_binaria.index.map({1: 'Casos Verdaderos', 0: 'Casos Incongruentes'}),
    color_discrete_sequence=['blue', 'red'])
    )


def show_predicted_incidents(predicted_data):
    """
    plot predicted incident data in line and area charts

    :param predicted_data: Dictionary containing month names as keys and predicted incident counts as values.
    """

    print("Raw Predicted Data:", predicted_data)

    if not isinstance(predicted_data, pd.DataFrame) or 'data' not in predicted_data:
        print("Incorrect data format. 'predicted_data' should be a DataFrame with a 'data' column.")
        return

    actual_data = predicted_data['data'].iloc[0]
    if not isinstance(actual_data, dict):
        print("The 'data' column does not contain a dictionary.")
        return

    # Convert the dictionary to a pandas DataFrame for easier manipulation
    df = pd.DataFrame(list(actual_data.items()), columns=['Month', 'Predicted Incidents'])
    # Convert 'Month' to a categorical type for proper sorting in the plot
    print("DataFrame after conversion:", df.head())

    df['Month'] = pd.Categorical(df['Month'], categories=[
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'],
        ordered=True)
    df.sort_values('Month', inplace=True)
    print(df.head(10))
    print(df.info())
    # Create a line chart
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(x=df['Month'], y=df['Predicted Incidents'], mode='lines+markers',
                                    name='Predicted Incidents', line=dict(color='blue', width=2)))

    # Enhance chart layout
    line_chart.update_layout(title='Monthly Predicted Incident Trends', xaxis_title='Month',
                             yaxis_title='Number of Incidents', template='seaborn')

    # Create an area chart
    area_chart = go.Figure()
    area_chart.add_trace(go.Scatter(x=df['Month'], y=df['Predicted Incidents'], fill='tozeroy',
                                    name='Incident Area', line=dict(color='cyan', width=2)))

    # Enhance chart layout
    area_chart.update_layout(title='Area Chart of Predicted Incidents', xaxis_title='Month',
                             yaxis_title='Number of Incidents', template='seaborn')

    # Pie chart
    pie_chart = go.Figure()
    pie_chart.add_trace(go.Pie(labels=df['Month'], values=df['Predicted Incidents'],
                               name='Incident Distribution'))

    #make it sexy
    pie_chart.update_layout(title='Distribution of Predicted Incidents by Month',
                            template='seaborn')

    # Display charts in Streamlit
    #st.plotly_chart(line_chart)
    st.plotly_chart(area_chart)
    st.plotly_chart(pie_chart)
