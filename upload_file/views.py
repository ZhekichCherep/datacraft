from django.shortcuts import render, redirect
from .modules.forms import UploadFileForm
from .modules.eda import read_data_file, get_preview_data
from django.conf import settings
from tempfile import mkdtemp
from django.core.files.storage import FileSystemStorage
import os

# Константы для ключей сессии
UPLOADED_FILE_PATH = 'uploaded_file_path'
CONFIG_PATH = 'config_path'
NUM_COLS = 'num_cols'
OBJ_COLS = 'obj_cols'
SHAPE = 'shape'

def cleanup_session(request):
    try:
        if UPLOADED_FILE_PATH in request.session:
            file_path = request.session[UPLOADED_FILE_PATH]
            if os.path.exists(file_path):
                os.remove(file_path)
                dir_path = os.path.dirname(file_path)
                try:
                    os.rmdir(dir_path)
                except OSError:
                    pass  
        
        if CONFIG_PATH in request.session:
            config_path = request.session[CONFIG_PATH]
            if os.path.exists(config_path):
                os.remove(config_path)
                
    except Exception as e:
        pass
    finally:
        request.session.flush()

def upload_file(request):
    cleanup_session(request)
    
    if request.method != 'POST':
        form = UploadFileForm()
        return render(request, 'upload_file/index.html')
    
    if 'file' not in request.FILES:
        return render(request, 'upload_file/index.html', {'errors': ['No file was submitted']})

    form = UploadFileForm(request.POST, request.FILES)

    if form.is_valid():
        try:
            temp_dir = mkdtemp()
            fs = FileSystemStorage(location=temp_dir)
            uploaded_file = request.FILES['file']
            file_name = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(file_name)
            
            config_path, errors = read_data_file(file_path)
            if errors:
                cleanup_session(request)
                return render(request, 'upload_file/index.html', {'errors': errors})
            
            request.session[UPLOADED_FILE_PATH] = file_path
            request.session[CONFIG_PATH] = config_path
            request.session['file_name'] = uploaded_file.name

            return redirect('preview')
        except Exception as e:
            cleanup_session(request)
            return render(request, 'upload_file/index.html', {'errors': [str(e)]})
    
    cleanup_session(request)
    return render(request, 'upload_file/index.html')

def preview(request):
    if UPLOADED_FILE_PATH not in request.session or CONFIG_PATH not in request.session:
        cleanup_session(request)
        return redirect('upload_file')
    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            return redirect('action_choice')  
        cleanup_session(request)
        return redirect('upload_file')

    try:
        context = {
            'file_name': request.session.get('file_name', '')
        }
        preview_data = get_preview_data(request.session[UPLOADED_FILE_PATH], request.session[CONFIG_PATH])
        context.update(preview_data)
        request.session[NUM_COLS] = context.pop(NUM_COLS, [])
        request.session[OBJ_COLS] = context.pop(OBJ_COLS, [])
        request.session[SHAPE] = context.get(SHAPE, (0, 0))
        
        return render(request, 'upload_file/preview.html', context)
    except Exception as e:
        cleanup_session(request)
        return render(request, 'upload_file/index.html', {'errors': [str(e)]})

def action_choice(request):
    if not all(key in request.session for key in [UPLOADED_FILE_PATH, CONFIG_PATH, SHAPE]):
        cleanup_session(request)
        return redirect('upload_file')
    
    if request.method == 'POST' and 'restart' in request.POST:
        cleanup_session(request)
        return redirect('upload_file')
    
    context = {
        'file_name': request.session.get('file_name', ''),
        'shape': request.session.get(SHAPE, (0, 0))
    }
    return render(request, 'upload_file/action_choise.html', context)


def num_preprocessings(request):
    if not all(key in request.session for key in [UPLOADED_FILE_PATH, CONFIG_PATH, NUM_COLS, SHAPE]):
        cleanup_session(request)
        return redirect('upload_file')

    if request.method == 'POST':
        if 'back' in request.POST:
            return redirect('preview')
        
    try:
        context = {
            'columns': request.session[NUM_COLS],
            'shape': request.session[SHAPE],
            'file_name': request.session.get('file_name', '')
        }
        return render(request, 'upload_file/num_preprocessing.html', context)
    except Exception as e:
        cleanup_session(request)
        return render(request, 'upload_file/index.html', {'errors': [str(e)]})


def text_preprocessing(request):
    if not all(key in request.session for key in [UPLOADED_FILE_PATH, CONFIG_PATH, OBJ_COLS]):
        cleanup_session(request)
        return redirect('upload_file')
    
    context = {
        'columns': request.session[OBJ_COLS],
        'shape': request.session[SHAPE],
        'file_name': request.session.get('file_name', '')
    }
    return render(request, 'upload_file/text_preprocessing.html', context)

def model_building(request):
    if not all(key in request.session for key in [UPLOADED_FILE_PATH, CONFIG_PATH]):
        cleanup_session(request)
        return redirect('upload_file')
    
    context = {
        'file_name': request.session.get('file_name', ''),
        'shape': request.session.get(SHAPE, (0, 0))
    }
    return render(request, 'upload_file/model_building.html', context)