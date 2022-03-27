from django.urls import path, re_path
from . import views

app_name='lnlogin'
urlpatterns = [
    path('', views.login, name='login'),
    path('auth/', views.auth, name='authorize'),
    path(r'^check/(?<k1>\w{32})$', views.check, name='check'),
    path('/logout', views.logout, name='logout')
]