import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import csv
import re

#https://hh.ru/search/vacancy?   clusters=true&ored_clusters=true& enable_snippets=true &salary=&st=searchVacancy&text=аналитик

vacancy = input('Введите должность: ')

r_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (HTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}
url = 'https://hh.ru'

r_params = {
    'clusters' : 'true',
    'ored_clusters':'true',
    'enable_snippets':'true',
    'salary': 'None',
    'st': 'searchVacancy',
    'text': vacancy
   }
response = requests.get(url + '/search/vacancy', params=r_params, headers=r_headers)
soup = bs(response.text, 'html.parser')
vacancy_list = soup.find_all('div', {'class':'vacancy-serp-item'})

all_vacancy = []
cnt = 1
while True:
    vacancy_list = soup.find_all('div', {'class': 'vacancy-serp-item'})
    for vacancy in vacancy_list:
        vacancy_data = {}
        link = vacancy.find('a')
        vacancy_url = link['href']
        vacancy_name = link.getText()
        vacancy_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        employer_name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).getText().replace(u'\xa0', u' ')

        vacancy_min = None
        vacancy_max = None
        vacancy_cur = None

        if vacancy_salary is not None:

            vacancy_salary = vacancy_salary.getText().replace('\u202f', '')
            vacancy_cur = vacancy_salary.split()[-1] #тк валюта явл последним элементом
            if vacancy_salary.find('–') > -1: #метод возвр позицию элемента или -1, если ничего не найдено. - лучше копировать прям с сайта\
                #если дефис нашли, то есть и мин и макс зп
                vacancy_min = int(vacancy_salary.split()[0])
                vacancy_max = int(vacancy_salary.split()[2])

            elif vacancy_salary.find('от'):
                vacancy_min = int(vacancy_salary.split()[1])

            elif vacancy_salary.find('до'):
                vacancy_max = int(vacancy_salary.split()[1])

        vacancy_data['url'] = vacancy_url
        vacancy_data['name'] = vacancy_name
        vacancy_data['employer_name'] = employer_name
        vacancy_data['salary_min'] = vacancy_min
        vacancy_data['salary_max'] = vacancy_max
        vacancy_data['salary_cur'] = vacancy_cur
        all_vacancy.append(vacancy_data)
    next_button = soup.find('a', {'data-qa': 'pager-next'})

    if next_button is None:
        break
    else:
        next_link = url + next_button['href']
        response = requests.get(next_link, headers=r_headers)
        soup = bs(response.text, 'html.parser')
        print(f'Обработано {cnt} страниц сайта')
        cnt +=1

pprint(all_vacancy)
print(len(all_vacancy))

