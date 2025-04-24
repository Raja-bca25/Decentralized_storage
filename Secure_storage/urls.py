from django.urls import path
from .views import upload_secure_file, retrieve_secure_file
from Secure_storage.views import upload_secure_file


urlpatterns = [
    path('upload/', upload_secure_file, name='upload_secure_file'),
    path('retrieve/', retrieve_secure_file, name='retrieve_secure_file'),
]