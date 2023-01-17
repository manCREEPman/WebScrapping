import nltk
from math import log
import re

# nltk.download() # для первого использования токенайзера 

def get_unique_and_all_words(list_text: list) -> tuple:
    words_list = [re.sub(r'[,«»—.:?()\"/!\n]', '', x.lower()) for x in list_text]
    words_list = [nltk.word_tokenize(text=x, language='russian') for x in words_list]
    temp = []
    [temp.extend(l) for l in words_list]
    words_list = temp
    return set(temp), temp


def get_word_entry_count(word: str, iterable: any) -> int:
    return len([x for x in iterable if x == word])


def prepare_data() -> dict:
    # считываем обучающие множества
    with open('ThemeExamplesEn', 'r', encoding='utf-8') as f:
        en_examples = f.readlines()
        f.close()
    with open('ThemeExamplesRus', 'r', encoding='utf-8') as f: 
        ru_examples = f.readlines()
        f.close()
    with open('ThemeExamplesFiction', 'r', encoding='utf-8') as f:
        fiction_examples = f.readlines()
        f.close()
    
    # формируем списки слов для классов англ и рус соответствующих теме, а также для контрпримеров
    theme_examples_set, theme_examples = get_unique_and_all_words((en_examples + ru_examples))
    fiction_set, fiction_examples = get_unique_and_all_words(fiction_examples)

    unique_words = fiction_set.union(theme_examples_set)

    return {
        'unique_words': unique_words,
        'theme_examples': theme_examples,
        'fiction_examples': fiction_examples
    }


def naive_bayes(text: str, data: dict, type: int = 1) -> float:
    NEURO_CLASSES = 2
    FICTION_CLASSES = 1
    
    theme_examples = data['theme_examples']
    fiction_examples = data['fiction_examples']
    unique_words_count = len(data['unique_words'])
    theme_words_count = len(theme_examples)
    fiction_words_count = len(fiction_examples)

    # слагаемые вероятности
    first_addend = 0.0
    second_addend = 0.0
    # если тип 1 - рассматриваем относящиеся к теме, иначе fiction
    if type == 1:
        first_addend = log(float(NEURO_CLASSES / (NEURO_CLASSES + FICTION_CLASSES)))
        _, text_all_words = get_unique_and_all_words([text])
        second_addend = sum([log((get_word_entry_count(word, theme_examples) + 1) / (unique_words_count + theme_words_count)) for word in text_all_words])
    else:
        first_addend = log(float(FICTION_CLASSES / (NEURO_CLASSES + FICTION_CLASSES)))
        _, text_all_words = get_unique_and_all_words([text])
        second_addend = sum([log((get_word_entry_count(word, fiction_examples) + 1) / (unique_words_count + fiction_words_count)) for word in text_all_words])
    return first_addend + second_addend


def classification_process(db_data: list[tuple]) -> list[tuple]:
    data = prepare_data()
    result = []
    print('===================================')
    for article in db_data:
        a = naive_bayes(article[1], data) 
        b = naive_bayes(article[1], data, type=0)
        if a > b:
            type = 1
        else:
            type = 0
        print(f'id: {article[0]} type = {type} (a = {a}, b = {b})')
        result.append((article[0], article[1], type))
    print('===================================')
    return result
