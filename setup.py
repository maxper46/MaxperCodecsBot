#!/usr/bin/env python

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, connection
from json import dumps
from config import database_args
from files import get_links, prepare_dict, load_base_page, load_codecses, BASE_URL


def create_connect() -> connection:
    args = database_args()
    try:
        conn = psycopg2.connect(**args)
    except psycopg2.OperationalError:
        create_base(args)
        conn = psycopg2.connect(**args)
    return conn


def create_base(args: dict) -> None:
    conn = psycopg2.connect(user=args['user'], password=args['password'])
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as curs:
        sql_create_database = f'CREATE DATABASE {args["dbname"]}'
        curs.execute(sql_create_database)
    conn.close()


def execute_query_and_commit(conn: connection, query, values=None):
    with conn.cursor() as cursor:
        cursor.execute(query, values)
        conn.commit()


def create_tables(connect: connection) -> None:
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
    execute_query_and_commit(connect, query)


def fill_docs_table(connect, filenames: list):
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
        execute_query_and_commit(connect, query, values)


if __name__ == '__main__':
    connect = create_connect()
    create_tables(connect)
    load_base_page(BASE_URL)
    links = get_links()
    load_codecses(links)
    fill_docs_table(connect, list(links.keys()))
    connect.close()
