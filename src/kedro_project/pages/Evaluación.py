import streamlit as st
import pandas as pd
from pipelines.data_science import nodes


#Función interna para hacer lectura de CSV
def load_from_csv (path):
    data=pd.read_csv(path)
    return data  


#------------------------------------------------------------------------------------------------------#

#INSTRUCCIONES PARA STREAMLIT INTERFAZ WEB

#Leemos los Síntomas existentes para que sean cargados en el multiselect de Streamlit (combo multiseleccionable)
df_sintomas= load_from_csv("data/03_primary/sintomas.csv")


st.sidebar.header("TFM Máster Data Science - KSchool - Gabriel Palomares")

st.sidebar.header ("Sistemas Recomendador de Enfermedades raras")



button_press = st.sidebar.button("Pulsa para comenzar Análisis y Recomendador")

option = st.sidebar.selectbox(
            'Seleccione aquí los síntomas del paciente, y luego pulse el botón superior para comenzar el análisis y recomendación.',
            df_sintomas)
#Incluimos el botón para comenzar el Analísis y Recomendación. 

ranking=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
buenos=["b", "c", "g", "i", "j"]
  

import numpy as np

n = 10
nums = np.zeros(n)

print(nums)


if (len(ranking)>0):   
    i=0
    
    while (i<len(ranking)):
        a=st.checkbox(ranking[i], key=i)
        if (a):
            nums[i]=True
          
        else:
            nums[i]=False
           
        i=i+1
   #



button_calcular = st.button("Calcular")

if (button_calcular):
    print (nums)
    print (buenos)

    i=0
    total=0
    while (i<len(nums)):
        print (nums[i])
        if nums[i]==1.0:
            print (ranking[i])
            if ranking[i] in buenos:
                print ("bien")
                total=total+1
            else:
                print ("no bien")
        i=i+1    

    total=total*20
    print (total)
   # 
   # 
    
   #  button_press=True    
    


   # genre = st.radio(
    #"What's your favorite movie genre",
    #[":rainbow[Comedy]", "***Drama***", "Documentary :movie_camera:"],
    #captions = [ranking])



    #Finalmente,se pinta en pantalla el listado que ha montado la función llamada_recomendador

