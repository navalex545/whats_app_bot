from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_view, name='upload'),
    path('status/<int:batch_id>/', views.status_view, name='status'),
    path('api/status/<int:batch_id>/', views.api_status, name='api_status'),
    path('api/start/<int:batch_id>/', views.start_sending, name='start_sending'),
    path('api/stop/<int:batch_id>/', views.stop_sending, name='stop_sending'),
    path('download-template/', views.download_template, name='download_template'),
]
