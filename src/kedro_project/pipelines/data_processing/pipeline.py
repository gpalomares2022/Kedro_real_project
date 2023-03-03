"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.18.5
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import preprocess_companies, preprocess_shuttles
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
        ]
    )
