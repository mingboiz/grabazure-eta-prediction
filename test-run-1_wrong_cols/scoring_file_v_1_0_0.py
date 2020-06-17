# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import pickle
import numpy as np
import pandas as pd
import azureml.train.automl
from sklearn.externals import joblib
from azureml.core.model import Model

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType


input_sample = pd.DataFrame({'trj_id': pd.Series(['4675'], dtype='int64'), 'osname': pd.Series(['ios'], dtype='object'), 'avg_speed': pd.Series(['18.43982979'], dtype='float64'), 'avg_bearing': pd.Series(['326.1667864'], dtype='float64'), 'day of week': pd.Series(['5'], dtype='int64'), 'is_Weekday': pd.Series(['0'], dtype='int64'), 'hour': pd.Series(['11'], dtype='int64'), 'time_group': pd.Series(['day'], dtype='object'), 'day': pd.Series(['13'], dtype='int64'), 'month': pd.Series(['4'], dtype='int64'), 'origin_avg_daily_rainfall': pd.Series(['0.0'], dtype='float64'), 'dest_avg_daily_rainfall': pd.Series(['0.0'], dtype='float64'), 'origin_lat': pd.Series(['1.342669897'], dtype='float64'), 'origin_lng': pd.Series(['103.9824935'], dtype='float64'), 'dest_lat': pd.Series(['1.376711251'], dtype='float64'), 'dest_lng': pd.Series(['103.8589185'], dtype='float64'), 'origin_region': pd.Series(['EAST REGION'], dtype='object'), 'origin_subregion': pd.Series(['CHANGI'], dtype='object'), 'dest_region': pd.Series(['NORTH-EAST REGION'], dtype='object'), 'dest_subregion': pd.Series(['SERANGOON'], dtype='object'), 'euclid_dist': pd.Series(['14249.01363'], dtype='float64')})
output_sample = np.array([0])


def init():
    global model
    # This name is model.id of model that we want to deploy deserialize the model file back
    # into a sklearn model
    model_path = Model.get_model_path(model_name = 'AutoML2243be91645')
    model = joblib.load(model_path)


@input_schema('data', PandasParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data):
    try:
        result = model.predict(data)
        return json.dumps({"result": result.tolist()})
    except Exception as e:
        result = str(e)
        return json.dumps({"error": result})
