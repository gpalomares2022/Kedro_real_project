"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.5
"""

import pandas as pd
import sklearn.metrics
import xmltodict
from typing import Dict
import logging
import numpy as np

import warnings


logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

#Función interna para cambiar los nombres de las columnas en una matriz por su propia posición de columna (cambia a número de pos).
def _cambiar_columnas(df):
    
    columnas=len(df.columns)
    i=0
    while (i<columnas):
        df = df.rename(columns={df.columns[i]:i})
        i=i+1
        
        
    return df

#Función privada, que usa import_enfermedades_xml, para eliminar carácteres innecesarios 
#en los nombres encontrados en el XML fuente (para enfermedades y frecuencias)
def _limpia_nombre (cadena):
    
    cadena_str= str(cadena)
    cadena_str=cadena_str[26:]
    cadena_str = cadena_str.replace('}', '',1)
    cadena_str = cadena_str.replace('\'','')
    
    return cadena_str

#------------------------------------------------------------------------------------------------------#

#Función primera del pipeline procesamiento de datos.  Se encarga de coger el XML y cargar la información de enfermedades-sintomas-frecuencias.
#Extrae en un dataframe los datos de Enfermedades-Síntomas-Frecuencias del XML de Orphadata. 

def import_enfermedades_xml(parameters: Dict):

    xml=open(parameters["path"], encoding='ISO-8859-1')
    xmldict = xmltodict.parse(xml.read())
    df_enfermedades = pd.DataFrame()
    lista_enfer_sinto_prob=[]
    first_tree=xmldict["JDBOR"]["HPODisorderSetStatusList"]["HPODisorderSetStatus"]
    id=0

    for nodo in xmldict["JDBOR"]["HPODisorderSetStatusList"]["HPODisorderSetStatus"]:
        
        enfermedad=_limpia_nombre(nodo["Disorder"]["Name"])
        sec_tree= nodo["Disorder"]["HPODisorderAssociationList"]
        if (len(sec_tree)==2):
            tam_sintomas=len(sec_tree["HPODisorderAssociation"])
            i=0
            registro_enfer_sinto_prob=[]
            while (i<tam_sintomas):
                registro_enfer_sinto_prob.append(enfermedad)
                registro_enfer_sinto_prob.append(id)

                registro_enfer_sinto_prob.append(sec_tree["HPODisorderAssociation"][i]["HPO"]["HPOTerm"])
                frecuencia=_limpia_nombre(sec_tree["HPODisorderAssociation"][i]["HPOFrequency"]["Name"])
                registro_enfer_sinto_prob.append(frecuencia)
                lista_enfer_sinto_prob.append (registro_enfer_sinto_prob)
                registro_enfer_sinto_prob=[]
                i=i+1
        id=id+1

    df_enfermedades = pd.DataFrame(lista_enfer_sinto_prob)
    df_enfermedades = df_enfermedades.rename(columns={0:'Enfermedad',1:'Id_Enfermedad', 2:'Sintoma', 3:"Frecuencia"})
    return df_enfermedades

#------------------------------------------------------------------------------------------------------#

#Función segunda del pipeline procesamiento de datos. Se encarga de aplicar EDA sobre el CSV disponible tras la lectura del XML.
#En concreto: elimina registros duplicados, los nulos, y los registros que contienen síntomas que sólo aparecen menos de 50 veces 
#en nuestra muestra. Además, se queda con los registros de Enfermedad-Sintoma-Frecuencia que tengan una frecuencia "Muy frecuente",
#  "Frecuente", "Obligatorio" y "Ocasional". Elimina pues los registros con frecuencia Muy poco frecuente y Excluyente.
#En notebook representa a las funciones eda_data y selection_data_frecuency unidas.
def clean_selection_and_preparation_data(csv_enfermedades: pd.DataFrame): 
        

    data=csv_enfermedades
    numero=float(data["Enfermedad"].nunique())

    logger.info ("Inicial antes de EDA")
    logger.info(f'Enfermedades={numero}')
      
    logger.info(f'Sintomas={data["Sintoma"].nunique()}')
    logger.info(f'Frecuencias={data["Frecuencia"].nunique()}')
    data=data.drop_duplicates()

    #Hacemos limpieza de nulos
    data=data.dropna()
    numero=float(data["Enfermedad"].nunique())

    #Nos quedamos con los sintomas que aparezcan más de 50 veces en enfermedades. Si no, eliminamos.
    vc = data["Sintoma"].value_counts()
    vector=vc[vc < 50].index
    for a in vector:
        indexNames = data [ data["Sintoma"] == a ].index
        for b in indexNames:
            data.drop(b , inplace=True, axis=0)
    numero=float(data["Enfermedad"].nunique())

    #Nos quedamos con los registros que sólo tengan estas frecuencias. El resto eliminamos.
    data=data[(data['Frecuencia']=="Muy frecuente (99-80%)") |
              (data['Frecuencia']=="Frecuente (79-30%)") |
              (data['Frecuencia']=="Obligatorio (100%)") |
              (data['Frecuencia']=="Ocasional (29-5%)") |
              (data['Frecuencia']=="Muy poco frecuente (4-1%)")
              
             ]
        
    numero=float(data["Enfermedad"].nunique())

    logger.info ("Final después de EDA")
   
    logger.info(f'Enfermedades={numero}')
      
    logger.info(f'Sintomas={data["Sintoma"].nunique()}')
    logger.info(f'Frecuencias={data["Frecuencia"].nunique()}')
    data=data.drop("Id_Enfermedad", axis=1)

   

    return data

#------------------------------------------------------------------------------------------------------#

#Función tercera del pipeline procesamiento de datos. Función que dado un dataframe de entrada (con todas los registros existentes
#  entre enfermedades, sus síntomas y la frecuencia de aparición), genera una matriz de enfermedades x sintomas, formada por valores
#  únicamente en celdas donde un síntoma concreto (fila) aparezca en la enfermedad. El valor que tendrá dependerá de la frecuencia de
#  aparición de dicho síntoma en la enfermedad (puntos) de tal forma que si es una frecuencia alta la aparición del síntoma en la enfermedad,
#  tendrá más puntuación que una frecuencia más baja. Se persigue con esto disponer de una matriz de puntuaciones/ratings donde cruzamos todos
#  los síntomas con todas las enfermedades, con un conjunto de puntuaciones.
# Estas son las puntuaciones de acuerdo a la existencia de un síntoma en una enfermedad: Muy frecuente"=3,
#  "Frecuente"=2, "Obligatorio"=4 y "Ocasional"=1. El resto de celdas tendrá un valor 0

def generate_data_scoring (clean_and_processed_enfermedades: pd.DataFrame):
    
    data=clean_and_processed_enfermedades
    sintomas=data.iloc[:,1]
    sintomas_sin_repe=sintomas.drop_duplicates()
    sintomas_sin_repe=sintomas_sin_repe.sort_values(ascending
                              = True)
    df_train=pd.DataFrame(columns=sintomas_sin_repe)

 
    
    data_agrupado = (data.groupby("Enfermedad")
         .agg({"Sintoma": np.array, "Frecuencia": np.array})
         .reset_index()
         )
    repeticiones=1
    z=0
    j=0
    while (z<repeticiones):
    

        i=0
        for a in data_agrupado["Enfermedad"]:
       
            lst = [0] * ((len(sintomas_sin_repe)))
           
            df_train.loc[len(df_train)] = lst
      
           
            pos=0
            for b in data_agrupado["Sintoma"][i]:
                frecuencia=data_agrupado["Frecuencia"][i][pos]
                if (frecuencia=="Muy frecuente (99-80%)"):
                        valor_entero=4
                elif (frecuencia=="Frecuente (79-30%)"):
                        valor_entero=3
                elif (frecuencia=="Obligatorio (100%)"):
                    valor_entero=5
                elif (frecuencia=="Ocasional (29-5%)"):
                    valor_entero=2
                elif (frecuencia=="Muy poco frecuente (4-1%)"):
                    valor_entero=1
                    
                df_train[b][j]=valor_entero
               
                pos=pos+1
            j=j+1
            i=i+1
        z=z+1
       
        
    df_train=_cambiar_columnas(df_train)    
    df_matrix=df_train.transpose()
   
   
  
   

    return df_matrix  


#------------------------------------------------------------------------------------------------------#

#Función cuarta del pipeline procesamiento de datos. Se encarga de calcular dos matrices de trabajo .
#La primera de similitud entre los síntomas, y la segunda, que guarda en CSV, la de recomendaciones
#Esta última de recomendación será cargada en el momento de calcular una recomendación de enfermedad 
#dado un síntoma.
#En este código, teniendo en cuenta que trabajamos con pipelines y guardado automático de CSV, no 
#se va a trabajar con SQlite3 de cara a guardar en bbdd las matrices (ya están disponibles en CSV para 
# el trabajo)

def generate_data_recommendations (data_scoring: pd.DataFrame):


    sim_matrix= sklearn.metrics.pairwise.cosine_similarity(data_scoring)

    sintomas_k = sim_matrix.dot(data_scoring) / np.array([np.abs(sim_matrix).sum(axis=1)]).T
    dataframe_recomendaciones= pd.DataFrame(sintomas_k)
    dataframe_recomendaciones.transpose()

    return dataframe_recomendaciones  


  #------------------------------------------------------------------------------------------------------#

#Función quinta del pipeline procesamiento de datos. Genera un CSV con todas las enfermedades registradas


def generate_data_enfermedades (clean_and_processed_enfermedades: pd.DataFrame):

    
    df_Enfermedades=clean_and_processed_enfermedades.groupby (["Enfermedad"]).count().reset_index()
    df_Enfermedades=df_Enfermedades.drop(["Sintoma","Frecuencia"], axis=1)
    df_Enfermedades=df_Enfermedades.reset_index()

    return df_Enfermedades

 #------------------------------------------------------------------------------------------------------#

#Función sexta del pipeline procesamiento de datos. Genera un CSV con todas los sítomas registrados

def generate_data_sintomas (clean_and_processed_enfermedades: pd.DataFrame):

    df_Sintomas=clean_and_processed_enfermedades.groupby (["Sintoma"]).count().reset_index()
    df_Sintomas=df_Sintomas.drop(["Enfermedad","Frecuencia"], axis=1)

    return df_Sintomas


