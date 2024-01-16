"""telegram_store URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from myapp import views as myapp_views  # Replace 'myapp' with your app's name

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', myapp_views.register, name='register'),
    path('login/', myapp_views.user_login, name='login'),
    path('index/', myapp_views.index, name='index'),
    path('', lambda request: redirect('login/'), name='root'),  # Redirect root to login
    path('logout/', myapp_views.user_logout, name='logout'),
    path('admin/', myapp_views.adminhome, name='admin_dashboard'),
    
    # Include other app-specific URLs here
]

