from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('index/', views.index, name='index'),
    # Add the URLs for admin_dashboard and staff_dashboard here
]