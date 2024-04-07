import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors

# Beispiel-Daten, ersetze dies durch deine tatsächlichen Daten
cancellations_summary = pd.read_csv(r"C:\Users\rober\OneDrive\Vorlesungen\Datenbasierte Fallstudien\Visualisierungen\Flights\Flights\cancellations_summary.csv")

# Farbschema
colors_hex = ["#db0d27", "#ec511a", "#f87d07", "#ffa600"]
alpha = 0.65
colors = [mcolors.to_rgba(c, alpha=alpha) for c in colors_hex][:len(cancellations_summary)]

# Funktion zur Erstellung des Kreisdiagramms
def create_pie_chart(data):
    fig, ax = plt.subplots()
    wedges, texts = ax.pie(data['cancellations'], startangle=90, counterclock=False, colors=colors, wedgeprops=dict(width=0.45))

    # Annotationen hinzufügen
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        x = np.cos(np.deg2rad(ang))
        y = np.sin(np.deg2rad(ang))
        
        horizontalalignment = 'left' if x > 0 else 'right'
        label_text = f"{data.iloc[i]['cancellation_reason']}\n{data.iloc[i]['cancellations']}\n({data.iloc[i]['percentage']}%)"
        
        ax.annotate(label_text, xy=(x, y), xycoords='data', 
                    xytext=(1.2*np.sign(x), 1.2*y), textcoords='data',
                    arrowprops=dict(arrowstyle="-", color="black", connectionstyle="angle,angleA=0,angleB=90"),
                    horizontalalignment=horizontalalignment, verticalalignment='center')
    
    plt.title('Gründe für Stornierungen ("cancellation_reasons")', pad=20)
    return fig

# Streamlit App
st.title('Stornierungsanalyse')

# Daten und Diagramm darstellen
sorted_data = cancellations_summary.sort_values('cancellations', ascending=False)
fig = create_pie_chart(sorted_data)
st.pyplot(fig)
