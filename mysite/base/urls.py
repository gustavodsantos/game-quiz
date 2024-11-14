from django.urls import path

from mysite.base import views

app_name = 'base'

urlpatterns = [
    path('', views.home, name='home'),
]
