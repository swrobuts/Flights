import pandas as pd
import dash
from dash import html

dash.register_page(__name__)

flight_routes_df = pd.read_csv(r"C:\Users\rober\OneDrive\Vorlesungen\Datenbasierte Fallstudien\Visualisierungen\Flights\Flights\flight_routes_summary.csv")

