# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import pickle
import numpy as np
import pandas as pd
import azureml.train.automl
import joblib
from azureml.core.model import Model

from inference_schema.schema_decorators import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type import NumpyParameterType
from inference_schema.parameter_types.pandas_parameter_type import PandasParameterType

input_sample = pd.read_csv('train.csv', header=0)
input_sample = pd.DataFrame({'Column1': pd.Series(['0'], dtype='int64'),
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
output_sample = np.array([0])


def init():
    global model
    # This name is model.id of model that we want to deploy deserialize the model file back
    # into a sklearn model
    model_path = Model.get_model_path(model_name='AutoML572e7832746')
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
