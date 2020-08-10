import os
import sys
import json
import requests
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from collections import defaultdict

from analyze_us_prior_flu_deaths import excess_deaths_by_state

# Set the size of the plot
plt.rcParams["figure.figsize"] = (12,9)

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
            p = positives - pos_prior # daily 
            t = test_count - tests_prior # daily
            d = deaths - death_prior # daily
            h = hospitalized - hos_prior # daily
            p_ratio = p / t
            d_ratio = d / t
            h_ratio = h / t
        positive_ratio[state].append(p_ratio)
        death_ratio[state].append(d_ratio)
        hospitalized_ratio[state].append(h_ratio)

        tests_prior = test_count
        death_prior = deaths
        pos_prior = positives
        neg_prior = negatives
        hos_prior = hospitalized

        if state == 'US':
            print(state, date, positives,
                  test_count, positives / test_count)

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
plt.ylim((0, max(new_tests[state])))
plt.legend()
fig.autofmt_xdate()
plt.tight_layout()

plt.savefig('graphs/us-counts.png',
            dpi=250.0, bbox_inches='tight')
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
            dpi=250.0, bbox_inches='tight')
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
plt.ylim((0, 1.05*max(positive_ratio[state][start:])))
plt.legend()
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig('graphs/us-test-ratios.png',
            dpi=250.0, bbox_inches='tight')
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
max_tests = 0
fig, ax = plt.subplots()
# top[1:] excludes US total
for state in top[1:] + ['remaining']:
    # Select highest test counts
    if max(new_tests[state][start:]) > max_tests:
        max_tests = 1.05*max(new_tests[state][start:])
        
    ax.plot(dates[state][start:], new_tests[state][start:],
            label=state+' tests ('+f'{state_test_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Testing by U.S. State")
plt.xlabel("date")
plt.ylabel("count")
plt.ylim((0, max_tests))
plt.legend()
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig('graphs/us-tests-by-state.png',
            dpi=250.0, bbox_inches='tight')
plt.show()


# Graphs Testing by U.S. State, LOG
fig, ax = plt.subplots()
ax.set_yscale('log')
max_tests = 0
# top[1:] excludes US total
for state in top[1:] + ['remaining']:
    if max_tests < max(new_tests[state][start:]):
        max_tests = max(new_tests[state][start:])
    ax.plot(dates[state][start:], new_tests[state][start:],
            label=state+' tests ('+f'{state_test_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Testing by U.S. State")
plt.xlabel("date")
plt.ylabel("count")
plt.ylim((0, max(max_tests, 1.0)))
plt.legend()
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig('graphs/us-tests-by-state-log.png',
            dpi=250.0, bbox_inches='tight')
plt.show()


# Testing ratio graphs
fig, ax = plt.subplots()
max_ratios = 0
# IGNORE FIRST 10 DAYS (not enough testing)
for state in top + ['US']:
    curr_ratio = round(positive_ratio[state][start:][-1], 3)
    if max(positive_ratio[state][start:]) > max_ratios:
         max_ratios = max(positive_ratio[state][start:])
    ax.plot(dates[state][start:], positive_ratio[state][start:],
            label=state+' (Ratio: '+f'{curr_ratio}' +
            ', Tests: ' + f'{state_test_totals[state]:,}' +')')
N = 8
xmin, xmax = ax.get_xlim()

ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))
plt.title("U.S. State Ratio of Positive Test Results")
plt.xlabel("date")
plt.ylabel("positive test percentage")
plt.ylim((0, max_ratios))
plt.legend()
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig('graphs/us-test-ratios-by-state.png',
            dpi=250.0, bbox_inches='tight')
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

max_deaths = 0
fig, ax = plt.subplots()
# top[1:] excludes US total
for state in top[1:]:
    if max(new_deaths[state]) > max_deaths:
        max_deaths = 1.05*max(new_deaths[state][start:])
    ax.plot(dates[state][start:], new_deaths[state][start:],
            label=state+' deaths ('+f'{state_death_totals[state]:,}'+')')

N = 8
xmin, xmax = ax.get_xlim()
ax.set_xticks(np.round(np.linspace(xmin, xmax, N), 2))

plt.title("Deaths by U.S. State")
plt.xlabel("date")
plt.ylabel("deaths")
plt.ylim((0, max_deaths))
plt.legend()
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig('graphs/us-deaths-by-state.png',
            dpi=250.0, bbox_inches='tight')
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
        ('06-24', "Phase 2"), # https://www.washingtontimes.com/news/2020/jun/23/bill-de-blasio-justice-department-spar-over-new-yo/
        ('07-04', '4th of July'),
        ('07-05', 'Phase 3'), # https://www.marketwatch.com/story/no-indoor-dining-when-new-york-city-reaches-phase-3-next-monday-2020-07-01
        ('07-22', 'Phase 4'), # https://www.msn.com/en-us/news/us/road-to-reopening-new-york-city-set-to-enter-phase-4-monday/ar-BB16VWuE
        ('09-04', 'School Opens'), # https://nycschoolcalendars.com/new-york-city-school-district/2020-2021
    ],
    "CA": [
        ('04-27', "Phase 0"), # https://covid19.ca.gov/roadmap/
        ('05-08', "Phase 1"), # https://www.cnn.com/2020/05/08/us/california-coronavirus-reopening/index.html
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
        ('06-09', "Phase 2"), # https://projects.sfchronicle.com/2020/coronavirus-map/california-reopening/
        ('06-12', "Phase 3"), # https://www.actionnewsnow.com/content/news/Phase-3-of-California-reopening-whats-open-571219961.html
        ('07-01', "Close Indoor, Again"), # https://covid19.ca.gov/roadmap-counties/
        ('07-04', '4th of July'),
        
    ],
    "IL": [
        ('05-05', "Phase 2"), # https://www.ksdk.com/article/news/health/coronavirus/illinois-reopening-plan-regions/63-c8fb6b2e-9de7-4193-a2b3-be3a4a7a3c3b
        ('05-25', "Memorial Day"),
        ('05-29', "Phase 3"), # https://www.nbcchicago.com/news/local/illinois-phase-3-how-businesses-will-reopen-and-what-you-will-be-allowed-to-do/2278083/
        ('05-30', "BLM Protests Start"),
        ('06-26', "Phase 4"), # https://www.msn.com/en-us/news/us/daywatch-illinois-to-enter-phase-4-on-friday-protests-impact-on-coronavirus-in-chicago-and-laurence-holmes-must-listen-radio/ar-BB15RQs1
        ('07-04', '4th of July'),
        ('08-15', 'Schools Partial Reopen') # https://publicholidays.us/school-holidays/illinois/
    ],
    "FL": [
        ('05-01', "Phase 1"), # https://www.baynews9.com/fl/tampa/coronavirus/2020/05/01/taking-a-look-at-floridas-phase-2-reopening
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
        ('06-02', "Phase 2"), # https://www.news-press.com/story/news/local/2020/06/04/desantis-phase-2-reopen-florida-what-means/5258774002/
        ('06-05', "Phase 3"), # https://www.msn.com/en-us/video/peopleandplaces/florida-enters-phase-3-on-friday/vi-BB150bdt
        ('07-03', 'Beach Closures'), # https://www.foxnews.com/transcript/florida-counties-announce-beach-closures-curfews-after-record-high-covid-19-spike
        ('07-04', '4th of July'),
        ('08-05', 'Schools Partial Reopen'), # https://www.wptv.com/news/education/back-to-school/west-palm-beach-private-school-to-have-kids-back-in-classrooms-wednesday
    ],
    "TX": [
        ('05-01', "Phase 1"), # https://gov.texas.gov/news/post/governor-abbott-announces-phase-one-to-open-texas-establishes-statewide-minimum-standard-health-protocols
        ('05-18', "Phase 2"), # https://gov.texas.gov/news/post/governor-abbott-announces-phase-two-to-open-texas
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"),
        ('06-03', "Phase 3"), # https://www.bizjournals.com/dallas/news/2020/05/29/phase-2-reopening.html
        ('07-04', '4th of July'),
        ('09-08', 'Schools Open In Person'), # https://talk1370.radio.com/articles/list-central-texas-school-district-back-to-school-plans
        
    ],
    "MA": [
        ('05-18', "Phase 1"), # https://www.msn.com/en-us/news/us/a-look-at-what-can-reopen-in-each-phase-of-massachusetts-opening-plan/ar-BB14fS5B
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"), 
        ('06-08', "Phase 2"), # https://www.masslive.com/coronavirus/2020/06/massachusetts-to-enter-phase-2-of-reopening-plan-on-monday-june-8.html
        ('07-04', '4th of July'),
        ('07-05', 'Phase 3'), # https://www.masslive.com/coronavirus/2020/07/massachusetts-to-allow-casinos-gyms-museums-to-reopen-as-early-as-monday-as-state-moves-into-phase-3-of-reopening.html
        ('09-10', 'Shools Reopen'), # https://www.bostonglobe.com/2020/08/09/metro/boston-schools-should-not-reopen-sept-10/
    ],
    "GA": [
        ('04-24', "Reopens"), # https://www.businessinsider.com/georgia-to-open-gyms-nail-salons-bowling-alleys-and-more-on-friday-2020-4?op=1
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"),
        ('07-04', '4th of July'),
        ('08-12' 'Schools Reopen'), # https://www.wsbtv.com/news/local/county-by-county-plans-returning-school-this-fall/QJAYLUB4TFBPBCJCIMVZXUQGFY/
    ],
    "MI": [
        ('05-07', "Phase 3"), # https://www.mlive.com/public-interest/2020/05/michigan-is-in-phase-3-of-6-in-coronavirus-response-and-recovery-governor-says.html
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"),
        ('06-01', "Phase 4"), # https://www.michigan.gov/coronavirus/0,9753,7-406-98163-530627--,00.html apverage - https://www.lansingstatejournal.com/story/news/2020/05/18/reopen-michigan-whitmer-coronavirus-restaurant-bars-retail-phase-safe-start/5215855002/, https://www.freep.com/story/news/local/michigan/2020/05/21/coronavirus-michigan-reopening-whitmer-retail-auto-dental/5235512002/, https://www.clickondetroit.com/news/local/2020/06/01/michigans-reopening-reaches-phase-4-heres-the-next-stage-and-what-it-will-take-to-get-there/
        ('07-04', '4th of July'),
        ('08-24', 'Schools Partial Reopen'), # https://publicholidays.us/school-holidays/michigan/
    ],
    "NJ": [
        ('05-18', "Beaches Open"), # https://www.inquirer.com/things-to-do/jersey-shore/new-jersey-beaches-shore-beach-coronavirus-social-distancing-20200507.html
        ('05-25', "Memorial Day"),
        ('05-30', "BLM Protests Start"),
        ('06-22', "Phase 2"), # https://newyork.cbslocal.com/2020/06/01/new-jersey-to-begin-phase-two-reopening-in-2-weeks-murphy-says/ https://www.inquirer.com/things-to-do/jersey-shore/new-jersey-beaches-shore-beach-coronavirus-social-distancing-20200507.html
        ('07-04', '4th of July'),
    ]
}

start = 70

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
    state_positives_total = sum(new_positives[state])

    # HOSPTIALIZED
    state_hos = []
    max_state_hos = max(new_hospitalized[state])
    state_hospitalized_total = 0
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

    # TESTS
    state_tests = []
    state_tests_avg = []
    max_state_tests = max(new_tests[state])
    for i in range(len(new_tests[state])):
        new_tests_ratio = 0.0
        if max_state_tests > 0:
            new_tests_ratio = new_tests[state][i] / max_state_tests
        state_tests.append(new_tests_ratio)
        state_tests_avg.append(
            sum(state_tests[-days:]) / len(state_tests[-days:])
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
            
    total_deaths = int(deaths_by_state[state]['weeks_deaths'].sum())
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
            label='Positives: '+f'{state_positives_total:,}',
            color="blue", alpha=0.6, linestyle='dotted')
    ax.plot(dates[state][start:], state_deaths[start:],
            label='Deaths: '+f'{state_death_totals[state]:,}',
            color="green", alpha=0.6, linestyle='dotted')

    ax.plot(dates[state][start:], state_tests[start:],
            label='Tests: '+f'{state_test_totals[state]:,}',
            color="purple", alpha=0.6, linestyle='dotted')
        
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
    plt.ylim((0, 1.1))
    plt.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig('graphs/us-stats-in-'+state+'.png',
                dpi=250.0, bbox_inches='tight')
    plt.show()
