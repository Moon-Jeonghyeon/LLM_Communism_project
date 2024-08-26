from django.shortcuts import render
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from words.models import Topic, Word, Sentence, Vocabulary, Quiz, Memo

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
        time.sleep(2)

        try:
            label_check = driver.find_element(By.CSS_SELECTOR, "label.inp_label_check")
            label_check.click()

            time.sleep(2)

            sentence_text = driver.find_element(By.CSS_SELECTOR, 'div.origin').text
            definition_text = driver.find_element(By.CSS_SELECTOR, 'div.translate').text
            source_text = driver.find_element(By.CSS_SELECTOR, 'a.source').text

            # 문장 객체 생성
            Sentence.objects.create(
                sentence=sentence_text,
                definition=definition_text,
                source=source_text,
                word=word_obj
            )

        except Exception as e:
            print(f"clicking label 에러: {e}")

    # 브라우저 닫기
    driver.quit()