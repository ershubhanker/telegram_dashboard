from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('index/', views.index, name='index'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/', views.adminhome, name='admin_dashboard'),
    # Add the URLs for admin_dashboard and staff_dashboard here
]