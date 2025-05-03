import pandas as pd
import numpy as np
from scipy import stats
import core.modules.fstream_operations as fstream

def mode(array: np.ndarray):
    return stats.mode(array).mode

def zscore_strategy(df: pd.DataFrame, columns: list, threshold=3) -> None:
    z_scores = np.abs(stats.zscore(df[columns]))
    outliers_mask = (z_scores > threshold).any(axis=1)
    df = df[~outliers_mask]
        

def iqr_strategy(df: pd.DataFrame, columns: str) -> None:
    for column in columns:
        pass

def winsorize_strategy(df, columns) -> None:
    for column in columns:
        pass

def cap_strategy(df, columns) -> None:
    for columns in columns:
        pass


MISSING_STRATEGY = {'mean': np.mean, 'median': np.median, 'mode': mode}
OUTLIER_STRATEGIES = {'zscore': zscore_strategy, 'iqr': iqr_strategy,
                       'winsorize': winsorize_strategy, 'cap': cap_strategy}
num_preprocessing = {}

def fill_miss(df: pd.DataFrame, columns: list, missing_strategy: str, constant: float):
    if missing_strategy == 'constant':
        df[columns] = df[columns].fillna(constant)

    elif missing_strategy == 'drop':
        df = df.dropna(subset=columns)

    else:
        func_to_miss = MISSING_STRATEGY[missing_strategy]
        for column in columns:
            df[column] = df[column].fillna(func_to_miss(df[column].dropna().values))
    return df

def process_num(path_to_file: str, path_to_config: str, columns_to_process: list, 
                missing_strategy: str, missing_constant: float, outlier_strategy: str, normalization_strategy: str):
    
    df = fstream.read_work_file(path_to_file, path_to_config)
    df.replace('', np.nan, inplace=True)
    df = fill_miss(df, columns_to_process, missing_strategy, missing_constant)

    if outlier_strategy:
        OUTLIER_STRATEGIES[outlier_strategy](df, columns_to_process)
    
    fstream.save_work_file(df, path_to_file, path_to_config)

    
