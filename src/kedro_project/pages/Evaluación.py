import streamlit as st
import pandas as pd
from pipelines.data_science.nodes import llamada_recomendador_metrica
import numpy as np

#Función interna para hacer lectura de CSV
def _load_from_csv (path):
    data=pd.read_csv(path)
    return data  

#Función interna para hacer escritura de CSV
def _write_to_csv (df,path):
    df.to_csv(path)

#Función interna para contar cuantos 1 tiene una lista. Es usado para contabilizar las enfermedades hay marcadas en el listado de checks.
#Los seleccionados se marca con 1, y los no en 0.
def _total_elements_with_1(list):
    count = 0
    for element in list:
        if element==1:
            count += 1
    return count
#------------------------------------------------------------------------------------------------------#

#INSTRUCCIONES PARA STREAMLIT INTERFAZ WEB

#Leemos los Síntomas existentes para que sean cargados en el combo de única selección de Streamlit
df_sintomas= _load_from_csv("data/03_primary/sintomas.csv")

#Información para pantalla
st.sidebar.header("TFM Máster Data Science - KSchool - Gabriel Palomares")

st.sidebar.header ("Evaluación contínua del Sistema Recomendador de Enfermedades raras")

listado_mezclados=[]



    
#Mosramos el combo    

sintoma = st.sidebar.selectbox(
            'Seleccione un único síntoma para que el sistema le proporcione un listado de 10 posibles enfermedades asociadas a éste:',
            df_sintomas)
#Incluimos el botón para que el sistema muestre el listado de enfermedades para evaluar. 
   
button_press = st.sidebar.button("Pulsa para obtener el listado")

  
if button_press: 
        #Si ya se ha seleccionado un síntoma y pulsado el botón, metemos en sesión el síntoma seleccionado (para que en la navegación
        # no se pierda el sintoma marcado)
        #Procedemos a llamar a la función de llamada_recomendador_metrica que nos devuelve: listado de 10 enfermedades (5 primeras 
        # recomendadas y 5 aleatorias, mezcladas), junto con el listado de las 5 que vienen recomendadas.
        
        st.session_state.sintoma=sintoma
        listado_mezclados, solo_los_recomendados=llamada_recomendador_metrica(sintoma)
        df_listado_mezclados=pd.DataFrame(listado_mezclados)
        _write_to_csv(df_listado_mezclados,"data/03_primary/listado_mezclados.csv")
        #guardamos en CSV tanto el listado de 10 enfermedades mezcladas, como el listado de las 5 recomendadas
        #Se guardan porque en la navegación, al montarse como un html, cada vez que refrescas tendrías que hacer este cálculo
        #En lugar de hacerlo, cargamos el CSV
        df_solo_los_recomendados=pd.DataFrame(solo_los_recomendados)
        _write_to_csv(df_solo_los_recomendados,"data/03_primary/listado_solo_los_recomendados.csv")



#Preparamos el listado de checks para la web (todo 0s). Conforme se vayan marcando los checks, esa posición se pondrá a 1. 
#Trabajaremos con True o False.
listado_web_checks = np.zeros(10)


if 'sintoma' in st.session_state:
    #Metemos esta condición de si hay síntoma en sesión, por si hay precarga de la web. En este caso cargaríamos los 2 listados de trabajo 
    df_listado_mezclados=_load_from_csv("data/03_primary/listado_mezclados.csv")
    listado_mezclados=df_listado_mezclados.to_numpy().transpose().tolist()
    listado_mezclados=listado_mezclados[1]
    df_solo_los_recomendados=_load_from_csv("data/03_primary/listado_solo_los_recomendados.csv")
    solo_los_recomendados=df_solo_los_recomendados.to_numpy().transpose().tolist()
    solo_los_recomendados=solo_los_recomendados[1] 

if (len(listado_mezclados)>0): 
        #Si ya tenemos 10 enfermedades, es porque ya hay una selección de síntoma.
        #Mostramos en pantalla un texto y el listado de checks con las 10 enfermedades (para marcar)
        sintoma=st.session_state.sintoma
        st.header("Aquí se exponen las enfermedades que pueden estar asociadas por el síntoma: "+ sintoma)
        st.write ("Debe seleccionar 5 enfermedades que, según su estudio, pueden estar asociadas con dicho síntoma, y por tanto deben ser estudiadas.")
        i=0
        #VAmos testeando si algún check se ha marcado, para marcar a True o False (1 o 0) el check
        while (i<len(listado_mezclados)):
            check_seleccionado=st.checkbox(listado_mezclados[i], key=i)
            if (check_seleccionado):
                listado_web_checks[i]=True
          
            else:
                listado_web_checks[i]=False
           
            i=i+1
        #Si hay listado, mostramos también ya el botón de calcular el porcentaje de acierto
        button_calcular = st.button("Calcular Acierto")

        if (button_calcular):
            enfermedades_acertadas=[]
            enfermedades_no_recomendadas=[]
            
            if _total_elements_with_1(listado_web_checks)!=5:
                st.write ("Debe seleccionar 5 elementos para poder continuar")

            else:    
            #Si se ha seleccionado 5 enfermedades por parte del usuario, requisito de la Evaluación, vamos comprobando cual es la selección de 
            #las enfermedades.      
            #Vamos calculando el porcentaje de acierto, e incluyendo en las listas que luego usaremos de reporting (ver siguientes lineas)
                i=0
                total=0
                while (i<len(listado_web_checks)):
                 
                    if listado_web_checks[i]==True:
                     
                        if listado_mezclados[i] in solo_los_recomendados:
                           
                            enfermedades_acertadas.append(listado_mezclados[i])
                            total=total+1
                        else:
                            enfermedades_no_recomendadas.append(listado_mezclados[i])
                            
                    i=i+1    

                total=total*20

                i=0
                enfermedades_no_acertadas=[]
                while (i<len(solo_los_recomendados)):
                    if solo_los_recomendados[i] not in enfermedades_acertadas:
                        enfermedades_no_acertadas.append(solo_los_recomendados[i])
                    i=i+1
                    
               
                st.header("Y el acierto es: " + str(total)+"%")

                #Aquí las listas calculadas para reporting, ahora en modo logs. Se pueden ver su descripción para ser entendidas
                print ("Listado de enfermedades, ofrecidas por el recomendador, que han sido diagnosticadas también por el usuario: ")
                print (enfermedades_acertadas)

                print ("Listado de enfermedades, ofrecidas por el recomendador, que NO han sido diagnosticadas por el usuario: ")
                print (enfermedades_no_acertadas)
                
                print ("Listado de enfermedades, NO ofrecidas por el recomendador, que han sido diagnosticadas por el usuario: ")
                print (enfermedades_no_recomendadas)
               
           
   

