# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data into a pandas DataFrame
try:
    spacex_df = pd.read_csv("spacex_launch_dash.csv")
except FileNotFoundError:
    print("Error: The file 'spacex_launch_dash.csv' was not found.")
    exit()

# Get min and max payload for the slider
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Create a Dash application
app = dash.Dash(__name__)

# Create options for the launch site dropdown
launch_sites = [{'label': 'All Sites', 'value': 'All Sites'}] + \
             [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create the app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    html.Br(),

    # Dropdown for Launch Site selection
    html.Div([
        html.Label("Select a Launch Site:"),
        dcc.Dropdown(
            id='site-dropdown',
            options=launch_sites,
            value='All Sites',
            placeholder="Select a Launch Site here",
            searchable=True
        )
    ]),
    html.Br(),

    # Pie chart for success/failure counts
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Slider for payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        value=[min_payload, max_payload],
        marks={i: {'label': str(i)} for i in range(0, 10001, 2500)}
    ),
    html.Br(),

    # Scatter chart for payload vs. success correlation
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for the pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(
            success_counts,
            values='count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_counts = site_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        fig = px.pie(
            success_counts,
            values='count',
            names=success_counts['class'].map({1: 'Success', 0: 'Failure'}),
            title=f'Total Launches for {selected_site}'
        )
    return fig

# Callback for the scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site != 'All Sites':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=f"Payload vs. Launch Success for {'All Sites' if selected_site == 'All Sites' else selected_site}"
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)