import pandas as pd
import chardet
import json
import upload_file.modules.fstream_operations as fstream_operations
import numpy as np

READ_FUNCTIONS = {
    'read_csv': pd.read_csv,
    'read_xlsx': pd.read_excel
}

def read_data_file(file_path: str) -> tuple:
    '''Возвращает путь к файлу с параметрами для парсинга файла, функции для его чтения
    и список ошибок'''
    if file_path.endswith('.xlsx'):
        read_function_name = 'read_xlsx'
        param_grid = [
            {},  
            {'header': 0},
            {'header': None},
            {'skiprows': 1},
        ]
    else:
        read_function_name = 'read_csv'
        param_grid = [
            {},  
            {'sep': ','},
            {'sep': ';'},
            {'sep': '; '},
            {'sep': '\t'},
            {'header': 0},
            {'header': None},
            {'skiprows': 1},
            {'encoding': 'utf-8'},
            {'encoding': 'latin-1'},
        ]
    
    max_width = 0
    params_index = -1
    read_function = READ_FUNCTIONS[read_function_name]
    for i, params in enumerate(param_grid):
        try:
            df = read_function(file_path, **params)
            if df.shape[1] > max_width:
                params_index = i
                max_width = df.shape[1]
                
        except Exception as e:
            raise ValueError(['Ошибка при чтении файла ' + file_path])

    if params_index != -1:
        path = file_path[: file_path.rfind('/')] + 'config.json'
        param_grid[params_index].update({'read_function': read_function_name})
        if fstream_operations.write_json(param_grid[params_index], path):
            return (path, None)

    return (None, ['Ошибка при попытке сохранения, попробуйте ещё раз'])
        
    
def try_to_numeric(df:pd.DataFrame) -> pd.DataFrame:
    for column in df.columns.to_list():
        pass
    return df

def get_preview_data(path_to_file: str, path_to_config: str) -> dict:
    params = {}
    if fstream_operations.json_load(params, path_to_config):
        # read_function = READ_FUNCTIONS[params.pop('read_function')]
        read_function = pd.read_csv
        df = read_function(path_to_file, **params)
        return {'data_preview': df.head().to_html(classes='table table-striped'),
            'columns': df.columns.tolist(),
            'shape': df.shape} 
    
    return None

def get_data_columns(path_to_file: str, path_to_config: str, is_num_columns=True) -> list:
    params = {}
    if fstream_operations.json_load(params, path_to_config):
        # read_function = READ_FUNCTIONS[params.pop('read_function')]
        read_function = pd.read_csv
        df = read_function(path_to_file, **params)
        if is_num_columns:
            return df.select_dtypes(include=np.number).columns.tolist()
        return df.select_dtypes(include=np.object_).columns.tolist() 
    