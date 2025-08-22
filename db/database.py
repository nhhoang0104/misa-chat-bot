from dotenv import load_dotenv
import os
import mysql.connector

class Database:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.database = os.getenv("DB_NAME")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.charset = 'utf8mb4'
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        if self.conn is None or self.cursor is None:
            self.connect()
        self.cursor.execute(query, params or ())
        # Chỉ commit nếu không phải SELECT
        if not query.strip().lower().startswith("select"):
            self.conn.commit()

    def fetch(self, query, params=None):
        if self.conn is None or self.cursor is None:
            self.connect()
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


