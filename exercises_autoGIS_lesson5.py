#!/usr/bin/env python
# coding: utf-8

# In[32]:


import folium
from pyproj import crs
import geopandas as gpd
import matplotlib.pyplot as plt


# In[51]:


# create map instance
m = folium.Map(location = [39.95300,-75.16355], zoom_start = 10,
              control_scale = True)
m


# In[38]:


# save map to html file
out_fp = 'base_map.html'
m.save(out_fp)


# In[49]:


# change the basemap style to stamen toner
# pass in a custom tile set url
api_key = 'cebee8f834f543ceae176470732a4542'
tilemap_url = 'https://tile.thunderforest.com/spinal-map/{z}/{x}/{y}.png?apikey=%s'% api_key
attribution = 'tile.thunderforest.com'
# m2 = folium.Map(location = [39.95300,-75.16355],tiles = tilemap_url, zoom_start = 10,
#               control_scale = True, prefer_canvas = True)
# m2
m2 = folium.Map(location=[39.95300,-75.16355], tiles=tilemap_url,
                zoom_start=12, control_scale=True, prefer_canvas=True, attr = attribution)

m2


# ## Adding Layers to The Map

# In[56]:


# add a marker to the first map
my_house = [39.94824, -75.16243] 

folium.Marker(location = my_house,
             popup = "Keon's House",
             icon = folium.Icon(color = 'green', icon = 'home')).add_to(m)

m # show map


# In[57]:


# add layers - point shp - covid test sites
url_testSites = 'http://data-phl.opendata.arcgis.com/datasets/398ec6ac0b7443babcdd41b40bab3407_0.geojson'
points = gpd.read_file(url_testSites)
points.head()


# In[58]:


# convert to folium GeoJson
points_gjson = folium.features.GeoJson(points, name = 'COVID-19 Test Sites')

# add points to the map
points_gjson.add_to(m)

m


# ## Layer Control

# In[59]:


# create a layer control object and add it to our map
folium.LayerControl().add_to(m)
m


# ## Heatmap
# Make a heatmap - wrangle the data first

# In[68]:


from folium.plugins import HeatMap

hm = folium.Map(location = [39.95300,-75.16355], zoom_start = 10,
              control_scale = True)

# get x y coords for each point
points['x'] = points['geometry'].x
points['y'] = points['geometry'].y

# create a list of coordinate pairs
locations = list(zip(points['y'], points['x']))
# print(f'Number of Test Sites: {len(locations)}')

HeatMap(locations).add_to(hm)
hm


# In[69]:


# Use marker clusters
from folium.plugins import MarkerCluster
marker_cluster = MarkerCluster(locations)

# define a new map instance
cm = folium.Map(location = [39.95300,-75.16355], zoom_start = 10,
              control_scale = True)

# add markers to map
marker_cluster.add_to(cm)

cm


# ## Chloropleth Maps - Sanitation Maps of Philly

# In[75]:


# read in another wfs service 
import requests
import geojson

# fetch data from WFS using requests
sanitation_areas = 'http://data.phl.opendata.arcgis.com/datasets/472c504f650242f4be612d8320b89c86_0.geojson'
data = gpd.read_file(sanitation_areas)
# create a geodataframe from the geojson

# check the data
data.head()


# In[83]:


# reproject to WGS84 if needed (folium uses web mercator)
# print(str(data.crs))
if str(data.crs) == 'epsg:4326':
    print('The data is in the right projection')
else:
    print('The data should be reprojected')


# In[85]:


# rename the sanitation area col
data = data.rename(columns = {'SANAREA': 'Sanitation Area'})

# make a new col for geoID - data needs to have unique identifier index
data['geoid'] = data.index.astype(str)


# In[107]:


# create map instance
chm = folium.Map(location = [39.95300,-75.16355], zoom_start = 11,
              control_scale = True, tiles = 'cartodbpositron')
# plot choropleth map - geoid col needs to be assigned as the first col
folium.Choropleth(geo_data = data, data = data, 
                columns = ['geoid', 'Sanitation Area'],
                 key_on = 'feature.id',
                 fill_color = 'YlOrRd',
                highlight = True,
                   legend_name = 'Sanitation Areas In Philadelphia (Source: Open Philly Data)' , 
                 line_weight = 0).add_to(chm)

chm


# ## Tooltips
# Add tooltips, we can add tooltips to our map when plotting the polygons as GeoJson objects using the GeoJsonTooltip feature.

# In[110]:


# Convert points to GeoJson
folium.features.GeoJson(data,  
                        name='Labels',
                        style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
                        tooltip=folium.features.GeoJsonTooltip(fields=['Sanitation Area'],
                                                                aliases = ['Sanitation Area:'],
                                                                labels=True,
                                                                sticky=False
                                                                            )
                       ).add_to(chm)
chm


# In[111]:


outfp = "choropleth_map.html"
chm.save(outfp)

