# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from shapely.geometry import shape
import rtree
import shapefile
from io import BytesIO
import geopandas as gpd
from zipfile import ZipFile
from math import radians, cos, sin, asin, sqrt, atan2, pi
import pandas as pd
import pyarrow.parquet as pq
import os
from IPython import get_ipython

# %% [markdown]
# # This notebook has 3 parts:
# - Unioning all the parquet files
# - Adding in the spatial data
# - Adding in the weather data
#
# ## Note: put this notebook in the same folder as:
# - city=Singapore
# - planning-area-census2010-shp.zip
# - may_apr_weather.csv
# %% [markdown]
# ### Loading all relevant libraries
#

# %%

get_ipython().system('pip install geopandas')
get_ipython().system('pip install pyshp')

get_ipython().system('sudo apt-get update && apt-get install -y libspatialindex-dev')
get_ipython().system('pip install rtree')


# %% [markdown]
# ### Unioning all the parquet files

# %%
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
        result.append(
            Haversine(orilng.iloc[i], orilat.iloc[i], deslng.iloc[i], deslat.iloc[i]))
    return pd.Series(result)


def GetDirection(orilat, orilng, deslat, deslng):
    result = []
    for i in range(len(orilat)):

        lat1, lon1, lat2, lon2 = orilat.iloc[i], orilng.iloc[i], deslat.iloc[i], deslng.iloc[i]
        dlon = lon2 - lon1

        X = cos(lat2) * sin(dlon)
        Y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

        result.append(((atan2(X, Y)*180/pi) + 360) % 360)

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

# since there is only one unique value under driving_mode we will drop this column
del df['driving_mode']

# sorting according to date
df.sort_values('pingtimestamp', axis=0, inplace=True, kind='mergesort')

# Creating new columns
df['avg_speed'] = df.speed
df['hour'] = df.pingtimestamp
df['day of week'] = df.pingtimestamp
df['day'] = df.pingtimestamp
df['month'] = df.pingtimestamp
df['is_Weekday'] = df.pingtimestamp
df['time_group'] = df.pingtimestamp
df['origin_lat'] = df.rawlat
df['origin_lng'] = df.rawlng
df['dest_lat'] = df.rawlat
df['dest_lng'] = df.rawlng
df['duration'] = df.pingtimestamp

# Aggregation of the new columns
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

df['euclid_dist'] = GetDistance(
    df.origin_lat, df.origin_lng, df.dest_lat, df.dest_lng)

df['avg_bearing'] = GetDirection(
    df.origin_lat, df.origin_lng, df.dest_lat, df.dest_lng)

print('Unioning parquet files done')

# %% [markdown]
# ### Adding in the spatial data
#
#

# %%
# df get from previous code on top ^^
df = pd.read_csv('all.csv')

zipfile = ZipFile('planning-area-census2010-shp.zip')
filenames = [y for y in sorted(zipfile.namelist()) for ending in [
    'dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)]

dbf, prj, shp, shx = [BytesIO(zipfile.read(filename))
                      for filename in filenames]
r = shapefile.Reader(shp=shp, shx=shx, dbf=dbf)

attributes, geometry = [], []
field_names = [field[0] for field in r.fields[1:]]
for row in r.shapeRecords():
    geometry.append(shape(row.shape.__geo_interface__))
    attributes.append(dict(zip(field_names, row.record)))

gdf = gpd.GeoDataFrame(data=attributes, geometry=geometry, crs='epsg:3414')
gdf.geometry = gdf.geometry.to_crs(epsg=4326)

points = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.origin_lng, df.origin_lat))

points = points.loc[points.geometry.is_valid]
gdf = gdf.loc[gdf.geometry.is_valid]

complete = gpd.sjoin(points, gdf, how='left', op="within")

df_complete = pd.DataFrame(complete)

df_complete = df_complete[['trj_id',
                           'avg_speed',
                           'avg_bearing',
                           'osname',
                           'hour',
                           'day',
                           'month',
                           'is_Weekday',
                           'time_group',
                           'origin_lat',
                           'origin_lng',
                           'dest_lat',
                           'dest_lng',
                           'duration',
                           'euclid_dist',
                           'PLN_AREA_N',
                           'REGION_N']]

df_complete['origin_subregion'] = df_complete['PLN_AREA_N']
df_complete['origin_region'] = df_complete['REGION_N']
del df_complete['PLN_AREA_N']
del df_complete['REGION_N']

points_dest = gpd.GeoDataFrame(df_complete, geometry=gpd.points_from_xy(
    df_complete.dest_lng, df_complete.dest_lat))

another = gpd.sjoin(points_dest, gdf, how='left', op='within')
df_updated = pd.DataFrame(another)

df_updated = df_updated[['trj_id',
                         'avg_speed',
                         'avg_bearing',
                         'osname',
                         'hour',
                         'day',
                         'month',
                         'is_Weekday',
                         'time_group',
                         'origin_lat',
                         'origin_lng',
                         'dest_lat',
                         'dest_lng',
                         'duration',
                         'euclid_dist',
                         'origin_subregion',
                         'origin_region',
                         'PLN_AREA_N',
                         'REGION_N']]

df_updated['dest_subregion'] = df_updated['PLN_AREA_N']
df_updated['dest_region'] = df_updated['REGION_N']
del df_updated['PLN_AREA_N']
del df_updated['REGION_N']

# writing to csv
# df_updated.to_csv('all_updated.csv')

df = df_updated

print('Adding spatial data done')

# %% [markdown]
# ### Adding in the weather data

# %%
weather = pd.read_csv('may_apr_weather.csv')

# df get from the previous code on top ^^
# df = pd.read_csv('all_updated.csv')

# dummy column for origin subregion for joining, need this because our dataset has 53 subregions but weather only 38
df['dummy_origin'] = df['origin_subregion']
conditions = [
    (df['dummy_origin'] == 'BUKIT BATOK'),
    (df['dummy_origin'] == 'HOUGANG'),
    (df['dummy_origin'] == 'JURONG EAST'),
    (df['dummy_origin'] == 'MARINA EAST'),
    (df['dummy_origin'] == 'OUTRAM'),
    (df['dummy_origin'] == 'STRAITS VIEW'),
    (df['dummy_origin'] == 'MUSEUM'),
    (df['dummy_origin'] == 'ROCHOR'),
    (df['dummy_origin'] == 'SINGAPORE RIVER'),
    (df['dummy_origin'] == 'RIVER VALLEY'),
    (df['dummy_origin'] == 'TANGLIN'),
    (df['dummy_origin'] == 'SENGKANG'),
    (df['dummy_origin'] == 'SIMPANG'),
    (df['dummy_origin'] == 'WESTERN ISLANDS'),
    (df['dummy_origin'] == 'WESTERN WATER CATCHMENT')]

choices = ['BUKIT PANJANG', 'PAYA LEBAR', 'CLEMENTI', 'MARINA SOUTH', 'MARINA SOUTH', 'MARINA SOUTH', 'DOWNTOWN CORE', 'DOWNTOWN CORE', 'DOWNTOWN CORE',
           'ORCHARD', 'ORCHARD', 'SELETAR', 'SEMBAWANG', 'BOON LAY', 'LIM CHU KANG']
df['dummy_origin'] = np.select(conditions, choices, df.dummy_origin)

# dummy column for destination subregion for joining
df['dummy_dest'] = df['dest_subregion']
conditions = [
    (df['dummy_dest'] == 'BUKIT BATOK'),
    (df['dummy_dest'] == 'HOUGANG'),
    (df['dummy_dest'] == 'JURONG EAST'),
    (df['dummy_dest'] == 'MARINA EAST'),
    (df['dummy_dest'] == 'OUTRAM'),
    (df['dummy_dest'] == 'STRAITS VIEW'),
    (df['dummy_dest'] == 'MUSEUM'),
    (df['dummy_dest'] == 'ROCHOR'),
    (df['dummy_dest'] == 'SINGAPORE RIVER'),
    (df['dummy_dest'] == 'RIVER VALLEY'),
    (df['dummy_dest'] == 'TANGLIN'),
    (df['dummy_dest'] == 'SENGKANG'),
    (df['dummy_dest'] == 'SIMPANG'),
    (df['dummy_dest'] == 'WESTERN ISLANDS'),
    (df['dummy_dest'] == 'WESTERN WATER CATCHMENT')]

choices = ['BUKIT PANJANG', 'PAYA LEBAR', 'CLEMENTI', 'MARINA SOUTH', 'MARINA SOUTH', 'MARINA SOUTH', 'DOWNTOWN CORE', 'DOWNTOWN CORE', 'DOWNTOWN CORE',
           'ORCHARD', 'ORCHARD', 'SELETAR', 'SEMBAWANG', 'BOON LAY', 'LIM CHU KANG']
df['dummy_dest'] = np.select(conditions, choices, df.dummy_dest)

df_a = pd.merge(df, weather,  how='left', left_on=[
                'dummy_origin', 'day', 'month'], right_on=['subregion', 'weather_day', 'weather_month'])
df_a = df_a.drop(['dummy_origin', 'weather_day',
                  'weather_month', 'subregion'], axis=1)
df_a.rename(columns={'Rainfall': 'origin_avg_daily_rainfall'}, inplace=True)

df_b = pd.merge(df_a, weather,  how='left', left_on=[
                'dummy_dest', 'day', 'month'], right_on=['subregion', 'weather_day', 'weather_month'])
df_b = df_b.drop(['dummy_dest', 'weather_day',
                  'weather_month', 'subregion'], axis=1)
df_b.rename(columns={'Rainfall': 'dest_avg_daily_rainfall'}, inplace=True)

df = df_b

print('Adding weather data done')

# %% [markdown]
# ### Final code to putput as .csv file or not
#

# %%
df_b.to_csv('all_updated_with_weather.csv')
