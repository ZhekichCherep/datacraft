from django.shortcuts import render, redirect
from core.modules.forms import UploadFileForm
from core.modules.eda import read_data_file, get_preview_data
from core.modules.fstream_operations import save_to_temp_dir, delete_files, read_work_file
from django.conf import settings

PIPELINE_PATH = 'pipeline_path'
UPLOADED_FILE_PATH = 'uploaded_file_path'
CONFIG_PATH = 'config_path'
NUM_COLS = 'num_cols'
OBJ_COLS = 'obj_cols'
SHAPE = 'shape'
COPIED_FILE_PATH = 'copied_path_file'
FILE_NAME = 'file_name'

def cleanup_session(request):
    try:
        delete_files([request.session[UPLOADED_FILE_PATH], request.session[CONFIG_PATH], request.session[COPIED_FILE_PATH]])          
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
            uploaded_file = request.FILES['file']
            file_path = save_to_temp_dir(uploaded_file)
            copied_file_path = save_to_temp_dir(uploaded_file)
            config_path, errors = read_data_file(file_path)
            
            if errors:
                cleanup_session(request)
                return render(request, 'upload_file/index.html', {'errors': errors})
            request.session.update({ UPLOADED_FILE_PATH: file_path,
                                    CONFIG_PATH: config_path,
                                    COPIED_FILE_PATH: copied_file_path,
                                    FILE_NAME: uploaded_file.name})

            return redirect('preview')
        except Exception as e:
            cleanup_session(request)
            return render(request, 'upload_file/index.html', {'errors': [str(e)]})
    
    cleanup_session(request)
    return render(request, 'upload_file/index.html')

def preview(request):
    if COPIED_FILE_PATH not in request.session or CONFIG_PATH not in request.session:
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
        preview_data = get_preview_data(request.session[COPIED_FILE_PATH], request.session[CONFIG_PATH])
        context.update(preview_data)
        request.session[NUM_COLS] = context.pop(NUM_COLS, [])
        request.session[OBJ_COLS] = context.pop(OBJ_COLS, [])
        request.session[SHAPE] = context.get(SHAPE, (0, 0))
        
        return render(request, 'upload_file/preview.html', context)
    except Exception as e:
        cleanup_session(request)
        return render(request, 'upload_file/index.html', {'errors': [str(e)]})

def action_choice(request):
    if not all(key in request.session for key in [COPIED_FILE_PATH, CONFIG_PATH, SHAPE]):
        cleanup_session(request)
        return redirect('upload_file')
    
    if request.method == 'POST' and 'restart' in request.POST:
        cleanup_session(request)
        return redirect('upload_file')
    
    context = {
        'file_name': request.session.get('file_name', ''),
        'shape': get_preview_data(request.session[COPIED_FILE_PATH], request.session[CONFIG_PATH])[SHAPE],
        'export_pipeline_enabled': PIPELINE_PATH in request.session
    }
    return render(request, 'upload_file/action_choise.html', context)

def import_pipeline(request):
    pass
