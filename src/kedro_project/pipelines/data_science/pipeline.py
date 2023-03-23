from kedro.pipeline import Pipeline, node, pipeline

from .nodes import evaluate_model,train_model, split_data


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=split_data,
                inputs=["data_train_enfermedades", "params:model_options"],
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split_data_node",
            ),
            node(
                func=train_model,
                inputs=["X_train", "y_train", "X_test", "y_test", "params:model_options"],
                outputs="classificator",
                name="train_model_node",
            ),
            node(
                func=evaluate_model,
                inputs=["classificator", "X_test", "y_test","params:model_options"],
                outputs=None,
                name="evaluate_model_node",
            ),
        ]
    )