import dash
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Dash-App erstellen
app = Dash(__name__, external_stylesheets=[
    'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css'
])

# URL zur CSV-Datei
URL = "https://media.githubusercontent.com/media/swrobuts/Flights/main/cancellations_summary.csv"
URL2 = ""

# Lese die CSV-Datei ein
cancellations_summary = pd.read_csv(URL)

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
                dbc.Col(dcc.Graph(id='cancellations-bar-chart'), width=6),
                dbc.Col(dcc.Graph(id='cancellations-pie-chart'), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(id='cancellations-line-chart'), width=12),
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
                margin=dict(l=0, r=0, t=0, b=0),
                height=100,
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



# Callback für das Balkendiagramm
@app.callback(
    Output('cancellations-bar-chart', 'figure'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_bar_chart(selected_airline, selected_reason, selected_year, selected_month):
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
   
    fig.update_layout(height=350, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
   
    return fig


# Callback für das Liniendiagramm



@app.callback(
    Output('cancellations-line-chart', 'figure'),
    [Input('airline-dropdown', 'value'),
     Input('reason-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('month-dropdown', 'value')]
)
def update_line_chart(selected_airline, selected_reason, selected_year, selected_month):
    filtered_data = cancellations_summary.copy()
   
    if selected_airline != 'Alle':
        filtered_data = filtered_data[filtered_data['airline'] == selected_airline]
    if selected_reason != 'Alle':
        filtered_data = filtered_data[filtered_data['cancellation_reason'] == selected_reason]
    if selected_year != 'Alle':
        filtered_data = filtered_data[filtered_data['year'] == selected_year]
    if selected_month != 'Alle':
        filtered_data = filtered_data[filtered_data['month'] == selected_month]

    line_data = filtered_data.groupby(['year', 'month'], as_index=False)['cancellations'].sum()
    line_data['date'] = pd.to_datetime(line_data[['year', 'month']].assign(day=1))

    fig = px.line(line_data, x='date', y='cancellations')

    fig.update_layout(
    xaxis=dict(title='Datum'),
    yaxis=dict(title='Anzahl der Stornierungen'),
    height=350,
    margin=dict(l=0, r=0, t=0, b=0)
)

    return fig

#Dash-App starten
if __name__ == '__main__':
    app.run_server(debug=True)