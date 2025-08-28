from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from unidecode import unidecode
import requests
import json
import os
import cv2
# wczytanie pliku mapującego
with open('mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)
# ścieżka do katalogu z klipami
path = 'pjm_clips'
# konfiguracja przeglądarki w trybie headless (bez otwarcia okna)
op = webdriver.ChromeOptions() # ChromeOptions -> Chrome, FirefoxOptions -> firerfox etc.
op.add_argument('--headless')
driver = webdriver.Chrome(options=op) # zmienić Chrome na wybraną przez siebie przeglądarke
# otwarcie strony
driver.get('https://www.slownikpjm.uw.edu.pl/list')
# maksymalny czas na oczekiwanie elementu strony
wait = WebDriverWait(driver, 10)

"""
    Sprawdza czy na stronie istnieje element określony przez xpath
"""
def check_exists_by_xpath(xpath) -> bool:
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

"""
    wyszukuje słowo na stronie, uruchamia metodę downloadfile służącą do pobrania pliku,
    zapisuje go w wybranym katalogu
"""
def scrape(word: str) -> None:
    # przejście do wyszukwiania zaawansowanego
    adv = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="searcher-tabs"]/li[2]/a')))
    adv.click()

    driver.implicitly_wait(10)
    # Wpisanie w pole wyszukiwania wybranego słowa
    box = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="sign_params_advanced"]/div[3]/div/input')))
    box.clear()
    box.send_keys(word)
    box.send_keys(Keys.ENTER)
    # sprawdzenie czy jest dostępny link do wideo
    if check_exists_by_xpath('/html/body/div[2]/div/div[3]/div[1]/p[1]/a'):
        video_link = wait.until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div[3]/div[1]/p[1]/a')))
        video_link.click()
        # pobranie linku
        get_video = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="gloss_view_video"]/source[1]')))
        downloadfile(word, get_video.get_attribute('src'))
    else:
        print(f'Brak klipu dla słowa {word}')
    # powrót do poprzedniej strony z wyszukiwarką
    driver.back()

"""
    Pobranie pliku wideo
"""
def downloadfile(name: str, url) -> None:
    filename_base = unidecode(name)
    filename = unidecode(filename_base) + '.mp4'
    r = requests.get(url)
    file_path = os.path.join(path, filename)
    # zapis do katalogu
    with open(file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                f.flush()
    f.close()
    driver.implicitly_wait(10)

# pobranie danych od użytkownika
text = input("Wpisz zdanie do przetłumaczenia na PJM: ")
tokens = text.lower().split()

clips = []
updated = False
# sprawdzenie dostępności klipów dla każdego słowa
for token in tokens:
    clip_file = mapping.get(token)
    if clip_file:
        clips.append(os.path.join('pjm_clips', clip_file))
    else:
        scrape(token)
        filename_base = unidecode(token)
        filename = f'{filename_base}.mp4'
        mapping[token] = filename
        clips.append(os.path.join('pjm_clips', filename))
        updated = True
#odtwarzanie klipów wiedo w kolejności
for clip_path in clips:
    cap = cv2.VideoCapture(clip_path)
    if not cap.isOpened():
        print(f"Nie można otworzyć pliku: {clip_path}")
        continue
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('PJM', frame)
        if cv2.waitKey(3) & 0xFF == ord('q'):
            break
    cap.release()
cv2.destroyAllWindows()
# aktualizacja pliku mapping.json, jeżeli wystąpiły nowe słowa
if updated:
    with open('mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
