#import the necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import time
from PIL import Image

def app():

    #let's hide the menu
    hide_menu="""
    <style>
    #MainMenu{
        visibility:hidden;
    }
    footer{visibility:hidden;
    }
    </style>
    """
    st.markdown(hide_menu,unsafe_allow_html=True)

    # set page title
    col1, col2 = st.columns(2)
    col2.title('Soil Transmitted Helminthiasis')
    st.markdown('----')

    @st.cache
    def get_data():
        df = pd.DataFrame(pd.read_excel('sth.xlsx')) #reading the data
        df = df[df['region'] == 'AFR']  # get rid of asian countries
        df = df.drop(['Number of Pre-SAC targeted', 'Drug combination, Pre-SAC','Number of SAC targeted','Drug combination, SAC','country_code','region'], axis=1) #get rid of these columns
        #converting relevant columns into numberic
        cols = df.columns.drop(['country','year'])
        df[cols]=df[cols].apply(pd.to_numeric, errors='coerce')
        df = df.fillna(0)  # replace all na values with 0
        df=df.set_index('country')
        return df

    def map(data):
        groupby_country = data.groupby('country').mean()
        #instantiate a new Nominatim client
        app = Nominatim(user_agent="lf")
        #create a dictionary for the selected Countries
        country_loc = dict({'country':[],'lat':[],'lon':[]})
        # get location raw data
        for i in range(len(groupby_country)):
            countries = groupby_country.index.unique().tolist()
            location = location = app.geocode(countries[i]).raw
            country_loc['country'].append(groupby_country.index.unique()[i])
            country_loc['lat'].append(location['lat'])
            country_loc['lon'].append(location['lon'])
        #let's create a new dataframe with the countries and their coordinates
        country_loc = pd.DataFrame(country_loc).set_index('country')
        #let's merge the coordinates with the data
        final_df= groupby_country.merge(country_loc,left_index=True,right_index=True)
        #plotting the map
        if age =='Pre-School-Aged (PSA)':
            figu = px.scatter_mapbox(data_frame=final_df,lon = final_df['lon'].astype(float),lat=final_df['lat'].astype(float),
            color=final_df['National coverage, Pre-SAC']*100,size=final_df['National coverage, Pre-SAC'],
            hover_name=final_df.index)
        else:
            figu = px.scatter_mapbox(data_frame=final_df,lon = final_df['lon'].astype(float),lat=final_df['lat'].astype(float),
            color=final_df['National coverage, SAC']*100,size=final_df['National coverage, SAC'],
            hover_name=final_df.index)
        figu.update_layout(hovermode='closest',mapbox=dict(style='open-street-map',
                                      center=go.layout.mapbox.Center(lat=7.18805555556, lon=21.0936111111), zoom=2), margin={'r': 0, 'l': 0, 'b': 0, 't': 0})
        st.markdown('Average national coverage by country from {} to {}'.format(year[0],year[-1]))
        st.plotly_chart(figu, use_container_width=True)
        return

    def graphs(data, age):
        PreSAC= ['Population requiring PC for STH, Pre-SAC','Reported number of Pre-SAC treated','Programme coverage, Pre-SAC','National coverage, Pre-SAC']
        SAC = ['Population requiring PC for STH, SAC', 'Reported number of SAC treated', 'Programme coverage, SAC', 'National coverage, SAC']
        #table to display raw data
        with st.expander('Click to view raw data'):
            st.write(data[PreSAC if age =='Pre-School-Aged (PSA)' else SAC])
        #first graph - pop requiring PC for LF
        fig2 = px.area(data, y= PreSAC[0] if age =='Pre-School-Aged (PSA)' else SAC[0],x="year",
                      hover_name=data.index, log_x=False, color=data.index, title='Population requiring PC from {} to {}'.format(year[0], year[1]))
        fig2.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})
        #second graph - pop actually treated for LF by year
        fig3 = px.area(
            data, x="year", y=PreSAC[1] if age =='Pre-School-Aged (PSA)' else SAC[1], color=data.index, title='Number treated from {} to {}'.format(year[0], year[1]), log_x=False)
        fig3.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})
        #render first and second grpah side by side for comparison
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig2, use_container_width=True)
        col2.plotly_chart(fig3, use_container_width=True)
        #third graph - national coverage by year
        fig4 = px.line(data, y= PreSAC[-1] if age =='Pre-School-Aged (PSA)' else SAC[-1], x="year",
                       hover_name=data.index, log_x=False, color=data.index, title='National coverage from {} to {}'.format(year[0], year[1]))
        fig4.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})
        #fourth figure - geographic coverage by year
        fig5 = px.line(data, y= PreSAC[2] if age =='Pre-School-Aged (PSA)' else SAC[2], x="year",
                       hover_name=data.index, log_x=True, color=data.index, title='Program Coverage from {} to {}'.format(year[0], year[1]))
        fig5.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})
        #plot fourth and fifth figures side by side for comparison
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig4, use_container_width=True)
        col2.plotly_chart(fig5, use_container_width=True)
        return

    def table(data,age):
        '''this function is for creating a table containing all the average values'''
        #list of columns for SAC and PreSAC
        PreSAC= ['Population requiring PC for STH, Pre-SAC','Reported number of Pre-SAC treated','Programme coverage, Pre-SAC','National coverage, Pre-SAC']
        SAC = ['Population requiring PC for STH, SAC', 'Reported number of SAC treated', 'Programme coverage, SAC', 'National coverage, SAC']
        #let's prepare the data and get the mean values
        groupby_country = data.drop(['year'],axis=1).groupby('country')
        table_df = groupby_country.mean().round(2) #round off the decimals to two places
        col1,col2 = st.columns(2)
        st.markdown('*Average* values by country from {} to {}'.format(year[0],year[1]))
        st.table(table_df[PreSAC if age =='Pre-School-Aged (PSA)' else SAC])
        return

    # get the data
    df = get_data()

    #side options menu
    with st.sidebar.form(key='fetch'):
        nation = st.multiselect('Select countries',df.index.unique().tolist(),['Mali', 'Ethiopia'])
        year = st.select_slider('Select year', options=np.sort(df.year.unique()),value=(2009, 2019))
        age = st.selectbox('Population type',['Pre-School-Aged (PSA)','School-Aged (SA)'])
        fetch = st.form_submit_button(label='Fetch')

    #sidebar info
    with st.sidebar.expander('Click to view Glossary 👓'):
        st.markdown("""
        - **Pre-SAC** – pre-school age children aged =>1 and <5>
        - **SAC** – school age children aged =>5 and <15>
        - **PC** - Preventive Chemotherapy
        - **PCT** - Preventive Chemotherapy and Transmission Control
        - **MDA** - Mass Drug Administration
        - **IU** - Implementation Unit
        - **Population requiring PC for STH**: total population of Pre-SAC and SAC living in all the endemic areas in a country and which require preventive chemotherapy (PC).
        - **Geographical coverage**: proportion (%) of endemic administrative units covered by preventive chemotherapy in a country.
        - **Programme coverage** : proportion (%) of individuals treated as per programme target set.
        - **National coverage**: proportion (%) of the population requiring PC for STH in the country that have been treated.
        """)

    if fetch:
        #prepare the data for graphing
        data=df.loc[nation]
        data = data[data['year'].isin(range(year[0], year[-1]))]
        #title
        st.info('{} Childre Data'.format(age))
        #map it
        map(data)
        #graph
        graphs(data,age)
        #table
        table(data,age)
    else:
        st.warning('Please select from the parameters on the left 👈🏾  and press "Fetch" ')
        st.info("If you don't select a country, you'll get blank graphs 🤪")
