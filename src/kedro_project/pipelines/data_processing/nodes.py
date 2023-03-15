"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.5
"""
import pandas as pd
import xmltodict
from typing import Dict, Tuple
"""Es una función interna por tener barra baja
YA AQUÍ DEVOLVEMOS TIPOS DE LAS VARIABLES Y LO QUE DEVUELVE """
def _is_true(x: pd.Series,) -> pd.Series:

  return x == "t"
"""DEVUELVE BOOLEANO SI X=='t'. ES LA TÍPICA FUNCIÓN PARA CONVERTIR UNA CADENA 'T' EN TRUE, QUE ES COMO DEBE TRABAJARSE"""

"""Es una función interna por tener barra baja"""
def _parse_percentage(x: pd.Series) -> pd.Series:

  x = x.astype(str).str.replace("%", "")

  x = x.astype(float) / 100

  return x
  """CAMBIA UN EJEMPLO: 10% POR 0.1, QUE ES MÁS ÚTIL PARA OPERAR.. NO NOS VALE PARA NADA 10%"""
"""Es una función interna por tener barra baja"""
def _parse_money(x: pd.Series) -> pd.Series:

  x = x.astype(str).str.replace("$", "").str.replace(",", "")

  x = x.astype(float)

  return x
"""QUITA LOS DOLARES Y COMAS"""
def _limpia_nombre (cadena):
    
    cadena_str= str(cadena)
    cadena_str=cadena_str[26:]
    cadena_str = cadena_str.replace('}', '',1)
    cadena_str = cadena_str.replace('\'','')
    
    return cadena_str

def import_enfermedades_xml(parameters: Dict):

    xml=open(parameters["path"], encoding='ISO-8859-1')
    xmldict = xmltodict.parse(xml.read())
    df_enfermedades = pd.DataFrame()
    lista_enfer_sinto_prob=[]
    first_tree=xmldict["JDBOR"]["HPODisorderSetStatusList"]["HPODisorderSetStatus"]

    for nodo in xmldict["JDBOR"]["HPODisorderSetStatusList"]["HPODisorderSetStatus"]:
        
        enfermedad=_limpia_nombre(nodo["Disorder"]["Name"])
        sec_tree= nodo["Disorder"]["HPODisorderAssociationList"]
        if (len(sec_tree)==2):
            tam_sintomas=len(sec_tree["HPODisorderAssociation"])
            i=0
            registro_enfer_sinto_prob=[]
            while (i<tam_sintomas):
                registro_enfer_sinto_prob.append(enfermedad)
                registro_enfer_sinto_prob.append(sec_tree["HPODisorderAssociation"][i]["HPO"]["HPOTerm"])
                frecuencia=_limpia_nombre(sec_tree["HPODisorderAssociation"][i]["HPOFrequency"]["Name"])
                registro_enfer_sinto_prob.append(frecuencia)
                lista_enfer_sinto_prob.append (registro_enfer_sinto_prob)
                registro_enfer_sinto_prob=[]
                i=i+1
    df_enfermedades = pd.DataFrame(lista_enfer_sinto_prob)
    df_enfermedades = df_enfermedades.rename(columns={0:'Enfermedad',1:'Sintoma', 2:"Frecuencia"})
    return df_enfermedades


















def preprocess_companies(companies: pd.DataFrame) -> pd.DataFrame:

  """Preprocesses the data for companies.
  
  FIJAOS!!! CADA FUNCIÓN DE PYTHON, ES UN NODO EN EL PIPELINE!!!!!



  Args:

    companies: Raw data.

  Returns:

    Preprocessed data, with `company_rating` converted to a float and

    `iata_approved` converted to boolean.

  """

  companies["iata_approved"] = _is_true(companies["iata_approved"])

  companies["company_rating"] = _parse_percentage(companies["company_rating"])

  return companies





def preprocess_shuttles(shuttles: pd.DataFrame) -> pd.DataFrame:

  """Preprocesses the data for shuttles.



  Args:

    shuttles: Raw data.

  Returns:

    Preprocessed data, with `price` converted to a float and `d_check_complete`,

    `moon_clearance_complete` converted to boolean.

  """

  shuttles["d_check_complete"] = _is_true(shuttles["d_check_complete"])

  shuttles["moon_clearance_complete"] = _is_true(shuttles["moon_clearance_complete"])

  shuttles["price"] = _parse_money(shuttles["price"])

  return shuttles

def create_model_input_table(

        shuttles: pd.DataFrame,

        companies: pd.DataFrame,

        reviews: pd.DataFrame,

        ) -> pd.DataFrame:

    

    rated_shuttles = shuttles.merge(

        reviews,

        left_on = 'id',

        right_on ='shuttle_id',

    )



    table = rated_shuttles.merge(

        companies,

        left_on = 'company_id',

        right_on = 'id',

        ).dropna()

    

    return table

