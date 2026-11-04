import plotly.express as px
import streamlit as st
from entrega1 import eventos
from entrega1 import partidos
from entrega1 import jugadores
import plotly.graph_objects as go
import pandas as pd

## PARTE 2

# ANÁLISIS 1
st.header("Análisis 1")

# GRÁFICO DE BARRAS
# crear el df partidos y eventos para el gráfico
st.subheader("Gráfico de barras: eventos de un partido")
partidos_grafico = partidos.copy()
eventos_grafico = eventos.copy()

partidos_grafico["etiqueta_partido"] = (partidos_grafico["index_partido"].astype(str)+ " - " + partidos_grafico["seleccion_local"].astype(str)+" vs "+partidos_grafico["seleccion_visitante"].astype(str))


# relacionar los eventos con sus partidos
eventos_grafico = eventos_grafico.merge(partidos_grafico[["index_partido","etiqueta_partido"]].drop_duplicates("index_partido"),on="index_partido",how="left")

# seleccionar partido
partidos_disponibles = (eventos_grafico[["index_partido","etiqueta_partido"]].dropna(subset=["etiqueta_partido"]).drop_duplicates(subset=["index_partido"]).sort_values("index_partido"))

if partidos_disponibles.empty:
    st.warning("No hay partidos relacionados con los eventos")
else:
    etiquetas = partidos_disponibles["etiqueta_partido"].tolist()
    partido_elegido = st.selectbox("Selecciona un partido:", options=etiquetas)

# Filtrar eventos 
    datos = eventos_grafico[eventos_grafico["etiqueta_partido"] == partido_elegido].copy()

    if not datos.empty:
        datos["minuto_evento"] = pd.to_numeric(datos["minuto_evento"],errors="coerce")
        datos = datos.dropna(subset=["minuto_evento","tipo_evento"])
        tipos = datos["tipo_evento"].unique()
        posiciones = {tipo: i+1 for i, tipo in enumerate(tipos)}
        datos["posicion"] = datos["tipo_evento"].map(posiciones)

        
        fig = px.bar(datos,x="minuto_evento",y="posicion",color="tipo_evento",hover_name="nombre_jugador",hover_data={"minuto_evento":True,"tipo_evento":True,"nombre_jugador":True,"seleccion_evento":True,"posicion":False},labels={"minuto_evento":"Minuto del partido","tipo_evento":"Tipo de evento","nombre_jugador":"Jugador","seleccion_evento":"Seleccion"}, title=f"Eventos del partido: {partido_elegido}")
        fig.update_layout(barmode="group",xaxis_title="Minuto del partido",yaxis=dict(title="Tipo de evento",tickmode="array",tickvals=list(posiciones.values()),ticktext=[str(tipo) for tipo in tipos]),legend_title="Tipo de evento",height=550)
        fig.update_xaxes(range=[0,max(95,datos["minuto_evento"].max()+5)],dtick=15)
        st.plotly_chart(fig,use_container_width=True)
        # tabla complementaria
        with st.expander("Ver tabla de eventos"):
            st.dataframe(datos[["minuto_evento","tipo_evento","nombre_jugador","seleccion_evento"]].sort_values("minuto_evento"),hide_index=True,use_container_width=True)

# MAPA DE CALOR
st.subheader("Mapa de calor: densidad de eventos en los partidos")
datos_calor = eventos.merge(partidos[["index_partido","ronda"]],on="index_partido",how="left").copy()

# filtramos la información
tipos = sorted(datos_calor["tipo_evento"].dropna().unique())
rondas = sorted(datos_calor["ronda"].dropna().unique())

tipo_elegido = st.selectbox("Tipo de envento",["Todos"] + list(tipos),key="tipo_calor")
ronda_elegida = st.selectbox("Rondas del partido", ["Todas"]+ list(rondas),key="ronda_calor")

# aplicar filtros
filtrados = datos_calor.copy()

if tipo_elegido != "Todos":
    filtrados = filtrados[filtrados["tipo_evento"] == tipo_elegido]

if ronda_elegida != "Todas":
    filtrados = filtrados[filtrados["ronda"]== ronda_elegida]

# agrupar los minutos en intervalos de 5 minutos
filtrados["intervalo"] = ((filtrados["minuto_evento"]// 5)*5).astype(int)

# crear el mapa de calor
calor = filtrados.groupby(["ronda","intervalo"]).size().reset_index(name="cantidad")

if not calor.empty:
    matriz = calor.pivot(index="ronda",columns="intervalo",values="cantidad").fillna(0)
    fig = px.imshow(matriz,labels={"x":"Minuto del partido (intervalos de 5 mins)","y":"Ronda","color":"Número de eventos"},aspect="auto",color_continuous_scale="YlOrRd",title="Densidad de eventos a lo largo del partido")
    st.plotly_chart(fig,use_container_width=True)
else:
    st.info("No hay eventos para los filtros seleccionados")

# respuesta a la pregunta "¿En qué intervalo se producen más goles?"
st.write(f"¿En qué intervalo se producen más goles?")
st.write(f"Observando el mapa de calor para el evento goles y todas las rondas, podemos observar que el intervalo en el que se producen más goles es el del minuto 90 hasta el 95, ya que es el que aparece más ocuro en el mapa")

# respuesta a la pregunta "¿Son las segundas partes más “entretenidas” que las primeras?"
st.write(f"¿Son las segundas partes más “entretenidas” que las primeras?")
st.write(f"Observando el mapa de calor deducimos que efectivamente las segundas partes (desde el minuto 45 hasta el 90) son más interesantes que las primeras partes (desde el minuto 0 hasta el minuto 45). Esto es así porque hay más densidad de eventos de todos los tipos (colores más intensos) en la segunda parte que en la primera")
st.write(f"Las primeras partes son más uniformes y claramente más suaves, salvo en fase de grupos, donde ya hay actividad alta desde el inicio")
st.write(f"En las rondas eliminatorias (octavos, cuartos, semifinales, tercer puesto y final), la segunda parte es algo más intensa sobre todo hacia el final")

# respuesta a la pregunta  " ¿Y las prórrogas?"
st.write("¿Y las prórrogas?")
st.write("Las prórrogas son en general menos intensas: casi todas las celdas entre el minuto 95 y el 115 son muy claras, es decir, pocos eventos")
st.write("Hay dos excepciones: en octavos de final, hay una celda más intensa y en la fase de grupos otra parecida. Podría deberse a algún partido atípico o por ejemplo a tandas de penaltis")


# GRÁFICO CIRCULAR
# seleccionar una selección
st.subheader("Gráfico circular: Eventos por selección")

selecciones = pd.concat([partidos["seleccion_local"],partidos["seleccion_visitante"]]).dropna().unique()
seleccion_elegida = st.selectbox("Selecciones", sorted(selecciones))

# filtramos los eventos de la seleccion
eventos_seleccion = eventos[eventos["seleccion_evento"] == seleccion_elegida].copy()

# eventos propios
print("Eventos de la selecicon")
print(eventos_seleccion["tipo_evento"].value_counts())

# buscamos los partidos que ha jugado la seleccion elegida
partidos_seleccion = partidos[(partidos["seleccion_local"] == seleccion_elegida)| (partidos["seleccion_visitante"] == seleccion_elegida)]


# seleccionamos todos los eventos de los partidos jugados
eventos_partidos_seleccion = eventos[eventos["index_partido"].isin(partidos_seleccion.index())].copy()

# calculamos los eventos a favor y los eventos en contra
eventos_partidos_seleccion["resultado_evento"] = "En contra"
eventos_partidos_seleccion.loc[eventos_partidos_seleccion["seleccion_evento"] == seleccion_elegida, "resultado_evento"] = "A favor"

# contamos los eventos por tipo y por resultado
resumen = (eventos_partidos_seleccion.groupby(["resultado_evento","tipo_evento"]).size().reset_index(name="cantidad"))
print("Resumen de los eventos")
print(resumen)

# creamos etiqueta
resumen["categoria"] = (resumen["tipo_evento"] + " - " + resumen["resultado_evento"])

# creamos gráfico circular
fig = px.pie(resumen, names="categoria", values="cantidad",title=f"Eventos de {seleccion_elegida}")
fig.update_layout(template="plotly_white")
fig.update_traces(textinfo="value")
st.plotly_chart(fig)


## ANÁLISIS 2. Rendimiento de Jugadores Clave. Se quiere evaluar qué jugadores han dado un mejor rendimiento en el Mundial 
# y si realmente las grandes estrellas han cumplido las expectativas o han decepcionado. Para ello genere las siguientes visualizaciones utilizando las librerías Ploty y Streamlit:

## 4) Crear gráfico de dispersión que enfrente "valor_mercado" y "calificacion_media" para los jugadores que han jugado mas de 180 minutos

import pandas as pd 

jugadores = pd.read_excel("jugadores.xlsx")

jugadores_filtrado = jugadores[jugadores["minutos_jugados"] >= 180]

fig = px.scatter(jugadores_filtrado, x = "valor_mercado", y = "calificacion_media", color = "posicion", size = "partidos_jugados", hover_data="seleccion_nacional", title= "Relación entre el Valor de Mercado y el Rendimiento de los Jugadores en el Mundial", template="plotly_white")

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
fig = px.bar(top15, x = "goles_minuto", y = "nombre_jugador", color= "goles_minuto",color_continuous_scale=["#66B8E5", "#62D2B0"], orientation="h", hover_data="ranking_mercado",title="Top 15 jugadores por goles/minuto",template="plotly_white")

fig.update_layout(xaxis_title="Goles por minuto",yaxis_title="Jugador",    coloraxis_showscale=False,)

fig.show()

## 6) Cree un gráfico de burbujas que relacione Minutos Jugados, Calificación Media y Valor de Mercado.

## Para marcar con un color específico a los jugadores que han marcado: 

def aplicar_color(goles):
    if goles > 0:
        color = "ha marcado"
    else: 
        color = "no ha marcado"
    return color

## Aquí creamos una nueva columna con el color que tiene que ser la burbuja de ese jugador:
jugadores_filtrado["color"] = jugadores_filtrado["goles"].apply(aplicar_color)

## Creamos el gráfico:

selecciones = st.sidebar.multiselect("Selección",jugadores_filtrado["seleccion_nacional"].dropna().unique(), default=jugadores_filtrado["seleccion_nacional"].dropna().unique())
posiciones = st.sidebar.multiselect("Posición",jugadores_filtrado["posicion"].dropna().unique(),default=jugadores_filtrado["posicion"].dropna().unique())

view = jugadores_filtrado[jugadores_filtrado["seleccion_nacional"].isin(selecciones) & jugadores_filtrado["posicion"].isin(posiciones)].copy() 
if view.empty: 
    st.info('No hay datos con estos filtros')


view = view.copy() 
view['obs_id'] = view.index

## En este gráfico se relacionan las tres varibales; dos están en los ejes y la tercera (valor_mercado) se ve visualemnte por el tamaño de la burbuja:

fig = px.scatter(view, x = "minutos_jugados", y = "calificacion_media", size= "valor_mercado", color="color", color_discrete_map={"ha marcado": "blue","no ha marcado": "purple"}, hover_data=["seleccion_nacional", "posicion"], template="plotly_white", title= "Rendimiento de los Jugadores según Minutos, Calificación y Valor de Mercado")
event = st.plotly_chart(fig, width= "stretch", key= "jugadores_plot", on_select="rerun", selection_mode= ('points','box'))


## ANÁLISIS 3.  Impacto Arbitral. Se quiere analizar si existen patrones diferenciados en el criterio arbitral a lo Largo del Mundial. 
# Para ello genere las siguientes visualizaciones utilizando las librerías Ploty y Streamlit:

## 7) Gráfico de cajas que muestre el número de tarjetas por partido 
## Primero de todo leemos los datafrmaes que vamos a usar:
eventos = pd.read_excel("eventos.xlsx")
partidos = pd.read_excel("partidos.xlsx")

## Primero, vamos a crear un nuevo dataframe con el indice de partido, la ronda y el número de tarjets (rojas y amarillas sumadas)
## Para esto, vmaos a necesitar usar la función .merge() con los dataframes eventos y partidos:

dataframe_tarjetas = pd.merge(eventos, partidos[["index_partido", "ronda"]], on="index_partido", how="left") ## usamos left porque nos queremos quedar con todos los eventos

dataframe_tarjetas = dataframe_tarjetas[dataframe_tarjetas["tipo_evento"].isin(["Yellow Card", "Red Card"])]

dataframe_tarjetas= dataframe_tarjetas.groupby(["index_partido","ronda"]).size().to_frame(name= "numero_tarjetas")

dataframe_tarjetas["numero_tarjetas"] = (dataframe_tarjetas["numero_tarjetas"].fillna(0).astype(int)) ## para que aparezcan también los partidos donde no hay ninguna tarjeta 

## Ahora para el gráfico de cajas agrupado por ronda:

fig = px.box(dataframe_tarjetas.reset_index(), x = "ronda", y = "numero_tarjetas",hover_data=["index_partido"],color_discrete_sequence=px.colors.qualitative.Pastel, title="Distribución de tarjetas por ronda del Mundial",) ## reseteamos el index para que existan como solumnas las variables 
fig.show()

##8)
st.subheader("Índice de Intervención Arbitral")

# establecemos los puntos 
PUNTOS = {"Yellow Card":1, "Red Card":3, "VAR Review":1, "Goal":0.2}
eventos_arbitros = eventos.copy()
eventos_arbitros["puntos"] = (eventos_arbitros["tipo_evento"].map(PUNTOS).fillna(0))

# sumamos los puntos por partido
indice_partido = (eventos_arbitros.groupby("index_partido")["puntos"].sum().reset_index(name="indice_arbitral"))
arbitros_partidos = partidos.merge(indice_partido, on="index_partido",how="left")
arbitros_partidos["indice_arbitral"] = (arbitros_partidos["indice_arbitral"].fillna(0))
arbitros_partidos["nombre_partido"] = (arbitros_partidos["seleccion_local"] + " vs " + arbitros_partidos["seleccion_visitante"])

# ronda y seleccion seleccionadas
ronda_seleccionada = st.selectbox("Todas las rondas", ["Todas"] + sorted(arbitros_partidos["ronda"].dropna().unique().tolist()),key="ronda_seleciconada")
selecciones_lista= pd.concat([arbitros_partidos["seleccion_local"], arbitros_partidos["seleccion_visitante"]]).dropna().unique()
seleccion_seleccionada = st.selectbox("Todas las selecciones", ["Todas"] + sorted(selecciones_lista.tolist()),key="seleccion_seleccionada")
datos_arbitros = arbitros_partidos.copy()


# aplicamos filtros
if ronda_seleccionada != "Todas":
    datos_arbitros = datos_arbitros[datos_arbitros["ronda"] == ronda_seleccionada]
if seleccion_seleccionada != "Todas":
    datos_arbitros = datos_arbitros[(datos_arbitros["seleccion_local"] == seleccion_seleccionada)|(datos_arbitros["seleccion_visitante"] == seleccion_seleccionada)]

resumen_arbitros = (datos_arbitros.groupby("arbitro", as_index=False).agg(partidos_arbitrados=("indice_arbitral","count"),media_indice=("indice_arbitral","mean")))
fig = px.bar(resumen_arbitros,x="partidos_arbitrados",y="arbitro",color="media_indice",orientation="h",hover_data=["media_indice"],title="Intervención arbitral por árbitro",labels={"partidos_arbitrados":"Número de partidos arbitrados","arbitro":"Árbitro", "media_indice":"Índice medio"})
st.plotly_chart(fig, width="stretch")








st.subheader("Severidad arbitral por selección")
resultados_selecciones = []
selecciones = sorted(set(arbitros_partidos["seleccion_local"].dropna())| set(arbitros_partidos["seleccion_visitante"].dropna()))
for seleccion in selecciones:
    partidos_seleccion = arbitros_partidos[(arbitros_partidos["seleccion_local"] == seleccion)| (arbitros_partidos["seleccion_visitante"]== seleccion)]

    if not partidos_seleccion.empty:
        partido_menor = partidos_seleccion.loc[partidos_seleccion["indice_arbitral"].idxmin()]
        partido_mayor = partidos_seleccion.loc[partidos_seleccion["indice_arbitral"].idxmax()]
        resultados_selecciones.append({"Selección":seleccion,"Árbitro menos severo": partido_menor["arbitro"],"Partido menor índice":partido_menor["nombre_partido"],"Índice menor":partido_menor["indice_arbitral"],"Árbitro más severo":partido_mayor["arbitro"],"Partido mayor índice":partido_mayor["nombre_partido"],"Índice mayor":partido_mayor["indice_arbitral"]})

tabla_severidad = pd.DataFrame(resultados_selecciones)
st.dataframe(tabla_severidad, use_container_width=True)



st.subheader("Coincidencias entre árbitros")
st.write("Árbitros menos severos")
st.write(tabla_severidad["Árbitro menos severo"].value_counts())
st.write("Árbitros más severos")
st.write(tabla_severidad["Árbitro más severo"].value_counts())



st.write("Observando las tablas anteriores, se confirma que sí que hay coincidencias en los árbitros. El valor de la tabla es la cantidad de veces que aparece cada árbitro como árbitro más severo o menos severo.")
st.write("Por ejemplo, el árbitro Néstor Pitana coincidió en cuatro selecciones como árbitro menos severo")










