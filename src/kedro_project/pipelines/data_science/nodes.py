import logging
from typing import Dict, Tuple
from git import List
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score, roc_curve, precision_score, recall_score
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import re
from sklearn.preprocessing import LabelEncoder






logger = logging.getLogger(__name__)

def _saca_enfermedades (vector,df_Enfermedades):
    
    enfermedades=[]
    for j in vector:
        enfermedades.append(df_Enfermedades[df_Enfermedades["index"]==j]["Enfermedad"])
        
    return enfermedades

def _aparece_y_como (scoring_enfermedades,id_Sintoma, df_Enfermedades, df_Sintomas,df_EnfeySinto_select):
    

    
    j=0
    enfermedades=[]
    while (j<len(scoring_enfermedades)):
        enfermedad=[]
        id_enfermedad=scoring_enfermedades["index"][j]
        scoring=scoring_enfermedades[id_Sintoma][j]
        
        enfermedad.append(id_enfermedad)
       
        enfermedad.append(df_Enfermedades[df_Enfermedades["index"]==id_enfermedad]["Enfermedad"].values[0])
   
        enfermedad.append(scoring)
        lista=df_EnfeySinto_select[df_EnfeySinto_select["Enfermedad"]==
                                   df_Enfermedades.loc[id_enfermedad][1]]
        lista=lista.reset_index()
        sintoma= df_Sintomas.loc[id_Sintoma].Sintoma
        
        i=0
        while i<len(lista):
         
            if lista["Sintoma"][i]==sintoma:
                enfermedad.append(lista["Frecuencia"][i])
            
            i=i+1  
        j=j+1
        enfermedades.append(enfermedad)
        df_enfermedades=pd.DataFrame(enfermedades)
        
    return df_enfermedades

def _aparece_y_como2 (enfermedades, df_Enfermedades, df_Sintomas,df_EnfeySinto_select):
    

    
    j=0
    lista_todo=[]
    df_enfermedades=pd.DataFrame()
    while (j<len(enfermedades)):
        enfermedad=[]
        id_enfermedad=enfermedades[j]
        #scoring=scoring_enfermedades[id_Sintoma][j]
        
        enfermedad.append(id_enfermedad)
       
        enfermedad.append(df_Enfermedades[df_Enfermedades["index"]==id_enfermedad]["Enfermedad"].values[0])
   
       # enfermedad.append(scoring)
        #lista=df_EnfeySinto_select[df_EnfeySinto_select["Enfermedad"]==
         #                          df_Enfermedades.loc[id_enfermedad][1]]
        #lista=lista.reset_index()
        #sintoma= df_Sintomas.loc[id_Sintoma].Sintoma
        
        #i=0
        #while i<len(lista):
         
         #   if lista["Sintoma"][i]==sintoma:
          #      enfermedad.append(lista["Frecuencia"][i])
            
           # i=i+1  
        #j=j+1
        lista_todo.append(enfermedad)
        j=j+1
    lista_todo=pd.DataFrame(lista_todo)
        
    return lista_todo
def trata_sintomas2 (parameters: list,df_transpuesta,df_enfermedades,df_sintomas,df_todo):
    comunes=[]
    logger.info(f'Param={parameters}')
    logger.info(f'sintomas?={parameters["sintomas"]}')
    sintomas=parameters["sintomas"]
    logger.info(f'Sintomas={sintomas}')
    primera_iter=True
    df_matrix=df_transpuesta
    lista=[]
    for i in sintomas:
        diccionario={
            "sintoma" : i,
            "clasificados" : 100
        }
        vector=[]
        #lista,vector=predict_similitud_entre_usuarios_by_pearson(df_transpuesta,i,20)
        v=predict_collaborative_filtering_ser_based(df_matrix, diccionario,df_sintomas,df_enfermedades,df_todo)
        logger.info(f'esto?={v}')
 #resul=nodes.predict_collaborative_filtering_ser_based (df_matrix,diccionario,df_sintomas,df_enfermedades,df_todo)
    
        
        enfermedades=v[0]
        enfermedades=list(enfermedades)
        logger.info(f'enfermedades?={enfermedades}')
      
        if primera_iter:
            comunes=enfermedades
            primera_iter=False

        else:            
            comunes = set(comunes).intersection(enfermedades)
        
        
    #enfermedades=_saca_enfermedades(comunes,df_enfermedades)
    enfermedades=_aparece_y_como2 (list(comunes), df_enfermedades, df_sintomas,df_todo)
    #logger.info(f'enfermeada?={enfermedades}')
   # print (enfermedades)
   # enfermedades=pd.DataFrame(enfermedades)
    return enfermedades

def predict_collaborative_filtering_ser_based(data_matrix: pd.DataFrame, parameters: Dict, 
                                              csv_sintomas: pd.DataFrame, csv_enfermedades: pd.DataFrame, 
                                              clean_and_processed_enfermedades: pd.DataFrame):
  
    sintoma=parameters["sintoma"]
    elementos=parameters["clasificados"]
    df_Sintomas=csv_sintomas
    df_EnfeySinto_select=clean_and_processed_enfermedades
    df_Enfermedades=csv_enfermedades
    ratings=data_matrix.values
    id_sintoma = df_Sintomas[df_Sintomas['Sintoma'] == sintoma].index.values[0]

    ratings_train, ratings_test = train_test_split(ratings, test_size = 0.2, shuffle=False, random_state=42)
    #print (ratings_train.shape)
    #print (ratings_test.shape)
    sim_matrix = 1 - sklearn.metrics.pairwise.cosine_distances(ratings)
    
    #Matriz de similitud entre los usuarios (distancia del coseno -vectores-).
    #Predecir la valoración desconocida de un ítem i para un usuario activo u basandonos en la suma ponderada de
    #todas las valoraciones del resto de usuarios para dicho ítem.
    #Recomendaremos los nuevos ítems a los usuarios según lo establecido en los pasos anteriores.
    #separar las filas y columnas de train y test
    sim_matrix_train = sim_matrix[0:386,0:386]
    sim_matrix_test = sim_matrix[386:483,386:483]
    
    #users_predictions = sim_matrix_train.dot(ratings_train) / np.array([np.abs(sim_matrix_train).sum(axis=1)]).T
    users_predictions = sim_matrix.dot(ratings) / np.array([np.abs(sim_matrix).sum(axis=1)]).T

    
    
    #Predicciones (las recomendaciones!)
    
    user0=users_predictions.argsort()[id_sintoma]
    vector_id_enfermedad_scoring=[]
    for i, aRepo in enumerate(user0[-elementos:]):
        v=[]
        selRepo = df_Enfermedades[df_Enfermedades["index"]==aRepo]
  
       # print('Enfermedad:', selRepo["Enfermedad"] , 'scoring:', users_predictions[sintoma_ver][aRepo])
        v.append (aRepo)
        v.append (users_predictions[id_sintoma][aRepo])
        vector_id_enfermedad_scoring.append(v)
        
    vector_id_enfermedad_scoring=pd.DataFrame(vector_id_enfermedad_scoring)
    vector_id_enfermedad_scoring = vector_id_enfermedad_scoring.rename(columns={1:id_sintoma, 0:"index"})
    
    listado_completo=_aparece_y_como (vector_id_enfermedad_scoring,id_sintoma, df_Enfermedades, df_Sintomas,df_EnfeySinto_select)
    listado_completo=listado_completo.rename(columns={1: "Enfermedad", 2: "Scoring", 3: "Frecuencia"})
    listado_completo=listado_completo.sort_values("Scoring", ascending=False)
    listado_completo=listado_completo.reset_index()
    listado_completo.drop("index", axis=1, inplace=True)
    #listado_completo= list(reserved(listado_completo))
    logger.info(f'Result={listado_completo}')
    return listado_completo
