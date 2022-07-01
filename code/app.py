from msilib.schema import CheckBox
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
#st.title('Hello World') #if i put ! infront of world or if make changes in the code---streamlit will not build the website from strat but it intelligently change the code and update with streamlit is very fast
#st.markdown('My First Dashboard')
#build the titlle
st.title('Motor Vehicle Collision in New York City')
st.markdown('This application is streamlit dashboard to analyze motor vehicle collision in NYC')
file_path='D:\cv projects\Data Science web/Motor_Vehicle_Collisions_Crashes.csv'
#@st.cache(persist=True) #we dont want to reload the data all the time and do compution all the time
def load_data(nrows):
    data=pd.read_csv(file_path, nrows=nrows, parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase= lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
    return data
data=load_data(10000)
original_data=data

st.header('Where are the most people injured in NYC?')
injured_people= st.slider("Number of persons injured in vehicle collision", 0,19)
st.map(data.query('injured_persons >= @injured_people')[['latitude','longitude']].dropna(how='any'))

st.header('How many collision occur during a given time of day')
hour=st.slider('Hour to look at',0,23)
data=data[data['date/time'].dt.hour==hour]

st.markdown("Vehicle collisions between %i:00 and %i:00 " %(hour,(hour+1)%24))
midpoint= (np.average(data['latitude']), np.average(data['longitude']))

st.write(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state={
        'latitude':midpoint[0],
        'longitude':midpoint[1],
        'zoom':11,
        'pitch':50.
    },

    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time','latitude', 'longitude']],
        get_position=['longitude','latitude'],
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0,1000],
        ),
    ],
))

st.subheader("Breakdown by minute between  %i:00 and %i:00 " %(hour,(hour+1)%24))
filtered = data[
    (data['date/time'].dt.hour>=hour) & (data['date/time'].dt.hour<(hour+1))
]

hist=np.histogram(filtered['date/time'].dt.minute, bins=60,range=(0,60))[0]
chart_data=pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data , x='minute', y='crashes', hover_data=['minute','crashes'], height=400)
st.write(fig)

st.header('Top 5 dangerous streets by affected type')
select = st.selectbox('Afftected type of people',['Pedestrians', 'Cyclists','Motorists'])

if select=='Pedestrians':
    st.write(original_data.query('injured_pedestrians>=1')[['on_street_name','injured_pedestrians']].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])
elif select=='Cyclist':
    st.write(original_data.query('injured_cyclists>=1')[['on_street_name','injured_cyclists']].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])
else:
    st.write(original_data.query('injured_motorists>=1')[['on_street_name','injured_motorists']].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])



if st.checkbox('Show Raw Data', False):
    st.subheader("Raw Data")
    st.write(data)

