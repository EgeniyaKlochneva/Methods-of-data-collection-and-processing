from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['mail']
mails = db.mails

chrome_options = Options()
chrome_options.add_argument('start-max')

driver = webdriver.Chrome()
driver.get('https://passport.yandex.ru/auth?from=mail&origin=hostroot_homer_auth_ru&retpath=https%3A%2F%2Fmail.yandex.ru%2F&backpath=https%3A%2F%2Fmail.yandex.ru%3Fnoretpath%3D1')


assert "Авторизация" in driver.title
elem = driver.find_element_by_id('passp-field-login')
elem.send_keys('evgeniya.klochneva')
elem.send_keys(Keys.RETURN)
time.sleep(2)
elem = driver.find_element_by_id('passp-field-passwd')
elem.send_keys('6,Bvxk!GAHF#dJB')
elem.send_keys(Keys.ENTER)
time.sleep(3)

# WebDriverWait(driver, 10).until(
#              EC.element_to_be_clickable((By.CLASS_NAME, 'ns-view-messages ns-view-id-132 js-action-context')))

#assert "Входящие" in driver.title
i = 0
while True:
    try:
        dict_of_data = {}
        froms = driver.find_elements_by_class_name('mail-MessageSnippet-FromText')
        froms[i].click()
        time.sleep(2)
        sender = driver.find_element_by_class_name('mail-MessageSnippet-FromText').get_attribute('title')
        date = driver.find_element_by_class_name('mail-MessageSnippet-Item_dateText').text
        subject = driver.find_element_by_class_name('mail-MessageSnippet-Item mail-MessageSnippet-Item_subject').text
        driver.back()
        time.sleep(2)
        dict_of_data['sender'] = sender
        dict_of_data['date'] = date
        dict_of_data['subject'] = subject
        mails.insert_one(dict_of_data)
        i += 1
    except Exception as e:
        print(e)
        break

#ошибки Message: no such element: Unable to locate element: {"method":"css selector","selector":".mail-MessageSnippet-Item mail-MessageSnippet-Item_subject"}
  #(Session info: chrome=90.0.4430.212)