"""
URL configuration for datacraft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from upload_file.views import upload_file, preview, action_choice, import_pipeline
from work_with_dataset.views import (num_preprocessings, text_preprocessing, model_building,
                                    export_dataset, export_pipeline,apply_pipeline, results_page)
from django.urls import path

urlpatterns = [
    path('', upload_file, name='upload_file'),
    path('preview/', preview, name='preview'),
    path('action-choice/', action_choice, name='action_choice'),
    path('num-preprocessing/', num_preprocessings, name='num_preprocessing'),
    path('text-preprocessing/', text_preprocessing, name='text_preprocessing'),
    path('model-building/', model_building, name='model_building'),
    path('export_dataset/', export_dataset, name='export_dataset'),
    path('export_pipeline/', export_pipeline, name='export_pipeline'),
    path('import_pipeline/', import_pipeline, name='import_pipeline'),
    path('apply_pipeline/', apply_pipeline, name='apply_pipeline'),
    path('results_page/', results_page, name='results_page')
]