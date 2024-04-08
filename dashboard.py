import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Streamlit App
st.markdown('<h1 style="font-size: 16px;">Stornierungen ("cancellations") nach Gründen</h1>', unsafe_allow_html=True)

# Pfad zur lokalen CSV-Datei
file_path = r"C:\Users\rober\OneDrive\Vorlesungen\Datenbasierte Fallstudien\Visualisierungen\Flights\Flights\cancellations_summary.csv"

# Lese die CSV-Datei direkt
cancellations_summary = pd.read_csv(file_path)

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
                             hoverinfo='label+percent', text=final_data['text'],  # Verwende 'final_data' für 'text'
                             textinfo='text',
                             marker=dict(colors=colors_hex),
                             rotation=194,
                             direction="clockwise",
                             hovertemplate=final_data['info'].apply(lambda x: f'<b> %{{label}}</b><b> | Anzahl der Vorfälle nach Airline</b><br>{x}<extra></extra>'),
                             hole=.6,
                             sort=False)])

# Anpassen der Fontsize bei den Labels
fig.update_traces(textfont_size=14) 

# Anpassen der Größe des Diagramms und Legende entfernen
fig.update_layout(width=450, height=400, showlegend=False)


# Diagramm in Streamlit anzeigen
st.plotly_chart(fig)