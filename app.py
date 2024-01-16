import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import storage
import pandas as pd
from io import BytesIO

alcaldia_input = 'ALVARO OBREGON'

# Reemplaza con tu información
bucket_name = 'cdmx911'
file_name = f'completa-alcaldia/{alcaldia_input}_data.csv'
project_id = 'lewagon-bootcamp-404323'

# Configura la conexión a Google Cloud Storage
client = storage.Client(project=project_id)
bucket = client.bucket(bucket_name)

# Descarga el archivo CSV como BytesIO
blob = bucket.blob(file_name)
content = blob.download_as_text()
csv_data = BytesIO(content.encode('utf-8'))

data_alcaldia = pd.read_csv(csv_data)


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
                       title=f'Number of Incidents by Type in {file_name.split("/")[1].rstrip("_data.csv")} ({selected_year} - {selected_month})')
               )

# Gráfico de pastel
st.plotly_chart(px.pie(filtered_data, names='incidente_c4', values='count',
                       title=f'Incident Distribution in {file_name.split("/")[1].rstrip("_data.csv")} ({selected_year} - {selected_month})')
               )
