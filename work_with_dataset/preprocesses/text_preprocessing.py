import pandas as pd
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from .pipeline_saver import PipelineSaver
import core.modules.fstream_operations as fstream

class TextPreprocessor:
    def __init__(self, pipeline_saver: PipelineSaver):
        self.pipeline_saver = pipeline_saver
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
    
    def lowercase(self, text: str) -> str:
        return text.lower()
    
    def remove_punctuation(self, text: str) -> str:
        return re.sub(r'[^\w\s]', '', text)
    
    def remove_stopwords(self, text: str) -> str:
        return ' '.join([word for word in text.split() if word not in self.stop_words])
    
    def apply_stemming(self, text: str) -> str:
        return ' '.join([self.stemmer.stem(word) for word in text.split()])
    
    def process_text(self, df: pd.DataFrame, columns: list, params: dict) -> pd.DataFrame:
        for column in columns:
            if self.pipeline_saver.is_create:
                self.pipeline_saver.update_column_processes(column, 'text_processing', params)
            
            if params.get('lowercase', False):
                df[column] = df[column].astype(str).apply(self.lowercase)
            
            if params.get('remove_punct', False):
                df[column] = df[column].astype(str).apply(self.remove_punctuation)
            
            if params.get('remove_stopwords', False):
                df[column] = df[column].astype(str).apply(self.remove_stopwords)
            
            if params.get('stemming', False):
                df[column] = df[column].astype(str).apply(self.apply_stemming)
        
        return df

def process_text_data(
    path_to_file: str,
    path_to_config: str,
    path_to_pipeline: str,
    columns_to_process: list,
    lowercase: bool = False,
    remove_punct: bool = False,
    remove_stopwords: bool = False,
    stemming: bool = False,
    is_create_pipeline: bool = True
) -> str:

    
    pipeline_saver = PipelineSaver(is_create_pipeline, path_to_pipeline)
    preprocessor = TextPreprocessor(pipeline_saver)
    
    df = fstream.read_work_file(path_to_file, path_to_config)
    
    text_params = {
        'lowercase': lowercase,
        'remove_punct': remove_punct,
        'remove_stopwords': remove_stopwords,
        'stemming': stemming
    }
    
    df = preprocessor.process_text(df, columns_to_process, text_params)
    
    pipeline_saver.save_steps()
    fstream.save_work_file(df, path_to_file, path_to_config)
    