#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from itertools import cycle, islice
from pivottablejs import pivot_ui
from Functions import *


# To delate warning messages

pd.options.mode.chained_assignment = None 


# # Ligas para importar

# In[2]:


Leagues = ['Premier League', 'Calcio', 'La Liga', 'Bundesliga', 'Francia']

def All_teams(League):

    dfs = []

    for i in League:
    
        df = get_data_for_league(i)
        dfs.append(df)
    
    return pd.concat(dfs)

df = All_teams(Leagues)


# In[3]:


df


# In[4]:


## Agrego una columna que muestre en que parte de la tabla finalizo el campeonato, donde 1 corresponde a los primeros 6

df['Table Sector'] = df['Position'].apply(lambda x: 1 if  7>x else ( 2 if  15 > x else 3 ))


# ## Cantidad de partidos seguidos sin empatar

# In[36]:


## Hay 236 equipos que tuvieron 0 partidos seguidos sin empatar, es decir, empataron en la primer fecha

df['Sec'].value_counts()


# ## Total de empates por sector de la tabla

# In[5]:


## Vemos que es muy dificil que los equipos de mitad de tabla para abajo empaten menos de 3 partidos por campeonato.

pd.crosstab(df['Table Sector'], df.Draw).transpose()


# ## Secuencia de partidos sin empatar por sector

# In[6]:


# Observamos que la mayor parte de equipos que empatan en la primer fecha son de mitad de tabla

pd.crosstab(df['Table Sector'], df.Sec).transpose()


# In[7]:


## No hay relacion en cuanto a los equipos que no empatan en mas de 7 fechas con su posicion en la tabla

df[df['Sec'] > 7]['Table Sector'].value_counts().plot.bar()


# In[8]:


## Pero si vemos que levemente hay mas equipos de mitad de tabla que empatan antes del cuarto partido

df[df['Sec'] < 4]['Table Sector'].value_counts().plot.bar(color= (0.2,0.4,0.6))


# # Agrego columnas con los flujos de cada semana

# In[9]:


def Weeks(tabla, n):
    for i in range(tabla.shape[0]):
        if tabla.loc[i, 'Sec'] == n-1:
            tabla.loc[i, 'Week_'+str(n)] = tabla.loc[i, 'B365_Draw'] * ( 2 ** (n-1))
        elif tabla.loc[i, 'Sec'] < n-1:
            tabla.loc[i, 'Week_'+str(n)] = 0
        else:
            tabla.loc[i, 'Week_'+str(n)] = -(2 ** (n-1))


# ## Tomo los pagos y los retornos de cada semana

# In[10]:


def Week_Paid(tabla):

    Paid = []

    for i in Week_list:
        paid = -(tabla[tabla[i] != 0][i].count() * (2 ** (int(i.split('_')[1])-1)))
        Paid.append(paid)
    return Paid

def Week_Return(tabla):

    Return = []

    for i in Week_list:
        retur = tabla[tabla[i] > 0][i].sum()
        Return.append(retur)
    return Return


# ## Creo una tabla con los resultados

# In[69]:


def Create_Table(tabla, Start, Teams):

    df_2 = tabla.head(Teams)
    df_2 = df_2.reset_index(drop=True)

    list= range(1,11)
    for i in list:
        Weeks(df_2, i)

    Week = ['Week_1', 'Week_2','Week_3', 'Week_4','Week_5', 'Week_6','Week_7', 'Week_8','Week_9', 'Week_10']  
    Week_list = ['Week_1', 'Week_2','Week_3', 'Week_4','Week_5', 'Week_6','Week_7', 'Week_8','Week_9', 'Week_10']    
    Week = pd.DataFrame(Week)
            

    Se = Week_Paid(df_2)
    Week['Paid'] = Se


    re = Week_Return(df_2)
    Week['Return'] = re


    Week.columns = ['Week', 'Paid', 'Return']

    Week = Week[['Week', 'Paid','Return']]

    Week = Week.round(1)
    Week['Cash'] = 0
    Week['Insert'] = 0
    Week.loc[0, 'Cash'] = int(Start) + Week.loc[0, 'Return'] + Week.loc[0, 'Paid']

    for i in range(1, len(Week.Return)):
        if (Week.loc[i, 'Paid'] + Week.loc[i-1, 'Cash']) > 0:
            Week.loc[i, 'Cash'] = (Week.loc[i, 'Paid'] + Week.loc[i-1, 'Cash']) + Week.loc[i, 'Return']
        elif (Week.loc[i, 'Paid'] + Week.loc[i-1, 'Cash']) < 0:
            Week.loc[i, 'Cash'] = Week.loc[i,'Return']
            Week.loc[i, 'Insert'] = (Week.loc[i, 'Paid'] + Week.loc[i-1, 'Cash'])
    
        
    return Week


# ## Verifico la tabla

# In[74]:


## Primero armo un df con los datos del inicio. 
## Puedo filtrar por alguna de los columnas, en este caso voy a tomar solo la Premier 

df_3 = df[(df.League == 'La Liga') & (df.Year == 19)]
df_3


# In[76]:


## Create_Table tiene tres variables, la primera es la tabla de arriba,
## la segunda corresponde a con cuanto dinero quisiera arrancar
## y la tercera, cuantos equipos al azar quiero de la tabla filtrada

Week_list = ['Week_1', 'Week_2','Week_3', 'Week_4','Week_5', 'Week_6','Week_7', 'Week_8','Week_9', 'Week_10'] 
    
Week = Create_Table(df_3,40, 20)
Week

# Cash muestra el total que tiene la cuenta al finalizar la fecha. Recordar que hay que sumarle nuestra inversion inicial.

# En la primer semana pagamos 20 euros, 1 a cada equipo, y ganamos 18.8, mas los 10 iniciales, la cuenta termina en 8.8

# La columna Insert indica si necesitamos poner mas plata para alcanzar la apuesta de la semana.
# Es decir, en la segunda fecha, como debemos pagar 30 euros para apostar, y tenemos en la cuenta 8.8, debemos agregar 21


# In[66]:





# In[16]:


## Vemos el grafico

Week['Cash'].plot()
Week['Insert'].plot()


# # Cantidad de equipos por liga con mas de 7 partidos sin el primer empate

# In[45]:


MoreThan7 = []

for i in Leagues:
    than = df[(df.League == i) & (df.Year < 15)]['Draw'].value_counts().sum()
    MoreThan7.append(than)
    
MoreThan7 = pd.DataFrame(MoreThan7)
MoreThan7['Team'] = Leagues
MoreThan7.columns = ['More', 'Team']
MoreThan7 = MoreThan7[['Team', 'More']]
MoreThan7 = MoreThan7.set_index('Team')
MoreThan7.plot.bar(figsize=(7,7))


# In[82]:


df[(df['Position'] == 1) & (df['League'] == '') & (df.Year > 17)]['B365_Draw'].mean()


# In[61]:


calcio = df[(df.League == 'Calcio') & (df.Year > 15) & (df.Sec > 6)]
calcio['Table Sector'].value_counts()


# In[51]:


LaLiga18 =Importar_Liga_Año('La Liga', 2018)
LaLiga18[(LaLiga18.HomeTeam == 'Alaves') | (LaLiga18.AwayTeam == 'Alaves') ]


# In[53]:


df.to_csv("C:\\Users\\juano\\Desktop\\Leagues.csv")

