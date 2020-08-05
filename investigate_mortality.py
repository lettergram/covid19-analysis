import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

mortality_file = "data/Weekly_counts_of_deaths_by_jurisdiction_and_age_group.csv"

df = pd.read_csv(mortality_file)

print(df.columns)

week_series = df.where(df['Year']==2020).sort_values(by=['Week'])['Week']
current_week = week_series.last_valid_index()
print("Current Week", current_week)

start_week = week_series[week_series.first_valid_index()]
end_week = week_series[week_series.last_valid_index()]

print(start_week, end_week)

deaths_by_years = df.replace({'Under 25 years': ' 0-25 years', '85 years and older': '85+   years'}).where(df['Week'] >= start_week).where(df["Week"] <= end_week).groupby(['Year', 'Age Group']).sum()

for key in deaths_by_years: # .index:
    print(key)
                    
print(deaths_by_years)

deaths_by_group = pd.DataFrame(deaths_by_years, columns=['Age Group', 'Number of Deaths'])
deaths_by_group.plot(x='Age Group', y='Number of Deaths', kind='line')
plt.show()
