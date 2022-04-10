from django.urls import path
from . import views

app_name='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('checkinvoice/<invoice_id>', views.check_invoice, name='checkinvoice'),
    path('tweet/', views.tweet, name='tweet')
]