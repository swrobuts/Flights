import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Seitenlayouteinstellungen anpassen
st.set_page_config(layout="wide")

# Streamlit App Header
st.title('Dashboard für Stornierungen')

# URL zur CSV-Datei
URL = "https://media.githubusercontent.com/media/swrobuts/Flights/main/cancellations_summary.csv"

# Lese die CSV-Datei ein
cancellations_summary = pd.read_csv(URL)

# Sidebar für Filter
st.sidebar.header('Filter')

# Dropdown für Fluggesellschaften
airline_options = ['Alle'] + sorted(cancellations_summary['airline'].unique().tolist())
selected_airline = st.sidebar.selectbox('Fluggesellschaft', options=airline_options)

# Dropdown für Stornierungsgründe
reason_options = ['Alle'] + sorted(cancellations_summary['cancellation_reason'].unique().tolist())
selected_reason = st.sidebar.selectbox('Stornierungsgrund', options=reason_options)

# Daten basierend auf der Auswahl filtern
if selected_airline != 'Alle':
    cancellations_summary = cancellations_summary[cancellations_summary['airline'] == selected_airline]
if selected_reason != 'Alle':
    cancellations_summary = cancellations_summary[cancellations_summary['cancellation_reason'] == selected_reason]

# Zwei Spalten für die Container erstellen
col1, col2 = st.columns([2, 2], gap="large")  # Verhältnis von 3:2 für die Spaltenbreiten

# Erster Container
with col1:
    st.header('Statistiken')
   
    # Stornierungen nach Airlines
    cancellations_sorted = cancellations_summary.groupby('airline', as_index=False)['cancellations'].sum().sort_values(by='cancellations', ascending=True)
    cancellations_sorted['formatted_cancellations'] = cancellations_sorted['cancellations'].apply(lambda x: "{:,.0f}".format(x).replace(",", "."))
   
    fig = px.bar(
        cancellations_sorted,
        y='airline',
        x='cancellations',
        orientation='h',
        color_discrete_sequence=['#49a9db'],
        text='formatted_cancellations'
    )
   
    max_cancellations = cancellations_sorted['cancellations'].max()
    padding = max_cancellations * 0.2
   
    fig.update_traces(textposition='outside')
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, max_cancellations + padding], title_text=''),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=True, title_text=''),
        plot_bgcolor='rgba(0,0,0,0)',
        width=400,  # Breite des Balkendiagramms anpassen
        height=370,
        margin=dict(l=0, r=260, t=10, b=0)
    )
   
    # Anpassen der Fontsize bei den Labels
    fig.update_traces(textfont_size=16)
    
    # Diagramm in Streamlit anzeigen
    st.plotly_chart(fig, use_container_width=True)

# Zweiter Container
with col2:
    st.header('Statistiken')
   
    # Daten vorbereiten und nach 'cancellations' sortieren
    sorted_data = cancellations_summary.groupby('cancellation_reason', as_index=False)['cancellations'].sum().sort_values(by='cancellations', ascending=False)
    sorted_data['percentage'] = (sorted_data['cancellations'] / sorted_data['cancellations'].sum() * 100).round(1)
    sorted_data['text'] = sorted_data.apply(lambda x: f"{x['cancellation_reason']}<br>{x['cancellations']:,}".replace(",", ".") + f"<br>({x['percentage']}%)", axis=1)
   
    # Gruppierung der Fluggesellschaften und Berechnung der Gesamtanteile
    grouped_data = cancellations_summary.groupby(['cancellation_reason', 'airline'], as_index=False)['cancellations'].sum()
    hover_texts = grouped_data.groupby('cancellation_reason').apply(
        lambda x: "<br>".join([f"{row['airline']}: {row['cancellations']}" for index, row in x.iterrows()])
    ).reset_index(name='info')
   
    # Füge den vorbereiteten Hover-Text den ursprünglichen Daten hinzu
    final_data = cancellations_summary.groupby('cancellation_reason', as_index=False)['cancellations'].sum()
    final_data = final_data.merge(hover_texts, on='cancellation_reason', how='left')
   
    # Prozentwerte und formatierten Text zu 'final_data' hinzufügen
    final_data['percentage'] = (final_data['cancellations'] / final_data['cancellations'].sum() * 100).round(1)
    final_data['text'] = final_data.apply(lambda x: f"<b>{x['cancellation_reason']}</b><br>{x['cancellations']:,}".replace(",", ".") + f"<br>({x['percentage']} %)", axis=1)
   
    # Farbschema mit Alpha-Wert
    colors_hex = ["rgba(236, 81, 26, 0.65)", "rgba(248, 125, 7, 0.65)",
                  "rgba(255, 166, 0, 0.65)", "rgba(219, 13, 39, 0.65)"]
   
    # Erstellung des Kreisdiagramms
    fig = go.Figure(data=[go.Pie(labels=final_data['cancellation_reason'], values=final_data['cancellations'],
                                 hoverinfo='label+percent', text=final_data['text'],
                                 textinfo='text',
                                 marker=dict(colors=colors_hex),
                                 rotation=194,
                                 direction="clockwise",
                                 hovertemplate=final_data['info'].apply(lambda x: f'<b> %{{label}}</b><b> | Anzahl der Vorfälle nach Airline</b><br>{x}<extra></extra>'),
                                 hole=.65,
                                 sort=False)])
   
    # Anpassen der Fontsize bei den Labels
    fig.update_traces(textfont_size=13)
   
    # Anpassen der Größe des Diagramms und Legende entfernen
    fig.update_layout(width=300, height=350, showlegend=False, margin=dict(l=10, r=500, t=80, b=0))  # Rechten Rand des Kreisdiagramms anpassen
   
    # Diagramm in Streamlit anzeigen
    st.plotly_chart(fig, use_container_width=True)

# Streamlit-App starten
st.title('Analyse der Stornierungen nach Fluggesellschaft')