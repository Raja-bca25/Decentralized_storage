from django.urls import path, include
urlpatterns = [
    path("api/v1/", include('Secure_storage.urls')),
]
