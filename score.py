import requests
import json
import pandas as pd

# URL for the web service
scoring_uri = 'http://50f50db3-ce0c-4d72-bc04-653e319f8723.southeastasia.azurecontainer.io/score'
# If the service is authenticated, set the key or token
key = 'LvalDhJvRqMg26KsehDKwYiawGCMLCDi'

# Two sets of data to score, so we get two results back
data = {"data":
        pd.DataFrame({'Column1': pd.Series(['0'], dtype='int64'),
                      'trj_id': pd.Series(['68140'], dtype='int64'),
                      'day': pd.Series(['9'], dtype='int64'),
                      'month': pd.Series(['4'], dtype='int64'),
                      'osname': pd.Series(['ios'], dtype='object'),
                      'avg_speed': pd.Series(['18.89527788'], dtype='float64'),
                      'avg_bearing': pd.Series(['197.5061677'], dtype='float64'),
                      'hour': pd.Series(['1'], dtype='int64'),
                      'day of week': pd.Series(['1'], dtype='int64'),
                      'is_Weekday': pd.Series(['1'], dtype='int64'),
                      'time_group': pd.Series(['late night'], dtype='object'),
                      'origin_lat': pd.Series(['1.365545977'], dtype='float64'),
                      'origin_lng': pd.Series(['103.9665453'], dtype='float64'),
                      'dest_lat': pd.Series(['1.280101083'], dtype='float64'),
                      'dest_lng': pd.Series(['103.8738231'], dtype='float64'),
                      'origin_region': pd.Series(['EAST REGION'], dtype='object'),
                      'origin_subregion': pd.Series(['PASIR RIS'], dtype='object'),
                      'dest_region': pd.Series(['CENTRAL REGION'], dtype='object'),
                      'dest_subregion': pd.Series(['MARINA SOUTH'], dtype='object'),
                      'euclid_dist': pd.Series(['14018.34497'], dtype='float64'),
                      'origin_avg_daily_rainfall': pd.Series(['0.2'], dtype='float64'),
                      'dest_avg_daily_rainfall': pd.Series(['0.0'], dtype='float64')})

        }
# Convert to JSON string
input_data = json.dumps(data)

# Set the content type
headers = {'Content-Type': 'application/json'}
# If authentication is enabled, set the authorization header
headers['Authorization'] = f'Bearer {key}'

# Make the request and display the response
resp = requests.post(scoring_uri, input_data, headers=headers)
print(resp.text)
