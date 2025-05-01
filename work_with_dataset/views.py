from django.shortcuts import render, redirect
from upload_file.views import cleanup_session
from upload_file.views import COPIED_FILE_PATH, CONFIG_PATH, NUM_COLS, SHAPE, FILE_NAME, OBJ_COLS

def num_preprocessings(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH, NUM_COLS, SHAPE]):
        cleanup_session(request)
        return redirect('upload_file')

    if request.method == 'POST':
        if 'back' in request.POST:
            return redirect('preview')
        
    try:
        context = {
            'columns': request.session[NUM_COLS],
            'shape': request.session[SHAPE],
            'file_name': request.session.get(FILE_NAME, '')
        }
        return render(request, 'upload_file/num_preprocessing.html', context)
    except Exception as e:
        cleanup_session(request)
        return render(request, 'upload_file/index.html', {'errors': [str(e)]})
    

def text_preprocessing(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH, OBJ_COLS]):
        cleanup_session(request)
        return redirect('upload_file')
    
    context = {
        'columns': request.session[OBJ_COLS],
        'shape': request.session[SHAPE],
        'file_name': request.session.get('file_name', '')
    }
    return render(request, 'upload_file/text_preprocessing.html', context)


def model_building(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH]):
        cleanup_session(request)
        return redirect('upload_file')
    
    context = {
        'file_name': request.session.get('file_name', ''),
        'shape': request.session.get(SHAPE, (0, 0))
    }
    return render(request, 'upload_file/model_building.html', context)