#import the necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import time
from PIL import Image
import folium
from streamlit_folium import folium_static
import geopandas as gpd

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
    col2.title('Lymphatic Filariasis')
    st.markdown('----')

    ##################################################################################
    ##################################################################################
    #######   Functions to grab data, transform it, graph, and map it!!!!!     #######
    ##################################################################################
    ##################################################################################

    @st.cache # cache the functions for faster use

    def get_data(): #function to grab and transform the data
        df = pd.DataFrame(pd.read_excel("LF_data.xlsx"))  # reading the data
        df = df[df["region"] == "AFR"]  # get rid of asian countries
        df = df.drop(
            ["Current status of MDA", "country_code", "Type of MDA", "region"], axis=1
        )  # get rid of these columns
        # converting relevant columns into numberic
        cols = df.columns.drop(["country", "year", "Mapping status"])
        df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
        df = df.fillna(0)  # replace all na values with 0
        df = df.set_index("country")
        df[['National coverage','Geographical coverage','Programme (drug) coverage']]=df[['National coverage','Geographical coverage','Programme (drug) coverage']].transform(lambda x: x*100)

        return df


    def graphs(data):

        # first graph - time vs drug coverage trends
        drug = px.line(
            data,
            y="Programme (drug) coverage",
            x="year",
            hover_name=data.index,
            log_x=False,
            color=data.index,
            title="Program drug coverage by year",
        )
        drug.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
        with st.expander("Click to view program drug coverage trends"):
            st.plotly_chart(drug, use_container_width=True)

        # second graph - pop requiring PC for LF
        fig2 = px.scatter(
            data,
            y="Population requiring PC for LF",
            x="year",
            hover_name=data.index,
            log_x=False,
            color=data.index,
            size="Population requiring PC for LF",
            render_mode='svg',
            #text = "Population requiring PC for LF",
            #trendline="ewm",
            title="Population requiring PC from {} to {}".format(year[0], year[1]),
        )
        fig2.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})

        # third graph - pop actually treated for LF by year
        fig3 = px.area(
            data,
            x="year",
            y="Reported number of people treated",
            color=data.index,
            title="Number of people treated from {} to {}".format(year[0], year[1]),
            log_x=False,
        )
        fig3.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})
        # render second and third grpah side by side for comparison
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig2, use_container_width=True)
        col2.plotly_chart(fig3, use_container_width=True)

        # fourth graph - national coverage by year
        fig4 = px.line(
            data,
            y="National coverage",
            x="year",
            hover_name=data.index,
            log_x=False,
            color=data.index,
            title="National coverage from {} to {}".format(year[0], year[1]),
        )
        fig4.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})

        # fifth figure - geographic coverage by year
        fig5 = px.line(
            data,
            y="Geographical coverage",
            x="year",
            hover_name=data.index,
            log_x=True,
            color=data.index,
            title="Geographical coverage from {} to {}".format(year[0], year[1]),
        )
        fig5.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 100})

        # plot fourth and fifth figures side by side for comparison
        col1, col2 = st.columns(2)
        col1.plotly_chart(fig4, use_container_width=True)
        col2.plotly_chart(fig5, use_container_width=True)
        return


    def map(data):
        #group the data by country and mean and round to 2 decimal places
        groupby_country = data.groupby("country").mean().round(2)

        # let's read the Africa Json
        afro_json = f"custom.geo.json"
        afro_geo = gpd.read_file(afro_json)

        groupby_country['admin']= groupby_country.index

        #merge the grouped data with the geodata
        merged_geo= afro_geo.merge(groupby_country, on= 'admin')

        #initialize the basemap
        m = folium.Map(location=[7.188,21.093],zoom_start=2.7, tiles="OpenStreetMap")

        folium.Choropleth(geo_data= merged_geo,
                          data=merged_geo,
                          columns = ['admin',"National coverage"],
                          key_on= 'feature.properties.admin',
                          fill_color='RdYlGn',
                          fill_opacity=1,
                          line_opacity=0.3,
                          smooth_factor=0,
                          Highlight=True,
                          name="Bread",
                          legend_name="Average national coverage",
                          line_color='#0000').add_to(m)

        #adding hover functionality
        style_function = lambda x: {'fillcolor':'#00bfb3',
                                     'color':'#000000',
                                     'fillopacity':0.1,
                                     'weight':0.1}
        highlight_function = lambda x:{'fillcolor':'#000000',
                                       'color':'#000000',
                                       'fillopacity':0.5,
                                       'weight':0.1}

        high = folium.features.GeoJson(
            data = merged_geo,
            style_function = style_function,
            control=False,
            highlight_function=highlight_function,
            tooltip = folium.features.GeoJsonTooltip(
                fields=['admin','National coverage','Geographical coverage'],
                aliases=['Country','Average National Coverage','Average Geographic Coverage'],
                style= ("background-color:#00bfb3; color:#333333;font-family:arial;font-size: 12px; padding:10px;")
            ))

        m.add_child(high)

        return m


    def table(data):
        """this function is for creating a table containing all the average values"""
        # let's prepare the data and get the mean values
        groupby_country = data.drop(["year"], axis=1).groupby("country")
        table_df = groupby_country.mean().round(2)  # round off the decimals to two places
        # dislay the table
        col1, col2 = st.columns(2)
        st.markdown("*Average* values by country from {} to {}".format(year[0], year[1]))
        st.table(table_df)
        return


    # let's get the data
    df = get_data()

    # sidebar options
    with st.sidebar.form(key="fetch"):
        nation = st.multiselect(
            "Select countries", df.index.unique().tolist(), ["Mali", "Kenya"]
        )
        year = st.select_slider(
            "Select year", options=np.sort(df.year.unique()), value=(2009, 2019)
        )
        fetch = st.form_submit_button(label="Fetch")

    # sidebar info
    with st.sidebar.expander("Click to view Glossary"):
        st.markdown(
            """
        - **PC** - Preventive Chemotherapy
        - **PCT** - Preventive Chemotherapy and Transmission Control
        - **MDA** - Mass Drug Administration
        - **IU** - Implementation Unit
        - **Population requiring PC for LF**: total population living in all the endemic IUs and which require preventive chemotherapy (PC).
        - **Geographical coverage**: proportion (%) of endemic IUs covered by MDA.
        - **Programme (drug) coverage** : proportion (%) of individuals treated as per programme target (Total population of targeted IUs).
        - **National coverage**: proportion (%) of the population requiring PC for LF in the country that have been treated
        """
        )

    if fetch:
        # prepare the data for graphing
        data = df.loc[nation]
        data = data[data["year"].isin(range(year[0], year[-1]))]

        # display the map
        st.write(
            "Average program drug coverage rate from {} to {}".format(year[0], year[-1])
        )

        folium_static(map(data),width=940,height=500)

       #show the graphs
        graphs(data)

        #show the averages table
        table(data)
    else:
        st.warning('Please select from the parameters on the left 👈🏾  and press "Fetch"')
        st.info("If you don't select a country, you'll get blank graphs 🤪")
