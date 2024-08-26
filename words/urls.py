from django.urls import path
from words import views

urlpatterns = [
    path("", views.get_words),
]