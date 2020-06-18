import requests
import json
from azureml.core import Webservice
service = Webservice(workspace="grab-azure", name="test-deploy")
swagger_uri = "http://64c18f0e-0fda-4aa6-acee-eab012e3c1e1.southeastasia.azurecontainer.io/swagger.json"

print(service.swagger_uri)

# services = Webservice.list(ws)
# print(services[0].scoring_uri)
# print(services[0].swagger_uri)

# primary, secondary = service.get_keys()
# print(primary)

# headers = {'Content-Type': 'application/json'}

# if service.auth_enabled:
#     headers['Authorization'] = 'Bearer '+service.get_keys()[0]
# elif service.token_auth_enabled:
#     headers['Authorization'] = 'Bearer '+service.get_token()[0]

# print(headers)

# test_sample = json.dumps({'data': [
#     [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
#     [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
# ]})

# response = requests.post(
#     service.scoring_uri, data=test_sample, headers=headers)
# print(response.status_code)
# print(response.elapsed)
# print(response.json())
