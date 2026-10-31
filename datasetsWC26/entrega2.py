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

## 5) Definir nuevas métricas: goles/minuto, goles+asistencias/minuto, asistencias/minuto, goles_concedidos/minuto, tarjetas_amarillas/minuto y tarjetas_rojas/minuto

## Para crear las nuevas métricas voy a añadir las nuevas varibles al datafrma jugadores:

jugadores_filtrado["goles_minuto"] = jugadores_filtrado["goles"]/jugadores_filtrado["minutos_jugados"]
jugadores_filtrado["goles_mas_asistencias_minuto"] = (jugadores_filtrado["goles"] + jugadores_filtrado["asistencias"])/jugadores["minutos_jugados"]
jugadores_filtrado["asistencias_minuto"] = jugadores_filtrado["asistencias"]/jugadores_filtrado["minutos_jugados"]
jugadores_filtrado["goles_concedidos_minuto"] = jugadores_filtrado["goles_concedidos"]/jugadores_filtrado["minutos_jugados"]
jugadores_filtrado["tarjetas_amarillas_minuto"] = jugadores_filtrado["tarjetas_amarillas"]/jugadores_filtrado["minutos_jugados"]
jugadores_filtrado["tarjetas_rojas_minuto"] = jugadores_filtrado["tarjetas_rojas"]/jugadores_filtrado["minutos_jugados"]

## Luego, para calcular la métrica agregada la vamos a definir nosotros, por ejemplo, los goles metidos es importante entonces vamos a darle un valor más alto que asistencias y así para todas las varibles. 
## Para las variables 'negativas' (goles_concedidos, tarjetas amarillas y tarjetas rojas) damos valores negativos. 

jugadores_filtrado["metrica_agregada"] = (3* jugadores_filtrado["goles_minuto"]) + (2*jugadores_filtrado["goles_mas_asistencias_minuto"]) + (2*jugadores_filtrado["asistencias_minuto"]) - (2*jugadores_filtrado["goles_concedidos_minuto"]) - (jugadores_filtrado["tarjetas_amarillas_minuto"]) - (3*jugadores_filtrado["tarjetas_rojas_minuto"])

## Para el gráfico, lo primero que vamos a hacer es crear una nueva varibale "ranking_mercado" que contenga el ranking que nos pide. 

jugadores_filtrado = jugadores_filtrado.sort_values(by = "valor_mercado", ascending=False)

jugadores_filtrado["ranking_mercado"] = range(1, len(jugadores_filtrado)+1)

## Ahora, como solo queremos los top 15, los seleccionamos:

top15 = jugadores_filtrado.sort_values(by="goles_minuto", ascending=False).head(15)

## Ahora creamos la gráfica de barras:
top15["ranking_texto"] = top15["ranking_mercado"].astype(str) + "º"
fig = px.bar(top15, x = "ranking_texto", y = "goles_minuto", color= "nombre_jugador", title="Top 15 jugadores por goles/minuto")

fig.update_layout(xaxis_title="Ranking en valor de mercado",yaxis_title="Goles por minuto")

fig.show()