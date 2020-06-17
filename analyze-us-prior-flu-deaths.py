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

select_columns = ['State Abbreviation', 'Year', 'Week',
                  'Week Ending Date', 'Number of Deaths']

df_range = df.where(df['Type']=='Predicted (weighted)')

df_group_by_date = df_range[select_columns]

# Calculate prior years statistics (2014-2019)
df_sum_pre_covid_week = df_group_by_date.where(df_group_by_date['Year']!=2020).groupby(
    ['State Abbreviation', 'Year', 'Week']
).sum()
df_avg_pre_covid_week = df_sum_pre_covid_week.groupby(['State Abbreviation', 'Week']).mean()
df_std_pre_covid_week = df_sum_pre_covid_week.groupby(['State Abbreviation', 'Week']).std()

# Add one STD
df_avg_std_pre_covid_week = df_avg_pre_covid_week + df_std_pre_covid_week 

df_covid_week = df_group_by_date.where(df_group_by_date['Year']==2020).groupby(
    ['State Abbreviation', 'Week', 'Week Ending Date']
).sum()

# Join prior with 2020 stats
df_covid_week = df_covid_week.merge(df_avg_std_pre_covid_week,
                                    on=["State Abbreviation", "Week"], how='left')

# Add back end the specific date ending the week
df_covid_week['Week Ending Date'] = df_group_by_date.where(df_group_by_date['Year']==2020).groupby(
    ['State Abbreviation', 'Week', 'Week Ending Date']
).sum().reset_index(level=['Week Ending Date'])['Week Ending Date']

# Rename columns for ease of use / understanding
df_covid_week = df_covid_week.reset_index(level=['State Abbreviation', 'Week'])
df_covid_week = df_covid_week.rename(columns={
    "Number of Deaths_x": "Deaths 2020",
    "Number of Deaths_y": "Deaths (5yr Avg)",
    "State Abbreviation": 'State'
})

# Drop year as it's no longer necessary, we know the current year in labels
df_covid_week = df_covid_week.drop(['Year'], axis=1)

# Find difference between the average + 1 std
df_covid_week['diff'] = (df_covid_week['Deaths 2020'] - df_covid_week['Deaths (5yr Avg)']).values

df_covid_week['normalized_diff'] = np.nan

# Function to noramlize 0 to 1, if less than 0 just set to zero
def normalize(x, max_val, min_val):
    return max(x / max_val, 0)

# For each state calculate the normal
for state in df_covid_week['State'].unique():
    state_max = df_covid_week.where(df_covid_week['State']==state)['diff'].max()
    state_min = df_covid_week.where(df_covid_week['State']==state)['diff'].min()
    
    vec = df_covid_week['diff'].where(df_covid_week['State']==state).apply(normalize, args=(state_max,state_min)).dropna().values

    df_covid_week.loc[df_covid_week['State']==state, 'normalized_diff'] = vec

state_deaths = {}
for state in df_covid_week['State'].unique():
    normalized = df_covid_week.where(df_covid_week['State']==state)['normalized_diff'].dropna().values
    week_ends = df_covid_week.where(df_covid_week['State']==state)['Week Ending Date'].dropna().values
    deaths_above_1_std = round(
        df_covid_week.where(df_covid_week['State']==state)['diff'].sum(),
        3
    )
    deaths =  df_covid_week.where(df_covid_week['State']==state)['Deaths 2020'].sum()    
    state_deaths[state] = {
        'deaths': deaths, 
        'deaths_above_1_std': deaths_above_1_std,
        'weeks_normalized': normalized.tolist(),
        'weeks_end': week_ends
    }
    
# Print the table out
with pd.option_context('display.max_rows', None, 'display.max_columns', 20):
    print(df_covid_week.to_string())
    
print('US Deaths',
      round(df_covid_week.where(df_covid_week['State']=='US')['diff'].sum(), 3))

print(state_deaths['IL'])

print(df_covid_week.where(df_covid_week['State']=='US')['normalized_diff'].dropna().values)

print(df_covid_week)
