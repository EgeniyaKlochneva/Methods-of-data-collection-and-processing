import requests
from bs4 import BeautifulSoup as bs
import csv
import re
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
hhru = db.hhru

vacancy = 'аналитик'


def hh_parser(vacancy):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
    url = 'https://hh.ru'
    vacancy_output = []
    params = {
        'text': vacancy,
        'search_field': 'name',
        'items_on_page': '50',
        'page': 0
    }

    for page_number in range(0, 100):
        params['page'] = page_number
        response = requests.get(url + '/search/vacancy', params=params, headers=headers)
        target_page = bs(response.text, 'html.parser')
        vacancy_list = target_page.find_all('div', {'class': 'vacancy-serp-item'})
        try:
            target_page.find('a', {'data-qa': 'pager-next'}).find('span')
            for vacancy in vacancy_list:
                vacancy_output.append(hh_get_vacancy_info(vacancy))
        except:
            break


def hh_get_vacancy_info(element):
    vacancy_base = {}
    # вакансия
    vacancy_name = element.find(
        'a', {
            'data-qa': 'vacancy-serp__vacancy-title'}).getText().replace(u'\xa0', u' ')
    vacancy_base['vacancy_name'] = vacancy_name

    # работодатель
    employer_name = element.find(
        'a', {
            'data-qa': 'vacancy-serp__vacancy-employer'}).getText().replace(
        u'\xa0', u' ').split(', ')[0]
    vacancy_base['employer_name'] = employer_name

    # зарплата
    salary = element.find(
        'span', {
            'data-qa': 'vacancy-serp__vacancy-compensation'})
    salary_currency = None
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary = salary.getText().replace(u'\u202f', u'')
        salary = re.split(r'\s|-', salary)
        if salary[0] == 'до':
            salary_min = None
            salary_max = int(salary[1])
            salary_currency = str(salary[2])
        elif salary[0] == 'от':
            salary_min = int(salary[1])
            salary_max = None
        else:
            salary_min = int(salary[0])
            salary_max = int(salary[2])
            salary_currency = str(salary[3])
    vacancy_base['salary_min'] = salary_min
    vacancy_base['salary_max'] = salary_max
    vacancy_base['salary_currency'] = salary_currency

    # ссылка на саму вакансию
    vacancy_url = element.find(
        'a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href').split('?')[0]
    vacancy_base['vacancy_url'] = vacancy_url
    hhru.insert_one(vacancy_base)

    #print(vacancy_base)

    return vacancy_base



hh_parser(vacancy)

print('-----------------------------------------')

# вакансии с зп больше определенной суммы
def search_in_db(db_name, salary):
    client = MongoClient('127.0.0.1', 27017)
    db = client['vacancies']
    hhru = db.hhru
    objects = hhru.find({"$or": [{'salary_min': {"$gt": salary}}, {'salary_max': {"$gt": salary}}]})

    for i in objects:
        print(i)
    return objects


search_in_db(db_name='vacancies', salary=300000)


# добавление новых вакансий в БД
hhru.update_one({'vacancy_url': vacancy['vacancy_url']}, {'$set': vacancy})

if hhru.find({'vacancy_url': {"$in": vacancy['vacancy_url']}}).limit(1) is not None:
    hhru.update_one(vacancy['vacancy_url'])
else:
    print(vacancy['vacancy_url'] + ' это новая вакансия. Добавлена в БД')
    hhru.insert(vacancy)

