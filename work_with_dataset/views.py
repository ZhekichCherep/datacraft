from django.shortcuts import render, redirect
import os
from upload_file.views import cleanup_session
from upload_file.views import (COPIED_FILE_PATH, CONFIG_PATH, NUM_COLS,
                               SHAPE, FILE_NAME, OBJ_COLS, PIPELINE_PATH, UPLOADED_FILE_PATH)
from .preprocesses.text_preprocessing import process_text_data
from .preprocesses.num_preprocessing import process_num
from django.http import FileResponse, HttpResponse
from work_with_dataset.preprocesses import pipeline_apply

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
        lowercase = request.POST.get('text_lowercase')
        remove_punct = request.POST.get('text_remove_punct')
        remove_stopwords = request.POST.get('text_remove_stopwords')
        stemming = request.POST.get('text_stemming')
        process_text_data(request.session[COPIED_FILE_PATH], request.session[CONFIG_PATH], request.session[PIPELINE_PATH],
                                                     selected_columns, lowercase, remove_punct, remove_stopwords, stemming)
        
        return redirect('action_choice')

    try:
        context = {
            'columns': request.session[OBJ_COLS],
            'shape': request.session[SHAPE],
            'file_name': request.session.get(FILE_NAME, '')
        }
        return render(request, 'work_with_dataset/text_preprocessing.html', context)
    
    except Exception as e:
        cleanup_session(request)
        return render(request, 'upload_file/index.html', {'errors': [str(e)]})


def model_building(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH]):
        cleanup_session(request)
        return redirect('upload_file')
    
    context = {
        'file_name': request.session.get('file_name', ''),
        'shape': request.session.get(SHAPE, (0, 0))
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
