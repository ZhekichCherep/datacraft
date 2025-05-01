from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='CSV файл',
        widget=forms.FileInput(attrs={
            'accept': '.csv, .xlsx',
            'class': 'file-input'
        })
    )