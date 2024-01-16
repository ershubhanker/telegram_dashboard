from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserLoginForm
from .models import CustomUser, AdminProfile, StaffProfile
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.is_admin:
                AdminProfile.objects.create(user=user)
            else:
                StaffProfile.objects.create(user=user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            print("login successfull")
            if user is not None:
                login(request, user)
                if user.is_admin:
                    return redirect('admin_dashboard')
                else:
                    return redirect('index')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def index(request):
    return render(request, 'index.html')


def user_logout(request):
    logout(request)
    return redirect('login') 

def adminhome(request):
    return render(request, 'index admin.html')