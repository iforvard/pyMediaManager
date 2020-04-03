import json
import requests


def create_json_news_list():
    news_list = {'news_list': []}
    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)


def add_news(head, body):
    news_list = read_news_list()
    news = {'head': head, 'body': body}
    news_list['news_list'].append(news)
    with open('news_list.json', 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)


def read_news_list(path='news_list.json'):
    with open(path, encoding="utf-8") as json_file:
        news_list = json.load(json_file)
        return news_list


def get_news_list_github():
    url_news_list = 'https://raw.githubusercontent.com/iforvard/pyMediaManager/master/homepagenews/news_list.json'
    news_list_json = requests.get(url_news_list).json()
    news_list = news_list_json['news_list']
    main_head = news_list_json['main_head']
    return news_list, main_head


if __name__ == '__main__':
    pass
