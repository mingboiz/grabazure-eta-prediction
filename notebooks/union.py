import os
import pyarrow.parquet as pq
import pandas as pd
from math import radians, cos, sin, asin, sqrt, atan2, pi

df = pd.DataFrame()

def TimeGroup(hour):
    if hour <= 7:
        return 'late night'
    elif hour <= 9:
        return 'morning peak'
    elif hour <= 18:
        return 'day'
    elif hour <= 20:
        return 'evening peak'
    elif hour <= 23:
        return 'night'
    
def Duration(series):
    return max(series) - min(series)

def Haversine(lon1, lat1, lon2, lat2):

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371e3
    return c * r

def GetDistance(orilat, orilng, deslat, deslng):
    result = []
    for i in range(len(orilat)):
        result.append( Haversine(orilng.iloc[i], orilat.iloc[i], deslng.iloc[i], deslat.iloc[i]) )
    return pd.Series(result)

def GetDirection(orilat, orilng, deslat, deslng):
    result = []
    for i in range(len(orilat)):
        
        lat1, lon1, lat2, lon2 = orilat.iloc[i], orilng.iloc[i], deslat.iloc[i], deslng.iloc[i]
        dlon = lon2 - lon1 
        dlat = lat2 - lat1
        
        X = cos(lat2) * sin(dlon)
        Y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
        
        result.append( ( (atan2(X,Y)*180/pi) + 360) % 360 )
        
    return pd.Series(result)


# Getting the data, but remove the 'break' to use full data, if not just 1 of the files
counter = 1
for file in os.listdir('city=Singapore'):
    print('Getting file {} now'.format(counter))
    DF = pq.read_table('city=Singapore/' + file).to_pandas()
    
    df = df.append(DF, ignore_index=True)
    counter += 1

id_col = ['trj_id']
numerical_cols = ['rawlat', 'rawlng', 'speed', 'bearing', 'accuracy']
categorical_cols = ['driving_mode', 'osname']

#since there is only one unique value under driving_mode we will drop this column
del df['driving_mode']

# sorting according to date
print('Sorting the dataset now')
df.sort_values('pingtimestamp', axis=0, inplace=True, kind='mergesort')

# Creating new columns
df['avg_speed'] = df.speed
df['hour'] = df.pingtimestamp
df['day of week'] = df.pingtimestamp
df['month'] = df.pingtimestamp
df['day'] = df.pingtimestamp
df['is_Weekday'] = df.pingtimestamp
df['time_group'] = df.pingtimestamp
df['origin_lat'] = df.rawlat
df['origin_lng'] = df.rawlng
df['dest_lat'] = df.rawlat
df['dest_lng'] = df.rawlng
df['duration'] = df.pingtimestamp

# Aggregation of the new columns
print('Aggregating the columns now')
df = df.groupby('trj_id', as_index=False).agg({'avg_speed': 'mean',
                                               'osname': 'first',
                                               'hour': lambda x: pd.to_datetime(min(x), unit='s').hour,
                                               'day of week': lambda x: pd.to_datetime(min(x), unit='s').dayofweek,
                                               'day': lambda x: pd.to_datetime(min(x), unit='s').day,
                                               'month': lambda x: pd.to_datetime(min(x), unit='s').month, 
                                               'is_Weekday': lambda x: 1 if pd.to_datetime(min(x), unit='s').weekday() < 5 else 0,
                                               'time_group': lambda x: TimeGroup(pd.to_datetime(min(x), unit='s').hour),
                                               'origin_lat': 'first',
                                               'origin_lng': 'first',
                                               'dest_lat': 'last',
                                               'dest_lng': 'last',
                                               'duration': lambda x: Duration(x)
                                               })

print('Calculating Euclidean distance...')
df['euclid_dist'] = GetDistance(df.origin_lat, df.origin_lng, df.dest_lat, df.dest_lng)

print('Calculating bearing...')
df['avg_bearing'] = GetDirection(df.origin_lat, df.origin_lng, df.dest_lat, df.dest_lng)

# Checking no duplicates
ArithmeticError(args)print('All IDs are unique: {}'.format(df.trj_id.nunique() == len(df)))

# to_csv
df.to_csv('all.csv')