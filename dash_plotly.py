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
import kaleido

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

# CSS-Stile definieren
styles = {
    'sidebar': {
        'background-color': '#f8f9fa',
        'min-height': '100vh',
        'padding': '20px',
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'bottom': 0,
        'width': '16.67%',
        'transition': 'transform 0.3s'
    },
    'icon': {
        'position': 'fixed',
        'top': '50%',
        'left': '16.67%',
        'transform': 'translate(-50%, -50%)',
        'cursor': 'pointer',
        'font-size': '24px',
        'color': 'red',
        'background-color': '#f8f9fa',
        'border-radius': '0 50% 50% 0',
        'padding': '20px',
        'box-shadow': '0 0 5px rgba(0, 0, 0, 0.2)',
        'z-index': '1000',
        'transition': 'left 0.3s'
    },
    'content': {
        'margin-left': '20%',
        'transition': 'margin-left 0.3s'
    }
}

# Layout der Dash-App
# Layout der Dash-App
app.layout = html.Div([
    html.Div([
        html.H3('Filter'),
        dcc.Dropdown(
            id='airline-dropdown',
            options=[{'label': airline, 'value': airline} for airline in ['Alle'] + sorted(cancellations_summary['airline'].unique().tolist())],
            value='Alle',
            clearable=False
        ),
        dcc.Dropdown(
            id='reason-dropdown',
            options=[{'label': reason, 'value': reason} for reason in ['Alle'] + sorted(cancellations_summary['cancellation_reason'].unique().tolist())],
            value='Alle',
            clearable=False
        ),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': year, 'value': year} for year in ['Alle'] + sorted(cancellations_summary['year'].unique().tolist())],
            value='Alle',
            clearable=False
        ),
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': month, 'value': month} for month in ['Alle'] + sorted(cancellations_summary['month'].unique().tolist())],
            value='Alle',
            clearable=False
        ),
    ], id='sidebar', style=styles['sidebar']),
    html.I(id="toggle-sidebar", n_clicks=0, style=styles['icon']),
    html.Div([
        html.H1('Dashboard für Stornierungen', className='text-center mb-4'),
        html.Div([
            dbc.Row([
                dbc.Col(
                    dbc.Card(id='total-cancelled-flights-card', className="mb-4"),
                    width=4
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Durchschnittliche Stornierungen pro Fluggesellschaft", className="card-title"),
                                html.P(id='avg-cancellations', className="card-text"),
                            ]
                        ),
                        className="mb-4",
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            [
                                html.H5("Stornierte Flüge", className="card-title"),
                                html.P(id='total-cancellations', className="card-text"),
                            ]
                        ),
                        className="mb-4",
                    ),
                    width=4,
                ),
            ]),
            dbc.Row([
                dbc.Col(html.Div(id='flights-table'), width=5),
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='cancellations-bar-chart', config={'displayModeBar': False}),
                        html.Div(style={'width': '15px'}),  # Platzhalter für den Abstand
                        dcc.Graph(id='cancellations-deviation-chart', config={'displayModeBar': False})
                    ], style={'display': 'flex'}),
                    width=6
                ),
                dbc.Col(dcc.Graph(id='cancellations-pie-chart', config={'displayModeBar': False}), width=3),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='cancellations-sm-chart', config={'displayModeBar': False}), width=12),
            ]),
        ])
    ], id='content', style=styles['content'])
])




# Callback für das Ein-/Ausklappen der Sidebar
@app.callback(
    [Output("sidebar", "style"),
     Output("toggle-sidebar", "style"),
     Output("toggle-sidebar", "className"),
     Output("content", "style")],
    [Input("toggle-sidebar", "n_clicks")],
    [State("sidebar", "style"),
     State("toggle-sidebar", "style"),
     State("content", "style")],
)
def toggle_sidebar(n_clicks, sidebar_style, icon_style, content_style):
    if n_clicks % 2 == 1:
        sidebar_style['transform'] = 'translateX(-100%)'
        icon_style['left'] = '0'
        content_style['margin-left'] = '0'
        return sidebar_style, icon_style, "fas fa-chevron-right", content_style
    else:
        sidebar_style['transform'] = 'translateX(0)'
        icon_style['left'] = '16.67%'
        content_style['margin-left'] = '19.67%'
        return sidebar_style, icon_style, "fas fa-chevron-left", content_style

# Callback für die Gesamtzahl der stornierten Flüge und die Kachel
@app.callback(
    Output('total-cancelled-flights-card', 'children'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_total_cancellations(selected_airline, selected_reason, selected_year, selected_month):
    filtered_data = cancellations_summary.copy()
   
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
    if selected_year != 'Alle':
        filtered_data = filtered_data[filtered_data['year'] == selected_year]
    #if selected_month != 'Alle':
       # filtered_data = filtered_data[filtered_data['month'] == selected_month]
   
    total_cancellations = filtered_data['cancellations'].sum()
   
    if selected_year != 'Alle' and selected_month != 'Alle':
        current_date = datetime(int(selected_year), int(selected_month), 1)
        previous_date = current_date - relativedelta(months=1)
        previous_data = cancellations_summary[(cancellations_summary['year'] == previous_date.year) & (cancellations_summary['month'] == previous_date.month)]
    elif selected_year != 'Alle':
        current_date = datetime(int(selected_year), 1, 1)
        previous_date = current_date - relativedelta(years=1)
        previous_data = cancellations_summary[cancellations_summary['year'] == previous_date.year]
    else:
        previous_data = pd.DataFrame()
   
    if not previous_data.empty:
        previous_cancellations = previous_data['cancellations'].sum()
        difference = total_cancellations - previous_cancellations
        percentage_change = (difference / previous_cancellations) * 100 if previous_cancellations != 0 else 0
       
        if difference > 0:
            arrow = html.Span('▲', style={'color': 'red', 'font-size': '25px'})
        else:
            arrow = html.Span('▼', style={'color': 'green', 'font-size': '25px'})
       
        # Erstelle die Sparklines für die monatlichen Stornierungen
        if selected_year != 'Alle':
            monthly_data = filtered_data.groupby('month')['cancellations'].sum().reset_index()
            month_names = [datetime(2000, int(m), 1).strftime('%b') for m in monthly_data['month']]
            sparkline_fig = go.Figure(go.Bar(
                x=month_names,
                y=monthly_data['cancellations'],
                marker_color='#7B96C4'
            ))
            sparkline_fig.update_traces(
                text=monthly_data['cancellations'],
                textposition='none',
                hoverinfo='text',
                hovertext=[f"{mon}: {val}" for mon, val in zip(month_names, monthly_data['cancellations'])]
            )
            sparkline_fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(
                    showgrid=False, 
                    zeroline=False, 
                    showticklabels=True, 
                    tickmode='array', 
                    tickvals=[month_names[0], month_names[-1]], 
                    ticktext=[month_names[0], month_names[-1]]
                ),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                title_text='',
                margin=dict(l=0, r=0, t=10, b=0),
                height=60,
                width=250,
                hovermode='x'
            )
        else:
            sparkline_fig = None
       
        return [
            html.H5("Stornierte Flüge", className="card-title"),
            html.P([
                html.Span(f"In {selected_year}: "),
                html.Span(f"{total_cancellations:,.0f}".replace(",", "."))
            ], className="card-text"),
            html.P([
                html.Span(f"Diff. zu {previous_date.year}: "),
                html.Span(f"{difference:,.0f} ".replace(",", ".")),
                html.Span(f"({percentage_change:.1f} %) "),
                arrow
            ], className="card-text"),
            dcc.Graph(figure=sparkline_fig, config={'displayModeBar': False}) if sparkline_fig else None
        ]
    else:
        return [
            html.H5("Stornierte Flüge", className="card-title"),
            html.P(f"{total_cancellations:,.0f}".replace(",", "."), className="card-text")
        ]


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
                width=0.6
            )
        )
        sparkline_fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
            ),
            height=24,
            width=130,
            margin=dict(l=0, r=0, t=0, b=4),
            xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            plot_bgcolor='rgba(255,255,255,1)',
            paper_bgcolor='rgba(255,255,255,1)'
        )

        # Umwandlung des Pünktlichkeitsprozentsatzes und der Stornoquote in das gewünschte Format
        percent_format = lambda x: "{}%".format(x.replace('.', ','))
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
            html.Span(cancellation_rate_formatted, style={'display': 'inline-block', 'textAlign': 'right', 'width': '50px'})
        ]
    )
    
        arrivals_style = {'width': '20%', 'textAlign': 'center'}
        departures_style = {'width': '20%', 'textAlign': 'center'}
        arrivals_content = html.Div(
        style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'},
        children=[
        html.Span(
            "{}%".format(monthly_totals['percent of arrivals on time'].iloc[-1].astype(str).replace('.', ',')),
            style={'display': 'inline-block', 'textAlign': 'right', 'width': '50px'}
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
            "{}%".format(monthly_totals['percent of departures on time'].iloc[-1].astype(str).replace('.', ',')),
            style={'display': 'inline-block', 'textAlign': 'right', 'width': '50px'}
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
            html.Td(airline, style={'width': '20%', 'paddingRight': '0px'}),
            html.Td(dcc.Graph(figure=sparkline_fig, config={'displayModeBar': False}), style={'width': '3%', 'paddingRight': '1px'}),
            html.Td(flights_value_and_bar, style={'width': '17%', 'paddingRight': '8px'}),
            html.Td(arrivals_content, style=arrivals_style),
            html.Td(departures_content, style=departures_style),
            html.Td(cancellation_content, style={'width': '10%', 'textAlign': 'center','paddingRight': '17px',})  
    ], style={'border-bottom': '1px solid #d3d3d3'}))

    # Gib die gesamte Tabelle zurück
    return html.Table([
        html.Thead(html.Tr([
            html.Th('Airline', style={'paddingRight': '0px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('', style={'paddingRight': '1px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th(flights_label, style={'paddingRight': '8px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('⌀ Pünktlichkeit (Ankunft)', style={'paddingRight': '8px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('⌀ Pünktlichkeit (Abflug)', style={'paddingRight': '8px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle'}),
            html.Th('⌀ Stornoquote', style={'paddingRight': '1px', 'border-top': '1px solid black', 'border-bottom': '1px solid black', 'height': '30px', 'vertical-align': 'middle', 'horizontal-align': 'center'})
        ], style={'background-color': 'white', 'margin-bottom': '10px'})),
        html.Tbody([
            html.Tr([html.Td('', style={'height': '10px'}) for _ in range(5)]),  # Leere Zeile einfügen
            *table_rows  # Bestehende Tabellenzeilen einfügen
        ], style={'border-top': '1px solid black'})
    ], style={'font-size': '0.85rem', 'width': '100%', 'height': '70%'})



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
    y_shift = 21  # Verschiebung entlang der y-Achse
   
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
        height=490,
        width=550,
        margin=dict({'pad':0}, l=0, r=0, t=60, b=0),
        bargap=0.4  # Abstand zwischen den Balken
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
        deviation_data['formatted_deviation'] = deviation_data['deviation'].apply(lambda x: f"{x:+.1f}".replace('.', ',') + '%')

       
        # Sortierung des Abweichungsdiagramms entsprechend der Sortierung des Balkendiagramms
        deviation_data = deviation_data.set_index('airline').reindex(cancellations_sorted['airline']).reset_index()
       
        max_deviation = deviation_data['deviation'].abs().max()
       
        fig_deviation = go.Figure()
       
        line_height = 34.7  # Höhe jeder Linie
       
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
                range=[0, 490],
                title_text='',
                automargin=True
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            height=490,
            width=350,  
            margin=dict({'pad':2}, l=0, r=0, t=60, b=0)
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
            width=350,
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
    sorted_data['text'] = sorted_data.apply(lambda x: f"{x['cancellation_reason']}<br>{x['cancellations']:,}".replace(",", ".") + f"<br>({x['percentage']}%)", axis=1)
   
    grouped_data = filtered_data.groupby(['cancellation_reason', 'airline'], as_index=False)['cancellations'].sum()
    hover_texts = grouped_data.groupby('cancellation_reason').apply(
        lambda x: "<br>".join([f"{row['airline']}: {row['cancellations']}" for index, row in x.iterrows()])
    ).reset_index(name='info')
   
    final_data = filtered_data.groupby('cancellation_reason', as_index=False)['cancellations'].sum()
    final_data = final_data.merge(hover_texts, on='cancellation_reason', how='left')
   
    final_data['percentage'] = (final_data['cancellations'] / final_data['cancellations'].sum() * 100).round(1)
    final_data['text'] = final_data.apply(lambda x: f"<b>{x['cancellation_reason']}</b><br>{x['cancellations']:,}".replace(",", ".") + f"<br>({x['percentage']} %)", axis=1)
   
    colors_hex = ["rgba(236, 81, 26, 0.65)", "rgba(248, 125, 7, 0.65)",
                  "rgba(255, 166, 0, 0.65)", "rgba(219, 13, 39, 0.65)"]
   
    fig = go.Figure(data=[go.Pie(labels=final_data['cancellation_reason'], values=final_data['cancellations'],
                                 hoverinfo='label+percent', text=final_data['text'],
                                 textinfo='text',
                                 marker=dict(colors=colors_hex),
                                 rotation=194,
                                 direction="clockwise",
                                 hovertemplate=final_data['info'].apply(lambda x: f'<b> %{{label}}</b><b> | Anzahl der Vorfälle nach Airline</b><br>{x}<extra></extra>'),
                                 hole=.65,
                                 sort=False)])
   
    fig.update_traces(textfont_size=11)
   
    fig.update_layout(height=350, width=360, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
   
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
                    facet_col_wrap=7,  # Setzen Sie hier die Anzahl der Spalten
                    height=530,
                    facet_col_spacing=0.01,
                    facet_row_spacing= 0.3,
                    title='Performance der Airlines: Pünktlichkeit bei Ankunft und Abflug')


    # Anpassen der Markergröße und Transparenz basierend auf der Abweichung bzw. Wert
    for trace in fig.data:
        if 'arrivals_deviation' in trace.name:
            #trace['marker']['opacity'] = [0.7 + 0.1 * (1 - abs(y / 100)) for y in trace.y]
            trace['marker']['size'] = [3 + 6 * (1 - abs(y / 100)) for y in trace.y]  # Moderate Größenanpassung
        else:
           # trace['marker']['opacity'] = 0.6  
            trace['marker']['size'] = 8  # Standardgröße

    # Update für die Achseneigenschaften, um sicherzustellen, dass Monate konsistent sind
    fig.update_xaxes(tickmode='array',
                        tickvals=[filtered_airlines['month_int'].min(),
                        filtered_airlines['month_int'].max()],
                        ticktext=[filtered_airlines.loc[filtered_airlines['month_int'].idxmin(), 'month'], filtered_airlines.loc[filtered_airlines['month_int'].idxmax(), 'month']],
                        showticklabels=True,
                        linecolor='grey', 
                        title_text='')
    fig.update_yaxes(title_text='') 

    # Einstellung des Layouts für weißen Hintergrund und Legende
    fig.update_layout(
        plot_bgcolor='rgba(255, 255, 255, 1)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
        showlegend=True,
        margin=dict(l=20, r=0, t=60, b=20),
        #grid=dict(rows=filtered_airlines['airline'].nunique() // 3, columns=3, pattern='independent', xgap=0.2, ygap=0.8)  
    )


    fig.update_traces(marker=dict(size=10, line=dict(color='DarkSlateGrey', width=0.5)))

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