import os
import json

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
    