import streamlit as st
import pandas as pd
import numpy as np
import preprocessor, helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import scipy

df = pd.read_csv('athlete_events.csv')
region = pd.read_csv('noc_regions.csv')

st. set_page_config(layout="wide")
st.sidebar.title('Olympics Analysis')
st.sidebar.image("https://cdn.pixabay.com/photo/2021/06/06/04/15/olympic-games-6314253_1280.jpg")
df = preprocessor.preprocess(df, region)
menu = st.sidebar.radio(
    'Select an Option',
    ('Medal Tally', 'Overall Analysis', 'Country-Wise', 'Athlete wise')
)

if menu == 'Medal Tally':
    years, country = helper.country_year_list(df)
    selected_year = st.sidebar.selectbox('Select year', years)
    selected_country = st.sidebar.selectbox('Select country', country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
    if selected_year=='Overall' and selected_country=='Overall':
        st.title('Overall Medal Tally')
    elif selected_year=='Overall' and selected_country!='Overall':
        st.title(selected_country + '\'s Performance')
    elif selected_year!='Overall' and selected_country=='Overall':
        st.title('Medal Tally of year ' + str(selected_year))
    else:
        st.title(selected_country + '\'s Performance in ' + str(selected_year))

    st.dataframe(medal_tally, 1000, 500)

if menu == 'Overall Analysis':
    # calculating number of times olympics held
    # -1 because, 1906 olympic data is in the df but it is not considered
    editions = df['Year'].unique().shape[0] - 1
    # No. of cities
    cities = df['City'].unique().shape[0]
    # No. of sports
    sports = df['Sport'].unique().shape[0]
    # No. of events
    events = df['Event'].unique().shape[0]
    # No. of athletes
    athletes = df['Name'].unique().shape[0]
    # Participating nations
    nations = df['region'].unique().shape[0]

    st.title("Top Stats")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Athletes")
        st.title(athletes)
    with col3:
        st.header("Countries")
        st.title(nations)

    nations_over_time = helper.data_over_time(df, 'region')
    fig = px.line(nations_over_time, x='Year', y='count')
    st.title("Participating nations over the years")
    st.plotly_chart(fig)

    events_over_time = helper.data_over_time(df, 'Event')
    fig = px.line(events_over_time, x='Year', y='count')
    st.title("Events held over the years")
    st.plotly_chart(fig)

    athletes_over_time = helper.data_over_time(df, 'Name')
    fig = px.line(athletes_over_time, x='Year', y='count')
    st.title("Athletes participation over the years")
    st.plotly_chart(fig)

    # Heatmap
    st.title('Number of events in each sport')
    fig, ax = plt.subplots(figsize=(15,15))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(x.pivot_table(index='Sport', columns='Year', values='Event', aggfunc='count').fillna(0), annot=True)
    st.pyplot(fig)

    # Display most successful athletes of respective sport
    st.title('Most successful athletes')
    # creating a list with unique sport values
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    selected_sport = st.selectbox('Select a sport', sport_list)
    # creating a list with unique event values
    event_list = df[df['Sport']==selected_sport]['Event'].unique().tolist()
    event_list.sort()
    event_list.insert(0, 'Overall')
    selected_event = st.selectbox('Select a event', event_list)
    # creating selectbox for choosing gender of athlete
    selected_sex = st.selectbox('Select sex of athlete', ['Overall', 'M', 'F'])
    # Function calling
    x = helper.most_successful(df, selected_sport, selected_event, selected_sex)
    st.table(x)

if menu == 'Country-Wise':
    st.title('Country-wise Analysis')

    # creating a list of countries to choose from
    country_list = np.unique(df['region'].dropna().values).tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox("Select country", country_list)

    # Line graph for each country's medal tally
    country_df = helper.yearwise_medal_tally(df, selected_country)
    fig = px.line(country_df, x='Year', y='Medal')
    st.title("Medals won by "+selected_country+' over years')
    st.plotly_chart(fig)

    # Heatmap
    pt = helper.country_heatmap(df, selected_country)
    if pt.empty == False:  # condition to avoid error if the country has no medals
        st.title(selected_country + '\'s performance in each sport')
        fig, ax = plt.subplots(figsize=(15, 15))
        ax = sns.heatmap(pt, annot=True)
        st.pyplot(fig)

        st.title('Most successful athletes in ' + selected_country)
        # creating a list with unique sport values
        sport_list = df['Sport'].unique().tolist()
        sport_list.sort()
        sport_list.insert(0, 'Overall')
        selected_sport = st.selectbox('Select a sport', sport_list)
        # creating selectbox for choosing gender of athlete
        selected_sex = st.selectbox('Select sex of athlete', ['Overall', 'M', 'F'])
        top10_df = helper.most_successful_in_country(df, selected_country, selected_sport, selected_sex)
        st.table(top10_df)

if menu == 'Athlete wise':

    # Age distribution graph
    st.title('Age distribution of athletes')
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()
    fig = ff.create_distplot([x1, x2, x3, x4],
                             ['Overall Age distribution', 'Gold medalist', 'Silver medalist', 'Bronze medalist'],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

    # Male vs Female participation over the years
    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

    #Scatter plot
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')
    st.title('Height Vs Weight chart of medal winning athletes')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    fig, ax = plt.subplots()
    ax = sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=30)
    st.pyplot(fig)