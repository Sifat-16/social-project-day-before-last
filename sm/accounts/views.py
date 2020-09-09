from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .forms import CreationForm
# Create your views here.

def signuppage(request):
    form = CreationForm()
    if request.method == 'POST':
        form = CreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = CreationForm()

    context = {'form': form}

    return render(request, 'registration/signup.html', context)

def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("pass")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('newsfeed')
        else:
            messages.info(request, 'Invalid Username or Password')


    return render(request, 'registration/login.html')

def logoutpage(request):
    logout(request)
    return redirect('newsfeed')