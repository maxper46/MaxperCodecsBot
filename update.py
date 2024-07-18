from json import dumps
from files import get_links, prepare_dict, load_base_page, load_codecses, BASE_URL
from database.database import bot_database as db


def fill_docs_table(filenames: list):
    for ind, filename in enumerate(filenames):
        if 'pdd_rf' in filename:
            continue
        doc_content = prepare_dict(filename)
        tmp_title = doc_content['doc_title']
        doc_title = tmp_title if '"' not in tmp_title else tmp_title[tmp_title.index('"') + 1:tmp_title.rindex('"')]
        content = dumps(doc_content)
        query = '''
                    UPDATE docs SET filename = %s, content = %s WHERE title = %s;
                    '''
        values = (filename, content, doc_title)
        db.execute_query_and_commit(query, values)


if __name__ == '__main__':
    load_base_page(BASE_URL)
    links = get_links()
    load_codecses(links)
    fill_docs_table(list(links.keys()))
