import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats.mstats import winsorize
import core.modules.fstream_operations as fstream
from .pipeline_saver import PipelineSaver

def mode(array: np.ndarray):
    return stats.mode(array).mode


def zscore_strategy(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver, threshold=3, uniq_threshold=20) -> pd.DataFrame:
    if pipeline_saver.is_create:
        mask = pd.Series(True, index=df.index)
        stats_dict = {}
        
        for column in columns:
            if len(df[column].unique()) < uniq_threshold:
                continue
                
            mean = df[column].mean()
            std = df[column].std()
            pipeline_saver.update_column_processes(column, 'zscore', {'mean': mean, 'std': std})
            z_scores = np.abs((df[column] - mean) / std)
            mask &= (z_scores <= threshold)
                
        return df[mask].reset_index(drop=True)
    
    mask = pd.Series(True, index=df.index)
    
    for column in columns:
        stats_dict = pipeline_saver.get_column_process(column, 'zscore')
        if stats_dict:
            mean = stats_dict['mean']
            std = stats_dict['std']
            
            z_scores = np.abs((df[column] - mean) / std)
            mask &= (z_scores <= threshold)
    
    return df[mask].reset_index(drop=True)
    
        

def iqr_strategy(df: pd.DataFrame, columns: str,  pipeline_saver: PipelineSaver, uniq_threshold=20) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            if len(df[column].unique()) < uniq_threshold:
                continue
            lower_bound, upper_bound = count_lower_upper_iqr_bound(df[column])
            pipeline_saver.update_column_processes(column, 'iqr', {'lower_bound': lower_bound, 'upper_bound': upper_bound})
            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        return df.reset_index(drop=True)
    
    for column in columns:
        stats_dict = pipeline_saver.get_column_process(column, 'iqr')
        if stats_dict:
            df = df[(df[column] >= stats_dict['lower_bound']) & (df[column] <= 'upper_bound')]

    return df.reset_index(drop=True)



def winsorize_strategy(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver,  limits=[0.05, 0.05], uniq_threshold=20) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            if len(df[column].unique()) < uniq_threshold:
                continue
            lower_bound = df[column].quantile(0.05)
            upper_bound = df[column].quantile(0.95)
            df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
            pipeline_saver.update_column_processes(column, 'winsorize', {'lower_bound': lower_bound, 'upper_bound': upper_bound})

        return df
    
    for column in columns:
        stats_dict = pipeline_saver.get_column_process(column, 'winsorize')
        if stats_dict:
            df[column] = df[column].clip(lower=stats_dict['lower_bound'], upper=stats_dict['upper_bound'])

    return df

    
def cap_strategy(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver, uniq_threshold=20, method: str = 'iqr') -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            if len(df[column].unique()) < uniq_threshold:
                continue 
            if method == 'iqr':
                lower_cap, upper_cap = count_lower_upper_iqr_bound(df[column])
            else:
                lower_cap = df[column].quantile(0.05)
                upper_cap = df[column].quantile(0.95)

            df[column] = df[column].clip(lower=lower_cap, upper=upper_cap)
            pipeline_saver.update_column_processes(column, 'cap', {'lower_cap': lower_cap, 'upper_cap': upper_cap})

        return df
    
    for column in columns:
        params = pipeline_saver.get_column_process(column, 'cap')
        if params:
            df[column] = df[column].clip(lower=params['lower_cap'], upper_cap=params['upper_cap'])

    return df



def minmax_scaling(df: pd.DataFrame, columns: list,  pipeline_saver: PipelineSaver, feature_range: tuple = (0, 1)) -> pd.DataFrame:
    if pipeline_saver.is_create:
        target_min, target_max = feature_range
        for column in columns:
            x_min = df[column].min()
            x_max = df[column].max()
            if x_min == x_max:
                df[column] = (target_max + target_min) / 2
                continue

            df[column] = (df[column] - x_min) / (x_max - x_min) 
            df[column] = df[column] * (target_max - target_min) + target_min
            pipeline_saver.update_column_processes(column, 'minmax', {'feature_range': feature_range, 'max': x_max, 'min': x_min})

        return df

    for column in columns:
        params = pipeline_saver.get_column_process(column, 'minmax')
        if params:
            target_min, target_max = params['feature_range']
            x_min, x_max = params['min'], params['max']
            df[column] = (df[column] - x_min) / (x_max - x_min) 
            df[column] = df[column] * (target_max - target_min) + target_min
        
    return df


def standart_scaling(df: pd.DataFrame, columns: list,  pipeline_saver: PipelineSaver) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            u = df[column].mean()
            s = df[column].std()
            if s == 0:
                continue
            df[column] = (df[column] - u) / s
            pipeline_saver.update_column_processes(column, 'standart', {'mean': u, 'std': s})

        return df
    
    for column in columns:
        params = pipeline_saver.get_column_process(column, 'standart')
        if params:
            df[column] = (df[column] - params['mean']) / params['std']

    return df


def robust_scaling(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            median = df[column].median()
            q1, q3 = df[column].quantile(0.25), df[column].quantile(0.75)
            if q1 == q3:
                continue
            df[column] = (df[column] - median) / (q3 - q1) 
            pipeline_saver.update_column_processes(column, 'robust', {'median': median, 'iqr': q3 - q1})

        return df
    
    for column in columns:
        params = pipeline_saver.get_column_process(column, 'robust')
        if params:
            df[column] = (df[column] - params['median']) / params['iqr']
        
    return df
    


def log_transform(df: pd.DataFrame, columns: list,  pipeline_saver: PipelineSaver, base: str = 'e') -> pd.DataFrame:
    if pipeline_saver.is_create:
        log_func = LOG_BASES[base]
        for column in columns:
            min_val = df[column].min()
            offset = 0
            if min_val <= 0:
                offset = 1 - min_val 
                
            df[column] = log_func(df[column] + offset)
            pipeline_saver.update_column_processes(column, 'log', {'base': base, 'offset': offset})
        return df
    
    for column in columns:
        params = pipeline_saver.get_column_process(column, 'log')
        if params:
            log_func = LOG_BASES[params['base']]
            df[column] = log_func(df[column] + offset)

    return df


def fill_constant(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver, constant=0) -> pd.DataFrame:
    if pipeline_saver.is_create:
        df[columns] = df[columns].fillna(constant)
        for column in columns:
            pipeline_saver.update_column_processes(column, 'constant', {'constant': constant})

        return df
    
    for column in columns:
        constant = pipeline_saver.get_column_process(column, 'constant')
        if constant:
            df[column] = df[column].fillna(constant['constant'])
    
    return df


def drop_misses(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver)-> pd.DataFrame:
    if pipeline_saver.is_create:
        df = df.dropna(subset=columns)
        for column in columns:
            pipeline_saver.update_column_processes(column, 'drop', {1})

        return df.reset_index(drop=True)
    
    for column in columns:
        drop = pipeline_saver.get_column_process(column, 'drop')
        if drop:
            df[column] = df[column].dropna()

    return df.reset_index(drop=True)

def fill_median(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver)-> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            value_to_miss = np.median(df[column].dropna().values)
            df[column] = df[column].fillna(value_to_miss)
            pipeline_saver.update_column_processes(column, 'median', {'value_to_miss': value_to_miss})
            
        return df
    
    for column in columns:
            miss_params = pipeline_saver.get_column_process(column, 'median')
            if miss_params:
                df[column] = df[column].fillna(miss_params['value_to_miss'])

    return df

def fill_mode(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver)-> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            value_to_miss = mode(df[column].dropna().values)
            df[column] = df[column].fillna(value_to_miss)
            pipeline_saver.update_column_processes(column, 'mode', {'value_to_miss': value_to_miss})
            
        return df
    
    for column in columns:
            miss_params = pipeline_saver.get_column_process(column, 'mode')
            if miss_params:
                df[column] = df[column].fillna(miss_params['value_to_miss'])

    return df


def fill_mean(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver)-> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            value_to_miss = np.mean(df[column].dropna().values)
            df[column] = df[column].fillna(value_to_miss)
            pipeline_saver.update_column_processes(column, 'mean', {'value_to_miss': value_to_miss})
            
        return df
    
    for column in columns:
            miss_params = pipeline_saver.get_column_process(column, 'mean')
            if miss_params:
                df[column] = df[column].fillna(miss_params['value_to_miss'])

    return df


LOG_BASES = {'e': np.log, '10': np.log10, '2': np.log2}
NUM_COLS_STRATEGY = {'minmax': minmax_scaling, 'standard': standart_scaling,
                     'robust': robust_scaling, 'log': log_transform, 'mean': fill_mean, 'median': fill_median,
                     'mode': fill_mode, 'drop': drop_misses, 'zscore': zscore_strategy, 'iqr': iqr_strategy,
                     'winsorize': winsorize_strategy, 'cap': cap_strategy, 'constant': fill_constant}
 

def process_num(path_to_file: str, path_to_config: str, path_to_pipeline: str, columns_to_process: list, 
                missing_strategy: str, missing_constant: float, outlier_strategy: str, 
                normalization_strategy: str, is_create_pipeline=True) -> str:
    
    pipeline_saver = PipelineSaver(is_create_pipeline, path_to_pipeline)

    df = fstream.read_work_file(path_to_file, path_to_config)

    if missing_strategy:
        if missing_strategy == 'constant':
            df = fill_constant(df, columns_to_process, pipeline_saver, missing_constant)
        else:
            df = NUM_COLS_STRATEGY[missing_strategy](df, columns_to_process, pipeline_saver)

    if outlier_strategy:
        df = NUM_COLS_STRATEGY[outlier_strategy](df, columns_to_process, pipeline_saver)
    
    if normalization_strategy:
        df = NUM_COLS_STRATEGY[normalization_strategy](df, columns_to_process, pipeline_saver)

    pipeline_saver.save_steps()
    fstream.save_work_file(df, path_to_file, path_to_config)


    
def count_lower_upper_iqr_bound(column: pd.Series) -> list:
        q1 = column.quantile(0.25)
        q3 = column.quantile(0.75)
        iqr = q3 - q1
        return q1 - 1.5 * iqr, q3 + 1.5 * iqr