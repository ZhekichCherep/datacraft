import os
import json
from django.core.files.storage import FileSystemStorage
from tempfile import mkdtemp
import pandas as pd

READ_FUNCTIONS = {
    'read_csv': pd.read_csv,
    'read_xlsx': pd.read_excel
}

def delete_files(file_pathes: tuple) -> bool:
    try:
        for file_path in file_pathes:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(file_path)
        return True
    except:
        return False

def write_json(dct: dict, path: str) -> None:
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(dct, f, ensure_ascii=False)
        return True
    except:
        return False
    
def json_load(path: str) -> dict:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return False
    

def save_to_temp_dir(file) -> str:
    temp_dir = mkdtemp()
    fs = FileSystemStorage(location=temp_dir)
    file_name = fs.save(file.name, file)
    file_path = fs.path(file_name)
    return file_path

def read_work_file(path_to_file: str, path_to_config: str) -> pd.DataFrame:
    params = json_load(path_to_config)
    read_function = READ_FUNCTIONS[params.pop('read_function')]
    df = read_function(path_to_file, **params)
    return df

def save_work_file(df: pd.DataFrame, path, path_to_config: str ) -> None:
    params = json_load(path_to_config)
    read_function = params.pop('read_function')
    delete_files((path))

    if read_function == 'read_csv':
        df.to_csv(path, **params, index=False)

    else: 
        df.to_excel(path, **params, index=False)
