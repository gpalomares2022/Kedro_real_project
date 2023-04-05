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

user_name = st.text_input('Indica Sintoma: ')
diccionario={
  "sintoma" : user_name,
  "clasificados" : 10
}
button_press = st.button("Pulsa para comenzar Análisis")
if button_press:

    resul=nodes.predict_collaborative_filtering_ser_based (df_matrix,diccionario,df_sintomas,df_enfermedades,df_todo)
    resul=resul.drop(0, axis=1)
    resul=resul.rename(columns={1: "Enfermedad", 2: "Scoring", 3: "Frecuencia"})
    resul=resul.sort_values("Scoring", ascending=False)
    
    st.dataframe(resul)
   

