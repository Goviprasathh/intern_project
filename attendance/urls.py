from django.urls import path,include
from .views import capture_images, register,attendance, capture_image,track_images,video_feed

urlpatterns = [
    
    path('', capture_images, name='capture_images'),
    path('register/', register, name='register_page'),
    path('take_attendance/', attendance, name='attendance_page'),
    path('video_feed/', video_feed, name='video_feed'),
    path('capture_image/', capture_image, name='capture_image'),
    path('track-images/', track_images, name='track_images'),
]
