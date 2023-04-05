"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.5
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import import_enfermedades_xml, clean_selection_and_preparation_data, generate_data_matrix, generate_data_enfermedades, generate_data_sintomas
  

"""aqui importamos las funciones de nodes (archivo nodes de la carpeta que tiene pipeline)"""

"""Ahora creamos un pipeline con los nodos que queramos eah"""
def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
             node(

                func=import_enfermedades_xml,

                inputs="params:processing_options",

                outputs="csv_enfermedades_and_sintomas",

                name="import_enfermedades_xml_node",

            ),
            node(

                func=clean_selection_and_preparation_data,

                inputs="csv_enfermedades_and_sintomas",

                outputs="clean_and_processed_enfermedades",

                name="clean_selection_and_preparation_data_node",

            ),
            node(

               func=generate_data_matrix,

               inputs="clean_and_processed_enfermedades",

               outputs="data_matrix",

               name="generate_data_matrix_node",

            ),
            node(

               func=generate_data_enfermedades,

               inputs="clean_and_processed_enfermedades",

               outputs="csv_enfermedades",

               name="generate_data_enfermedades_node",

            ),
            node(

               func=generate_data_sintomas,

               inputs="clean_and_processed_enfermedades",

               outputs="csv_sintomas",

               name="generate_data_sintomas_node",

            ),
            
        ]
    )
"""Se puede usar la misma función en nodos diferentes con imputs diferentes. Típica función genérica que puedes preparar para varios"""