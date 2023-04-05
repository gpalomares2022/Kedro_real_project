from kedro.pipeline import Pipeline, node, pipeline


from .nodes import predict_collaborative_filtering_ser_based, trata_sintomas2


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=predict_collaborative_filtering_ser_based,
                inputs=["data_matrix", "params:model_options","csv_sintomas", "csv_enfermedades", "clean_and_processed_enfermedades"],
                outputs="data_calculated_scoring",
                name="predict_collaborative_filtering_ser_based_node",
            ),
            node(
                func=trata_sintomas2,
                inputs=["params:model_options","data_matrix","csv_enfermedades","csv_sintomas","clean_and_processed_enfermedades"],
                outputs="data_calculated_multi_scoring",
                name="trata_sintomas2_node",
            ),

            
        ]
    )