import numpy as np

def medal_tally(df):
    # New dataframe with medal counts
    medal_tally = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    medal_tally = medal_tally.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold', ascending=False).reset_index()
    medal_tally['Total'] = medal_tally['Gold'] + medal_tally['Silver'] + medal_tally['Bronze']
    return medal_tally

def country_year_list(df):
    # This functions returns list of years when olympic was held and list of countries participated till date
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def fetch_medal_tally(df, years, country):
    medals = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])
    flag = 0
    if years == 'Overall' and country == 'Overall':
        temp_medal = medals
    elif years == 'Overall' and country != 'Overall':
        flag = 1
        temp_medal = medals[medals['region'] == country]
    elif years != 'overall' and country == 'Overall':
        temp_medal = medals[medals['Year'] == int(years)]
    else:
        temp_medal = medals[(medals['Year'] == int(years)) & (medals['region'] == country)]

    if flag == 1:
        x = temp_medal.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Year',
                                                                                       ascending=True).reset_index()
    else:
        x = temp_medal.groupby('region').sum()[['Gold', 'Silver', 'Bronze']].sort_values('Gold',
                                                                                         ascending=False).reset_index()
    x['Total'] = x['Gold'] + x['Silver'] + x['Bronze']
    return x

def data_over_time(df, col):
    data_over_time = df.drop_duplicates(['Year', col])['Year'].value_counts().reset_index().sort_values('Year')
    return data_over_time


def most_successful(df, sport, event, sex):
    tempdf = df.dropna(subset=['Medal'])
    if sport != 'Overall':
        tempdf = tempdf[tempdf['Sport'] == sport]
    if sex != 'Overall':
        tempdf = tempdf[tempdf['Sex'] == sex]
    if event != 'Overall':
        tempdf = tempdf[tempdf['Event'] == event]
    # count number of medals per athlete, top 15 only
    x = tempdf['Name'].value_counts().reset_index().head(15)
    # merge x on df
    x = x.merge(df, left_on='Name', right_on='Name', how='left')
    x = x.rename(columns={'count': 'Medals'})
    # take out required columns from full df
    x = x[['Name', 'Sex', 'Sport', 'Event', 'Medals', 'region']]
    # removing duplicate athlete names from x and re_indexing
    x = x.drop_duplicates('Name').reset_index().drop(['index'], axis=1)
    return x

def yearwise_medal_tally(df, country):
    a = df.dropna(subset=['Medal'])
    a.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)
    a = a[a['region'] == country]
    final_df = a.groupby('Year').count()['Medal'].reset_index()
    return final_df

def country_heatmap(df, country):
    a = df.dropna(subset=['Medal'])
    a.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)
    a = a[a['region'] == country]
    # pt is pivot table
    pt = a.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt

def most_successful_in_country(df, country, sport, sex):
    tempdf = df.dropna(subset=['Medal'])
    tempdf = tempdf[tempdf['region'] == country]
    if sport != 'Overall':
        tempdf = tempdf[tempdf['Sport'] == sport]
    if sex != 'Overall':
        tempdf = tempdf[tempdf['Sex'] == sex]
    # count number of medals per athlete, top 15 only
    x = tempdf['Name'].value_counts().reset_index().head(10)
    # merge x on df
    x = x.merge(df, left_on='Name', right_on='Name', how='left')
    # take out required columns from full df
    x = x[['Name', 'count', 'Sport','Sex', 'Event']]
    # removing duplicate athlete names from x and re_indexing
    x = x.drop_duplicates('Name').reset_index().drop(['index'], axis=1)
    x = x.rename(columns={'count':'Medals'})
    return x

def weight_v_height(df,sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    #athlete_df['Medal'].fillna('No Medal', inplace=True)
    athlete_df['Medal'].dropna()
    if sport != 'Overall':
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        return temp_df
    else:
        return athlete_df

def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()
    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)
    return final