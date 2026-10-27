import pandas as pd
import os
import zipfile
import matplotlib.pyplot as plt
import numpy as np

# 1) Realizamos una exploración inicial de los datos, mostrando la dimension, tipo de datos, numeor de valores nulos por columna y los primeros registros

ruta = "."
archivos = os.listdir(ruta)
print(archivos)
datasets = {}

for archivo in archivos:
    if archivo.endswith(".csv"):
        datasets[archivo] = pd.read_csv(os.path.join(ruta,archivo),sep=None,engine="python")

for nombre, df in datasets.items():
    print("ARCHIVO",nombre)
    print("TAMAÑO",df.shape)
    print("COLUMNAS")
    print(df.columns)
    print("TIPOS DE DATOS:", df.dtypes)
    print("VALORES NULOS:", df.isna().sum())
    print("CABEZERA:", df.head())

# 2) Creamos 3 variables del tipo DataFrame

partidos = pd.DataFrame()
eventos = pd.DataFrame()
jugadores = pd.DataFrame()

# 3) Añadimos a cada DataFrame las columnas que nos piden

#PARTIDOS:

df_mundial_202 = pd.read_csv("matches_mundial202.csv")
df_mundial_202

df_mundial_2026 = pd.read_csv("matches_mundial2026.csv", sep=";")
df_mundial_2026

partidos["fecha_partido"] = pd.concat([df_mundial_202["Date"], df_mundial_2026["date"]], ignore_index=True)
partidos["ronda"] = pd.concat([df_mundial_202["Round"], pd.Series([None]*len(df_mundial_2026))], ignore_index=True)
partidos["estadio"] = pd.concat([df_mundial_202["Venue"], pd.Series([None]*len(df_mundial_2026))], ignore_index=True)
partidos["ciudad_partido"] = partidos["estadio"].str.split(",").str[-1].str.strip()
partidos["pais_partido"] = pd.concat([df_mundial_202["Host"], pd.Series([None]*len(df_mundial_2026))], ignore_index=True)
partidos["seleccion_local"] =  pd.concat([df_mundial_202["home_team"], pd.Series([None]*len(df_mundial_2026))], ignore_index=True)
partidos["seleccion_visitante"] =  pd.concat([df_mundial_202["away_team"], pd.Series([None]*len(df_mundial_2026))], ignore_index=True)
partidos["marcador_local"] =  pd.concat([df_mundial_202["home_score"], df_mundial_2026["home_score"]], ignore_index=True)
partidos["marcador_visitante"] =  pd.concat([df_mundial_202["away_score"], df_mundial_2026["away_score"]], ignore_index=True)
partidos["prorroga"]  = pd.concat([df_mundial_202["Notes"].str.contains("extra time",case=False,na=False).map({True: "SI", False: "NO"}), pd.Series([None]*len(df_mundial_2026))], ignore_index=True)
partidos["penalty_local"] = pd.concat([df_mundial_202["home_penalty"], df_mundial_2026["home_penalty_score"]], ignore_index=True)
partidos["penalty_visitante"] = pd.concat([df_mundial_202["away_penalty"], df_mundial_2026["away_penalty_score"]], ignore_index=True)
partidos["penalty_local"] = partidos["penalty_local"].fillna(0)
partidos["penalty_visitante"] = partidos["penalty_visitante"].fillna(0)
partidos["arbitro"] =  pd.concat([df_mundial_202["Referee"], pd.Series([None]*len(df_mundial_2026))], ignore_index=True)


# JUGADORES:
df_player_stats = pd.read_csv("2026player_stats.csv",sep=";")
df_player_stats

df_squads =  pd.read_csv("2026squads_and_players.csv",sep=";")
df_squads

df_teams = pd.read_csv("2026nationalteams.csv")

jugadores["nombre_jugador"] = df_player_stats["player_name"]
jugadores["team_id"] = df_player_stats["team_id"]
jugadores = pd.merge(jugadores,df_teams[["team_id","team_name"]].drop_duplicates(subset="team_id"), on="team_id",how="left")
jugadores = jugadores.drop(columns=["team_id"])
jugadores = jugadores.rename(columns={"team_name": "seleccion_nacional"})
jugadores["club_jugador"] = df_squads["club_team"]
jugadores["partidos_seleccion"] = df_squads["caps"]
jugadores["posicion"] = df_player_stats["position"]
jugadores["valor_mercado"] = df_squads["market_value_eur"]
jugadores["partidos_jugados"] = df_player_stats["matches_played"]
jugadores["minutos_jugados"] = df_player_stats["minutes_played"]
jugadores["goles"] = df_player_stats["goals"]
jugadores["asistencias"] = df_player_stats["assists"]
jugadores["tiros"] = df_player_stats["shots"]
jugadores["tarjetas_amarillas"] = df_player_stats["yellow_cards"]
jugadores["tarjetas_rojas"] = df_player_stats["red_cards"]
jugadores["paradas"] = df_player_stats["saves"]
jugadores["paradas"] = jugadores["paradas"].fillna(0) ## cambiamos los valores NaN por 0 ya que la mayoria de jugadores no son porteros y pues, no hacen ninguna parada
jugadores["goles_concedidos"] = df_player_stats["goals_conceded"]
jugadores["calificacion_media"] = df_player_stats["average_rating"]

# EVENTOS: 
df_events = pd.read_csv("2026match_register.csv", sep=";")

eventos["minuto_evento"] = df_events["minute"]
eventos["index_partido"] = df_events["match_id"]
eventos["player_id"] = df_events["player_id"]
eventos = pd.merge(eventos, df_player_stats[["player_id","player_name","team_id"]], on="player_id", how="left")
eventos["tipo_evento"] = df_events["event_type"]
eventos = pd.merge(eventos, df_teams[["team_id","team_name"]].drop_duplicates(subset="team_id"), on="team_id", how="left")
eventos = eventos.rename(columns = {"player_name":"nombre_jugador", "team_name":"seleccion_evento"})
eventos = eventos.drop(columns=["player_id", "team_id"])

# 4) Una vez, creados los dataframes que nos piden, vamos a limpiarlos teniendo en cuenta los valores duplicados, nulos y/o anómalos que pudieran contener.

# Vamos a empezar con el dataframe de partidos:
partidos.head()
print(partidos["prorroga"].value_counts(dropna=False)) ## esta variable vemos que ya esta normalizada, no hace falta cambiar nada.
print(partidos["ronda"].value_counts(dropna=False))

#Aquí, para los valores que toman la ronda podemos asumir que hay algunos como 'First group stage' y 'First round' que en verdad se refieren a la misma cosa. Vamos a juntar todos los que pensamos que se refieren a la misma cosa:
mapa = {"First group stage": "Group stage","First round": "Group stage","Second round": "Second group stage"}
partidos["ronda"] = partidos["ronda"].replace(mapa)

# Vamos a acabar normalizando el texto de todos los valores por si acaso:
columnas_texto = ["estadio", "ciudad_partido", "pais_partido", "seleccion_local", "seleccion_visitante", "arbitro"]
for columna in columnas_texto:
    partidos[columna] = partidos[columna].str.strip()


# Vamos a ver que columnas contienen valores nulos:
partidos.info()                 # dtypes, non-null counts
partidos.describe(include="all")# min/max/mean, suspicious values
partidos.isna().sum()           # nulls per column
partidos.duplicated().sum()     # duplicate rows

"""
Aquí por ejemplo vemos que la variable con mayor número de valores nulos es la de arbitro. 
Además tmabién podemos ver que hay muchos registros que les faltan muchos de los valores porque 
muchass variables tiene exactamente 964 valores non nulos. Por ahora no vamos a eliminarlos pero 
dependiendo de caules son las variablaes que faltan (si son importantes o no) y el análisis que queramos 
llevar a cabo, se podrían eliminar.

"""

# Aquí podemos ver los histogramas de las varibales númericas para ver si hay algunos valores sospechosos:
columnas_numericas = ["marcador_local", "marcador_visitante", "penalty_local", "penalty_visitante"]

fig, axes = plt.subplots(2, 2, figsize=(10, 6))
axes = axes.flatten()

for ax, c in zip(axes, columnas_numericas):
    partidos[c].hist(bins=12, ax=ax)
    ax.set_title(c)

plt.tight_layout()
plt.show()


"""
Podemos ver que la mayoria de valores de penalties, tanto local como 
visitante es de cero, que tiene sentido. Lo único que es un poco raro el 
que hay un valor de marcador_local de 10 es poco probable pero seguro 
siguen siendo posible asique no lo vamos a eliminar de el dataframe.
"""
partidos.describe()


# Aquí borramos todos los duplicados ya que sobran siempre:
partidos = partidos.drop_duplicates()
partidos.nunique()

# Ahora para el dataframe de jugadores:
jugadores.head()
print(jugadores["nombre_jugador"].value_counts(dropna=False))

# Aquí ya vemos que el jugador Ali Ahmed tiene dos registros, vamos a ver si es un error:
jugadores[jugadores["nombre_jugador"] == 'Ali Ahmed']

"""
Aquí vemos que son registros completamente diferentes, y haciendo un poco 
de research en el internet hemos visto que existen 2 Ali Ahmeds uno que 
juega para canada y otro para Arabia Saudita. Asi que dejamos los dos ahí. 
"""

# Normalizamos las demás variables categórica porsi acaso:
columnas_texto = ["seleccion_nacional", "club_jugador", "posicion"]
for columna in columnas_texto:
    jugadores[columna] = jugadores[columna].str.strip()

# Como hemos hecho en el dataframe de partidos, vamos a hacer lo mismo aquí(analizamos los nulos):
jugadores.info()                 # dtypes, non-null counts
jugadores.describe(include="all")# min/max/mean, suspicious values
jugadores.isna().sum()           # nulls per column
jugadores.duplicated().sum()     # duplicate rows


"""
Como podemos ver en la tabla de arriba la varible de goles_concedidos tiene 
un número muy abjo de valores existentes y la mayoria son nulos (88% de 
valores nulos), para esto hay una explicación bastante lógica ya que los 
goles concedidos son una estadística que normalmente se utiliza para los 
porteros. Vamos a comprobarlo usando groupby:
"""
jugadores.groupby("posicion")["goles_concedidos"].count()


# Ahora vamos a analizar y limpiar las columnas com variables númericas: 
columnas_numericas = ["valor_mercado","partidos_jugados", "minutos_jugados", "goles", "asistencias", "tiros", "tarjetas_amarillas", "tarjetas_rojas", "paradas","goles_concedidos", "calificacion_media"]
fig, axes = plt.subplots(4, 3, figsize=(20, 16))
axes = axes.flatten()

for ax, c in zip(axes, columnas_numericas):
    jugadores[c].hist(bins=12, ax=ax)
    ax.set_title(c)

plt.tight_layout()
plt.show()

"""
Al ver estos histogramas podemos ver un par de cosas:
1) paradas tiene muchos ceros que tiene sentido ya que es una estadística qie pertence principalmente a porteros entonces no es algo raro.
2) La mayoria de jugadores tienen una calificacion media entre 6 y 8 pero luego hay unos pocos cerca de cero --> valor centinela?
"""

# Vamos a ver primero lo de califiacaion_media
jugadores["calificacion_media"].value_counts(dropna=False).sort_index()
jugadores[jugadores["calificacion_media"] < 5][["nombre_jugador", "partidos_jugados","minutos_jugados", "calificacion_media"]]


"""
Aquí vemos claramente que los valores que tiene una calificaion media de 
cero es porque han jugado muy poco , como mucho 2 minutos en total. Por 
esto podemos asumir que el valor 0 se usa para representar la ausencia de una calificaión en 
lugar de una valoración real de como juago ese jugador. Podemos identificarlos como posibles valores centinela y
reemplazar las calificaiones por NaN:
"""

jugadores["calificacion_media"] = jugadores["calificacion_media"].replace(0, np.nan)
jugadores.describe()

# Eliminamos duplicados si hay:
partidos = partidos.drop_duplicates()
# Por ultimo vamos a ver el dataframe de eventos: Aquí hemos realizado el apartado 5 también.
eventos.head()
eventos.describe()

"""
Con las estadísticas mostradas arriba, ya de primeras podemos ver cosas raras. 
Por ejemplo el mínimo de el minuto es -45 que debe ser un error ya que no se puede tener un 
tiempo negativo. Vamos a verlo más de cerca:
"""
eventos[eventos["minuto_evento"] < 0]
eventos["minuto_evento"].value_counts(dropna=False).sort_index()


"""
Aquí además vemos que hay valores que son altamente grandes, por ejemplo 999. 
El tiempo normal de un partido podriamos ponerlo como 130 minutos, vamos a ver 
cuantos valores hay mayor que ese:  
"""
eventos[eventos["minuto_evento"] > 130]

"""
Como hay valores para la varibale de minuto_evento que incumplen las reglas de 
dominio, aunque podriían ser error de introduccioón de signo, no tenemos suficiente 
información para determinar cual sería el valor correcto. Entonces hemos deicidido 
reemplazarlos por valores NaN:
"""
eventos.loc[eventos["minuto_evento"] < 0, "minuto_evento"] = np.nan
eventos.loc[eventos["minuto_evento"] > 130, "minuto_evento"] = np.nan

# Vamos a investigar los valores ausentes para la variable nombre_jugador:
eventos["nombre_jugador"].value_counts(dropna=False).sort_index()
eventos[eventos["nombre_jugador"].isna()]

"""
podemos ver que estos registros estan casi vacios ya que solo tienen una variable 
con valor significativo. Vamos a eliminarlas (solo las que tengan los cuatro valores 
ausentes): 
"""
eventos = eventos.dropna(subset=["minuto_evento","index_partido","nombre_jugador","tipo_evento"],how="all")
eventos["tipo_evento"].value_counts(dropna=False).sort_index()

"""
Aquí vemos que hay algunas variable que significan lo mismo, por ejmplo VAR 
Review y Review VAR son lo mismo. Las unificamos:
"""
eventos["tipo_evento"] = eventos["tipo_evento"].replace("Review VAR", "VAR Review")
eventos["seleccion_evento"].value_counts(dropna=False).sort_index()

# No se ve nada raro aquí asi que lo dejamos como estaba. 

# 6) reconstruir una 'fecha_partido' usando expresiones regulares en el dataframe partidos
partidos["fecha_partido"].str.match(r"^\d{4}-\d{2}-\d{2}$")

#Primero, vamos a crear una función que identifique el formato de la fecha:
import re

def identificar_formato(fecha):
    fecha = str(fecha)

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
        return "AAAA-MM-DD"

    elif re.fullmatch(r"\d{2}-\d{2}-\d{4}", fecha):
        return "MM-DD-AAAA"
    
    elif re.fullmatch(r"\d{1,2} [A-Za-z]+ \d{4}",fecha):
        return "DD Mes AAAA"
    
    elif re.fullmatch(r"^\d{2}/\d{2}/\d{4}$", fecha):
        return "DD/MM/AAAA"

    elif re.fullmatch(r"[A-Za-z]+ \d{1,2}, \d{4}", fecha):
        return "Mes DD, AAAA"

    elif re.fullmatch(r"\d{1,2}-[A-Za-z]{3}-\d{2}", fecha):
        return "DD-Mes-AA"

    elif re.fullmatch(r"[A-Za-z]+ \d{1,2} \d{4}", fecha):
        return "Mes DD AAAA"

    elif re.fullmatch(r"\d{8}", fecha):
        return "AAAAMMDD"

    elif re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", fecha):
        return "DD.MM.AAAA"


    elif re.fullmatch(r"\d{1,2} de [a-zA-Z]+ de \d{4}", fecha):
            return "DD de Mes de AAAA"

    elif re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*", fecha):
        return "fecha con hora"
    else: 
        return "Otro"

#Una vez creada la función, vamos a crear una nueva columna en el dataframe que contenga el formato de la fecha de cada fecha:
partidos["formato_fecha"] = partidos["fecha_partido"].apply(identificar_formato)

#Y para contar cuantos registros hay por formato: 
partidos["formato_fecha"].value_counts()

meses = {
    "january": "01", "jan": "01", "enero": "01", "ene": "01",
    "february": "02", "feb": "02", "febrero": "02",
    "march": "03", "mar": "03", "marzo": "03",
    "april": "04", "apr": "04", "abril": "04", "abr": "04",
    "may": "05", "mayo": "05",
    "june": "06", "jun": "06", "junio": "06",
    "july": "07", "jul": "07", "julio": "07",
    "august": "08", "aug": "08", "agosto": "08", "ago": "08",
    "september": "09", "sep": "09", "sept": "09", "septiembre": "09",
    "october": "10", "oct": "10", "octubre": "10",
    "november": "11", "nov": "11", "noviembre": "11",
    "december": "12", "dec": "12", "diciembre": "12", "dic": "12"
}

#Ahora vamos a crear una función que, dependiendo del formato de la fecha,la recontruya para que sean todas iguales:
def convertir_fecha(fecha):
    fecha = str(fecha).strip()
    formato = identificar_formato(fecha)

    if formato in ["AAAA-MM-DD", "fecha con hora"]:
        partes = fecha[:10].split("-")
        ano, mes, dia = partes

    elif formato == "MM-DD-AAAA":
        partes = fecha.split("-")
        mes, dia, ano = partes

    elif formato == "DD Mes AAAA":
        partes = fecha.split()
        dia, mes, ano = partes
        mes = meses[mes.lower()]

    elif formato == "DD/MM/AAAA":
        partes = fecha.split("/")
        dia, mes, ano = partes

    elif formato == "Mes DD, AAAA":
        partes = fecha.replace(",", "").split()
        mes, dia, ano = partes 
        mes = meses[mes.lower()]

    elif formato == "DD-Mes-AA":
        partes = fecha.split("-")
        dia = partes[0]
        mes = partes[1]
        ano = "20" + partes[2]
        mes = meses[mes.lower()]

    elif formato == "Mes DD AAAA":
        partes = fecha.split()
        mes, dia, ano = partes
        mes = meses[mes.lower()]

    elif formato == "AAAAMMDD":
        ano = fecha[:4]
        mes = fecha[4:6]
        dia = fecha[6:]

    elif formato == "DD.MM.AAAA":
        partes = fecha.split(".")
        dia, mes, ano = partes

    elif formato == "DD de Mes de AAAA":
        partes = fecha.split(" de ")
        dia, mes, ano = partes
        mes = meses[mes.lower()]

    resultado = f"{int(dia)}/{int(mes)}/{int(ano)}"
    return resultado

partidos["fecha_original"] = partidos["fecha_partido"]
partidos["fecha_partido"] = partidos["fecha_partido"].apply(convertir_fecha)

#7) Imputación de valores faltantes

#Valor_mercado: complete los datos faltantes utilizando Imputación por la Media de todos los jugadores de la misma Selección del jugador a imputar
jugadores["valor_mercado"].isna().value_counts()
#Aquí vemos que hay 90 valores faltantes.
jugadores["is_valor_nan"] = jugadores["valor_mercado"].isna() # nos creamos una columna que nos dice si los valores son nulos o no
jugadores.groupby(["seleccion_nacional"])["is_valor_nan"].value_counts() # clasificamos los nulos por el sector de ocupación
jugadores["valor_mercado"] = jugadores["valor_mercado"].fillna(jugadores.groupby("seleccion_nacional")["valor_mercado"].transform("mean"))

#Calificacion_media: complete los datos faltantes con Imputación por Regresión basada en la correlación con las estadísticas de goles, asistencias, tarjetas amarillas y rojas, paradas o goles concedidos (Consejo: distinga el caso de porteros y otras posiciones
#La primera imputación por regresión la vamos a hacer basada en la correlación con las estadisticas de goles (vamos a usar solo los jugadores que no sean porteros, ya que estos interferian con la imputación porque tendrian valores para esta variable muy baja aunque puedan tener calificaciones altas)

jugadores_campo = jugadores[jugadores["posicion"] != "GK"]
jugadores_campo.plot("calificacion_media", "goles", kind="scatter")

from sklearn.linear_model import LinearRegression

jugadores_imputacion_goles = jugadores_campo.copy()

# Eliminamos las filas que no tienen m2. La regresión necesita ejemplos completos para aprender
train = jugadores_imputacion_goles.dropna(subset=["goles", "calificacion_media"])

# Entrenamos el modelo. El modelo aprende la relación entre habitaciones y metros cuadrados.
# .fit(X, y) x- variable explicativa, n_rooms; y - variable objetivo - m2

model = LinearRegression().fit(
    train[["goles"]],
    train["calificacion_media"])

mask = jugadores_imputacion_goles["calificacion_media"].isna()

# Filtramos los valores faltantes y predecimos sus valores a partir del modelo
mask_pred = mask & jugadores_imputacion_goles["goles"].notna()

jugadores_imputacion_goles.loc[mask_pred, "calificacion_media"] = model.predict(
    jugadores_imputacion_goles.loc[mask_pred, ["goles"]]
)

# Marcamos que datos fueron imputados
jugadores_imputacion_goles["imputed"] = mask

def fit_linear_regression(df: pd.DataFrame,    x_col: str,    y_col: str) -> LinearRegression:

    df_non_nan = df.dropna(subset=[y_col])
    model = LinearRegression().fit(
        df_non_nan[[x_col]], 
        df_non_nan[y_col])
    return model

def predict_linear_regression(    df: pd.DataFrame,    x_col: str,    model: LinearRegression) -> pd.Series:
    return model.predict(df[[x_col]])

# Representamos el gráfico utilizando la columna imputed para el color
fig, ax = plt.subplots()
plt.scatter(jugadores_imputacion_goles["calificacion_media"], jugadores_imputacion_goles["goles"], c=jugadores_imputacion_goles["imputed"])

ax.set_xlabel("calificacion_media")
ax.set_ylabel("goles")

#Ahora repetimos la imputacion pero con asistencias (seguiremos usando el datafrmae que solo contiene los jugadores):

jugadores_campo.plot("calificacion_media", "asistencias", kind="scatter")
jugadores_imputacion_asistencias = jugadores_campo.copy()

# Eliminamos las filas que no tienen m2. La regresión necesita ejemplos completos para aprender
train = jugadores_imputacion_asistencias.dropna(subset=["asistencias", "calificacion_media"])

# Entrenamos el modelo. El modelo aprende la relación entre habitaciones y metros cuadrados.
# .fit(X, y) x- variable explicativa, n_rooms; y - variable objetivo - m2

model = LinearRegression().fit(
    train[["asistencias"]],
    train["calificacion_media"])

mask = jugadores_imputacion_asistencias["calificacion_media"].isna()

# Filtramos los valores faltantes y predecimos sus valores a partir del modelo
mask_pred = mask & jugadores_imputacion_asistencias["asistencias"].notna()

jugadores_imputacion_asistencias.loc[mask_pred, "calificacion_media"] = model.predict(
    jugadores_imputacion_asistencias.loc[mask_pred, ["asistencias"]]
)

# Marcamos que datos fueron imputados
jugadores_imputacion_asistencias["imputed"] = mask

def fit_linear_regression(df: pd.DataFrame,    x_col: str,    y_col: str) -> LinearRegression:

    df_non_nan = df.dropna(subset=[y_col])
    model = LinearRegression().fit(
        df_non_nan[[x_col]], 
        df_non_nan[y_col])
    return model

def predict_linear_regression(    df: pd.DataFrame,    x_col: str,    model: LinearRegression) -> pd.Series:
    return model.predict(df[[x_col]])

# Representamos el gráfico utilizando la columna imputed para el color
fig, ax = plt.subplots()
plt.scatter(jugadores_imputacion_asistencias["calificacion_media"], jugadores_imputacion_asistencias["asistencias"], c=jugadores_imputacion_asistencias["imputed"])

ax.set_xlabel("calificacion_media")

ax.set_ylabel("asistencias")

#Para las variables de tarjetas amarillas y rojas podemos usar todos los jugadores:
jugadores.plot("calificacion_media", "tarjetas_amarillas", kind="scatter")
jugadores_imputacion_amarillas = jugadores.copy()

# Eliminamos las filas que no tienen m2. La regresión necesita ejemplos completos para aprender
train = jugadores_imputacion_amarillas.dropna(subset=["tarjetas_amarillas", "calificacion_media"])

# Entrenamos el modelo. El modelo aprende la relación entre habitaciones y metros cuadrados.
# .fit(X, y) x- variable explicativa, n_rooms; y - variable objetivo - m2

model = LinearRegression().fit(
    train[["tarjetas_amarillas"]],
    train["calificacion_media"])

mask = jugadores_imputacion_amarillas["calificacion_media"].isna()

# Filtramos los valores faltantes y predecimos sus valores a partir del modelo
mask_pred = mask & jugadores_imputacion_amarillas["tarjetas_amarillas"].notna()

jugadores_imputacion_amarillas.loc[mask_pred, "calificacion_media"] = model.predict(
    jugadores_imputacion_amarillas.loc[mask_pred, ["tarjetas_amarillas"]]
)

# Marcamos que datos fueron imputados
jugadores_imputacion_amarillas["imputed"] = mask

def fit_linear_regression(df: pd.DataFrame,    x_col: str,    y_col: str) -> LinearRegression:

    df_non_nan = df.dropna(subset=[y_col])
    model = LinearRegression().fit(
        df_non_nan[[x_col]], 
        df_non_nan[y_col])
    return model

def predict_linear_regression(    df: pd.DataFrame,    x_col: str,    model: LinearRegression) -> pd.Series:
    return model.predict(df[[x_col]])

# Representamos el gráfico utilizando la columna imputed para el color
fig, ax = plt.subplots()
plt.scatter(jugadores_imputacion_amarillas["calificacion_media"], jugadores_imputacion_amarillas["tarjetas_amarillas"], c=jugadores_imputacion_amarillas["imputed"])

ax.set_xlabel("calificacion_media")

ax.set_ylabel("tarjetas_amarillas")

jugadores.plot("calificacion_media", "tarjetas_rojas", kind="scatter")

jugadores_imputacion_rojas = jugadores.copy()

# Eliminamos las filas que no tienen m2. La regresión necesita ejemplos completos para aprender
train = jugadores_imputacion_rojas.dropna(subset=["tarjetas_rojas", "calificacion_media"])

# Entrenamos el modelo. El modelo aprende la relación entre habitaciones y metros cuadrados.
# .fit(X, y) x- variable explicativa, n_rooms; y - variable objetivo - m2

model = LinearRegression().fit(
    train[["tarjetas_rojas"]],
    train["calificacion_media"])

mask = jugadores_imputacion_rojas["calificacion_media"].isna()

# Filtramos los valores faltantes y predecimos sus valores a partir del modelo
mask_pred = mask & jugadores_imputacion_rojas["tarjetas_rojas"].notna()

jugadores_imputacion_rojas.loc[mask_pred, "calificacion_media"] = model.predict(
    jugadores_imputacion_rojas.loc[mask_pred, ["tarjetas_rojas"]]
)

# Marcamos que datos fueron imputados
jugadores_imputacion_rojas["imputed"] = mask

def fit_linear_regression(df: pd.DataFrame,    x_col: str,    y_col: str) -> LinearRegression:

    df_non_nan = df.dropna(subset=[y_col])
    model = LinearRegression().fit(
        df_non_nan[[x_col]], 
        df_non_nan[y_col])
    return model

def predict_linear_regression(    df: pd.DataFrame,    x_col: str,    model: LinearRegression) -> pd.Series:
    return model.predict(df[[x_col]])

# Representamos el gráfico utilizando la columna imputed para el color
fig, ax = plt.subplots()
plt.scatter(jugadores_imputacion_rojas["calificacion_media"], jugadores_imputacion_rojas["tarjetas_rojas"], c=jugadores_imputacion_rojas["imputed"])

ax.set_xlabel("calificacion_media")

ax.set_ylabel("tarjetas_rojas")

#Para la ultima variable usamos solo los porteros: 

jugadores_porteros = jugadores[jugadores["posicion"] == "GK"]
jugadores_porteros.plot("calificacion_media", "goles_concedidos", kind="scatter")

jugadores_imputacion_goles_concedidos = jugadores_porteros.copy()

# Eliminamos las filas que no tienen m2. La regresión necesita ejemplos completos para aprender
train = jugadores_imputacion_goles_concedidos.dropna(subset=["goles_concedidos", "calificacion_media"])

# Entrenamos el modelo. El modelo aprende la relación entre habitaciones y metros cuadrados.
# .fit(X, y) x- variable explicativa, n_rooms; y - variable objetivo - m2

model = LinearRegression().fit(
    train[["goles_concedidos"]],
    train["calificacion_media"])

mask = jugadores_imputacion_goles_concedidos["calificacion_media"].isna()

# Filtramos los valores faltantes y predecimos sus valores a partir del modelo
mask_pred = mask & jugadores_imputacion_goles_concedidos["goles_concedidos"].notna()

jugadores_imputacion_goles_concedidos.loc[mask_pred, "calificacion_media"] = model.predict(
    jugadores_imputacion_goles_concedidos.loc[mask_pred, ["goles_concedidos"]]
)

# Marcamos que datos fueron imputados
jugadores_imputacion_goles_concedidos["imputed"] = mask

def fit_linear_regression(df: pd.DataFrame,    x_col: str,    y_col: str) -> LinearRegression:

    df_non_nan = df.dropna(subset=[y_col])
    model = LinearRegression().fit(
        df_non_nan[[x_col]], 
        df_non_nan[y_col])
    return model

def predict_linear_regression(    df: pd.DataFrame,    x_col: str,    model: LinearRegression) -> pd.Series:
    return model.predict(df[[x_col]])

# Representamos el gráfico utilizando la columna imputed para el color
fig, ax = plt.subplots()
plt.scatter(jugadores_imputacion_goles_concedidos["calificacion_media"], jugadores_imputacion_goles_concedidos["goles_concedidos"], c=jugadores_imputacion_goles_concedidos["imputed"])

ax.set_xlabel("calificacion_media")

ax.set_ylabel("goles_concedidos")

jugadores_porteros.plot("calificacion_media", "paradas", kind="scatter")

jugadores_imputacion_paradas = jugadores_porteros.copy()

# Eliminamos las filas que no tienen m2. La regresión necesita ejemplos completos para aprender
train = jugadores_imputacion_paradas.dropna(subset=["paradas", "calificacion_media"])

# Entrenamos el modelo. El modelo aprende la relación entre habitaciones y metros cuadrados.
# .fit(X, y) x- variable explicativa, n_rooms; y - variable objetivo - m2

model = LinearRegression().fit(
    train[["paradas"]],
    train["calificacion_media"])

mask = jugadores_imputacion_paradas["calificacion_media"].isna()

# Filtramos los valores faltantes y predecimos sus valores a partir del modelo
mask_pred = mask & jugadores_imputacion_paradas["paradas"].notna()

jugadores_imputacion_paradas.loc[mask_pred, "calificacion_media"] = model.predict(
    jugadores_imputacion_paradas.loc[mask_pred, ["paradas"]]
)

# Marcamos que datos fueron imputados
jugadores_imputacion_paradas["imputed"] = mask

def fit_linear_regression(df: pd.DataFrame,    x_col: str,    y_col: str) -> LinearRegression:

    df_non_nan = df.dropna(subset=[y_col])
    model = LinearRegression().fit(
        df_non_nan[[x_col]], 
        df_non_nan[y_col])
    return model

def predict_linear_regression(    df: pd.DataFrame,    x_col: str,    model: LinearRegression) -> pd.Series:
    return model.predict(df[[x_col]])

# Representamos el gráfico utilizando la columna imputed para el color
fig, ax = plt.subplots()
plt.scatter(jugadores_imputacion_paradas["calificacion_media"], jugadores_imputacion_paradas["paradas"], c=jugadores_imputacion_paradas["imputed"])

ax.set_xlabel("calificacion_media")

ax.set_ylabel("paradas")

#Minuto_evento: complete los datos faltantes utilizando Imputación por Interpolación considerando los eventos previos y posteriores del mismo partido
#Como nos pide hacer la imputación por interpolación considernado los eventos previos y posteriores (es decir, ambos), usaremos interpolación local.

eventos["minuto_evento"] = (eventos["minuto_evento"].interpolate("linear")) # La interpolación lineal calcula los valores faltantes siguiendo una línea recta entre los puntos vecinos.)

#8) Ahora solo falta exportar los tres dataframes a excel. Para ello vamos a usar una funcion de pandas:
jugadores.to_excel("jugadores.xlsx", index=False)
partidos.to_excel("partidos.xlsx", index=False)
eventos.to_excel("eventos.xlsx", index=False)

















# BLOQUE 2
# ANÁLISIS 1
import plotly as px
import streamlit as st

# GRÁFICO DE BARRAS
# crear el df partidos para el gráfico
partidos_grafico = partidos.copy().reset_index()
partidos_grafico["partido"] = (partidos_grafico["seleccion_local"].astype(str)+"-"+partidos_grafico["seleccion_visitante"].astype(str))

# crear el df eventos para el gráfico
eventos_grafico = eventos.copy()

# relacionar los eventos con sus partidos
partidos_grafico["index_partido"] = pd.to_numeric(partidos_grafico["index_partido"],errors="coerce")
eventos_grafico["index_partido"] = pd.to_numeric(eventos_grafico["index_partido"],errors="coerce")

eventos_grafico = eventos_grafico.merge(partidos_grafico[["index_partido","partido"]],on="index_partido",how="left")

eventos_grafico

# lista de partidos
lista_partidos = eventos_grafico["partido"].dropna().unique()
partido_elegido = st.selectbox("Selecciona un partido:", lista_partidos.tolist())

# Filtrar eventos 
datos = eventos_grafico[eventos_grafico["partido"] == partido_elegido].copy()

fig = px.scatter(datos,x="minuto_evento",y="tipo_evento",color="tipo_evento",hover_name="nombre_jugador",hover_data={"minuto_evento":True,"tipo_evento":True,"nombre_jugador":True,"seleccion_evento":True},labels={"minuto_evento":"Minuto del partido","tipo_evento":"Tipo de evento","nombre_jugador":"Jugador","seleccion_evento":"Seleccion"}, title=f"Eventos del partido: {partido_elegido}")
fig.update_layout(xaxis_title="Minuto del partido",yaxis_title="Tipo de evento",legend_title="Tipo de evento",height=550)
fig.update_xaxes(range=[0,max(95,datos["minuto_evento"].max()+5)],dtick=15)
st.plotly_chart(fig,use_container_width=True)
with st.expander("Ver tabla de eventos"):
    st.dataframe(datos[["minuto_evento","tipo_evento","nombre_jugador","seleccion_evento"]].sort_values("minuto_evento"),hide_index=True,use_container_width=True)


# MAPA DE CALOR
tipos_evento = sorted(eventos_grafico["tipo_evento"].unique())
tipos_elegidos = st.multiselect("Selecicona los tipos de evento: ",tipos_evento,default=tipos_evento)
rondas = sorted(eventos_grafico["ronda"].unique)
rondas_elegidas = st.multiselect("Selecciona las rondas",rondas,default=rondas)

# aplicar filtros
datos_mapa = eventos_grafico[eventos_grafico["tipo_evento"].isin(tipos_elegidos) & eventos_grafico["ronda"].isin(rondas_elegidas)].copy()