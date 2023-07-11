import psycopg2
from psycopg2 import sql


class DataBase:
    def __init__(self, db_url_object):
        self.conn = psycopg2.connect(db_url_object)
        self.cursor = self.conn.cursor()

    def insert_in_db(self, profile_id, worksheet_id):
        insert_query = sql.SQL("INSERT INTO viewed (profile_id, worksheet_id) VALUES (%s, %s)")
        self.cursor.execute(insert_query, (profile_id, worksheet_id))
        self.conn.commit()

    def select_from_db(self):
        select_query = sql.SQL("SELECT profile_id, worksheet_id FROM viewed")
        self.cursor.execute(select_query)
        return self.cursor.fetchall()
