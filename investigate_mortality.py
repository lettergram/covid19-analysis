import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

mortality_file = "data/Weekly_counts_of_deaths_by_jurisdiction_and_age_group.csv"

df = pd.read_csv(mortality_file)
df = df.reset_index()
print(df.columns)

week_series = df.where(df['Year']==2020).sort_values(by=['Week'])['Week']
current_week = week_series.last_valid_index()
print("Current Week", current_week)

start_week = week_series[week_series.first_valid_index()]
end_week = week_series[week_series.last_valid_index()]

print(start_week, end_week)

deaths_by_years = df.replace({'Under 25 years': ' 0-25 years', '85 years and older': '85+   years'}).where(df['Week'] >= start_week).where(df["Week"] <= end_week).groupby(['Year', 'Age Group']).sum().reset_index().drop(columns=['index', 'Week'])

deaths_by_group = pd.DataFrame(deaths_by_years, columns=['Age Group', 'Number of Deaths'])

print(deaths_by_group)

deaths_by_group.plot(x='Age Group', y='Number of Deaths', kind='bar')
plt.show()

print("\n\n--------------------------------------------\n\n")

pd.options.display.float_format = '{:20,.2f}'.format

print(deaths_by_years.groupby(['Year']).sum())
print("\n")

deaths_pre_2020 = deaths_by_years.where(deaths_by_years['Year']!=2020)
std_years = deaths_pre_2020.std(axis=0, skipna=True)

deaths_2019 = deaths_pre_2020.where(deaths_pre_2020['Year']==2019).groupby(['Year']).sum()['Number of Deaths'].mean()
deaths_2020 = deaths_by_years.where(deaths_by_years['Year']==2020).groupby(['Year']).sum()['Number of Deaths'].mean()

deaths_avg_std_pre_2020 = deaths_pre_2020.groupby(['Year']).sum()['Number of Deaths'].mean() + std_years['Number of Deaths']
deaths_avg_68_std_pre_2020 = deaths_pre_2020.groupby(['Year']).sum()['Number of Deaths'].mean() + 0.68*std_years['Number of Deaths']

print('2020 Deaths 1 STD above 5 year avg: {:8,.2f}'.format(deaths_2020 - deaths_avg_std_pre_2020))
print('2020 Deaths 0.68 STD above 5 year avg: {:8,.2f}'.format(deaths_2020 - deaths_avg_68_std_pre_2020))
print('2020 Deaths Over 2019: {:8,.2f}'.format(deaths_2020 - deaths_2019))
