#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


df = pd.read_csv('all.csv')
del df['Unnamed: 0']
df.head()


# In[3]:


from zipfile import ZipFile
import geopandas as gpd


# In[5]:


get_ipython().system('pip install geopandas')


# In[ ]:


import folium


# In[201]:


zipfile = ZipFile('planning-area-census2010-shp.zip')
filenames = [y for y in sorted(zipfile.namelist()) for ending in ['dbf', 'prj', 'shp', 'shx'] if y.endswith(ending)] 
print(filenames)


# In[ ]:


from io import BytesIO
import shapefile
from shapely.geometry import shape  
import osr


# In[ ]:


import rtree


# In[ ]:


dbf, prj, shp, shx = [BytesIO(zipfile.read(filename)) for filename in filenames]
r = shapefile.Reader(shp=shp, shx=shx, dbf=dbf)


# In[205]:


attributes, geometry = [], []
field_names = [field[0] for field in r.fields[1:]]  
for row in r.shapeRecords():  
    geometry.append(shape(row.shape.__geo_interface__))  
    attributes.append(dict(zip(field_names, row.record)))  
    
print (row.shape.__geo_interface__)


# In[206]:


gdf = gpd.GeoDataFrame(data = attributes, geometry = geometry, crs = {'init': 'epsg:3414'}) #shouldn't this be 4326
gdf.geometry=gdf.geometry.to_crs("EPSG:4326")
gdf.head()


# In[ ]:


import matplotlib.pyplot as plt


# In[208]:


gdf['REGION_N'].unique()


# In[ ]:


#gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
#polys = gpd.read_file('planning-boundary-area.kml', driver='KML')


# In[ ]:


points = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.origin_lng, df.origin_lat))


# In[211]:


print(points.head())


# In[212]:


#kml1 = polys.loc[polys['Name']=='kml_1']

#kml1.reset_index(drop=True, inplace=True)

fig, ax = plt.subplots()
gdf.plot(ax=ax, facecolor='gray');
north_region.plot(ax=ax, facecolor='red');
points.plot(ax=ax, color='blue', markersize=5);
plt.tight_layout();


# In[213]:


complete = gpd.sjoin(points, gdf, op = 'within')


# In[214]:


type(complete)


# In[215]:


df_complete = pd.DataFrame(complete)
df_complete.info()


# In[ ]:


df_complete = df_complete[['trj_id', 'avg_speed', 'avg_bearing', 'osname', 'hour', 'day', 'is_Weekday', 'time_group', 'origin_lat', 'origin_lng', 'dest_lat', 
                           'dest_lng', 'duration', 'euclid_dist', 'PLN_AREA_N', 'REGION_N']]


# In[217]:


df_complete.head()


# In[218]:


df_complete['origin_subregion'] = df_complete['PLN_AREA_N']
df_complete['origin_region'] = df_complete['REGION_N']
del df_complete['PLN_AREA_N']
del df_complete['REGION_N']
df_complete.head()


# In[219]:


type(df_complete)


# In[ ]:


points_dest =  gpd.GeoDataFrame(
    df_complete, geometry=gpd.points_from_xy(df_complete.dest_lng, df_complete.dest_lat))


# In[221]:


print(points_dest)


# In[222]:


another = gpd.sjoin(points_dest, gdf, op = 'within')
df_updated = pd.DataFrame(another)


# In[223]:


df_updated = df_updated[['trj_id', 'avg_speed', 'avg_bearing', 'osname', 'hour', 'day', 'is_Weekday', 'time_group', 'origin_lat', 'origin_lng', 'dest_lat', 
                           'dest_lng', 'duration', 'euclid_dist', 'origin_subregion', 'origin_region', 'PLN_AREA_N', 'REGION_N']]
df_updated['dest_subregion'] = df_updated['PLN_AREA_N']
df_updated['dest_region'] = df_updated['REGION_N']
del df_updated['PLN_AREA_N']
del df_updated['REGION_N']
df_updated.head()


# In[ ]:


df_updated.to_csv('all_updated.csv')


# In[ ]:




