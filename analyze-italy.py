import os
import csv
import numpy as np
from matplotlib import pyplot as plt

pre = 'COVID-19/dati-andamento-nazionale'
files = os.listdir(pre)

prior = 0
new_tests = 0
values = []
for f in files:
    filename = pre + '/' + f
    if '.csv' in filename:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)
                new_tests += int(row['tamponi']) - prior
                values.append(
                    {
                        "date": row['data'], # date
                        "total hospitalized": row['totale_ospedalizzati'],# total hospitlized
                        "total currently positive": row['totale_attualmente_positivi'], # total currently positive
                        "new positives": row['nuovi_attualmente_positivi'], # New positive
                        "hospitalized": row['ricoverati_con_sintomi'], # hospitalized with symptoms                        
                        "tests": row['tamponi'], # test
                        "deceased": row['deceduti'] # dead
                    }
                )
                prior = int(row['tamponi'])
            
        print(f)

deaths_dict = {}
tests_dict = {}
new_positve_dict = {}
hospitalized_dict = {}
deaths_dict = {}
for value in values:
    omitted_dates = ['2020-02-24T18:00:00', '2020-03-13T17:00:00']
    if value['date'] not in omitted_dates:
        date = value['date'].replace('2020-', '').split('T')[0]
        print(date, value['tests'], value['deceased'])        
        tests_dict[date] = int(value['tests'])
        deaths_dict[date] = int(value['deceased'])
        new_positve_dict[date] = int(value['new positives'])
        hospitalized_dict[date] = int(value['hospitalized'])
        deaths_dict[date] = int(value['deceased'])
    
dates = []
tests = []
deaths= []
test_diffs = []
new_positives = []
new_hospitalized = []
hospitalized = []
new_deaths = []
positive_ratio = []
hospitalized_ratio = []
prior = 0
death_prior = 0
hos_prior = 0
for date in sorted(tests_dict, key=lambda d: int(''.join(d.split('T')[0].split('-')))):
    
    dates.append(date)
    
    tests.append(tests_dict[date])
    deaths.append(deaths_dict[date])

    test_diffs.append(tests[-1] - prior)
    new_deaths.append(deaths[-1] - death_prior)

    new_positives.append(new_positve_dict[date])
    positive_ratio.append(new_positve_dict[date] / test_diffs[-1])
        
    hospitalized.append(hospitalized_dict[date])
    new_hospitalized.append(hospitalized_dict[date] - hos_prior)
    hospitalized_ratio.append(new_hospitalized[-1] / test_diffs[-1])

    print(date, tests[-1] - prior)
    
    prior = tests[-1]
    death_prior = deaths[-1]
    hos_prior = hospitalized[-1]
    

fig, ax = plt.subplots()

ax.plot(dates, test_diffs, label='new tests')
ax.plot(dates, new_positives, label='new positives')
ax.plot(dates, new_deaths, label='new deaths')
ax.plot(dates, hospitalized, label='hospitalizations')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Italy Tests, Positives, Deaths and Hospitalizations")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.show()


fig, ax = plt.subplots()

ax.plot(dates, positive_ratio, label='positive test ratio')
ax.plot(dates, hospitalized_ratio, label='hospitalization ratio')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Italy Ratio of Positive Test Results")
plt.xlabel("date")
plt.ylabel("positive test percentage")
plt.legend()
fig.autofmt_xdate()
plt.show()
