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

#Función interna para hacer sustituciones de una cadena, y sea más fácil de trabajar el XML
def _limpia_nombre (cadena):
    
    cadena_str= str(cadena)
    cadena_str=cadena_str[26:]
    cadena_str = cadena_str.replace('}', '',1)
    cadena_str = cadena_str.replace('\'','')
    
    return cadena_str

#------------------------------------------------------------------------------------------------------#

#Función primera del pipeline procesamiento de datos.  Se encarga de coger el XML y cargar la información de enfermedades-sintomas-frecuencias
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
              (data['Frecuencia']=="Ocasional (29-5%)")
              
             ] 
    numero=float(data["Enfermedad"].nunique())

    logger.info ("Final después de EDA")
   
    logger.info(f'Enfermedades={numero}')
      
    logger.info(f'Sintomas={data["Sintoma"].nunique()}')
    logger.info(f'Frecuencias={data["Frecuencia"].nunique()}')
    data=data.drop("Id_Enfermedad", axis=1)

   

    return data

#------------------------------------------------------------------------------------------------------#

#Función tercera del pipeline procesamiento de datos. Se encarga de calcular los ratings o scoring de relación entre enfermedades
#y síntomas. En función de la frecuencia dará un valor de 1,2,3, o 4
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
             
                        valor_entero=3
                
                elif (frecuencia=="Frecuente (79-30%)"):
           
                        valor_entero=2
                
                         
                elif (frecuencia=="Obligatorio (100%)"):
                    valor_entero=4

                elif (frecuencia=="Ocasional (29-5%)"):
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

def generate_data_recommendations (data_scoring: pd.DataFrame):


    sim_matrix= sklearn.metrics.pairwise.cosine_similarity(data_scoring)

    sintomas_k = sim_matrix.dot(data_scoring) / np.array([np.abs(sim_matrix).sum(axis=1)]).T
    dataframe_recomendaciones= pd.DataFrame(sintomas_k)
    dataframe_recomendaciones.transpose()

    return dataframe_recomendaciones  


  #------------------------------------------------------------------------------------------------------#

#Función quinta del pipeline procesamiento de datos. Genera un CSV con todas las enfermedades registradas


def generate_data_enfermedades (clean_and_processed_enfermedades: pd.DataFrame):

    data=clean_and_processed_enfermedades
    df_Enfermedades=data.groupby (["Enfermedad"]).count().reset_index()
    df_Enfermedades=df_Enfermedades.drop(["Sintoma","Frecuencia"], axis=1)
    df_Enfermedades=df_Enfermedades.reset_index()

    return df_Enfermedades

 #------------------------------------------------------------------------------------------------------#

#Función sexta del pipeline procesamiento de datos. Genera un CSV con todas los sítomas registrados

def generate_data_sintomas (clean_and_processed_enfermedades: pd.DataFrame):

    data=clean_and_processed_enfermedades
    df_Sintomas=data.groupby (["Sintoma"]).count().reset_index()
    df_Sintomas=df_Sintomas.drop(["Enfermedad","Frecuencia"], axis=1)

    return df_Sintomas


