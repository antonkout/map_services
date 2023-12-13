import dash
from dash import html
from dash.dependencies import Output, Input
from dash import dcc
import json
import fiona

with open('./data/appstyles.json', 'r') as file:
    data = json.load(file)
    
with open('./data/marks_rangeslider.json', 'r') as file:
    marks = json.load(file)

with open('./data/marks_dropdown.json', 'r') as file:
    dropdict = json.load(file)

with open('./data/categories.json', 'r') as file:
    categ = json.load(file)

with open('./data/timeline_dic.json', 'r') as file:
    timeline = json.load(file)

# SIDEBAR_STYLE = data['SIDEBAR_STYLE']
TOPBAR_STYLE = data['TOPBAR_STYLE']
CONTENT_STYLE = data['CONTENT_STYLE']

image_path1 = 'assets/my-image.png'
image_path2 = 'assets/upourgeio.png'
webmap_path = "./excavations_map.html"

# Define the sidebar
sidebar = html.Div(
    className='top-bar',
    children=[
        html.Img(src=image_path1, className="sidebar-image", style={'float': 'left', 'margin-right': '10px', 'width': '2.5%'}),
        # html.Hr(),
        html.P("Διαδραστικός Χάρτης ανασκαφών στην περιοχή της Άμφισσας", className="lead", style={'text-align': 'center', 'font-size': '20px', 'font-family':'century','text-decoration': 'underline'}),
        # html.Hr(),
        html.Div(
            className='checklist',
            style={'float': 'right','text-align': 'left', 'margin-right': '5px', 'margin-top': '-45px'},
            children=[
                dcc.Dropdown(
                            id = 'dropdown',
                            style={'width': '300px', 'z-index': '9999'},
                            options=[
                                {
                                    "label": html.Span(['Πρωτοελλαδική περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Πρωτοελλαδική περίοδος"
                                },
                                {
                                    "label": html.Span(['Γεωμετρική περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Γεωμετρική περίοδος"
                                },
                                {
                                    "label": html.Span(['Αρχαϊκή περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Αρχαϊκή περίοδος"
                                },
                                {
                                    "label": html.Span(['Κλασική περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Κλασική περίοδος"
                                },
                                {
                                    "label": html.Span(['Ελληνιστική περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Ελληνιστική περίοδος"
                                },
                                {
                                    "label": html.Span(['Ρωμαϊκή περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Ρωμαϊκή περίοδος"
                                },
                                {
                                    "label": html.Span(['Αυτοκρατορικοί χρόνοι'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Αυτοκρατορικοί χρόνοι"
                                },
                                {
                                    "label": html.Span(['Μεσαιωνικοί χρόνοι'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Μεσαιωνικοί χρόνοι"
                                },
                                {
                                    "label": html.Span(['Παλαιοχριστιανικοί χρόνοι'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Παλαιοχριστιανικοί χρόνοι"
                                },
                                {
                                    "label": html.Span(['Μέση Βυζαντινή περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Μέση Βυζαντινή περίοδος"
                                },
                                {
                                    "label": html.Span(['Ύστεροβυζαντινή περίοδος'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Ύστεροβυζαντινή περίοδος"
                                },
                                {
                                    "label": html.Span(['Οθωμανικοί χρόνοι'], style={'color': 'black', 'font-size': 16, 'font-family':'Roboto'}),
                                    "value": "Οθωμανικοί χρόνοι"
                                },
                            ],
                            value='Πρωτοελλαδική περίοδος'
                        )
            ]
        ),
   
    ],
    style=TOPBAR_STYLE,
)
content = html.Div(
    id="page-content",
    children=[
        html.Div(
            className='map',
            children=[html.Iframe(id='map', srcDoc=open(webmap_path, 'r').read(), width='100%', height='810')]
        ),

        html.Div(
            className="row",
            style={'justify-content': 'center'},
            children=[
                html.Div(
                    className="col-md-12",
                    style={'margin-top': '20px'},
                    children=[
                        dcc.RangeSlider(
                            id='range-slider',
                            min=-3500,
                            max=1821,
                            value=[-3500, 1821],
                            marks=marks,
                            allowCross=False,
                            dots=False,
                            step=None,
                            tooltip={"placement": "bottom", "always_visible": False}
                        )
                    ]
                )
            ]
        )
    ],
    style=CONTENT_STYLE
)

app = dash.Dash('excavations_API', external_stylesheets=[{'href': '/static/styles.css', 'rel': 'stylesheet'}])
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

@app.callback(
    Output('map', 'srcDoc'),
    Input('range-slider', 'value')
)
def update_map_and_slider(range_values):
    from webmap_folium import default_map

    min_value, max_value = range_values[0], range_values[1]

    file_path = './data/excavation_ruins.geojson'

    geometry, properties = [], []
    with fiona.open(file_path, 'r') as src:
        for feature in src:
            # Process each feature as needed
            geometry.append(feature['geometry'])
            properties.append(feature['properties'])

    timeline_dic = timeline['timeline_dic_n']
    category_colors = categ['category_colors']
    category_icons = categ['category_icons']

    user_range = [timeline_dic.get(str(min_value)), timeline_dic.get(str(max_value))]
    
    subset_features = []
    for geom, props in zip(geometry, properties):
        from_id = props['from_id']
        until_id = props['until_id']

        if len(user_range) > 1:
            if from_id >= user_range[0] and until_id <= user_range[1]:
                subset_features.append({'geometry': geom, 'properties': props})
        else:
            if from_id == user_range[0]:
                subset_features.append({'geometry': geom, 'properties': props})

    subset_geometry, subset_properties = [], []
    for feature in subset_features:
        # Process each feature as needed
        subset_geometry.append(feature['geometry'])
        subset_properties.append(feature['properties'])

    # Create a Folium Map
    webmap_path = default_map(True, subset_properties, subset_geometry, category_colors, category_icons)

    return open(webmap_path, 'r').read()

@app.callback(
    Output('range-slider', 'value'),
    Input('dropdown', 'value'),
    prevent_initial_call=True
)
def update_map_dropdown(selected_value):
    user_range = dropdict[selected_value]
    timeline_dic = timeline['timeline_dic_n']
    keys = [key for key, value in timeline_dic.items() if value == user_range[0] or value == user_range[1]]
    selected_marks = {key: marks[key] for key in keys if key in marks}

    # Get the minimum and maximum keys from selected_marks
    min_key = min(selected_marks.keys())
    max_key = max(selected_marks.keys())

    # Create a list or tuple with the lower and upper bounds
    value = [int(min_key), int(max_key)]
    value.sort()

    return value

if __name__ == '__main__':
    PORT = 8081  # Set the desired port number
    ADDRESS = '127.0.0.1'  # Set the desired IP address or leave it as None for the default address
    app.run_server(debug=True, use_reloader=False, port=PORT, host=ADDRESS)
