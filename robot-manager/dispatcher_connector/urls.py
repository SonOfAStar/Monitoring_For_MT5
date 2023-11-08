from django.urls import path

from . import views

urlpatterns = [
    path('send_cmd', views.send_cmd_view, name='send_cmd_view'),
]