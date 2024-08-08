import aiohttp
import aiofiles
import os.path
from bs4 import BeautifulSoup as Soup


async def load_base_page(base_url: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(base_url) as response:
            r = await response.text()
            async with aiofiles.open('codecses/base_page', 'w') as file:
                await file.write(r)


async def get_links() -> dict:
    codecses = {}
    async with aiofiles.open('codecses/base_page', 'r', encoding='utf-8') as file:
        file_text = await file.read()
        soup = Soup(file_text, 'lxml')
    data = soup.find('tbody')
    rows = data.find_all('tr')
    for row in rows[2:]:
        link = row.find_all('a')[2]['href']
        tmp_name = link[link.rindex('/'):]
        name = 'codecses/' + tmp_name[tmp_name.index('_') + 1:]
        full_link = link if link.startswith('https') else 'https://garant.ru' + link
        codecses[name] = full_link
    return codecses


async def load_codecses(codecses: dict, update: bool = False) -> list:
    res = []
    async with aiohttp.ClientSession() as session:
        for name in codecses:
            async with session.get(codecses[name]) as response:
                if not os.path.exists(name) or int(response.headers['Content-Length']) != os.path.getsize(name):
                    if update:
                        res.append(name)
                    async with aiofiles.open(name, 'wb') as file:
                        chunk = await response.content.readany()
                        while chunk:
                            await file.write(chunk)
                            chunk = await response.content.readany()
    return res if update else list(codecses.keys())


async def prepare_dict(filename: str) -> dict:
    res_dict = {}
    art_number, art_title, section, chapter, next_art = 0, None, None, None, None
    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        file_text = await file.read()
        soup = Soup(file_text, 'lxml')
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
