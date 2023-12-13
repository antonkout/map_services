import dash
from dash import callback_context, dcc, html
from pyproj import CRS
import landsatxplore.api
from landsatxplore.earthexplorer import EarthExplorer
from dash.dependencies import Output, Input, State
from datetime import date
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import os
import folium
import geopandas
from shapely.geometry import Polygon
import pandas as pd
import numpy as np
from rs_utils import draw_map, download_sentinel

app = dash.Dash('download_imgs_API')
m = draw_map(zoom=4)

app.layout = html.Div(children=[
    html.Div(
        className="study-browser-banner row",
        children=[
            html.Div(
                className="div-logo",
                children=html.Img(
                    className="logo", src=app.get_asset_url("./Logo_RSLab_logo_LRn.png")
                ),
            ),
            html.H2(
                className="h2-title",
                children="RSLab NTUA | Search & Download Satellite products",
                style={
                    "text-align": "center",
                    "font-size": "18px",
                    "display": "inline-block",
                },
            ),
        ],
    ),
    html.Div(
        className="row",
        children=[
            html.Div(
                className="two columns div-user-controls",
                children=[
                    html.Br(),
                    html.Br(),
                    html.Label(
                        ["Select Satellite:"],
                        style={"font-weight": "bold"},
                    ),
                    html.P(),
                    dcc.Dropdown(
                        id="dropdown",
                        options=[
                            {"label": "Sentinel-1", "value": "S1"},
                            {"label": "Sentinel-2", "value": "S2"},
                            {"label": "Sentinel-3", "value": "S3"},
                            {"label": "Landsat-8", "value": "L8"},
                        ],
                        searchable=False,
                        clearable=False,
                        value="S2",
                    ),
                    html.P(),
                    html.Label(
                        ["Choose Time Range:"],
                        style={"font-weight": "bold"},
                    ),
                    html.P(),
                    html.Div(
                        [
                            dcc.DatePickerRange(
                                id="my-date-picker-range",
                                calendar_orientation="horizontal",
                                clearable=False,
                                stay_open_on_select=False,
                                style={
                                    "zIndex": 10,
                                    "font-size": "14px",
                                    "display": "inline-block",
                                    "border-radius": "2px",
                                    "border": "3px solid #ccc",
                                    "color": "#333",
                                    "border-spacing": "0",
                                    "border-collapse": "separate",
                                },
                                display_format="DD-MMM-YYYY",
                                min_date_allowed=date(2018, 1, 1),
                                max_date_allowed=date(2020, 12, 1),
                                initial_visible_month=date(2020, 1, 1),
                                start_date=date(2020, 1, 1),
                                end_date=date(2020, 1, 7),
                            )
                        ]
                    ),
                    html.Div(
                        [
                            html.P(),
                            html.Label(
                                ["Choose Maximum Cloudiness:"],
                                style={"font-weight": "bold"},
                            ),
                            html.P(),
                            dcc.Slider(
                                id="my-slider",
                                min=0,
                                max=100,
                                step=5,
                                value=10,
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                        ]
                    ),
                    html.Button(
                        children="Search",
                        id="btn-nclicks-2",
                        n_clicks=0,
                        style={"color": "#93A5AC", "width": "100%"},
                    ),
                    html.Br(),
                    html.Br(),
                    html.P(),
                    html.Label(
                        ["Please enter desired product:"],
                        style={"font-weight": "bold"},
                    ),
                    dcc.Input(
                        id="productid",
                        type="text",
                        placeholder="Desired product id",
                        style={"width": "100%"},
                    ),
                    html.Br(),
                    html.P(),
                    html.Label(
                        ["Please specify output folder:"],
                        style={"font-weight": "bold"},
                    ),
                    dcc.Input(
                        id="outputfolder",
                        type="text",
                        placeholder="Desired output folder",
                        style={"width": "100%"},
                    ),
                    html.Br(),
                    html.Br(),
                    html.Button(
                        children="Download",
                        id="download_button",
                        n_clicks=0,
                        style={"color": "#93A5AC", "width": "100%"},
                    ),
                ],
            ),
            html.Div(
                className="eight columns div-for-charts bg-black",
                children=[
                    html.Br(),
                    html.Br(),
                    html.Div(
                        children=[
                            html.Iframe(
                                id="map",
                                srcDoc=open("./examplemap.html", "r").read(),
                                # path to created webmap
                                width="100%",
                                height="500",
                            )
                        ]
                    ),
                    html.P(),
                    html.Label(
                        ["Products Found Text-Box"],
                        style={
                            "font-size": "16px",
                            "font-weight": "bold",
                            "text-align": "center",
                            "color": "#93A5AC",
                        },
                    ),
                    html.Div(
                        id="textarea",
                        style={
                            "whiteSpace": "pre-line",
                            "width": "100%",
                            "text-align": "center",
                            "display": "inline-block",
                            "border-radius": "1px",
                            "border": "2px solid #ccc",
                            "color": "#DBD0C0",
                            "border-spacing": "0",
                            "border-collapse": "separate",
                        },
                    ),
                    html.Div(
                        id="placeholder",
                        style={
                            "whiteSpace": "pre-line",
                            "width": "100%",
                            "text-align": "center",
                        },
                    ),
                ],
            ),
            html.Div(
                className="two columns div-for-charts bg-black",
                children=[
                    html.Br(),
                    html.Br(),
                    html.Label(
                        ["Enter Sci-Hub Credentials:"],
                        style={"font-weight": "bold"},
                    ),
                    html.P(),
                    dcc.Input(
                        id="username", type="text", placeholder="Username", debounce=True
                    ),
                    dcc.Input(
                        id="password", type="text", placeholder="Password", debounce=True
                    ),
                ],
            ),
        ],
    ),
])


@app.callback(
    [Output('map', 'srcDoc'),
    Output('textarea', 'children')],
    [Input('btn-nclicks-2', 'n_clicks'),
    State('dropdown', 'value'),
    State('my-date-picker-range', 'start_date'),
    State('my-date-picker-range', 'end_date'),
    State('my-slider', 'value'),
    State('username','value'),
    State('password','value')]
    )

def search(btn2,selecdrop,start_date, end_date,value,usr,pas):
    start_date_object = date.fromisoformat(start_date)
    start = start_date_object.strftime('%Y%m%d')
    end_date_object = date.fromisoformat(end_date)
    end = end_date_object.strftime('%Y%m%d')
    outdir = './outputdir'
    usr=str(usr)
    pas=str(pas) 
    geojson_path = os.getcwd() + '/mydata.geojson'

#Search Sentinel-2
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if btn2 is not None and btn2> 0 and selecdrop=='S2': 
        if 'btn-nclicks-2' in changed_id:
            api = SentinelAPI(usr, pas,'https://scihub.copernicus.eu/dhus') 
            startdate = start 
            enddate = end
            s=[]
            cloudcover = (0,value)
            
            footprint = geojson_to_wkt(read_geojson(geojson_path))
            pp = api.query(footprint,
                        date=(startdate, enddate),
                        platformname='Sentinel-2',
                        area_relation = 'Intersects',#Intersects
                        producttype= 'S2MSI1C',
                        cloudcoverpercentage=cloudcover,
                        processinglevel = 'Level-1C') #Level-1C because Level-2A we need to change google storage folder
            products = list(pp.items())
            areas = api.to_geodataframe(pp)
            base_map = draw_map(zoom=8)
            for _, r in areas.iterrows():
                sim_geo = geopandas.GeoSeries(r['geometry']).simplify(tolerance=0.001)
                geo_j = sim_geo.to_json()
                geo_j = folium.GeoJson(data=geo_j,
                                       style_function=lambda x: {'fillColor': 'orange'},
                                      zoom_on_click =True)
                html = '''<p align="center">Found product at date <strong>{}</strong> at tile <strong>{}</strong> with cloud percentage <strong>{}</strong></p>'''.format(r['ingestiondate'].strftime('%d-%m-%Y'),r['tileid'],str(np.round(r['cloudcoverpercentage'],2)))
                iframe = folium.IFrame(html,width=173,height=100)
                folium.Popup(iframe,max_width=200).add_to(geo_j)
                geo_j.add_to(base_map)

            folium.GeoJson(os.getcwd() + '/mydata.geojson', name="geojson").add_to(base_map)
            base_map.save('./examplemap.html')
            msg = open('./examplemap.html', 'r').read()
            
            for k in range(len(products)):
                string = 'Found product: {} with cloudcover percentage: {} \n'.format(products[k][1]['title'],np.round(products[k][1]['cloudcoverpercentage'],2))
                s.append(string)
            if (len(s)!=0):
                return msg, s

#Search Sentinel-1
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if btn2 is not None and btn2> 0 and selecdrop=='S1': 
        if 'btn-nclicks-2' in changed_id:
            api = SentinelAPI(usr, pas,'https://scihub.copernicus.eu/dhus') 
            startdate = start 
            enddate = end
            s=[]
            footprint = geojson_to_wkt(read_geojson(geojson_path))
            pp = api.query(footprint,
                        date=(startdate, enddate),
                        platformname='Sentinel-1',
                        producttype='SLC',
                        area_relation = 'Intersects') #Level-1C because Level-2A we need to change google storage folder
            products = list(pp.items())
            areas = api.to_geodataframe(pp)
            base_map = draw_map(zoom=8)
            for _, r in areas.iterrows():
                sim_geo = geopandas.GeoSeries(r['geometry']).simplify(tolerance=0.001)
                geo_j = sim_geo.to_json()
                geo_j = folium.GeoJson(data=geo_j,
                                       style_function=lambda x: {'fillColor': 'orange'},
                                      zoom_on_click =True)
                html = '''<p align="center">Found product at date <strong>{}</strong> with mission datatakeid: <strong>{}</strong></p>'''.format(r['ingestiondate'].strftime('%d-%m-%Y'),r['missiondatatakeid'])#s[-42:-35]
                iframe = folium.IFrame(html,width=173,height=100)
                folium.Popup(iframe,max_width=200).add_to(geo_j)
                geo_j.add_to(base_map)

            folium.GeoJson(os.getcwd() + '/mydata.geojson', name="geojson").add_to(base_map)
            base_map.save('examplemap.html')
            msg = open('./examplemap.html', 'r').read()
            
            for k in range(len(products)):
                string = 'Found product: {} with size {} \n'.format(products[k][1]['title'],products[k][1]['size'])
                s.append(string)
            if (len(s)!=0):
                return msg, s            
            
#Search Landsat-8            
    if btn2 is not None and btn2> 0 and selecdrop=='L8': 
        if 'btn-nclicks-2' in changed_id:
            api = landsatxplore.api.API(usr,pas)
            cloudcover = value
            dataset='landsat_8_c1'
            products = []
            startd = start[:4]+'-'+start[4:6]+'-'+start[6:]
            endd = end[:4]+'-'+end[4:6]+'-'+end[6:]
            s=[]
            area = read_geojson(geojson_path)['features'][0]["geometry"]["coordinates"][0]
            xmin, ymin, xmax, ymax  = pd.DataFrame(area).iloc[:,0].min(), pd.DataFrame(area).iloc[:,1].min(), pd.DataFrame(area).iloc[:,0].max(), pd.DataFrame(area).iloc[:,1].max()
            footprint = (xmin, ymin, xmax, ymax)
            tmp = api.search(dataset,start_date=startd,end_date=endd,max_cloud_cover=cloudcover, bbox = footprint)
            
            lon_list, lat_list, polygon = [], [], []
            
            base_map = draw_map(zoom=8)
            if(tmp!=[]):
                for p in range(len(tmp)):
                    products.append(tmp[p])
                    for k in range(len(tmp[p]['spatialCoverage']['coordinates'][0])):
                        lon_list.append(tmp[p]['spatialCoverage']['coordinates'][0][k][0])
                        lat_list.append(tmp[p]['spatialCoverage']['coordinates'][0][k][1])
                    polygon_geom = Polygon(zip(lon_list, lat_list))
                    crs = CRS("WGS84")
                    sim_geo = geopandas.GeoSeries(geopandas.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])['geometry'][0]).simplify(tolerance=0.001)
                    geo_j = sim_geo.to_json()
                    geo_j = folium.GeoJson(data=geo_j,
                                           style_function=lambda x: {'fillColor': 'orange'},
                                          zoom_on_click =True)
                    html = '''<p align="center">Found product at date <strong>{}</strong> at tile <strong>{}</strong> with cloud percentage <strong>{}</strong></p>'''.format(tmp[p]['publishDate'][:10],tmp[p]['displayId'][10:16],tmp[p]['cloudCover'])
                    iframe = folium.IFrame(html,width=173,height=100)
                    folium.Popup(iframe,max_width=200).add_to(geo_j)
                    geo_j.add_to(base_map)
            
            folium.GeoJson(os.getcwd() + '/mydata.geojson', name="geojson").add_to(base_map)
            base_map.save('examplemap.html')
            msg = open('./examplemap.html', 'r').read()
            
            for k in range(len(products)):
                string = 'Found product: {} with cloudcover percentage: {} at date: {} \n'.format(str(products[k]['entityId']),
                                                                                                  str(products[k]['cloudCover']),
                                                                                                  str(products[k]['date_l1_generated']))
                s.append(string)
            if (len(s)!=0):
                return msg, s    
        
#Search Sentinel-3
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if btn2 is not None and btn2> 0 and selecdrop=='S3': 
        if 'btn-nclicks-2' in changed_id:
            api = SentinelAPI(usr, pas,'https://scihub.copernicus.eu/dhus') 
            startdate = start 
            enddate = end
            s=[]
            footprint = geojson_to_wkt(read_geojson(geojson_path))
            pp = api.query(footprint,
                        date=(startdate, enddate),
                        platformname='Sentinel-3',
                        producttype='SL_1_RBT___',
                        area_relation = 'Intersects') 
            
            products = list(pp.items())
            areas = api.to_geodataframe(pp)
            base_map = draw_map(zoom=8)
            for _, r in areas.iterrows():
                sim_geo = geopandas.GeoSeries(r['geometry']).simplify(tolerance=0.001)
                geo_j = sim_geo.to_json()
                geo_j = folium.GeoJson(data=geo_j,
                                       style_function=lambda x: {'fillColor': 'orange'},
                                      zoom_on_click =True)
                html = '''<p align="center">Found product at date <strong>{}</strong></p>'''.format(r['ingestiondate'].strftime('%d-%m-%Y'))
                iframe = folium.IFrame(html,width=173,height=100)
                folium.Popup(iframe,max_width=200).add_to(geo_j)
                geo_j.add_to(base_map)

            folium.GeoJson(os.getcwd() + '/mydata.geojson', name="geojson").add_to(base_map)
            base_map.save('examplemap.html')
            msg = open('./examplemap.html', 'r').read()
            
            for k in range(len(products)):
                string = 'Found product: {} from platform identifier: {} \n'.format(products[k][1]['title'],products[k][1]['platformidentifier'])
                s.append(string)
            if (len(s)!=0):
                return msg, s
    else:
        raise dash.exceptions.PreventUpdate
    
@app.callback(
  [Output('placeholder', 'children')],
   [Input('download_button', 'n_clicks'),
   State('dropdown', 'value'),
   State('productid', 'value'),
   State('outputfolder', 'value'),
   State('username','value'),
   State('password','value')])

def download(btn,selecdrop,desired_prod,outdir,usr,pas):
    usr=str(usr)
    pas=str(pas) 
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if btn is not None and btn> 0 and selecdrop=='S2': 
        if 'download_button' in changed_id:
            s2_folder = outdir + '/Sentinel-2/'
        if not os.path.exists(s2_folder):
            os.mkdir(s2_folder)
            print ('Created S2-Folder Successfully!!')
        else:
            print ("Directory %s already exists" % s2_folder)

        print()
        t1 = desired_prod[-21:-19]
        t2 = desired_prod[-19:-18]
        t3 = desired_prod[-18:-16]
        download_url = 'http://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/'+t1+'/'+t2+'/'+t3+'/'+desired_prod+'.SAFE'
        download_sentinel(download_url, s2_folder)
        return ['Download Complete']
    
    elif btn is not None and btn> 0 and selecdrop=='S1': 
        if 'download_button' in changed_id:
            s1_folder = outdir + '/Sentinel-1/'
        if not os.path.exists(s1_folder):
            os.mkdir(s1_folder)
            print ('Created S1-Folder Successfully!!')
        else:
            print ("Directory %s already exists" % s1_folder)

        print()
        t1 = desired_prod[-21:-19]
        t2 = desired_prod[-19:-18]
        t3 = desired_prod[-18:-16]
        download_url = 'http://storage.googleapis.com/gcp-public-data-sentinel-2/tiles/'+t1+'/'+t2+'/'+t3+'/'+desired_prod+'.SAFE'
        download_sentinel(download_url, s2_folder)
        return ['Download Complete']
    
    
    elif btn is not None and btn> 0 and selecdrop=='S3': 
        if 'download_button' in changed_id:
            s3_folder = outdir + '/Sentinel-3/'
        if not os.path.exists(s3_folder):
            os.mkdir(s3_folder)
            print ('Created S3-Folder Successfully!!')
        else:
            print ("Directory %s already exists" % s3_folder)
            
    
    elif btn is not None and btn> 0 and selecdrop=='L8': 
        if 'download_button' in changed_id:
            ee = EarthExplorer(usr, pas)
            scene = str(desired_prod)
            outputdir = outdir + '/Landsat-8/'
            if not os.path.exists(outputdir):
                os.mkdir(outputdir)
                print ("Successfully created the directory %s " % outputdir)
            else:
                print ("Directory %s already exists" % outputdir)

            ee.download(scene_id=scene, output_dir=outputdir)
            ee.logout()
        return ['Download Complete']
    
    else:
        raise dash.exceptions.PreventUpdate

if __name__ == '__main__':    
    PORT = 8084 # Set the desired port number
    ADDRESS = '127.0.0.1'  # Set the desired IP address or leave it as None for the default address
    app.run_server(debug=True, use_reloader=False,port=PORT, host=ADDRESS)