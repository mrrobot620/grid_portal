from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("" , views.login_view , name="login"),
    path("home" , views.home , name="home"),
    path("logout" , views.logout_view , name="logout"),
    path('folder/<str:folder_name>/', views.folder_detail, name='folder_detail'),
    path('folder/<str:folder_name>/upload/', views.upload_csv_to_storage, name='upload_csv'),

]
