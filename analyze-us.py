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
hospitalized_dict = defaultdict(dict)
deaths_dict = defaultdict(dict)

for state in history_data:
    
    date = state['date']
    state_abr = state['state']
    status = defaultdict(int)

    keys = ['positive', 'negative', 'death', 'hospitalized']
    for key in keys:
        if key not in state:
            status[key] = 0
        elif state[key] != None:
            status[key] = int(state[key])

   # State Specific & US counts
    for state_id in [state_abr, 'US']:
        if date in pos_dict[state_id]:
            pos_dict[state_id][date] += status['positive']
            neg_dict[state_id][date] += status['negative']
            deaths_dict[state_id][date] += status['death']
            hospitalized_dict[state_id][date] += status['hospitalized']
        else:
            pos_dict[state_id][date] = status['positive']
            neg_dict[state_id][date] = status['negative']
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

        deaths, positives, negatives, hospitalized = 0, 0, 0, 0

        if date in pos_dict[state]:
            
            deaths = deaths_dict[state][date]
            positives = pos_dict[state][date]
            negatives = neg_dict[state][date]
            hospitalized = hospitalized_dict[state][date]
        
        test_count = positives + negatives
        
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

        # print(state, date, test_count)


start = 60

# Raw numbers country wide
fig, ax = plt.subplots()

state = 'US'
ax.plot(dates[state][start:], new_tests[state][start:], label='new tests')
ax.plot(dates[state][start:], new_positives[state][start:], label='new positives')
ax.plot(dates[state][start:], new_negatives[state][start:], label='new negatives')
ax.plot(dates[state][start:], new_deaths[state][start:], label='new deaths')
ax.plot(dates[state][start:], new_hospitalized[state][start:], label='new hospitalizations')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("U.S. Tests, Positives, Deaths and Hospitalizations")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.savefig('graphs/us-counts.png',
            dpi=150.0, bbox_inches='tight')
plt.show()



# Raw numbers country wide, LOG
fig, ax = plt.subplots()
ax.set_yscale('log')

state = 'US'
ax.plot(dates[state][start:], new_tests[state][start:], label='new tests')
ax.plot(dates[state][start:], new_positives[state][start:], label='new positives')
ax.plot(dates[state][start:], new_negatives[state][start:], label='new negatives')
ax.plot(dates[state][start:], new_deaths[state][start:], label='new deaths')
ax.plot(dates[state][start:], new_hospitalized[state][start:], label='new hospitalizations')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("U.S. Tests, Positives, Deaths and Hospitalizations")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.savefig('graphs/us-counts-log.png',
            dpi=150.0, bbox_inches='tight')
plt.show()




# Testing ratio graphs
fig, ax = plt.subplots()
state = 'US'
ax.plot(dates[state][start:], positive_ratio[state][start:], label='positive to test ratio')
ax.plot(dates[state][start:], death_ratio[state][start:], label='mortality to test ratio')
ax.plot(dates[state][start:], hospitalized_ratio[state][start:], label='hospitalization to test ratio')

N = 8
xmin, xmax = ax.get_xlim()

ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))
plt.title("U.S. Ratio of Positive Test Results")
plt.xlabel("date")
plt.ylabel("positive test percentage")
plt.legend()
fig.autofmt_xdate()
plt.savefig('graphs/us-test-ratios.png',
            dpi=150.0, bbox_inches='tight')
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
    
# Take top tests / deaths
for i in range(len(new_tests['US'])):
    tests_on_date = 0
    deaths_on_date = 0
    for state, total_tests in top_testing[split:]:
        tests_on_date += new_tests[state][i]
        deaths_on_date += new_deaths[state][i]
    new_tests['remaining'].append(tests_on_date)
    new_deaths['remaining'].append(deaths_on_date)
    dates['remaining'].append(dates['US'][i])
state_test_totals['remaining'] = sum(new_tests['remaining'])


# Graphs Testing by U.S. State
fig, ax = plt.subplots()
# top[1:] excludes US total
for state in top[1:] + ['remaining']:
    ax.plot(dates[state][start:], new_tests[state][start:],
            label=state+' tests ('+f'{state_test_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Testing by U.S. State")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.savefig('graphs/us-tests-by-state.png',
            dpi=150.0, bbox_inches='tight')
plt.show()



# Graphs Testing by U.S. State, LOG
fig, ax = plt.subplots()
ax.set_yscale('log')
# top[1:] excludes US total
for state in top[1:] + ['remaining']:
    ax.plot(dates[state][start:], new_tests[state][start:],
            label=state+' tests ('+f'{state_test_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Testing by U.S. State")
plt.xlabel("date")
plt.ylabel("count")
plt.legend()
fig.autofmt_xdate()
plt.savefig('graphs/us-tests-by-state-log.png',
            dpi=150.0, bbox_inches='tight')
plt.show()


# Testing ratio graphs
fig, ax = plt.subplots()

# IGNORE FIRST 10 DAYS (not enough testing)
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
plt.savefig('graphs/us-test-ratios-by-state.png',
            dpi=150.0, bbox_inches='tight')
plt.show()


# Graphs deaths by U.S. State
top_deaths = {}
for state in new_deaths:
    top_deaths[state] = sum(new_deaths[state])
top_deaths = sorted(top_deaths.items(), key=lambda x: x[1], reverse=True)

top = []
state_death_totals = {}
for state, total_deaths in top_deaths[:split]:
    top.append(state)
# Transfer all totals in dict
for state, total_deaths in top_deaths:
    state_death_totals[state] = total_deaths
    
fig, ax = plt.subplots()
# top[1:] excludes US total
for state in top[1:]:
    ax.plot(dates[state][start:], new_deaths[state][start:],
            label=state+' deaths ('+f'{state_death_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Deaths by U.S. State")
plt.xlabel("date")
plt.ylabel("deaths")
plt.legend()
fig.autofmt_xdate()
plt.savefig('graphs/us-deaths-by-state.png',
            dpi=150.0, bbox_inches='tight')
plt.show()



# Graphs overlay for one State

# top[1:] excludes US total
designated_states = ['NY', 'CA', 'IL', 'FL', 'TX', 'MA']# new_positives.keys()

for state in designated_states:
    fig, ax = plt.subplots()
    state_pos = []
    max_state_pos = max(new_positives[state])
    for i in range(len(new_positives[state])):
        new_pos_ratio = 0.0
        if max_state_pos > 0:
            new_pos_ratio = new_positives[state][i] / max_state_pos
        state_pos.append(new_pos_ratio)
    ax.plot(dates[state][start:], state_pos[start:],
            label=state+' Positives: '+f'{state_test_totals[state]:,}')

    state_hos = []
    max_state_hos = max(new_hospitalized[state])
    for i in range(len(new_hospitalized[state])):
        new_hos_ratio = 0.0
        if max_state_hos > 0:
            new_hos_ratio = new_hospitalized[state][i] / max_state_hos
        state_hos.append(new_hos_ratio)
    state_hospitalized_total = sum(new_hospitalized[state])
    ax.plot(dates[state][start:], state_hos[start:],
            label=state+' Hospitalized: '+f'{state_hospitalized_total:,}')

    state_deaths = []
    max_state_deaths = max(new_deaths[state])
    for i in range(len(new_deaths[state])):
        new_death_ratio = 0.0
        if max_state_deaths > 0:
            new_death_ratio = new_deaths[state][i] / max_state_deaths
        state_deaths.append(new_death_ratio)
    ax.plot(dates[state][start:], state_deaths[start:],
            label=state+' Deaths: '+f'{state_death_totals[state]:,}')

    N = 8
    xmin, xmax = ax.get_xlim()
    ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

    plt.title("Stats in " + state)
    plt.xlabel("date")
    plt.ylabel("normalized trends")
    plt.legend()
    fig.autofmt_xdate()
    plt.savefig('graphs/us-stats-in-'+state+'.png',
                dpi=150.0, bbox_inches='tight')
    plt.show()
