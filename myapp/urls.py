from django.urls import path
from . import views

app_name = 'myapp'
urlpatterns = [
    path('', views.research_home, name='home'),
    path('run-research/', views.run_research, name='run_research'),
    path('download-report/<str:token>/', views.download_report, name='download_report'),
]
