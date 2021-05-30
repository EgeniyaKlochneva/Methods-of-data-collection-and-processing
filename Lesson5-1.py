from pprint import pprint
from selenium import webdriver
import time
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['mails']
main_coll = db.main_coll

driver = webdriver.Chrome()
driver.get('https://mail.ru/')

# авторизация
login = driver.find_element_by_name("login")
login.send_keys('study.ai_172')
button = driver.find_element_by_xpath("//button[@data-testid='enter-password']")
button.click()

time.sleep(1)
password = driver.find_element_by_name("password")
password.send_keys('NextPassword172!')

button = driver.find_element_by_xpath("//button[@data-testid='login-to-mail']")
button.click()

# ссылки на письма
time.sleep(5)
mail_all = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
url = [el.get_attribute('href') for el in mail_all]
links = set(url)
len_check = len(links)

while True:
    actions = ActionChains(driver)
    actions.move_to_element(mail_all[-1])
    actions.perform()
    time.sleep(5)
    mail_all = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
    url = [el.get_attribute('href') for el in mail_all]
    links.update(set(url))
    if len_check == len(links):
        break
    len_check = len(links)

# данные из писем
mails = []
for link in links:
    mail_data = {}
    driver.get(link)
    time.sleep(2)

    mail_data['from'] = driver.find_element_by_class_name('letter-contact').get_attribute('title')
    mail_data['title'] = driver.find_element_by_xpath('//h2').text
    mail_data['text'] = driver.find_element_by_class_name('letter-body').text
    mail_data['date'] = driver.find_element_by_class_name('letter__date').text
    mail_data['link'] = link

    mails.append(mail_data)


for el in mails:
    main_coll.update_one({'link': el.get('link')}, {'$set': el}, upsert=True)

print(f'Писем в базе: {main_coll.count_documents({})}')

