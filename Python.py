import streamlit as st
import pandas as pd
import altair as alt

import io
import numpy as np
import plotly_express as px

import matplotlib.pyplot as plt
import seaborn as sns


## Data ----------------------------------------------------------------------------------------
df = pd.read_csv('/Users/annaliisadistefano/Desktop/Erasmus/PythonDS/country_vaccinations 2.csv')
dfpop = pd.read_csv('/Users/annaliisadistefano/Desktop/Erasmus/PythonDS/population_by_country_2020.csv')
dfcases = pd.read_csv('/Users/annaliisadistefano/Desktop/Erasmus/PythonDS/owid-covid-data.csv')

df = df[df['iso_code'].notna()]

df1 = df[['country','iso_code','date','total_vaccinations','people_vaccinated','daily_vaccinations']]

data = df1[['country', 'daily_vaccinations']].groupby('country').count()

countries_list = data[data.daily_vaccinations < 10].index
df1 = df1[~df1['country'].isin(countries_list)]

dfpop.rename(columns={"Country (or dependency)":"country","Population (2020)":"population"}, inplace=True)
dfpop["country"].replace({"Czech Republic (Czechia)": "Czechia", }, inplace=True)

dfpop1 = dfpop[['country','population']]

# Merge vaccination data with population data
result = pd.merge(df1, dfpop1,how="left",on=['country'])
result['country'].nunique()
len(result) - result['population'].count()
result.isna().sum()

result['percentage_total_vaccinations'] = (100*result['total_vaccinations']) /  (2* result['population']) 
result['percentage_people_vaccinated'] =  (100*result['people_vaccinated']) / result['population'] 
result['vaccination_rate'] =  (100*result['daily_vaccinations']) / result['population'] 

# Cleaning cases database
dfcases1 = dfcases.loc[dfcases['date'] > '2020-12-01']

dfcases2 = dfcases1[['date','location','new_cases_smoothed','new_deaths_smoothed','total_cases']]
dfcases2.rename(columns = {'location':'country'}, inplace = True)

totcases = dfcases1.loc[ dfcases1['date'] == '2021-02-13', ['location', 'total_cases']]
totcases = totcases.drop(2122)
totcases = totcases.drop(30425)


# Merge the covid cases data to vaccinations and population
result3 = pd.merge(result, dfcases2,how="left", left_on=['country', 'date'], right_on=['country', 'date'])

result3.sort_values(by = 'date')


## Data visualisation ---------------------------------------------------------------------------
histdata = result.loc[result['date'] == '2021-01-15'] 
histdata['country'].nunique()

histdata.vaccination_rate.plot(kind='hist', bins=80, title = 'Vaccination rate histogram over all countries and time')

result.loc[result['country'] == 'Germany'][['daily_vaccinations','date']].reset_index().plot(x='date', y='daily_vaccinations', title = 'Germany Vaccinations Timeseries')

# Time series of daily vaccinations for European countries
timeseries_ger = result.loc[result['country'] == 'Germany'][['daily_vaccinations','date']]
timeseries_ger.columns = ['Germany.','date']

timeseries_frn = result.loc[result['country'] == 'France'][['daily_vaccinations','date']]
timeseries_frn.columns = ['France.','date']

timeseries_uk = result.loc[result['country'] == 'United Kingdom'][['daily_vaccinations','date']]
timeseries_uk.columns = ['United Kingdom.','date']

timeseries_itl = result.loc[result['country'] == 'Italy'][['daily_vaccinations','date']]
timeseries_itl.columns = ['Italy.','date']

timeseries_sp = result.loc[result['country'] == 'Spain'][['daily_vaccinations','date']]
timeseries_sp.columns = ['Spain.','date']

timeseries_pl = result.loc[result['country'] == 'Poland'][['daily_vaccinations','date']]
timeseries_pl.columns = ['Poland.','date']

timeseries_rm = result.loc[result['country'] == 'Romania'][['daily_vaccinations','date']]
timeseries_rm.columns = ['Romania.','date']

timeseries_nl = result.loc[result['country'] == 'Netherlands'][['daily_vaccinations','date']]
timeseries_nl.columns = ['Netherlands.','date']

timeseries = timeseries_ger.merge(timeseries_frn, on="date", how = 'outer') 
timeseries = timeseries.merge(timeseries_itl, on="date", how = 'outer') 
timeseries = timeseries.merge(timeseries_uk, on="date", how = 'outer')
timeseries = timeseries.merge(timeseries_sp, on="date", how = 'outer')
timeseries = timeseries.merge(timeseries_pl, on="date", how = 'outer')
timeseries = timeseries.merge(timeseries_rm, on="date", how = 'outer')
timeseries = timeseries.merge(timeseries_nl, on="date", how = 'outer').head(45)

timeseries.reset_index().plot(x='date', y=['Germany.', 'France.', 'Italy.', 'United Kingdom.', 'Netherlands.'], title = 'European Vaccination Timeseries')

# Time series of cumulative vaccinations in europe
timeseries_c = timeseries
timeseries_c['Germany'] = timeseries['Germany.'].cumsum()
timeseries_c['France'] = timeseries['France.'].cumsum()
timeseries_c['Italy'] = timeseries['Italy.'].cumsum()
timeseries_c['United Kingdom'] = timeseries['United Kingdom.'].cumsum()
timeseries_c['Spain'] = timeseries['Spain.'].cumsum()
timeseries_c['Poland'] = timeseries['Poland.'].cumsum()
timeseries_c['Romania'] = timeseries['Romania.'].cumsum()
timeseries_c['Netherlands'] = timeseries['Netherlands.'].cumsum()


# Scatterplot US
scatter_US = result3.loc[result['country'] == 'United States']
scatter_US.plot(x= 'new_cases_smoothed', y = 'new_deaths_smoothed', kind = 'scatter', title = 'US correlation Vaccinations/Cases')

# Pairplot UK
scatter_uk = result3.loc[result3['country'] == 'United Kingdom']
scatter_uk = scatter_uk.drop(columns=['iso_code','date','country','percentage_people_vaccinated','percentage_total_vaccinations','population','vaccination_rate'])
#sns.pairplot(scatter_uk)

# Pairplot (log) Israel
scatter_israel = result3.loc[result3['country'] == 'Israel']
scatter_israel = scatter_israel.drop(columns=['iso_code','date','country','percentage_people_vaccinated','percentage_total_vaccinations','population','vaccination_rate'])
#sns.pairplot((np.log(scatter_israel)))

# Create dataframe with three countries
scatter3countries = result3.loc[result3['country'].isin(['United Kingdom', 'Israel','United States'])].drop(columns=['iso_code','date','percentage_people_vaccinated','percentage_total_vaccinations','population','vaccination_rate'])

# Pairplot with three countries
#sns.pairplot(scatter3countries, hue='country')

# One scatter with three countries
#px.scatter(scatter3countries, x='new_cases_smoothed', y='new_deaths_smoothed', color='country')


## Interactive graphs ---------------------------------------------------------------------------

# Choropleth
map_series = result.groupby(['country'])['vaccination_rate'].sum()
map_final = map_series.to_frame()
map_final['country'] = map_series.index
map_final.rename(columns = {'vaccination_rate':'Progress'}, inplace = True)
fig = px.choropleth(map_final, locations='country', color='Progress', locationmode='country names',  range_color=[0, 7], title =  'Vaccination Progress World Map (percentage of population)')
#fig.show()

# Bubble graph with total covid cases - create data frame cases_final line 42

fig2 = px.scatter_geo(totcases, locations="location", 
                      #color="Progress",
                     hover_name="location", size="total_cases", locationmode='country names', size_max=55, 
                      #range_color=[0, 8], 
                     projection="natural earth", title = 'Total Covid Cases per Country')
#fig2.show()

# Timeseries of daily vaccinations
fig3 = px.line(timeseries, x='date', y=["Germany.", "France.", "Italy.", "United Kingdom.", "Netherlands." ], 
               labels={
                     "date": "Date(day)",
                     "value": "Daily vaccinations",
                     "variable": "Country:"
                 }, title = "Time Series of Daily Vaccinations in Europe")
#fig3.show()

# Timeseries of cumulative vaccinations
fig4 = px.line(timeseries_c, x='date', y=["Germany", "France", "Italy", "United Kingdom", "Spain", "Poland", "Romania", "Netherlands" ], 
               labels={
                     "date": "Date(day)",
                     "value": "Cumulative vaccinations",
                     "variable": "Country:"
                 }, title = "Time Series of Cumulative Vaccinations in Europe")

## Streamlit -----------------------------------------------------------------------------------
st.title("Covid-19 Vaccination Progress")
st.text("Hello whatsup guys its working")


st.plotly_chart(fig)

st.plotly_chart(fig2)

st.plotly_chart(fig3)

st.plotly_chart(fig4)

# change URL










