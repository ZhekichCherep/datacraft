from django.shortcuts import render, redirect
import os
from upload_file.views import cleanup_session
from upload_file.views import (COPIED_FILE_PATH, CONFIG_PATH, NUM_COLS, ML_MODELS_DIR,
                               SHAPE, FILE_NAME, OBJ_COLS, PIPELINE_PATH, UPLOADED_FILE_PATH)
from .preprocesses.text_preprocessing import process_text_data
from .preprocesses.num_preprocessing import process_num
from django.http import FileResponse, HttpResponse
from work_with_dataset.preprocesses import pipeline_apply
from .build_apply_ml_models.build_ml_model import build_ml_model

def num_preprocessings(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH, NUM_COLS, SHAPE]):
        cleanup_session(request)
        return redirect('upload_file')
    
    if request.method == 'POST':
        
        selected_columns = request.POST.getlist('selected_columns')   
        missing_strategy = request.POST.get('missing_strategy')
        missing_constant = request.POST.get('missing_constant')
        outlier_strategy = request.POST.get('outlier_strategy')
        normalization_strategy = request.POST.get('normalization_strategy')
        process_num(request.session[COPIED_FILE_PATH], request.session[CONFIG_PATH], request.session[PIPELINE_PATH],
                                                     selected_columns, missing_strategy, missing_constant, outlier_strategy, normalization_strategy)
        
        return redirect('action_choice')

    try:
        context = {
            'columns': request.session[NUM_COLS],
            'shape': request.session[SHAPE],
            'file_name': request.session.get(FILE_NAME, '')
        }
        return render(request, 'work_with_dataset/num_preprocessing.html', context)
    except Exception as e:
        cleanup_session(request)
        return render(request, 'upload_file/index.html', {'errors': [str(e)]})
    

def text_preprocessing(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH, NUM_COLS, SHAPE]):
        cleanup_session(request)
        return redirect('upload_file')
    
    if request.method == 'POST':
        
        selected_columns = request.POST.getlist('selected_columns')   
        missing_strategy = request.POST.get('missing_strategy')
        missing_constant = request.POST.get('missing_constant')
        encode_strategy = request.POST.get('categorical_strategy')
        lowercase = "lowercase" if request.POST.get('text_lowercase') else None
        remove_punct = "remove_punct" if request.POST.get('text_remove_punct') else None
        remove_stopwords = "remove_stopwords" if request.POST.get('text_remove_stopwords') else None
        stemming = "stemming" if request.POST.get('text_stemming') else None
        process_text_data(request.session[COPIED_FILE_PATH], request.session[CONFIG_PATH], request.session[PIPELINE_PATH], 
                          selected_columns, True, missing_strategy, missing_constant, encode_strategy, 
                          *[lowercase, remove_punct, remove_stopwords, remove_punct, stemming])
        
        return redirect('action_choice')

    context = {
        'columns': request.session[OBJ_COLS],
        'shape': request.session[SHAPE],
        'file_name': request.session.get(FILE_NAME, '')
    }
    return render(request, 'work_with_dataset/text_preprocessing.html', context)


def results_page(request):
    if not all(key in request.session for key in ['metrics', 'model_path']):
        return redirect('upload_file')
    
    metrics = request.session['metrics']
    model_path = request.session['model_path']
    
    context = {
        'accuracy': metrics.get('accuracy', None),
        'precision': metrics.get('precision', None),
        'recall': metrics.get('recall', None),
        'f1': metrics.get('f1', None),
        'roc_auc': metrics.get('roc_auc', None),
        'roc_curve': metrics.get('roc_curve', None),
        'confusion_matrix': metrics.get('confusion_matrix', None),
        'model_path': model_path
    }
    
    return render(request, 'work_with_dataset/results_page.html', context)


def model_building(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH]):
        cleanup_session(request)
        return redirect('upload_file')
    
    if request.method == 'POST':
        features = request.POST.getlist('features')
        target = request.POST.get('target')
        selected_model = request.POST.get('selected_model')
        
        test_split = True if request.POST.get('test_split') else False
        test_size = int(request.POST.get('test_size', 20)) / 100  # Конвертируем % в дробь
        random_state = int(request.POST.get('random_state', 42))
        
        cross_validate = True if request.POST.get('cross_validate') else False
        cv_folds = int(request.POST.get('cv_folds', 5)) if cross_validate else None
        
        model_params = {}
        
        if selected_model == 'random_forest':
            model_params = {
                'n_estimators': int(request.POST.get('rf_n_estimators', 100)),
                'max_depth': request.POST.get('rf_max_depth') or None,  # None если пустое значение
                'min_samples_split': int(request.POST.get('rf_min_samples_split', 2)),
                'model_type': 'random_forest'
            }
            if model_params['max_depth'] is not None:
                model_params['max_depth'] = int(model_params['max_depth'])
                
        elif selected_model == 'logistic_regression':
            model_params = {
                'C': float(request.POST.get('lr_c', 1.0)),
                'max_iter': int(request.POST.get('lr_max_iter', 100)),
                'model_type': 'logistic_regression'
            }
            
        elif selected_model == 'svm':
            model_params = {
                'C': float(request.POST.get('svm_c', 1.0)),
                'kernel': request.POST.get('svm_kernel', 'rbf'),
                'model_type': 'svm'
            }
        
        training_config = {
            'features': features,
            'target': target,
            'test_options': {
                'test_split': test_split,
                'test_size': test_size,
                'random_state': random_state
            },
            'cross_validation': {
                'enable': cross_validate,
                'folds': cv_folds
            },
            'model_params': model_params
        }
        
        metrics = build_ml_model(
            request.session[COPIED_FILE_PATH],
            request.session[CONFIG_PATH],
            request.session[ML_MODELS_DIR],
            selected_model,
            training_config
        )
        
        request.session['metrics'] = metrics
        request.session['model_path'] = metrics.get('model_path', '')
        
        return redirect('results_page')
    
    context = {
        'file_name': request.session.get('file_name', ''),
        'shape': request.session.get(SHAPE, (0, 0)),
        'columns': request.session[NUM_COLS]
    }
    return render(request, 'work_with_dataset/model_building.html', context)


def export_dataset(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH]):
        cleanup_session(request)
        return redirect('upload_file')
    
    return response_file(request.session[COPIED_FILE_PATH])


def export_pipeline(request):
    if PIPELINE_PATH not in request.session:
        return redirect('action_choice')

    return response_file(request.session[PIPELINE_PATH])



def response_file(file_path):
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    
    return HttpResponse("File not found", status=404)


def apply_pipeline(request):
    if request.method != 'POST':
        return redirect('action_choice')
    
    if not all(key in request.session for key in [UPLOADED_FILE_PATH, PIPELINE_PATH]):
        return HttpResponse("Required data not found in session", status=400)
    
    
    pipeline_apply.apply_pipeline(request.session[PIPELINE_PATH], request.session[COPIED_FILE_PATH], request.session[CONFIG_PATH])
            
    return redirect('preview')  
