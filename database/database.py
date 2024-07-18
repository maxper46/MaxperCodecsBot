import psycopg2
from json import dumps
from config import database_args


users_db = {}


class Database:
    def __init__(self):
        self.conn_args = database_args()
        self.conn = psycopg2.connect(**self.conn_args)

    def execute_query_and_commit(self, query, values=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()

    def get_row_by_query(self, query: str, values: tuple = None) -> tuple:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
        if result:
            return result
        return (None,)

    def get_titles_list(self) -> list:
        with self.conn.cursor() as cursor:
            query = '''SELECT title FROM docs'''
            cursor.execute(query)
            result = cursor.fetchall()
        if result:
            return [i[0] for i in result]
        return []

    def is_user_exists(self, user_id: int) -> bool:
        """User exists?"""
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s);"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def create_if_not_exists(
            self,
            user_id: int,
            current_doc: int | None,
            current_art: str,
            current_page: int,
            bookmarks: dict
    ) -> None:
        query = '''
        INSERT INTO users (user_id, current_doc, current_art, current_page,  bookmarks)
        VALUES (%s, %s, %s, %s, %s);
        '''
        bookmarks_json = dumps(bookmarks)
        values = (user_id, current_doc, current_art, current_page, bookmarks_json)

        self.execute_query_and_commit(query, values)

    def set_current_doc(self, user_id: int, doc_id: int, art_number: str = '1', page_number: int = 1) -> None:
        query = "UPDATE users SET current_doc = %s, current_art = %s, current_page = %s WHERE user_id = %s;"
        values = (doc_id, art_number, page_number, user_id)
        self.execute_query_and_commit(query, values)

    def set_current_art(self, user_id: int, art_number: str) -> None:
        query = "UPDATE users SET current_art = %s, current_page = 1 WHERE user_id = %s;"
        values = (art_number, user_id)
        self.execute_query_and_commit(query, values)

    def set_current_page(self, user_id: int, page_number: str) -> None:
        query = "UPDATE users SET current_page = %s WHERE user_id = %s;"
        values = (page_number, user_id)
        self.execute_query_and_commit(query, values)

    def get_doc_data(self, doc_id: int, key: str) -> str | dict:
        query = "SELECT content->%s FROM docs WHERE doc_id = %s;"
        values = (key, doc_id)
        result = self.get_row_by_query(query, values)
        doc_data = result[0]
        return doc_data

    def get_current_info(self, user_id: int) -> tuple:
        query = "SELECT current_doc, current_art, current_page FROM users WHERE user_id = %s;"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result

    def get_current_doc_id(self, user_id: int) -> tuple:
        query = "SELECT current_doc FROM users WHERE user_id = %s;"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result

    def is_key_exists(self, doc_id: int, key: str) -> str:
        query = "SELECT content ? %s FROM docs WHERE doc_id = %s;"
        values = (key, str(doc_id))
        result = self.get_row_by_query(query, values)
        return result[0]

    def is_bookmark_exists(self, user_id: int, key: str) -> str:
        query = "SELECT bookmarks ? %s FROM users WHERE user_id = %s;"
        values = (key, str(user_id))
        result = self.get_row_by_query(query, values)
        return result[0]

    def add_bookmark(self, user_id: int, key: str, value: str) -> None:
        query = 'UPDATE users SET bookmarks = bookmarks || %s WHERE user_id = %s'
        values = (dumps({key: value}), user_id)
        self.execute_query_and_commit(query, values)

    def del_bookmark(self, user_id: int, key: str) -> None:
        query = 'UPDATE users SET bookmarks = bookmarks - %s WHERE user_id = %s'
        values = (key, user_id)
        self.execute_query_and_commit(query, values)

    def get_bookmarks(self, user_id: int) -> dict:
        query = "SELECT bookmarks FROM users WHERE user_id = %s;"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        doc_data = result[0]
        return doc_data


bot_database = Database()
