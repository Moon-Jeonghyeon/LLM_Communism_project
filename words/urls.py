from django.urls import path
from words import views

app_name = "words"
urlpatterns = [
    path("update_words/", views.update_word),
    path("get_sentences/", views.get_sentences),
    path("category/", views.category, name="category"),
    path("learn/",views.learn_words, name="learn_words"),
    path("quiz/", views.quiz, name="quiz"),
    path("quiz_results/", views.quiz_results, name="quiz_results"),
    path("vocabulary/", views.vocabulary, name="vocabulary"),
    path("vocabulary/delete/<int:vocab_id>/", views.delete_vocab, name="delete_vocab"),
]