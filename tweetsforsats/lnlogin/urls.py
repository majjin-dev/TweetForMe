from django.urls import path, re_path
from . import views

app_name='lnlogin'
urlpatterns = [
    path('', views.login, name='login'),
    path('auth', views.auth, name='authorize'),
    path('check', views.check, name='check'),
    path('logout/', views.logout, name='logout')
]