from pymongo import MongoClient
from pprint import pprint


client = MongoClient('localhost', 27017)
db = client['vacancy']
collection = db.vacansy
db.collection.insert_many('parser_results.csv')
# не могу разобраться как прочитать СЮДА данные..


for i in db.collection.find({'vacancy_min': {'$gt': 10000}}):
    pprint(i)

