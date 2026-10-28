import plotly as px

## PARTE 2

## ANÁLISIS 2. Rendimiento de Jugadores Clave. Se quiere evaluar qué jugadores han dado un mejor rendimiento en el Mundial 
# y si realmente las grandes estrellas han cumplido las expectativas o han decepcionado. Para ello genere las siguientes visualizaciones utilizando las librerías Ploty y Streamlit:

import pandas as pd 

jugadores = pd.read_csv("jugadores.xlsx")



jugadores["valor_de_mercado"]
jugadores["calificacion_media"]

px.scatter