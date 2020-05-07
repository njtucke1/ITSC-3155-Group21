import dash
import dash_table
import dash_html_components as html
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

date = datetime.datetime(2020,4,29)
date_queries = []
for i in range(7):
    date_queries.append(str(date.strftime('%m-%d-%y')))
    date += datetime.timedelta(days=1)

# Load CSV file from Datasets folder
cred = credentials.Certificate('./ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()
df = pd.read_csv("example_output.csv")

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Data Vision',
            style={
                'textAlign': 'center',
                'color': '#3391FF'
            }
            ),
    html.Div('Web dashboard for Data Visualization using Python',
             style={'textAlign': 'center'}),
    html.Div('Air Table Web Scraping for Company Hiring Status',
             style={'textAlign': 'center'}),
    html.Br(),
    html.Br(),
    dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        fixed_rows={'headers': True},
        filter_action='native',
        sort_action='native',
        style_cell={
            'height': 'auto',
            'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
            'whiteSpace': 'normal',
            'textAlign': 'left',
            'backgroundColor': '#C2D0E1'
        },
        style_table={
            'maxHeight': '500px',
            'maxWidth': '75%',
            'margin': 'auto'
        },
        style_header={
            'backgroundColor': '#3391FF',
            'fontWeight': 'bold'
        }
    )
])

if __name__ == 'main':
    app.run_server(debug=True)