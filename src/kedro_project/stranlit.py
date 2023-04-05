from logging import Logger
from typing import List
import streamlit as st
import yaml
from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline
import pandas as pd
from pipelines.data_science import nodes



def load_from_csv (path):
    data=pd.read_csv(path)
    return data  
df_matrix=load_from_csv("/Users/o002629/Documents/Kschool/Master/TFM_project/data/03_primary/df_matrix.csv")
df_enfermedades= load_from_csv("data/01_raw/enfermedades.csv")
df_sintomas= load_from_csv("data/01_raw/sintomas.csv")
df_todo=load_from_csv("data/03_primary/sintomas_and_enfermedades_prepaired.csv")

lista=['Gastroesophageal reflux','Dysphagia','Cough','Weight loss']
df_lista=pd.DataFrame(lista)
options = st.multiselect(
    'Sintoma',
    df_sintomas,
    [])




button_press = st.button("Pulsa para comenzar Análisis")
if button_press:
   
    st.write('You selected:', options[1])
    sintomas=[]
    for i in options:
        #opciones.append(i)
        st.write('bucle:', i)
        sintomas.append(i)

   #print(options)
    
    

    #sintomas=parameters["sintomas"]
    st.write('sintomas:', sintomas)
   # Logger.info(f'sintomas?={}')
    diccionario={
      "sintomas" : sintomas,
      "clasificados" : 10
    }
    #resul=nodes.predict_collaborative_filtering_ser_based (df_matrix,diccionario,df_sintomas,df_enfermedades,df_todo)
    #def trata_sintomas2 (sintomas,df_transpuesta,df_enfermedades,df_sintomas,df_todo ):
    resul=nodes.trata_sintomas2(diccionario,df_matrix,df_enfermedades,df_sintomas,df_todo)
    #trata_sintomas2 (parameters: Dict,df_transpuesta,df_enfermedades,df_sintomas,df_todo):
    #resul=resul.drop(0, axis=1)
    
    
    st.dataframe(resul)
   

