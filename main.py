import requests as req
from bs4 import BeautifulSoup
import json

url = "https://lenta.ru"
newsPrefix = "/news"


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


def getAllNews(url, newsPrefix):
    links = getLinks(url, newsPrefix)
    with open("novosti.jsonl", 'a', encoding='utf-8') as f:
        for link in links:
            jsonlArticle = json.dumps(getArticle(link), ensure_ascii=False)
            f.write(jsonlArticle + '\n')

getAllNews(url,newsPrefix)
