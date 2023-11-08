from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'account_manager'

urlpatterns = [
    path('', views.index, name='index'),
    path('report/<str:date>', views.report_view_dated, name='report_dated'),
    path('report/', views.report_view, name='report'),
    path('monitor/', views.monitor_view, name='monitoring'),
    path('account_for/', views.account_selection_view, name='choose_account'),
    path('account_deals_for/<int:id>', views.accounter_view, name='choose_deals'),
    path('accept_deals/', views.account_for_deals, name='accept_deals'),

]
