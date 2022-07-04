#!/usr/bin/env python
# coding: utf-8

import pandas as pd 
import geopandas as gpd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# read shapefile 
gdf = gpd.read_file('District Boundaries - BNM Internship.shp')


# plot with colors, and right dimensions
gdf.plot(column='ADM2_EN', cmap=None, legend=None, figsize=(20, 20))

# gdf[["Shape_Leng", "Shape_Area", "ADM2_EN", "ADM2_PCODE", "ADM2_REF", "ADM2ALT1EN", "ADM2ALT2EN", "ADM1_EN", "ADM1_PCODE", "ADM0_EN", "ADM0_PCODE", "date", "validOn", "validTo", "geometry"]]
newgdf = gdf[["ADM2_EN", "ADM1_EN", "Shape_Leng", "Shape_Area", "ADM2_PCODE", "ADM1_PCODE",
        "date", "validOn","geometry"]]

newgdf.columns=["District", "State", "Shape_Leng", "Shape_Area", "District Postcode", "State Postcode", "date", "validOn","geometry"]
newgdf.plot(column='District', cmap=None, legend=None, figsize=(20, 20))

poi = gpd.read_file('POIs - BNM Internship.shp')
simple_poi = poi[["osm_id", "man_made", "geometry"]].copy()

@st.cache(suppress_st_warning=True)
def fit_district_coord_to_state():
    st.write("Cache miss: fit_district_coord_to_state() ran") 
    poi_temp = gpd.read_file(r'C:\Users\hp\Downloads\hotosm_mys_points_of_interest_points_shp/hotosm_mys_points_of_interest_points.shp')
    gdf_temp = gpd.read_file(r'C:\Users\hp\Downloads\mys_admb_unhcr_20210211_shp\mys_admbnda_adm2_unhcr_20210211.shp')
    test_state = []
    test_dist = []
    k = 1
    for i in poi_temp["geometry"]:
        j = 0
        while not i.within(gdf_temp.iat[j, 14]):
            j = j + 1
            if j >= 144: 
                break 
        if j >= 144: 
            test_dist.append("None")
            test_state.append("None")
        else: 
            test_dist.append(gdf_temp.iat[j, 2])
            test_state.append(gdf_temp.iat[j, 7]) 
    return(test_dist, test_state)

temp = fit_district_coord_to_state()
poi["District"]= temp[0]
poi["State"] = temp[1]

poi_none = poi[poi.District == "None"]
kv_gdf = gdf[gdf.ADM1_EN == "Selangor"]
kv_gdf = kv_gdf.append(gdf[(gdf.ADM1_EN == "W.P. Putrajaya")], ignore_index=True)
kv_gdf = kv_gdf.append(gdf[(gdf.ADM1_EN == "W.P. Kuala Lumpur")], ignore_index=True)
kv_gdf = kv_gdf.append(gdf[(gdf.ADM2_EN == "Seremban")], ignore_index=True)

# find missing POI within KV and assign correct District and State 
# ID = 2083151347, 5928578725 ; to be changed from None to Klang 
#poi[poi.osm_id == 2083151347] # index of 3848
#poi[poi.osm_id == 5928578725] # index of 32419
poi.at[3848, 'State'] = "Selangor"
poi.at[3848, 'District'] = "Klang"
poi.at[32419, 'State'] = "Selangor"
poi.at[32419, 'District'] = "Klang"

kv_poi = poi[poi.State == "Selangor"]
kv_poi = kv_poi.append(poi[poi.State == "W.P. Putrajaya"], ignore_index=True)
kv_poi = kv_poi.append(poi[poi.State == "W.P. Kuala Lumpur"], ignore_index=True)
kv_poi = kv_poi.append(poi[poi.District == "Seremban"], ignore_index=True)



districts = kv_gdf['ADM2_EN'].unique()

shop_1 = sorted(list(filter(None, kv_poi['shop'].unique())))
shop_2 = [name.title() for name in shop_1]
amenity_1 = sorted(list(filter(None, kv_poi['amenity'].unique())))
amenity_2 = [name.title() for name in amenity_1]
tourism_1 = sorted(list(filter(None, kv_poi['tourism'].unique())))
tourism_2 = [name.title() for name in tourism_1]
man_made_1 = sorted(list(filter(None, kv_poi['man_made'].unique())))
man_made_2 = [name.title() for name in man_made_1]
types = {
    'Shops' : shop_2, 
    'Amenity': amenity_2,
    'Tourism': tourism_2,
    'Man Made': man_made_2
}
category = sorted(['Shops', 'Amenity', 'Tourism', 'Man Made'])

MY_HASH = {
    pd.DataFrame: lambda _: None,
    str: lambda _: None,
    int: lambda _: None,
    list: lambda _: None,
    gpd.GeoDataFrame: lambda _: None
}
@st.cache(suppress_st_warning=True, hash_funcs=MY_HASH)
def build_df():
    st.write("build_df() ran")
    f_kv_poi = kv_poi.copy()
    f_districts = kv_gdf['ADM2_EN'].unique()
    f_shopc = []
    f_amenc = []
    f_tourc = []
    f_manmc = []
    f_coord = []
    f_shopt = pd.DataFrame()
    f_ament = pd.DataFrame()
    f_tourt = pd.DataFrame()
    f_manmt = pd.DataFrame()
    for d in f_districts: 
        summary = f_kv_poi[f_kv_poi.District == str(d)].count()
        f_shopc.append(summary[11])
        f_amenc.append(summary[6])
        f_tourc.append(summary[1])
        f_manmc.append(summary[13])
        f_shopt = pd.concat([f_shopt, f_kv_poi[f_kv_poi.District == str(d)].shop.value_counts()], axis=1)
        f_ament = pd.concat([f_ament, f_kv_poi[f_kv_poi.District == str(d)].amenity.value_counts()], axis=1)
        f_tourt = pd.concat([f_tourt, f_kv_poi[f_kv_poi.District == str(d)].tourism.value_counts()], axis=1)
        f_manmt = pd.concat([f_manmt, f_kv_poi[f_kv_poi.District == str(d)].man_made.value_counts()], axis=1)
    return(f_shopt, f_ament, f_tourt, f_manmt, f_shopc, f_amenc, f_tourc, f_manmc)

temp_store = build_df()
shopt = temp_store[0]
ament = temp_store[1]
tourt = temp_store[2]
manmt = temp_store[3]
shopc = temp_store[4]
amenc = temp_store[5]
tourc = temp_store[6]
manmc = temp_store[7]

shopt.columns = districts
ament.columns = districts 
tourt.columns = districts
manmt.columns = districts
total_df= pd.DataFrame()

total_df = total_df.set_axis(districts, axis=0)

total_df= pd.concat([total_df, shopt.transpose(), ament.transpose(), tourt.transpose(), manmt.transpose()], axis=1)
total_df['Amenity'] = amenc
total_df['Man Made'] = manmc
total_df['Shops'] = shopc
total_df['Tourism'] = tourc
total_df = total_df.fillna(0)
total_df = (100. * total_df / total_df.sum()).round(2)
temp = pd.DataFrame(kv_gdf.geometry).transpose()
temp.columns = districts
total_df = pd.concat([total_df, temp.transpose()], axis=1)

total_df['districts'] = districts
total_df.columns = [x.title() for x in total_df.columns]
total_gdf = gpd.GeoDataFrame(total_df, crs="EPSG:4326", geometry='Geometry')


st.title ("An Analysis of the Points of Interest (POIs) within Klang Valley ")
st.header("Definition of POIs")
st.write('We have four categories, "Amenity", "Man Made", "Shops", and "Tourism". And with each category, there are multiple types of POIs.')

# insert simple description of certain POIs measured. 

st.header("Visualization")
st.write('Please select the category and type to view the choropleth maps.')
# #    st.write("Select Category and Type")
# #    category_option = st.selectbox('Select Category', category)
# #type_option = st.selectbox('Select Type', types[str(category_option)])

#     # adding "select" as the first and default choice
#     category_option = st.selectbox('Select Category', options=['select']+list(types.keys()))
#     # display selectbox 2 if manufacturer is not "select"
#     if category_option != 'select':
#         type_option = st.selectbox('Select Type', options=types[category_option])
#     submitted = st.form_submit_button("Submit")
#     if submitted:
#         st.write('You selected ' + category_option + ' ' + type_option)

category_option = st.selectbox('Select Category', options=['Select Category']+list(types.keys()))

if category_option != 'Select Category':
    max_category = total_gdf.loc[total_gdf[str(category_option)].idxmax()][303]
    min_category = total_gdf.loc[total_gdf[str(category_option)].idxmin()][303]
    st.write(f"You have selected Category **{category_option}**")
    fig_category = go.Figure(px.choropleth_mapbox(total_gdf,
                   geojson=total_gdf.geometry,
                   locations=total_gdf.Districts,
                   color=str(category_option),
                   center={"lat": 3.140853, "lon": 101.693207},
                   mapbox_style="carto-positron",
                   zoom=7.5, 
                   color_continuous_scale = "blues", 
                   opacity=0.7,
                   labels={str(category_option): "%"}
                   ))

    fig_category.update_geos(fitbounds="locations", visible=False)
    fig_category.update_layout(title_text=f"Choropleth Map for {category_option} in Klang Valley Districts", 
        paper_bgcolor="#F0F2F6",
        margin={"r": 30, "t": 50, "l": 1, "b": 1})
    st.plotly_chart(fig_category)
    st.write(f"Max: {max_category}, Min: {min_category}")

    type_option = st.selectbox('Select Type', options=['Select Type']+types[category_option])

    if type_option != 'Select Type': #st.submit('Confirm')
        st.write(f"You have selected Type **{type_option}** for Category {category_option}.")
        max_type = total_gdf.loc[total_gdf[str(type_option)].idxmax()][303]
        min_type = total_gdf.loc[total_gdf[str(type_option)].idxmin()][303]

        hi = total_gdf[[str(type_option), 'Geometry', 'Districts']]
        fig_type = go.Figure(px.choropleth_mapbox(hi,
                           geojson=hi.Geometry,
                           locations=hi.Districts,
                           color=str(type_option),
                           center={"lat": 3.140853, "lon": 101.693207},
                           mapbox_style="carto-positron",
                           zoom=7.5, 
                           color_continuous_scale = "bupu", 
                           opacity=0.7, 
                           labels={str(type_option): "%"}
                           ))

        fig_type.update_geos(fitbounds="locations", visible=False)
        fig_type.update_layout(title_text=f"Choropleth Map for {type_option} ({category_option}) in Klang Valley Districts", 
            paper_bgcolor="#F0F2F6",
            margin={"r": 30, "t": 50, "l": 1, "b": 1})
        st.plotly_chart(fig_type)
        st.write(f"Max: {max_type}, Min: {min_type}")


st.header("Comments")
st.write('From comparing the district with the most and least respective POI, we can see that Kuala Lumpur is the district with the most POIs.')
st.write('We can also see that Kuala Selangor has the least POIs in general.')
st.write('However, we also can see that the information from these maps are not very useful.')

st.header('Improvements')
st.write('What the visualizations lack is a comparison with other factors. Adding information such as **population density**, **number of roads or rivers**, or other information that would allow a more in depth comparison would result in a better analysis of the POIs.')
st.write('This would allow us to correlate and understand why certain districts have more or less POIs than others.')
st.write('Another point of improvement could be allowing user to zoom in a specific district to see the precise locations of the respective POIs.')

st.header("Questions")
st.write('Which district has the most "Shops"? Which shops are most prevalent in Petaling? Does more people lead to more petrol stations?')

