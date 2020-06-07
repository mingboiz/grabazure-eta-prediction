from urllib.request import urlopen
from urllib.error import HTTPError
from getLocations import getLocationID
from time import time

startTime = time()
print('Starting crawler...\n')

_INTERESTED_YEARS = tuple(range(2014, 2019))
_MONTHS = tuple(range(1, 13))
print('Scraping location IDs...')
_LOCATIONS = getLocationID()
print('Done scraping location IDs!\n')
_OUTPUT_FILENAME = 'raw/weatherData.csv'
_BASE_URL = 'http://www.weather.gov.sg/files/dailydata/DAILYDATA_S{}_{}{:02d}.csv'

_TOTAL_ENTRIES = len(_INTERESTED_YEARS) * len(_MONTHS) * len(_LOCATIONS)
curProcessed = 0
checkpointIndex = 1

print('Beginning core scrape...')
print('Progress: ' + '-'*10, end='')
with open(_OUTPUT_FILENAME, 'w') as dataOut:
    # Read labels
    labelURL = 'http://www.weather.gov.sg/files/dailydata/DAILYDATA_S{}_{}{:02d}.csv'.format(
        105, 2020, 1)
    with urlopen(labelURL) as response:
        html = response.read().decode('utf-8', 'ignore')
        dataOut.write('LocationID,' + html.strip().split('\n')[0])

    # Read all csv data
    for year in _INTERESTED_YEARS:
        for month in _MONTHS:
            for locName, locID in _LOCATIONS:
                curProcessed += 1

                url = _BASE_URL.format(locID, year, month)
                try:
                    with urlopen(url) as response:
                        html = response.read().decode('utf-8', 'ignore').strip().split('\n')
                        for line in html[1:]:
                            line = line.strip()
                            dataOut.write('{},{}\n'.format(locID, line))
                except HTTPError:
                    continue

                if curProcessed == checkpointIndex*_TOTAL_ENTRIES // 10:
                    print('\b'*10 + '+'*checkpointIndex +
                          '-'*(10-checkpointIndex), end='')
                    checkpointIndex += 1
print('\nCore scrape done!\n')

endTime = time()
print('Crawler done!\nTime taken: {:.3f}s'.format(endTime-startTime))
