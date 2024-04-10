import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc

# Dash-App erstellen
app = Dash(__name__, external_stylesheets=[
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css'
])

# URL zur CSV-Datei
URL = "https://media.githubusercontent.com/media/swrobuts/Flights/main/cancellations_summary.csv"

# Lese die CSV-Datei ein
cancellations_summary = pd.read_csv(URL)

# CSS-Stile definieren
styles = {
    'sidebar': {
        'background-color': '#f8f9fa',
        'min-height': '100vh',
        'padding': '20px'
    }
}

# Gesamtzahl der stornierten Flüge berechnen
total_cancelled_flights = cancellations_summary['cancellations'].sum()

# Card für die Gesamtzahl der stornierten Flüge erstellen
total_cancelled_flights_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Gesamtzahl der stornierten Flüge", className="card-title"),
            html.P(f"{total_cancelled_flights:,.0f}", className="card-text"),
        ]
    ),
    className="mb-4",
)

# Layout der Dash-App
app.layout = html.Div([
    html.Div([
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
            )
        ], className='col-md-2 sidebar', style=styles['sidebar']),
        html.Div([
            html.H1('Dashboard für Stornierungen', className='text-center mb-4'),
            html.Div([
                dbc.Row([
                    dbc.Col(total_cancelled_flights_card, width=4),
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
                                    html.H5("Gesamtzahl der Stornierungen", className="card-title"),
                                    html.P(id='total-cancellations', className="card-text"),
                                ]
                            ),
                            className="mb-4",
                        ),
                        width=4,
                    ),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='cancellations-bar-chart'), width=6),
                    dbc.Col(dcc.Graph(id='cancellations-pie-chart'), width=6),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='cancellations-line-chart'), width=12),
                ]),
            ])
        ], className='col-md-10')
    ], className='row')
])

# Callback-Funktionen
# ...

# Callback für das Balkendiagramm
@app.callback(
    Output('cancellations-bar-chart', 'figure'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value')]
)
def update_bar_chart(selected_airline, selected_reason):
    filtered_data = cancellations_summary.copy()
   
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
   
    cancellations_sorted = filtered_data.groupby('airline', as_index=False)['cancellations'].sum().sort_values(by='cancellations', ascending=True)
    cancellations_sorted['formatted_cancellations'] = cancellations_sorted['cancellations'].apply(lambda x: "{:,.0f}".format(x).replace(",", "."))
   
    fig = px.bar(
        cancellations_sorted,
        y='airline',
        x='cancellations',
        orientation='h',
        color_discrete_sequence=['#7B96C4'],
        text='formatted_cancellations'
    )
   
    max_cancellations = cancellations_sorted['cancellations'].max()
    padding = max_cancellations * 0.2
   
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, max_cancellations + padding], title_text=''),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title_text=''),
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=0, r=0, t=0, b=0)
    )
   
    fig.update_traces(textfont_size=11)
   
    return fig

# Callback für das Kreisdiagramm
@app.callback(
    Output('cancellations-pie-chart', 'figure'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value')]
)
def update_pie_chart(selected_airline, selected_reason):
    filtered_data = cancellations_summary.copy()
   
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
   
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
   
    fig.update_layout(height=350, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
   
    return fig

# Callback für das Liniendiagramm
@app.callback(
    Output('cancellations-line-chart', 'figure'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value')]
)
def update_line_chart(selected_airline, selected_reason):
    filtered_data = cancellations_summary.copy()
   
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
   
    line_data = filtered_data.groupby('airline', as_index=False)['cancellations'].sum()
   
    fig = px.line(line_data, x='airline', y='cancellations')
   
    fig.update_layout(
        xaxis=dict(title='Fluggesellschaft'),
        yaxis=dict(title='Anzahl der Stornierungen'),
        height=350,
        margin=dict(l=0, r=0, t=0, b=0)
    )
   
    return fig

# Dash-App starten
if __name__ == '__main__':
    app.run_server(debug=True)