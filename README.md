# Microsoft Azure Hackathon 2020
## Grab Data Science Challenge - Haidilao
Natalie Lam, Benedict Tay, Yang Ming

## Steps

### Make use of notebook 'prediction.ipynb' in the repository to make predictions using the endpoint

  1. Input data should be a list of JSON objects, each JSON object should have these specified attributes as the example shown below:

```dotnetcli
input_data = [
    {"latitude_origin": -6.141255,
    "longitude_origin": 106.692710,
    "latitude_destination": -6.141150,
    "longitude_destination": 106.693154,
    "timestamp": 1590487113,
    "hour_of_day": 9,
    "day_of_week": 1
    },
    {"latitude_origin": -3.14159,
    "longitude_origin": 108.123710,
    "latitude_destination": -3.141150,
    "longitude_destination": 106.621154,
    "timestamp": 1590481313,
    "hour_of_day": 5,
    "day_of_week": 2
    },
    ...
]
```
  2. You can populate the `` predictions `` array to with the predicted outputs from our Model to calculate RMSE. The ```predict()``` function takes as input a single JSON object and an endpoint, and outputs the prediction for that JSON object.

```dotnetcli
predictions = list()
for i in range(len(test_data)):
    predictions.append(predict(test_data[i], endpoint))
```
  3. The ``endpoint`` and authentication objects are specified in our submission slides. Please change the <b>endpoint</b> in the code chunk in your prediction.py to the given URI:

<pre>
endpoint = '<b>localhost:8888</b>'

'''
Input data should be a list of json objects.

Each json object should have those attributes as specified:
        lattitude_origin
        longitude_origin
        lattitude_destination
        longitude_destination
        timestamp
        hour_of_day
        day_of_week
'''
</pre>
