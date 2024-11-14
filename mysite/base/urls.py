from django.urls import path

from mysite.base import views

app_name = 'base'

urlpatterns = [
    path('', views.home, name='home'),
    path('perguntas/<int:indice>', views.perguntas, name='perguntas'),
    path('classificacao', views.classificacao, name='classificacao'),
]
