from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import os

path='pjm_clips'
driver = webdriver.Edge()
driver.get('https://www.slownikpjm.uw.edu.pl/list')

def scrape(word):
    adv = driver.find_element(By.XPATH, '//*[@id="searcher-tabs"]/li[2]/a')
    adv.click()

    driver.implicitly_wait(10)

    box = driver.find_element(By.XPATH, '//*[@id="sign_params_advanced"]/div[3]/div/input')
    box.clear()
    box.send_keys(word)
    box.send_keys(Keys.ENTER)

    driver.implicitly_wait(10)

    video_link = driver.find_element(By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/p[1]/a')
    video_link.click()

    driver.implicitly_wait(10)

    get_video = driver.find_element(By.XPATH, '//*[@id="gloss_view_video"]/source[1]')
    # print(get_video.get_attribute('src'))

    downloadfile(word, get_video.get_attribute('src'))



def downloadfile(name, url):
    name = name+'.mp4'
    r = requests.get(url)
    file_path = os.path.join(path, name)
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                f.flush()
    f.close()
    driver.implicitly_wait(10)

text = input("Wpisz zdanie do przetłumaczenia na PJM: ")
tokens = text.lower().split()

for token in tokens:
    scrape(token)
    driver.back()





