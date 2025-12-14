from django import forms


class MultipleFileInput(forms.FileInput):
    """Custom widget that allows multiple file selection."""
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        default_attrs = {'multiple': True}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)


class MultipleFileField(forms.FileField):
    """Custom field that handles multiple file uploads."""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ExcelUploadForm(forms.Form):
    """Form for uploading Excel file and attachments."""
    
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Upload an Excel file (.xlsx) with columns: Phone, Message, Attachment (optional)'
    )
    
    attachments = MultipleFileField(
        label='Attachment Files',
        required=False,
        help_text='Upload any files referenced in the Excel (PDFs, images, etc.)'
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            if not file.name.endswith(('.xlsx', '.xls')):
                raise forms.ValidationError('Please upload an Excel file (.xlsx or .xls)')
        return file
