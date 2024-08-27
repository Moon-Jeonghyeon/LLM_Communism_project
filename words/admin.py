from django.contrib import admin
from words.models import Word, Sentence, Vocabulary, Quiz, Memo

# Register your models here.
@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "word",
        "definition",
        "topic",
        "difficulty",
    ]

@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "sentence",
        "definition",
        "source",
        "word",
    ]

    # def get_words(self):
    #     return ", ".join([word.word for word in self.word.all()])
    # get_words.short_description = "Words"  # 관리자 페이지에 표시할 이름

@admin.register(Vocabulary)
class VocabularyAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "word",
        "added_at",
    ]

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "word",
        "sentence",
        "user_answer",
        "is_correct",
        "quiz_date",
    ]

@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "content",
        "created_at",
        "updated_at",
    ]