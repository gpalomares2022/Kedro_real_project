import logging
import sqlite3
from typing import Dict, Tuple
from git import List
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from sklearn.metrics import f1_score, accuracy_score, roc_auc_score, roc_curve, precision_score, recall_score
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
import numpy as np
import xgboost as xgb

import re
from sklearn.preprocessing import LabelEncoder






logger = logging.getLogger(__name__)

def _contar(data):

    result = {}
    for item in data:
        if item not in result.keys():
            result[item] = 1
        else:
            result[item] += 1
    #result = {'a': 'Apple', 'b': 'Banana', 'c': 'Cherries', 'd': 'Dragon Fruit'}

    myList = zip(result.keys(), result.values()) 

    myList = list(myList)   
    return myList



def _aparece_y_como (scoring_enfermedades,id_Sintoma, df_Enfermedades, df_Sintomas,df_EnfeySinto_select):
    
    #print ("como coño")
    
    j=0
    enfermedades=[]
    while (j<len(scoring_enfermedades)):
        enfermedad=[]
        id_enfermedad=scoring_enfermedades["index"][j]
        scoring=scoring_enfermedades[id_Sintoma][j]
        
        enfermedad.append(id_enfermedad)
        
       
        enfermedad.append(df_Enfermedades[df_Enfermedades["index"]==id_enfermedad]["Enfermedad"].values[0])
   
        enfermedad.append(str(scoring))
        lista=df_EnfeySinto_select[df_EnfeySinto_select["Enfermedad"]==
                                   df_Enfermedades.loc[id_enfermedad][1]]
        lista=lista.reset_index()
        sintoma= df_Sintomas.loc[id_Sintoma].Sintoma
        enfermedad.append(sintoma)
        i=0
        while i<len(lista):
         
            if lista["Sintoma"][i]==sintoma:
                enfermedad.append(lista["Frecuencia"][i])
            
            i=i+1  
        j=j+1
        enfermedades.append(enfermedad)
        df_enfermedades=pd.DataFrame(enfermedades)
        
    return df_enfermedades

# def _aparece_y_como2 (enfermedades, df_Enfermedades, df_Sintomas,df_EnfeySinto_select):
    

    
#     j=0
#     lista_todo=[]
#     df_enfermedades=pd.DataFrame()
#     while (j<len(enfermedades)):
#         enfermedad=[]
#         id_enfermedad=enfermedades[j]
#         #scoring=scoring_enfermedades[id_Sintoma][j]
        
#         enfermedad.append(id_enfermedad)
       
#         enfermedad.append(df_Enfermedades[df_Enfermedades["index"]==id_enfermedad]["Enfermedad"].values[0])
   
#        # enfermedad.append(scoring)
#         #lista=df_EnfeySinto_select[df_EnfeySinto_select["Enfermedad"]==
#          #                          df_Enfermedades.loc[id_enfermedad][1]]
#         #lista=lista.reset_index()
#         #sintoma= df_Sintomas.loc[id_Sintoma].Sintoma
        
#         #i=0
#         #while i<len(lista):
         
#          #   if lista["Sintoma"][i]==sintoma:
#           #      enfermedad.append(lista["Frecuencia"][i])
            
#            # i=i+1  
#         #j=j+1
#         lista_todo.append(enfermedad)
#         j=j+1
#     lista_todo=pd.DataFrame(lista_todo)
        
#     return lista_todo

# def _prepara_matrix (comunes, enfermedades, sintomas,df_todo,df_matrix):

#     resultados=[]
#   #  prueba=pd.DataFrame()
#     #prueba.add
    
#     comunes=pd.merge(comunes, enfermedades, on='key')




#     return resultados


    

def trata_sintomas_copy (parameters: list,df_transpuesta,df_enfermedades,df_sintomas,df_todo):
    comunes=[]
    logger.info(f'Param={parameters}')
    logger.info(f'sintomas?={parameters["sintomas"]}')
    sintomas=parameters["sintomas"]
    logger.info(f'Sintomas={sintomas}')
    clasificados=parameters["clasificados"]
    logger.info(f'Clasificados={clasificados}')
    primera_iter=True
    df_matrix=df_transpuesta
    lista=[]
    enfermedades_scoring=[]
    enfermedades_scoring=pd.DataFrame(enfermedades_scoring)
    enfermedades=[]
    i=0
    resuultados=pd.DataFrame()
    print("número:", clasificados)
    init_collaborative_filtering_user_based (df_matrix.values)
    
    
    for i in sintomas:
        diccionario={
            "sintoma" : i,
            "clasificados" : clasificados
        }
        vector=[]
        #lista,vector=predict_similitud_entre_usuarios_by_pearson(df_transpuesta,i,20)
        v=predict_collaborative_filtering_ser_based(diccionario,df_sintomas,df_enfermedades,df_todo)
      
        
        v=pd.DataFrame(v)
        V=v.dropna()
        #EN ENFERMEDADES SCORING VAMOS COGIENDO LOS X ENFERMEDADES POR CADA SINTOMA. NO FILTRAMOS... SOLO RECOPILAMOS CON CONCAT EN BUCLE
        enfermedades_scoring=pd.concat([enfermedades_scoring,v], axis=0)
        enfermedades_scoring=enfermedades_scoring.dropna()
        
    print("TODAS: ", enfermedades_scoring)
   #DE TODO EL LISTADO GRANDE QUE HEMOS SACADO, FILTRAMOS QUITANDO LOS QUE NO ESTÉN EN LA LISTA DE COMUNES
    if len(enfermedades_scoring)>0:
     
       # enfermedades_scoring=enfermedades_scoring.sort_values(by="Scoring", ascending=False)

        data_agrupado = (enfermedades_scoring.groupby("Enfermedad")
         .agg({"Frecuencia": np.array, "Scoring": np.double, "Síntomas": np.array})
         .reset_index()
         )
        #print(data_agrupado.shape)
        enfermedades_suma=[]
        #print("tamaño: ", len(data_agrupado))
        #print ("cuantos ", data.shape)
        i=0
        
        
        while (i<len(data_agrupado)):
             enfermedad_suma=[]
             enfermedad_suma.append (data_agrupado["Enfermedad"][i])
             #print("scoringss", data_agrupado["Scoring"])

             sintomas_para_sumar=data_agrupado["Scoring"][i]
             nombre_sintoma=data_agrupado["Síntomas"][i]
             
             #sintomas_para_sumar=(data_agrupado["Scoring"][i])
             agrupado_nombre_sintoma=[]
             if (type(sintomas_para_sumar)==np.float64):
                #print("ok")
                g=[]
                total=round(sintomas_para_sumar,3)
                g.append(nombre_sintoma[0] + " ("+ str(total) + ")")
                num_sintomas=1

              #  agrupado_nombre_sintoma.append( nombre_sintoma + " ("+ str(total) +")")
             else:
                 j=0
                 total=0
                 num_sintomas=len(sintomas_para_sumar)
                 g=[]
                 while (j<num_sintomas):
                     print("sin: ", sintomas_para_sumar[j])
                     valor= round(sintomas_para_sumar[j],3)

                     g.append(nombre_sintoma[j] + " ("+ str(valor) + ")")
                    # agrupado_nombre_sintoma.append(
                     total=sintomas_para_sumar[j]+total
                     j=j+1
                 
             
             enfermedad_suma.append(g)
             enfermedad_suma.append(total)
                # print (total)
             
             
             enfermedades_suma.append(enfermedad_suma)
            
             i=i+1
      
        df_enfermedades_suma=pd.DataFrame (enfermedades_suma)
        df_enfermedades_suma = df_enfermedades_suma.rename(columns={1:"Síntomas", 0:"Enfermedad", 2:"Scoring"})
        df_enfermedades_suma=df_enfermedades_suma.sort_values(by="Scoring", ascending=False)
        df_enfermedades_suma=df_enfermedades_suma.reset_index()
        df_enfermedades_suma.drop("index", axis=1, inplace=True)
        #enfermedades_suma=enfermedades_suma.sort()
        print(df_enfermedades_suma)
   # enfermedades=pd.DataFrame(enfermedades)
    else:
        enfermedades_scoring=pd.DataFrame()
        data_agrupado=pd.DataFrame()
        df_enfermedades_suma=pd.DataFrame()

    #print (enfermedades_scoring)
 
    return  enfermedades_scoring.head(50), data_agrupado, df_enfermedades_suma





def init_collaborative_filtering_user_based (ratings):
    
    #sim_matrix = 1 - sklearn.metrics.pairwise.cosine_distances(ratings)
    sim_matrix= sklearn.metrics.pairwise.cosine_similarity(ratings)
    sintomas_k = sim_matrix.dot(ratings) / np.array([np.abs(sim_matrix).sum(axis=1)]).T
    #print(sintomas_k)


    conn = sqlite3.connect('test_database')
    c = conn.cursor()


    df = pd.DataFrame(sintomas_k)
    df=df.transpose()
    df.to_sql('scorings_tfm_kedro', conn, if_exists='replace', index = False)





def predict_collaborative_filtering_ser_based( parameters: Dict, 
                                              csv_sintomas: pd.DataFrame, csv_enfermedades: pd.DataFrame, 
                                              clean_and_processed_enfermedades: pd.DataFrame):
  
    sintoma=parameters["sintoma"]
    elementos=parameters["clasificados"]
    df_Sintomas=csv_sintomas
    df_EnfeySinto_select=clean_and_processed_enfermedades
    df_Enfermedades=csv_enfermedades
    #ratings=data_matrix.values
    id_sintoma = df_Sintomas[df_Sintomas['Sintoma'] == sintoma].index.values[0]


    conn = sqlite3.connect('test_database')
    c = conn.cursor()
    c.execute('''  SELECT * FROM scorings_tfm_kedro
          ''')
    #Predicciones (las recomendaciones!)
    sintomas_k = pd.DataFrame(c.fetchall())  
    sintomas_k=sintomas_k.transpose()
    #print (sintomas_k)
    sintomas_k=sintomas_k.to_numpy()
    
    
    #Predicciones (las recomendaciones!)
    
    user0=sintomas_k.argsort()[id_sintoma]
    vector_id_enfermedad_scoring=[]
    for i, aRepo in enumerate(user0[-elementos:]):
        v=[]
        selRepo = df_Enfermedades[df_Enfermedades["index"]==aRepo]
  
       # print('Enfermedad:', selRepo["Enfermedad"] , 'scoring:', users_predictions[sintoma_ver][aRepo])
        v.append (aRepo)
        v.append (sintomas_k[id_sintoma][aRepo])
        v.append (sintoma)
        vector_id_enfermedad_scoring.append(v)
        
    vector_id_enfermedad_scoring=pd.DataFrame(vector_id_enfermedad_scoring)
    vector_id_enfermedad_scoring = vector_id_enfermedad_scoring.rename(columns={1:id_sintoma, 0:"index"})
    
    listado_completo=_aparece_y_como (vector_id_enfermedad_scoring,id_sintoma, df_Enfermedades, df_Sintomas,df_EnfeySinto_select)
    listado_completo=listado_completo.rename(columns={1: "Enfermedad", 2: "Scoring", 3: "Síntomas", 4: "Frecuencia"})
    listado_completo=listado_completo.sort_values("Scoring", ascending=False)
    listado_completo=listado_completo.reset_index()
    listado_completo.drop("index", axis=1, inplace=True)
    #listado_completo= list(reserved(listado_completo))
   # logger.info(f'Result={listado_completo}')
    return listado_completo
