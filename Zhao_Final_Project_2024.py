'''
"""Name: Michael Zhao
CS230: 2
Data: Massachusetts Car Crash 2017
Description:
This program runs different queries related to crashes that occurred within 
certain cities/towns, months, and hours. The program consists of maps, graphs,
and widgets that make the UI more accessible and easy to understand.
Streamlit cloud link: https://cs230project-mzhao.streamlit.app/
'''


import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk

def getdf(): #function loads the dataset from CSV file
    df = pd.read_csv("2017_Crashes_10000_sample.csv")
    return df

def bar_chart(df, start_month, end_month):
    st.title('Crashes by Hour in Massachusetts')
    df['CRASH_DATE_TEXT'] = [pd.to_datetime(date) for date in df['CRASH_DATE_TEXT']] 
    filtered_df = df[(df['CRASH_DATE_TEXT'] >= start_month) & (df['CRASH_DATE_TEXT'] <= end_month)]
    crashes_per_hour = filtered_df.groupby('CRASH_HOUR').size()
    if crashes_per_hour.empty:
        st.error("No crashes recorded for the selected date range. Please adjust the slider.")
        return None, None
    else:
        st.bar_chart(crashes_per_hour)
        return filtered_df, crashes_per_hour

def map_crashes(df, selected_city='Boston'): #multi parameter, Boston is a default value 
    st.title(f'Map of Crashes in {selected_city}')
    selected_crashes = df[df['CITY_TOWN_NAME'] == selected_city]
    center_lat = selected_crashes['LAT'].mean()
    center_lon = selected_crashes['LON'].mean()

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=selected_crashes,
        get_position=['LON', 'LAT'],
        get_radius=100,
        get_fill_color=[255, 0, 0],  # Red color for the markers
        pickable=True,
        tooltip={'html': '<b>Severity:</b> {CRASH_SEVERITY_DESCR}'}
    )
    map = pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(
            latitude=center_lat, 
            longitude=center_lon, 
            zoom=12,
            bearing=0,
            pitch=30
        ),
        map_style='dark'
    )
    st.pydeck_chart(map)

def crash_severity_chart(df):
    selected_cities = st.multiselect('Select City/Town', df['CITY_TOWN_NAME'].unique())
    selected_severity = st.multiselect('Select Severity Level', df['CRASH_SEVERITY_DESCR'].unique())
    if not selected_cities or not selected_severity:
        st.warning("Please select at least one city/town and severity level.")
    else:
        filtered_df = df[df['CITY_TOWN_NAME'].isin(selected_cities) & df['CRASH_SEVERITY_DESCR'].isin(selected_severity)]
        if filtered_df.empty:
            st.info("No data available for the selected options.")
        else:
            crashes_by_city_severity = filtered_df.groupby(['CITY_TOWN_NAME', 'CRASH_SEVERITY_DESCR']).size().unstack(fill_value=0)
            severity_order = ['Non-fatal injury', 'Fatal injury', 'Property damage only (none injured)', 'Not Reported']
            crashes_by_city_severity = crashes_by_city_severity.reindex(columns=severity_order, fill_value=0)
            crashes_by_city_severity.plot(kind='bar', figsize=(10, 6))
            plt.title('Crash Severity by City/Town')
            plt.xlabel('City/Town')
            plt.ylabel('Number of Crashes')
            plt.xticks(rotation=45)
            st.pyplot(plt)

def main():
    df = getdf()
    st.sidebar.title("Navigation")
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    home_button_clicked = st.sidebar.button("Home")
    crashes_by_hour_button_clicked = st.sidebar.button("Crashes by Hour")
    map_of_crashes_button_clicked = st.sidebar.button("Map of Crashes")
    crash_severity_button_clicked = st.sidebar.button("Crash Severity by City/Town")

    if home_button_clicked:
        st.session_state.page = "Home"
    elif crashes_by_hour_button_clicked:
        st.session_state.page = "Crashes by Hour"
    elif map_of_crashes_button_clicked:
        st.session_state.page = "Map of Crashes"
    elif crash_severity_button_clicked:
        st.session_state.page = "Crash Severity by City/Town"

    if st.session_state.page == "Home":
        st.title("Welcome to the Massachusetts Car Crashes Analysis App!")
        st.video("https://www.youtube.com/watch?v=tVm6OWbUTG0")
    elif st.session_state.page == "Crashes by Hour":
        display_crashes_by_hour(df)
    elif st.session_state.page == "Map of Crashes":
        display_map_of_crashes(df)
    elif st.session_state.page == "Crash Severity by City/Town":
        display_crash_severity(df)
        
def display_crashes_by_hour(df):
    st.title("Crashes by Hour")
    min_date, max_date = pd.to_datetime('2017-01-01'), pd.to_datetime('2017-12-31')
    start_month, end_month = st.select_slider(
        'Select Date Range',
        options=pd.date_range(min_date, max_date, freq='MS').strftime('%b %Y'),
        value=(min_date.strftime('%b %Y'), max_date.strftime('%b %Y'))
    )
    start_date = pd.to_datetime(start_month, format='%b %Y')
    end_date = pd.to_datetime(end_month, format='%b %Y')
    bar_chart(df, start_date, end_date)

def display_map_of_crashes(df):
    st.title("Map of Crashes")
    selected_city = st.selectbox('Select a City/Town', sorted(df['CITY_TOWN_NAME'].unique()))
    map_crashes(df, selected_city)

def display_crash_severity(df):
    st.title("Crash Severity by City/Town")
    crash_severity_chart(df)

main()
