#!/usr/bin/env python

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from json import dumps
from database.database import bot_database as db
from config import database_args
from files import get_links, prepare_dict, load_base_page, load_codecses, BASE_URL


def create_base() -> None:
    args = database_args()
    try:
        conn = psycopg2.connect(**args)
    except psycopg2.OperationalError:
        conn = psycopg2.connect(user=args['user'], password=args['password'])
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as curs:
            sql_create_database = f'CREATE DATABASE {args["dbname"]}'
            curs.execute(sql_create_database)
    conn.close()


def create_tables() -> None:
    query = '''
    drop table if exists users;
    drop table if exists docs;
    
    CREATE TABLE IF NOT EXISTS public.docs
    (
        doc_id serial PRIMARY KEY,
        title text,
        filename text,
        content jsonb        
    );

    CREATE TABLE IF NOT EXISTS public.users
    (
        user_id integer PRIMARY KEY,
        current_doc integer,
        current_art varchar,
        current_page integer,
        bookmarks jsonb,
        CONSTRAINT fkkey_users_current_doc FOREIGN KEY (current_doc) REFERENCES public.docs (doc_id)
    );
'''
    db.execute_query_and_commit(query)


def fill_docs_table(filenames: list):
    for filename in filenames:
        if 'pdd_rf' in filename:
            continue
        doc_content = prepare_dict(filename)
        tmp_title = doc_content['doc_title']
        doc_title = tmp_title if '"' not in tmp_title else tmp_title[tmp_title.index('"') + 1:tmp_title.rindex('"')]
        content = dumps(doc_content)
        query = '''
                    INSERT INTO docs (title, filename, content)
                    VALUES (%s, %s, %s);
                    '''
        values = (doc_title, filename, content)
        db.execute_query_and_commit(query, values)


if __name__ == '__main__':
    create_base()
    create_tables()
    load_base_page(BASE_URL)
    links = get_links()
    load_codecses(links)
    fill_docs_table(list(links.keys()))
