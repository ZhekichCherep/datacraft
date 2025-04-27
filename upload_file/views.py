from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .modules.forms import UploadFileForm
from .modules.eda import read_data_file, get_preview_data
import pandas as pd
import os
from django.conf import settings
from tempfile import mkdtemp
from django.core.files.storage import FileSystemStorage


from django.shortcuts import render, redirect
import json

UPLOADED_FILE_PATH = 'uploaded_file_path'
CONFIG_PATH = 'config_path'

def upload_file(request):
    if request.method != 'POST':
        form = UploadFileForm()
        return render(request, 'upload_file/index.html')
    
    form = UploadFileForm(request.POST, request.FILES)
    
    if 'file' not in request.FILES:
        return render(request, 'upload_file/index.html', {'errors': ['No file was submitted']})

    form = UploadFileForm(request.POST, request.FILES)

    if form.is_valid():
        temp_dir = mkdtemp()
        fs = FileSystemStorage(location=temp_dir)
        uploaded_file = request.FILES['file']
        file_name = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_name)
        
        config_path, errors = read_data_file(file_path)
        if errors:
            return render(request, 'upload_file/index.html', {'errors': errors})
             
        request.session[UPLOADED_FILE_PATH] = file_path
        request.session[CONFIG_PATH] = config_path
        print(request)

        return redirect('preview')  

    else:
        form = UploadFileForm()
    request.session.flush()
    return render(request, 'upload_file/index.html')

def preview(request):
    if UPLOADED_FILE_PATH not in request.session or CONFIG_PATH not in request.session:
        return redirect('upload_file')
    
    if request.method == 'POST' and UPLOADED_FILE_PATH in request.session and CONFIG_PATH in request.session:
        if 'confirm' in request.POST:
            return redirect('choose_preprocessing_pipeline')

    context = {
        'file_name': request.session.get('file_name', '')
    }
    context.update(get_preview_data(request.session[UPLOADED_FILE_PATH], request.session[CONFIG_PATH]))

    return render(request, 'upload_file/preview.html', context)

def confirm(request):
    if request.method == 'POST' and UPLOADED_FILE_PATH in request.session and CONFIG_PATH in request.session:
        if 'confirm' in request.POST:
            return redirect('choose_preprocessing_pipeline')
                
        request.session.flush()
        return redirect('upload_file')


def choose_preprocessings_pipeline(request):
    return render(request, 'upload_file/preprocessing.html')