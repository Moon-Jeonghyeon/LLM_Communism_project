from django.urls import path
from words import views

app_name = "words"
urlpatterns = [
    path("update_words/", views.update_word),
    path("category/", views.category, name="category"),
    path("voca/", views.voca, name="vaca"),
]