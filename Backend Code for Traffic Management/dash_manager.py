import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load initial data (empty if file doesn't exist yet)
try:
    df = pd.read_csv("traffic_summary.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["Metric", "Value"])

# Create Dash app
app = dash.Dash(__name__)
app.title = "Traffic Management Dashboard"

# Layout
app.layout = html.Div([
    html.H1("🚦 Real-Time Traffic Management Dashboard", style={"textAlign": "center"}),

    # Efficiency Card
    html.Div([
        html.H3("Traffic Efficiency (%)", style={"textAlign": "center"}),
        html.Div(id="efficiency-output", style={"fontSize": "30px", "textAlign": "center", "color": "green"})
    ], style={"width": "30%", "display": "inline-block"}),

    # Wait Time Card
    html.Div([
        html.H3("Avg Vehicle Wait Time (seconds)", style={"textAlign": "center"}),
        html.Div(id="wait-time-output", style={"fontSize": "30px", "textAlign": "center", "color": "blue"})
    ], style={"width": "30%", "display": "inline-block"}),

    # Congestion Message
    html.Div([
        html.H3("Congestion Status", style={"textAlign": "center"}),
        html.Div(id="congestion-message", style={"fontSize": "20px", "textAlign": "center", "color": "red"})
    ], style={"width": "30%", "display": "inline-block"}),

    html.Hr(),

    # Bottleneck Lanes Table
    html.H3("🚧 Bottleneck Lanes"),
    dash_table.DataTable(
        id="bottleneck-table",
        columns=[{"name": "Lane ID", "id": "Bottleneck Lanes"}, {"name": "Avg Vehicles Waiting", "id": "Avg Vehicles Waiting"}],
        style_table={"width": "50%"},
        style_cell={"textAlign": "center"},
    ),

    html.Hr(),

    # Live Congestion Chart
    html.H3("📊 Traffic Congestion Overview"),
    dcc.Graph(id="congestion-chart"),

    html.Hr(),

    # Final Heatmap Image
    html.H3("🗺️ Final Congestion Heatmap"),
    html.Img(src="congestion_heatmap.png", style={"width": "60%"})
], style={"padding": "20px"})

# Callback to update dashboard every 5 seconds
@app.callback(
    [Output("efficiency-output", "children"),
     Output("wait-time-output", "children"),
     Output("congestion-message", "children"),
     Output("bottleneck-table", "data"),
     Output("congestion-chart", "figure")],
    Input("efficiency-output", "id")
)
def update_dashboard(_):
    """Update dashboard with latest data from CSV."""
    try:
        df = pd.read_csv("traffic_summary.csv")
    except FileNotFoundError:
        return "Waiting for data...", "Waiting for data...", "No data yet", [], px.bar()

    efficiency = df.loc[df["Metric"] == "Efficiency (%)", "Value"].values[0]
    avg_wait_time = df.loc[df["Metric"] == "Average Wait Time (seconds)", "Value"].values[0]
    congestion_status = df.loc[df["Metric"] == "Congestion Status", "Value"].values[0]

    # Bottleneck lanes
    bottleneck_lanes = df.loc[df["Metric"] == "Bottleneck Lanes"]
    if not bottleneck_lanes.empty:
        bottleneck_data = pd.DataFrame(bottleneck_lanes[["Bottleneck Lanes", "Avg Vehicles Waiting"]])
    else:
        bottleneck_data = []

    # Generate congestion chart
    congestion_chart = px.bar(df[df["Metric"] == "Bottleneck Lanes"], x="Bottleneck Lanes", y="Avg Vehicles Waiting",
                              color="Avg Vehicles Waiting", title="Traffic Congestion per Lane")

    return f"{efficiency}%", f"{avg_wait_time} sec", congestion_status, bottleneck_data, congestion_chart

# Run Dash app
if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
