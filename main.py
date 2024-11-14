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

@st.cache_data
def ohw(df):
    nunique_year = df.groupby(['name', 'sex'])['year'].nunique()
    one_hit_wonders = nunique_year[nunique_year == 1].index
    one_hit_wonder_data = df.set_index(['name', 'sex']).loc[one_hit_wonders].reset_index()
    return one_hit_wonder_data

data = load_name_data()
ohw_data = ohw(data)


st.title("Anna's Awesome App")

with st.sidebar:
    st.link_button("View 2024 baby name ideas", "https://www.babycenter.com/baby-names/most-popular/top-baby-names-2024")

tab1, tab2, tab3 = st.tabs(['Names', 'Years', 'Letters'])

with tab1:
    input_name = st.text_input("Enter a Name:")
    name_data = data[data['name']==input_name].copy()
    fig = px.line(name_data, x = 'year', y='count', color = 'sex')
    st.plotly_chart(fig)

    
with tab2:
    year_input = st.slider("Year", min_value = 1880, max_value = 2023, value = 2000)

    with st.popover("Open Table"):
        st.write("Unique Names Table")
        table = unique_names_summary(data, year= year_input)
        st.dataframe(table)

    n_names = st.radio("Number of names per sex", [3,5,10])
    fig2 = top_names_plot(data, year=year_input, n = n_names)
    st.plotly_chart(fig2)

def top_letter_plot(df, letter, n=10, width=800, height=600, variable='count'):
    # Ensure 'name' is a string and strip any leading/trailing spaces
    df['name'] = df['name'].str.strip().astype(str)
    
    # Check if the letter input is valid
    if len(letter) != 1 or not letter.isalpha():
        st.error("Please enter a single alphabetical letter.")
        return

    # Check if the 'name' column has any NaN or non-string values
    if df['name'].isnull().any():
        st.warning("There are NaN values in the 'name' column. They will be ignored.")
    
    # Filter data by names starting with the provided letter
    letter_data = df[df['name'].str.startswith(letter, na=False, case=False)].copy()
    
    # Check if any data was filtered
    if letter_data.empty:
        st.warning(f"No data found for names starting with '{letter}'")
        return
    
    letter_data['overall_rank'] = letter_data[variable].rank(method='min', ascending=False).astype(int)
    
    # Process male and female names separately
    male_names = letter_data[letter_data['sex'] == 'M']
    top_male = male_names.sort_values(variable, ascending=False).head(n)
    top_male['sex_rank'] = range(1, len(top_male) + 1)  # Rank within male names

    female_names = letter_data[letter_data['sex'] == 'F']
    top_female = female_names.sort_values(variable, ascending=False).head(n)
    top_female['sex_rank'] = range(1, len(top_female) + 1)  # Rank within female names

    # Combine the male and female data
    combined_data = pd.concat([top_male, top_female]).sort_values(variable, ascending=False)

    # Create the plot
    fig = px.bar(
        combined_data,
        x='name',
        y=variable,
        color='sex',
        category_orders={"name": combined_data['name'].tolist()},
        hover_data={'sex_rank': True, 'overall_rank': True, 'sex': False, 'name': False}
    )

    fig.update_layout(
        title=f"Top {n} Names Starting with '{letter.upper()}' by Gender",
        width=width,
        height=height
    )
    return fig

with tab3:
    letter_input = st.text_input("Enter a letter:", max_chars=1)
    n_letters = st.selectbox("Number of names per sex", [3, 5, 10])

    if letter_input:
        fig3 = top_letter_plot(data, letter=letter_input, n=n_letters)
        if fig3:
            st.plotly_chart(fig3)

    
