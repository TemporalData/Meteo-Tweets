#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import bokeh
from bokeh.models import ColumnDataSource
import pyproj
from pyproj import Transformer


# In[2]:


#Loading twitter data into the python environment

twitter_data = pd.read_csv("complete_swiss_dataset.csv",encoding = "ISO-8859-15")


# In[3]:


twitter_data.head()


# In[4]:


for i in range(0,len(twitter_data.columns)):
    print(twitter_data.columns[i])


# In[5]:


time_data = twitter_data[['created_at_CET','Overall.score']].sort_values(by='created_at_CET',ignore_index=True)


# In[6]:


time_data.head()


# In[7]:


twitter_data['created_at_CET'][921301]


# In[8]:


twitter_data[['latitude','longitude']].head()


# In[31]:


coord_data = twitter_data[['latitude','longitude']]
coord_data = coord_data.round(3)


# In[10]:


coord_data.head()


# In[23]:


from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider

output_file("tile.html")

tile_provider = get_provider(CARTODBPOSITRON)

# range bounds supplied in web mercator coordinates
p = figure(x_range=(650000, 1200000), y_range=(5700000, 6100000),
           x_axis_type="mercator", y_axis_type="mercator", plot_width=1000)
p.add_tile(tile_provider)

transformer = Transformer.from_crs("epsg:4326", "EPSG:3857")

merc_coord = transformer.transform(coord_data['latitude'].values,
                            coord_data['longitude'].values)

source = ColumnDataSource(data=dict(longitude=merc_coord[0], latitude=merc_coord[1]))

p.circle(x='longitude', y='latitude', size=1, color="black", alpha=0.7, source=source)

#show(p)


# In[12]:


from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider

output_file("tile.html")

tile_provider = get_provider(CARTODBPOSITRON)

# range bounds supplied in web mercator coordinates
p = figure(x_range=(650000, 1200000), y_range=(5700000, 6100000),
           x_axis_type="mercator", y_axis_type="mercator",
           plot_width=1000)
p.add_tile(tile_provider)

transformer = Transformer.from_crs("epsg:4326", "EPSG:3857")

coord_data_no_dup = coord_data.drop_duplicates()

merc_coord_no_dup = transformer.transform(coord_data_no_dup['latitude'].values,
                                   coord_data_no_dup['longitude'].values)

source = ColumnDataSource(data=dict(longitude=merc_coord_no_dup[0], latitude=merc_coord_no_dup[1]))

p.circle(x='longitude', y='latitude', size=1, color="black", alpha=0.7, source=source)

show(p)


# In[13]:


CH = ((6,  11), (45.5, 48))

from datashader.utils import lnglat_to_meters as webm
x_range,y_range = [list(r) for r in webm(*CH)]

plot_width  = int(3096)
plot_height = int(plot_width*7.0/12)


# In[24]:


import datashader as ds, datashader.transfer_functions as tf, numpy as np
from datashader import spatial

background = "black"

from functools import partial
from datashader.utils import export_image
from datashader.colors import colormap_select, Greys9
from IPython.core.display import HTML, display

export = partial(export_image, background = background, export_path="export")
cm = partial(colormap_select, reverse=(background!="black"))

cvs = ds.Canvas(plot_width, plot_height, *webm(*CH))

#Formatting merc_coord for datashader
merc_coord_ds = pd.DataFrame(np.array(merc_coord).T)
merc_coord_ds.columns = ['latitude','longitude']


agg = cvs.points(merc_coord_ds, 'latitude', 'longitude')
export(tf.shade(agg, cmap = cm(Greys9,0.25), how='linear'),"census_gray_linear")


# In[25]:


export(tf.shade(agg, cmap = cm(Greys9,0.2), how='eq_hist'),"census_gray_eq_hist")


# In[26]:


from colorcet import fire
export(tf.shade(agg, cmap = cm(fire,0.2), how='eq_hist'),"census_ds_fire_eq_hist")


# In[18]:


import holoviews as hv, geoviews as gv, geoviews.tile_sources as gts
from holoviews.operation.datashader import datashade, dynspread
from holoviews import opts
hv.extension('bokeh')

opts.defaults(
    opts.Overlay(width=900, height=525, xaxis=None, yaxis=None))


# In[27]:


points = hv.Points(gv.Dataset(merc_coord_ds, kdims=['latitude', 'longitude']))


# In[28]:


population = dynspread(datashade(points, cmap=fire, element_type=gv.Image))


# In[30]:


population = dynspread(datashade(points, cmap=fire, element_type=gv.Image))
gts.EsriImagery() * population


# In[ ]:




