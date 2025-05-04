class PipelineSaver:
    '''Класс для сохранения пайплайна обучения будет записывать в json следующую структуру:
    [{0:{
        column_name: {
            name_preprocess: [process params]} #like median, std 
            }}]'''
    
    def __init__(self, is_create):
        
        self.steps = []
        self.current_step = 0
        self.is_create = is_create

    def start_step(self):
        self.steps.append({self.current_step: {}})

    def end_step(self):
        self.current_step += 1


