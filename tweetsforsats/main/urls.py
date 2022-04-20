from django.urls import path
from . import views

app_name='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('checkinvoice/<invoice_id>', views.check_invoice, name='checkinvoice'),
    path('tweet/', views.tweet, name='tweet'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('withdraw_request', views.withdraw_request, name='withdraw_request'),
    path('withdraw_status/<k1>', views.withdraw_status, name='withdraw_status')
]