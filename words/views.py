from django.shortcuts import render
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from words.models import Topic, Word, Sentence, Vocabulary, Quiz, Memo
from random import sample

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
            sentence_obj = Sentence.objects.get_or_create(
                sentence=sentence,
                definition=definition_text,
                source=source_text,
            )
            print(f"Sentence saved: {sentence}")

            sentence_obj.word.add(word_obj)
            sentence_obj.save()

        except Exception as e:
            print(f"clicking label 에러: {e}")

    # 브라우저 닫기
    driver.quit()

def category(request):
    main_topics = Topic.objects.values_list("main_topic", flat=True).distinct()

    topic_data = []

    for main in main_topics:
        sub_topics = Topic.objects.filter(main_topic=main).values_list("sub_topic", flat=True).distinct()
        sub_topics = list(sub_topics)
        topic_data.append({
            "main_topic": main,
            "sub_topics": sub_topics,
        })

    return render(request, "words/category.html", {"topic_data": topic_data})
    

def voca(request):
    return render(request, "words/voca.html")

def learn_words(request, topic_id):
    # 주제에 해당하는 단어들 중 뜻이 있는 단어들
    words = Word.objects.filter(topic__id=topic_id, definition__isnull=False)
    # 그 중 예문이 있는 단어들
    words_with_sentences = [word for word in words if word.sentences.exists()]

    # 랜덤으로 10개 단어 선택
    selected_words = sample(words_with_sentences, min(len(words_with_sentences), 10))

    context = {
        "selected_words": selected_words,
    }

    return render(request, "words/learn_words.html", context)

def quiz(request):
    # 사용자가 학습한 경우 학습한 단어들로만 문제를 내고, 사용자가 학습 없이 문제 풀기를 선택한 경우 단어장에 있는 단어와 랜덤 10개의 단어 중 무작위로 10개를 선택함

    # POST 방식 요청 시
    if request.method == "POST":
        selected_words = request.POST.get("selected_words")

        # 선택 단어들이 있다면
        if selected_words:
            # 이전 선택 단어들은 id가 쉼표로 구분되어 있으므로 , 를 기준으로 분리함
            word_ids = selected_words.split(",")
            
            # word_ids 에 해당하는 단어 중 단어 뜻과 문장 해석이 있는 단어 객체 반환
            words = Word.objects.filter(id__in=word_ids, definition__isnull=False, sentences_definition__isnull=False)

        # 사용자가 단어를 학습하지 않은 경우   
        else:
            # 전체 단어 중 랜덤하게 10개 단어 선택
            all_words = list(Word.objects.filter(definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10])
            
            # 사용자의 단어장에서 단어 객체 반환
            vocab_words = list(Vocabulary.objects.filter(user=request.user).values_list("word", flat=True))

            # 단어 뜻과 예문 해석이 있는 단어를 랜덤하게 10개 선택
            vocab_words = Word.objects.filter(id__in=vocab_words, definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10]

            # 두 리스트를 합치고, 중복 없이 10개의 단어를 랜덤하게 선택함
            combined_words = list(set(all_words + list(vocab_words)))
            words = combined_words[:10]

    # GET 방식 요청 시(사용자가 바로 페이지에 접근한 경우) 동일한 로직 실행
    else:
        all_words = list(Word.objects.filter(definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10])
        vocab_words = list(Vocabulary.objects.filter(user=request.user).values_list('word', flat=True))
        vocab_words = Word.objects.filter(id__in=vocab_words, definition__isnull=False, sentences__definition__isnull=False).order_by("?")[:10]
        combined_words = list(set(all_words + list(vocab_words)))
        words = combined_words[:10]

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
            user_answer = request.POST.get(f"anwers_{ word.id }")

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
