import pandas as pd
import core.modules.fstream_operations as fstream_operations
import numpy as np
import xlrd
import csv

READ_FUNCTIONS = {
    'read_csv': pd.read_csv,
    'read_xlsx': pd.read_excel
}

def read_data_file(file_path: str) -> tuple:
    if file_path.endswith('.xlsx'):
        read_function_name = 'read_xlsx'
        param_grid = [
            {},  
            {'header': 0},
            {'header': None},
            {'skiprows': 1},
        ]
        # sheet = xlrd.open_workbook(file_path).sheet_by_index(0) 
  
        # col = csv.writer(open("T.csv",  
        #                     'w',  
        #                     newline="")) 
        
        # for row in range(sheet.nrows): 
        #     col.writerow(sheet.row_values(row)) 
        
        # df = pd.DataFrame(pd.read_csv("T.csv"))
    else:
        read_function_name = 'read_csv'
        param_grid = [
            {'sep': ','},
            {},
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
        path = file_path[: file_path.rfind('\\')] + 'config.json'
        param_grid[params_index].update({'read_function': read_function_name})
        if fstream_operations.write_json(param_grid[params_index], path):
            return (path, None)

    return (None, ['Ошибка при попытке сохранения, попробуйте ещё раз'])
        

def get_preview_data(path_to_file: str, path_to_config: str) -> dict:

    df = fstream_operations.read_work_file(path_to_file, path_to_config)
    return {'data_preview': df.head(7).to_html(classes='table table-striped'),
        'columns': df.columns.tolist(),
        'shape': df.shape, 
        'num_cols': df.select_dtypes(include=np.number).columns.tolist(),
        'obj_cols': df.select_dtypes(include=np.object_).columns.tolist()} 


    