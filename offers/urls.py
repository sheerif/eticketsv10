from django.urls import path
from .views import offers_page
urlpatterns = [ path("", offers_page, name="offers_page") ]
