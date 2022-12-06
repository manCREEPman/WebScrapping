import os
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller as chromedriver
import time
import db.DBOperations


elibrary = "https://www.elibrary.ru"
habr = "https://habr.com"
wink = "https://wink.ru"
maddevs = "https://maddevs.io"


def set_headers():
    return {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}


def get_soup(item, type = 'lxml') -> BeautifulSoup:
    return BeautifulSoup(item, type)


def get_selenium_req(url):
    options = Options()
    options.headless = True
    page = webdriver.Chrome(chromedriver.install(), options=options)
    page.get(url)
    return page


def get_req(url, headers = set_headers()):
    return requests.get(url, headers)


def parse_habr(url):
    habr_start = time.time()

    soup = get_soup(get_selenium_req(url).page_source)

    allArticles = soup.find_all('article')


    info = {}
    article_count = 0
    for article in allArticles:
        info['title'] = article.find('a', class_='tm-article-snippet__title-link').find('span').text
        info['author'] = article.find('a', class_='tm-user-info__userpic').get('title')

        try:
            annotation = article.find('div', class_='article-formatted-body article-formatted-body article-formatted-body_version-2')
            info['annotation'] = annotation.find('p').text.replace("'", "''")
        except:
            annotation = article.find('div', class_='article-formatted-body article-formatted-body article-formatted-body_version-1').text
            info['annotation'] = annotation.replace("'", "''")

        info['url'] = habr + article.find('a', class_='tm-article-snippet__title-link').get('href')

        info['paper_text'] = get_soup(get_req(info['url']).content).find('article', class_= 'tm-article-presenter__content tm-article-presenter__content_narrow')
        text = "\n\t".join(x.text for x in info['paper_text'].find_all('p'))
        info['paper_text'] = text if len(text) > 0 else info['paper_text'].find('div', xmlns = 'http://www.w3.org/1999/xhtml').text
        info['paper_text'] = info['paper_text'].replace("'", "''")

        # if db.DBOperations.insertInfo(info): article_count += 1
        # else: break
        print(info)

    habr_end = time.time()
    habr_time = habr_end - habr_start
    return habr_time


def parse_wink(url):
    wink_start = time.time()

    soup = get_soup(get_req(url).content)

    allBooks = soup.find_all('div', class_='item_itubtxt')

    info = {}

    article_count = 0
    for book in allBooks:

        info['title'] = book.find('h4', class_ = 'root_r1lbxtse title_tyrtgqg root_subtitle2_r3qime3').text
        title =  info['title'].split('. ')
        title_split = ". ".join(title[i] for i in range(len(title)-1) )
        if len(title_split) > 0:
            info['title'] = title_split
        else:
            title = info['title'].split("! ")
            info['title'] = ". ".join(title[i] for i in range(len(title)-1) )

        info['author'] = title[-1]
        info['url'] = wink + book.find('a').get('href')

        item_page = get_soup(get_req(info['url']).content)
        info['paper_text'] = item_page.find('p', class_ = 'root_r1lbxtse text_t1gefzhn root_body1_rjqy0lg').text.replace("'", "''")
        info['annotation'] = item_page.find_all('a', class_ = 'root_rwxlfxa root_hover_rwzvnfy')
        info['annotation'] = ", ".join(x.text for x in info['annotation']).replace("'", "''")



    wink_end = time.time()
    wink_time = wink_end - wink_start

    return wink_time


def parse_maddevs(url):
    maddevs_start = time.time()
    # шаманим с получением данных
    options = Options()
    options.headless = True
    page = webdriver.Chrome(chromedriver.install(), options=options)
    page.get(url)
    cookie_agree = page.find_element(By.XPATH, '//button[contains(text(), "✓  I agree")]')
    cookie_agree.click()
    counter = 0
    while counter != 100:
        counter = counter + 1
        dummy = page.find_element(By.TAG_NAME, 'a')
        for _ in range(10):
            dummy.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)
        try:
            button = page.find_element(By.XPATH, '//button[contains(text(), "See more")]')
            button.click()
        except:
            break
    
    soup = get_soup(page.page_source)
    allArticles = soup.find_all('div', class_='post-card')

    info = {}
    article_count = 0
    for article in allArticles:
        about = article.find('p', class_='post-card__paragraph')
        if about.text.lower().find('artificial intelligence') != -1:
            info['title'] = article.find('h2', class_='post-card__title post-card__title--full').get('title').replace("'", "''")
            info['author'] = article.find('p', class_='post-author__name').get('title')
            info['url'] = maddevs + article.find('a', class_='post-card__image').get('href')
            info['annotation'] = article.find('p', class_='post-card__paragraph').text.replace("'", "''")

            item_page = get_soup(get_req(info['url']).content).find('section', class_='blog-post__text-container')
            info['paper_text'] = "\n\t".join(x.text for x in item_page.find_all('p')).replace("'", "''")
            print(info) 

        # if db.DBOperations.insertInfo(info): article_count += 1
        # else: break

    maddevs_end = time.time()
    maddevs_time = maddevs_end - maddevs_start

    return maddevs_time

def update_info():

    update_start = time.time()

    path = r"C:\my_files\dz\_univer\_маг_Методы_извлечения_информации_из_сетевых_источников\lab3\out\artifacts\proj1_jar\proj1.jar"
    os.system(f"java -cp {path} db.Main")

    update_end = time.time()

    update_time = update_end - update_start

    return update_time


def execute():
    t1 = parse_habr('https://habr.com/ru/search/?q=%D1%82%D1%80%D0%B5%D1%85%D0%BC%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D1%81%D0%B2%D0%B5%D1%80%D1%82%D0%BE%D1%87%D0%BD%D1%8B%D0%B5%20%D0%BD%D0%B5%D0%B9%D1%80%D0%BE%D0%BD%D0%BD%D1%8B%D0%B5%20%D1%81%D0%B5%D1%82%D0%B8&&target_type=posts&order=date')
    t2 = parse_wink('https://wink.ru/collections/audioknigi')
    t3 = parse_maddevs('https://maddevs.io/tag/software-development/')
    t4 = update_info()

def parse_elibrary():
    data = []

    # выполняем поиск
    options = Options()
    options.headless = True
    browser = webdriver.Chrome(chromedriver.install(), options=options)
    browser.get('https://www.elibrary.ru/querybox.asp?scope=newquery')
    textarea = browser.find_element(By.TAG_NAME, 'textarea')
    textarea.clear()
    textarea.send_keys(u"трехмерные сверточные нейронные сети")
    time.sleep(2)
    go_button = browser.find_element(By.XPATH, '//a[text() = "Поиск"]')    
    go_button.click()
    time.sleep(7)

    # подготовка к парсингу
    link_list = get_soup(browser)
    main_table = link_list.find(id="restab")
    table_body = main_table.findChild('tbody')

    # проходимся по каждому результату поиска
    for row in table_body.findChildren('tr'):
        if row.get('id', None) is not None:
            try:
                td = row.getChild('td')
                div = td.getChild('div')
                a = div.getChild('a')

                # в случае, когда доступен весь текст - открываем новую вкладку
                if a.get('title', None) == 'Доступ к полному тексту открыт':
                    paper_td = row.find(attrs={"valign": "top"})
                    td_div = paper_td.getChild('div')
                    td_a = td_div.getChild('a')
                    paper_soup = get_soup(get_selenium_req(td_a['href']).page_source)
                    # обработка внутренностей статьи

            except:
                continue

# execute()
# parse_elibrary()
# parse_habr()
parse_maddevs("https://maddevs.io/tag/software-development/")
