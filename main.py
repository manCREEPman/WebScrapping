from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller as chromedriver
import time
from db.DBOperations import insertInfo, updateInfo, getDBInfo
from classificator import classification_process


elibrary = "https://www.elibrary.ru"
habr = "https://habr.com"
wink = "https://wink.ru"
maddevs = "https://maddevs.io"
sciencedirect = "https://www.sciencedirect.com"
neurohive = "https://neurohive.io"


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

        # вставка в БД
        insertInfo(info)

    habr_end = time.time()
    habr_time = habr_end - habr_start
    return habr_time


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

    rows = classification_process(getDBInfo('where type is null'))
    # tuple(id, paper_text, type)
    for row in rows:
        updateInfo(row[0], row[2])

    rows = getDBInfo('where type is null')
    update_end = time.time()
    update_time = update_end - update_start
    return update_time


def parse_neuralhive(url):
    update_start = time.time()
    soup = get_soup(get_req(url).content)
    for article in soup.find_all('article'):
        info = dict()
        a_title = article.find('a', attrs={'rel': 'bookmark'})
        annotation_div = article.find('div', class_='entry-summary')
        
        info['title'] = a_title.text
        info['url'] = a_title['href']
        info['annotation'] = annotation_div.text

        article_soup = get_soup(get_req(info['url']).content)

        text_section = article_soup.find('section')
        
        info['author'] = article_soup.find('div', class_='author-header').find('a').text
        info['paper_text'] = "\n\t".join(x.text for x in text_section.find_all(['p', 'ul', 'ol']))

        # вставка в БД
        insertInfo(info)
    update_end = time.time()

    return update_end - update_start


def parse_sciencedirect(url):
    update_start = time.time()
    options = Options()
    page = webdriver.Chrome(chromedriver.install(), options=options)
    page.get(url)
    time.sleep(5)
    soup = get_soup(page.page_source)
    article_ol = soup.find('ol', class_='article-list-items')
    for li in article_ol.find_all('li', class_='js-article-list-item'):
        info = dict()
        a_li = li.find('dt').find('a')
        info['title'] = a_li.text
        info['url'] = sciencedirect + a_li['href']
        info['author'] = li.find('dd', class_='js-article-author-list').text


        another_page = webdriver.Chrome(chromedriver.install(), options=Options())
        another_page.get(info['url'])
        time.sleep(5)

        article_soup = get_soup(another_page.page_source)
        text_section = article_soup.find('article')

        abstract = text_section.find('div', class_='abstract')
        introduction = text_section.find('div', attrs={'id': 'preview-section-introduction'})
        snippets = text_section.find('div', attrs={'id': 'preview-section-snippets'})

        info['annotation'] = "\n\t".join(x.text for x in abstract.find_all(['p', 'ul', 'ol']))
        info['paper_text'] = "\n\t".join(x.text for x in introduction.find_all(['p', 'ul', 'ol'])) \
            + "\n\t".join(x.text for x in snippets.find_all(['p', 'ul', 'ol']))

        insertInfo(info)
    update_end = time.time()

    return update_end - update_start


def execute():
    user_answer = input('Хотите выполнить полный парсинг? y/n').lower()
    while user_answer not in {'y', 'n'}:
        user_answer = input('Хотите выполнить полный парсинг? y/n').lower()

    if user_answer == 'y':
        t1 = parse_habr('https://habr.com/ru/search/?q=%D1%82%D1%80%D0%B5%D1%85%D0%BC%D0%B5%D1%80%D0%BD%D1%8B%D0%B5%20%D1%81%D0%B2%D0%B5%D1%80%D1%82%D0%BE%D1%87%D0%BD%D1%8B%D0%B5%20%D0%BD%D0%B5%D0%B9%D1%80%D0%BE%D0%BD%D0%BD%D1%8B%D0%B5%20%D1%81%D0%B5%D1%82%D0%B8&&target_type=posts&order=date')
        print(f'Парсинг habr занял {t1} сек')
        t2 = parse_neuralhive('https://neurohive.io/ru/tutorial/')
        print(f'Парсинг neuralhive занял {t2} сек')
        t3 = parse_sciencedirect('https://www.sciencedirect.com/journal/neural-networks/articles-in-press')
        print(f'Парсинг sciencedirect занял {t3} сек')
    
    t4 = update_info()
    print(f'Классификация завершена за {t4} сек')


execute()
