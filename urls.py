from django.urls import path
from .views import FaceRecognitionAPI


urlpatterns = [
    path('recognize/', FaceRecognitionAPI.as_view(), name='recognize'),  # URL becomes 'api/recognize/'
]
