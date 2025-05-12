import pandas as pd
import re
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from .pipeline_saver import PipelineSaver
import core.modules.fstream_operations as fstream
from .pipeline_saver import PipelineSaver
from .num_preprocessing import fill_constant, fill_mode, drop_misses

STOP_WORDS = set(stopwords.words('english'))
STEMMER = PorterStemmer()


def to_lowercase(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            pipeline_saver.update_column_processes(column, 'to_lowercase')
        df[column] = df[column].apply(lambda string: string.lower())

        return df
    
    for column in columns:
        df[column] = df[column].apply(lambda string: string.lower())

    return df



def remove_punct(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            pipeline_saver.update_column_processes(column, 'remove_punct')
        df[column] = df[column].apply(lambda string: re.sub(r'[^\w\s]', '', string))

        return df
    
    for column in columns:
        df[column] = df[column].apply(lambda string: re.sub(r'[^\w\s]', '', string))

    return df



def remove_stopwords(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            pipeline_saver.update_column_processes(column, 'remove_stopwords')
            df[column] = df[column].apply(lambda string: ' '.join([word for word in string.split() if word not in STOP_WORDS]))

        return df
    
    for column in columns:
        df[column] = df[column].apply(lambda string: ' '.join([word for word in string.split() if word not in STOP_WORDS]))

    return df


def apply_stemming(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            pipeline_saver.update_column_processes(column, 'apply_stemming')
            df[column] = df[column].apply(lambda string: ' '.join([STEMMER.stem(word) for word in string.split()]))

        return df
    
    for column in columns:
        df[column] = df[column].apply(lambda string: ' '.join([word for word in string.split() if word not in STOP_WORDS]))

    return df

 
import pandas as pd
from sklearn.preprocessing import (
    OneHotEncoder, 
    OrdinalEncoder, 
    TargetEncoder
)
from sklearn.model_selection import train_test_split


def onehot_encode(df: pd.DataFrame, columns: list, pipeline_saver: PipelineSaver) -> pd.DataFrame:
    if pipeline_saver.is_create:
        for column in columns:
            encoder = OneHotEncoder(sparse_output=False)
            encoded = encoder.fit_transform(df[[column]])
            encoded_df = pd.DataFrame(encoded, columns=[f"{column}_{cat}" for cat in encoder.categories_[0]])

            pipeline_saver.update_column_processes(column, 'onehot', {'categories': encoder.categories_[0].tolist()})
            df = pd.concat([df.drop(columns=[column]), encoded_df], axis=1)

        return df
    
    for column in columns:
        categories = pipeline_saver.get_column_process(column, 'onehot')
        for cat in categories['categories']:
            df[f"{column}_{cat}"] = (df[column] == cat).astype(int)
        df = df.drop(columns=[column])


    return df



def encode_categorical(
    df: pd.DataFrame,
    columns: list,
    pipeline_saver: PipelineSaver,
    strategy: str = 'onehot',
    target: str = None,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Кодирование категориальных переменных
    """
    if not columns:
        return df
    
    if pipeline_saver.is_create:
        for column in columns:
            if strategy == 'onehot':
                encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
                encoded = encoder.fit_transform(df[[column]])
                encoded_df = pd.DataFrame(
                    encoded,
                    columns=[f"{column}_{cat}" for cat in encoder.categories_[0]]
                )
                pipeline_saver.update_column_processes(
                    column,
                    'categorical_encoding',
                    {'strategy': 'onehot', 'categories': encoder.categories_[0].tolist()}
                )
                df = pd.concat([df.drop(columns=[column]), encoded_df], axis=1)
            
            elif strategy == 'ordinal':
                encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
                df[column] = encoder.fit_transform(df[[column]])
                pipeline_saver.update_column_processes(
                    column,
                    'categorical_encoding',
                    {'strategy': 'ordinal', 'categories': encoder.categories_[0].tolist()}
                )
            
            elif strategy == 'target':
                if not target:
                    raise ValueError("Target column must be specified for target encoding")
                
                encoder = TargetEncoder(random_state=random_state)
                X_train, X_test, y_train, _ = train_test_split(
                    df[column], df[target],
                    test_size=0.2,
                    random_state=random_state
                )
                encoder.fit(X_train, y_train)
                df[column] = encoder.transform(df[[column]])
                pipeline_saver.update_column_processes(
                    column,
                    'categorical_encoding',
                    {'strategy': 'target', 'target': target, 'encoder_params': encoder.get_params()}
                )
            
            elif strategy == 'frequency':
                freq_map = df[column].value_counts(normalize=True).to_dict()
                df[column] = df[column].map(freq_map)
                pipeline_saver.update_column_processes(
                    column,
                    'categorical_encoding',
                    {'strategy': 'frequency', 'freq_map': freq_map}
                )
    
    else:
        for column in columns:
            params = pipeline_saver.get_column_process(column, 'categorical_encoding')
            if params:
                if params['strategy'] == 'onehot':
                    categories = params['categories']
                    for cat in categories:
                        df[f"{column}_{cat}"] = (df[column] == cat).astype(int)
                    df = df.drop(columns=[column])
                
                elif params['strategy'] == 'ordinal':
                    cat_map = {cat: i for i, cat in enumerate(params['categories'])}
                    df[column] = df[column].map(cat_map).fillna(-1)
                
                elif params['strategy'] == 'target':
                    encoder = TargetEncoder(**params['encoder_params'])
                    df[column] = encoder.transform(df[[column]])
                
                elif params['strategy'] == 'frequency':
                    df[column] = df[column].map(params['freq_map'])
    
    return df

CAT_PROCESSES = {'lowercase': to_lowercase, 'remove_punct': remove_punct, 'remove_stopwords': remove_stopwords, 
                 'stemming': apply_stemming, 'onehot': onehot_encode, 'mode': fill_mode, 'constant': fill_constant,
                 'drop': drop_misses}

def process_text_data(path_to_file: str, path_to_config: str, path_to_pipeline: str, categorical_cols: list, is_create_pipeline: bool,
                 missing_strategy: str = 'mode',  missing_constant: float = None, categorical_strategy: str = 'onehot',
                 *params_to_text) -> None:


    pipeline_saver = PipelineSaver(is_create_pipeline, path_to_pipeline)
    df = fstream.read_work_file(path_to_file, path_to_config)
    
    if missing_strategy == 'constant':
        fill_constant(df, categorical_cols, pipeline_saver, missing_constant)
    else:
        df = CAT_PROCESSES[missing_strategy](df, categorical_cols, pipeline_saver)

    if categorical_strategy:
        df = CAT_PROCESSES[categorical_strategy](df, categorical_cols, pipeline_saver)
    
    pipeline_saver.save_steps()
    fstream.save_work_file(df, path_to_file, path_to_config)
