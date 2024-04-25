import dash

# Dash-App initialisieren
dash.register_page(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'])

import pandas as pd
import folium
from branca.colormap import LinearColormap
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash.exceptions import PreventUpdate


# Daten einlesen und vorverarbeiten
flights_routes_df = pd.read_csv(r"https://media.githubusercontent.com/media/swrobuts/Flights/main/flight_routes_summary.csv")


connections_df = flights_routes_df.groupby(['origin_city', 'destination_city', 'origin_airport_lat', 'origin_airport_lon', 'destination_airport_lat', 'destination_airport_lon', 'year', 'month'])['count(flight_id)'].sum().reset_index()
connections_df.columns = ['origin_city', 'destination_city', 'origin_airport_lat', 'origin_airport_lon', 'destination_airport_lat', 'destination_airport_lon', 'year', 'month', 'total_flights']
connections_orig_airports_df = connections_df.groupby(['origin_city', 'origin_airport_lat', 'origin_airport_lon', 'destination_city', 'destination_airport_lat', 'destination_airport_lon', 'year', 'month']).sum('total_flights').reset_index()
cached_connections_df = flights_routes_df.groupby(['origin_city', 'destination_city', 'origin_airport_lat', 'origin_airport_lon', 'destination_airport_lat', 'destination_airport_lon', 'year', 'month'])['count(flight_id)'].sum().reset_index()
cached_connections_df.columns = ['origin_city', 'destination_city', 'origin_airport_lat', 'origin_airport_lon', 'destination_airport_lat', 'destination_airport_lon', 'year', 'month', 'total_flights']
cached_connections_orig_airports_df = cached_connections_df.groupby(['origin_city', 'origin_airport_lat', 'origin_airport_lon', 'destination_city', 'destination_airport_lat', 'destination_airport_lon', 'year', 'month']).sum('total_flights').reset_index()

# MinMax-Scaler
max_bewegungen = connections_orig_airports_df['total_flights'].max()
min_bewegungen = connections_orig_airports_df['total_flights'].min()

# Funktion, um die Flugbewegungen zu skalieren
def scale_bewegungen(flugbewegungen):
    return (flugbewegungen - min_bewegungen) / (max_bewegungen - min_bewegungen)

# Daten aggregieren, um die Top 30 Flughäfen zu bestimmen
top_airports = connections_orig_airports_df.groupby(['origin_airport_lat', 'origin_airport_lon', 'origin_city']).agg({
    'total_flights': 'sum'
}).reset_index().nlargest(30, 'total_flights')



# Styles definieren
styles = {
    'routes-sidebar': {
        'position': 'fixed',
        'top': '-300px',
        'left': '12.5%',
        'right': '25.5%',
        'height': '252px',
        'maxWidth': '95%',
        'padding': '20px',
        'backgroundColor':
        '#f8f9fa',
        'transition': 'top 0.3s ease-in-out',
        'zIndex': 1000,
        'overflowY': 'auto',
        'boxShadow': '0 6px 8px rgba(0, 0, 0, 0.1)'},
    'routes-sidebar-open': {'top': '0'},
    'routes-sidebar-header': {'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'},
    'routes-sidebar-content': {'display': 'flex', 'justifyContent': 'space-between'},
    'filter-group': {'flex': '1', 'padding': '0 3px', 'marginBottom': '10px'},
    'icon-container': {
        'position': 'fixed',
        'top': '8px',  
        'left': '20px',  
        'display': 'flex',
        'alignItems': 'center',
        'backgroundColor': '',
        'padding': '0px',  
        'borderRadius': '50%', 
        'cursor': 'pointer',
        'zIndex': 1030,  
        'color': 'orange',
        'fontSize': '35px', 
        'width': '35px',
        'height': '35px' 
        },
    'routes-selected-year': {'marginLeft': '10px', 'fontSize': '18px', 'fontWeight': 'bold'},
    'icon': {
        'transition': 'transform 0.3s ease-in-out',
        'display': 'block',  # Stellt sicher, dass das Icon als Blockelement behandelt wird
        'textAlign': 'center',  # Zentriert den Text innerhalb des Blocks
        'fontSize': '50px',  # Größe des Icons anpassen
        'color': 'white'
            },
    'icon-open': {'transform': 'rotate(180deg)'},
    'routes-content': {'marginTop': '50px', 'padding': '20px', 'transition': 'marginTop 0.3s ease-in-out'},
    'content-open': {'marginTop': '300px'},
    'routes-container': {'display': 'grid', 'gap': '5px', 'alignItems': 'stretch', 'height': '100vh', 'maxWidth': '94%', 'width': '92%', 'marginRight': '0px', 'padding': '0 2px'},
    'card': {'backgroundColor': '#E7EFF9', 'transition': 'all 0.3s ease'},
    'card-cancellations': {'backgroundColor': '#FEECEC', 'transition': 'all 0.3s ease'},
    'info-main-value': {'fontSize': '1rem', 'transition': 'fontSize 0.3s ease'},
    'graph-container': {
        'marginBottom': '2px',
        'marginLeft': '10px',
        'marginRight': '0px',
        'height': '450px',
        'justifyContent': 'center',  
        'alignItems': 'center' 
    },
    'card-body': {
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'space-around',
        'height': '510px'  # Erhöhe die Höhe der Karte für bessere Platzierung
    }
}

# App-Layout definieren
layout = html.Div([
    dcc.Store(id='routes-sidebar-toggle-state', data={'open': False}), 
    html.Div([
        html.Div([
            html.H3('Filter'),
        ], style=styles['routes-sidebar-header']),
        html.Div([
            dcc.Dropdown(
                id='routes-year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(connections_df['year'].unique())],
                value=sorted(connections_df['year'].unique())[-1],
                clearable=False,
                placeholder='Jahr auswählen',
                style={'marginBottom': '20px'}
            ),
            dcc.Dropdown(
                id='origin-dropdown',
                options=[{'label': 'Alle', 'value': 'all'}] + [{'label': city, 'value': city} for city in top_airports['origin_city'].unique()],
                value='all',
                clearable=False,
                placeholder='Startflughafen',
                style={'marginBottom': '20px'}
            ),
            dcc.Dropdown(
                id='destination-dropdown',
                options=[{'label': 'Alle', 'value': 'all'}] + [{'label': city, 'value': city} for city in top_airports['origin_city'].unique()],
                value='all',
                clearable=False,
                placeholder='Landeflughafen',
                style={'marginBottom': '20px'}
            ),
        ], style=styles['filter-group']),
    ], id='routes-sidebar', className='routes-sidebar', style=styles['routes-sidebar']),
    html.Div(style=styles['icon-container'], children=[
        html.I(id="routes-toggle-sidebar", n_clicks=0, children=""),
        html.Div(id='routes-selected-year', style=styles['routes-selected-year']),
    ]),
    html.Div([
        html.H3(''),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                            html.Div([
                                html.Div(id='all-year', style={'width': '49%', 'display': 'inline-block', 'textAlign': 'right', 'paddingRight': '10px'}),
                                html.Div("|", style={'display': 'inline-block'}),
                                html.Div(id='all-total', style={'width': '49%', 'display': 'inline-block', 'textAlign': 'left', 'paddingLeft': '10px'})
                                ], style={'width': '100%', 'textAlign': 'left', 'weight': 'bold'}),
                        html.Div([dcc.Graph(id='origin-top-flights', config={'displayModeBar': False})], style=styles['graph-container'])
                        
                    ], style=styles['card-body']),
                    style={'width': '90%', 'marginBottom': '10px'}  # Volle Breite und angepasster Margin
                ),
            ),
        ]),
        html.Div(html.Iframe(id='map-iframe', srcDoc=None, width='90%', height='800'), style={'height': '800px'})
    ], id='routes-content', className='routes-content', style=styles['routes-content'])
], className='routes-container', style=styles['routes-container'])



@callback(
    Output('routes-selected-year', 'children'),
    [Input('routes-year-dropdown', 'value')]
)
def update_selected_year(selected_year):
    return f"{selected_year}"


# Callback zur Aktualisierung des Sidebar-Zustands
@callback(
    Output('routes-sidebar-toggle-state', 'data'),
    Input('routes-toggle-sidebar', 'n_clicks'),
    State('routes-sidebar-toggle-state', 'data'),
    prevent_initial_call=True
)
def update_sidebar_state(n_clicks, data):
    if not n_clicks:
        raise PreventUpdate
    data['open'] = not data['open']
    return data

# Callback zur Anwendung des Sidebar-Zustands
@callback(
    [Output('routes-sidebar', 'style'),
     Output('routes-content', 'style'),
     Output('routes-toggle-sidebar', 'children')],
    Input('routes-sidebar-toggle-state', 'data')
)
def apply_sidebar_state(data):
    sidebar_style = styles['routes-sidebar']
    content_style = styles['routes-content']
    # Setze ein einfaches Unicode-Zeichen für den geschlossenen Zustand
    icon_text = '▼'  

    if data and data['open']:
        sidebar_style = {**styles['routes-sidebar'], **styles['routes-sidebar-open']}
        content_style = {**styles['routes-content'], **styles['content-open']}
        # Setze ein anderes Unicode-Zeichen für den geöffneten Zustand
        icon_text = '▲'

    return sidebar_style, content_style, icon_text


# Hilfsfunktion für die Formatierung der Flugzahlen
def format_k_or_m(value):
    if value >= 1000000:
        return f"{value / 1000000:.1f}".replace('.', ',') + ' M'
    elif value >= 1000:
        return f"{value / 1000:.1f}".replace('.', ',') + ' K'
    return str(value)

# Callback für die Aktualisierung der Visualisierungen basierend auf der Auswahl
@callback(
    [
        Output('all-year', 'children'),
        Output('all-total', 'children'),
        Output('origin-top-flights', 'figure'),
        Output('map-iframe', 'srcDoc')
    ],
    [
        Input('origin-dropdown', 'value'),
        Input('destination-dropdown', 'value'),
        Input('routes-year-dropdown', 'value')
    ]
)


def update_visualizations_flights(selected_origin, selected_destination, selected_year):
    # Beginne mit den gesamten Daten und filtere dann, falls erforderlich
    filtered_data = connections_df[
        (connections_df['year'] == selected_year) &
        ((connections_df['origin_city'] == selected_origin) | (selected_origin == 'all')) &
        ((connections_df['destination_city'] == selected_destination) | (selected_destination == 'all'))
    ]
   
    # Aggregate die Daten neu, basierend auf der Filterung
    origin_flights_by_month = filtered_data.groupby(['month', 'origin_city'])['total_flights'].sum().reset_index()
    total_flights_per_city = filtered_data.groupby('origin_city', as_index=False)['total_flights'].sum()
    sorted_cities = total_flights_per_city.sort_values(by='total_flights', ascending=False)
    top_origin_cities = sorted_cities['origin_city'].head(10).tolist()
   
    # Berechne die Gesamtflüge
    total_flights = filtered_data['total_flights'].sum()
   
    cols = 5  # Anpassen an die Anzahl der darzustellenden Städte
    rows = int(len(top_origin_cities) / cols) + (len(top_origin_cities) % cols > 0)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=top_origin_cities)
    for index, city in enumerate(top_origin_cities, start=1):
        row = (index - 1) // cols + 1
        col = (index - 1) % cols + 1
        city_data = origin_flights_by_month[origin_flights_by_month['origin_city'] == city]
        fig.add_trace(
            go.Scatter(x=city_data['month'], y=city_data['total_flights'], mode='lines', name=city, line=dict(color='red')),
            row=row, col=col
        )
   
    # Setze die y-Achse auf die gleiche Skalierung für alle Diagramme
    max_flights = origin_flights_by_month['total_flights'].max()*1.1
    min_flights = origin_flights_by_month['total_flights'].min()
    fig.update_yaxes(range=[min_flights, max_flights])

    fig.update_layout(
      height=220 * rows,
        width=380 * cols,
        title_text='Flüge nach Top-10 Startflughäfen pro Monat',
        title_y=0.99,
        title_x=0,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',   
        #plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=30, t=70, b=0)    
        )
    fig.update_xaxes(
        title_text='',
        tickmode='array',
        tickvals=list(range(1, 13)),
        ticktext=['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
        )
    fig.update_yaxes(title_text='', row=1)

   
    # Karte aktualisieren
    m = folium.Map(location=[34.0522, -118.2437], zoom_start=5, tiles='CartoDB Positron')
   
    # Gruppiere die Linien nach Start- und Zielflughafen
    grouped_lines = filtered_data.groupby(['origin_airport_lat', 'origin_airport_lon', 'destination_airport_lat', 'destination_airport_lon'])['total_flights'].sum().reset_index()
   
    # Füge gruppierte Linien zur Karte hinzu
    for _, row in grouped_lines.iterrows():
        scaled_bewegungen = scale_bewegungen(row['total_flights'])
        opacity = scaled_bewegungen  
        
        line = folium.PolyLine(
            locations=[
                (row['origin_airport_lat'], row['origin_airport_lon']),
                (row['destination_airport_lat'], row['destination_airport_lon'])
            ],
            color=f'rgba(255, 0, 0, {opacity*0.08})',
            weight=scaled_bewegungen*0.9,
        )
        line.add_to(m)
   
    # Füge Marker für die 30 Städte mit den meisten Flugbewegungen hinzu
    for _, airport in top_airports.iterrows():
        folium.Marker(
            location=[airport['origin_airport_lat'], airport['origin_airport_lon']],
            popup=f"{airport['origin_city']}// Flights: {airport['total_flights']}",
            icon=folium.Icon(icon='plane', prefix='fa', color='gray')
        ).add_to(m)
   
    return (
        f"Jahr: {selected_year}",
        f"Total Flights: {format_k_or_m(total_flights)}",
        fig,
        m._repr_html_()
)

# if __name__ == '__main__':
#     app.run_server(debug=True)