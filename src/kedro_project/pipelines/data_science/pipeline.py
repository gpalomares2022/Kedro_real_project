from kedro.pipeline import Pipeline, node, pipeline


from .nodes import recommendation_collaborative_filtering_user_based


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            #node(
             #   func=predict_collaborative_filtering_ser_based,
              #  inputs=["data_matrix", "params:model_options","csv_sintomas", "csv_enfermedades", "clean_and_processed_enfermedades"],
               # outputs="data_calculated_scoring",
                #name="predict_collaborative_filtering_ser_based_node",
            #)
           

            
        ]
    )