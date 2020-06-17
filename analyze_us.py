import os
import sys
import json
import requests
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict

from analyze_us_prior_flu_deaths import excess_deaths_by_state

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


start = 65

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
plt.tight_layout()
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
plt.tight_layout()
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
plt.tight_layout()
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
split = 15
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
plt.tight_layout()
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
plt.tight_layout()
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
plt.tight_layout()
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
plt.tight_layout()
plt.savefig('graphs/us-deaths-by-state.png',
            dpi=150.0, bbox_inches='tight')
plt.show()


# OF FORM:
#  state_deaths[state] = {
#      'deaths': deaths,
#      'deaths_above_1_std': deaths_above_1_std,
#      'weeks_normalized': normalized.tolist(),
#      'weeks_end': week_ends
#  }                                                        
deaths_by_state = excess_deaths_by_state()


# Graphs overlay for one State

annotated_states = {
    "NY": [
        # x-value (date)
        ('04-12', "Easter Sunday"),
        ('04-26', "2 Weeks After Easter"),
        ('05-10', "4 Weeks After Easter"),
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
        ('06-08', "Phase 1"), # https://www.governor.ny.gov/news/governor-cuomo-announces-new-york-city-enter-phase-1-reopening-june-8-and-five-regions-enter
    ],
    "CA": [
        ('04-27', "Phase 0"), # https://covid19.ca.gov/roadmap/
        ('05-08', "Phase 1"), # https://www.cnn.com/2020/05/08/us/california-coronavirus-reopening/index.html
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
        ('06-09', "Phase 2") # https://projects.sfchronicle.com/2020/coronavirus-map/california-reopening/
    ],
    "IL": [
        ('05-05', "Phase 2"), # https://www.ksdk.com/article/news/health/coronavirus/illinois-reopening-plan-regions/63-c8fb6b2e-9de7-4193-a2b3-be3a4a7a3c3b
        ('05-25', "Memorial Day"),
        ('05-29', "Phase 3"), # https://www.nbcchicago.com/news/local/illinois-phase-3-how-businesses-will-reopen-and-what-you-will-be-allowed-to-do/2278083/
        ('05-30', "BLM Protests Start"), 
    ],
    "FL": [
        ('05-01', "Phase 1"), # https://www.baynews9.com/fl/tampa/coronavirus/2020/05/01/taking-a-look-at-floridas-phase-2-reopening
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
        ('06-02', "Phase 2"), # https://www.news-press.com/story/news/local/2020/06/04/desantis-phase-2-reopen-florida-what-means/5258774002/
    ],
    "TX": [
        ('05-01', "Phase 1"), # https://gov.texas.gov/news/post/governor-abbott-announces-phase-one-to-open-texas-establishes-statewide-minimum-standard-health-protocols
        ('05-18', "Phase 2"), # https://gov.texas.gov/news/post/governor-abbott-announces-phase-two-to-open-texas
        ('05-25', "Memorial Day"),
        ('05-29', "Phase 3"), # https://www.bizjournals.com/dallas/news/2020/05/29/phase-2-reopening.html
        ('05-30', "BLM Protests Start"), 
    ],
    "MA": [
        ('05-18', "Phase 1"), # https://www.msn.com/en-us/news/us/a-look-at-what-can-reopen-in-each-phase-of-massachusetts-opening-plan/ar-BB14fS5B
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
        ('06-08', "Phase 2"), # https://www.masslive.com/coronavirus/2020/06/massachusetts-to-enter-phase-2-of-reopening-plan-on-monday-june-8.html
    ],
    "GA": [
        ('04-24', "Reopens"), # https://www.businessinsider.com/georgia-to-open-gyms-nail-salons-bowling-alleys-and-more-on-friday-2020-4?op=1
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
    ],
    "MI": [
        ('05-07', "Phase 3"), # https://www.mlive.com/public-interest/2020/05/michigan-is-in-phase-3-of-6-in-coronavirus-response-and-recovery-governor-says.html
        ('05-25', "Memorial Day"),
        ('05-26', "Phase 4"), # average - https://www.lansingstatejournal.com/story/news/2020/05/18/reopen-michigan-whitmer-coronavirus-restaurant-bars-retail-phase-safe-start/5215855002/, https://www.freep.com/story/news/local/michigan/2020/05/21/coronavirus-michigan-reopening-whitmer-retail-auto-dental/5235512002/, https://www.clickondetroit.com/news/local/2020/06/01/michigans-reopening-reaches-phase-4-heres-the-next-stage-and-what-it-will-take-to-get-there/
        ('05-30', "BLM Protests Start"), 
    ],
    "NJ": [
        ('05-18', "Beaches Open"), # https://www.inquirer.com/things-to-do/jersey-shore/new-jersey-beaches-shore-beach-coronavirus-social-distancing-20200507.html
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"),
    ]
}

state_pos = {}
state_pos_avg = {}
for state in annotated_states.keys():

    fig, ax = plt.subplots()
    
    # POSITIVES
    days = 5
    state_pos[state] = []
    state_pos_avg[state] = []
    max_state_pos = max(new_positives[state])
    for i in range(len(new_positives[state])):
        new_pos_ratio = 0.0
        if max_state_pos > 0:
            new_pos_ratio = new_positives[state][i] / max_state_pos
        state_pos[state].append(new_pos_ratio)
        state_pos_avg[state].append(
            sum(state_pos[state][-days:]) / len(state_pos[state][-days:])
        )

    # HOSPTIALIZED
    state_hos = []
    max_state_hos = max(new_hospitalized[state])
    if max_state_hos > 0:
        for i in range(len(new_hospitalized[state])):
            new_hos_ratio = 0.0
            if max_state_hos > 0:
                new_hos_ratio = new_hospitalized[state][i] / max_state_hos
            state_hos.append(new_hos_ratio)
        state_hospitalized_total = sum(new_hospitalized[state])

    # DEATHS
    state_deaths = []
    state_deaths_avg = []
    max_state_deaths = max(new_deaths[state])
    for i in range(len(new_deaths[state])):
        new_death_ratio = 0.0
        if max_state_deaths > 0:
            new_death_ratio = new_deaths[state][i] / max_state_deaths
        state_deaths.append(new_death_ratio)
        state_deaths_avg.append(
            sum(state_deaths[-days:]) / len(state_deaths[-days:])
        )


    # UNCONFIRMED COVID DEATHS
    i, normalized_deaths = 0, []
    deaths_above_1_std = []
    for date in dates[state][start:]:

        weeks_end_date = deaths_by_state[state]['weeks_end'][-1]
        weeks_end_date = '-'.join(weeks_end_date.split('/')[0:2])

        if int(date.replace("-", "")) <= int(weeks_end_date.replace("-", "")):
            weeks_end_date = deaths_by_state[state]['weeks_end'][i]
            weeks_end_date = '-'.join(weeks_end_date.split('/')[0:2])

        if int(date.replace("-", "")) > int(weeks_end_date.replace("-", "")):
            i+=1
                

        if len(deaths_by_state[state]['weeks_normalized']) > i:
            normalized_deaths.append(
                deaths_by_state[state]['weeks_normalized'][i])
            deaths_above_1_std.append(
                deaths_by_state[state]['weeks_deaths'][i] / max_state_deaths
            )
        else:
            normalized_deaths.append(0)
            deaths_above_1_std.append(0)
            
    total_deaths = int(deaths_by_state[state]['deaths'])
    # deaths_above_1_std = deaths_by_state[state]['deaths_above_1_std'].sum()
                
        
    ax.plot(dates[state][start:], state_pos_avg[state][start:],
            label='Positives, '+str(days)+' Day Avg', color="blue")
    ax.plot(dates[state][start:], state_deaths_avg[start:],
            label='Deaths ('+str(days)+' Day Avg)', color="green")

    ax.plot(dates[state][start:],
            normalized_deaths, # deaths_above_1_std,
            label='Deaths Over Norm: '+f'{total_deaths:,}',
            color="red")

    ax.plot(dates[state][start:], state_pos[state][start:],
            label='Positives: '+f'{state_test_totals[state]:,}',
            color="blue", alpha=0.6, linestyle='dotted')
    ax.plot(dates[state][start:], state_deaths[start:],
            label='Deaths: '+f'{state_death_totals[state]:,}',
            color="green", alpha=0.6, linestyle='dotted')    
    if max_state_hos > 0:
        ax.plot(dates[state][start:], state_hos[start:],
                label='Hospitalized: '+f'{state_hospitalized_total:,}',
                color="orange", alpha=0.6, linestyle='dotted')

    next_phase = 0
    for x in range(start, len(dates[state])):
        if next_phase < len(annotated_states[state]):
            
            if dates[state][x] == annotated_states[state][next_phase][0]:
                text = annotated_states[state][next_phase][1]
                text += " (" + dates[state][x]  + ")"
                xy = (dates[state][x], state_pos_avg[state][x])
                arrows = dict(facecolor='black',  arrowstyle="->")
                xytext = (dates[state][x],
                          max(state_pos_avg[state][x]-0.25, 0.0))
                if "Phase" not in text:
                    xytext = (dates[state][x],
                              min(state_pos_avg[state][x]+0.25, 1.0))
                plt.annotate(text, xy=xy, xycoords='data',
                             xytext=xytext, arrowprops=arrows,
                             bbox=dict(boxstyle="round", fc="w"),
                )
                next_phase += 1

            
    
    N = 8
    xmin, xmax = ax.get_xlim()
    ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

    plt.title("Stats in " + state)
    plt.xlabel("date")
    plt.ylabel("normalized trends")
    plt.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig('graphs/us-stats-in-'+state+'.png',
                dpi=150.0, bbox_inches='tight')
    plt.show()
