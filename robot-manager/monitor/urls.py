from django.contrib import admin
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.main_view, name='main_view'),

]
