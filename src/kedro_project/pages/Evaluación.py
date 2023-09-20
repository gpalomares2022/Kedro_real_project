import streamlit as st
import pandas as pd
from pipelines.data_science.nodes import llamada_recomendador_metrica
from pipelines.data_science import nodes


#Función interna para hacer lectura de CSV
def load_from_csv (path):
    data=pd.read_csv(path)
    return data  

def total_elements(list):
    count = 0
    for element in list:
        if element==1:
            count += 1
    return count
#------------------------------------------------------------------------------------------------------#

#INSTRUCCIONES PARA STREAMLIT INTERFAZ WEB

#Leemos los Síntomas existentes para que sean cargados en el multiselect de Streamlit (combo multiseleccionable)
df_sintomas= load_from_csv("data/03_primary/sintomas.csv")


st.sidebar.header("TFM Máster Data Science - KSchool - Gabriel Palomares")

st.sidebar.header ("Evaluación contínua del Sistema Recomendador de Enfermedades raras")

ranking=[]
option=""

#if 'sintoma' not in st.session_state:
    
    

option = st.sidebar.selectbox(
            'Seleccione un único síntoma para que el sistema le proporcione un listado de 10 posibles enfermedades asociadas a éste:',
            df_sintomas)
#Incluimos el botón para comenzar el Analísis y Recomendación. 
   
button_press = st.sidebar.button("Pulsa para obtener el listado")

  
if button_press: #and 'sintoma' not in st.session_state:
     #   print ("entra")
        
        st.session_state.sintoma=option
        ranking, buenos=llamada_recomendador_metrica(option)
        df_ranking=pd.DataFrame(ranking)
        df_ranking.to_csv("data/04_feature/listado_evaluado.csv")
        df_buenos=pd.DataFrame(buenos)
        df_buenos.to_csv("data/04_feature/listado_bueno.csv")


import numpy as np

n = 10
nums = np.zeros(n)
#print ("opcion")
#print (option)
#print (st.session_state.sintoma)

if 'sintoma' in st.session_state: #and len(option)==0:
    ranking_cargado=pd.read_csv("data/04_feature/listado_evaluado.csv")
    ranking=ranking_cargado.to_numpy().transpose().tolist()
    ranking=ranking[1]
    buenos_cargado=pd.read_csv("data/04_feature/listado_bueno.csv")
    buenos=buenos_cargado.to_numpy().transpose().tolist()
    buenos=buenos[1]     
if (len(ranking)>0): 

        option=st.session_state.sintoma
        st.header("Aquí se exponen las enfermedades que pueden estar asociadas por el síntoma: "+ option)
        st.write ("Debe seleccionar 5 enfermedades que, según su estudio, pueden estar asociadas con dicho síntoma, y por tanto deben ser estudiadas.")
        i=0
    
        while (i<len(ranking)):
            a=st.checkbox(ranking[i], key=i)
            if (a):
                nums[i]=True
          
            else:
                nums[i]=False
           
            i=i+1
   #
        #print (nums)
        



        button_calcular = st.button("Calcular")

        if (button_calcular):
            enfermedades_acertadas=[]
            enfermedades_no_recomendadas=[]
            if total_elements(nums)!=5:
                st.write ("Debe seleccionar 5 elementos para poder continuar")

            else:    
               # print (buenos)

                i=0
                total=0
                while (i<len(nums)):
                   # print (nums[i])
                    if nums[i]==1.0:
                       # print (ranking[i])
                        if ranking[i] in buenos:
                           # print ("La enfermedad siguiente, ofrecida por el recomendador, ha sido diagnosticada también por el usuario: ", ranking[i])
                            enfermedades_acertadas.append(ranking[i])
                            total=total+1
                        else:
                            enfermedades_no_recomendadas.append(ranking[i])
                            #print ("no bien")
                    i=i+1    

                total=total*20
               
                st.header("Y el acierto es: " + str(total)+"%")
                print ("Listado de enfermedades, ofrecidas por el recomendador, que han sido diagnosticadas también por el usuario: ")
                print (enfermedades_acertadas)
                df_enfermedades_acertadas=pd.DataFrame(enfermedades_acertadas)
                df_enfermedades_acertadas.to_csv("data/04_feature/enfermedades_acertadas.csv")
                print ("Listado de enfermedades, NO ofrecidas por el recomendador, que han sido diagnosticadas por el usuario: ")
                print (enfermedades_no_recomendadas)
                df_enfermedades_no_recomendadas=pd.DataFrame(enfermedades_no_recomendadas)
                df_enfermedades_no_recomendadas.to_csv("data/04_feature/enfermedades_no_recomendadas.csv")
           
   # 
   # 
    
 

   # genre = st.radio(
    #"What's your favorite movie genre",
    #[":rainbow[Comedy]", "***Drama***", "Documentary :movie_camera:"],
    #captions = [ranking])



    #Finalmente,se pinta en pantalla el listado que ha montado la función llamada_recomendador

