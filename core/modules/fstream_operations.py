import os
import json
from django.core.files.storage import FileSystemStorage
from tempfile import mkdtemp


def delete_files(file_pathes: tuple) -> bool:
    try:
        for file_path in file_pathes:
            if os.path.exists(file_path):
                os.remove(file_path)
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
    
def json_load( path: str) -> bool:
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