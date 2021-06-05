from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import time
import json

client = MongoClient('localhost', 27017)
db = client['hits_mv']
hits = db.sales_hits

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

section = driver.find_element_by_xpath("//h2[contains(text(),'Новинки')]/ancestor::div[@class='section']")
time.sleep(5)
button = section.find_element_by_class_name('i-icon-fl-arrow-right')

data = set()
len_data = 0
while True:
    button.click()
    time.sleep(2)
    data.update(section.find_elements_by_xpath(".//a[contains(@class, 'fl-product-tile-picture')]"))
    if len_data == len(data):
        break
    else:
        len_data = len(data)

for good in data:
    print(good.get_attribute('data-product-info'))
    j_data = json.loads(good.get_attribute('data-product-info'))
    hits.insert_one(j_data)
