from django.urls import path
from words import views

app_name = "words"
urlpatterns = [
    path("update_words/", views.update_word),
    path("get_sentences/", views.get_sentences),
]