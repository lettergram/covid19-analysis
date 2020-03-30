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
    
history_data = json.loads(response.content.decode('utf-8'))

pos_dict = defaultdict(dict)
neg_dict = defaultdict(dict)
pending_dict = defaultdict(dict)
hospitalized_dict = defaultdict(dict)
deaths_dict = defaultdict(dict)

for state in history_data:
    
    date = state['date']
    state_abr = state['state']
    status = defaultdict(int)

    for key in ['positive', 'negative', 'pending',
                'death', 'hospitalized']:        
        if state[key] != None:
            status[key] = int(state[key])

   # State Specific & US counts
    for state_id in [state_abr, 'US']:
        if date in pos_dict[state_id]:
            pos_dict[state_id][date] += status['positive']
            neg_dict[state_id][date] += status['negative']
            pending_dict[state_id][date] += status['pending']
            deaths_dict[state_id][date] += status['death']
            hospitalized_dict[state_id][date] += status['hospitalized']
        else:
            pos_dict[state_id][date] = status['positive']
            neg_dict[state_id][date] = status['negative']
            pending_dict[state_id][date] = status['pending']
            deaths_dict[state_id][date] = status['death']
            hospitalized_dict[state_id][date] = status['hospitalized']


dates = defaultdict(list)
new_deaths = defaultdict(list)
new_tests = defaultdict(list)
new_positives = defaultdict(list)
new_negatives = defaultdict(list)
new_hospitalized = defaultdict(list)

positive_ratio = defaultdict(list)
death_ratio = defaultdict(list)
hospitalized_ratio = defaultdict(list)

for state in pos_dict:
    
    tests_prior, death_prior = 0, 0
    pos_prior, neg_prior, hos_prior = 0, 0, 0

    for date in sorted(pos_dict['US']):

        deaths, positives, negatives = 0, 0, 0
        pending, hospitalized = 0, 0

        if date in pos_dict[state]:
            
            deaths = deaths_dict[state][date]
            positives = pos_dict[state][date]
            negatives = neg_dict[state][date]
            pending = pending_dict[state][date]
            hospitalized = hospitalized_dict[state][date]
        
        test_count = positives + negatives + pending
        
        dates[state].append(datetime.strptime(str(date), '%Y%m%d').strftime("%m-%d"))
        new_tests[state].append(test_count - tests_prior)
        new_deaths[state].append(deaths - death_prior)
        new_positives[state].append(positives - pos_prior)
        new_negatives[state].append(negatives - neg_prior)
        new_hospitalized[state].append(hospitalized - hos_prior)

        p_ratio, d_ratio, h_ratio = 0.0, 0.0, 0.0
        if new_tests[state][-1] > 0:
            p_ratio = positives / test_count
            d_ratio = deaths / test_count
            h_ratio = hospitalized / test_count
        positive_ratio[state].append(p_ratio)
        death_ratio[state].append(d_ratio)
        hospitalized_ratio[state].append(h_ratio)

        tests_prior = test_count
        death_prior = deaths
        pos_prior = positives
        neg_prior = negatives
        hos_prior = hospitalized



# Raw numbers country wide
fig, ax = plt.subplots()

state = 'US'
ax.plot(dates[state], new_tests[state], label='new tests')
ax.plot(dates[state], new_positives[state], label='new positives')
ax.plot(dates[state], new_negatives[state], label='new negatives')
ax.plot(dates[state], new_deaths[state], label='new deaths')
ax.plot(dates[state], new_hospitalized[state], label='new hospitalizations')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("U.S. Tests, Positives, Deaths and Hospitalizations")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.show()



# Raw numbers country wide, LOG
fig, ax = plt.subplots()
ax.set_yscale('log')

state = 'US'
ax.plot(dates[state], new_tests[state], label='new tests')
ax.plot(dates[state], new_positives[state], label='new positives')
ax.plot(dates[state], new_negatives[state], label='new negatives')
ax.plot(dates[state], new_deaths[state], label='new deaths')
ax.plot(dates[state], new_hospitalized[state], label='new hospitalizations')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("U.S. Tests, Positives, Deaths and Hospitalizations")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.show()




# Testing ratio graphs
fig, ax = plt.subplots()
state = 'US'
ax.plot(dates[state], positive_ratio[state], label='positive to test ratio')
ax.plot(dates[state], death_ratio[state], label='mortality to test ratio')
ax.plot(dates[state], hospitalized_ratio[state], label='hospitalization to test ratio')

N = 8
xmin, xmax = ax.get_xlim()

ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))
plt.title("U.S. Ratio of Positive Test Results")
plt.xlabel("date")
plt.ylabel("positive test percentage")
plt.legend()
fig.autofmt_xdate()
plt.show()




# Calculates Testing by U.S. State
top_testing = {}
for state in new_tests:
    top_testing[state] = sum(new_tests[state])
top_testing = sorted(top_testing.items(), key=lambda x: x[1], reverse=True)

state_test_totals = {}
top = []
split = 10
for state, total_tests in top_testing[:split]:
    top.append(state)
    state_test_totals[state] = total_tests

for i in range(len(new_tests['US'])):
    tests_on_date = 0
    for state, total_tests in top_testing[split:]:
        tests_on_date += new_tests[state][i]
    new_tests['remaining'].append(tests_on_date)
    dates['remaining'].append(dates['US'][i])
state_test_totals['remaining'] = sum(new_tests['remaining'])


# Graphs Testing by U.S. State
fig, ax = plt.subplots()
# top[1:] excludes US total
for state in top[1:] + ['remaining']:
    ax.plot(dates[state], new_tests[state],
            label=state+' tests ('+f'{state_test_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Testing by U.S. State")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.show()

# Graphs Testing by U.S. State, LOG
fig, ax = plt.subplots()
ax.set_yscale('log')
# top[1:] excludes US total
for state in top[1:] + ['remaining']:
    ax.plot(dates[state], new_tests[state],
            label=state+' tests ('+f'{state_test_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Testing by U.S. State")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.show()


# Testing ratio graphs
fig, ax = plt.subplots()

# IGNORE FIRST 10 DAYS (not enough testing)
start = 10
for state in top + ['US']:
    avg_ratio = round(sum(positive_ratio[state][start:])
                      / len(positive_ratio[state][start:]), 3)
    ax.plot(dates[state][start:], positive_ratio[state][start:],
            label=state+' (Ratio: '+f'{avg_ratio}' +
            ', Tests: ' + f'{state_test_totals[state]:,}' +')')
N = 8
xmin, xmax = ax.get_xlim()

ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))
plt.title("U.S. State Ratio of Positive Test Results")
plt.xlabel("date")
plt.ylabel("positive test percentage")
plt.legend()
fig.autofmt_xdate()
plt.show()
