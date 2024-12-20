import pandas as pd
import zipfile
import plotly.express as px
import matplotlib.pyplot as plt
import requests
from io import BytesIO
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from my_plots import *
import streamlit as st

@st.cache_data
def load_name_data():
    names_file = 'https://www.ssa.gov/oact/babynames/names.zip'
    response = requests.get(names_file)
    with zipfile.ZipFile(BytesIO(response.content)) as z:
        dfs = []
        files = [file for file in z.namelist() if file.endswith('.txt')]
        for file in files:
            with z.open(file) as f:
                df = pd.read_csv(f, header=None)
                df.columns = ['name','sex','count']
                df['year'] = int(file[3:7])
                dfs.append(df)
        data = pd.concat(dfs, ignore_index=True)
    data['pct'] = data['count'] / data.groupby(['year', 'sex'])['count'].transform('sum')
    return data

data = load_name_data()

st.title("Anna's Name App")

with st.sidebar:
    st.write("Other Resources")
    st.link_button("View 2024 baby name ideas", "https://www.babycenter.com/baby-names/most-popular/top-baby-names-2024")

tab1, tab2 = st.tabs(['Names', 'Years'])

with tab1:
    input_name = st.text_input("Enter a Name:")
    name_data = data[data['name'] == input_name].copy()

    st.write("Line Graph")
    fig_line = px.line(name_data, x='year', y='count', color='sex')
    st.plotly_chart(fig_line, key="line_chart")

    st.write("Histogram")
    fig_histogram = px.histogram(name_data, x='year', y='count', nbins=14, color='sex')
    st.plotly_chart(fig_histogram)
    
with tab2:
    year_input = st.slider("Year", min_value = 1880, max_value = 2023, value = 2000)

    with st.popover("Open Table"):
        st.write("Unique Names Table")
        table = unique_names_summary(data, year= year_input)
        st.dataframe(table)

    n_names = st.radio("Number of names per sex", [3,5,10])
    fig2 = top_names_plot(data, year=year_input, n = n_names)
    st.plotly_chart(fig2)



    
