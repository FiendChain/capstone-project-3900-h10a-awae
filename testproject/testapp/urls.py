from django.urls import path
from . import views

urlpatterns = [
    path('message/', views.displayMessage),
    path('home/', views.homepage, name="homepage"),
    path('login/', views.login, name="login"),
    path('registration/', views.registration, name="registration"),

]