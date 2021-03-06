COVID19 Analysis
================

Repository containing my analysis of COVID19.

Initialize the submodules:
```
git submodule update --init --recursive
```

Update the submodules
```
git submodule update --recursive --remote
```

Generate analysis on Italy:

```
python3 analyze-italy.py
```

## Graphs Generated:

### Counts in Italy
![Counts in Italy](/graphs/italy-counts.png)

### Positive Ratio in Italy
![Ratios in Italy](/graphs/italy-test-ratios.png)

### Counts in US
![Counts in US](/graphs/us-counts.png)

### Positive Ratio in US
![Ratios in US](/graphs/us-test-ratios.png)

### State Statistics (Forlida)
![State Statistics](/graphs/us-stats-in-FL.png)


## CDC Numbers

Total Cases: https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/total-cases-onset.json

Total New Cases: https://www.cdc.gov/coronavirus/2019-ncov/cases-updates/us-cases-epi-chart.json

Excess Deaths: https://www.cdc.gov/nchs/nvss/vsrr/covid19/excess_deaths.htm

## COVID Tracking

Covidtracking.com: https://covidtracking.com/api/states/daily

Data: CDC Flu / Pnumonia Mortality per state - https://www.cdc.gov/nchs/pressroom/sosmap/flu_pneumonia_mortality/flu_pneumonia.htm also in `data/` folder