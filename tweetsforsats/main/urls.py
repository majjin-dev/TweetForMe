from django.urls import path
from . import views

app_name='main'
urlpatterns = [
    path('', views.index, name='index'),
    path('check-invoice/<id>', views.check_invoice, name='check_invoice')
]