import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)

mortality_file = "data/Weekly_counts_of_deaths_by_jurisdiction_and_age_group.csv"

df = pd.read_csv(mortality_file)
df = df.reset_index()
print(df.columns)

week_series = df.where(df['Year']==2020).sort_values(by=['Week'])['Week']
current_week = week_series.last_valid_index()
print("Current Week", current_week)

start_week = week_series[week_series.first_valid_index()]
end_week = week_series[week_series.last_valid_index()]

# Drop us total index
us_index = df[df['State Abbreviation'] == 'US'].index
df.drop(us_index, inplace=True)

# Drop type duplicates due to predicted weighting (same as unweighted in dataset)
# Decided to keep weighted
df.drop(df[df['Type']=='unweighted'].index, inplace=True)

deaths_by_years = df.replace(
    {'Under 25 years': ' 0-25 years', '85 years and older': '85+   years'}).where(
        df['Week'] >= start_week
    )

# General information to print out, helpful for debugging
print("\n-------------------\n")
print(deaths_by_years.where(df['Year']==2020).where(df['Week']==20).dropna(how='all').where(df['State Abbreviation']=='AL').dropna(how='all')[
    ['Year', 'State Abbreviation', 'Jurisdiction',
     'Age Group', 'Week', 'Number of Deaths', 'Type']])

print(deaths_by_years.where(df['Year']==2019).where(
    df['Week']<=end_week).dropna(how='all')['Number of Deaths'].sum())

print("\n-------------------\n")

# Plot year after year
deaths_by_week = deaths_by_years.dropna(how='all').groupby(['Year', 'Week']).sum()[['Number of Deaths']]
ax = deaths_by_week.plot.line(y='Number of Deaths')
ax.set_ylim([min(deaths_by_week['Number of Deaths'].values)*0.92,
             max(deaths_by_week['Number of Deaths'].values)*1.08])
ax.set_xlabel('(Year, Week)')
ax.set_ylabel('Deaths per Week')
ax.set_title('U.S. Deaths per Week')

ax.yaxis.grid(True, color='#EEEEEE')
ax.xaxis.grid(False)
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=False)

plt.tight_layout()
plt.savefig('graphs/us-deaths-per-week.png',
            dpi=250.0, bbox_inches='tight')
plt.show()


# Overlay plot of year over year
yearly_dict = {}
deaths_by_week = deaths_by_week.reset_index()
max_count, min_count = 0, 0
# print(deaths_by_week)
for year in deaths_by_week['Year'].unique():
    yearly_dict[year] = deaths_by_week.where(
        deaths_by_week['Year']==year).dropna(how='all')['Number of Deaths'].values
    
    if len(yearly_dict[year]) < len(deaths_by_week['Week'].unique()):
        pad = np.zeros(len(deaths_by_week['Week'].unique()) - len(yearly_dict[year]))
        yearly_dict[year] = np.append(yearly_dict[year], pad)

    if max(yearly_dict[year]) > max_count:
        max_count = max(yearly_dict[year])
    if min(yearly_dict[year]) < min_count:
        min_count = min(yearly_dict[year])
        
yearly_df = pd.DataFrame(yearly_dict, index=deaths_by_week['Week'].unique())

ax = yearly_df.plot.line()
ax.set_xlim([0, 52])
ax.set_ylim([min_count*0.92, max_count*1.08])

ax.set_xlabel('Week of Year')
ax.set_ylabel('Deaths per Week')
ax.set_title('U.S. Deaths per Week of Year')

ax.yaxis.grid(True, color='#EEEEEE')
ax.xaxis.grid(False)
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=False)

plt.tight_layout()
plt.savefig('graphs/us-deaths-by-week-of-year.png',
            dpi=250.0, bbox_inches='tight')
plt.show()


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

ax.set_xlabel('Age Groups')
ax.set_ylabel('Deaths')
ax.set_title('U.S. Deaths by Age Group')

ax.yaxis.grid(True, color='#EEEEEE')
ax.xaxis.grid(False)
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=False)

fig.tight_layout()
plt.savefig('graphs/us-deaths-by-age-group.png',
            dpi=250.0, bbox_inches='tight')
plt.show()



print("\n\n==========================================")
print("========== Predicted Deaths ==============")
print("==========================================\n\n")


pd.options.display.float_format = '{:20,.2f}'.format

# Seperate deaths pre-2020 by year
deaths_pre_2020 = deaths_by_years.where(deaths_by_years['Year']!=2020).dropna(how='all')
deaths_pre_2020_yr = deaths_pre_2020.groupby('Year').sum().reset_index()


# Generate Predicted deaths via linear regression
from sklearn.linear_model import LinearRegression
model = LinearRegression()

X = [[int(i)] for i in deaths_pre_2020_yr['Year'].values.tolist()]
Y = [[int(i)] for i in deaths_pre_2020_yr['Number of Deaths'].values.tolist()]

model.fit(X, Y)

std_years = deaths_pre_2020.std(axis=0, skipna=True)['Number of Deaths']
predicted_deaths = model.predict([[2020]])[0][0]


# Plot Deaths
death_by_years = deaths_by_years.dropna(how='all').groupby('Year').sum().reset_index()
ax = death_by_years.plot.scatter(x='Year', y='Number of Deaths')
plt.plot(X+[[2020]], model.predict(X+[[2020]]), c='r')

ax.set_xlabel('Year')
ax.set_ylabel('Deaths (Yearly)')
ax.set_title('U.S. Deaths by Year (Current Week)')

ax.yaxis.grid(True, color='#EEEEEE')
ax.xaxis.grid(False)
ax.set_axisbelow(True)
ax.tick_params(bottom=False, left=False)

ax.ticklabel_format(useOffset=False)

fig.tight_layout()
plt.savefig('graphs/us-deaths-by-year.png',
            dpi=250.0, bbox_inches='tight')
plt.show()


# Print the table for real vs predicted 
print('Model Score (R^2):', model.score(X, Y))
print("Year, Pred., Real")
for i in range(len(X)):
    print(int(X[i][0]),
          int(model.predict([[X[i][0]]])),
          int(deaths_pre_2020_yr['Number of Deaths'].values[i]))


print("\n\n==========================\n\n")
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
