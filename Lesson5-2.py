from selenium import webdriver

from selenium.webdriver.chrome.options import Options
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['hits_mv']
hits = db.sales_hits


def write_to_mongo(elems):
    for elem in elems:
        name = elem.find_element_by_class_name('fl-product-tile-title__link sel-product-tile-title').text
        price = elem.find_element_by_class_name('fl-product-tile-price__current').text
        hits.insert_one({'name': name, 'price': price})


chrome_options = Options()
chrome_options.add_argument('start-max')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.mvideo.ru/')

block = driver.find_element_by_class_name('grid-view')
elems = block.find_elements_by_class_name('gallery-list-item')

#write_to_mongo(elems)
#gallery-layout_products gallery-layout_product-set
buttons = block.find_element_by_class_name('carousel-paging').find_elements_by_tag_name('a')[1:]
for button in buttons:
    button.click()
    time.sleep(2)
    block = driver.find_element_by_class_name('gallery-layout_products gallery-layout_product-set grid-view')
    elems = block.find_elements_by_class_name('gallery-list-item')[:4]
    write_to_mongo(elems)


#это вообще реально победить?... Ну что опять не так.. Я уже столько вариантов перебрала.И так и эдак..
