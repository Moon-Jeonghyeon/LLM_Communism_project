from django.shortcuts import render, redirect, get_object_or_404
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from words.models import Topic, Word, Sentence, Vocabulary, Quiz, Memo
from random import sample
from collections import defaultdict

# Create your views here.
def get_words(request):
    # 보류: 바로 객체 생성하기.
    url = "https://www.oxfordlearnersdictionaries.com/topic/"

    driver = webdriver.Chrome()

    driver.get(url) # url 접속

    topics = driver.find_elements(By.CLASS_NAME, "topic-label")
    word_list = []

    for topic_index in range(len(topics)):
        topics = driver.find_elements(By.CLASS_NAME, "topic-label")
        if topic_index >= len(topics):
            break

        try:
            main_topic = topics[topic_index].text.strip()
            topics[topic_index].click()
            time.sleep(2)
        except Exception as e:
            print(f"main topics 에러: {e}")
            continue

        processed_subtopics = []
        topic_boxes = driver.find_elements(By.CLASS_NAME, "topic-box-secondary-heading")

        while len(processed_subtopics) < len(topic_boxes):
            for index, topic_box in enumerate(topic_boxes):
                if index in processed_subtopics:
                    continue
        
                try:
                    topic_boxes = driver.find_elements(By.CLASS_NAME, "topic-box-secondary-heading")
                    sub_topic = topic_boxes[index].text
                    sub_topic = sub_topic.replace("(see all)", "").strip()
                    topic_box = topic_boxes[index]
            
                    topic_box.click()
                    time.sleep(2)
                except Exception as e:
                    print(f"sub-topics 에러: {e}")
                    continue
        
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, "li[data-hw]")
                    for element in elements:
                        word = element.get_attribute("data-hw")
                        try:
                            difficulty = element.find_element(By.CSS_SELECTOR, "span.belong-to").text
                        except:
                            difficulty = "N/A"

                        try:
                            topic, created = Topic.objects.get_or_create(main_topic=main_topic, sub_topic=sub_topic)
                            Word.objects.get_or_create(word=word, difficulty=difficulty, topic=topic)
                        except Exception as e:
                            print(f"word, difficulty 에러: {e}")
                            continue
                except Exception as e:
                    print(f"processing 에러: {e}")
                    continue
                    
                processed_subtopics.append(index)
        
                driver.back() # 뒤로가기
                time.sleep(2)
        
                topic_boxes = driver.find_elements(By.CLASS_NAME, "topic-box-secondary-heading")

        try:
            back_btn = driver.find_element(By.CSS_SELECTOR, "a.topic_back")
            back_btn.click()
            time.sleep(2)
        except Exception as e:
            print(f"뒤로가기 에러: {e}")
            continue

    driver.quit()

def update_word(request):
    base_url = "https://en.dict.naver.com/#/search?"
    driver = webdriver.Chrome()

    # DB에서 단어를 가져오기 (정의가 없는 단어만)
    words = Word.objects.filter(definition__isnull=True)

    for word_obj in words:
        word = word_obj.word

        # 단어 정의 가져오기
        driver.get(f"{base_url}range=word&query={word}")
        time.sleep(2)

        try:
            origin_div = driver.find_element(By.CSS_SELECTOR, 'div.row')
            mean_elements = origin_div.find_elements(By.CSS_SELECTOR, 'p.mean')
            definition = '\n'.join([mean.text for mean in mean_elements])
            
            # 단어 정의 업데이트
            word_obj.definition = definition
            word_obj.save()
            print(f"단어 뜻 저장 완료: {definition}")
            
        except Exception as e:
            print(f"Error occurred: {e}")
            continue

    driver.quit()

def get_sentences(request):
    base_url = "https://en.dict.naver.com/#/search?"
    driver = webdriver.Chrome()

    # 이미 뜻이 있는 단어들만 해당
    words = Word.objects.filter(definition__isnull=False)

    for word_obj in words:
        word = word_obj.word

        # 예문 페이지로 이동
        driver.get(f"{base_url}range=example&query={word}")
        time.sleep(2)  # 페이지 로드 대기

        try:
            label_check = driver.find_element(By.CSS_SELECTOR, "label.inp_label_check")
            label_check.click()

            time.sleep(2)  # 클릭 후 페이지 로드 대기

            origin_div = driver.find_element(By.CSS_SELECTOR, 'div.origin')
            text_span = origin_div.find_element(By.CSS_SELECTOR, 'span.text')
            
            # span.text 내부의 모든 텍스트를 추출
            sentence = text_span.text
            definition_text = driver.find_element(By.CSS_SELECTOR, 'div.translate').text
            source_text = driver.find_element(By.CSS_SELECTOR, 'a.source').text

            # 문장 객체 생성
            Sentence.objects.get_or_create(
                sentence=sentence,
                definition=definition_text,
                source=source_text,
                word=word_obj,
            )
            print(f"Sentence saved: {sentence}")

        except Exception as e:
            print(f"clicking label 에러: {e}")

    # 브라우저 닫기
    driver.quit()

def category(request):
    # 난이도 선택
    difficulty_choices = (
        ("A1", "입문"),
        ("A2", "초급"),
        ("B1", "중급"),
        ("B2", "중상급"),
        ("C1", "상급"),
        ("C2", "고급")
    )

    # defaultdict 사용하기
    topic_data = defaultdict(list)
    
    # 주제 객체 반환
    for obj in Topic.objects.all():
        # 주제 객체의 main_topic을 키로 하고, 여러 obj(주제 객체)를 값으로 리스트 안에 추가한다.
        topic_data[obj.main_topic].append(obj)
    # topic_data 를 defaultdict 가 아닌 일반 dict 로 묶어준다.
    topic_data = dict(topic_data)
    print(topic_data)

    context = {
        "topic_data": topic_data,
        "difficulty_choices": difficulty_choices,
    }

    return render(request, "words/category.html", context)
    

def learn_words(request):
    topic_id = request.GET.get("topic_id")
    difficulty = request.GET.get("difficulty")

    words_with_sentences = []

    # 조건에 맞는 단어 필터링하기
    # 주제&난이도별 단어인 경우
    if topic_id and difficulty:
        words = Word.objects.filter(topic__id=topic_id, difficulty=difficulty, definition__isnull=False)

    # 주제별 단어인 경우
    elif topic_id:
        words = Word.objects.filter(topic__id=topic_id, definition__isnull=False)

    # 난이도별 단어인 경우
    elif difficulty:
        words = Word.objects.filter(difficulty=difficulty, definition__isnull=False)
    
    else:
        words = Word.objects.filter(definition__isnull=False)
    
    # 그 중 예문이 있는 단어들
    words_with_sentences = [word for word in words if word.sentences.exists()]

    # 랜덤으로 10개 단어 선택
    selected_words = sample(words_with_sentences, min(len(words_with_sentences), 10))

    # template에 아이디 자리인 value 값에 넘겨주기 위해 만든 변수
    selected_words_ids = ",".join([str(word.id) for word in words])

    context = {
        "selected_words": selected_words,
        "selected_words_ids": selected_words_ids,
        "topic_id": topic_id,
        "difficulty": difficulty,
    }

    return render(request, "words/learn_words.html", context)

def filtering_words(user, topic_id, difficulty):
    # 주제&난이도별 단어인 경우
    if topic_id and difficulty:

        # 주제&난이도별 단어 중 10개 단어 선택
        all_words = Word.objects.filter(topic__id=topic_id, difficulty=difficulty, definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10]

        # 사용자의 단어장에서 단어 객체 반환
        vocab_words = Vocabulary.objects.filter(user=user, word__topic__id=topic_id, word__difficulty=difficulty).values_list("word", flat=True)
    
    # 주제별 단어인 경우
    elif topic_id:
        all_words = Word.objects.filter(topic__id=topic_id, definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10]
        vocab_words = Vocabulary.objects.filter(user=user, word__topic__id=topic_id).values_list("word", flat=True)

    # 난이도별 단어인 경우
    elif difficulty:
        all_words = Word.objects.filter(difficulty=difficulty, definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10]
        vocab_words = Vocabulary.objects.filter(user=user, word__difficulty=difficulty).values_list("word", flat=True)

    # 이외 경우
    else:
        all_words = Word.objects.filter(definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10]
        vocab_words = Vocabulary.objects.filter(user=user).values_list("word", flat=True)

    # 단어장에 있는 단어로 필터링된 단어 가져오기
    vocab_words = Word.objects.filter(id__in=vocab_words, definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10]

    # 단어가 있는지 확인하고, 중복 없이 두 리스트를 합치기(|)
    combined_words = list(set(all_words) | set(vocab_words))
    if combined_words:
        return combined_words[:10]
    return combined_words

def quiz(request):
    # 쿼리스트링에서 topic_id와 difficulty 값 가져오기
    topic_id = request.GET.get("topic_id")
    difficulty = request.GET.get("difficulty")

    # POST 방식 요청 시
    if request.method == "POST":
        selected_words = request.POST.get("selected_words")
        print(selected_words)

        if selected_words:
            # 선택된 단어들로 필터링
            word_ids = selected_words.split(",")
            words = Word.objects.filter(id__in=word_ids, definition__isnull=False, sentences__definition__isnull=False)

            print("word_ids:", word_ids)

        else:
            # 주제와 난이도에 따른 필터링
            words = filtering_words(request.user, topic_id, difficulty)

    else:
        # GET 방식 요청 시 선택된 단어가 없는 경우와 동일한 로직
        words = filtering_words(request.user, topic_id, difficulty)

    # selected_words 가 있는 경우 words 는 selected_words 의 아이디로 필터링한 단어 객체로 퀴즈를 내고, combined_words 는 selected_words 가 없는 경우에 사용됨.
    return render(request, "words/quiz.html", {"words": words})


def quiz_results(request):
    # POST 방식 요청 시
    if request.method == "POST":
        results = []
        correct_count = 0
        # keys 중 answers_ 로 시작하는 키만 가져옴. quiz 템플릿의 answer_{{ word.id }} 에서 word 의 id를 가져오고 이 리스트 안에 포함된 단어 객체들을 반환함.
        word_ids = [key.split("_")[1] for key in request.POST.keys() if key.startswith("answers_")]
        words = Word.objects.filter(id__in=word_ids)

        for word in words:
            # 사용자가 입력한 정답
            user_answer = request.POST.get(f"answers_{ word.id }")

            # 사용자 입력 답이 단어와 같으면 True
            correct = user_answer.lower() == word.word.lower()

            # 정답일 때
            if correct:
                correct_count += 1
            
            # 단어 객체, 정답 여부, 사용자 답안, 실제 답안을 딕셔너리로 묶어서 리스트에 추가함
            results.append({
                "word": word,
                "correct": correct,
                "user_answer": user_answer,
                "correct_answer": word.word,
                "definition": word.definition,
            })

            # 요청을 보낸 사용자의 단어장에 단어가 없는 경우 객체를 생성함
            Vocabulary.objects.get_or_create(user=request.user, word=word)

        # 퀴즈 결과, 맞춘 개수, 총 문제 수를 context로 전달함
        context = {
            "results": results,
            "correct_count": correct_count,
            "total_count": len(words),
        }

        return render(request, "words/quiz_results.html", context)

def vocabulary(request):
    # 쿼리스트링에서 정렬 기준과 방향 가져오기
    order_by = request.GET.get("order_by", "word__word")
    direction = request.GET.get("direction", "asc")

    # 주제별 정렬
    if order_by == "word__topic__main_topic":
        if direction == "desc":
            order_by_fields = ["word__topic__main_topic", "-word__word"]
        else:
            order_by_fields = ["word__topic__main_topic", "word__word"]

    # 난이도별 정렬
    elif order_by == "word__difficulty":
        if direction == "desc":
            order_by_fields = ["word__difficulty", "-word__word"]
        else:
            order_by_fields = ["word__difficulty", "word__word"]

    # 단어 정렬
    else:
        if direction == "desc":
            order_by_fields = ["-word__word"]
        else:
            order_by_fields = ["word__word"]

    user_vocabulary = Vocabulary.objects.filter(user=request.user).select_related("word").order_by(*order_by_fields)

    # lstrip을 사용해 기본 선택 상태를 유지함
    context = {
        "vocabulary": user_vocabulary,
        "order_by": order_by.lstrip("-"),
        "direction": direction,
    }

    return render(request, "words/vocabulary.html", context)

def delete_vocab(request, vocab_id):
    vocab = get_object_or_404(Vocabulary, id=vocab_id, user=request.user)

    if request.method == "POST":
        vocab.delete()
        return redirect("/words/vocabulary/")
    
    return render(request, "words/vocabulary.html")