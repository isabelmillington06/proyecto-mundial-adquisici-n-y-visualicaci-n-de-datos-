import plotly.express as px
import matplotlib.pyplot as plt


## PARTE 2

## ANÁLISIS 2. Rendimiento de Jugadores Clave. Se quiere evaluar qué jugadores han dado un mejor rendimiento en el Mundial 
# y si realmente las grandes estrellas han cumplido las expectativas o han decepcionado. Para ello genere las siguientes visualizaciones utilizando las librerías Ploty y Streamlit:

## 4) Crear gráfico de dispersión que enfrente "valor_mercado" y "calificacion_media" para los jugadores que han jugado mas de 180 minutos

import pandas as pd 

jugadores = pd.read_excel("jugadores.xlsx")

jugadores_filtrado = jugadores[jugadores["minutos_jugados"] >= 180]

fig = px.scatter(jugadores_filtrado, x = "valor_mercado", y = "calificacion_media", color = "posicion", size = "partidos_jugados", hover_data="seleccion_nacional", title= "Relación entre el Valor de Mercado y el Rendimiento de los Jugadores en el Mundial" )

fig.show()

## Calculamos la correlacion entre las dos varibale para responder a la pregunta 
correlacion = jugadores_filtrado["valor_mercado"].corr(jugadores_filtrado["calificacion_media"])

print("Correlación:", correlacion)

## 4) 

