from core.modules.fstream_operations import read_work_file
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, confusion_matrix, 
                            RocCurveDisplay)
import pickle
import os
from django.conf import settings
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64



def build_random_forest_classifier(df: pd.DataFrame, feature_cols: list, target_cols: list,  model_params: dict) -> RandomForestClassifier:
    model_params.pop('model_type', None)
    model = RandomForestClassifier(**model_params)
    model.fit(df[feature_cols], df[target_cols])

    return model


def build_logistic_regression(df: pd.DataFrame, feature_cols: list, target_cols: list,  model_params: dict) -> LogisticRegression:
    model_params.pop('model_type', None)

    model = LogisticRegression(**model_params)

    model.fit(df[feature_cols], df[target_cols])


    return model

def build_svm(df: pd.DataFrame, feature_cols: list, target_cols: list,  model_params: dict) -> SVC:
    model_params.pop('model_type', None)
    model = LogisticRegression(**model_params)
    model.fit(df[feature_cols], df[target_cols])

    return model


MODELS_TO_BUILD = {'logistic_regression': build_logistic_regression, 'svm': build_svm, 'random_forest': build_random_forest_classifier}


def build_ml_model(file_path: str, config_path: str, model_dir: str, selected_model: str, training_config: dict) -> dict:
    df = read_work_file(file_path, config_path)
    feature_cols = training_config['features']
    target_col = training_config['target']
    
    metrics = {}
    
    if training_config['test_options']['test_split']:
        X_train, X_test, y_train, y_test = train_test_split(
            df[feature_cols], df[target_col], 
            test_size=training_config['test_options']['test_size'],
            random_state=training_config['test_options']['random_state']
        )
        
        model = MODELS_TO_BUILD[selected_model](
            pd.concat([X_train, y_train], axis=1),
            feature_cols,
            target_col,
            training_config['model_params']
        )
        
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None


        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        if y_proba is not None:
            metrics['roc_auc'] = roc_auc_score(y_test, y_proba)
            
            roc_curve = RocCurveDisplay.from_estimator(model, X_test, y_test)
            plt.close() 

            roc_buffer = BytesIO()
            roc_curve.plot()
            plt.savefig(roc_buffer, format='png')
            plt.close()
            roc_buffer.seek(0)
            metrics['roc_curve'] = base64.b64encode(roc_buffer.getvalue()).decode('utf-8')
        
        
        model_path = os.path.join(model_dir, f'{selected_model}_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        metrics['model_path'] = model_path
        
    return metrics




