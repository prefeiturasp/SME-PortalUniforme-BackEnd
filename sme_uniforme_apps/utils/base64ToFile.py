from django.core.files.base import ContentFile
import base64

def base64ToFile(base):
    format, imgstr = base.split(';base64,') 
    ext = format.split('/')[-1] 
    data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return {'data': data, 'ext': ext }