import requests
import os.path
from bs4 import BeautifulSoup as Soup


def load_base_page(base_url: str):
    r = requests.get(base_url)
    with open('codecses/base_page', 'w') as file:
        file.write(r.text)


def get_links() -> dict:
    codecses = {}
    with open('codecses/base_page', 'r', encoding='utf-8') as file:
        soup = Soup(file.read(), 'lxml')
    data = soup.find('tbody')
    rows = data.find_all('tr')
    for row in rows[2:]:
        link = row.find_all('a')[2]['href']
        tmp_name = link[link.rindex('/'):]
        name = 'codecses/' + tmp_name[tmp_name.index('_') + 1:]
        full_link = link if link.startswith('https') else 'https://garant.ru' + link
        codecses[name] = full_link
    return codecses


def load_codecses(codecses: dict):
    for name in codecses:
        if not os.path.exists(name):
            req = requests.get(codecses[name])
            with open(name, 'wb') as file:
                file.write(req.content)
        else:
            head_req = requests.request('HEAD', codecses[name])
            if int(head_req.headers['Content-Length']) != os.path.getsize(name):
                req = requests.get(codecses[name])
                with open(name, 'wb') as file:
                    file.write(req.content)


def prepare_dict(filename: str) -> dict:
    res_dict = {}
    art_number, art_title, section, chapter, next_art = 0, None, None, None, None
    with open(filename, 'r', encoding='utf-8') as file:
        soup = Soup(file.read(), 'lxml')
    doc_title = soup.find('book-title').text
    doc_date = soup.find('date').text
    data = soup.find("section", {"id": "sub_0"})
    for tag in data.find_all('section'):
        if tag.has_attr('id'):
            title = tag.find('title')
            if title.text.startswith('Раздел'):
                section = title.text
            elif title.text.startswith('Глава'):
                chapter = title.text
            elif title.text.startswith('Статья'):
                prev_number = art_number
                tmp_title = title.text.split(None, 2)
                if len(tmp_title) == 3:
                    _, art_number, art_title = tmp_title
                else:
                    art_number, art_title = tmp_title[1], ''
                art_number = art_number[:-1] if art_number.endswith('.') else art_number
                text = title.find_next_siblings('p')
                art_text = '\n'.join(i.text for i in text)
                article = {art_number: {'title': art_title, 'text': art_text, 'section': section,
                           'chapter': chapter, 'prev': prev_number, 'next': 0}}
                res_dict.update(article)
                if len(res_dict) > 1:
                    res_dict[list(res_dict.keys())[-2]]['next'] = art_number
    first_number = list(res_dict.keys())[0]
    last_number = art_number
    res_dict.update({'doc_title': doc_title, 'doc_date': doc_date, 'first_number': first_number,
                     'last_number': last_number})
    return res_dict


BASE_URL = 'https://www.garant.ru/products/solution/mobile_tech/'
