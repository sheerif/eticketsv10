from django.urls import path
from .views import signup, logout_simple
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_simple, name="logout"),
]
