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


lenta_parser_news()
for i in collection.find({}):
    pprint(i)
