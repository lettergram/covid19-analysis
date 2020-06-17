import os
import datetime
import numpy as np
import pandas as pd

# https://www.cdc.gov/nchs/pressroom/sosmap/flu_pneumonia_mortality/flu_pneumonia.htm
cdc_mortality_file = open('data/CDC_Influenza_Pneumonia_Mortality_by_State.csv', 'r')

deaths_per_year = {}
first = True
for row in cdc_mortality_file:
    if not first:
        # "YEAR","STATE","RATE","DEATHS","URL"
        r = row.replace('"', '').split(",")
        if r[0] not in deaths_per_year:
            deaths_per_year[r[0]] = {}
        if r[3]:
            deaths_per_year[r[0]][r[1]] =  int(r[3])
    else:
        first = False

state_avgs = {}
years = ['2018', '2017', '2016', '2015', '2014']
for state in deaths_per_year[years[0]].keys():
    print("")
    total = 0
    state_avgs[state] = []
    for year in years:
        print(state, year, deaths_per_year[year][state])
        state_avgs[state].append(deaths_per_year[year][state])
    avg = sum(state_avgs[state]) / len(state_avgs[state])
    print("AVERAGE: ", avg, "\n----------------\n")








    

# Triggered: https://www.reddit.com/r/Coronavirus/comments/h7s70f/by_the_end_of_this_weekend_more_americans_will/funn3ua?utm_source=share&utm_medium=web2x
# https://www.cdc.gov/nchs/nvss/vsrr/covid19/excess_deaths.htm
cdc_mortality_file = open(
    'data/Weekly_counts_of_deaths_by_jurisdiction_and_age_group.csv', 'r'
)

df = pd.read_csv(cdc_mortality_file)

print(df.columns.values)

select_columns = ['State Abbreviation', 'Year', 'Week',
                  'Week Ending Date', 'Number of Deaths']

# Current week of year 2020
#current_week = max(df.where(df['Year']==2020)['Week'].dropna())

#df_range = df.where(((df['Week'] >= 1) & (df['Week'] <= current_week)))
df_range = df.where(df['Type']=='Predicted (weighted)')

df_group_by_date = df_range[select_columns]

df_sum_pre_covid_week = df_group_by_date.where(df_group_by_date['Year']!=2020).groupby(
    ['State Abbreviation', 'Year', 'Week']
).sum()

df_avg_pre_covid_week = df_sum_pre_covid_week.groupby(['State Abbreviation', 'Week']).mean()
df_std_pre_covid_week = df_sum_pre_covid_week.groupby(['State Abbreviation', 'Week']).std()

# Add one STD
df_avg_std_pre_covid_week = df_avg_pre_covid_week + df_std_pre_covid_week 

df_covid_week = df_group_by_date.where(df_group_by_date['Year']==2020).groupby(
    ['State Abbreviation', 'Week']
).sum()

with pd.option_context('display.max_rows', None, 'display.max_columns', 3):
    print(df_avg_pre_covid_week)

print(len(df_covid_week['Number of Deaths'].values),
      len(df_avg_pre_covid_week['Number of Deaths'].values))

df_covid_week = df_covid_week.merge(df_avg_std_pre_covid_week,
                                    on=["State Abbreviation", "Week"],
                                    how='left')

df_covid_week = df_covid_week.reset_index(level=['State Abbreviation', 'Week'])
df_covid_week = df_covid_week.rename(columns={
    "Number of Deaths_x": "Deaths 2020",
    "Number of Deaths_y": "Deaths (5yr Avg)",
    "State Abbreviation": 'State'
})

print(df_covid_week.columns)

df_covid_week = df_covid_week.drop(['Year'], axis=1)

df_covid_week['diff'] = (df_covid_week['Deaths 2020'] - df_covid_week['Deaths (5yr Avg)']).values


with pd.option_context('display.max_rows', None, 'display.max_columns', 20):
    print(df_covid_week.to_string())
print(df_covid_week.columns)

df_covid_week['normalized_diff'] = np.nan

def normalize(x, max_val, min_val):
    return max(x / max_val, 0)

for state in df_covid_week['State'].unique():
    state_max = df_covid_week.where(df_covid_week['State']==state)['diff'].max()
    state_min = df_covid_week.where(df_covid_week['State']==state)['diff'].min()
    
    vec = df_covid_week['diff'].where(df_covid_week['State']==state).apply(normalize, args=(state_max,state_min)).dropna().values

    df_covid_week.loc[df_covid_week['State']==state, 'normalized_diff'] = vec


with pd.option_context('display.max_rows', None, 'display.max_columns', 20):
    print(df_covid_week.to_string())
print(df_covid_week.columns)
