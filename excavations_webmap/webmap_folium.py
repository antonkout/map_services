'''
The following script prepares the data provided in a geojson format in order
to be presented in an interactive webapp. The data refer to the excavation sites of the 
Amfissa region.

author: Antonios Koutroumpas
email: antkoutrou@protonmail.com
'''

import folium
import fiona
from folium.plugins import Fullscreen, FastMarkerCluster, MeasureControl
import json
from pathlib import Path 
import base64

def create_popup_content(category, description, xronologia, apo, mexri, evrimata, bibliografia, thesi, arxaiologos, id, img_files):
    '''
    Generates HTML content for a popup window with archaeological information.

    Parameters:
    - category (str): The category of the archaeological find.
    - description (str): A detailed description of the archaeological find.
    - xronologia (str): The chronological period of the find.
    - apo (str): The starting date of the find.
    - mexri (str): The ending date of the find.
    - evrimata (str): Discoveries associated with the find.
    - bibliografia (str): Bibliographic references related to the find.
    - thesi (str): The geographical location of the find.
    - arxaiologos (str): The archaeologist associated with the find.
    - id (str): The unique identifier of the find.
    - img_files (list): A list of file paths to images associated with the find.
    '''
    popup_content = f"""
                            <div style="text-align: center;"><h3><b>{category}</b></h3></div>
                            <div style="text-align: right;">{xronologia}, </div>
                            <div style="text-align: right;">{apo} - {mexri}</div><br>
                            <div style="text-align: center;"><u>Περιγραφή</u></div>
                            {description}<br><br>    
                    """
    for file_path in img_files:
        path = Path(file_path)
        if path.stem == id:
            selected_file = file_path
            with open(selected_file, 'rb') as image_file:
                image_data = image_file.read()
            # Encode the image data in base64
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            popup_content = popup_content + f"""<div style="text-align: center;">
                <img src="data:image/jpeg;base64,{encoded_image}" alt="Image" width="350px"><br><br>
            </div>""" 

    if evrimata is not None and evrimata != '-' and evrimata != "":
        popup_content = popup_content + f"""
                                        <div style="text-align: center;"><u>Ευρήματα</u></div>
                                        {evrimata}<br><br>
                                        """
        
    popup_content = popup_content + f"""
                                    <div style="text-align: center;">Αρχαιολόγος: <b>{arxaiologos}</b></div><br><br> 
                                    <div style="text-align: right;"><small>&#x1F4CD; {thesi}</small></div>
                                    <div style="text-align: right;"><small>&#x1F4D6; {bibliografia}</small></div>
                                    """
    
    return popup_content

def input_vector(geojson_path, desname, feature_group, colorn):
    '''
    This function takes a geojson path and inputs it in an existing 
    previously generated map

    Parameters:
        geojson_path: str. Path to geojson file
        desname: str. Name to be displayed on the map
        feature_group: folium.featuregroup. Feature group that belongs
        colorn: str. Color to use for visualization
    '''

    with fiona.open(geojson_path, 'r') as file:
        features = list(file)

    name = geojson_path.split('/')[-1].split('.')[0].split('_')[-1]

    for feature in features:
        geometry = feature['geometry']
        properties = feature['properties']

        element = folium.GeoJson(geometry, name=desname, style_function=lambda x: {"fillColor": colorn, "color": "lightgray"}, overlay=True, control=True, show=False)
        popup_style = 'font-size: 15px;'  # Adjust the font size as needed
        popup_content = f'<div style="{popup_style}"><b>{desname}</b>: {properties["description"]}</div>'
        if 'bibliography' in properties:
            popup_content = popup_content + f'<br><br><div style="text-align: right;"><small>&#x1F4D6; {properties["bibliography"]}</small></div>'
        popup = folium.Popup(popup_content, min_width=500, max_width=600)
        element.add_child(popup)
        element.add_to(feature_group)

    return element


def default_map(landmarks:True, properties, geometry, category_colors, category_icons):
    '''
    This function creates an empty folium map, with specific parameters
    in order to display the landmarks.

    Parameters
        landmarks: bool. Whether to load landmarks or not.
    '''

    ''' 1. Set up a map '''
    map = folium.Map(location=(38.527, 22.378), tiles=None, 
                width = '100%', height='100%', 
                prefer_canvas=False, control_scale=True, control=False,
                min_zoom=13, max_zoom=30)
    map.fit_bounds([[38.5118, 22.3584], [38.5437, 22.3979]])

    '''2. Add map widgets to improve user experience'''
    # Add the Fullscreen control to the map
    fullscreen = Fullscreen()
    map.add_child(fullscreen)

    '''3. Add the desired FIXED feature groups'''
    # Add multiple basemaps into a unique Feature Group
    feature_group1 = folium.map.FeatureGroup(name='Υπόβαθρο Χάρτη', show = True)
    # Add Google Maps tile layer
    tile_url = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}'
    tile1 = folium.TileLayer(tile_url, attr="Google Maps", name="Google Maps")
    tile1.add_to(feature_group1)
    # Add base map tile layer - ArcGIS World Imagery
    tile_url1 = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
    tile2 = folium.TileLayer(tile_url1, attr='Tiles &copy; Esri', name='Satellite')
    tile2.add_to(feature_group1)
    # Add base map tile layer - OpenTopoMap
    tile_url2 = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
    tile3 = folium.TileLayer(tile_url2, attr='OpenTopoMap', name="OpenTopoMap")
    tile3.add_to(feature_group1)
    tile4 = folium.TileLayer('cartodb positron', name="Cartodb")
    tile4.add_to(feature_group1)
    feature_group1.add_to(map)

    # Add the infrastructure to basemap
    feature_group2 = folium.map.FeatureGroup(name='Υποδομή', show = True)
    # Add roads of amfissa
    roads = input_vector("./data/amfissa_roads.geojson", "Οδικό Δίκτυο", feature_group2, "darkblue")
    # Add the buildings polygons
    buildings = input_vector("./data/amfissa_buildings.geojson", "Αστικό Δίκτυο", feature_group2, "darkorange")
    # Add the ancient wall
    wall = input_vector("./data/ancient_wall.geojson", "Αρχαία Οχύρωση", feature_group2, "darkred")
    # Add the ancient fortess
    fortess = input_vector("./data/ancient_fortess.geojson", "Αρχαίο Κάστρο", feature_group2, "darkgreen")
    # Place Feature Group to map
    feature_group2.add_to(map)

    # Load images directory
    img_dir = Path.cwd() / "photos"
    # Filter the files in the directory by extension
    img_files = [str(file) for file in img_dir.iterdir() if file.suffix.lower() in ['.jpg', '.jpeg']]
    
    '''4. Add the desired NON-FIXED feature groups'''
    if landmarks:
        feature_group3 = folium.map.FeatureGroup(name='Σημεία Ενδιαφέροντος', show = True)
        # Create layer groups for each category
        category_layers = {}
        for category in category_colors:
            category_layers[category] = folium.FeatureGroup(name=category)
            category_layers[category].add_to(map)

        # Filter out only the Folium elements
        folium_groups = {
            key: value
            for key, value in category_layers.items()
            if isinstance(value, folium.map.FeatureGroup)
        }
        ls = list()
        for _, value in folium_groups.items():
            ls.append(value)

        # Create a MarkerCluster layer
        # Create a MarkerCluster for each category
        category_clusters = {}

        for m, property in enumerate(properties):
            category = property['category']
            description, xronologia, apo, mexri, evrimata, arxaiologos = (
                property['description'],
                property['xronologia'],
                property['from'],
                property['until'],
                property['evrimata'],
                property['arxaiologos'],
            )
            bibliografia, thesi, id = property['bibliografia'], property['thesi'], str(property['id'])
            color = category_colors.get(category, 'gray')
            icon = category_icons.get(category, 'info-sign')
            # Define what to be displayed in the popup window
            popup_content = create_popup_content(
                category, description, xronologia, apo, mexri, evrimata, bibliografia, thesi, arxaiologos, id, img_files
            )
            iframe = folium.IFrame(popup_content)
            popupwin = folium.Popup(iframe, min_width=500, max_width=600)
            marker = folium.Marker(
                location=[geometry[m]['coordinates'][1], geometry[m]['coordinates'][0]],
                name=category,
                popup=popupwin,
                icon=folium.Icon(color=color, icon='location-pin', prefix='fa-solid')
            )

            # Check if a FastMarkerCluster for the category already exists, otherwise create a new one
            if category in category_clusters:
                marker_cluster = category_clusters[category]
            else:
                marker_cluster = FastMarkerCluster([], options={'spiderfyOnMaxZoom': True, 'showCoverageOnHover': False, 'zoomToBoundsOnClick': True}, name=category)
                category_clusters[category] = marker_cluster

            # Add the marker to the corresponding category FastMarkerCluster
            marker_cluster.add_child(marker)

        # Add the FastMarkerClusters to the category_layers
        for category, marker_cluster in category_clusters.items():
            marker_cluster.add_to(category_layers[category])

    '''5. Add everything to the webmap'''
    # Create lists of layer objects for each group
    group1_layers = [tile1, tile2, tile3, tile4]
    group2_layers = [roads, buildings, wall, fortess]
    group3_layers = ls.copy()

    # Add layer control to the map
    group1 = {
        f'<u>Υπόβαθρο Χάρτη</u>': group1_layers,
    }
    group2 = {
        f'<u>Υποδομή</u>': group2_layers,
    }
    group3 = {
        f'<u>Σημεία Ενδιαφέροντος</u>': group3_layers,
    }

    grouped_control1 = folium.plugins.GroupedLayerControl(group1, 
                                                          position='bottomleft', 
                                                          collapsed=False, 
                                                          sortLayers=False, 
                                                          exclusive_groups=True)

    grouped_control2 = folium.plugins.GroupedLayerControl(group2, 
                                                          position='topright', 
                                                          collapsed=False, 
                                                          sortLayers=False, 
                                                          exclusive_groups=False)
    
    grouped_control3 = folium.plugins.GroupedLayerControl(group3, 
                                                          position='bottomright', 
                                                          collapsed=False, 
                                                          sortLayers=False, 
                                                          exclusive_groups=False)
    

    map.add_child(grouped_control1)
    map.add_child(grouped_control2)
    map.add_child(grouped_control3)
    outpath = "./excavations_map.html"
    map.save(outpath)

    return outpath


# Read the data for the webmap
file_path = './data/excavation_ruins.geojson'
geometry, properties = [], []
with fiona.open(file_path) as src:
    for feature in src:
        # Process each feature as needed
        geometry.append(feature['geometry'])
        properties.append(feature['properties'])

# Load the JSON file
with open('./data/categories.json', 'r') as file:
    data = json.load(file)

 # Access the dictionaries
category_colors = data['category_colors']
category_icons = data['category_icons']

map = default_map(True, properties, geometry, category_colors, category_icons)