import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats.mstats import winsorize
import core.modules.fstream_operations as fstream
from .pipeline_saver import PipelineSaver

def mode(array: np.ndarray):
    return stats.mode(array).mode


def zscore_strategy(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver, threshold=3, uniq_threshold=20) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    for column in columns:
        if len(df[column].unique()) < uniq_threshold:
            continue
        z_scores = np.abs(stats.zscore(df[column]))
        mask &= (z_scores <= threshold)

    return df[mask].reset_index(drop=True)
        

def iqr_strategy(df: pd.DataFrame, columns: str,  pipeline_saver: PipelineSaver, uniq_threshold=20) -> pd.DataFrame:
    for column in columns:
        if len(df[column].unique()) < uniq_threshold:
            continue
        lower_bound, upper_bound = count_lower_upper_iqr_bound(df[column])
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

    return df.reset_index(drop=True)


def winsorize_strategy(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver,  limits=[0.05, 0.05], uniq_threshold=20) -> pd.DataFrame:
    for column in columns:
        if len(df[column].unique()) < uniq_threshold:
            continue
        df[column] = winsorize(df[column], limits=limits)
    return df


def cap_strategy(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver, uniq_threshold=20, method: str = 'iqr') -> pd.DataFrame:
    for column in columns:
        if len(df[column].unique()) < uniq_threshold:
            continue 
        if method == 'iqr':
            lower_cap, upper_cap = count_lower_upper_iqr_bound(df[column])
        else:
            lower_cap = df[column].quantile(0.05)
            upper_cap = df[column].quantile(0.95)

        df[column] = df[column].clip(lower=lower_cap, upper=upper_cap)

    return df


def minmax_scaling(df: pd.DataFrame, columns: list,  pipeline_saver: PipelineSaver, feature_range: tuple = (-1, 1)) -> pd.DataFrame:
    target_min, target_max = feature_range
    for column in columns:
        x_min = df[column].min()
        x_max = df[column].max()
        if x_min == x_max:
            df[column] = (target_max + target_min) / 2
        df[column] = (df[column] - x_min) / (x_max - x_min) 
        df[column] = df[column] * (target_max - target_min) + target_min

    return df


def standart_scaling(df: pd.DataFrame, columns: list,  pipeline_saver: PipelineSaver) -> pd.DataFrame:
    for column in columns:
        u = df[column].mean()
        s = df[column].std()
        if s == 0:
            continue
        df[column] = (df[column] - u) / s

    return df


def robust_scaling(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver) -> pd.DataFrame:
    for column in columns:
        median = df[column].median()
        q1, q3 = df[column].quantile(0.25), df[column].quantile(0.75)
        if q1 == q3:
            continue
        df[column] = (df[column] - median) / (q3 - q1) 

    return df
    


def log_transform(df: pd.DataFrame, columns: list,  pipeline_saver: PipelineSaver, base: str = 'e') -> pd.DataFrame:
    log_func = LOG_BASES[base]
    for column in columns:
        min_val = df[column].min()
        if min_val <= 0:
            offset = 1 - min_val 
            df[column] = log_func(df[column] + offset)
        else:
            df[column] = log_func(df[column])

    return df

LOG_BASES = {'e': np.log, '10': np.log10, '2': np.log2}
MISSING_STRATEGY = {'mean': np.mean, 'median': np.median, 'mode': mode}
OUTLIER_STRATEGIES = {'zscore': zscore_strategy, 'iqr': iqr_strategy,
                       'winsorize': winsorize_strategy, 'cap': cap_strategy}
NORMALIZTION_STRATEGY = {'minmax': minmax_scaling, 'standart': standart_scaling,
                         'robust': robust_scaling, 'log': log_transform}


def fill_miss(df: pd.DataFrame, columns: list, missing_strategy: str, constant: float):
    if missing_strategy == 'constant':
        df[columns] = df[columns].fillna(constant)
        return df.reset_index(drop=True)

    if missing_strategy == 'drop':
        df = df.dropna(subset=columns)
        return df.reset_index(drop=True)

    func_to_miss = MISSING_STRATEGY[missing_strategy]
    for column in columns:
        df[column] = df[column].fillna(func_to_miss(df[column].dropna().values))
        
    return df.reset_index(drop=True)

def process_num(path_to_file: str, path_to_config: str, columns_to_process: list, 
                missing_strategy: str, missing_constant: float, outlier_strategy: str, normalization_strategy: str, is_create_pipeline=True):
    
    pipeline_saver = PipelineSaver(is_create_pipeline)
    pipeline_saver.start_step()
    df = fstream.read_work_file(path_to_file, path_to_config)

    df = fill_miss(df, columns_to_process, missing_strategy, missing_constant)

    if outlier_strategy:
        df = OUTLIER_STRATEGIES[outlier_strategy](df, columns_to_process)
    
    if normalization_strategy:
        df = NORMALIZTION_STRATEGY[normalization_strategy](df, columns_to_process)
    fstream.save_work_file(df, path_to_file, path_to_config)

    
def count_lower_upper_iqr_bound(column: pd.Series) -> list:
        q1 = column.quantile(0.25)
        q3 = column.quantile(0.75)
        iqr = q3 - q1
        return q1 - 1.5 * iqr, q3 + 1.5 * iqr