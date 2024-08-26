from django.shortcuts import render
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from words.models import Topic, Word, Sentence, Vocabulary, Quiz, Memo

# Create your views here.
def get_words():
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
        main_topic = topics[topic_index].text.strip()
        topics[topic_index].click()
        time.sleep(2)

        processed_subtopics = []
        topic_boxes = driver.find_elements(By.CLASS_NAME, "topic-box-secondary-heading")

        while len(processed_subtopics) < len(topic_boxes):
            for index, topic_box in enumerate(topic_boxes):
                if index in processed_subtopics:
                    continue
        
                topic_boxes = driver.find_elements(By.CLASS_NAME, "topic-box-secondary-heading")
                sub_topic = topic_boxes[index].text
                sub_topic = sub_topic.replace("(see all)", "").strip()
                topic_box = topic_boxes[index]
        
                topic_box.click()
                time.sleep(2)
        
                elements = driver.find_elements(By.CSS_SELECTOR, "li[data-hw]")
                for element in elements:
                    word = element.get_attribute("data-hw")
                    try:
                        difficulty = element.find_element(By.CSS_SELECTOR, "span.belong-to").text
                    except:
                        difficulty = "N/A"

                    topic, created = Topic.objects.get_or_create(main_topic=main_topic, sub_topic=sub_topic)
                    Word.objects.get_or_create(word=word, difficulty=difficulty, topic=topic)

                    print(word, difficulty, main_topic, sub_topic)
        
                processed_subtopics.append(index)
        
                driver.back() # 뒤로가기
                time.sleep(2)
        
                topic_boxes = driver.find_elements(By.CLASS_NAME, "topic-box-secondary-heading")

        back_btn = driver.find_element(By.CSS_SELECTOR, "a.topic_back")
        back_btn.click()
        time.sleep(2)

    topics = driver.find_elements(By.CLASS_NAME, "topic-label")