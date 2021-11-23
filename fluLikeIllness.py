import json
import os
from os import stat
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, date
from datawrapper import Datawrapper

ACCESS_TOKEN = os.getenv('DW_API_KEY')

dw = Datawrapper(access_token=ACCESS_TOKEN)

### Function to update datawrapper charts
def updateChart(dw_chart_id, dataSet, updateDate, weekendDate, dw_api_key):
    dw.add_data(
    chart_id=dw_chart_id,
    data=dataSet
    )

    time.sleep(2)

    headers = {
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + dw_api_key
    }

    response = requests.request(method="PATCH", 
                                url="https://api.datawrapper.de/v3/charts/" + dw_chart_id, 
                                json={"metadata": {
                                        "annotate": {
                                            "notes": f'''Updated 
                                            {str(updateDate.strftime('%B %d, %Y'))} 
                                            (data reported for the week ending 
                                            {str(weekendDate.strftime('%B %d, %Y'))}). 
                                            Note: Due to COVID-19, the CDC has suspended data 
                                            collection and assessment of the geographic spread 
                                            of flu cases in the U.S.during the 2020-2021 
                                            flu season.'''
                                    }
                                }},
                                headers=headers)

    response.raise_for_status()

    time.sleep(2)

    dw.publish_chart(chart_id=dw_chart_id)

### Function to get ILI CDC data
def getFluJSON(url, instance):
    try:
        r = requests.get(url,timeout=3)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error:{errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting:{errc}")
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:{errt}")
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else:{err}")
    
    rJSON = r.json()
    fluDict = json.loads(rJSON)

    latest = fluDict[instance]

    data = pd.DataFrame.from_dict(latest)
    return(data)





stateInfo = getFluJSON("https://gis.cdc.gov/grasp/FluView1/Phase1IniP", 'stateinfo')
time.sleep(3)
busData = getFluJSON("https://gis.cdc.gov/grasp/FluView1/Phase1IniP", 'busdata')
time.sleep(3)
legend = getFluJSON("https://gis.cdc.gov/grasp/FluView1/Phase1IniP", 'ili_intensity')
time.sleep(3)
dates = getFluJSON("https://gis.cdc.gov/grasp/FluView1/Phase1IniP", 'mmwr')

busDataLatest = busData[busData['mmwrid'] == max(busData['mmwrid'])]


mmwridLatest = max(busDataLatest['mmwrid'])

stateInfo['mmwrid'] = mmwridLatest

stateDates = pd.merge(stateInfo, dates, on='mmwrid', how='left')
stateDatesBus = pd.merge(stateDates, busDataLatest, on='stateid', how='left')
stateDatesBus['iliactivityid'] = stateDatesBus['iliactivityid'].fillna(0)
stateDatesBusLeg = pd.merge(stateDatesBus, legend, left_on='iliactivityid', right_on='iliActivityid', how='left')

stateDatesBusLeg.astype({'stateid': 'int64'})
stateDatesBusLegFilter = stateDatesBusLeg[stateDatesBusLeg['stateid'] <= 51]

finalData = stateDatesBusLegFilter[['statename', 'stateid', 'statefips', 'iliactivityid', 'ili_activity_label', 'legend', 'weekend']]

finalData.to_csv('latestILIData.csv', index=None)
latestWeekendDateStr = finalData['weekend'][0]
latestWeekendDate = datetime.strptime(latestWeekendDateStr, '%Y-%m-%d')

runDay = date.today()


updateChart('pw8yq', finalData, runDay, latestWeekendDate, ACCESS_TOKEN)

