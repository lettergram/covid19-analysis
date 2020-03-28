import os
import json
import requests
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict

# From covidtracking.com
url = 'https://covidtracking.com/api/states/daily'

response = requests.get(url)

if response.status_code != 200:
    print("URL ERROR")
    exit()
    
data = json.loads(response.content.decode('utf-8'))
for state in data:
    print(
        state['date'],
        state['state'],
        state['positive'],
        state['negative'],
        state['pending'],
        state['hospitalized'],
        state['death'],
    )
    
pos_dict = defaultdict(int)
neg_dict = defaultdict(int)
pending_dict = defaultdict(int)
hospitalized_dict = defaultdict(int)
deaths_dict = defaultdict(int)
for state in data:
    date = state['date']
    if state['positive'] != None:
        pos_dict[date] += int(state['positive'])
    if state['negative'] != None:
        neg_dict[date] += int(state['negative'])
    if state['pending'] != None:
        pending_dict[date] += int(state['pending'])
    if state['death'] != None:
        deaths_dict[date] += int(state['death'])
    if state['hospitalized'] != None:
        hospitalized_dict[date] += int(state['hospitalized'])

dates = []
positives = []
negatives = []
deaths= []

tests = []
test_diffs = []

hospitlized = []

new_deaths = []
new_tests = []
new_positives = []
new_negatives = []

tests_prior = 0
death_prior = 0
pos_prior = 0
neg_prior = 0

positive_ratio = []

for date in sorted(pos_dict):

    dates.append(datetime.strptime(str(date), '%Y%m%d').strftime("%m-%d"))
    
    tests.append(pos_dict[date] + neg_dict[date])
    positives.append(pos_dict[date])
    negatives.append(neg_dict[date])    
    deaths.append(deaths_dict[date])
    hospitlized.append(hospitalized_dict[date])

    new_tests.append(tests[-1] - tests_prior)
    new_deaths.append(deaths[-1] - death_prior)
    new_positives.append(positives[-1] - pos_prior)
    new_negatives.append(negatives[-1] - neg_prior)

    positive_ratio.append(new_positives[-1] / new_tests[-1])

    tests_prior = tests[-1]
    death_prior = deaths[-1]
    pos_prior = positives[-1]
    neg_prior = negatives[-1]

fig, ax = plt.subplots()

ax.plot(dates, new_tests, label='new tests')
ax.plot(dates, new_positives, label='new positives')
ax.plot(dates, new_negatives, label='new negatives')
ax.plot(dates, new_deaths, label='new deaths')
ax.plot(dates, hospitlized, label='hospitalizations')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("U.S. Tests, Positives, Deaths and Hospitalizations")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.show()


fig, ax = plt.subplots()

ax.plot(dates, positive_ratio, label='positive test ratio')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("U.S. Ratio of Positive Test Results")
plt.xlabel("date")
plt.ylabel("positive test percentage")
plt.legend()
fig.autofmt_xdate()
plt.show()
