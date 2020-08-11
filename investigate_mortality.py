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

us_index = df[df['State Abbreviation'] == 'US'].index
df.drop(us_index, inplace=True)

deaths_by_years = df.replace(
    {'Under 25 years': ' 0-25 years', '85 years and older': '85+   years'}).where(
        df['Week'] >= start_week
    )

pd.set_option('display.max_rows', None)
print(deaths_by_years.where(df['Year']==2019).dropna(how='all')[
    ['State Abbreviation', 'Week', 'Number of Deaths']])
print("\n-------------------\n")
print(deaths_by_years.where(df['Year']==2019).dropna(how='all')[['State Abbreviation', 'Week', 'Number of Deaths']])
print("\n-------------------\n")
print(deaths_by_years.where(df['Year']==2019).dropna(how='all').groupby(['State Abbreviation'])[['Number of Deaths']])
print("\n-------------------\n")
print(deaths_by_years.where(df['Year']==2019).where(df['Week']==1.0).dropna(how='all')[['State Abbreviation', 'Jurisdiction', 'Age Group', 'Week', 'Number of Deaths']])
print("\n-------------------\n")
print(deaths_by_years.where(df['Year']==2019).dropna(how='all').groupby(['Week']).sum()[
    ['Number of Deaths']])
print("\n-------------------\n")

deaths_by_years = deaths_by_years.where(
        df["Week"] <= end_week
    ).groupby(
        ['Year', 'Age Group']
    ).sum().reset_index().drop(columns=['index', 'Week'])

print(deaths_by_years)
print("\n-------------------\n")
print()

deaths_by_group = pd.DataFrame(deaths_by_years,
                               columns=['Year', 'Age Group', 'Number of Deaths'])

print(deaths_by_group)


# deaths_by_group.plot(x='Age Group', columns=['Year', 'Number of Deaths'], kind='bar')
# deaths_by_group.set_index(['Age Group'], inplace=True)


fig, ax = plt.subplots(figsize=(12, 8))
years = deaths_by_group['Year'].unique().astype(int)
age_groups = deaths_by_group['Age Group'].unique()
X = np.arange(len(age_groups))
bar_width = 0.15

plt.set_cmap('Oranges_r')

count = 1
for year in years:
    ax.bar(X+count*bar_width,
           deaths_by_group.loc[
               deaths_by_group['Year']==year, 'Number of Deaths'], 
           width=bar_width, label=str(year))
    count += 1

# Fix the x-axes.
ax.set_xticks(X + 3.5*bar_width)
ax.set_xticklabels(deaths_by_group['Age Group'].values)

# Format graph
ax.legend()

ax.set_xlabel('Deaths')
ax.set_ylabel('Age Groups')
ax.set_title('Deaths per Age Group')

ax.yaxis.grid(True, color='#EEEEEE')
ax.xaxis.grid(False)
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=False)

fig.tight_layout()
plt.show()



print("\n\n--------------------------------------------\n\n")

pd.options.display.float_format = '{:20,.2f}'.format

deaths_pre_2020 = deaths_by_years.where(deaths_by_years['Year']!=2020).dropna(how='all')
deaths_pre_2020_yr = deaths_pre_2020.groupby('Year').sum()

deaths_pre_2020_yr = deaths_pre_2020_yr.reset_index()

from sklearn.linear_model import LinearRegression
model = LinearRegression()

X = [[int(i)] for i in deaths_pre_2020_yr['Year'].values.tolist()]
Y = [[int(i)] for i in deaths_pre_2020_yr['Number of Deaths'].values.tolist()]

model.fit(X, Y)

std_years = deaths_pre_2020.std(axis=0, skipna=True)['Number of Deaths']
predicted_deaths = model.predict([[2020]])[0][0]

print('Model Score (R^2):', model.score(X, Y))
print("Year, Pred., Real")
for i in range(len(X)):
    print(int(X[i][0]),
          int(model.predict([[X[i][0]]])),
          int(deaths_pre_2020_yr['Number of Deaths'].values[i]))
    
print('\nPredicted 2020 Deaths:', predicted_deaths)
print('Confirmed 2020 Deaths:', deaths_by_years.where(
    deaths_by_years['Year']==2020).groupby(['Year']).sum()['Number of Deaths'].values[0],
      '\n')

deaths_2019 = deaths_pre_2020.where(
    deaths_pre_2020['Year']==2019).groupby(
        ['Year']
    ).sum()['Number of Deaths'].mean()

deaths_2020 = deaths_by_years.where(
    deaths_by_years['Year']==2020).groupby(
        ['Year']
    ).sum()['Number of Deaths'].mean()

deaths_avg_std_pre_2020 = deaths_pre_2020.groupby(
    ['Year']).sum()['Number of Deaths'].mean() + std_years

deaths_avg_68_std_pre_2020 = deaths_pre_2020.groupby(
    ['Year']).sum()['Number of Deaths'].mean() + 0.68 * std_years



print('2020 Deaths 1 STD above 5 year avg: {:8,.2f}'.format(
    deaths_2020 - deaths_avg_std_pre_2020))

print('2020 Deaths 0.68 STD above 5 year avg: {:8,.2f}'.format(
    deaths_2020 - deaths_avg_68_std_pre_2020))

print('2020 Deaths Regression Prediction(s): {:8,.2f}'.format(
    deaths_2020 - predicted_deaths))

print('2020 Deaths Over 2019: {:8,.2f}'.format(deaths_2020 - deaths_2019))
