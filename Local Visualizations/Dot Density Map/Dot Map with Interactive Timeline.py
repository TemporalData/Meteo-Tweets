#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import bokeh
from bokeh.models import ColumnDataSource
import pyproj
from pyproj import Transformer
from datetime import date,datetime


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


# In[9]:


coord_data = twitter_data[['latitude','longitude']]
coord_data = coord_data.round(3)


# In[10]:


coord_data.head()


# In[11]:


transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")


# In[12]:


from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, OSM, get_provider

output_file("tile.html")

tile_provider = get_provider(CARTODBPOSITRON)

# range bounds supplied in web mercator coordinates
p = figure(x_range=(650000, 1200000), y_range=(5700000, 6100000),
           x_axis_type="mercator", y_axis_type="mercator", plot_width=1000)
p.add_tile(tile_provider)

transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")

merc_coord = transformer.transform(coord_data['latitude'].values,
                            coord_data['longitude'].values)

source = ColumnDataSource(data=dict(longitude=merc_coord[0], latitude=merc_coord[1]))

p.circle(x='longitude', y='latitude', size=1, color="black", alpha=0.7, source=source)

#show(p)


# In[ ]:





# In[13]:


from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, OSM, get_provider

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


# In[14]:


CH = ((6,  11), (45.5, 48))

from datashader.utils import lnglat_to_meters as webm
x_range,y_range = [list(r) for r in webm(*CH)]

plot_width  = int(3096)
plot_height = int(plot_width*7.0/12)


# In[16]:


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


# In[17]:


export(tf.shade(agg, cmap = cm(Greys9,0.2), how='eq_hist'),"census_gray_eq_hist")


# In[18]:


from colorcet import fire
export(tf.shade(agg, cmap = cm(fire,0.2), how='eq_hist'),"census_ds_fire_eq_hist")


# In[ ]:


import holoviews as hv, geoviews as gv, geoviews.tile_sources as gts
from holoviews.operation.datashader import datashade, dynspread
from holoviews import opts
hv.extension('bokeh')

opts.defaults(
    opts.Overlay(width=900, height=525, xaxis=None, yaxis=None))


# In[ ]:


points = hv.Points(gv.Dataset(merc_coord_ds, kdims=['latitude', 'longitude']))


# In[ ]:


population = dynspread(datashade(points, cmap=fire, element_type=gv.Image))


# In[ ]:


population = dynspread(datashade(points, cmap=fire, element_type=gv.Image))
gts.EsriImagery() * population


# In[37]:


import yaml

from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, Button, TextInput, DateRangeSlider
from bokeh.plotting import figure
from bokeh.themes import Theme
from bokeh.io import show, output_notebook

output_notebook()


# In[28]:


dev_coord_data_time = twitter_data[['latitude','longitude','created_at_CET']]


# In[29]:


dev_coord_data_time = dev_coord_data_time.set_index(['created_at_CET'])


# In[30]:


dev_coord_data_time


# In[31]:


dev_coord_data_time.index = pd.to_datetime(dev_coord_data_time.index, format='%Y-%m-%d %H:%M:%S')


# In[32]:


dev_coord_data_time = dev_coord_data_time.sort_index()


# In[40]:


def bkapp(doc):

    tile_provider = get_provider(CARTODBPOSITRON)

    # range bounds supplied in web mercator coordinates
    p = figure(x_range=(650000, 1200000), y_range=(5700000, 6100000),
               x_axis_type="mercator", y_axis_type="mercator")
    p.add_tile(tile_provider)

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857")

    dev_merc_coord = transformer.transform(dev_coord_data_time['latitude']['2015-1-1':'2015-2-1'].values,
                                dev_coord_data_time['longitude']['2015-1-1':'2015-2-1'].values)

    source = ColumnDataSource(data=dict(longitude=dev_merc_coord[0], latitude=dev_merc_coord[1]))

    p.circle(x='longitude', y='latitude', size=1, color="black", alpha=0.7, source=source)
    
    def callback(attr, old, new):
        
        start_date = date.fromtimestamp(new[0]/1000)
        
        end_date = date.fromtimestamp(new[1]/1000)
        
        dev_merc_coord = transformer.transform(dev_coord_data_time['latitude'][start_date:end_date].values,
                                               dev_coord_data_time['longitude'][start_date:end_date].values)
        
        source.data = dict(longitude=dev_merc_coord[0], latitude=dev_merc_coord[1])
        

    date_slider = DateRangeSlider(title="Date Range: ", start=date(2015, 1, 1),
                                 end=date(2018,9,6), value=(date(2015, 1, 1), date(2015, 12, 31)), step=1)
    
    date_slider.on_change('value', callback)
    
    def my_button_handler(new):
        
        start_date = start_date_input.value
        
        end_date = end_date_input.value
        
        dev_merc_coord = transformer.transform(dev_coord_data_time['latitude'][start_date:end_date].values,
                                               dev_coord_data_time['longitude'][start_date:end_date].values)
        
        source.data = dict(longitude=dev_merc_coord[0], latitude=dev_merc_coord[1])

    button = Button(label="Update", button_type="success")

    button.on_click(my_button_handler)
    
    start_date_input = DatePicker(value="2015-01-01", title="Start Date:")
    
    end_date_input = DatePicker(value="2015-02-01", title="End Date:")

    doc.add_root(row(column(p),column(start_date_input,end_date_input,button)))


# In[41]:


show(bkapp)


# In[35]:


from bokeh.io import output_file, show
from bokeh.models import DatePicker

output_file("date_picker.html")

color_picker = DatePicker(title='Test',value="2015-01-01")

show(color_picker)


# In[ ]:


start_date = date.fromisoformat(start_date_input.value)
        
        end_date = date.fromisoformat(end_date_input.value)
        
        dev_merc_coord = transformer.transform(dev_coord_data_time['latitude'][start_date:end_date].values,
                                               dev_coord_data_time['longitude'][start_date:end_date].values)
        
        source.data = dict(longitude=dev_merc_coord[0], latitude=dev_merc_coord[1])

