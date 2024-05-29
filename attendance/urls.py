from django.urls import path
from .views import capture_images, register,attendance

urlpatterns = [
    path('', capture_images, name='capture_images'),
    path('register/', register, name='register_page'),
    path('take_attendance/', attendance, name='attendance_page'),
]
