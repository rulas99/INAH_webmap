#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt

from folium.plugins import MarkerCluster
import folium
from folium import plugins


# In[14]:


pol=gpd.read_file('zip://Datos/Poligonos.zip') # Poligonos de zonas arqueologicas 181

zaap=gpd.read_file('zip://Datos/ZAAP.zip') # Zonas arquelogicas abiertas al publico 194

zagv=gpd.read_file('zip://Datos/ZAGV.zip') # Zonas NO abiertas al público 138

vis=gpd.read_file('zip://Datos/ZA_VISIT_2019.zip')


# In[22]:


camp = pd.read_csv('Datos/Nombre_campos_Bd.csv') 


# In[24]:


campos=[]
for i in (pol,zaap,zagv,vis):
    campos+=list(i.columns)


# In[25]:


catalogo=dict()

for i in campos:
    try:
        Nombre = camp[camp.Campo==i]["Nombre"].iloc[0]
    except: 
        Nombre = i
    
    catalogo[i]=Nombre


# In[48]:


google="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
gattr="<a href=https://www.google.com/maps/@24,-101.4,3274426m/data=!3m1!1e3/>Google Maps</a>"
esri="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


# In[18]:


ls=list(pol.columns)[1:-6]
ls.append(list(pol.columns)[-3])


# In[392]:


mapa = folium.Map(location=[24, -101.4], zoom_start=5.49,tiles=None,height="91%",control_scale=True)
folium.TileLayer(tiles=google,attr=gattr, name='Google Hibryd').add_to(mapa)

za=folium.FeatureGroup(name="Zonas arqueológicas", show=True)
mapa.add_child(za)

pol["color"]="#FFE801"
zajson=pol.to_json()

folium.GeoJson(zajson,tooltip=folium.GeoJsonTooltip(fields=ls,aliases=[catalogo[i]+": " for i in ls]),
               style_function=lambda x: {'color' : x['properties']['color'],'opacity': 0.5,'fillColor' :"#E8FF00",
                                            }).add_to(za)

fg1=folium.FeatureGroup(name='Zonas abiertas al público', show=False)
mapa.add_child(fg1)

mc = MarkerCluster()

for row in zaap.itertuples():
    
    cols=[catalogo[i] for i in zaap.columns][1:-1]
    dat=[row[i] for i in range(2,len(row)-1)]
    
    popup_df = pd.DataFrame({"CAMPO":cols,"VALOR":dat}).drop(index=[28,29])
    popup_html = popup_df.to_html(classes='table table-hover table-responsive-sm text-center', index=False, 
                                  header=False,justify='center')
   
    if row.NOM_CED==None:
        nom="Sin nombre"
    else:
        nom=row.NOM_CED
        
    mc.add_child(folium.Marker(location=[row.LATITUD,  row.LONGITUD],
                 popup=folium.map.Popup(popup_html,min_width=200,max_width=400,min_height=100,max_height=400),
                               tooltip='Zona abierta al público',icon=folium.Icon(color='blue', icon='angle-double-down',prefix='fa')))
    #folium.map.Tooltip()


fg1.add_child(mc)

fg2=folium.FeatureGroup(name='Zonas con un grado de vista', show=False)

for row in zagv.itertuples():
    
    cols2=[catalogo[i] for i in zagv.columns][1:-1]
    dat2=[row[i] for i in range(1,len(row))][1:-1]
    
    popup_df2 = pd.DataFrame({"CAMPO":cols2,"VALOR":dat2}).drop([19,18])
    popup_html2 = popup_df2.to_html(classes='table table-hover table-responsive-sm text-center', index=False, 
                                  header=False,justify='center',)
   
        
    fg2.add_child(folium.Marker(location=[row.LATITUD,  row.LONGITUD],
                 popup=folium.map.Popup(popup_html2,min_width=200,max_width=400,min_height=100,max_height=400),
                               tooltip='Zonas con un grado de vista',icon=folium.Icon(color='red', icon='angle-double-down',prefix='fa')))

mapa.add_child(fg2)

fg3=folium.FeatureGroup(name='Visitantes', show=False)

for i in vis.itertuples():
    if i.T_2019==0:
        r=1
    elif i.T_2019<1000:
        r=2+i.T_2019/100
    elif i.T_2019<100000:
        r=10+i.T_2019/10000
    elif i.T_2019<1000000:
        r=35+i.T_2019/100000
    else:
        r=90+i.T_2019/1000000
    
    ##print(i.T_2019,"  ",round(r))
    
    folium.Circle(
        location=[i.geometry.centroid.y, i.geometry.centroid.x],
        radius=r*200,
        #popup='Visitantes: {}'.format(i.T_2019),
        tooltip='{} visitantes en {}'.format(i.T_2019,i.ZA),
        color='pink',
        #fill=True,
        #fill_color='pink',
        ##fill_opacity=.1,
        ).add_to(fg3)

mapa.add_child(fg3)

#minimap=plugins.MiniMap(tile_layer="Stamen Terrain",toggle_display=True,height=100,width=100)
#mapa.add_child(minimap)
plugins.Fullscreen(position='bottomleft').add_to(mapa)
plugins.MousePosition(position='topright',prefix='Lat:',separator='  Lon: ').add_to(mapa)

measure_control = plugins.MeasureControl(position='topleft', 
                                 active_color='green', 
                                 completed_color='red', 
                                 primary_length_unit='meters',secondary_length_unit='kilometers',secondary_area_unit='hectares')
mapa.add_child(measure_control)

draw = plugins.Draw(export=True,position="topleft")
draw.add_to(mapa)

plugins.LocateControl().add_to(mapa)


folium.LayerControl("bottomleft").add_to(mapa)

tit1="<h1 class='text-center'>Zonas Arquelógicas abiertas al público.</h1>"

mapa.get_root().html.add_child(folium.Element(tit1))

mapa.save("index.html")

