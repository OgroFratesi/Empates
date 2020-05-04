import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from itertools import cycle, islice
from tqdm.notebook import tqdm

pd.options.mode.chained_assignment = None 

def Importar_Liga_Año(liga,año):

    year = str(año)
    
    path = r'C:\Users\juano\Desktop\Excels - Football Data\\'
    prin = (path + liga + ' - ' +  year  + '.csv')


    liga = pd.read_csv(prin, sep= ';')
    

    return  liga

def Dictionary(Liga):

 ## Create a list with all the Team Names of the league
    
    Team_list = Liga.HomeTeam
    Team_list = list(Team_list.unique())
   
 ## A dictionary so we can insert all the team tables 
    
    Team_Dic = {}
    
    col = ['Date', 'HomeTeam', 'AwayTeam', 'FTR', 'Draw', 'Sec', 'B365D']
        
 ## We add to de Dictionary the tables which the matches of all individual teams

    for i in Team_list:
        Team_Dic[i] = Liga[(Liga['HomeTeam'] == i)|(Liga['AwayTeam'] == i)]
  
 ## Reset the index for all the tables

    for key, item in Team_Dic.items():
        item= item.reset_index(drop=True)
        Team_Dic[key]=item
  
 ## Append a new column named DRAW, where 1 is Draw and 0 Not Draw

    for key, item in Team_Dic.items():
        item['Draw'] = item['FTR'].apply(lambda x: 1 if x =='D' else 0)
        item['Sec'] = 0
        Team_Dic[key]= item[col]
  
 ## Insert a columns with the points per game
    
    for key, item in Team_Dic.items():
        item['Points'] = 0
    
    for key, item in Team_Dic.items():
        for i in range(item['HomeTeam'].shape[0]):
            if item['HomeTeam'][i] == key:
                if item['FTR'][i] == 'H':
                    item['Points'][i] = 3
                elif item['FTR'][i] == 'D':
                    item['Points'][i] = 1
            elif item['AwayTeam'][i] == key:
                if item['FTR'][i] == 'A':
                    item['Points'][i] = 3
                elif item['FTR'][i] == 'D':
                    item['Points'][i] = 1
            else:
                item['Points'][i] = 0
        
     
 
 ## Now append another column with the number of consecutive matches without Draw

    for key, item in Team_Dic.items():
        for i in range(1, (len(Team_list)-1)*2):
            if item.loc[0, 'Draw'] == 0:
                item.loc[0, 'Sec'] = 1
            if item.loc[i, 'Draw'] == 0:
                item.loc[i, 'Sec'] = item.loc[i-1, 'Sec'] + 1
            else:
                item.loc[i, 'Sec'] = 0

    return Team_Dic

def Secuencia(Dictionary, Liga):
    
    #      Append a new column to all tables with 0 value
        
    
    for key, item in Dictionary.items():
        item['First'] = 0
        
    #     Loop for create a sequence of numbers until the first Draw

    
    rows = 38
    
    i = 0
    
    for key, item in Dictionary.items():
        for i in range(38):
            i = 0
            while i < rows and item.loc[i,'Sec'] != 0:
                item.loc[i, 'First'] = item.loc[i, 'Sec']
                i += 1
                
      
   #    Create a DataFrame with the total matches before a draw for all teams.
    
 
    First = []
    Points = []
    Draw = []
    B365_Draw = []
    
    Team_list = Liga.HomeTeam
    Team_list = list(Team_list.unique())    
    
    for key, item in Dictionary.items():
        First.append(item['First'].max())
        
    
    for key, item in Dictionary.items():
        Points.append(item['Points'].sum())
        
    for key, item in Dictionary.items():
        Draw.append(item['Draw'].sum())
        
    for key, item in Dictionary.items():
        if 'B365D' in item:
            B365_Draw.append(item['B365D'].mean())
        else:
            B365_Draw.append(3)
    
    Sequence = pd.DataFrame(First)
    Sequence['Team_list'] = Team_list
    Sequence.columns = ['Sec', 'Team']
    Sequence = Sequence[['Team', 'Sec']]
    Sequence['Points'] = Points
    Sequence['Draw'] = Draw
    Sequence['B365_Draw'] = B365_Draw
    
    
    return Sequence
  
def Ag_Liga_Año(tabla, liga, año):
    tabla['Year'] = año
    tabla['League'] = liga
    tabla['Position'] = tabla['Points'].rank(ascending= False)
    tabla['Position'] = tabla['Position'].apply(lambda x: int(x))
    tabla = tabla[['Team', 'League', 'Year', 'Sec','Draw','Position', 'Points', 'B365_Draw']]
    
    ## Also insert a column with the positions
    

    
    return tabla

def get_data_for_league(league):
    dfs = []
    for year in tqdm(range(2010,2020),leave=False):
        df = Importar_Liga_Año(league,year)
        dic = Dictionary(df)
        sec = Secuencia(dic, df)
        sec = Ag_Liga_Año(sec, '%s' % (league), year - 2000)
        dfs.append(sec)
    return pd.concat(dfs)



def All_teams(League):

    dfs = []

    for i in League:
    
        df = get_data_for_league(i)
        dfs.append(df)
    
    return pd.concat(dfs)