import logging
from typing import Dict, Tuple
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score, roc_curve, precision_score, recall_score
from sklearn.model_selection import GridSearchCV
from sklearn.multioutput import MultiOutputClassifier
import numpy as np
import xgboost as xgb
import lightgbm as lgb
import re
from sklearn.preprocessing import LabelEncoder






logger = logging.getLogger(__name__)


def split_data(data_train_enfermedades: pd.DataFrame, parameters: Dict) -> Tuple:
    """Splits data into features and targets training and test sets.

    Args:
        data: Data containing features and target.
        parameters: Parameters defined in parameters/data_science.yml.
    Returns:
        Split data.
    """
        #
    #data_train_enfermedades=data_train_enfermedades.drop (['Enfermedad'], axis=1)
    X=data_train_enfermedades
    y=data_train_enfermedades["id_Enfermedad"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    return X_train, X_test, y_train, y_test


def train_model(X_train: pd.DataFrame, y_train: pd.DataFrame, X_test: pd.DataFrame, y_test: pd.Series, parameters: Dict) -> RandomForestClassifier:
     

     param_grid = { 
        #'n_estimators': [200, 500],
        'max_depth' : [10,25, 35],
       # 'criterion' :['gini', 'entropy']
     }
     param_rm = {'criterion': 'entropy',
        'max_depth': 30,
        'max_features': 'auto',
        'n_estimators': 500}
    
     rf= RandomForestClassifier ()  
     #rf = lgb.LGBMClassifier()

     #rf = xgb.XGBClassifier()
 
     ## Generate model
     logger.info ("empecé grid")
     

## Make prediction
     #new_names = {col: re.sub(r'[^A-Za-z0-9_]+', '', col) for col in X_train.columns}
     #new_n_list = list(new_names.values())
# [LightGBM] Feature appears more than one time.
     #new_names = {col: f'{new_col}_{i}' if new_col in new_n_list[:i] else new_col for i, (col, new_col) in enumerate(new_names.items())}
     #X_train = X_train.rename(columns=new_names)
     #le = LabelEncoder()
     #y_train = le.fit_transform(y_train)
     rf.fit(X_train, y_train)
     #logger.info(f'paramma={rf.get_params}')

     #CV_rfc = GridSearchCV(estimator=rf, param_grid=param_grid, cv= 5)
     #CV_rfc.fit(X_train, y_train)
     #logger.info(f'Grid={CV_rfc.best_params_}')
     #logger.info(f'Grid={CV_rfc.best_score_}')
     #logger.info ("empecé rf")
     #rf_gscv=RandomForestClassifier(**CV_rfc.best_params_)
     #rf = LGBMRegressor(**params_lgbm)
     
     #rf_gscv.fit(X_train, y_train)
     logger.info ("terminé grid y rf")
     #new_names = {col: re.sub(r'[^A-Za-z0-9_]+', '', col) for col in X_test.columns}
     #new_n_list = list(new_names.values())
# [LightGBM] Feature appears more than one time.
     #new_names = {col: f'{new_col}_{i}' if new_col in new_n_list[:i] else new_col for i, (col, new_col) in enumerate(new_names.items())}
     #X_test = X_test.rename(columns=new_names)
     y_pred=rf.predict(X_test)
    
     #probs=regressor.predict_proba(X_test)[:, 1]
     acc = accuracy_score(y_test, y_pred)
     pres= precision_score (y_test, y_pred, average='micro')
     f1 = f1_score(y_test, y_pred, average='micro')
     rec= recall_score (y_test, y_pred, average='micro')

     #auc = roc_auc_score(y_test, probs)
     logger.info(f'Accurancy={acc}')
     logger.info(f'Precision={pres}')
     logger.info(f'F1={f1}')
     logger.info(f'Recall={rec}')
     

     return rf

   

def evaluate_model(
    classificator: RandomForestClassifier, X_test: pd.DataFrame, y_test: pd.Series, parameters: Dict
):
    """Calculates and logs the coefficient of determination.

    Args:
        regressor: Trained model.
        X_test: Testing data of independent features.
        y_test: Testing data for price.
    """
    y_pred=classificator.predict(X_test)
    probs=classificator.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    pres= precision_score (y_test, y_pred, average='micro')
    f1 = f1_score(y_test, y_pred, average='micro')
    rec= recall_score (y_test, y_pred, average='micro')
    #auc = roc_auc_score(y_test, probs)
    logger.info(f'Accurancy={acc}')
    logger.info(f'Precision={pres}')
    logger.info(f'Recall={rec}')
    logger.info(f'F1={f1}')
  
    #print ("auc: ", auc)
    #y_pred = regressor.predict(X_test)
    #score = r2_score(y_test, y_pred)  #Correlacion
    #logger.info("Model has a coefficient R^2 of %.3f on test data.", score)
    #logger.info("With LGBMRegressor and parameters %.f max_depth, %.f n_estimators, %.3f learning_rate", parameters["max_depth"], parameters["n_estimators"],parameters["learning_rate"] )
   