from django.urls import path
from words import views

app_name = "words"
urlpatterns = [
    path("update_words/", views.update_word),
    path("category/", views.category, name="category"),
    path("voca/", views.voca, name="vaca"),
    path("learn/<int:topic_id>/",views.learn_words, name="learn_words"),
    path("quiz/", views.quiz, name="quiz"),
    path("quiz_results/", views.quiz_results, name="quiz_results"),
]