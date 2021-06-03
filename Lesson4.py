from pymongo import MongoClient
from pprint import pprint
from lxml import html
import requests

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (HTML, like Gecko) /'
                  'Chrome/90.0.4430.212 Safari/537.36'}

client = MongoClient('localhost', 27017)
db = client['news']
collection = db.news


def lenta_parser_news():
    lenta_url = 'https://lenta.ru'
    response = requests.get(lenta_url, headers=header)
    dom = html.fromstring(response.text)

    items = dom.xpath("//section[contains(@class,'row b-top7-for-main')]//div[contains(@class, 'item')]")

    for item in items:
        news = {}
        name = item.xpath(".//a/text()")
        link = item.xpath(".//a/@href")
        news['date'] = item.xpath(".//a/time/@datetime")

        for i in range(len(link)):
            if link[i].find('https') == -1:
                news['url'] = lenta_url + link[i]
            else:
                news['url'] = link[i]

        news['title'] = name[0].replace(u'\xa0', u' ')
        news['source'] = 'lenta.ru'

        collection.replace_one({'url': news['url']}, news, True)

def yandex_parser_news(echo=False):
    yandex_url = 'https://yandex.ru/news/'
    response = requests.get(yandex_url, headers=header)
    dom = html.fromstring(response.text)
    items = dom.xpath('//article')[:5]
    news = {}
    for item in items:
        news['title'] = item.xpath('..//h2/text()')[0].replace('\xa0', ' ')
        news['url'] = item.xpath('..//a/@href')[0]
        news['source'] = item.xpath('..//a/text()')[0]
        news['date'] = item.xpath('..//span[@class="mg-card-source__time"]/text()')[0]
        if echo:
            print(news)
        collection.replace_one({'url': news['url']}, news, True)
        #insert_collection(news)

lenta_parser_news()
for i in collection.find({}):
    pprint(i)

yandex_parser_news()
for i in collection.find({}):
    pprint(i)