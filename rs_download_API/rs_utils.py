import os
import requests
from google.cloud import bigquery
from google.oauth2 import service_account
import urllib
import folium
from folium.plugins import MeasureControl, Draw, MousePosition

def query_sentinel(key_json, project_id, start, end, tile, cloud=100.):
    BASE_URL = 'http://storage.googleapis.com/'
    credentials = service_account.Credentials.from_service_account_file(key_json)
    client = bigquery.Client(credentials=credentials, project=project_id)
    query = client.query("""
                SELECT * FROM `bigquery-public-data.cloud_storage_geo_index.sentinel_2_index` 
                    WHERE mgrs_tile IN ("{t}") 
                    AND DATE(sensing_time) BETWEEN DATE("{s}") AND DATE("{e}")
                """.format(t=tile, s=start, e=end))
    results = query.result()
    df = results.to_dataframe()
    good_scenes = []
    for i, row in df.iterrows():
        print (row['product_id'], '; cloud cover:', row['cloud_cover'])
        if float(row['cloud_cover']) <= cloud:
            good_scenes.append(row['base_url'].replace('gs://', BASE_URL))
    return good_scenes

def download_file(url, dst_name):
    try:
        data = requests.get(url, stream=True)
        with open(dst_name, 'wb') as out_file:
            for chunk in data.iter_content(chunk_size=100 * 100):
                out_file.write(chunk)
    except:
        print ('\t ... {f} FAILED!'.format(f=url.split('/')[-1]))
    return

def make_safe_dirs(scene, outpath):
    scene_name = os.path.basename(scene)
    scene_path = os.path.join(outpath, scene_name)
    manifest = os.path.join(scene_path, 'manifest.safe')
    manifest_url = scene + '/manifest.safe'
    if os.path.exists(manifest):
        os.remove(manifest)
    download_file(manifest_url, manifest)
    with open(manifest, 'r') as f:
        manifest_lines = f.read().split()
    download_links = []
    load_this = False
    for line in manifest_lines:
        if(len(manifest_lines)>1600): 
            if 'href' in line:
                online_path = line[7:line.find('><')]
                tile = scene_name.split('_')[-2]
                if online_path.startswith('/GRANULE/'):
                    if '_' + tile + '_' in online_path:
                        load_this = True
                else:
                    load_this = True
                if load_this:
                    local_path = os.path.join(scene_path, *online_path.split('/')[1:])
                    online_path = scene + online_path
                    download_links.append((online_path, local_path))
        else:
            if 'href' in line:
                online_path = line[7:line.find('><') - 2]
                tile = scene_name.split('_')[-2]
                if online_path.startswith('/GRANULE/'):
                    if '_' + tile + '_' in online_path:
                        load_this = True
                else:
                    load_this = True
                if load_this:
                    local_path = os.path.join(scene_path, *online_path.split('/')[1:])
                    online_path = scene + online_path
                    download_links.append((online_path, local_path))
        load_this = False
    for extra_dir in ('AUX_DATA', 'HTML','rep_info'):
        if not os.path.exists(os.path.join(scene_path, extra_dir)):
            os.makedirs(os.path.join(scene_path, extra_dir))
        if(extra_dir == 'rep_info'):
            url = scene +'/rep_info/S2_User_Product_Level-1C_Metadata.xsd'
            urllib.request.urlretrieve(url, os.path.join(scene_path, extra_dir)+'/S2_User_Product_Level-1C_Metadata.xsd')

    return download_links

def download_sentinel(scene, dst):
    scene_name = scene.split('/')[-1]
    scene_path = os.path.join(dst, scene_name)
    if not os.path.exists(scene_path):
        os.mkdir(scene_path)
    print ('Downloading scene {s} ...'.format(s=scene_name))
    download_links = sorted(make_safe_dirs(scene, dst))
    p = []
    for l in download_links:
        if not os.path.exists(os.path.dirname(l[1])):
            os.makedirs(os.path.dirname(l[1]))
        if os.path.exists(l[1]):
            os.remove(l[1])
        if l[1].endswith('.jp2'):
            print ('\t ... *{b}'.format(b=l[1].split('_')[-1]))
        if download_file(l[0], l[1]) is False:
            print ('\t ... {f} failed to download! Download for this scene is cancelled here!'.format(f=l[0]))       

def draw_map(zoom):
    base_map = folium.Map(location=[37.9838, 23.7275],tiles='cartodbpositron',zoom_start = zoom) 
    MousePosition().add_to(base_map)
    base_map.add_child(MeasureControl())

    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

    MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lng_first=True,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(base_map)

    outjson = 'mydata.geojson'
    draw = Draw(export=True, filename = outjson, position='topleft',
        draw_options={'polyline':False,'marker':False, 'circlemarker':False},
        edit_options={'poly': {'allowIntersection': False}})
    draw.add_to(base_map)
    base_map.save('./examplemap.html')
    return base_map