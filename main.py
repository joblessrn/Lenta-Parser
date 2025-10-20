import requests as req
from bs4 import BeautifulSoup
import json
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


url = "https://lenta.ru"
newsPrefix = "/news"
lock = threading.Lock()

def getLinks(url, newsPrefix):
    response = req.get(url)
    html = response.text
    allLinks = []
    soup = BeautifulSoup(html, 'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href.startswith(newsPrefix):
            allLinks.append(url + href)

    #for link in allLinks:
    #    print(link)

    return allLinks


def getArticle(link):
    try:
        time.sleep(random.uniform(0.3, 1.0))
        html = req.get(link)
        soup = BeautifulSoup(html.text, 'html.parser')
        category = soup.find('a', class_='topic-header__item topic-header__rubric')
        pTags = soup.find_all('p', class_='topic-body__content-text')
        articleTexts = []

        for p in pTags:
            text = p.get_text(separator=' ', strip=True)
            articleTexts.append(text)

        fullText = " ".join(articleTexts)
        jsonArticle = {"url": link,
                       "category": category.text,
                       "article": fullText}

        return jsonArticle
    except Exception as e:
        print(f"Ошибка при обработке {link}: {e}")
        return None


def getAllNews(urls, max_workers=8, batch_size=20):
    filename = "novosti.jsonl"
    batches = [urls[i:i+batch_size] for i in range(0, len(urls), batch_size)]
    c = 1
    for batch_num, batch in enumerate(batches, 1):
        print(f"Обрабатываем батч {batch_num}/{len(batches)} ({len(batch)} ссылок)")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(getArticle, link) for link in batch]

            for future in as_completed(futures):
                result = future.result()
                print(f"result {c} = {result}")
                c = c + 1
                if result:
                    with lock:
                        with open(filename, 'a', encoding='utf-8',buffering=1) as f:
                            jsonlArticle = json.dumps(result, ensure_ascii=False)
                            f.write(jsonlArticle + '\n')

        if batch_num < len(batches):
            batch_delay = random.uniform(4.0, 7.0)
            #print(f"Пауза между батчами: {batch_delay:.2f} сек")
            time.sleep(batch_delay)


links = getLinks(url, newsPrefix)
getAllNews(links)

