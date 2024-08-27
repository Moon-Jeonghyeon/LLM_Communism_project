from django.db import models
from users.models import User

# Create your models here.
difficulty_choices = (
    ("A1", "입문"),
    ("A2", "초급"),
    ("B1", "중급"),
    ("B2", "중상급"),
    ("C1", "상급"),
    ("C2", "고급")
)

# 주제 테이블
class Topic(models.Model):
    main_topic = models.CharField("메인 주제", max_length=50)
    sub_topic = models.CharField("서브 주제", max_length=50)

    def __str__(self):
        return f"{self.main_topic} > {self.sub_topic}"

# 단어 테이블
class Word(models.Model):
    word = models.CharField("단어", max_length=100)
    definition = models.TextField("정의", blank=True, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, related_name="words", blank=True, null=True)
    difficulty = models.CharField("난이도", max_length=10, choices=difficulty_choices, blank=True, null=True)

    def __str__(self):
        return self.word
    
    
# 문장 테이블
class Sentence(models.Model):
    sentence = models.TextField("예문")
    definition = models.TextField("뜻", null=True, blank=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='sentences', null=True)
    source = models.CharField("출처", max_length=100)

    def __str__(self):
        return self.sentence

# 단어장 테이블
class Vocabulary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    added_at = models.DateTimeField("등록일", auto_now_add=True)

# 퀴즈 테이블
class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
    user_answer = models.CharField("사용자 입력 정답", max_length=100)
    is_correct = models.BooleanField("정답 여부")
    quiz_date = models.DateTimeField("진행일", auto_now_add=True)

# 메모 테이블
class Memo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField("내용")
    created_at = models.DateTimeField("작성일", auto_now_add=True)
    updated_at = models.DateTimeField("수정일", auto_now=True)
