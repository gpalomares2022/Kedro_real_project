import logging
from typing import Dict, Tuple

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor



logger = logging.getLogger(__name__)


def split_data(data: pd.DataFrame, parameters: Dict) -> Tuple:
    """Splits data into features and targets training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters/data_science.yml.
    Returns:
        Split data.
    """
    X = data[parameters["features"]]
    y = data[parameters["target"]]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=parameters["test_size"], random_state=parameters["random_state"]
    )
    return X_train, X_test, y_train, y_test


def train_model(
      X_train: pd.DataFrame, y_train: pd.DataFrame, parameters: Dict) -> RandomForestRegressor:
     
     max_depth= parameters["max_depth"]
     n_estimators= parameters["n_estimators"]
     learning_rate= parameters["learning_rate"]
     params_lgbm={'max_depth':max_depth, 'n_estimators': n_estimators, 'learning_rate': learning_rate}
     params_random_forest={'max_depth':max_depth}
     rf= RandomForestRegressor (**params_random_forest)   
     #rf = LGBMRegressor(**params_lgbm)

     rf.fit(X_train, y_train)
     return rf

   

def evaluate_model(
    regressor: RandomForestRegressor, X_test: pd.DataFrame, y_test: pd.Series, parameters: Dict
):
    """Calculates and logs the coefficient of determination.

    Args:
        regressor: Trained model.
        X_test: Testing data of independent features.
        y_test: Testing data for price.
    """
    y_pred = regressor.predict(X_test)
    score = r2_score(y_test, y_pred)  #Correlacion
    logger.info("Model has a coefficient R^2 of %.3f on test data.", score)
    #logger.info("With LGBMRegressor and parameters %.f max_depth, %.f n_estimators, %.3f learning_rate", parameters["max_depth"], parameters["n_estimators"],parameters["learning_rate"] )
    logger.info("With RandomForest and parameters %.f max_depth", parameters["max_depth"])