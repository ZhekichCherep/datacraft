import pandas as pd
import chardet
import json

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
                max_width = df.shape[2]
                
        except Exception as e:
            raise ValueError(['Ошибка при чтении файла ' + file_path[: file_path.rfind('/')]])

    if params_index != -1:
        path = file_path[: file_path.rfind('/')] + 'config.json'
        try:
            with open(path, 'w', encoding='utf-8') as f:
                param_grid[params_index].update({'read_function': read_function_name})
                json.dump(param_grid[params_index], f, ensure_ascii=False)
        except:
            return (None, ['Ошибка при попытке сохранения, попробуйте ещё раз'])
        
        return (path, None)
    


def get_preview_data(path_to_file, path_to_config) -> dict:
    params = ['ioa']
    try:
        with open(path_to_config, 'r', encoding='utf-8') as f:
            params = json.load(f)
    except:
        raise ValueError(f'Не удалось прочитать файл {path_to_config} с парамтрами')
    
    read_function = READ_FUNCTIONS[params.pop('read_function')]
    df = read_function(path_to_file, **params)
    return {'data_preview': df.head().to_html(classes='table table-striped'),
            'columns': df.columns.tolist(),
            'shape': df.shape} 