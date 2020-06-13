import os
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

# Week 22 is current
df_range = df.where(((df['Week'] >= 1) & (df['Week'] <= 22)))
print(df_range)

df_range = df_range.groupby(['State Abbreviation', 'Year', 'Week']).sum()
print(df_range.to_string())

df_range = df_range.groupby(['State Abbreviation', 'Year']).sum()
print(df_range.to_string())

deaths_per_state = {}
first = True
for row in cdc_mortality_file:
    if not first:
        # 0-Jurisdiction, 1-Week Ending Date, 2-State Abbreviation, 3-Year,        
        # 4-Week, 5-Age Group, 6-Number of Deaths
        r = row.replace('"', '').split(",")
        state = r[2]
        year = int(r[3])
        week = int(r[4])
        deaths = int(r[6])
        
        if state not in deaths_per_state:
            deaths_per_state[state] = {}
            
        if year not in deaths_per_state[state]:
            deaths_per_state[state][year] = {}
            
        deaths_per_state[state][year][week] = deaths
        
        print(state, year, week, deaths)
    else:
        first = False

for state in deaths_per_state:
    for year in deaths_per_state[state]:
        for week in deaths_per_state[state][year]:
            print(state, year, deaths_per_state[state][year][wee+k])

for state in deaths_per_state:
    for year in deaths_per_state[state]:
        sum_year = 0
        for week in range(1, len(deaths_per_state[state][2020])):
            sum_year += deaths_per_state[state][year][week]
        print(state, year, sum_year)
        
