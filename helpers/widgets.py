from django.forms import widgets

class DateWidget(widgets.DateInput):
    template_name = "widgets/date.html"
    
class CkeditorWidget(widgets.Textarea):
    template_name = "widgets/ckeditor.html"

class SelectWidget(widgets.SelectMultiple):
    template_name = "widgets/select.html"

class ImageInput(widgets.ClearableFileInput):
    template_name = "widgets/image-input.html"
    
