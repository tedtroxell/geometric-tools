
from dash import Dash, dcc, html, Input, Output, State, callback,ctx
import dash_vtk
import base64
from dash_vtk.utils import to_mesh_state
from sklearn.neighbors import KDTree

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# store a null reference to render right away
vtk_view=None
app.layout = html.Div(
    style={"height": "calc(100vh - 16px)", "width": "100%"},
    children=[
        html.Div(
            vtk_view, 
            style={"height": "80%", "width": "80%","padding-left":"10%"}, # add bad css to center it
            id="render"
        ),
        html.Div([
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                html.Div(id='output-data-upload'),
            ]),
        dcc.Input(
        id="click-info-output",
        type="hidden",
        style={'overflowX': 'scroll'}
    )
        ],
)

import numpy as np

import pyvista as pv

def parse_contents(contents, filename, date):

    content_type, content_string = contents.split(',')
    
    #write the file to disk and load
    decoded = base64.b64decode(content_string)
    with open(filename,"wb") as fp:
        fp.write(decoded)
    mesh = pv.read(filename)

    # convert the pyvista mesh to a Dash Mesh
    mesh_state = to_mesh_state(mesh,field_to_keep='scalar')
    vtk_view = dash_vtk.View(
        children=[dash_vtk.GeometryRepresentation(
                children=dash_vtk.Mesh(state=mesh_state),
                colorMapPreset="jet",
                colorDataRange=[0.2, 0.9],
            ),
        ],
        id="mesh",
        pickingModes=["click"],
    )
    return vtk_view

@callback(Output('render', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'),
            )
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children



# @callback(
#     State('render', 'data'),
#     Input('rendered', 'clickInfo')
# )
# def display_clicked_content(click_info):
#     global scalars
#     if click_info is not None:
#         mesh = pv.read(fname)
#         tree = KDTree(mesh.points)
#         distances, indices = tree.query([click_info['worldPosition']])
#         distances = distances.flatten()
#         scalars = distances
#     return click_info['worldPosition']

if __name__ == "__main__":
    app.run_server(debug=True)
