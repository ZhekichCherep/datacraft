from core.modules.fstream_operations import write_json, json_load


class PipelineSaver:
    '''Класс для сохранения пайплайна обучения будет записывать в json следующую структуру:
    {column1: {
        process1_name: process1_params, 
        process2_name: process2_params}
    column 2}'''
    
    def __init__(self, is_create: bool, path: str):
        self.steps = {}
        self.path = path
        self.is_create = is_create
        self.load_steps()


    def update_column_processes(self, column: str, process: str, params: dict={}) -> None:
        if column not in self.steps.keys():
            self.steps[column] = {process: params}
        else:
            self.steps[column].update({process: params})
        
    def get_column_process(self, column: str, process: str):
        if column not in self.steps.keys() or process not in self.steps[column].keys():
            return None
        return self.steps[column][process]
    
    def save_steps(self):
        write_json(self.steps, self.path)
    
    def load_steps(self):
        self.steps = json_load(self.path)
        if not self.steps:
            self.steps = {}







