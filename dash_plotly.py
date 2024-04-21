import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64

# Dash-App erstellen
app = Dash(__name__, external_stylesheets=[
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'
])

# URL zur CSV-Datei
URL = "https://media.githubusercontent.com/media/swrobuts/Flights/main/cancellations_summary.csv"
URL2 = "https://media.githubusercontent.com/media/swrobuts/Flights/main/airliness_summary.csv"

# Lese die CSV-Datei ein
cancellations_summary = pd.read_csv(URL)
airlines_summary = pd.read_csv(URL2)

# Konvertiere Monatsnamen in numerische Werte
month_map = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}
cancellations_summary['month'] = cancellations_summary['month'].map(month_map)
airlines_summary['month'] = airlines_summary['month'].map(month_map)

# App-Layout
styles = {
    'sidebar': {
        'position': 'fixed',
        'top': '-250px',
        'left': '12.5%',
        'right': '25.5%',
        'height': '252px',
        'max-width': '95%',
        'padding': '20px',
        'background-color': '#f8f9fa',
        'transition': 'top 0.3s ease-in-out',
        'z-index': 1000,
        'overflow-y': 'auto',
        'box-shadow': '0 6px 8px rgba(0, 0, 0, 0.1)',
    },
    'sidebar-open': {
        'top': '0',
    },
    'sidebar-header': {
        'display': 'flex',
        'justify-content': 'space-between',
        'align-items': 'center',
        'margin-bottom': '20px',
    },
    'sidebar-content': {
        'display': 'flex',
        'justify-content': 'space-between',
    },
    'filter-group': {
        'flex': '1',
        'padding': '0 3px',
        'margin-bottom': '10px',
    },
    'icon-container': {
        'position': 'fixed',
        'top': '0px',
        'left': '5px',
        'display': 'flex',
        'align-items': 'center',
        'background-color': 'white',
        'padding': '13px',
        'border-radius': '65%',
        'cursor': 'pointer',
        'z-index': 1001,
        'color': 'orange',  
        'font-size': '40px',
    },    
    'selected-year': {
        'margin-left': '10px',
        'font-size': '18px',
        'font-weight': 'bold',  
    },
    'icon': {
        'transition': 'transform 0.3s ease-in-out',
    },
    'icon-open': {
        'transform': 'rotate(180deg)',
    },
    'content': {
        'margin-top': '50px',
        'padding': '20px',
        'transition': 'margin-top 0.3s ease-in-out',
    },
    'content-open': {
        'margin-top': '300px',
    },
'container': {
        'display': 'grid',
        #'grid-template-columns': '150fr', 
        'gap': '5px',  # Setzt einen Abstand zwischen den Spalten
        'align-items': 'stretch',
        'height': '100vh',
        'max-width': '100%',
        'width': '98%',
        'margin': '0 auto',
        'padding': '0 2px',
    },
    'card': {
        'background-color': '#E7EFF9',
        'transition': 'all 0.3s ease',
    },
    'card-cancellations': {
        'background-color': '#FEECEC',
        'transition': 'all 0.3s ease',
    },
    'info-main-value': {
        'font-size': '1rem',
        'transition': 'font-size 0.3s ease',
    },
}

app.layout = html.Div([
    dcc.Store(id='sidebar-state', data=False),
    html.Div([
        html.Div([
            html.H3('Filter'),
        ], style=styles['sidebar-header']),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='airline-dropdown',
                    options=[{'label': airline, 'value': airline} for airline in ['Alle'] + sorted(cancellations_summary['airline'].unique().tolist())],
                    value='Alle',
                    clearable=False,
                    placeholder='Fluggesellschaft',
                    style={'margin-bottom': '20px'}  # Vertikaler Abstand zwischen den Dropdown-Menüs
                ),
                dcc.Dropdown(
                    id='reason-dropdown',
                    options=[{'label': reason, 'value': reason} for reason in ['Alle'] + sorted(cancellations_summary['cancellation_reason'].unique().tolist())],
                    value='Alle',
                    clearable=False,
                    placeholder='Grund',
                    style={'margin-bottom': '20px'}  # Vertikaler Abstand zwischen den Dropdown-Menüs
                ),
            ], style=styles['filter-group']),
            html.Div([
                dcc.Dropdown(
                    id='year-dropdown',
                    options=[{'label': year, 'value': year} for year in sorted(cancellations_summary['year'].unique(), reverse=True)],
                    value=cancellations_summary['year'].max(),
                    clearable=False,
                    placeholder='Jahr',
                    style={'margin-bottom': '20px'}  # Vertikaler Abstand zwischen den Dropdown-Menüs
                ),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[{'label': month, 'value': month} for month in ['Alle'] + sorted(cancellations_summary['month'].unique().tolist())],
                    value='Alle',
                    clearable=False,
                    placeholder='Monat',
                    style={'margin-bottom': '20px'}  # Vertikaler Abstand zwischen den Dropdown-Menüs
                ),
            ], style=styles['filter-group']),
        ], style=styles['sidebar-content']),
    ], id='sidebar', className='sidebar', style=styles['sidebar']),
    html.Div([
        html.I(id="toggle-sidebar", n_clicks=0, className='fas fa-chevron-down', style=styles['icon']),
        html.Div(id='selected-year', style=styles['selected-year']),
    ], style=styles['icon-container']),
    html.Div([
        html.H3(''),
        html.Div(id='all-flights-year'),
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.P(id='all-flights-total', className="info-main-value", style=styles['info-main-value'])
                            ], className="info-section"),
                            html.Div([
                                dcc.Graph(id='all-flights-sparkline', config={'displayModeBar': False})
                            ], style={'margin-bottom':'0px'}),   
                            html.Div([
                                html.P(id='all-flights-diff', className="info-diff", style={'font-family': 'Arial, sans-serif', 'font-size': '14px', 'line-height': '1.5'}),
                                html.P(id='all-flights-mean', className="info-diff", style={'font-family': 'Arial, sans-serif', 'font-size': '14px', 'line-height': '1.5'})
                            ], className="info-section"),
                        ], className="d-flex justify-content-around align-items-center info-container"),
                    ]),
                    style={'width': '850px' , 'height': '170px','background-color': '#E7EFF9', 'margin-bottom': '60px'}
                ),
               
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.Div(id='all-cancellations-year'),
                        html.Div([
                            html.Div([
                                html.P(id='all-cancellations-total', className="info-main-value", style=styles['info-main-value'])
                            ]),
                            html.Div([
                                dcc.Graph(id='all-cancellations-sparkline', config={'displayModeBar': False})
                            ], style={'margin-bottom':'0px'}),                          
                            html.Div([
                                html.P(id='all-cancellations-diff', className="info-diff", style={'font-family': 'Arial, sans-serif', 'font-size': '14px', 'line-height': '1.5'}),
                                html.P(id='all-cancellations-mean', className="info-diff", style={'font-family': 'Arial, sans-serif', 'font-size': '14px', 'line-height': '1.5'})
                            ]),
                            html.Div([
                                dcc.Graph(id='cancellations-pie-chart', config={'displayModeBar': False})
                            ]),
                        ], className="d-flex justify-content-around align-items-center info-container"),
                    ]),
                     style={'margin-left':'-340px', 'width':'940px', 'height': '170px', 'margin-bottom': '20px', 'background-color': '#FEECEC'}
                ),
             
            ),
        ]),
        dbc.Row([
            dbc.Col(
                html.Div(id='flights-table')
            ),
            dbc.Col(
                dcc.Graph(id='cancellations-bar-chart', config={'displayModeBar': False}),
                style={'margin-left': '-100px', 'margin-right': '0px','textAlign': 'left', 'width': '400px'}  
            ),
            #html.Div(style={'width': '0.8%', 'height': 'auto', 'display': 'inline-block', 'visibility': 'hidden'}),
            dbc.Col(
                dcc.Graph(id='cancellations-deviation-chart', config={'displayModeBar': False}),
                style={'margin-left': '-350px', 'textAlign': 'left', 'width': '300px'}  
            ),
        ]),
        dbc.Row([
            dbc.Col(
                dcc.Graph(id='cancellations-sm-chart', config={'displayModeBar': False}, style={'margin-left': '-20px', 'width':'1850px'}),
                
            ),
        ]),
    ], id='content', className='content', style=styles['content'])
], className='container', style=styles['container'])

@app.callback(
    Output('selected-year', 'children'),
    [Input('year-dropdown', 'value')]
)
def update_selected_year(selected_year):
    return str(selected_year)

@app.callback(
    [Output('sidebar', 'style'),
     Output('content', 'style'),
     Output('toggle-sidebar', 'className'),
     Output('sidebar-state', 'data')],
    [Input('toggle-sidebar', 'n_clicks')],
    [State('sidebar-state', 'data')]
)
def toggle_sidebar(n_clicks, sidebar_state):
    if n_clicks:
        if sidebar_state:
            sidebar_style = styles['sidebar']
            content_style = styles['content']
            icon_class = 'fas fa-chevron-down'
            sidebar_state = False
        else:
            sidebar_style = {**styles['sidebar'], **styles['sidebar-open']}
            content_style = {**styles['content'], **styles['content-open']}
            icon_class = 'fas fa-chevron-up'
            sidebar_state = True
    else:
        sidebar_style = styles['sidebar']
        content_style = styles['content']
        icon_class = 'fas fa-chevron-down'
        sidebar_state = False
    return sidebar_style, content_style, icon_class, sidebar_state




# Callback für die Kästchen mit den Informationen zu allen Flügen und Stornierungen
def format_k_or_m(value):
    if value >= 1000000:
        return f"{value / 1000000:.1f}".replace('.', ',') + ' M'
    elif value >= 1000:
        return f"{value / 1000:.1f}".replace('.', ',') + ' K'
    else:
        return str(value)

@app.callback(
    [Output('all-flights-year', 'children'),
    Output('all-flights-total', 'children'),
    Output('all-flights-diff', 'children'),
    Output('all-flights-mean', 'children'),    
    Output('all-flights-sparkline', 'figure'),
    Output('all-cancellations-year', 'children'),
    Output('all-cancellations-total', 'children'),
    Output('all-cancellations-diff', 'children'),
    Output('all-cancellations-mean', 'children'),
    Output('all-cancellations-sparkline', 'figure')],
    [Input('year-dropdown', 'value')]
)
def update_header_boxes(selected_year):
    flights_data = airlines_summary[airlines_summary['year'] == selected_year]
    cancellations_data = cancellations_summary[cancellations_summary['year'] == selected_year]
    total_flights = flights_data['total_flights'].sum()
    total_cancellations = cancellations_data['cancellations'].sum()
    previous_year = int(selected_year) - 1
    previous_flights_data = airlines_summary[airlines_summary['year'] == previous_year]
    previous_cancellations_data = cancellations_summary[cancellations_summary['year'] == previous_year]

    if not previous_flights_data.empty:
        previous_total_flights = previous_flights_data['total_flights'].sum()
        flights_difference = total_flights - previous_total_flights
        flights_percentage_change = (flights_difference / previous_total_flights) * 100
        flights_arrow = '▼' if flights_difference < 0 else '▲'
        flights_color = 'red' if flights_difference < 0 else 'green'

        # Formatieren der absoluten Zahl mit Punkten als Tausendertrennzeichen
        formatted_flights_difference = "{:+,.0f}".format(flights_difference).replace(",", "X").replace(".", ",").replace("X", ".")

        # Formatieren der Prozentzahl mit Komma als Dezimaltrennzeichen
        formatted_flights_percentage_change = "{:+.1f}".format(flights_percentage_change).replace(".", ",")

        flights_diff_text = html.Span([
            "{} ({} %) ".format(formatted_flights_difference, formatted_flights_percentage_change),
            html.Span(flights_arrow, style={'color': flights_color})
        ])
    else:
        flights_diff_text = None

    if not previous_cancellations_data.empty:
        previous_total_cancellations = previous_cancellations_data['cancellations'].sum()
        cancellations_difference = total_cancellations - previous_total_cancellations
        cancellations_percentage_change = (cancellations_difference / previous_total_cancellations) * 100
        cancellations_arrow = '▼' if cancellations_difference < 0 else '▲'
        cancellations_color = 'green' if cancellations_difference < 0 else 'red'

        # Formatieren der absoluten Zahl mit Punkten als Tausendertrennzeichen
        formatted_cancellations_difference = "{:+,.0f}".format(cancellations_difference).replace(",", "X").replace(".", ",").replace("X", ".")

        # Formatieren der Prozentzahl mit Komma als Dezimaltrennzeichen
        formatted_cancellations_percentage_change = "{:+.1f}".format(cancellations_percentage_change).replace(".", ",")

        cancellations_diff_text = html.Span([
            "{} ({}%) ".format(formatted_cancellations_difference, formatted_cancellations_percentage_change),
            html.Span(cancellations_arrow, style={'color': cancellations_color})
        ])
    else:
        cancellations_diff_text = None
    
    flights_sparkline_data = flights_data.groupby('month')['total_flights'].sum().reset_index()
    cancellations_sparkline_data = cancellations_data.groupby('month')['cancellations'].sum().reset_index()

   
    # Behandle fehlende Werte in der Spalte 'month'
    flights_sparkline_data['month'] = flights_sparkline_data['month'].fillna(0).astype(int)
    cancellations_sparkline_data['month'] = cancellations_sparkline_data['month'].fillna(0).astype(int)
   
    # Konvertiere Monatszahlen in Monatsnamen
    flights_sparkline_data['month'] = flights_sparkline_data['month'].apply(lambda x: datetime(2000, x, 1).strftime('%b') if x != 0 else '')
    cancellations_sparkline_data['month'] = cancellations_sparkline_data['month'].apply(lambda x: datetime(2000, x, 1).strftime('%b') if x != 0 else '')
   
    # Berechne den Durchschnitt pro Monat
    flights_mean = total_flights / 12

    # Berechne den Durchschnitt pro Airlines
    cancellations_mean = total_cancellations / flights_data['airline'].nunique()
   
    flights_sparkline_fig = go.Figure(go.Scatter(
        x=flights_sparkline_data['month'],
        y=flights_sparkline_data['total_flights'],
        mode='lines',
        line=dict(color='#1F77B4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)',
        text=[f"Monat: {month}, Flüge: {format_k_or_m(value)}" for month, value in zip(flights_sparkline_data['month'], flights_sparkline_data['total_flights'])],
        hoverinfo='text',
        name='',
        hovertemplate='<b>Monat</b>: %{x}<br><b>Flüge</b>: %{y}'
    ))
    # Hinzufügen der roten Punkte und Labels für den ersten und letzten Punkt
    if not flights_sparkline_data.empty:
        first_month = flights_sparkline_data.iloc[0]
        last_month = flights_sparkline_data.iloc[-1]
   
        flights_sparkline_fig.add_trace(go.Scatter(
            x=[first_month['month'], last_month['month']],
            y=[first_month['total_flights'], last_month['total_flights']],
            mode='markers+text',
            marker=dict(color='red', size=8),
            text=[format_k_or_m(first_month['total_flights']), format_k_or_m(last_month['total_flights'])],
            textposition=["bottom center", "bottom center"],
            showlegend=False,
            hoverinfo='text',
            name='',
            hovertemplate='<b>Monat</b>: %{x}<br><b>Flüge</b>: %{y}'            
        ))
    flights_sparkline_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        tickvals=[flights_sparkline_data['month'].iloc[0], flights_sparkline_data['month'].iloc[-1]],
        ticktext=['Jan', 'Dez'],
        tickfont=dict(size=10)
    ),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=90,
        width=350,
        showlegend=False
    )

    cancellations_sparkline_fig = go.Figure(go.Scatter(
        x=cancellations_sparkline_data['month'],
        y=cancellations_sparkline_data['cancellations'],
        mode='lines',
        line=dict(color='#FF7F0E', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 127, 14, 0.2)',
        text=[f"Monat: {month}, Stornos: {format_k_or_m(value)}" for month, value in zip(cancellations_sparkline_data['month'], cancellations_sparkline_data['cancellations'])],
        hoverinfo='text',
        name='',
        hovertemplate='<b>Monat</b>: %{x}<br><b>Stornos</b>: %{y}'
    ))

    # Hinzufügen der roten Punkte und Labels für den ersten und letzten Punkt
    if not cancellations_sparkline_data.empty:
        first_month = cancellations_sparkline_data.iloc[0]
        last_month = cancellations_sparkline_data.iloc[-1]

    cancellations_sparkline_fig.add_trace(go.Scatter(
        x=[first_month['month'], last_month['month']],
        y=[first_month['cancellations'], last_month['cancellations']],
        mode='markers+text',
        marker=dict(color='red', size=8),
        text=[format_k_or_m(first_month['cancellations']), format_k_or_m(last_month['cancellations'])],
        textposition=["bottom center", "bottom center"],
        showlegend=False,
        hoverinfo='text',
        name='',
        hovertemplate='<b>Monat</b>: %{x}<br><b>Stornos</b>: %{y}'
    ))  

    cancellations_sparkline_fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
        showgrid=False,
        zeroline=False,
        showticklabels=True,
        tickvals=[cancellations_sparkline_data['month'].iloc[0], cancellations_sparkline_data['month'].iloc[-1]],
        ticktext=['Jan', 'Dez'],
        tickfont=dict(size=10)
    ),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=90,
        width=350,
        showlegend=False
    )
    def format_number(value):
        if value >= 1e6:
            return f"{value / 1e6:.1f} M"
        elif value >= 1e3:
            return f"{value / 1e3:.0f} K"
        else:
            return f"{value:.0f}"
    return (
        f"",
        html.Div([
            html.Span(f"Flüge in {selected_year} ", style={'font-size': '14px'}),
            html.Br(),
            html.Span(f"{format_number(total_flights)}", style={'font-size': '32px', 'font-weight': 'bold'})
        ], style={'margin-top': '2px'}),            
        html.Div([
            html.Span(f"Differenz zu {previous_year} ", style={'font-size': '14px'}),
            html.Br(),
            html.Span(flights_diff_text, style={'font-size': '16px', 'font-weight': 'bold'})
        ], style={'margin-top': '2px'}),
        html.Div([
            html.Span(f"⌀ Anzahl Flüge pro Monat in {selected_year} ", style={'font-size': '14px'}),
            html.Br(),
            html.Span("{:,}".format(int(flights_mean)).replace(',', '.'), style={'font-size': '16px', 'font-weight': 'bold'})
        ], style={'margin-top': '3px'}),
        flights_sparkline_fig,
        f"",
        html.Div([
            html.Span(f"Stornos in {selected_year} ", style={'font-size': '14px'}),
            html.Br(),
            html.Span(f"{format_number(total_cancellations)}", style={'font-size': '32px', 'font-weight': 'bold'})
        ], style={'margin-top': '2px'}),            
        html.Div([
            html.Span(f"Differenz zu {previous_year} ", style={'font-size': '14px'}),
            html.Br(),
            html.Span(cancellations_diff_text, style={'font-size': '16px', 'font-weight': 'bold'})
        ], style={'margin-top': '2px'}),
        html.Div([
            html.Span(f"⌀ Anzahl Stornos pro Airline", style={'font-size': '14px'}),
            html.Br(),
            html.Span("{:,}".format(int(cancellations_mean)).replace(',', '.'), style={'font-size': '16px', 'font-weight': 'bold'})
        ], style={'margin-top': '3px'}),
        cancellations_sparkline_fig
    )

#Tabelle mit Sparklines
@app.callback(
    Output('flights-table', 'children'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_flights_table(selected_airline, selected_reason, selected_year, selected_month):
    filtered_data = airlines_summary.copy()
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
    if selected_year != 'Alle':
        filtered_data = filtered_data[filtered_data['year'] == selected_year]
    if selected_month != 'Alle':
        filtered_data = filtered_data[filtered_data['month_int'] == int(selected_month)]
    max_flights = filtered_data['total_flights'].max()
    max_length = max([len(str(x)) for x in filtered_data['total_flights']])

    # Anpassung des Labels für die Flüge
    flights_label = "Alle Flüge"
    if selected_year != 'Alle' and selected_month == 'Alle':
        flights_label = f"Alle Flüge in 12-{selected_year}"
    elif selected_year != 'Alle' and selected_month != 'Alle':
        flights_label = f"Alle Flüge in {selected_month}-{selected_year}"
    elif selected_year != 'Alle':
        flights_label = f"Alle Flüge in {selected_year}"

    table_rows = []
    for airline in filtered_data.sort_values('total_flights', ascending=False)['airline'].unique():
        airline_data = filtered_data[filtered_data['airline'] == airline]
        monthly_totals = airline_data.groupby(['month_int', 'month', 'year']).agg({
            'total_flights': 'sum',
            'percent of arrivals on time': 'mean',
            'percent of departures on time': 'mean',  
            'cancellation_rate_percent': 'mean'
        }).reset_index()
        hover_texts = [f"{row['month']} {row['total_flights']}" for index, row in monthly_totals.iterrows()]
	
        sparkline_fig = go.Figure(
            go.Bar(
                x=monthly_totals['month_int'],
                y=monthly_totals['total_flights'],
                hoverinfo='text',
                marker=dict(color='#7B96C4'),
                hovertext=hover_texts,
                width=0.65
            )
        )
        sparkline_fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
            ),
            height=24,
            width=110,
            margin=dict(l=0, r=0, t=0, b=4),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            plot_bgcolor='rgba(255,255,255,1)',
            paper_bgcolor='rgba(255,255,255,1)'
        )

        # Umwandlung des Pünktlichkeitsprozentsatzes und der Stornoquote in das gewünschte Format
        percent_format = lambda x: "{} %".format(x.replace('.', ','))
        cancellation_rate_formatted = percent_format(f"{monthly_totals['cancellation_rate_percent'].iloc[-1]:.1f}")

    
        flights_value_formatted = f"{monthly_totals['total_flights'].iloc[-1]:{max_length},}".replace(",", ".")
        bar_width = f"{(monthly_totals['total_flights'].iloc[-1] / max_flights) * 60:.1f}%"
        flights_value_and_bar = html.Div([
            html.Div(flights_value_formatted, style={'width': f'{max_length * 7}px', 'textAlign': 'right', 'marginRight': '8px'}),
            html.Div(style={
            'width': bar_width,
            'height': '10px',
            'backgroundColor': '#7B96C4',
        }),
        ], style={'display': 'flex', 'width': '100%', 'alignItems': 'center', 'height': '70%'})

        cancellation_content = html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
        children=[
            html.Span(cancellation_rate_formatted, style={'display': 'inline-block', 'textAlign': 'right', 'width': '40px'})
        ]
    )
    
        arrivals_style = {'width': '15%', 'textAlign': 'center'}
        departures_style = {'width': '15%', 'textAlign': 'center'}
        arrivals_content = html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
        children=[
        html.Span(
            "{} %".format(monthly_totals['percent of arrivals on time'].iloc[-1].astype(str).replace('.', ',')),
            style={'display': 'inline-block', 'textAlign': 'right', 'width': '40px'}
        ),
        html.Div(
            '',
            style={
                'width': '10px',
                'height': '10px',
                'backgroundColor': 'red' if monthly_totals['percent of departures on time'].iloc[-1] < 80 else 'transparent',
                'borderRadius': '50%',
                'display': 'inline-block',
                'marginLeft': '8px'
            }
        )
    ]
)

        departures_content = html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
        children=[
        html.Span(
            "{} %".format(monthly_totals['percent of departures on time'].iloc[-1].astype(str).replace('.', ',')),
            style={'display': 'inline-block', 'textAlign': 'right', 'width': '40px'}
        ),
        html.Div(
            '',
            style={
                'width': '10px',
                'height': '10px',
                'backgroundColor': 'red' if monthly_totals['percent of departures on time'].iloc[-1] < 80 else 'transparent',
                'borderRadius': '50%',
                'display': 'inline-block',
                'marginLeft': '8px'
            }
        )
    ]
)

        # Füge die Zeile zur Tabelle hinzu
        table_rows.append(html.Tr([
            html.Td(airline, style={'width': '19%', 'paddingRight': '0px'}),
            html.Td(dcc.Graph(figure=sparkline_fig, config={'displayModeBar': False}), style={'width': '3%', 'paddingRight': '1px'}),
            html.Td(flights_value_and_bar, style={'width': '15%', 'paddingRight': '2px'}),
            html.Td(arrivals_content, style=arrivals_style),
            html.Td(departures_content, style=departures_style),
            html.Td(cancellation_content, style={'width': '8%', 'textAlign': 'center','paddingRight': '1px',})  
    ], style={'border-bottom': '1px solid #d3d3d3'}))

    # Gib die gesamte Tabelle zurück
    return html.Table([
        html.Thead(html.Tr([
            html.Th('Airline', style={'paddingRight': '0px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('', style={'paddingRight': '1px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th(flights_label, style={'paddingRight': '2px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('⌀ Pünktlich (Ankunft)', style={'paddingRight': '0px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('⌀ Pünktlich (Abflug)', style={'paddingRight': '0px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('⌀ Storniert', style={'paddingRight': '1px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle', 'horizontal-align': 'center'})
        ], style={'background-color': 'white', 'margin-bottom': '10px'})),
        html.Tbody([
            html.Tr([html.Td('', style={'height': '10px'}) for _ in range(5)]),  # Leere Zeile einfügen
            *table_rows  # Bestehende Tabellenzeilen einfügen
        ], style={'border-top': '1px solid black'})
    ], style={'font-size': '0.85rem', 'width': '850px', 'height': '80%'})


# Callback für das Balkendiagramm und das Abweichungsdiagramm
@app.callback(
    [Output('cancellations-bar-chart', 'figure'),
     Output('cancellations-deviation-chart', 'figure')],
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_charts(selected_airline, selected_reason, selected_year, selected_month):
    y_shift = 16  # Verschiebung entlang der y-Achse
   
    filtered_data = cancellations_summary.copy()
   
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
    if selected_year != 'Alle':
        filtered_data = filtered_data[filtered_data['year'] == selected_year]
    if selected_month != 'Alle':
        filtered_data = filtered_data[filtered_data['month'] == selected_month]
   
    cancellations_sorted = filtered_data.groupby('airline', as_index=False)['cancellations'].sum().sort_values(by='cancellations', ascending=True)
    cancellations_sorted['formatted_cancellations'] = cancellations_sorted['cancellations'].apply(lambda x: "{:,.0f}".format(x).replace(",", "."))
   
    fig_bar = px.bar(
        cancellations_sorted,
        y='airline',
        x='cancellations',
        orientation='h',
        color_discrete_sequence=['#DE5D6D'],
        text='formatted_cancellations'
    )
   
    max_cancellations = cancellations_sorted['cancellations'].max()
    padding = max_cancellations * 0.2
   
    fig_bar.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[0, max_cancellations + padding],
            title_text=''
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=True,
            title_text='',
            tickfont=dict(size=12),
            automargin=True
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        height=440,
        width=650,
        margin=dict({'pad':6}, l=0, r=0, t=60, b=0),
        bargap=0.4,  # Abstand zwischen den Balken
        title=dict(
            text=f"<b>Anzahl der Stornierungen nach Airlines in {selected_year if selected_year != 'Alle' else 'allen Jahren'}",
            font=dict(size=14),
            x=0.28,
            xanchor='center',
            y=0.97,
            yanchor='top'
        ),
        shapes=[
            dict(
                type='line',
                x0=0,
                x1=0,
                y0=0,
                y1=1,
                xref='paper',
                yref='paper',
                line=dict(color='grey', width=1)
            )
        ]
    )
   
    fig_bar.update_traces(textfont_size=11, textposition='outside')
   
    # Berechnung der Abweichungen zum Vorjahr
    if selected_year == 'Alle':
        current_year = int(filtered_data['year'].max())
    else:
        current_year = int(selected_year)
    previous_year = current_year - 1
   
    current_year_data = filtered_data[filtered_data['year'] == current_year].groupby('airline', as_index=False)['cancellations'].sum()
    previous_year_data = cancellations_summary[cancellations_summary['year'] == previous_year].groupby('airline', as_index=False)['cancellations'].sum()
   
    if not previous_year_data.empty:
        deviation_data = current_year_data.merge(previous_year_data, on='airline', suffixes=('_current', '_previous'), how='left')
        deviation_data['cancellations_previous'] = deviation_data['cancellations_previous'].fillna(0)
        deviation_data['deviation'] = ((deviation_data['cancellations_current'] - deviation_data['cancellations_previous']) / deviation_data['cancellations_current']) * 100
        deviation_data['formatted_deviation'] = deviation_data['deviation'].apply(lambda x: f"{x:+.1f}".replace('.', ',') + ' %')
       
        # Sortierung des Abweichungsdiagramms entsprechend der Sortierung des Balkendiagramms
        deviation_data = deviation_data.set_index('airline').reindex(cancellations_sorted['airline']).reset_index()
       
        max_deviation = deviation_data['deviation'].abs().max()
       
        fig_deviation = go.Figure()
       
        line_height = 31  # Höhe jeder Linie
       
        for i, row in deviation_data.iterrows():
            color = '#DE5D6D' if row['deviation'] >= 0 else '#1F5CB0'
            fig_deviation.add_shape(
                type='line',
                x0=0,
                y0=i * line_height + y_shift,
                x1=row['deviation'],
                y1=i * line_height + y_shift,
                line=dict(color=color, width=1.5)
            )
            fig_deviation.add_trace(go.Scatter(
                x=[row['deviation']],
                y=[i * line_height + y_shift],
                mode='markers',
                marker=dict(color=color, size=8),
                hoverinfo='text',
                hovertext=f"{row['airline']}<br># Stornos im Vorjahr: {row['cancellations_previous']:,.0f}".replace(".", ","),
                showlegend=False
            ))
            fig_deviation.add_annotation(
                x=row['deviation'],
                y=i * line_height + y_shift,
                text=row['formatted_deviation'],
                showarrow=False,
                font=dict(size=11),
                xanchor='left' if row['deviation'] >= 0 else 'right',
                xshift=10 if row['deviation'] >= 0 else -10,
                yshift=0
            )
       
        fig_deviation.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font=dict(color="black")
            ),
            xaxis=dict(
                showgrid=False,
                zeroline=True,
                zerolinecolor='grey',
                zerolinewidth=0.5,
                showticklabels=False,
                range=[-max_deviation*1.2, max_deviation*1.2],  # Vergrößerung des Bereichs der x-Achse
                title_text=''
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[0, 440],
                title_text='',
                automargin=True
            ),
            title=dict(
                text=f"<b>Abweichungen zu {int(selected_year)-1 if selected_year != 'Alle' else 'Vorjahr'}",
                font=dict(size=14),
                x=0.49,
                xanchor='center',
                y=0.97,
                yanchor='top'
        ),
            plot_bgcolor='rgba(0,0,0,0)',
            height=440,
            width=350,  
            margin=dict({'pad':1}, l=0, r=30, t=57, b=0)
        )
    else:
        fig_deviation = go.Figure()
        fig_deviation.update_layout(
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                title_text=''
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                title_text='',
                automargin=True
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            height=440,
            width=300,
            margin=dict({'pad':0}, l=0, r=0, t=30, b=0),
            annotations=[
                dict(
                    x=0.5,
                    y=0.5,
                    text="Keine Daten für das Vorjahr verfügbar",
                    showarrow=False,
                    font=dict(size=12)
                )
            ]
        )
   
    return fig_bar, fig_deviation

# Callback für das Kreisdiagramm
@app.callback(
    Output('cancellations-pie-chart', 'figure'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_pie_chart(selected_airline, selected_reason, selected_year, selected_month):
    filtered_data = cancellations_summary.copy()
   
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
    if selected_year != 'Alle':
        filtered_data = filtered_data[filtered_data['year'] == selected_year]
    if selected_month != 'Alle':
        filtered_data = filtered_data[filtered_data['month'] == selected_month]
   
    sorted_data = filtered_data.groupby('cancellation_reason', as_index=False)['cancellations'].sum().sort_values(by='cancellations', ascending=False)
    sorted_data['percentage'] = (sorted_data['cancellations'] / sorted_data['cancellations'].sum() * 100).round(1)
    sorted_data['text'] = sorted_data.apply(lambda x: f"{x['cancellation_reason']}<br>{x['cancellations']:,}".replace(",", ".") + f"<br>({x['percentage']} %)", axis=1)
   
    grouped_data = filtered_data.groupby(['cancellation_reason', 'airline'], as_index=False)['cancellations'].sum()
    hover_texts = grouped_data.groupby('cancellation_reason').apply(
        lambda x: "<br>".join([f"{row['airline']}: {row['cancellations']}" for index, row in x.iterrows()])
    ).reset_index(name='info')
   
    final_data = filtered_data.groupby('cancellation_reason', as_index=False)['cancellations'].sum()
    final_data = final_data.merge(hover_texts, on='cancellation_reason', how='left')
   
    final_data['percentage'] = (final_data['cancellations'] / final_data['cancellations'].sum() * 100).round(1)
    final_data['text'] = final_data.apply(lambda x: f"<b>{x['cancellation_reason']}</b><br>{x['cancellations']:,}".replace(",", "."), axis=1)
   
    colors_hex = ["rgba(236, 81, 26, 0.65)", "rgba(248, 125, 7, 0.65)",
                  "rgba(255, 166, 0, 0.65)", "rgba(219, 13, 39, 0.65)"]
   
    fig = go.Figure(data=[go.Pie(labels=final_data['cancellation_reason'], values=final_data['cancellations'],
                                 hoverinfo='label+percent',
                                 text=final_data['text'],
                                 textinfo='text',
                                 marker=dict(colors=colors_hex),
                                 rotation=194,
                                 direction="clockwise",
                                 hovertemplate=final_data['info'].apply(lambda x: f'<b> %{{label}}</b><b> | Anzahl der Vorfälle nach Airline</b><br>{x}<extra></extra>'),
                                 hole=.65,
                                 sort=False)])
   
    fig.update_traces(textfont_size=11)
   
    fig.update_layout(height=125, width=260, showlegend=False, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='#FEECEC')

   
    return fig

import plotly.express as px

# Callback für das Small Multiples
@app.callback(
    Output('cancellations-sm-chart', 'figure'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_bar_chart(selected_airline, selected_reason, selected_year, selected_month):
    filtered_airlines = airlines_summary.copy()
    # Anwendung der Filter
    if selected_airline != 'Alle':
        filtered_airlines = filtered_airlines[filtered_airlines['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_airlines = filtered_airlines[filtered_airlines['cancellation_reason'] == selected_reason]
    if selected_year != 'Alle':
        filtered_airlines = filtered_airlines[filtered_airlines['year'] == selected_year]
    if selected_month != 'Alle':
        filtered_airlines = filtered_airlines[filtered_airlines['month_int'] == selected_month]
   
    # Berechnung der Abweichung von 100% für "percent of arrivals on time"
    filtered_airlines['arrivals_deviation'] = 100 - filtered_airlines['percent of arrivals on time']
    filtered_airlines['departures_deviation'] = 100 - filtered_airlines['percent of departures on time']
   
    fig = px.scatter(filtered_airlines,
                    x='month_int',
                    y=['arrivals_deviation', 'departures_deviation'],
                    color='variable',
                    color_discrete_map={
                     'arrivals_deviation': '#F28E6A',
                     'departures_deviation': 'red'
                    },                  
                    facet_col='airline',
                    facet_col_wrap=7,  
                    height=550,
                    facet_col_spacing=0.01,
                    facet_row_spacing= 0.35,
                    #labels={'airline':''}
    )
    # Anpassen der Markergröße und Transparenz basierend auf der Abweichung bzw. Wert
    for trace in fig.data:
        if 'arrivals_deviation' in trace.name:
            trace['marker']['opacity'] = [0.7 if y <= 20 else 0.8 + 0.2 * (100 - y) / 80 for y in trace.y]
            trace['marker']['size'] = [7 if y <= 20 else 10 + 10 * (y - 20) / 80 for y in trace.y]
            
        else:
            trace['marker']['opacity'] = [0.9 if y <= 20 else 0.7 + 0.2 * (100 - y) / 80 for y in trace.y]
            trace['marker']['size'] = [7 if y <= 20 else 10 + 10 * (y - 20) / 80 for y in trace.y]
    
    # Anpassung der x-Achse basierend auf der Auswahl im Monatsfilter
    if selected_month != 'Alle':
        month_name = {1: 'Jan', 2: 'Feb', 3: 'Mrz', 4: 'Apr', 5: 'Mai', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Dez'}[selected_month]
        fig.update_xaxes(tickmode='array',
                         tickvals=[selected_month],
                         ticktext=[month_name],
                         showticklabels=True,
                         linecolor='grey',
                         title_text='')
    else:
        fig.update_xaxes(tickmode='array',
                         tickvals=[filtered_airlines['month_int'].min(),
                                   filtered_airlines['month_int'].max()],
                         ticktext=['Jan', 'Dez'],
                         showticklabels=True,
                         linecolor='grey',
                         title_text='')
    
    fig.update_yaxes(title_text='')
    for trace in fig.data:
        if trace.name == 'arrivals_deviation':
            trace.name = 'Pünktlich bei Ankunft'
        elif trace.name == 'departures_deviation':
            trace.name = 'Pünktlich bei Abflug'
    # Einstellung des Layouts für weißen Hintergrund und Legende
    fig.update_layout(
        margin=dict(l=0, r=0, t=120, b=0),  # Randdefinition: links, rechts, oben, unten
        plot_bgcolor='rgba(255, 255, 255, 1)',  # Korrekter RGBA-Wert für einen weißen Hintergrund
        paper_bgcolor='rgba(255, 255, 255, 1)',  # Ebenfalls weißer Hintergrund
        showlegend=True,
        legend_title='',
        legend=dict(
            orientation='h',  # Horizontale Ausrichtung der Legende
            yanchor='bottom',
            y=1.1,  
            xanchor='left',
            x=-0.01,
           itemsizing='constant'  # Gleichbleibende Größe der Legenden-Symbole
        ),
        title=dict(  # Korrektur für die Eröffnungsklammer von dict
            text='<b>Performance der Airlines: Pünktlichkeit bei Ankunft und Abflug</b>',  # HTML-Tag für Fettschrift und korrekter Abschluss des Texts
            font=dict(
                size=14,  # Schriftgröße für den Titel
                family="Arial, sans-serif",  # Schriftart für den Titel
                color="black"  # Schriftfarbe
            ),
            y=0.95,  # Vertikale Position des Titels
            x=0.009,  # Horizontale Position des Titels
            xanchor='left',  # Ausrichtung des Titels
            yanchor='top'  # Vertikale Ankerung des Titels
    )
)
       
   
    fig.update_traces(marker=dict(line=dict(color='DarkSlateGrey', width=0.5)))
    # Setze die y-Achse so, dass 100 das Maximum ist
    fig.update_yaxes(autorange="reversed", tickvals=[0, 20, 40, 60, 80, 100], ticktext=[100, 80, "","","",0])
    # Füge für jede Facette spezielle Linien hinzu
    for i in range(1, len(filtered_airlines['airline'].unique()) + 1):
        # Grüne Linie bei y=0 (entspricht 100% Optimum)
        fig.add_shape(
            type="line",
            xref=f"x{i}",
            yref=f"y{i}",
            x0=filtered_airlines['month_int'].min(),
            x1=filtered_airlines['month_int'].max(),
            y0=0,
            y1=0,
            line=dict(
                color="lime",
                width=2
            )
        )
        fig.add_annotation(
        x=filtered_airlines['month_int'].min()-1,  # Anfang des x-Bereichs für jede Facette
        y=35,  # Y-Position für den Pfeil, muss eventuell angepasst werden
        text="schlechter",
          textangle=-90,  # Der Text der Annotation,
        showarrow=False,  # Zeigt den Pfeil
        arrowhead=2,  # Stil des Pfeilkopfes
        xref=f"x{i}",  # x-Referenz auf die entsprechende Facettenachse
        yref=f"y{i}",  # y-Referenz auf die entsprechende Facettenachse
        ax=-3,  # Verschiebung des Pfeils in x-Richtung (links)
        ay=20,  # Verschiebung des Pfeils in y-Richtung (nach unten)
        arrowcolor="red",  # Farbe des Pfeils
        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="black"
        ),
        arrowsize=1,  # Größe des Pfeils, kann skaliert werden
        arrowwidth=2,  # Breite des Pfeilstrichs
    )
        # Rote gepunktete Linie bei y=20 (entspricht 80% Schwellenwert)
        fig.add_shape(
            type="line",
            xref=f"x{i}",
            yref=f"y{i}",
            x0=filtered_airlines['month_int'].min(),
            x1=filtered_airlines['month_int'].max(),
            y0=20,
            y1=20,
            line=dict(
                color="red",
                width=1,
                dash="dot"
            )
        )
    return fig



#Dash-App starten
if __name__ == '__main__':
    app.run_server(debug=True)