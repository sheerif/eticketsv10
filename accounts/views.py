from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages

def signup(request):
    next_url = request.GET.get("next") or "/offers/"
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Compte créé et connecté ✅")
            return redirect(next_url)
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form, "next": next_url})

def logout_simple(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté(e) ✅")
    next_url = request.GET.get("next") or "/offers/"
    return redirect(next_url)
