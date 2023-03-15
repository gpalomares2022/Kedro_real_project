"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.5
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import preprocess_companies, preprocess_shuttles, create_model_input_table, import_enfermedades_xml
"""aqui importamos las funciones de nodes (archivo nodes de la carpeta que tiene pipeline)"""

"""Ahora creamos un pipeline con los nodos que queramos eah"""
def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
               
                func=preprocess_companies,
                inputs="companies",
                outputs="preprocessed_companies",
                name="preprocess_companies_node",
            ),
            node(
                func=preprocess_shuttles,
                inputs="shuttles",
                outputs="preprocessed_shuttles",
                name="preprocess_shuttles_node",
            ),
            node(

                func=create_model_input_table,

                inputs=["preprocessed_shuttles","preprocessed_companies", "reviews"],

                outputs="model_input_table",

                name="create_model_input_table_node",

            ),
            node(

                func=import_enfermedades_xml,

                inputs="params:processing_options",

                outputs="processed_enfermedades",

                name="import_enfermedades_xml_node",

            ),
            
        ]
    )
"""Se puede usar la misma función en nodos diferentes con imputs diferentes. Típica función genérica que puedes preparar para varios"""